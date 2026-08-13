from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from dcfa.canonical import canonical_json_bytes, content_id
from dcfa.constants import EvidenceStatus, ExecutionProfile
from dcfa.errors import DCFAError, ErrorCode
from dcfa.evidence import EvidenceLedger, validate_bundle_evidence
from dcfa.schemas import AnalysisSpecification
from dcfa.tabcf_iv.validation import validate_tabcf_specification


def test_specification_is_immutable_and_has_stable_content_id(
    development_specification: AnalysisSpecification,
) -> None:
    with pytest.raises(FrozenInstanceError):
        development_specification.seed = 3  # type: ignore[misc]
    copy = replace(development_specification)
    assert copy.specification_id == development_specification.specification_id
    assert canonical_json_bytes(copy) == canonical_json_bytes(development_specification)
    assert content_id("spec", copy) == development_specification.specification_id


def test_fallback_profile_and_evidence_status_are_fail_closed(
    development_specification: AnalysisSpecification,
) -> None:
    invalid = replace(
        development_specification,
        execution_profile=ExecutionProfile.LOCKED_EVALUATION,
        evidence_status=EvidenceStatus.ELIGIBLE_FOR_RELEASE,
    )
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(invalid)
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE


def test_evidence_content_id_and_all_query_fields_are_fail_closed(
    completed_engine_run,
) -> None:
    _engine, run = completed_engine_run
    record = run.ledger.records()[0]
    with pytest.raises(DCFAError) as raised:
        EvidenceLedger((replace(record, evidence_id="evidence_forged"),))
    assert raised.value.code is ErrorCode.EVIDENCE_MISMATCH

    with pytest.raises(DCFAError) as raised:
        EvidenceLedger((replace(record, value_raw=float("nan")),))
    assert raised.value.code is ErrorCode.EVIDENCE_MISMATCH

    forged_query = replace(run.bundle.queries[0], units="forged_units")
    forged_bundle = replace(run.bundle, queries=(forged_query, *run.bundle.queries[1:]))
    with pytest.raises(DCFAError) as raised:
        validate_bundle_evidence(forged_bundle, run.ledger)
    assert raised.value.code is ErrorCode.EVIDENCE_MISMATCH


@pytest.mark.parametrize(
    "changes",
    [
        {"intervention_grid": (0.0, float("nan"))},
        {"backend_parameters": (("ignored_parameter", "value"),)},
        {"queries": ()},
    ],
)
def test_nonfinite_or_ambiguous_specification_fields_are_rejected(
    development_specification: AnalysisSpecification,
    changes: dict[str, object],
) -> None:
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(replace(development_specification, **changes))
    assert raised.value.code is ErrorCode.INVALID_SPECIFICATION


def test_non_numeric_query_field_is_a_typed_specification_error(
    development_specification: AnalysisSpecification,
) -> None:
    invalid_query = replace(development_specification.queries[0], x="not-a-number")
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(replace(development_specification, queries=(invalid_query,)))
    assert raised.value.code is ErrorCode.INVALID_SPECIFICATION
