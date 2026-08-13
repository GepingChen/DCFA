from __future__ import annotations

import numpy as np

from dcfa.tabcf_iv.estimands import canonicalize_cdf, interpolate_risks, invert_cdf


def test_cdf_range_monotonicity_quantile_inversion_and_risk_interpolation() -> None:
    y_grid = np.array([0.0, 1.0, 2.0, 3.0])
    raw = np.array([[-0.1, 0.6, 0.5, 1.2], [0.0, 0.2, 0.8, 1.0]])
    canonical = canonicalize_cdf(raw)
    assert np.all((canonical >= 0.0) & (canonical <= 1.0))
    assert np.all(np.diff(canonical, axis=1) >= 0.0)
    quantiles = invert_cdf(canonical, y_grid, (0.5, 0.9))
    risks = interpolate_risks(canonical, y_grid, (1.5,))
    assert quantiles.shape == (2, 2)
    assert np.all(quantiles[:, 0] <= quantiles[:, 1])
    assert np.isclose(risks[1, 0], 0.5)
