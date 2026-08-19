from __future__ import annotations

from dataclasses import replace

from dcfa.constants import SupportStatus, WarningSeverity
from dcfa.errors import ErrorCode
from dcfa.schemas import QueryResult, WarningRecord
from dcfa_website_demo.presentation import (
    CLAIM_PRESENTATION,
    ERROR_CATEGORY_BY_CODE,
    SUPPORT_PRESENTATION,
    UNKNOWN_CLAIM,
    UNKNOWN_WARNING,
    WARNING_PRESENTATION,
    display_value,
    present_error,
    present_query,
    present_units,
    quantile_label,
)


def _query(**updates: object) -> QueryResult:
    query = QueryResult(
        query_id="query_internal",
        claim_type="quantile_contrast_x_minus_comparison_x",
        value_raw=4.84621917,
        value_display="4.84622",
        units="Y_units",
        support_status=SupportStatus.SUPPORTED,
        warnings=(
            WarningRecord(
                code="DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE",
                message="Internal artifact message.",
                severity=WarningSeverity.WARNING,
                source="backend.contract",
            ),
        ),
        evidence_id="evidence_internal",
    )
    return replace(query, **updates)


def test_presentation_mappings_cover_bounded_website_contracts() -> None:
    assert set(CLAIM_PRESENTATION) == {
        "interventional_mean",
        "interventional_quantile",
        "threshold_risk",
        "mean_contrast_x_minus_comparison_x",
        "quantile_contrast_x_minus_comparison_x",
        "risk_contrast_x_minus_comparison_x",
    }
    assert set(SUPPORT_PRESENTATION) == set(SupportStatus)
    assert set(ERROR_CATEGORY_BY_CODE) == set(ErrorCode)
    assert {
        "DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE",
        "DEVELOPMENT_FALLBACK_NOT_TABCF",
        "WEAK_FIRST_STAGE_EMPIRICAL_WARNING",
        "CONTROL_RANK_CALIBRATION_WARNING",
        "RESIDUAL_DEPENDENCE_EMPIRICAL_WARNING",
        "WEAK_INTERVENTION_SUPPORT",
    } == set(WARNING_PRESENTATION)


def test_query_projection_rounds_only_for_display_and_translates_internal_units() -> None:
    query = _query()
    presented = present_query(query)

    assert presented.allow_numeric is True
    assert presented.value_display == "4.85"
    assert presented.value_display == display_value(query.value_raw)
    assert query.value_raw == 4.84621917
    assert query.value_display == "4.84622"
    assert presented.units == "outcome units"
    assert present_units("percentage points") == "percentage points"
    assert present_units("<script>") == "outcome units"
    assert quantile_label(0.5) == "Median"
    assert quantile_label(0.1) == "10% quantile"


def test_unknown_claim_warning_support_and_error_fail_closed_without_raw_text() -> None:
    unknown_warning = WarningRecord(
        code="FUTURE_INTERNAL_WARNING",
        message="Private backend context /tmp/example",
        severity=WarningSeverity.WARNING,
        source="future.stage",
    )
    presented = present_query(
        _query(
            claim_type="future_internal_claim",
            support_status="future_support",
            warnings=(unknown_warning,),
        )
    )

    assert presented.claim is UNKNOWN_CLAIM
    assert presented.warnings == (UNKNOWN_WARNING,)
    assert presented.allow_numeric is False
    assert presented.value_display is None
    error = present_error("FUTURE_INTERNAL_ERROR")
    assert error.title == "Result verification failed"
    assert "FUTURE_INTERNAL_ERROR" not in error.explanation
