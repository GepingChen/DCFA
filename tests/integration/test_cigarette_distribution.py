"""Exact-price composite requests use fake predictions only; never real GPU evidence."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from dcfa.agent.compiler import CompilationRequest, SpecificationCompiler
from dcfa.artifact_validation import verify_run_directory
from dcfa.constants import EstimatorBackend
from dcfa.distribution_reporting import export_distribution
from dcfa.errors import DCFAError
from dcfa.tabcf_iv.backend import TabPFNBackend
from dcfa.tabcf_iv.distribution import derive_distribution
from dcfa.tabcf_iv.pipeline import TabCFAnalysisEngine, predict_backend
from dcfa_website_demo.app import execute_prepared_local_csv, format_portfolio_result
from dcfa_website_demo.csv_upload import (
    CSVDataBoundary,
    assign_csv_roles,
    read_authorized_csv_columns,
)
from dcfa_website_demo.dialogue import CSVConversation, prepare_turn
from dcfa_website_demo.gemini import GeminiWebsiteCompilation
from dcfa_website_demo.numeric_request import numeric_proposal
from tests.unit import test_backend_contract

fake_tabpfn = test_backend_contract.fake_tabpfn

CSV = Path("examples/cigarette_demand_small/cigarette_144.csv")
COLUMNS = ("log_packs_per_capita", "log_real_price", "real_sales_tax")
PROMPT = (
    "Use log_packs_per_capita as Y, log_real_price as X, real_sales_tax as Z; no W. "
    "Price from 100 to 120 CPI-deflated cents per pack. "
    "The CSV already contains natural-log sales and natural-log real prices. "
    "Return both CDFs, quantiles .25/.50/.75/.90, second minus first differences in "
    "packs per person per year, probability exceeding 120 packs per person per year, "
    "percentage-point difference and 90th change minus median change."
)


def proposal():
    return {
        "decision": "analyze",
        "reason": "Explicit distribution request",
        "outcome": COLUMNS[0],
        "treatment": COLUMNS[1],
        "instrument": COLUMNS[2],
        "treatment_type": "continuous",
        "objective": "distribution",
        "x_label": "exact",
        "comparison_x_label": "exact",
        "level_label": "quartiles_and_upper",
        "distribution": {
            "prices": [100, 120],
            "threshold": 120,
            "treatment_units": "CPI-deflated cents per pack",
            "outcome_units": "packs per person per year",
            "treatment_scale": "stored_natural_log",
            "outcome_scale": "stored_natural_log",
            "scale_quote": "The CSV already contains natural-log sales and "
            "natural-log real prices.",
        },
    }


def compilation():
    p, values, d = numeric_proposal(proposal(), [{"role": "user", "content": PROMPT}], COLUMNS, {})
    trace = {
        "proposal": p,
        "model_request_count": 1,
        "confirmed_roles": {
            role: {"column": column, "column_position": i + 1, "definition": "Not provided"}
            for i, (role, column) in enumerate(
                zip(("outcome", "treatment", "instrument"), COLUMNS, strict=True)
            )
        },
    }
    return GeminiWebsiteCompilation(*values, trace=trace, distribution=d)


def dataset():
    validated = read_authorized_csv_columns(
        CSV, confirmed=True, data_boundary=CSVDataBoundary.HF_ZEROGPU_LOCAL
    )
    return validated, assign_csv_roles(
        validated, outcome=COLUMNS[0], treatment=COLUMNS[1], instrument=COLUMNS[2]
    )


def request():
    _, data = dataset()
    grid = (math.log(100), math.log(120))
    return CompilationRequest(
        dataset_hash=data.manifest.dataset_hash,
        outcome=COLUMNS[0],
        treatment=COLUMNS[1],
        instrument=COLUMNS[2],
        objective="distribution",
        intervention_grid=grid,
        x=grid[1],
        comparison_x=grid[0],
        distribution=compilation().distribution,
        estimator_backend=EstimatorBackend.TABPFN,
        seed=20260920,
    )


def test_compile_units_card_and_no_fit():
    from dcfa_website_demo.dialogue import plan_html

    c = compilation()
    card = plan_html(c)
    assert "4.60517018598809" in card and "4.78749174278204" in card
    assert "CPI-deflated cents per pack" in card and "not transformed again" in card
    assert "percentiles" not in card
    spec = SpecificationCompiler().compile(request()).specification
    assert spec.intervention_grid == (math.log(100), math.log(120))
    assert spec.quantile_levels == (0.25, 0.5, 0.75, 0.9)
    assert spec.risk_thresholds == (math.log(120),)
    for grid in ((100.0, 120.0), (math.log(math.log(100)), math.log(math.log(120)))):
        with pytest.raises(DCFAError):
            SpecificationCompiler().compile(replace(request(), intervention_grid=grid))
    session = CSVConversation()
    prepare_turn(session, str(CSV), PROMPT, {}, True, lambda *a: ("Review plan", c))
    prepare_turn(session, str(CSV), "确认", {}, True, lambda *a: ("Use the button", c))
    assert session.status == "ready"


@pytest.mark.parametrize("change", ["symbolic", "scale", "price", "units", "missing_quote"])
def test_numeric_substitutions_rejected(change):
    p = proposal()
    if change == "symbolic":
        p.pop("distribution")
        p.update(
            objective="quantile_contrast",
            x_label="high",
            comparison_x_label="low",
            level_label="median",
        )
    elif change == "scale":
        p["distribution"]["treatment_scale"] = "log_csv_again"
    elif change == "price":
        p["distribution"]["prices"] = [math.log(100), math.log(120)]
    elif change == "units":
        p["distribution"]["treatment_units"] = "nominal cents"
    else:
        p["distribution"]["scale_quote"] = "natural log inferred from column name"
    with pytest.raises((ValueError, DCFAError)):
        numeric_proposal(p, [{"role": "user", "content": PROMPT}], COLUMNS, {})


def test_nontrivial_original_unit_hand_calculation():
    d = compilation().distribution
    y = np.log([10.0, 100.0, 200.0])
    f = [[0.1, 0.5, 0.95], [0.2, 0.6, 0.9]]
    q = np.log([[40.0, 80.0, 130.0, 170.0], [35.0, 90.0, 120.0, 145.0]])
    result = derive_distribution(d, y, f, q, [[0.7], [0.8]])
    m = {v["key"]: v["value"] for v in result["metrics"]}
    assert m["quantile_difference:0.5"] == pytest.approx(10)
    assert m["quantile_difference:0.9"] == pytest.approx(-25)
    assert m["upper_minus_middle_change"] == pytest.approx(-35)
    assert m["exceedance:0"] == pytest.approx(30)
    assert m["exceedance:1"] == pytest.approx(20)
    assert m["exceedance_difference"] == pytest.approx(-10)
    assert "mixed signs" in result["summary"] and "curves cross" in result["summary"]
    assert np.allclose(result["outcome_axis"], [10, 100, 200])
    q[1, 3] = y[-1]
    limited = derive_distribution(d, y, f, q, [[0.7], [0.8]])
    assert limited["quantiles"][3]["boundary_limited"] == [False, True]
    assert "no resolved" in limited["summary"]


@pytest.fixture
def wide_fake_ranks(fake_tabpfn, monkeypatch):
    from dcfa.tabcf_iv.backend import TabPFNDistributionModel

    original = TabPFNDistributionModel.cdf

    def cdf(self, features, values, *, paired):
        result = original(self, features, values, paired=paired)
        if paired:
            # A deliberately broad fake first-stage CDF exercises the success path.
            # Production support rules and all CSV values remain unchanged.
            return np.random.default_rng(15).permutation(np.linspace(0.01, 0.99, len(features)))
        return result

    monkeypatch.setattr(TabPFNDistributionModel, "cdf", cdf)
    return fake_tabpfn


def test_composite_fake_tabpfn_two_fits_cache_and_artifact(wide_fake_ranks, tmp_path):
    fake_tabpfn = wide_fake_ranks
    _, data = dataset()
    spec = SpecificationCompiler().compile(request()).specification
    engine = TabCFAnalysisEngine(
        backend_factory=lambda s: TabPFNBackend(seed=s.seed, execution_profile=s.execution_profile)
    )
    run = engine.analyze(data.columns, spec, data.manifest, output_dir=tmp_path / "run")
    assert run.backend_fit_calls == 2
    assert len(fake_tabpfn) == 2 and all(m.fits == 1 for m in fake_tabpfn)
    assert set(fake_tabpfn[1].outputs) == {"mean", "full"}
    assert len(run.bundle.x_grid) == 2 and len(run.bundle.y_grid) == 161
    assert len(run.bundle.queries) == 340
    for q in run.bundle.queries:
        assert engine.follow_up(spec, q.query_id) == q
        assert run.ledger.resolve(q.evidence_id).value_raw == q.value_raw
    assert engine.analyze(data.columns, spec, data.manifest).backend_fit_calls == 0
    assert len(fake_tabpfn) == 2
    assert verify_run_directory(tmp_path / "run")["status"] == "valid"
    exported = json.loads((tmp_path / "run/distribution_results.json").read_text())
    assert exported["distribution"]["quantiles"] == run.bundle.distribution["quantiles"]
    assert len(export_distribution(run.bundle, run.ledger)["evidence"]) == 340
    assert any(w.code == "QUANTILE_GRID_ENDPOINT" for w in run.bundle.warnings)


def test_csv_composite_cpu_finalize(wide_fake_ranks, monkeypatch, tmp_path):
    fake_tabpfn = wide_fake_ranks
    monkeypatch.setattr(
        "dcfa_website_demo.app.make_local_tabpfn_v2_backend",
        lambda s, **k: TabPFNBackend(seed=s.seed, execution_profile=s.execution_profile),
    )
    stages = []

    def gpu(backend, stage, *args):
        stages.append(stage)
        return predict_backend(backend, stage, *args)

    validated, _ = dataset()
    result = execute_prepared_local_csv(
        validated,
        compilation(),
        20260920,
        model_path=tmp_path / "fake",
        prediction_runner=gpu,
        output_root=tmp_path / "runs",
    )
    assert result.response.status == "completed", result.response.error
    assert stages == ["stage1", "stage2"]
    assert len(fake_tabpfn) == 2
    assert verify_run_directory(result.output_dir)["status"] == "valid"
    rendered = format_portfolio_result(result)
    assert "percentage points" in rendered[2] and rendered[4]
    assert "Boundary-limited" in rendered[2]

    import zipfile

    from dcfa_website_demo.zerogpu import _verified_projection

    packaged = _verified_projection(result, None)
    assert not result.output_dir.exists()
    archive = Path(packaged[5]["value"])
    with zipfile.ZipFile(archive) as z:
        z.extractall(tmp_path / "download")
    extracted = next((tmp_path / "download").rglob("distribution_results.json")).parent
    assert verify_run_directory(extracted)["status"] == "valid"
    archive.unlink()
    Path(packaged[4]["value"]).unlink()


def test_narrow_fake_rank_support_refuses_before_stage2(fake_tabpfn, tmp_path):
    _, data = dataset()
    spec = SpecificationCompiler().compile(request()).specification
    engine = TabCFAnalysisEngine(
        backend_factory=lambda s: TabPFNBackend(seed=s.seed, execution_profile=s.execution_profile)
    )
    with pytest.raises(DCFAError, match="unsupported"):
        engine.analyze(data.columns, spec, data.manifest, output_dir=tmp_path / "blocked")
    assert len(fake_tabpfn) == 1 and fake_tabpfn[0].fits == 1
    assert not (tmp_path / "blocked/result_bundle.json").exists()


def test_full_dialogue_compilation_uses_one_fake_request(tmp_path):
    from dcfa_website_demo.dialogue import compile_csv_turn
    from tests.provider_fakes import FakeGeminiClient

    client = FakeGeminiClient()
    client.interactions.output_text = json.dumps(
        {
            "decision": "ready",
            "message": "Review the exact prices and units.",
            "proposal": proposal(),
            "definitions": {"outcome": "", "treatment": "", "instrument": ""},
        }
    )
    key = tmp_path / "key"
    key.write_text("fake-key-not-a-real-provider-credential")
    key.chmod(0o600)
    calls = []
    _, c = compile_csv_turn(
        [{"role": "user", "content": PROMPT}],
        COLUMNS,
        {},
        api_key_file=key,
        on_request=lambda: calls.append(1),
        client=client,
    )
    assert c.distribution.prices == (100, 120)
    assert len(calls) == len(client.interactions.calls) == 1
    assert "rows" not in json.loads(client.interactions.calls[0]["input"])


def test_csv_handler_cached_followup_and_repeated_click(tmp_path, monkeypatch):
    monkeypatch.setenv("GRADIO_TEMP_DIR", str(tmp_path))
    from types import SimpleNamespace

    import gradio as gr

    from tests.integration.test_csv_dialogue import handlers

    path = tmp_path / "copy.csv"
    path.write_bytes(CSV.read_bytes())
    c = compilation()
    calls = []
    executions = []

    def chat(*args):
        calls.append(True)
        return "Review the plan", c

    def execute(*args):
        executions.append(True)
        return tuple(gr.update(value="Cached evidence-backed report") for _ in range(9))

    h = handlers(chat, execute)
    session = CSVConversation()
    profile = SimpleNamespace(username="alice")
    h["talk"](session, str(path), "fake-key", "", "", "", True, PROMPT, profile)
    args = (session, str(path), "", "", "", True, 20260920, session.revision, profile)
    completed = list(h["generate"](*args))[-1]
    assert session.cached_answer and session.validated is None
    assert completed[5]["value"] == ""
    assert not path.exists()
    list(h["generate"](*args))
    reply = h["talk"](session, None, "", "", "", "", True, "Explain the tail", profile)
    assert "Cached report" in reply[1][-1]["content"]
    assert calls == executions == [True]
    assert h["reset_session"](session)[0].cached_answer is None


def test_actual_cpu_finalize_failure_does_not_retry_fits(wide_fake_ranks, monkeypatch, tmp_path):
    from dcfa_website_demo.app import WebsiteFinalizationError

    monkeypatch.setattr(
        "dcfa_website_demo.app.make_local_tabpfn_v2_backend",
        lambda s, **k: TabPFNBackend(seed=s.seed, execution_profile=s.execution_profile),
    )

    def fail(*a, **kw):
        raise RuntimeError("fake CPU rendering failure")

    monkeypatch.setattr("dcfa.distribution_reporting.render_distribution_plot", fail)
    validated, _ = dataset()
    with pytest.raises(WebsiteFinalizationError, match="fake CPU"):
        execute_prepared_local_csv(
            validated,
            compilation(),
            20260920,
            model_path=tmp_path / "fake",
            prediction_runner=predict_backend,
            output_root=tmp_path / "runs",
        )
    assert len(wide_fake_ranks) == 2
    assert not list((tmp_path / "runs").rglob("*.json"))
