from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from dcfa.constants import EstimatorBackend, EvidenceStatus, ExecutionProfile
from dcfa.errors import BackendError, DCFAError, ErrorCode
from dcfa.tabcf_iv.managed_client import (
    MANAGED_BACKEND_PARAMETERS,
    MANAGED_CLIENT_VERSION,
    TabPFNClientBackend,
    _numpy_bar_distribution_cdf,
)
from dcfa.tabcf_iv.validation import validate_tabcf_specification


def test_numpy_bar_cdf_matches_piecewise_uniform_distribution() -> None:
    borders = np.array([0.0, 1.0, 3.0])
    logits = np.log(np.array([[0.25, 0.75]]))
    evaluation = np.array([[-1.0, 0.0, 0.5, 1.0, 2.0, 3.0, 4.0]])
    observed = _numpy_bar_distribution_cdf(borders, logits, evaluation)
    expected = np.array([[0.0, 0.0, 0.125, 0.25, 0.625, 1.0, 1.0]])
    assert np.allclose(observed, expected)


def test_numpy_bar_cdf_restores_zero_probability_transport_values() -> None:
    borders = np.asarray([0.0, 1.0, 1.0, 2.0])
    logits = np.asarray([[0.0, np.nan, 0.0]])
    evaluation = np.asarray([[0.5, 1.5]])

    observed = _numpy_bar_distribution_cdf(borders, logits, evaluation)

    assert np.allclose(observed, [[0.25, 0.75]])


def test_numpy_bar_cdf_rejects_a_row_without_probability_mass() -> None:
    with pytest.raises(ValueError, match="no finite probability mass"):
        _numpy_bar_distribution_cdf(
            np.asarray([0.0, 1.0]),
            np.asarray([[np.nan]]),
            np.asarray([[0.5]]),
        )


def test_managed_backend_rejects_nonfrozen_client_version() -> None:
    with pytest.raises(BackendError) as raised:
        TabPFNClientBackend(seed=1, regressor_class=object, client_version="0.3.2")
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE


def test_managed_specification_is_development_only_and_exact(
    development_specification,
) -> None:
    managed = replace(
        development_specification,
        estimator_backend=EstimatorBackend.TABPFN,
        execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
        evidence_status=EvidenceStatus.DEVELOPMENT_ONLY,
        backend_parameters=MANAGED_BACKEND_PARAMETERS,
    )
    validate_tabcf_specification(managed)
    with pytest.raises(DCFAError) as raised:
        validate_tabcf_specification(
            replace(
                managed,
                backend_parameters=(*MANAGED_BACKEND_PARAMETERS[:-1], ("thinking_mode", "true")),
            )
        )
    assert raised.value.code is ErrorCode.INVALID_SPECIFICATION

    backend = TabPFNClientBackend.from_specification(
        managed,
        regressor_class=object,
        client_version=MANAGED_CLIENT_VERSION,
    )
    assert backend.manifest.evidence_status is EvidenceStatus.DEVELOPMENT_ONLY
    assert backend.manifest.model_artifact_hash.startswith("managed_service_")
