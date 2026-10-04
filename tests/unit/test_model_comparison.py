from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.special import ndtr, ndtri

from dcfa.tabcf_iv import model_comparison as comparison


def test_oracle_scoring_and_probability_direction():
    x = np.asarray([-0.5, 0.0, 0.5])
    mean = 0.8 + 1.4 * x + 0.25 * x * x
    sd = np.sqrt(0.9**2 + 0.6**2)
    grid = np.linspace(-10, 10, 401)
    levels = [0.1, 0.5, 0.9]
    bundle = dict(
        x_grid=x,
        y_grid=grid,
        quantile_levels=levels,
        interventional_mean=mean,
        interventional_cdf=ndtr((grid[None, :] - mean[:, None]) / sd),
        interventional_quantiles=mean[:, None] + sd * ndtri(levels),
    )
    assert all(v < 1e-14 for v in comparison.score_bundle(bundle, 0).values())
    bundle["interventional_mean"] = mean + 2
    assert comparison.score_bundle(bundle, 0)["mean_rmse"] == pytest.approx(2)


def test_partial_pairs_keep_failures_and_signed_regressions():
    records = [
        dict(
            seed=comparison.SEEDS[0],
            model=mode,
            status="completed",
            grid={},
            metrics={m: v for m in comparison.METRICS},
        )
        for mode, v in [("api_only", 2.0), ("v2_only", 1.0)]
    ]
    records.append(dict(seed=comparison.SEEDS[1], model="api_only", status="blocked"))
    result = comparison.summarize(records)
    assert result["completed_pairs"] == 1
    assert result["aggregate"]["cdf_rmse"]["mean_difference"] == 1
    assert result["aggregate"]["cdf_rmse"]["seed_standard_error"] is None
    assert result["arms"][-1]["status"] == "blocked"


def test_resume_never_resubmits_recorded_or_ambiguous_attempts(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("dcfa_website_demo.daily.archive_daily_result", lambda result: None)

    def executor(*, mode, compiled_kwargs, managed_settings):
        calls.append((compiled_kwargs["seed"], mode))
        return SimpleNamespace(
            response=SimpleNamespace(status="blocked", error={"code": "OUTSIDE_SUPPORT"}),
            output_dir=compiled_kwargs["output_root"],
            llm_trace={"daily_execution": {"attempts": [{}], "actual_model": None}},
        )

    root = tmp_path / "run"
    comparison.run_comparison(root, executor=executor)
    assert len(calls) == 10
    comparison.run_comparison(root, resume=True, executor=executor)
    assert len(calls) == 10
    path = root / f"seed-{comparison.SEEDS[0]}" / "api_only" / "measurement.json"
    path.unlink()  # Simulate interruption after submission, before local completion.
    result = comparison.run_comparison(root, resume=True, executor=executor)
    assert len(calls) == 10
    assert result["arms"][0]["status"] == "interrupted_execution_not_resubmitted"
    with pytest.raises(ValueError, match="fresh"):
        comparison.run_comparison(root, executor=executor)


def test_quota_stops_remaining_arms(tmp_path, monkeypatch):
    monkeypatch.setattr("dcfa_website_demo.daily.archive_daily_result", lambda result: None)
    calls = []

    def executor(*, mode, compiled_kwargs, managed_settings):
        calls.append(mode)
        return SimpleNamespace(
            response=SimpleNamespace(status="blocked", error={"code": "MANAGED_QUOTA_EXHAUSTED"}),
            output_dir=compiled_kwargs["output_root"],
            llm_trace={
                "daily_execution": {"attempts": [{}], "error_code": "MANAGED_QUOTA_EXHAUSTED"}
            },
        )

    result = comparison.run_comparison(tmp_path / "quota", executor=executor)
    assert calls == ["api_only"]
    assert sum(r["status"] == "not_run_quota" for r in result["arms"]) == 9
    saved = json.loads((tmp_path / "quota" / "summary.json").read_text())
    assert saved["completed_pairs"] == 0
