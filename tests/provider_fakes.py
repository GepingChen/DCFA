"""Contract-faithful fake providers shared by public-release integration tests."""

from __future__ import annotations

import json
from typing import Any

import numpy as np


class FakeClientRegressor:
    prediction_calls = 0

    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["model_path"] == "v2.5_default"
        assert kwargs["n_estimators"] == 1
        assert kwargs["thinking_mode"] is False
        self._last_meta: dict[str, Any] = {}
        self._last_trace_id = "public-release-fake-trace"

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
        means = np.column_stack([np.ones(len(matrix)), matrix]) @ self.coefficients
        type(self).prediction_calls += 1
        self._last_meta = {"package_version": "8.3.0"}
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
        self.authenticated = False
        self.reset_called = False

    def set_access_token(self, token: str) -> None:
        self.authenticated = token.startswith("tabpfn_sk_")

    def reset(self) -> None:
        self.authenticated = False
        self.reset_called = True


class _FakeGeminiUsage:
    total_input_tokens = 120
    total_output_tokens = 48
    total_thought_tokens = 32
    total_tokens = 200


class _FakeGeminiInteraction:
    status = "completed"
    model = "gemini-3.6-flash"
    usage = _FakeGeminiUsage()
    id = ""

    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeGeminiInteractions:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _FakeGeminiInteraction:
        self.calls.append(kwargs)
        return _FakeGeminiInteraction(self.output_text)


class FakeGeminiClient:
    def __init__(self) -> None:
        proposal = {
            "decision": "analyze",
            "reason": "Compile the requested median contrast.",
            "outcome": "Y",
            "treatment": "X",
            "instrument": "Z",
            "treatment_type": "continuous",
            "objective": "quantile_contrast",
            "x_label": "high",
            "comparison_x_label": "low",
            "level_label": "median",
        }
        self.interactions = _FakeGeminiInteractions(json.dumps(proposal))
        self.closed = False

    def close(self) -> None:
        self.closed = True
