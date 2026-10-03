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


def test_managed_estimator_uses_explicit_35_without_removed_client_options() -> None:
    class Regressor:
        def __init__(
            self,
            *,
            model_path,
            n_estimators,
            random_state,
            ignore_pretraining_limits,
            thinking_mode,
        ):
            assert model_path == "v3.5_default"
            assert n_estimators == 1
            assert random_state == 7
            assert not ignore_pretraining_limits
            assert not thinking_mode

    backend = TabPFNClientBackend(
        seed=7, regressor_class=Regressor, client_version=MANAGED_CLIENT_VERSION
    )
    assert isinstance(backend._new_estimator(), Regressor)


def test_managed_service_observation_records_resolved_model_and_preserves_version_check() -> None:
    class Regressor:
        _last_meta = {
            "package_version": "9.0.0",
            "billing_model_version": "v3.5",
            "n_estimators": 1,
            "tabpfn_config": {"model_path": "/app/tabpfn_models/tabpfn-v3.5.safetensors"},
        }

    backend = TabPFNClientBackend(
        seed=7, regressor_class=Regressor, client_version=MANAGED_CLIENT_VERSION
    )
    estimator = Regressor()
    backend._record_observation(estimator, "full", np.zeros((2, 1)))
    details = dict(backend.audit_details)
    assert details["request_1_billing_model_version"] == "v3.5"
    assert details["request_1_model_path"].endswith("tabpfn-v3.5.safetensors")
    estimator._last_meta = {"package_version": "unexpected"}
    with pytest.raises(BackendError) as raised:
        backend._record_observation(estimator, "full", np.zeros((2, 1)))
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE
    assert backend.api_prediction_calls == 1
