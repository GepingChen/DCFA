"""Tables, downloadable projections and plots from one validated distribution bundle."""

from __future__ import annotations

from pathlib import Path

from dcfa.canonical import to_primitive
from dcfa.evidence import validate_bundle_evidence


def export_distribution(bundle, ledger):
    validate_bundle_evidence(bundle, ledger)
    if bundle.distribution is None:
        raise ValueError("No distribution projection is available.")
    return {
        "result_bundle_id": bundle.result_bundle_id,
        "track": bundle.track.value,
        "evidence_status": bundle.evidence_status.value,
        "distribution": bundle.distribution,
        "evidence": {
            q.query_id: to_primitive(ledger.resolve(q.evidence_id)) for q in bundle.queries
        },
        "warnings": to_primitive(bundle.warnings),
        "assumptions": bundle.assumptions,
    }


def distribution_markdown(distribution, queries):
    """Use validated display strings without recalculating headline values."""
    d = distribution
    r = d["request"]
    lookup = {q.query_id: q for q in queries}

    def cell(key):
        q = lookup[key]
        return q.value_display

    p0, p1 = r["prices"]
    lines = [
        "### Distributional analysis — Track T · Real data · Exploratory estimates",
        "",
        f"Prices: {p0:g} to {p1:g} {r['treatment_units']}. "
        f"All differences are {p1:g} minus {p0:g}.",
        "",
        "**Sales quantiles**",
        "",
        f"Levels and changes are in {r['outcome_units']}. "
        "Each row describes a percentile of the estimated sales distribution; "
        "the median is the 50th percentile.",
        "",
        f"| Quantile | Price {p0:g} | Price {p1:g} | Change ({p1:g} − {p0:g}) |",
        "|:---|---:|---:|---:|",
    ]
    boundary_notes = []
    for row in d["quantiles"]:
        prices = ", ".join(
            f"{price:g}"
            for price, limited in zip(r["prices"], row["boundary_limited"], strict=True)
            if limited
        )
        if prices:
            boundary_notes.append(f"{row['level']:.0%} at price {prices}")
        lines.append(
            f"| {row['level']:.0%} | {cell(row['values'][0])} | "
            f"{cell(row['values'][1])} | {cell(row['difference'])} |"
        )
    if boundary_notes:
        lines += [
            "",
            "Boundary-limited quantiles: " + "; ".join(boundary_notes) + ". "
            "These estimates reach the evaluated grid endpoint.",
        ]
    lines += [
        "",
        "**Probability above the sales threshold**",
        "",
        f"Sales strictly exceeding {r['threshold']:g} {r['outcome_units']}. "
        "Levels are percentages; the change is in percentage points.",
        "",
        f"| Price {p0:g} (%) | Price {p1:g} (%) | Change (percentage points) |",
        "|---:|---:|---:|",
        f"| {cell(d['probabilities'][0])} | {cell(d['probabilities'][1])} | "
        f"{cell(d['probability_difference'])} |",
        "",
        "**Change in the 90th-percentile–median gap:** "
        f"{cell(d['gap_change'])} {r['outcome_units']}.",
        "",
        d["summary"],
        "",
        "The downloaded technical appendix contains the evidence index for these estimates.",
        "",
        "Point estimates only. No confidence intervals or significance conclusions. "
        "These are changes in aggregate distributions, not individual effects. "
        "CDFs show only the evaluated outcome range; no tail extrapolation.",
    ]
    return "\n".join(lines)


def render_distribution_plot(bundle, ledger, output_path: Path):
    validate_bundle_evidence(bundle, ledger)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = bundle.distribution
    r = d["request"]
    lookup = {q.query_id: q.value_raw for q in bundle.queries}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for curve in d["curves"]:
        axes[0].plot(
            d["outcome_axis"],
            [lookup[k] for k in curve["cdf"]],
            label=f"{curve['price']:g} {r['treatment_units']}",
        )
    axes[0].axvline(r["threshold"], color="gray", linestyle="--")
    axes[0].scatter([r["threshold"]] * 2, [lookup[k] for k in d["threshold_cdf"]], s=25)
    axes[0].set(
        xlabel=r["outcome_units"],
        ylabel="Cumulative probability",
        title="Estimated outcome distributions",
        ylim=(0, 1),
        xlim=(d["outcome_axis"][0], d["outcome_axis"][-1]),
    )
    axes[0].legend(fontsize=8)
    levels = [row["level"] for row in d["quantiles"]]
    values = [lookup[row["difference"]] for row in d["quantiles"]]
    axes[1].plot(levels, values, "o-", label="Second price minus first")
    for row, value in zip(d["quantiles"], values, strict=True):
        if any(row["boundary_limited"]):
            axes[1].annotate(
                "grid endpoint",
                (row["level"], value),
                fontsize=8,
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
            )
    axes[1].margins(y=0.16)
    axes[1].axhline(0, color="gray", linestyle="--")
    axes[1].set(xlabel="Outcome quantile", ylabel=f"Change ({r['outcome_units']})", xticks=levels)
    axes[1].set_title("Changes across the outcome distribution")
    axes[1].set_xticklabels([f"{level:.0%}" for level in levels])
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle("Exploratory point estimates · Track T · No uncertainty intervals")
    fig.text(
        0.5,
        0.01,
        "Curves and tables use the same validated results. Evidence is included in the download.",
        ha="center",
        fontsize=7,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, facecolor="white")
    plt.close(fig)
