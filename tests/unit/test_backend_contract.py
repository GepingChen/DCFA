from __future__ import annotations

import subprocess
import sys

import numpy as np
import pytest

import dcfa.tabcf_iv.backend as backend_module
from dcfa.constants import ExecutionProfile
from dcfa.errors import BackendError, ErrorCode
from dcfa.tabcf_iv.backend import SklearnQuantileBackend, TabPFNBackend
from dcfa.tabcf_iv.local_tabpfn import (
    LOCAL_TABPFN_V2_MODEL_HASH,
    LOCAL_TABPFN_V2_MODEL_REPO,
    LOCAL_TABPFN_V2_MODEL_REVISION,
)


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


def test_local_tabpfn_hashed_model_fails_before_import_on_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    calls: list[str] = []

    def record_import(name: str):
        calls.append(name)
        raise AssertionError("A mismatched local model must fail before import.")

    model_path = tmp_path / "model.ckpt"
    model_path.write_bytes(b"wrong-model")
    monkeypatch.setattr(backend_module.importlib, "import_module", record_import)
    backend = TabPFNBackend(
        seed=1,
        execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
        model_path=str(model_path),
        model_artifact_hash=LOCAL_TABPFN_V2_MODEL_HASH,
        model_version="v2",
        model_repo=LOCAL_TABPFN_V2_MODEL_REPO,
        model_revision=LOCAL_TABPFN_V2_MODEL_REVISION,
        model_filename="tabpfn-v2-regressor-v2_default.ckpt",
        n_estimators=1,
        device="cuda",
    )
    with pytest.raises(BackendError) as raised:
        backend.fit_distribution(np.ones((40, 1)), np.linspace(0.0, 1.0, 40))
    assert raised.value.code is ErrorCode.HASH_MISMATCH
    assert calls == []
    assert backend.fit_calls == 0


def test_local_tabpfn_manifest_records_frozen_runtime_settings(tmp_path) -> None:
    model_path = tmp_path / "model.ckpt"
    model_path.write_bytes(b"not-loaded-by-manifest")
    backend = TabPFNBackend(
        seed=7,
        execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
        model_path=str(model_path),
        model_artifact_hash=LOCAL_TABPFN_V2_MODEL_HASH,
        model_version="v2",
        model_repo=LOCAL_TABPFN_V2_MODEL_REPO,
        model_revision=LOCAL_TABPFN_V2_MODEL_REVISION,
        model_filename="tabpfn-v2-regressor-v2_default.ckpt",
        n_estimators=1,
        device="cuda",
    )
    parameters = dict(backend.manifest.parameters)
    assert parameters["model_version"] == "v2"
    assert parameters["model_repo"] == LOCAL_TABPFN_V2_MODEL_REPO
    assert parameters["model_revision"] == LOCAL_TABPFN_V2_MODEL_REVISION
    assert parameters["n_estimators"] == 1
    assert parameters["device"] == "cuda"


@pytest.fixture
def fake_tabpfn(monkeypatch):
    """Exercise real adapters with a deterministic regressor, without Torch/GPU."""
    from scipy.special import expit

    instances = []

    class Regressor:
        def __init__(self, **kwargs):
            self.outputs = []
            self.fits = 0
            instances.append(self)

        def fit(self, features, target):
            self.fits += 1
            self.coefficients = np.linalg.lstsq(
                np.column_stack([np.ones(len(features)), features]), target, rcond=None
            )[0]

        def predict(self, features, *, output_type):
            self.outputs.append(output_type)
            values = np.column_stack([np.ones(len(features)), features]) @ self.coefficients
            return values if output_type == "mean" else {"criterion": None, "logits": values}

    def cdf(self, features, values, *, paired):
        full = self._full_output(features)
        evaluation = backend_module._distribution_eval_matrix(
            values, n_rows=len(features), paired=paired
        )
        result = expit(evaluation - full["logits"][:, None])
        return result[:, 0] if paired else result

    monkeypatch.setattr(TabPFNBackend, "_load_classes", lambda self: (Regressor, None))
    monkeypatch.setattr(backend_module.TabPFNDistributionModel, "cdf", cdf)
    return instances


def test_shared_stage2_matches_legacy_full_artifacts(
    fake_tabpfn, development_dataset, specification_copy, tmp_path
):
    from dataclasses import replace

    from dcfa.artifact_validation import verify_run_directory
    from dcfa.constants import EstimatorBackend
    from dcfa.tabcf_iv.pipeline import TabCFAnalysisEngine

    class LegacyBackend(TabPFNBackend):
        fit_mean_distribution = None

    spec = replace(specification_copy, estimator_backend=EstimatorBackend.TABPFN)
    manifest = replace(development_dataset.manifest, estimator_backend=EstimatorBackend.TABPFN)
    runs = []
    for name, backend_type in (("legacy", LegacyBackend), ("shared", TabPFNBackend)):
        run = TabCFAnalysisEngine(
            backend_factory=lambda s, backend_type=backend_type: backend_type(
                seed=s.seed, execution_profile=s.execution_profile
            )
        ).analyze(development_dataset.columns, spec, manifest, output_dir=tmp_path / name)
        runs.append(run)
        assert verify_run_directory(tmp_path / name)["status"] == "valid"
    assert [run.backend_fit_calls for run in runs] == [3, 2]
    assert len(fake_tabpfn) == 5
    assert all(model.fits == 1 for model in fake_tabpfn)
    assert set(fake_tabpfn[-1].outputs) == {"mean", "full"}
    assert runs[0].bundle == runs[1].bundle
    assert runs[0].ledger.records() == runs[1].ledger.records()
    for path in (tmp_path / "legacy").iterdir():
        assert path.read_bytes() == (tmp_path / "shared" / path.name).read_bytes(), path.name
