"""One styled workspace and a separate gallery around the pinned ZeroGPU runtime."""

from pathlib import Path

import gradio as gr

REPORT_URL = "https://gepingchen.github.io/agentic-tabcf/cigarette-tabpfn35.html"

PRESENTATION_CSS = """
#main-tabs > .tab-nav { margin: 1rem 0; }
#report-version-tabs > .tab-nav { margin-bottom: 1rem; }
#report-version-tabs .tabitem { min-width: 0; }
.demo-report-intro { color: var(--demo-muted); line-height: 1.55; }
.demo-report-frame iframe { display: block; width: 100%; height: 1050px;
  border: 1px solid var(--demo-line); border-radius: .35rem; }
#confirm-report-button.primary { min-height: 3rem; background: var(--demo-accent-deep);
  color: white; font-weight: 750; }
"""


def build_presentation(live_demo: gr.Blocks, report: Path) -> gr.Blocks:
    """Reparent existing controls so their IDs, state and callbacks stay intact."""
    input_tabs = next(
        block for block in live_demo.blocks.values()
        if isinstance(block, gr.Tabs) and block.elem_id == "input-tabs"
    )
    tabs = {child.id: child for child in input_tabs.children if isinstance(child, gr.Tab)}
    csv, historical = tabs["csv"], tabs["saved_example"]
    workspace = next(
        block for block in live_demo.blocks.values() if block.elem_id == "analysis-input"
    )
    input_column = next(child for child in workspace.children if input_tabs in child.children)
    original_csv_children = list(csv.children)
    original_roots = list(live_demo.children)
    policy_blocks = [
        block for block in original_roots[:original_roots.index(workspace)]
        if not (isinstance(block, gr.HTML) and "demo-hero" in str(block.value))
    ]
    for block in live_demo.blocks.values():
        if isinstance(block, gr.Button) and block.value == "Confirm and generate report":
            block.elem_id = "confirm-report-button"
    csv.label = "Analyze your data"
    historical.label = "TabPFN v2 · Historical"
    historical.id = "historical"
    synthetic = tabs.get("example")
    if synthetic is not None:
        synthetic.visible = False

    with gr.Blocks(
        title="Agentic TabCF", analytics_enabled=False,
        fill_width=True, delete_cache=(300, 900),
    ) as demo:
        # Register every existing component and event before changing only the layout tree.
        live_demo.render()
        hero = gr.HTML(
            '<header class="demo-hero"><h1>Agentic TabCF</h1>'
            '<p class="demo-hero-copy">Upload your data. Describe your question. '
            'Explore treatment effects.</p></header>'
        )
        with gr.Tabs(selected="csv", elem_id="main-tabs") as main_tabs:
            with gr.Tab("Example reports", id="reports"):
                gr.Markdown(
                    "The same cigarette dataset and price question, analyzed in two "
                    "independent model runs. These saved reports do not rerun analysis "
                    "or require sign-in. Differences do not establish model superiority.",
                    elem_classes="demo-report-intro",
                )
                with gr.Tabs(selected="report35", elem_id="report-version-tabs") as report_tabs:
                    with gr.Tab("TabPFN 3.5", id="report35"):
                        gr.Markdown(
                            "### Cigarette sales · TabPFN 3.5\n\n"
                            "Saved `v3.5_default` run · exploratory point estimates · "
                            "`development_only`. State–year per-capita sales, not individual "
                            "smoking. No confidence intervals, significance or policy-benefit "
                            "claim.\n\n"
                            f"[Open the full report]({REPORT_URL}) for full-width charts "
                            "and expandable evidence. The downloaded HTML also works offline."
                        )
                        gr.DownloadButton("Download standalone HTML report", value=str(report))
                        gr.HTML(
                            f'<iframe src="{REPORT_URL}" '
                            'title="Saved TabPFN-3.5 cigarette report" '
                            'referrerpolicy="no-referrer"></iframe>',
                            elem_classes="demo-report-frame",
                        )
        with csv:
            with gr.Accordion("Data and model policy", open=False) as policy:
                pass
        with historical:
            historical_note = gr.Markdown(
                "**Historical TabPFN v2 run.** This report comes from a separate saved "
                "analysis of the same data and question. Its results and downloads belong "
                "to that run, not the TabPFN 3.5 report.",
                elem_classes="demo-report-intro",
            )

    # Move the upload and shared results into one pane, without nesting a second app.
    input_column.children = original_csv_children + [
        child for child in input_column.children if child is not input_tabs
    ]
    policy.children = policy_blocks
    csv.children = [workspace, policy]
    main_tabs.children = [csv, main_tabs.children[0]] + ([synthetic] if synthetic else [])
    report_tabs.children.append(historical)
    historical.children.remove(historical_note)
    historical.children.insert(0, historical_note)
    demo.children = [hero, main_tabs] + [
        block for block in original_roots
        if block is not workspace and block not in policy_blocks
        and not (isinstance(block, gr.HTML) and "demo-hero" in str(block.value))
    ]
    return demo.queue(max_size=8, default_concurrency_limit=1)
