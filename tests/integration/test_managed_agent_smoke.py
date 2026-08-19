from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from dcfa.artifact_validation import verify_run_directory
from dcfa.tabcf_iv.managed_client import MANAGED_CLIENT_VERSION
from dcfa.tabcf_iv.managed_smoke import run_managed_agent_smoke


class FakeClientRegressor:
    prediction_calls = 0

    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["model_path"] == "v2.5_default"
        assert kwargs["n_estimators"] == 1
        assert kwargs["thinking_mode"] is False
        self._last_meta: dict[str, Any] = {}
        self._last_trace_id = "fake-trace"

    def fit(self, features: np.ndarray, target: np.ndarray) -> FakeClientRegressor:
        matrix = np.asarray(features, dtype=float)
        values = np.asarray(target, dtype=float)
        design = np.column_stack([np.ones(len(matrix)), matrix])
        self.coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
        residuals = values - design @ self.coefficients
        self.scale = max(float(np.std(residuals)), 0.2)
        self.lower = float(np.min(values) - 4.0 * self.scale)
        self.upper = float(np.max(values) + 4.0 * self.scale)
        return self

    def predict(self, features: np.ndarray, *, output_type: str) -> Any:
        matrix = np.asarray(features, dtype=float)
        design = np.column_stack([np.ones(len(matrix)), matrix])
        means = design @ self.coefficients
        type(self).prediction_calls += 1
        self._last_meta = {
            "package_version": "8.3.0",
            "task": "regression",
            "test_set_num_rows": len(matrix),
            "test_set_num_cols": matrix.shape[1],
        }
        if output_type == "mean":
            return means
        assert output_type == "full"
        borders = np.linspace(self.lower, self.upper, 101)
        centers = 0.5 * (borders[:-1] + borders[1:])
        logits = -0.5 * ((centers[None, :] - means[:, None]) / self.scale) ** 2
        return {"borders": borders, "logits": logits}


class FakeClientModule:
    TabPFNRegressor = FakeClientRegressor

    def __init__(self) -> None:
        self.reset_called = False
        self.authenticated = False

    def set_access_token(self, token: str) -> None:
        self.authenticated = token.startswith("tabpfn_sk_")

    def get_api_usage(self) -> str:
        return f"fake_usage={FakeClientRegressor.prediction_calls * 5000}"

    def reset(self) -> None:
        self.reset_called = True
        self.authenticated = False


def _token_file(tmp_path: Path) -> Path:
    path = tmp_path / "tabpfn-token"
    path.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    path.chmod(0o600)
    return path


def test_fixed_managed_agent_smoke_is_evidence_linked_and_batched(tmp_path) -> None:
    FakeClientRegressor.prediction_calls = 0
    client = FakeClientModule()
    output_dir = tmp_path / "managed-smoke"
    result = run_managed_agent_smoke(
        token_file=_token_file(tmp_path),
        output_dir=output_dir,
        client_module=client,
        client_version=MANAGED_CLIENT_VERSION,
    )

    assert result.response.status == "completed"
    assert result.response.tool_calls == 1
    assert result.response.retry_count == 0
    assert result.run is not None
    assert result.run.backend_fit_calls == 3
    assert result.api_prediction_calls == 3
    assert FakeClientRegressor.prediction_calls == 3
    assert client.reset_called
    assert all(query.evidence_id for query in result.response.queries)
    assert any(
        warning.code == "DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE"
        for warning in result.response.warnings
    )
    assert verify_run_directory(output_dir)["status"] == "valid"

    audit = [
        json.loads(line)
        for line in (output_dir / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    service_event = next(item for item in audit if item["event_type"] == "managed_service_observed")
    details = dict(service_event["details"])
    assert details["api_prediction_calls"] == "3"
    assert details["request_1_service_package_version"] == "8.3.0"
