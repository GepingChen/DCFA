"""Display the curated cigarette report without providers or statistical execution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ASSET_ROOT = Path(__file__).with_name("assets") / "cigarette_v1"


@dataclass(frozen=True)
class PreparedReport:
    context: str
    report: str
    warnings: str
    appendix: str
    plot: Path
    csv: Path
    archive: Path
    display_archive: Path
    metadata: dict[str, object]


def load_prepared_report(root: Path = ASSET_ROOT) -> PreparedReport:
    """Read public, release-reviewed files; never fit or contact a provider."""
    names = (
        "report.md",
        "interventional_summary.png",
        "cigarette_144.csv",
        "report.zip",
        "metadata.json",
        "display_report.md",
        "display_summary.png",
        "display_report.zip",
    )
    if any(not (root / name).is_file() for name in names):
        raise ValueError("The saved example report is unavailable. No analysis was started.")
    report = (root / "display_report.md").read_text(encoding="utf-8")
    body, appendix = report.split("<details>", 1)
    appendix, warnings = appendix.split("</details>", 1)
    context, body = body.split(
        "![Estimated outcome distributions and summaries](interventional_summary.png)", 1
    )
    context = "\n".join(
        line for line in context.splitlines() if not line.startswith(("# Agentic", "<!--"))
    )
    appendix = appendix.replace("<summary>Technical appendix and evidence index</summary>", "")
    metadata = json.loads((root / names[4]).read_text(encoding="utf-8"))
    for key in ("saved_at_utc", "source_commit"):
        if not isinstance(metadata.get(key), str):
            raise ValueError("The saved example metadata is incomplete.")
    from dcfa.distribution_reporting import archive_links_as_text

    return PreparedReport(
        context=archive_links_as_text(context.strip()),
        report=body.strip(),
        warnings=warnings.strip(),
        appendix=archive_links_as_text(appendix.strip()),
        plot=root / "display_summary.png",
        csv=root / names[2],
        archive=root / names[3],
        display_archive=root / "display_report.zip",
        metadata=metadata,
    )


def render_prepared_report() -> None:
    """Create a read-only report tab with no event handlers or conversation state."""
    import gradio as gr

    gr.Markdown(
        "## Cigarette demand: what does the tool deliver?\n\n"
        "A saved report from a real TabPFN run. **No API key or Hugging Face sign-in "
        "is needed to view it; viewing does not rerun the analysis.**"
    )
    try:
        saved = load_prepared_report()
    except (OSError, ValueError, KeyError):
        gr.Markdown("The saved example report is unavailable. No analysis was started.")
        return
    gr.Markdown(saved.context, elem_classes="demo-answer")
    gr.Image(
        value=str(saved.plot),
        interactive=False,
        show_label=False,
        elem_id="example-plot",
        height=None,
    )
    gr.Markdown(saved.report, elem_classes="demo-answer")
    with gr.Row():
        gr.DownloadButton("Download demo CSV", value=str(saved.csv))
        gr.DownloadButton(
            "Download readable report ZIP", value=str(saved.display_archive), variant="primary"
        )
        gr.DownloadButton("Download original report ZIP", value=str(saved.archive))
    gr.Markdown(
        "The readable ZIP contains a display-only report and figure plus the unchanged original "
        "run files under original/run-0001/. Open report.md alongside its image in a Markdown "
        "viewer. The original ZIP remains available separately.\n\n"
        "[Data source and preparation](https://github.com/GepingChen/DCFA/blob/main/"
        "examples/cigarette_demand_small/SOURCE.md) · "
        "[Data license](https://github.com/GepingChen/DCFA/blob/main/"
        "examples/cigarette_demand_small/GPL-2.0.txt)"
    )
    with gr.Accordion("Technical appendix and run details", open=False):
        gr.Markdown(saved.appendix, elem_classes="demo-answer")
        gr.Markdown(
            f"Run saved: {saved.metadata['saved_at_utc']} · "
            f"Source version: `{saved.metadata['source_commit']}` · "
            "Backend: local TabPFN v2 on HF ZeroGPU."
        )
    gr.HTML(saved.warnings)


def write_display_derivative(root: Path = ASSET_ROOT) -> None:
    """Refresh display-only assets from the immutable original ZIP, without model execution.

    Run with: python -m dcfa_website_demo.prepared_report
    """
    import tempfile
    import zipfile

    from dcfa.distribution_reporting import distribution_report, render_distribution_figure
    from dcfa.reporting import report_boundary

    with tempfile.TemporaryDirectory(prefix="dcfa-display-") as temporary:
        with zipfile.ZipFile(root / "report.zip") as archive:
            archive.extractall(temporary)
        source = Path(temporary) / "run-0001"
        bundle = json.loads((source / "result_bundle.json").read_text())
        spec = json.loads((source / "specification.json").read_text())
        data = json.loads((source / "dataset_manifest.json").read_text())
        backend = json.loads((source / "backend_manifest.json").read_text())
        report = distribution_report(
            bundle,
            boundary=report_boundary(bundle, backend),
            specification=spec,
            dataset_manifest=data,
            sample_description=(
                "48 US states in 1985, 1990 and 1995; state-year aggregates with equal weights. "
                "Annual cigarette sales per capita (Y), real price (X), real sales tax (Z). "
                "Sample details: [data source and preparation](original/SOURCE.md)."
            ),
            artifact_prefix="original/run-0001/",
            display_note=(
                "**Display-only derivative of the saved cigarette run; no new fit or analysis.** "
                "The run and evidence identities below belong to the original result. "
                "The unchanged original report is [available here](original/run-0001/report.md)."
            ),
        )
        (root / "display_report.md").write_text(report, encoding="utf-8")
        render_distribution_figure(
            bundle["distribution"], bundle["queries"], root / "display_summary.png"
        )
        with zipfile.ZipFile(root / "display_report.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(root / "display_report.md", "report.md")
            archive.write(root / "display_summary.png", "interventional_summary.png")
            for path in sorted(source.iterdir()):
                archive.write(path, "original/run-0001/" + path.name)
            for name in ("SOURCE.md", "GPL-2.0.txt", "metadata.json"):
                archive.write(root / name, "original/" + name)


if __name__ == "__main__":
    write_display_derivative()
