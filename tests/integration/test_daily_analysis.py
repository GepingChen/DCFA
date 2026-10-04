"""Daily switching mechanics only; synthetic/fake estimators are not GPU evidence."""

import json
from dataclasses import replace

import httpx
import numpy as np
import pytest

from dcfa.constants import EstimatorBackend
from dcfa.errors import BackendError, ErrorCode
from dcfa.tabcf_iv.backend import SklearnQuantileBackend
from dcfa.tabcf_iv.development_dgp import generate_development_iv
from dcfa.tabcf_iv.local_tabpfn import LOCAL_TABPFN_V2_BACKEND_PARAMETERS
from dcfa.tabcf_iv.managed_client import MANAGED_BACKEND_PARAMETERS, TabPFNClientBackend
from dcfa.tabcf_iv.managed_session import QuotaUsage, quota_error, response_guard
from dcfa.tabcf_iv.pipeline import predict_backend
from dcfa_website_demo.app import _execute_compiled_dataset
from dcfa_website_demo.daily import execute_daily_dataset
from dcfa_website_demo.gemini import GeminiWebsiteCompilation
from tests.integration.test_website_demo import FakeClientRegressor


@pytest.fixture
def confirmed(tmp_path):
    data = generate_development_iv(n=128, seed=20260813, instrument_strength=1.6)
    return dict(
        result_scenario="strong_iv",
        output_scenario="test",
        output_root=tmp_path,
        columns=data.columns,
        manifest=replace(data.manifest, estimator_backend=EstimatorBackend.TABPFN),
        outcome="Y",
        treatment="X",
        instrument="Z",
        seed=20260813,
        interventions=tuple(
            float(x) for x in np.quantile(data.columns["X"], [0.1, 0.3, 0.5, 0.7, 0.9])
        ),
        compilation=GeminiWebsiteCompilation(
            "Y", "X", "Z", "quantile_contrast", "high", "low", 0.5, {}
        ),
    )


class FakeV2(SklearnQuantileBackend):
    name = EstimatorBackend.TABPFN

    @property
    def manifest(self):
        return replace(
            super().manifest,
            parameters=(*super().manifest.parameters, ("model_version", "v2"), ("device", "cuda")),
        )


def executor(name, calls, failure=None):
    def run(kwargs, directory, settings):
        calls.append((name, "start", kwargs))
        if failure == "before":
            raise quota_error(QuotaUsage(5, 5, 5, 20), stage="test.before")

        def runner(backend, stage, *args):
            calls.append((name, stage, backend))
            if stage == failure:
                raise quota_error(QuotaUsage(5, 5, 5, 20), stage="test." + stage)
            return predict_backend(backend, stage, *args)

        return _execute_compiled_dataset(
            **kwargs,
            reserved_output_dir=directory,
            preserve_failure=True,
            backend_parameters=MANAGED_BACKEND_PARAMETERS
            if name == "api"
            else LOCAL_TABPFN_V2_BACKEND_PARAMETERS,
            backend_factory=(
                lambda spec: TabPFNClientBackend(
                    seed=spec.seed, regressor_class=FakeClientRegressor, client_version="0.6.1"
                )
            )
            if name == "api"
            else (lambda spec: FakeV2(seed=spec.seed)),
            prediction_runner=runner,
        )

    return run


@pytest.mark.parametrize("failure", ["before", "stage1", "stage2"])
def test_full_restart_preserves_request_and_records(confirmed, failure):
    calls = []
    result = execute_daily_dataset(
        mode="api_preferred",
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=executor("api", calls, failure),
        v2_executor=executor("v2", calls),
    )
    assert result.response.status == "completed", result.response.error
    assert [(n, s) for n, s, _ in calls if n == "v2"] == [
        ("v2", "start"),
        ("v2", "stage1"),
        ("v2", "stage2"),
    ]
    starts = [kw for _, s, kw in calls if s == "start"]
    for key in ("seed", "interventions", "manifest", "outcome", "treatment", "instrument"):
        assert starts[0][key] == starts[1][key]
    assert starts[0]["compilation"] is not starts[1]["compilation"]
    api_backends = [b for n, s, b in calls if n == "api" and s != "start"]
    v2_backends = [b for n, s, b in calls if n == "v2" and s != "start"]
    assert not any(a is b for a in api_backends for b in v2_backends)
    record = result.llm_trace["daily_execution"]
    assert record["fallback_completed"] and len(record["attempts"]) == 2
    assert record["actual_model"] == "TabPFN v2"
    assert (result.output_dir.parent / "attempt-1-api" / "attempt.json").is_file()
    assert result.response.queries[0].evidence_id
    assert any(
        w.code == "DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE" for w in result.response.warnings
    )
    assert "结果可能不同" in (result.output_dir / "analysis_report.md").read_text()


@pytest.mark.parametrize(
    "mode,names", [("api_preferred", ["api"]), ("api_only", ["api"]), ("v2_only", ["v2"])]
)
def test_modes_success(confirmed, mode, names):
    calls = []
    result = execute_daily_dataset(
        mode=mode,
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=executor("api", calls),
        v2_executor=executor("v2", calls),
    )
    assert result.response.status == "completed", result.response.error
    assert [n for n, s, _ in calls if s == "start"] == names
    assert not result.llm_trace["daily_execution"]["fallback_attempted"]


@pytest.mark.parametrize(
    "code",
    [
        ErrorCode.MANAGED_RATE_LIMITED,
        ErrorCode.DATA_ACCESS_BLOCKED,
        ErrorCode.MANAGED_SERVICE_FAILED,
        ErrorCode.INVALID_DATA,
        ErrorCode.OUTSIDE_SUPPORT,
        ErrorCode.UNSUPPORTED_BACKEND_PROFILE,
        ErrorCode.EVIDENCE_MISMATCH,
    ],
)
def test_other_errors_never_switch(confirmed, code):
    def fail(*args):
        raise BackendError(code, "Safe failure", stage="test")

    def forbidden(*args):
        pytest.fail("Unexpected v2 execution")

    result = execute_daily_dataset(
        mode="api_preferred",
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=fail,
        v2_executor=forbidden,
    )
    assert result.response.error["code"] == code
    assert len(result.llm_trace["daily_execution"]["attempts"]) == 1


@pytest.mark.parametrize("mode,expected", [("api_only", 1), ("api_preferred", 2), ("v2_only", 1)])
def test_failed_v2_or_fixed_api_stops(confirmed, mode, expected):
    def quota(*args):
        raise quota_error(QuotaUsage(5, 5, 5, 20), stage="test")

    def missing(*args):
        raise BackendError(ErrorCode.V2_UNAVAILABLE, "No GPU", stage="test")

    result = execute_daily_dataset(
        mode=mode,
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=quota,
        v2_executor=missing,
    )
    assert result.response.status == "blocked"
    assert len(result.llm_trace["daily_execution"]["attempts"]) == expected


@pytest.mark.parametrize(
    "status,usage,code",
    [
        (429, None, ErrorCode.MANAGED_RATE_LIMITED),
        (429, QuotaUsage(1, 5, 1, 20), ErrorCode.MANAGED_RATE_LIMITED),
        (429, QuotaUsage(5, 5, 5, 20), ErrorCode.MANAGED_QUOTA_EXHAUSTED),
        (401, QuotaUsage(5, 5, 5, 20), ErrorCode.DATA_ACCESS_BLOCKED),
        (403, None, ErrorCode.DATA_ACCESS_BLOCKED),
        (503, QuotaUsage(5, 5, 5, 20), ErrorCode.MANAGED_SERVICE_FAILED),
        (426, None, ErrorCode.UNSUPPORTED_BACKEND_PROFILE),
    ],
)
def test_http_classification_never_copies_body(status, usage, code):
    guard = response_guard(lambda: usage)
    with pytest.raises(BackendError) as caught:
        guard(httpx.Response(status, json={"message": "quota exhausted PRIVATE SECRET"}))
    assert caught.value.code == code
    assert "PRIVATE" not in json.dumps(caught.value.to_dict())


def test_unknown_usage_and_success():
    assert QuotaUsage.parse({"daily_tokens_used": "5"}) is None
    response_guard(lambda: None)(httpx.Response(200))
    response_guard(lambda: None)(httpx.Response(409))


def test_v2_failure_has_no_third_attempt(confirmed):
    calls = []

    def broken(*args):
        calls.append("v2")
        raise RuntimeError("PRIVATE provider body")

    result = execute_daily_dataset(
        mode="api_preferred",
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=executor("api", [], "stage2"),
        v2_executor=broken,
    )
    assert calls == ["v2"]
    assert result.response.error["code"] == ErrorCode.V2_EXECUTION_FAILED
    assert "PRIVATE" not in (result.output_dir / "daily_execution.json").read_text()
    assert not result.response.queries


def test_cached_followup_keeps_v2_identity_without_refitting(confirmed, monkeypatch):
    import dcfa_website_demo.app as app
    from dcfa.tabcf_iv.pipeline import TabCFAnalysisEngine
    from dcfa_website_demo.v2_remote import expected_specification

    engines = []

    def build_engine(**kwargs):
        engine = TabCFAnalysisEngine(**kwargs)
        engines.append(engine)
        return engine

    monkeypatch.setattr(app, "TabCFAnalysisEngine", build_engine)
    calls = []
    result = execute_daily_dataset(
        mode="api_preferred",
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=executor("api", calls, "stage2"),
        v2_executor=executor("v2", calls),
    )
    before = len(calls)
    query = engines[-1].follow_up(
        expected_specification(confirmed), result.response.queries[0].query_id
    )
    assert query == result.response.queries[0]
    assert len(calls) == before
    assert result.llm_trace["daily_execution"]["actual_model"] == "TabPFN v2"


def test_weak_warning_and_support_survive_fallback(confirmed):
    from dcfa.canonical import to_primitive

    weak = generate_development_iv(n=128, seed=20260813, instrument_strength=0.02)
    confirmed.update(
        columns=weak.columns,
        manifest=replace(weak.manifest, estimator_backend=EstimatorBackend.TABPFN),
        interventions=tuple(
            float(v) for v in np.quantile(weak.columns["X"], [0.3, 0.4, 0.5, 0.6, 0.7])
        ),
    )
    result = execute_daily_dataset(
        mode="api_preferred",
        compiled_kwargs=confirmed,
        managed_settings={},
        api_executor=executor("api", [], "before"),
        v2_executor=executor("v2", []),
    )
    assert result.response.status == "completed"
    bundle = json.loads((result.output_dir / "result_bundle.json").read_text())
    assert bundle["warnings"] == to_primitive(result.response.warnings)
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" in {w.code for w in result.response.warnings}
    assert bundle["queries"][0]["support_status"] == result.response.queries[0].support_status.value


def test_fixed_v2_does_not_read_managed_credentials(confirmed, monkeypatch):
    monkeypatch.setenv("DCFA_V2_EXECUTOR", "local_cuda")
    monkeypatch.setattr(
        "dcfa.tabcf_iv.managed_smoke.read_managed_token_file",
        lambda *a: pytest.fail("Fixed v2 read a Prior Labs credential"),
    )
    result = execute_daily_dataset(mode="v2_only", compiled_kwargs=confirmed, managed_settings={})
    assert result.response.error["code"] == ErrorCode.V2_UNAVAILABLE


def test_guard_and_credentials_cleaned_after_exception():
    from tabpfn_client.client import ServiceClient

    from dcfa.tabcf_iv.managed_session import managed_session
    from tests.integration.test_website_demo import FakeClientModule

    client = FakeClientModule()
    before = list(ServiceClient.httpx_client.event_hooks["response"])
    with pytest.raises(RuntimeError):
        with managed_session(client, "tabpfn_sk_test_credential_for_unit_test"):
            assert len(ServiceClient.httpx_client.event_hooks["response"]) == len(before) + 1
            raise RuntimeError("test")
    assert ServiceClient.httpx_client.event_hooks["response"] == before
    assert client.reset_called
    assert "Authorization" not in ServiceClient.httpx_client.headers
    from tabpfn_client.options import get_opts

    assert get_opts().TABPFN_TOKEN is None
