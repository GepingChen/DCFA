from __future__ import annotations

import numpy as np

from dcfa.hillstrom_policy.estimators import (
    design_propensities,
    doubly_robust_scores,
    ipw_scores,
    policy_influence_scores,
)
from dcfa.hillstrom_policy.policies import uniform_policy


def test_ipw_and_dr_recover_known_randomized_policy_value() -> None:
    rng = np.random.default_rng(20260808)
    n = 60_000
    x = rng.normal(size=n)
    true_means = np.column_stack([1.0 + x, 2.0 + 0.5 * x, 0.5 - x])
    actions = rng.integers(0, 3, size=n)
    outcomes = true_means[np.arange(n), actions] + rng.normal(0.0, 0.5, size=n)
    propensities = design_propensities(n)
    target = float(np.mean(true_means[:, 1]))
    policy = uniform_policy(n, 1)

    ipw = np.mean(
        policy_influence_scores(
            ipw_scores(outcomes, actions, np.zeros_like(true_means), propensities),
            policy,
            (0.0, 0.0, 0.0),
        )
    )
    dr_correct_outcome = np.mean(
        policy_influence_scores(
            doubly_robust_scores(outcomes, actions, true_means, propensities),
            policy,
            (0.0, 0.0, 0.0),
        )
    )
    assert abs(ipw - target) < 0.05
    assert abs(dr_correct_outcome - target) < 0.03
