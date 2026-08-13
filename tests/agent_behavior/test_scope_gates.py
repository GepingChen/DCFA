from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from dcfa.constants import EvidenceStatus
from dcfa.errors import DCFAError, ErrorCode
from dcfa.schemas import AnalysisSpecification, CausalRoles
from dcfa.tabcf_iv.development_dgp import DevelopmentIVDataset
from dcfa.tabcf_iv.pipeline import TabCFAnalysisEngine


@pytest.mark.parametrize(
    ("roles", "expected_code"),
    [
        (
            CausalRoles(
                outcome="Y",
                treatment="X",
                instrument="Z",
                baseline_covariates=("W1",),
            ),
            ErrorCode.UNSUPPORTED_BASELINE_COVARIATES,
        ),
        (
            CausalRoles(
                outcome="Y",
                treatment="X",
                instrument="Z",
                treatment_type="categorical",
            ),
            ErrorCode.UNSUPPORTED_TREATMENT,
        ),
    ],
)
def test_scope_gates_fire_before_backend_construction_or_fit(
    roles: CausalRoles,
    expected_code: ErrorCode,
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    construction_calls = 0

    def forbidden_factory(specification: AnalysisSpecification):
        nonlocal construction_calls
        construction_calls += 1
        raise AssertionError("Backend construction must not happen before scope gates.")

    specification = replace(development_specification, roles=roles)
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine(backend_factory=forbidden_factory).analyze(
            development_dataset.columns,
            specification,
            development_dataset.manifest,
        )
    assert raised.value.code is expected_code
    assert construction_calls == 0


def test_data_hash_mismatch_fires_before_backend_construction(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    construction_calls = 0

    def forbidden_factory(specification: AnalysisSpecification):
        nonlocal construction_calls
        construction_calls += 1
        raise AssertionError("Backend construction must not happen before the data-hash gate.")

    tampered = dict(development_dataset.columns)
    tampered_x = np.asarray(tampered["X"], dtype=float).copy()
    tampered_x[0] += 0.25
    tampered["X"] = tampered_x
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine(backend_factory=forbidden_factory).analyze(
            tampered,
            development_specification,
            development_dataset.manifest,
        )
    assert raised.value.code is ErrorCode.HASH_MISMATCH
    assert construction_calls == 0


def test_manifest_marker_mismatch_fires_before_backend_construction(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    construction_calls = 0

    def forbidden_factory(specification: AnalysisSpecification):
        nonlocal construction_calls
        construction_calls += 1
        raise AssertionError("Backend construction must not happen before the manifest gate.")

    mismatched_manifest = replace(
        development_dataset.manifest,
        evidence_status=EvidenceStatus.ELIGIBLE_FOR_RELEASE,
    )
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine(backend_factory=forbidden_factory).analyze(
            development_dataset.columns,
            development_specification,
            mismatched_manifest,
        )
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE
    assert construction_calls == 0


def test_manifest_provenance_gap_fires_before_backend_construction(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    construction_calls = 0

    def forbidden_factory(specification: AnalysisSpecification):
        nonlocal construction_calls
        construction_calls += 1
        raise AssertionError("Backend construction must not happen before the manifest gate.")

    incomplete_manifest = replace(development_dataset.manifest, source="")
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine(backend_factory=forbidden_factory).analyze(
            development_dataset.columns,
            development_specification,
            incomplete_manifest,
        )
    assert raised.value.code is ErrorCode.INVALID_DATA
    assert construction_calls == 0
