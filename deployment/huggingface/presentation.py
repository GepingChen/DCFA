"""Presentation shell around the unchanged, pinned ZeroGPU runtime."""

from pathlib import Path

import gradio as gr

REPORT_URL = "https://gepingchen.github.io/agentic-tabcf/cigarette-tabpfn35.html"


def build_presentation(live_demo: gr.Blocks, report: Path) -> gr.Blocks:
    """Keep saved results separate from the existing authenticated live workflow."""
    for block in live_demo.blocks.values():
        if isinstance(block, gr.Tabs) and block.elem_id == "input-tabs":
            tabs = {child.id: child for child in block.children if isinstance(child, gr.Tab)}
            tabs["csv"].label = "Analyze your data"
            block.selected = "csv"
            block.children = [tabs["csv"], tabs["saved_example"]] + [
                child for child in block.children if child.id not in {"csv", "saved_example"}
            ]
            if "example" in tabs:
                # Hide the old runtime's public entry while preserving its shared callbacks.
                tabs["example"].visible = False

    with gr.Blocks(
        title="Agentic TabCF",
        analytics_enabled=False,
        fill_width=True,
        delete_cache=(300, 900),
    ) as demo:
        gr.Markdown(
            "# Agentic TabCF\n\n"
            "From a price question to a reviewable plan and a traceable report. "
            "**Built with PriorLabs-TabPFN.**"
        )
        with gr.Tabs(selected="report35"):
            with gr.Tab("TabPFN-3.5 example report", id="report35"):
                gr.Markdown(
                    "## If cigarette prices rose, how might sales change?\n\n"
                    "**Saved real TabPFN-3.5 analysis · exploratory point estimates · "
                    "development_only.** No login, API key or model call is needed to read it. "
                    "State–year per-capita sales, not individual smoking. "
                    "No confidence intervals, significance or policy-benefit claim.\n\n"
                    f"[Open the full report in your browser]({REPORT_URL}) "
                    "for full-width charts and expandable evidence. "
                    "The downloaded HTML also works offline."
                )
                gr.DownloadButton("Download standalone HTML report", value=str(report))
                gr.HTML(
                    f'<iframe src="{REPORT_URL}" title="Saved TabPFN-3.5 cigarette report" '
                    'style="width:100%;height:1050px;border:1px solid #d2dcda;border-radius:8px" '
                    'referrerpolicy="no-referrer"></iframe>'
                )
            with gr.Tab("Interactive analysis", id="live"):
                gr.Markdown(
                    "**Live workflow:** sign in and provide the required credentials and "
                    "data-transfer consent before computation. The inner “Example report” "
                    "tab is a separate historical TabPFN v2 run; it is not the 3.5 report above."
                )
                live_demo.render()
    return demo.queue(max_size=8, default_concurrency_limit=1)
