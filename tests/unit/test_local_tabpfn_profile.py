from __future__ import annotations

from dataclasses import replace

import pytest

from dcfa.constants import EstimatorBackend, EvidenceStatus, ExecutionProfile
from dcfa.errors import DCFAError, ErrorCode
from dcfa.schemas import AnalysisSpecification, CausalRoles, QuerySpecification
from dcfa.tabcf_iv.local_tabpfn import LOCAL_TABPFN_V2_BACKEND_PARAMETERS
from dcfa.tabcf_iv.validation import validate_tabcf_specification


def _specification() -> AnalysisSpecification:
    return AnalysisSpecification(
        dataset_hash="sha256:" + "1" * 64,
        roles=CausalRoles(outcome="Y", treatment="X", instrument="Z"),
        queries=(QuerySpecification("median", "quantile", x=1.0, level=0.5),),
        intervention_grid=(0.0, 1.0),
        quantile_levels=(0.5,),
        execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
        estimator_backend=EstimatorBackend.TABPFN,
        evidence_status=EvidenceStatus.DEVELOPMENT_ONLY,
        backend_parameters=LOCAL_TABPFN_V2_BACKEND_PARAMETERS,
    )


def test_local_tabpfn_v2_profile_is_exact_and_development_only() -> None:
    validate_tabcf_specification(_specification())

    changed = replace(
        _specification(),
        backend_parameters=(*LOCAL_TABPFN_V2_BACKEND_PARAMETERS[:-1], ("n_estimators", "8")),
    )
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(changed)
    assert raised.value.code is ErrorCode.INVALID_SPECIFICATION

    locked = replace(
        _specification(),
        execution_profile=ExecutionProfile.LOCKED_EVALUATION,
        evidence_status=EvidenceStatus.ELIGIBLE_FOR_RELEASE,
    )
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(locked)
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE
