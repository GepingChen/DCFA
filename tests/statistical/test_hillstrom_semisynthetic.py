from __future__ import annotations

from dataclasses import replace

import pytest

from dcfa.artifact_validation import verify_run_directory
from dcfa.errors import DCFAError, ErrorCode
from dcfa.hillstrom_policy.data import generate_development_rct, make_stratified_split
from dcfa.hillstrom_policy.semisynthetic import SEMISYNTHETIC_SCENARIOS, run_four_scenarios
from dcfa.hillstrom_policy.semisynthetic_pipeline import run_semisynthetic_benchmark


def test_four_semisynthetic_scenarios_have_same_constraint_oracles() -> None:
    dataset = generate_development_rct(n=900, seed=41)
    split = make_stratified_split(dataset, seed=42)
    results = run_four_scenarios(
        dataset,
        split,
        replications=2,
        row_count=600,
        seed=43,
    )
    assert {result.scenario for result in results} == set(SEMISYNTHETIC_SCENARIOS)
    assert len(results) == 8
    for result in results:
        assert result.data_label == "development_synthetic_not_hillstrom_calibrated"
        assert result.learned_regret >= 0.0
        assert result.best_uniform_regret >= 0.0
        assert result.oracle_value >= result.learned_policy_value - 1e-10
        assert result.oracle_value >= result.best_uniform_value - 1e-10
        assert 0.0 <= result.optimal_action_accuracy <= 1.0
        assert result.selective_regret >= 0.0
        assert result.fallback_inclusive_value == result.learned_policy_value
        assert result.action_value_gap_mae >= 0.0
        assert sum(sum(row) for row in result.action_confusion_matrix) == pytest.approx(1.0)
        assert result.constraint_violations == 0


def test_semisynthetic_aggregates_have_evidence_and_verified_artifacts(tmp_path) -> None:
    dataset = generate_development_rct(n=900, seed=51)
    split = make_stratified_split(dataset, seed=52)
    run = run_semisynthetic_benchmark(
        dataset,
        split,
        replications=2,
        row_count=600,
        seed=53,
        output_dir=tmp_path,
    )
    assert len(run.replications) == 8
    assert len(run.bundle.values) == 84
    assert len(run.ledger.records()) == 84
    assert all(estimate.evidence_id for estimate in run.bundle.values)
    assert verify_run_directory(tmp_path)["status"] == "valid"


def test_semisynthetic_entrypoint_rejects_stale_raw_data_hash(tmp_path) -> None:
    dataset = generate_development_rct(n=900, seed=61)
    split = make_stratified_split(dataset, seed=62)
    tampered = replace(dataset, spend=(dataset.spend[0] + 1.0, *dataset.spend[1:]))
    with pytest.raises(DCFAError) as exc_info:
        run_semisynthetic_benchmark(
            tampered,
            split,
            replications=1,
            row_count=600,
            seed=63,
            output_dir=tmp_path,
        )
    assert exc_info.value.code is ErrorCode.HASH_MISMATCH
    assert not any(tmp_path.iterdir())
