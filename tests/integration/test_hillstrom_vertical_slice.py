from __future__ import annotations

import json
from dataclasses import replace

import pytest

from dcfa.artifact_validation import verify_run_directory
from dcfa.errors import DCFAError, ErrorCode
from dcfa.evidence import validate_track_h_release
from dcfa.hillstrom_policy.contracts import HillstromPolicySpecification, PolicyObjective
from dcfa.hillstrom_policy.data import generate_development_rct, make_stratified_split
from dcfa.hillstrom_policy.pipeline import HillstromPolicyEngine


def _run(tmp_path=None):
    dataset = generate_development_rct(n=900, seed=21)
    split = make_stratified_split(dataset, seed=22)
    specification = HillstromPolicySpecification(
        dataset_hash=dataset.manifest.dataset_hash,
        split_manifest_id=split.split_manifest_id,
        objective=PolicyObjective(),
        seed=23,
    )
    run = HillstromPolicyEngine().analyze(
        dataset,
        split,
        specification,
        output_dir=tmp_path,
    )
    return dataset, run


def test_vertical_slice_freezes_then_evaluates_with_three_estimators(tmp_path) -> None:
    _dataset, run = _run(tmp_path)
    assert run.test_outcomes_accessed_after_freeze
    assert len(run.bundle.values) == 16
    assert len(run.bundle.contrasts) == 6
    assert len(run.bundle.experimental_effects) == 9
    assert len(run.ledger.records()) == 31
    assert run.bundle.missingness_status == "validated_zero_missing_or_nonfinite_values"
    assert sum(count for _action, count, _share in run.bundle.action_allocations) == (
        run.bundle.test_row_count
    )
    assert len(run.bundle.baseline_balance) == 7
    event_types = [event.event_type for event in run.audit.events()]
    assert event_types.index("policy_frozen") < event_types.index("test_outcomes_unlocked")
    result = verify_run_directory(tmp_path)
    assert result["status"] == "valid"
    assert result["track"] == "hillstrom_policy"
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "H0 data audit" in report
    assert "Frozen operational specification and allocation" in report
    assert "## Assumptions" in report


def test_artifact_verifier_recomputes_backend_manifest_identity(tmp_path) -> None:
    _dataset, _run_result = _run(tmp_path)
    path = tmp_path / "run_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["backend_manifest_id"] = "backend_tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(DCFAError) as exc_info:
        verify_run_directory(tmp_path)
    assert exc_info.value.code is ErrorCode.HASH_MISMATCH


def test_development_fixture_is_rejected_by_track_h_release_gate() -> None:
    dataset, run = _run()
    with pytest.raises(DCFAError) as exc_info:
        validate_track_h_release(
            run.bundle,
            run.ledger,
            dataset.manifest,
            run.policy_artifact,
        )
    assert exc_info.value.code is ErrorCode.RELEASE_GATE_FAILED
    assert "not_real_randomized_experiment" in exc_info.value.context["failures"]


def test_hillstrom_run_is_deterministic() -> None:
    _dataset_one, run_one = _run()
    _dataset_two, run_two = _run()
    assert run_one.bundle == run_two.bundle
    assert run_one.policy_artifact == run_two.policy_artifact


def test_hillstrom_rejects_superseded_protocol_version() -> None:
    dataset = generate_development_rct(n=600, seed=64)
    split = make_stratified_split(dataset, seed=65)
    specification = HillstromPolicySpecification(
        dataset_hash=dataset.manifest.dataset_hash,
        split_manifest_id=split.split_manifest_id,
        objective=PolicyObjective(),
        specification_version="hillstrom_policy_v4",
    )
    with pytest.raises(DCFAError) as exc_info:
        HillstromPolicyEngine().analyze(dataset, split, specification)
    assert exc_info.value.code is ErrorCode.INVALID_SPECIFICATION


@pytest.mark.parametrize(
    ("specification_change", "expected_code"),
    [
        ("margin", ErrorCode.INVALID_SPECIFICATION),
        ("propensity", ErrorCode.INVALID_SPECIFICATION),
        ("capacity", ErrorCode.CONSTRAINT_VIOLATION),
    ],
)
def test_policy_specification_fields_cannot_be_silently_ignored(
    tmp_path,
    specification_change: str,
    expected_code: ErrorCode,
) -> None:
    dataset = generate_development_rct(n=600, seed=71)
    split = make_stratified_split(dataset, seed=72)
    specification = HillstromPolicySpecification(
        dataset_hash=dataset.manifest.dataset_hash,
        split_manifest_id=split.split_manifest_id,
        objective=PolicyObjective(),
        seed=73,
    )
    if specification_change == "margin":
        specification = replace(
            specification,
            objective=replace(specification.objective, margin=0.5),
        )
    elif specification_change == "propensity":
        specification = replace(specification, propensity_source="fitted_propensity")
    else:
        specification = replace(specification, capacity_fraction=float("nan"))
    with pytest.raises(DCFAError) as exc_info:
        HillstromPolicyEngine().analyze(
            dataset,
            split,
            specification,
            output_dir=tmp_path / specification_change,
        )
    assert exc_info.value.code is expected_code
    assert not (tmp_path / specification_change).exists()
