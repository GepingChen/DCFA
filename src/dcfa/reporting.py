"""Reports and plots derived only from validated result bundles."""

from __future__ import annotations

from pathlib import Path
from tempfile import gettempdir

import numpy as np

from dcfa.constants import EstimatorBackend, EvidenceStatus
from dcfa.evidence import EvidenceLedger, validate_bundle_evidence
from dcfa.schemas import ResultBundle


def render_markdown_report(bundle: ResultBundle, ledger: EvidenceLedger) -> str:
    validate_bundle_evidence(bundle, ledger)
    if bundle.evidence_status is EvidenceStatus.DEVELOPMENT_ONLY:
        if bundle.estimator_backend is EstimatorBackend.SKLEARN_QUANTILE_FALLBACK:
            boundary = (
                "> **Development-only engineering output.** This run uses "
                "a local scikit-learn quantile approximation. "
                "It is not a TabCF estimate, is not eligible for locked Track T evaluation, "
                "and must not support a headline causal claim."
            )
        else:
            boundary = (
                "> **Development-only managed TabPFN output.** This run is service-version-"
                "traceable but not checkpoint/image-hash reproducible, is not eligible for "
                "locked Track T evaluation, and must not support a release claim."
            )
    else:
        boundary = (
            "> Locked Track T result; release eligibility still requires the release validator."
        )
    lines = [
        "# TabCF Analyst report",
        "",
        boundary,
        "",
        "Track T · Distributional instrumental-variable analysis",
        "",
        "## Visual summary",
        "",
        "![Estimated outcome distributions and summaries](interventional_summary.png)",
        "",
        "The chart and tables use the same validated results. Read them together with the "
        "support diagnostics and warnings below.",
        "",
    ]
    if bundle.distribution is not None:
        from dcfa.distribution_reporting import distribution_markdown

        lines.append(distribution_markdown(bundle.distribution, bundle.queries))
    else:
        lines.extend(
            [
                "## Estimated outcomes",
                "",
                "| Estimate | Value | Support | Reference |",
                "|---|---:|---|---|",
            ]
        )
        for index, query in enumerate(bundle.queries, 1):
            label = {
                "interventional_mean": "Estimated mean outcome",
                "interventional_quantile": "Estimated outcome quantile",
                "threshold_risk": "Estimated threshold probability",
                "mean_contrast_x_minus_comparison_x": (
                    "Mean difference (requested minus comparison)"
                ),
                "quantile_contrast_x_minus_comparison_x": (
                    "Quantile difference (requested minus comparison)"
                ),
                "risk_contrast_x_minus_comparison_x": (
                    "Probability difference (requested minus comparison)"
                ),
            }.get(query.claim_type, "Estimated outcome")
            support = query.support_status.value.replace("_", " ").capitalize()
            lines.append(
                f"| {label} | {query.value_display} {query.units} | {support} | [{index}] |"
            )
    lines.extend(
        [
            "",
            "## Empirical diagnostics",
            "",
            bundle.diagnostics.interpretation,
            "",
            "Diagnostic numbers are available in the machine-readable result bundle and are "
            "not evidence that IV validity or identification has been proved.",
            "",
            "## Warnings",
            "",
        ]
    )
    if bundle.warnings:
        for warning in bundle.warnings:
            lines.append(f"- {warning.message}")
    else:
        lines.append(
            "- No additional empirical warning was triggered by the development thresholds."
        )
    lines.extend(["", "## Assumptions and scope", ""])
    lines.extend(f"- {assumption}" for assumption in bundle.assumptions)
    lines.extend(
        [
            "",
            "<details>",
            "<summary>Technical appendix and evidence index</summary>",
            "",
            f"- Run ID: `{bundle.run_id}`",
            f"- Result bundle: `{bundle.result_bundle_id}`",
            f"- Specification: `{bundle.specification_id}`",
            f"- Dataset hash: `{bundle.dataset_hash}`",
            f"- Evidence status: `{bundle.evidence_status.value}`",
            "",
            "Table references resolve to the evidence records included in this download.",
            "Curve points are also included in this index.",
            "",
            "| Reference | Query | Validated value | Evidence ID |",
            "|---|---|---|---|",
        ]
    )
    for index, query in enumerate(bundle.queries, 1):
        lines.append(
            f"| [{index}] | `{query.query_id}` | {query.value_display} {query.units} "
            f"| `{query.evidence_id}` |"
        )
    lines.extend(["", "### Warning codes", ""])
    lines.extend(f"- `{warning.code}`: {warning.message}" for warning in bundle.warnings)
    lines.extend(["", "</details>", ""])
    return "\n".join(lines)


def render_bundle_plot(bundle: ResultBundle, ledger: EvidenceLedger, output_path: Path) -> None:
    validate_bundle_evidence(bundle, ledger)
    if bundle.distribution is not None:
        from dcfa.distribution_reporting import render_distribution_plot

        render_distribution_plot(bundle, ledger, output_path)
        return
    import os

    matplotlib_config = Path(gettempdir()) / "dcfa-matplotlib-cache"
    matplotlib_config.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_config))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_grid = np.asarray(bundle.x_grid, dtype=float)
    y_grid = np.asarray(bundle.y_grid, dtype=float)
    cdf = np.asarray(bundle.interventional_cdf, dtype=float)
    means = np.asarray(bundle.interventional_mean, dtype=float)
    quantiles = np.asarray(bundle.interventional_quantiles, dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for index in np.linspace(0, len(x_grid) - 1, min(4, len(x_grid))).round().astype(int):
        axes[0].plot(y_grid, cdf[index], label=f"x={x_grid[index]:.3g}")
    axes[0].set_xlabel("Outcome grid")
    axes[0].set_ylabel("Interventional CDF")
    axes[0].set_ylim(-0.02, 1.02)
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.25)

    axes[1].plot(x_grid, means, marker="o", label="mean")
    for level_index, level in enumerate(bundle.quantile_levels):
        axes[1].plot(x_grid, quantiles[:, level_index], label=f"q={level:g}")
    axes[1].set_xlabel("Intervention x")
    axes[1].set_ylabel("Outcome")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.25)
    fig.suptitle("Estimated outcome distributions and summaries", fontsize=10)
    fig.text(
        0.5,
        0.01,
        "Read with the report warnings and evidence appendix.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, facecolor="white")
    plt.close(fig)
