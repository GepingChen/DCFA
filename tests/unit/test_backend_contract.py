from __future__ import annotations

import subprocess
import sys

import numpy as np
import pytest

import dcfa.tabcf_iv.backend as backend_module
from dcfa.constants import ExecutionProfile
from dcfa.errors import BackendError, ErrorCode
from dcfa.tabcf_iv.backend import SklearnQuantileBackend, TabPFNBackend


def test_fallback_is_deterministic() -> None:
    rng = np.random.default_rng(41)
    features = rng.normal(size=(80, 2))
    target = features[:, 0] - 0.5 * features[:, 1] + rng.normal(scale=0.1, size=80)
    first = SklearnQuantileBackend(seed=9).fit_distribution(features, target)
    second = SklearnQuantileBackend(seed=9).fit_distribution(features, target)
    first_quantiles = first.predict_quantiles(features[:7])
    second_quantiles = second.predict_quantiles(features[:7])
    assert np.array_equal(first_quantiles, second_quantiles)
    assert np.all(np.diff(first_quantiles, axis=1) >= 0.0)
    cdf = first.cdf(features[:7], np.linspace(-2.0, 2.0, 21), paired=False)
    assert np.all((cdf >= 0.0) & (cdf <= 1.0))
    assert np.all(np.diff(cdf, axis=1) >= 0.0)


def test_fallback_import_does_not_import_torch_in_clean_process() -> None:
    code = (
        "import sys; import dcfa.tabcf_iv.backend; "
        "assert 'torch' not in sys.modules; assert 'tabpfn' not in sys.modules"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_tabpfn_import_failure_is_typed_and_never_invokes_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fail_import(name: str):
        calls.append(name)
        raise ImportError("injected import failure")

    monkeypatch.setattr(backend_module.importlib, "import_module", fail_import)
    backend = TabPFNBackend(seed=1, execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT)
    with pytest.raises(BackendError) as raised:
        backend.fit_distribution(np.ones((40, 1)), np.linspace(0.0, 1.0, 40))
    assert raised.value.code is ErrorCode.BACKEND_IMPORT_FAILED
    assert calls == ["torch"]
    assert backend.fit_calls == 0


def test_locked_tabpfn_requires_hashed_model_and_runtime_before_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def record_import(name: str):
        calls.append(name)
        raise AssertionError("Locked contract should fail before import.")

    monkeypatch.setattr(backend_module.importlib, "import_module", record_import)
    backend = TabPFNBackend(seed=1, execution_profile=ExecutionProfile.LOCKED_EVALUATION)
    with pytest.raises(BackendError) as raised:
        backend.fit_distribution(np.ones((40, 1)), np.linspace(0.0, 1.0, 40))
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE
    assert calls == []
    assert backend.fit_calls == 0


def test_locked_tabpfn_requires_current_host_image_before_import(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    calls: list[str] = []

    def record_import(name: str):
        calls.append(name)
        raise AssertionError("Locked contract should fail before import.")

    model_path = tmp_path / "model.ckpt"
    model_path.write_bytes(b"frozen-test-model")
    monkeypatch.delenv("DCFA_RUNTIME_IMAGE_DIGEST", raising=False)
    monkeypatch.setattr(backend_module.importlib, "import_module", record_import)
    backend = TabPFNBackend(
        seed=1,
        execution_profile=ExecutionProfile.LOCKED_EVALUATION,
        model_path=str(model_path),
        model_artifact_hash="sha256:663815900ba09e3c16c99987e95ac9c36791f4062c2909f67d6ac57478ee8ec4",
        runtime_image_digest="sha256:" + "2" * 64,
    )
    with pytest.raises(BackendError) as raised:
        backend.fit_distribution(np.ones((40, 1)), np.linspace(0.0, 1.0, 40))
    assert raised.value.code is ErrorCode.UNSUPPORTED_BACKEND_PROFILE
    assert calls == []
    assert backend.fit_calls == 0
