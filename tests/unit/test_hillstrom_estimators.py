from __future__ import annotations

import numpy as np

from dcfa.hillstrom_policy.estimators import (
    design_propensities,
    doubly_robust_scores,
    paired_policy_contrast,
    policy_influence_scores,
)
from dcfa.hillstrom_policy.policies import (
    enforce_email_capacity,
    policy_from_values,
    uniform_policy,
)


def test_dr_score_hand_calculation_and_design_propensity() -> None:
    outcomes = np.array([2.0, 4.0])
    actions = np.array([0, 1])
    predictions = np.array([[1.0, 10.0, 20.0], [2.0, 3.0, 30.0]])
    propensities = design_propensities(2)
    scores = doubly_robust_scores(outcomes, actions, predictions, propensities)
    np.testing.assert_allclose(propensities, np.full((2, 3), 1.0 / 3.0))
    np.testing.assert_allclose(scores, [[4.0, 10.0, 20.0], [2.0, 6.0, 30.0]])


def test_cost_application_and_paired_contrast_use_same_rows() -> None:
    scores = np.array([[2.0, 5.0, 1.0], [4.0, 3.0, 2.0], [1.0, 8.0, 0.0]])
    email = uniform_policy(3, 1)
    no_email = uniform_policy(3, 0)
    costs = (0.0, 1.0, 0.0)
    np.testing.assert_allclose(policy_influence_scores(scores, email, costs), [4.0, 2.0, 7.0])
    contrast = paired_policy_contrast(scores, email, no_email, costs)
    expected = np.array([2.0, -2.0, 6.0])
    assert contrast.value == np.mean(expected)
    assert contrast.standard_error == np.std(expected, ddof=1) / np.sqrt(3)


def test_uncertainty_fallback_and_capacity_are_deterministic() -> None:
    values = np.array(
        [
            [0.0, 3.0, 1.0],
            [0.0, 2.0, 1.9],
            [0.0, 4.0, 1.0],
            [0.0, 1.0, 2.0],
        ]
    )
    policy = policy_from_values(values, uncertainty_threshold=0.2)
    assert np.argmax(policy, axis=1).tolist() == [1, 0, 1, 2]

    unconstrained = policy_from_values(values, uncertainty_threshold=0.0)
    constrained = enforce_email_capacity(unconstrained, values, 0.5)
    assert np.argmax(constrained, axis=1).tolist() == [1, 0, 1, 0]
    assert int(np.sum(np.argmax(constrained, axis=1) != 0)) == 2
