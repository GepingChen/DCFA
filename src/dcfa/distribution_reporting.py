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
        return f"{float(lookup[key].value_raw):.1f}"

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
        "The PDF panel is an approximate probability density obtained by finite-differencing "
        "the displayed CDF grid. It is not a separate fitted model, is not smoothed, and does "
        "not extrapolate beyond the evaluated outcome range.",
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
    colors = ("#2563eb", "#f97316")
    fig, axes = plt.subplot_mosaic([["cdf", "pdf"], ["quantile", "quantile"]], figsize=(12, 8.6))
    for index, curve in enumerate(d["curves"]):
        axes["cdf"].plot(
            d["outcome_axis"],
            [lookup[k] for k in curve["cdf"]],
            color=colors[index],
            label=f"Price = {curve['price']:g}",
        )
    axes["cdf"].axvline(r["threshold"], color="gray", linestyle="--")
    for index, (cdf_key, probability_key) in enumerate(
        zip(d["threshold_cdf"], d["probabilities"], strict=True)
    ):
        cdf_value = lookup[cdf_key]
        axes["cdf"].scatter([r["threshold"]], [cdf_value], color=colors[index], s=28, zorder=3)
        axes["cdf"].annotate(
            f"P(> threshold) = {lookup[probability_key]:.1f}%",
            (r["threshold"], cdf_value),
            xytext=(7, 10 if index else -14),
            textcoords="offset points",
            fontsize=8,
            color=colors[index],
        )
    axes["cdf"].annotate(
        f"Outcome threshold = {r['threshold']:g}",
        (r["threshold"], 0.99),
        xytext=(6, -4),
        textcoords="offset points",
        va="top",
        fontsize=8,
        color="dimgray",
    )
    axes["cdf"].set(
        xlabel=r["outcome_units"],
        ylabel="P(sales ≤ outcome under intervention)",
        title="Interventional CDFs",
        ylim=(0, 1),
        xlim=(d["outcome_axis"][0], d["outcome_axis"][-1]),
    )
    axes["cdf"].legend(fontsize=8)

    for index, density in enumerate(d["densities"]):
        axes["pdf"].plot(
            d["density_axis"],
            [lookup[k] for k in density["pdf"]],
            color=colors[index],
            label=f"Price = {density['price']:g}",
        )
    axes["pdf"].set(
        xlabel=r["outcome_units"],
        ylabel="Approximate probability density",
        title="CDF-derived approximate density (PDF)",
        xlim=(d["outcome_axis"][0], d["outcome_axis"][-1]),
    )
    axes["pdf"].legend(fontsize=8)

    levels = [row["level"] for row in d["quantiles"]]
    values = [lookup[row["difference"]] for row in d["quantiles"]]
    axes["quantile"].plot(
        levels,
        values,
        "o-",
        color="#0f766e",
        label=f"Price {r['prices'][1]:g} − price {r['prices'][0]:g}",
    )
    for row, value in zip(d["quantiles"], values, strict=True):
        axes["quantile"].annotate(
            f"{value:.1f}",
            (row["level"], value),
            fontsize=8,
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
        )
        if any(row["boundary_limited"]):
            axes["quantile"].scatter(
                [row["level"]],
                [value],
                facecolors="white",
                edgecolors="#0f766e",
                linewidths=2,
                s=55,
                zorder=4,
            )
            axes["quantile"].annotate(
                "grid boundary",
                (row["level"], value),
                fontsize=8,
                xytext=(0, -16),
                textcoords="offset points",
                ha="center",
            )
    axes["quantile"].margins(y=0.22)
    axes["quantile"].axhline(0, color="gray", linestyle="--")
    axes["quantile"].set(
        xlabel="Outcome quantile",
        ylabel=f"Change ({r['outcome_units']})",
        xticks=levels,
    )
    axes["quantile"].set_title("Quantile changes across the outcome distribution")
    axes["quantile"].set_xticklabels([f"{level:.0%}" for level in levels])
    axes["quantile"].legend(fontsize=8)
    for ax in axes.values():
        ax.grid(alpha=0.2)
    fig.suptitle("Exploratory point estimates · Track T · No uncertainty intervals")
    fig.text(
        0.5,
        0.025,
        "PDF = finite-difference slope of the displayed CDF, with no smoothing or tail "
        "extrapolation. Curves and tables use the same validated result bundle.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, facecolor="white")
    plt.close(fig)
