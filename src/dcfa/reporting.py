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
    title = "# TabCF Analyst local development report"
    if bundle.evidence_status is EvidenceStatus.DEVELOPMENT_ONLY:
        if bundle.estimator_backend is EstimatorBackend.SKLEARN_QUANTILE_FALLBACK:
            boundary = (
                "> **Development-only engineering output.** This run uses "
                f"`{bundle.estimator_backend.value}` under `{bundle.execution_profile.value}`. "
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
        title,
        "",
        boundary,
        "",
        "## Run identity",
        "",
        f"- Track: `{bundle.track.value}`",
        f"- Run ID: `{bundle.run_id}`",
        f"- Result bundle: `{bundle.result_bundle_id}`",
        f"- Specification: `{bundle.specification_id}`",
        f"- Dataset hash: `{bundle.dataset_hash}`",
        f"- Evidence status: `{bundle.evidence_status.value}`",
        "",
        "## Evidence-linked query results",
        "",
        "| Query | Claim type | Value | Support | Evidence ID |",
        "|---|---|---:|---|---|",
    ]
    for query in bundle.queries:
        lines.append(
            f"| `{query.query_id}` | `{query.claim_type}` | {query.value_display} "
            f"{query.units} | `{query.support_status.value}` | `{query.evidence_id}` |"
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
            lines.append(f"- `{warning.code}`: {warning.message}")
    else:
        lines.append(
            "- No additional empirical warning was triggered by the development thresholds."
        )
    lines.extend(["", "## Assumptions and scope", ""])
    lines.extend(f"- {assumption}" for assumption in bundle.assumptions)
    lines.append("")
    return "\n".join(lines)


def render_bundle_plot(bundle: ResultBundle, ledger: EvidenceLedger, output_path: Path) -> None:
    validate_bundle_evidence(bundle, ledger)
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
    fig.suptitle(
        f"{bundle.execution_profile.value} | {bundle.estimator_backend.value} | "
        f"{bundle.evidence_status.value}",
        fontsize=10,
    )
    evidence_ids = ", ".join(query.evidence_id for query in bundle.queries)
    fig.text(
        0.5,
        0.01,
        f"bundle={bundle.result_bundle_id} | evidence={evidence_ids}",
        ha="center",
        fontsize=6,
    )
    fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, facecolor="white")
    plt.close(fig)
