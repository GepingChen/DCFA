from __future__ import annotations

import numpy as np

from dcfa.tabcf_iv.development_dgp import generate_development_iv
from dcfa.tabcf_iv.diagnostics import compute_diagnostics


def test_weak_iv_fixture_emits_empirical_warning_without_validity_claim() -> None:
    dataset = generate_development_iv(n=500, seed=312, instrument_strength=0.0)
    z = dataset.columns["Z"]
    x = dataset.columns["X"]
    y = dataset.columns["Y"]
    order = np.argsort(np.argsort(x, kind="mergesort"), kind="mergesort")
    control_rank = (order + 0.5) / len(order)
    diagnostics, warnings = compute_diagnostics(z, x, y, control_rank)
    assert diagnostics.first_stage_f < 10.0
    warning_codes = {warning.code for warning in warnings}
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" in warning_codes
    weak_warning = next(
        warning for warning in warnings if warning.code == "WEAK_FIRST_STAGE_EMPIRICAL_WARNING"
    )
    assert "does not prove" in weak_warning.message.lower()
