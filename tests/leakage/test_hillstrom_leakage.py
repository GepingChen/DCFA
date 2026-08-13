from __future__ import annotations

from dataclasses import replace

import pytest

from dcfa.canonical import sha256_digest
from dcfa.errors import DCFAError, ErrorCode
from dcfa.hillstrom_policy.contracts import HillstromPolicySpecification, PolicyObjective
from dcfa.hillstrom_policy.data import (
    TestOutcomeGate as OutcomeGate,
)
from dcfa.hillstrom_policy.data import (
    fit_preprocessor,
    generate_development_rct,
    load_hillstrom_csv,
    make_stratified_split,
)
from dcfa.hillstrom_policy.pipeline import HillstromPolicyEngine
from dcfa.hillstrom_policy.policies import fit_frozen_policy


def _fixture():
    dataset = generate_development_rct(n=600, seed=11)
    split = make_stratified_split(dataset, seed=12)
    specification = HillstromPolicySpecification(
        dataset_hash=dataset.manifest.dataset_hash,
        split_manifest_id=split.split_manifest_id,
        objective=PolicyObjective(),
        seed=13,
    )
    return dataset, split, specification


def test_split_is_disjoint_complete_and_feature_schema_excludes_outcomes() -> None:
    dataset, split, _specification = _fixture()
    train = set(split.train_indices)
    validation = set(split.validation_indices)
    test = set(split.test_indices)
    assert not train & validation
    assert not train & test
    assert not validation & test
    assert train | validation | test == set(range(dataset.row_count))
    assert not {"visit", "conversion", "spend", "history_segment"} & set(dataset.feature_names)


def test_preprocessor_records_only_allowed_fit_indices() -> None:
    dataset, split, _specification = _fixture()
    preprocessing = fit_preprocessor(dataset, split.train_indices, fit_split="training")
    assert preprocessing.fit_indices_hash == sha256_digest(tuple(sorted(split.train_indices)))
    assert preprocessing.fit_split == "training"


def test_test_outcomes_require_matching_frozen_policy() -> None:
    dataset, split, specification = _fixture()
    gate = OutcomeGate(dataset, split)
    fit = fit_frozen_policy(dataset, split, specification)
    assert not gate.test_outcomes_accessed
    bad_policy = replace(fit.artifact, created_without_test_outcomes=False)
    with pytest.raises(DCFAError) as exc_info:
        gate.unlock(bad_policy)
    assert exc_info.value.code is ErrorCode.POLICY_NOT_FROZEN
    assert not gate.test_outcomes_accessed
    actions, outcomes = gate.unlock(fit.artifact)
    assert len(actions) == len(split.test_indices) == len(outcomes)
    assert gate.test_outcomes_accessed


def test_real_loader_fails_closed_without_provenance(tmp_path) -> None:
    with pytest.raises(DCFAError) as exc_info:
        load_hillstrom_csv(
            tmp_path / "not-read.csv",
            exact_source="",
            retrieval_date="",
            license_note="",
        )
    assert exc_info.value.code is ErrorCode.INVALID_DATA


def test_policy_input_rejects_missing_or_nonfinite_outcomes() -> None:
    dataset, _split, _specification = _fixture()
    bad_spend = (float("nan"), *dataset.spend[1:])
    with pytest.raises(DCFAError) as exc_info:
        make_stratified_split(replace(dataset, spend=bad_spend), seed=99)
    assert exc_info.value.code is ErrorCode.INVALID_DATA
    assert exc_info.value.stage == "hillstrom.data.missingness"


def test_stale_hillstrom_manifest_hash_blocks_before_policy_fit_or_test_access() -> None:
    dataset, split, specification = _fixture()
    tampered_spend = (dataset.spend[0] + 1.0, *dataset.spend[1:])
    with pytest.raises(DCFAError) as exc_info:
        HillstromPolicyEngine().analyze(
            replace(dataset, spend=tampered_spend),
            split,
            specification,
        )
    assert exc_info.value.code is ErrorCode.HASH_MISMATCH
    assert exc_info.value.stage == "hillstrom.data.hash"


def test_split_must_be_actually_stratified_not_only_disjoint() -> None:
    dataset, split, _specification = _fixture()
    actions = dataset.actions
    train = list(split.train_indices)
    validation = list(split.validation_indices)
    train_position = next(index for index, row in enumerate(train) if actions[row] == 0)
    validation_position = next(index for index, row in enumerate(validation) if actions[row] == 1)
    train[train_position], validation[validation_position] = (
        validation[validation_position],
        train[train_position],
    )
    tampered = replace(
        split,
        train_indices=tuple(sorted(train)),
        validation_indices=tuple(sorted(validation)),
    )
    with pytest.raises(DCFAError) as exc_info:
        OutcomeGate(dataset, tampered)
    assert exc_info.value.code is ErrorCode.SPLIT_LEAKAGE
