"""Tables, downloadable projections and plots from one validated distribution bundle."""

from __future__ import annotations

import html
import re
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


COMPACT_REPORT_MARKER = "<!-- Compact distribution report v1 -->"


def headline_queries(distribution, queries):
    """Only visible summaries; grid points remain in the complete evidence export."""
    keys = set()
    for row in distribution["quantiles"]:
        if row["level"] in (0.25, 0.5, 0.75):
            keys.update(row["values"])
            keys.add(row["difference"])
    if distribution["request"]["threshold"] is not None:
        keys.update(distribution["probabilities"])
        keys.add(distribution["probability_difference"])
    return [q for q in to_primitive(queries) if q["query_id"] in keys]


def distribution_context(
    distribution, *, specification=None, dataset_manifest=None, sample_description=""
):
    """Background from confirmed roles/units and supplied dataset metadata only."""
    r = distribution["request"]
    p0, p1 = r["prices"]
    spec = to_primitive(specification) if specification is not None else {}
    data = to_primitive(dataset_manifest) if dataset_manifest is not None else {}
    roles = spec.get("roles", {})
    lines = [
        "### Distributional analysis — Track T · Exploratory estimates",
        "",
        "**Question:** Under the maintained IV assumptions, how does the estimated "
        f"outcome distribution change from treatment {p0:g} to {p1:g} "
        f"{r['treatment_units']}? All differences are {p1:g} minus {p0:g}.",
        "",
    ]
    if data.get("row_count") is not None:
        lines += [f"**Sample:** {data['row_count']} observations. " + sample_description, ""]
    if roles:
        lines += [
            f"**Variables:** Y = `{roles['outcome']}`; X = `{roles['treatment']}`; "
            f"Z = `{roles['instrument']}`. No baseline covariates.",
            "",
        ]
    scales = {
        "stored_natural_log": "stored natural logs (not logged again)",
        "original": "original units",
    }
    lines += [
        f"**Scales:** Model X: {scales.get(r['treatment_scale'], r['treatment_scale'])}; "
        f"model Y: {scales.get(r['outcome_scale'], r['outcome_scale'])}. "
        f"Displayed interventions: {r['treatment_units']}; outcome axis, quantiles and "
        f"quantile changes: {r['outcome_units']}. "
        "Logged model outcomes are mapped back to original units for display."
        if r["outcome_scale"] == "stored_natural_log"
        else f"**Scales:** Model and display use the requested scales: "
        f"X = {r['treatment_scale']}, Y = {r['outcome_scale']}. "
        f"Treatment units: {r['treatment_units']}; outcome units: {r['outcome_units']}.",
    ]
    return "\n".join(lines)


def distribution_markdown(distribution, queries):
    """Use validated values with references to the compact evidence index."""
    d = distribution
    r = d["request"]
    selected = headline_queries(d, queries)
    lookup = {q["query_id"]: q for q in selected}
    refs = {q["query_id"]: index for index, q in enumerate(selected, 1)}

    def cell(key, limited=False):
        display = "Not resolved on grid" if limited else f"{float(lookup[key]['value_raw']):.1f}"
        if display == "-0.0":
            display = "0.0"
        return f"{display} [{refs[key]}]"

    p0, p1 = r["prices"]
    lines = [
        "**Outcome quantiles**",
        "",
        f"Levels and changes are in {r['outcome_units']}. "
        "Each row describes a percentile of the estimated outcome distribution; "
        "the median is the 50th percentile. Changes use unrounded estimates, "
        "so rounded columns may not subtract exactly. References resolve in the appendix.",
        "",
        f"| Quantile | At {p0:g} | At {p1:g} | Change ({p1:g} − {p0:g}) |",
        "|:---|---:|---:|---:|",
    ]
    for row in d["quantiles"]:
        if row["level"] not in (0.25, 0.5, 0.75):
            continue
        values = [
            cell(key, limited)
            for key, limited in zip(row["values"], row["boundary_limited"], strict=True)
        ]
        change = cell(row["difference"], any(row["boundary_limited"]))
        lines.append(f"| {row['level']:.0%} | {values[0]} | {values[1]} | {change} |")
    if r["threshold"] is not None:
        lines += [
            "",
            "**Probability above the specified outcome threshold**",
            "",
            f"Outcome strictly exceeding {r['threshold']:g} {r['outcome_units']}. "
            "Levels are percentages; the change is in percentage points.",
            "",
            f"| At {p0:g} (%) | At {p1:g} (%) | Change (percentage points) |",
            "|---:|---:|---:|",
            f"| {cell(d['probabilities'][0])} | {cell(d['probabilities'][1])} | "
            f"{cell(d['probability_difference'])} |",
        ]
    return "\n".join(lines)


_POINT_WARNING = (
    "Point estimates only, without confidence intervals or significance. "
    "Quantile changes are distributional, not individual effects. "
    "CDFs cover only the evaluated outcome grid; no extrapolation."
)
_POOLED_WARNING = (
    "Real-data exploratory state-year aggregates with equal observation weights, repeated "
    "states, and omitted income and state/year effects. Within-state dependence and omitted "
    "confounding are not addressed. Instrument exclusion and exogeneity remain assumptions."
)
_MODEL_ASSUMPTION = (
    "One continuous treatment, one continuous outcome, one scalar instrument, "
    "and no baseline covariates W."
)
_IV_ASSUMPTION = (
    "Relevance, exclusion, instrument exogeneity, scalar monotonicity, and common support "
    "are assumptions; empirical diagnostics do not prove them."
)
_DIAGNOSTIC_LIMIT = (
    "These are empirical diagnostics. They do not prove instrument validity or identification."
)
_DEVELOPMENT_WARNING = (
    "This TabPFN-backed managed/local run is development-only, not a hash-locked Track T "
    "result, and is ineligible for release claims."
)
_DEVELOPMENT_ASSUMPTIONS = {
    "Local TabPFN v2 uses the recorded checkpoint artifact, but the current runtime image "
    "is not release-locked and cannot enter locked Track T evidence.": (
        "Development-only local TabPFN v2 output. The checkpoint artifact is recorded, but the "
        "runtime image is not release-locked. Ineligible for locked Track T or release claims."
    ),
    "Managed-service TabPFN is service-version-traceable rather than bitwise reproducible "
    "and cannot enter locked Track T evidence.": (
        "Development-only managed TabPFN output. Service-version-traceable, not bitwise "
        "checkpoint/image reproducible. Ineligible for locked Track T or release claims."
    ),
    "This TabPFN development profile is recorded in the backend manifest and cannot enter "
    "locked Track T evidence.": (
        "Development-only TabPFN output. The backend manifest records the execution profile. "
        "Ineligible for locked Track T or release claims."
    ),
}


def distribution_warning_html(bundle, *, boundary=""):
    """Merge only recognized exact text; new codes or changed messages remain visible."""
    b = to_primitive(bundle)
    groups = {}
    remaining = []
    assumptions = list(b["assumptions"])
    dev = None
    for warning in b["warnings"]:
        code, message = warning["code"], warning["message"]
        if (code, message) == ("DISTRIBUTIONAL_POINT_ESTIMATES", _POINT_WARNING):
            groups["Uncertainty and interpretation"] = message
        elif (code, message) == ("POOLED_STATE_YEAR_LIMITATIONS", _POOLED_WARNING):
            groups["Data and model"] = message.removesuffix(
                " Instrument exclusion and exogeneity remain assumptions."
            )
            # Preserve the removed clause even when the usual IV assumption is absent.
            groups["IV assumptions"] = "Instrument exclusion and exogeneity remain assumptions."
        elif (code, message) == ("DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE", _DEVELOPMENT_WARNING):
            dev = message
        else:
            remaining.append(f"{code}: {message}")
    if _MODEL_ASSUMPTION in assumptions:
        groups["Data and model"] = (
            groups.get("Data and model", "") + " " + _MODEL_ASSUMPTION
        ).strip()
        assumptions.remove(_MODEL_ASSUMPTION)
    if _IV_ASSUMPTION in assumptions:
        groups["IV assumptions"] = _IV_ASSUMPTION.replace(
            "empirical diagnostics do not prove them.",
            "empirical diagnostics do not prove instrument validity or identification.",
        )
        assumptions.remove(_IV_ASSUMPTION)
    interpretation = b["diagnostics"]["interpretation"]
    if interpretation != _DIAGNOSTIC_LIMIT or not groups.get("IV assumptions"):
        remaining.append(interpretation)
    elif "identification" not in groups["IV assumptions"]:
        groups["IV assumptions"] += " " + interpretation
    known_boundary = ""
    if dev:
        for assumption, summary in _DEVELOPMENT_ASSUMPTIONS.items():
            if assumption in assumptions:
                dev = summary
                assumptions.remove(assumption)
                from dcfa.reporting import TABPFN_BOUNDARIES

                profile = (
                    "local"
                    if assumption.startswith("Local TabPFN v2")
                    else "managed"
                    if assumption.startswith("Managed-service")
                    else "development"
                )
                known_boundary = TABPFN_BOUNDARIES[profile]
                break
        groups["Development status"] = dev
    remaining.extend(assumptions)
    # Recognized TabPFN boundaries restate the warning and execution-profile assumption.
    # Retain any other boundary (including sklearn restrictions) verbatim.
    if boundary and boundary != known_boundary:
        remaining.append(boundary.replace("> ", "").replace("**", ""))
    groups["Density approximation"] = (
        "The PDF is an approximate density from finite-differencing the displayed CDF grid; "
        "it is not separately fitted, smoothed or renormalized. No tail extrapolation is "
        "performed; omitted tail mass means its integral over this range need not be one."
    )
    order = (
        "Uncertainty and interpretation",
        "Data and model",
        "IV assumptions",
        "Density approximation",
        "Development status",
    )
    items = [
        f"<li><strong>{title}:</strong> {html.escape(groups[title])}</li>"
        for title in order
        if title in groups
    ]
    items += [f"<li>{html.escape(note)}</li>" for note in dict.fromkeys(remaining)]
    return (
        '<div class="distribution-warnings" style="font-size:0.875em;line-height:1.5">'
        '<small style="font-size:inherit"><strong>Warnings and interpretation limits</strong><ul>'
        + "".join(items)
        + "</ul></small></div>"
    )


def archive_links_as_text(markdown: str) -> str:
    """Archive members have no relative URL on the website; downloads retain live links."""
    return re.sub(
        r"\[([^\]]+)\]\((?!https?://)([^)]+)\)",
        lambda match: f"{match[1]} (`{match[2]}` in the downloaded ZIP)",
        markdown,
    )


def distribution_appendix(bundle, *, artifact_prefix=""):
    b = to_primitive(bundle)
    r = b["distribution"]["request"]
    lines = ["<details>", "<summary>Technical appendix and evidence index</summary>", ""]
    for title, key in (
        ("Run ID", "run_id"),
        ("Result bundle", "result_bundle_id"),
        ("Specification", "specification_id"),
        ("Dataset hash", "dataset_hash"),
        ("Evidence status", "evidence_status"),
    ):
        lines.append(f"- {title}: `{b[key]}`")
    lines += [
        "",
        "**Empirical support and diagnostics**",
        "",
        "Support describes empirical coverage, not proof of IV validity or identification. "
        "X values and intervals below use the model input scale: " + r["treatment_scale"] + ".",
        "",
    ]
    for item in b["support"]:
        index = b["x_grid"].index(item["x"]) if item["x"] in b["x_grid"] else None
        label = (
            f"Intervention {r['prices'][index]:g} {r['treatment_units']}"
            if index is not None and index < len(r["prices"])
            else "Intervention"
        )
        lines += [
            f"- {label} (model X = {item['x']:.6g}): **{item['status']}**; "
            f"coverage score {item['coverage_score']:.6g}. {item['reason']} "
            f"Strict interval: [{item['strict_interval'][0]:.6g}, "
            f"{item['strict_interval'][1]:.6g}]; recommended interval: "
            f"[{item['recommended_interval'][0]:.6g}, {item['recommended_interval'][1]:.6g}]."
        ]
    labels = (
        ("first_stage_f", "First-stage F"),
        ("first_stage_r2", "First-stage R²"),
        ("control_rank_cvm", "Control-rank CvM"),
        ("control_rank_mean", "Control-rank mean"),
        ("residual_dependence_score", "Residual-dependence score"),
    )
    lines += ["", "| Stored diagnostic | Value |", "|---|---:|"]
    lines += [f"| {label} | {b['diagnostics'][key]:.6g} |" for key, label in labels]
    lines += [
        "",
        "**Summary evidence**",
        "",
        "| Reference | Query | Validated value | Evidence ID |",
        "|---|---|---|---|",
    ]
    for index, query in enumerate(headline_queries(b["distribution"], b["queries"]), 1):
        lines.append(
            f"| [{index}] | `{query['query_id']}` | {query['value_display']} "
            f"{query['units']} | `{query['evidence_id']}` |"
        )
    lines += [
        "",
        "Complete CDF/PDF grid evidence is in "
        f"[distribution_results.json]({artifact_prefix}distribution_results.json): "
        "`distribution.curves[].cdf` and `distribution.densities[].pdf` contain query IDs; "
        "`evidence[query_id]` contains their values, units, support and evidence IDs. "
        f"[evidence_records.jsonl]({artifact_prefix}evidence_records.jsonl) resolves every "
        "evidence ID. Full support, diagnostics, raw warning records and assumptions: "
        f"[result_bundle.json]({artifact_prefix}result_bundle.json).",
        "",
        "### Warning codes",
        "",
    ]
    lines += [f"- `{warning['code']}`" for warning in b["warnings"]]
    return "\n".join(lines + ["", "</details>"])


def distribution_report(
    bundle,
    *,
    boundary="",
    specification=None,
    dataset_manifest=None,
    sample_description="",
    artifact_prefix="",
    display_note="",
):
    b = to_primitive(bundle)
    return (
        "\n\n".join(
            [
                "# Agentic TabCF report",
                COMPACT_REPORT_MARKER,
                display_note,
                distribution_context(
                    b["distribution"],
                    specification=specification,
                    dataset_manifest=dataset_manifest,
                    sample_description=sample_description,
                ),
                "![Estimated outcome distributions and summaries](interventional_summary.png)",
                distribution_markdown(b["distribution"], b["queries"]),
                distribution_appendix(b, artifact_prefix=artifact_prefix),
                distribution_warning_html(b, boundary=boundary),
            ]
        )
        + "\n"
    )


def render_distribution_plot(bundle, ledger, output_path: Path):
    validate_bundle_evidence(bundle, ledger)
    render_distribution_figure(
        to_primitive(bundle)["distribution"], to_primitive(bundle)["queries"], output_path
    )


def render_distribution_figure(distribution, queries, output_path: Path):
    """Plot stored projections only; callers validate their source bundle first."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = distribution
    r = d["request"]
    lookup = {q["query_id"]: q["value_raw"] for q in queries}
    colors = ("#2563eb", "#f97316")
    fig, axes = plt.subplot_mosaic([["cdf"], ["pdf"]], figsize=(6, 8.2))
    for index, curve in enumerate(d["curves"]):
        axes["cdf"].plot(
            d["outcome_axis"],
            [lookup[k] for k in curve["cdf"]],
            color=colors[index],
            label=f"Treatment = {curve['price']:g}",
        )
    if r["threshold"] is not None:
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
        ylabel="Cumulative probability",
        title="Interventional CDFs",
        ylim=(0, 1),
        xlim=(d["outcome_axis"][0], d["outcome_axis"][-1]),
    )
    axes["cdf"].legend(fontsize=11)

    for index, density in enumerate(d["densities"]):
        axes["pdf"].plot(
            d["density_axis"],
            [lookup[k] for k in density["pdf"]],
            color=colors[index],
            label=f"Treatment = {density['price']:g}",
        )
    axes["pdf"].set(
        xlabel=r["outcome_units"],
        ylabel="Approximate probability density",
        title="CDF-derived approximate density",
        xlim=(d["outcome_axis"][0], d["outcome_axis"][-1]),
    )
    axes["pdf"].legend(fontsize=11)

    for ax in axes.values():
        ax.grid(alpha=0.2)
        ax.tick_params(labelsize=11)
        ax.xaxis.label.set_size(12)
        ax.yaxis.label.set_size(12)
    fig.suptitle("Exploratory distribution estimates · Track T")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, facecolor="white")
    plt.close(fig)
