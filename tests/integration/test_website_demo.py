from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pytest

from dcfa.agent.gemini_live import GOOGLE_GENAI_VERSION
from dcfa.agent.state import AgentState
from dcfa.artifact_validation import verify_run_directory
from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.managed_client import MANAGED_CLIENT_VERSION
from dcfa_website_demo.app import (
    MAX_DEMO_ROWS,
    MAX_DEMO_SEED,
    _execution_error_outputs,
    _input_error_outputs,
    _reserve_output_directory,
    build_app,
    execute_csv_upload,
    execute_portfolio_scenario,
    format_portfolio_result,
    resolve_build_revision,
)
from dcfa_website_demo.csv_upload import (
    STANDARD_DEMO_ROWS,
    export_standard_demo_csv,
    load_authorized_csv,
)
from dcfa_website_demo.presentation import display_value
from dcfa_website_demo.service import build_service, require_available_port


class FakeClientRegressor:
    prediction_calls = 0

    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["model_path"] == "v2.5_default"
        assert kwargs["n_estimators"] == 1
        assert kwargs["thinking_mode"] is False
        self._last_meta: dict[str, Any] = {}
        self._last_trace_id = "website-fake-trace"

    def fit(self, features: np.ndarray, target: np.ndarray):
        matrix = np.asarray(features, dtype=float)
        values = np.asarray(target, dtype=float)
        design = np.column_stack([np.ones(len(matrix)), matrix])
        self.coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
        residuals = values - design @ self.coefficients
        self.scale = max(float(np.std(residuals)), 0.2)
        self.lower = float(np.min(values) - 4.0 * self.scale)
        self.upper = float(np.max(values) + 4.0 * self.scale)
        return self

    def predict(self, features: np.ndarray, *, output_type: str) -> Any:
        matrix = np.asarray(features, dtype=float)
        means = np.column_stack([np.ones(len(matrix)), matrix]) @ self.coefficients
        type(self).prediction_calls += 1
        self._last_meta = {"package_version": "8.3.0"}
        if output_type == "mean":
            return means
        assert output_type == "full"
        borders = np.linspace(self.lower, self.upper, 101)
        centers = 0.5 * (borders[:-1] + borders[1:])
        logits = -0.5 * ((centers[None, :] - means[:, None]) / self.scale) ** 2
        return {"borders": borders, "logits": logits}


class FakeClientModule:
    TabPFNRegressor = FakeClientRegressor

    def __init__(self) -> None:
        self.authenticated = False
        self.reset_called = False

    def set_access_token(self, token: str) -> None:
        self.authenticated = token.startswith("tabpfn_sk_")

    def reset(self) -> None:
        self.authenticated = False
        self.reset_called = True


class FakeGeminiUsage:
    total_input_tokens = 120
    total_output_tokens = 48
    total_thought_tokens = 32
    total_tokens = 200


class FakeGeminiInteraction:
    status = "completed"
    model = "gemini-3.6-flash"
    usage = FakeGeminiUsage()

    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.id = ""


class FakeGeminiInteractions:
    def __init__(self, output_text: str, *, raises: bool = False) -> None:
        self.output_text = output_text
        self.raises = raises
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> FakeGeminiInteraction:
        self.calls.append(kwargs)
        if self.raises:
            raise RuntimeError("synthetic Gemini failure")
        return FakeGeminiInteraction(self.output_text)


class FakeGeminiClient:
    def __init__(self, output_text: str | None = None, *, raises: bool = False) -> None:
        self.interactions = FakeGeminiInteractions(
            output_text or _valid_gemini_proposal(),
            raises=raises,
        )
        self.closed = False

    def close(self) -> None:
        self.closed = True


def _valid_gemini_proposal(**updates: str) -> str:
    proposal = {
        "decision": "analyze",
        "reason": "Compile the requested median contrast.",
        "outcome": "Y",
        "treatment": "X",
        "instrument": "Z",
        "treatment_type": "continuous",
        "objective": "quantile_contrast",
        "x_label": "high",
        "comparison_x_label": "low",
        "level_label": "median",
    }
    proposal.update(updates)
    return json.dumps(proposal)


@pytest.fixture
def managed_client(tmp_path: Path) -> dict[str, Any]:
    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    return {
        "token_file": token_file,
        "client_module": FakeClientModule(),
        "client_version": MANAGED_CLIENT_VERSION,
        "gemini_api_key_file": gemini_key_file,
        "gemini_client": FakeGeminiClient(),
        "gemini_sdk_version": GOOGLE_GENAI_VERSION,
    }


def test_website_demo_import_is_lazy_and_keeps_hillstrom_isolated() -> None:
    code = (
        "import sys; import dcfa_website_demo.app as app; "
        "assert 'gradio' not in sys.modules; "
        "assert 'torch' not in sys.modules; "
        "assert 'tabpfn' not in sys.modules; "
        "assert 'tabpfn_client' not in sys.modules; "
        "assert 'google.genai' not in sys.modules; "
        "assert not any(name.startswith('dcfa.hillstrom_policy') for name in sys.modules); "
        "assert callable(app.build_app); assert callable(app.execute_portfolio_scenario)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_container_package_includes_gemini_profile_and_both_secrets() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")
    compose = Path("compose.yaml").read_text(encoding="utf-8")

    assert "COPY evaluation/configs/website_demo_gemini_v1.json" in dockerfile
    assert "ARG DCFA_BUILD_REVISION=unknown" in dockerfile
    assert "DCFA_BUILD_REVISION=${DCFA_BUILD_REVISION}" in dockerfile
    assert "!evaluation/configs/website_demo_gemini_v1.json" in dockerignore
    assert "DCFA_GEMINI_API_KEY_FILE=/run/secrets/gemini_api_key" in dockerfile
    assert "DCFA_WEBSITE_GEMINI_CONFIG_FILE=/app/evaluation/configs/" in dockerfile
    assert "/run/secrets/gemini_api_key:ro" in compose
    assert "/run/secrets/tabpfn_api_key:ro" in compose
    assert "DCFA_BUILD_REVISION: ${DCFA_BUILD_REVISION:-unknown}" in compose


def test_supported_website_scenario_returns_real_state_trace_and_evidence(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    FakeClientRegressor.prediction_calls = 0
    result = execute_portfolio_scenario(
        "strong_iv",
        160,
        20260810,
        output_root=tmp_path,
        **managed_client,
    )
    assert result.response.status == "completed"
    assert result.response.final_state is AgentState.COMPLETED
    assert result.response.result_bundle_id is not None
    assert len(result.response.queries) == 1
    assert result.response.queries[0].evidence_id.startswith("evidence_")
    assert result.plot_path is not None and result.plot_path.is_file()
    assert FakeClientRegressor.prediction_calls == 3
    assert managed_client["client_module"].reset_called
    assert len(managed_client["gemini_client"].interactions.calls) == 1
    llm_call = managed_client["gemini_client"].interactions.calls[0]
    assert llm_call["store"] is False
    assert llm_call["response_format"]["mime_type"] == "application/json"
    assert llm_call["generation_config"]["max_output_tokens"] == 1024
    assert "response_mime_type" not in llm_call
    assert "labels" not in llm_call
    model_input = json.loads(llm_call["input"])
    assert set(model_input) == {
        "available_roles",
        "baseline_covariates",
        "intervention_labels",
        "supported_summaries",
        "user_question",
    }
    assert "rows" not in llm_call["input"]
    assert result.llm_trace["data_rows_sent_to_gemini"] == 0
    assert result.llm_trace["actual_intervention_values_sent_to_gemini"] == 0
    assert result.llm_trace["interaction_id"] is None
    assert (result.output_dir / "gemini_compilation.json").is_file()
    numerical_core = json.loads(
        (result.output_dir / "numerical_core.json").read_text(encoding="utf-8")
    )
    assert numerical_core["estimator_backend"] == "tabpfn"
    assert numerical_core["evidence_status"] == "development_only"
    assert verify_run_directory(result.output_dir)["status"] == "valid"

    status, states, answer, evidence, plot = format_portfolio_result(result)
    assert "development-only" in status
    assert "Result verified" in status
    assert "Question interpreted" in states
    assert "Result verified" in states
    query = result.response.queries[0]
    assert display_value(query.value_raw) in answer
    assert "outcome units" in answer
    visitor_text = "\n".join((status, states, answer, evidence))
    for internal_value in (
        query.claim_type,
        query.evidence_id,
        query.support_status.value,
        result.response.result_bundle_id,
        result.response.specification_id,
        *(warning.code for warning in query.warnings),
    ):
        assert internal_value not in visitor_text
    assert plot == str(result.plot_path)
    assert result.plot_path.name == "website_interventional_summary.png"
    assert (result.output_dir / "interventional_summary.png").is_file()
    ledger_record = json.loads(
        (result.output_dir / "evidence_records.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert ledger_record["value_raw"] == query.value_raw

    unknown_query = replace(query, claim_type="future_internal_claim")
    unknown_result = replace(
        result,
        response=replace(result.response, queries=(unknown_query,)),
    )
    unknown_status, unknown_states, unknown_answer, unknown_details, unknown_plot = (
        format_portfolio_result(unknown_result)
    )
    assert "Result verification failed" in unknown_status
    assert "Safety check stopped" in unknown_states
    assert display_value(query.value_raw) not in unknown_answer
    assert "local artifact review" in unknown_details
    assert unknown_plot is None


def test_authorized_csv_upload_runs_managed_tabpfn_and_binds_manifest(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    csv_path = export_standard_demo_csv(tmp_path / "standard-demo.csv")
    FakeClientRegressor.prediction_calls = 0

    result = execute_csv_upload(
        csv_path,
        "Y",
        "X",
        "Z",
        True,
        20260813,
        output_root=tmp_path / "runs",
        **managed_client,
    )

    assert result.scenario == "csv_upload"
    assert result.response.status == "completed"
    assert result.response.final_state is AgentState.COMPLETED
    assert result.response.queries[0].evidence_id.startswith("evidence_")
    assert result.llm_trace["proposal"]["objective"] == "quantile_contrast"
    assert result.output_dir is not None
    assert result.output_dir.parent.parent.name.startswith("csv-upload-")
    assert FakeClientRegressor.prediction_calls == 3
    manifest = json.loads((result.output_dir / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_kind"] == "user_authorized_local_csv_upload"
    assert manifest["columns"] == ["Z", "X", "Y"]
    assert manifest["row_count"] == STANDARD_DEMO_ROWS
    assert manifest["estimator_backend"] == "tabpfn"
    assert manifest["evidence_status"] == "development_only"


def test_csv_upload_requires_confirmation_before_client_or_output(tmp_path: Path) -> None:
    csv_path = export_standard_demo_csv(tmp_path / "standard-demo.csv")

    with pytest.raises(ValueError, match="Confirm authorization"):
        execute_csv_upload(
            csv_path,
            "Y",
            "X",
            "Z",
            False,
            20260813,
            output_root=tmp_path / "runs",
            token_file=tmp_path / "missing-token",
        )

    assert not (tmp_path / "runs").exists()


def test_csv_upload_rejects_extra_columns_and_discrete_treatment(tmp_path: Path) -> None:
    extra_path = tmp_path / "extra.csv"
    with extra_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Y", "X", "Z", "W"))
        writer.writerows((index, index / 10, index / 20, 1.0) for index in range(120))
    with pytest.raises(ValueError, match="exactly the three selected"):
        load_authorized_csv(
            extra_path,
            outcome="Y",
            treatment="X",
            instrument="Z",
            confirmed=True,
        )

    discrete_path = tmp_path / "discrete.csv"
    with discrete_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Y", "X", "Z"))
        writer.writerows((index / 7, index % 2, index / 20) for index in range(120))
    with pytest.raises(ValueError, match="treatment X must have at least"):
        load_authorized_csv(
            discrete_path,
            outcome="Y",
            treatment="X",
            instrument="Z",
            confirmed=True,
        )


def test_weak_website_scenario_preserves_empirical_warnings(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    result = execute_portfolio_scenario(
        "weak_iv",
        160,
        20260810,
        output_root=tmp_path,
        **managed_client,
    )
    warning_codes = {warning.code for warning in result.response.queries[0].warnings}
    assert result.response.status == "completed"
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" in warning_codes
    assert "WEAK_INTERVENTION_SUPPORT" in warning_codes
    status, _, answer, evidence, plot = format_portfolio_result(result)
    assert "demo-status--warning" in status
    assert "Weak instrument signal" in evidence
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" not in evidence
    assert "weak_support" not in "\n".join((status, answer, evidence))
    assert plot is not None
    assert verify_run_directory(result.output_dir)["status"] == "valid"


def test_outside_support_executes_real_gate_and_renders_without_number(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    result = execute_portfolio_scenario(
        "support_violation",
        160,
        20260810,
        output_root=tmp_path,
        **managed_client,
    )
    assert result.response.status == "blocked"
    assert result.response.final_state is AgentState.BLOCKED
    assert result.response.queries == ()
    assert result.response.error is not None
    assert result.response.error["code"] == ErrorCode.OUTSIDE_SUPPORT.value
    assert result.plot_path is None
    assert result.output_dir is None
    assert not list(tmp_path.rglob("run-*"))

    status, states, answer, evidence, plot = format_portfolio_result(result)
    assert ErrorCode.OUTSIDE_SUPPORT.value not in status
    assert "Outside observed data support" in status
    assert "Safety check stopped" in states
    assert "No numerical answer" in answer
    assert "No result details" in evidence
    assert plot is None


def test_managed_failure_never_falls_back_to_sklearn(tmp_path: Path) -> None:
    class FailingRegressor(FakeClientRegressor):
        def fit(self, features: np.ndarray, target: np.ndarray):
            raise RuntimeError("synthetic managed failure")

    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    client = FakeClientModule()
    client.TabPFNRegressor = FailingRegressor

    result = execute_portfolio_scenario(
        "strong_iv",
        128,
        20260810,
        output_root=tmp_path,
        token_file=token_file,
        client_module=client,
        client_version=MANAGED_CLIENT_VERSION,
        gemini_api_key_file=gemini_key_file,
        gemini_client=FakeGeminiClient(),
        gemini_sdk_version=GOOGLE_GENAI_VERSION,
    )

    assert result.response.status == "blocked"
    assert result.response.error is not None
    assert result.response.error["code"] == ErrorCode.BACKEND_FIT_FAILED.value
    assert result.response.queries == ()
    assert result.output_dir is None
    assert not list(tmp_path.rglob("numerical_core.json"))
    assert client.reset_called

    status, states, answer, evidence, plot = format_portfolio_result(result)
    assert ErrorCode.BACKEND_FIT_FAILED.value not in status
    assert "temporarily unavailable" in status
    assert "Safety check stopped" in states
    assert "No numerical answer" in answer
    assert "No result details" in evidence
    assert plot is None


def test_gemini_failure_stops_before_managed_fit_or_output(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    FakeClientRegressor.prediction_calls = 0
    managed_client["gemini_client"] = FakeGeminiClient(raises=True)

    with pytest.raises(DCFAError) as raised:
        execute_portfolio_scenario(
            "strong_iv",
            128,
            20260815,
            output_root=tmp_path / "runs",
            **managed_client,
        )

    assert raised.value.code == ErrorCode.LLM_API_FAILED
    assert len(managed_client["gemini_client"].interactions.calls) == 1
    assert FakeClientRegressor.prediction_calls == 0
    assert managed_client["client_module"].reset_called
    assert not (tmp_path / "runs").exists()

    visitor_outputs = _execution_error_outputs(raised.value)
    visitor_text = "\n".join(value for value in visitor_outputs if isinstance(value, str))
    assert "Analysis service is temporarily unavailable" in visitor_text
    assert ErrorCode.LLM_API_FAILED.value not in visitor_text
    assert raised.value.stage not in visitor_text
    assert "synthetic Gemini failure" not in visitor_text


def test_gemini_clarification_stops_without_exposing_model_reason(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    managed_client["gemini_client"] = FakeGeminiClient(
        _valid_gemini_proposal(
            decision="clarify",
            reason="The requested summary is ambiguous.",
        )
    )

    with pytest.raises(DCFAError) as raised:
        execute_portfolio_scenario(
            "strong_iv",
            128,
            20260815,
            question="Tell me what happens.",
            output_root=tmp_path / "runs",
            **managed_client,
        )

    assert raised.value.code == ErrorCode.LLM_OUTPUT_INVALID
    assert raised.value.stage == "website_demo.gemini_decision"
    assert raised.value.context == {"decision": "clarify"}
    assert "ambiguous" not in raised.value.message
    assert FakeClientRegressor.prediction_calls == 0
    assert not (tmp_path / "runs").exists()


def test_gemini_proposal_selects_the_deterministic_query(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    managed_client["gemini_client"] = FakeGeminiClient(
        _valid_gemini_proposal(
            reason="Compile the mean at center treatment.",
            objective="mean",
            x_label="center",
            comparison_x_label="none",
            level_label="none",
        )
    )

    result = execute_portfolio_scenario(
        "strong_iv",
        128,
        20260815,
        question="What is the mean outcome at the center treatment level?",
        output_root=tmp_path / "runs",
        **managed_client,
    )

    assert result.response.status == "completed"
    assert result.response.queries[0].claim_type == "interventional_mean"
    assert result.llm_trace["proposal"]["objective"] == "mean"
    assert result.llm_trace["proposal"]["x_label"] == "center"


def test_run_directories_are_reserved_atomically(tmp_path: Path) -> None:
    def reserve(_: int) -> Path:
        return _reserve_output_directory(tmp_path, "strong_iv", 17)

    with ThreadPoolExecutor(max_workers=8) as executor:
        paths = tuple(executor.map(reserve, range(16)))

    assert len(paths) == len(set(paths)) == 16
    assert all(path.is_dir() for path in paths)
    assert {path.name for path in paths} == {f"run-{index:04d}" for index in range(1, 17)}


def test_bounded_controls_reject_invalid_values_before_allocating_output(
    tmp_path: Path,
    managed_client: dict[str, Any],
) -> None:
    for rows, seed in (
        (119, 1),
        (MAX_DEMO_ROWS + 1, 1),
        (160, -1),
        (160, MAX_DEMO_SEED + 1),
    ):
        try:
            execute_portfolio_scenario(
                "strong_iv", rows, seed, output_root=tmp_path, **managed_client
            )
        except ValueError as exc:
            raw_message = str(exc)
            status, states, answer, evidence, plot = _input_error_outputs(raw_message)
        else:  # pragma: no cover - makes an unexpected fit an explicit test failure
            raise AssertionError("Invalid controls unexpectedly executed the workflow.")
        assert "Input needs attention" in status
        assert raw_message not in status
        assert "No workflow progress" in states
        assert "No numerical answer" in answer
        assert "No numerical result" in evidence
        assert plot is None
    assert not list(tmp_path.rglob("run-*"))


def test_default_app_config_omits_machine_audit_payload_and_shows_build() -> None:
    app = build_app(build_revision="deadbee")
    config = json.dumps(app.config, sort_keys=True)

    assert "Build deadbee" in config
    for forbidden in (
        "Agent trace",
        "Machine-readable state and identity",
        "specification_id",
        "result_bundle_id",
        "token_usage",
        "state_events",
    ):
        assert forbidden not in config


def test_build_revision_accepts_short_commit_and_safe_container_fallback(monkeypatch) -> None:
    monkeypatch.setenv("DCFA_BUILD_REVISION", "deadbee")
    assert resolve_build_revision() == "deadbee"
    monkeypatch.setenv("DCFA_BUILD_REVISION", "unknown")
    assert resolve_build_revision() == "unknown"


def test_port_preflight_reports_an_existing_local_instance() -> None:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind(("127.0.0.1", 0))
        port = occupied.getsockname()[1]
        with pytest.raises(RuntimeError, match=f"127.0.0.1:{port} is already in use"):
            require_available_port("127.0.0.1", port)


def test_health_endpoint_identifies_development_service_and_security_headers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))
    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    monkeypatch.setenv("DCFA_TABPFN_TOKEN_FILE", str(token_file))
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    monkeypatch.setenv("DCFA_GEMINI_API_KEY_FILE", str(gemini_key_file))

    async def get(path: str) -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)

    response = asyncio.run(get("/healthz"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["evidence_status"] == "development_only"
    assert response.json()["backend"] == "tabpfn_client_managed"
    assert response.json()["model"] == "v2.5_default"
    assert response.json()["llm_model"] == "gemini-3.6-flash"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"

    ready = asyncio.run(get("/readyz"))
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["output_root_writable"] is True
    assert ready.json()["managed_credential_ready"] is True
    assert ready.json()["gemini_credential_ready"] is True
    assert ready.json()["gemini_config_ready"] is True


def test_readiness_fails_when_output_root_has_no_directory_parent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", "/dev/null/dcfa-output")
    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    monkeypatch.setenv("DCFA_TABPFN_TOKEN_FILE", str(token_file))
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    monkeypatch.setenv("DCFA_GEMINI_API_KEY_FILE", str(gemini_key_file))

    async def get_readiness() -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/readyz")

    response = asyncio.run(get_readiness())
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["output_root_writable"] is False
    assert response.json()["managed_credential_ready"] is True
    assert response.json()["gemini_credential_ready"] is True


def test_readiness_fails_closed_without_managed_credential(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))
    monkeypatch.setenv("DCFA_TABPFN_TOKEN_FILE", str(tmp_path / "missing-token"))
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    monkeypatch.setenv("DCFA_GEMINI_API_KEY_FILE", str(gemini_key_file))

    async def get_readiness() -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/readyz")

    response = asyncio.run(get_readiness())
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["output_root_writable"] is True
    assert response.json()["managed_credential_ready"] is False
    assert response.json()["gemini_credential_ready"] is True


def test_readiness_fails_closed_without_gemini_credential(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))
    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    monkeypatch.setenv("DCFA_TABPFN_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("DCFA_GEMINI_API_KEY_FILE", str(tmp_path / "missing-gemini-key"))

    async def get_readiness() -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/readyz")

    response = asyncio.run(get_readiness())
    assert response.status_code == 503
    assert response.json()["managed_credential_ready"] is True
    assert response.json()["gemini_credential_ready"] is False


def test_readiness_fails_closed_without_gemini_profile(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))
    token_file = tmp_path / "tabpfn-token"
    token_file.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    token_file.chmod(0o600)
    gemini_key_file = tmp_path / "gemini-key"
    gemini_key_file.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key_file.chmod(0o600)
    monkeypatch.setenv("DCFA_TABPFN_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("DCFA_GEMINI_API_KEY_FILE", str(gemini_key_file))
    monkeypatch.setenv(
        "DCFA_WEBSITE_GEMINI_CONFIG_FILE",
        str(tmp_path / "missing-gemini-profile.json"),
    )

    async def get_readiness() -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/readyz")

    response = asyncio.run(get_readiness())
    assert response.status_code == 503
    assert response.json()["managed_credential_ready"] is True
    assert response.json()["gemini_credential_ready"] is True
    assert response.json()["gemini_config_ready"] is False
