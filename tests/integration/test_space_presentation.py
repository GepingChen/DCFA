"""Rearranging the public workspace must preserve live consent and result wiring."""

import importlib.util
from pathlib import Path

import gradio as gr
from fastapi.testclient import TestClient
from gradio.routes import App


def test_report_gallery_keeps_existing_api_state_and_result_controls(tmp_path):
    source = Path(__file__).resolve().parents[2] / "deployment/huggingface/presentation.py"
    spec = importlib.util.spec_from_file_location("space_presentation", source)
    presentation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(presentation)
    report = tmp_path / "report.html"
    report.write_text("<h1>Saved report</h1>")
    with gr.Blocks() as live:
        gr.HTML('<header class="demo-hero"><h1>Old heading</h1></header>')
        mode = gr.Radio(["api_preferred"], value="api_preferred", elem_id="analysis-mode")
        policy = gr.Markdown("**Data and model policy:** Existing transfer rules")
        with gr.Column(elem_id="analysis-input") as workspace:
            with gr.Column():
                with gr.Tabs(selected="saved_example", elem_id="input-tabs"):
                    with gr.Tab("Example report", id="saved_example"):
                        historical_text = gr.Markdown("Saved historical report")
                    with gr.Tab("Upload CSV", id="csv"):
                        consent = gr.Checkbox(label="Consent required")
                        button = gr.Button("Confirm and generate report")
                    with gr.Tab("Run synthetic example", id="example"):
                        gr.Button("Run example")
            with gr.Column(elem_id="analysis-results") as results:
                result = gr.Textbox()
        gr.HTML('<footer class="demo-footer">Original attribution</footer>')
        button.click(
            lambda approved: "allowed" if approved else "blocked",
            consent, result, api_name="consent_probe", queue=False,
        )
    original_functions = list(live.fns.values())
    shell = presentation.build_presentation(live, report)
    assert list(shell.fns.values()) == original_functions
    main_tabs = next(b for b in shell.blocks.values() if b.elem_id == "main-tabs")
    report_tabs = next(b for b in shell.blocks.values() if b.elem_id == "report-version-tabs")
    assert main_tabs.selected == "csv"
    assert [tab.label for tab in main_tabs.children if tab.visible] == [
        "Analyze your data", "Example reports",
    ]
    assert report_tabs.selected == "report35"
    assert [tab.label for tab in report_tabs.children] == [
        "TabPFN 3.5", "TabPFN v2 · Historical",
    ]
    assert workspace in main_tabs.children[0].children
    assert results in workspace.children
    def contains(parent, target):
        return parent is target or any(
            contains(child, target) for child in getattr(parent, "children", [])
        )

    assert contains(workspace.children[0], consent)
    assert historical_text in report_tabs.children[1].children
    assert contains(main_tabs.children[0].children[1], mode)
    assert policy in main_tabs.children[0].children[1].children
    config = shell.get_config_file()
    by_id = {c["id"]: c for c in config["components"]}
    layout_ids = []

    def visit(node):
        layout_ids.append(node["id"])
        for child in node.get("children", []):
            visit(child)

    visit(config["layout"])
    assert len(layout_ids) == len(set(layout_ids))
    visible_heroes = [
        by_id[i] for i in layout_ids if i in by_id
        and by_id[i]["type"] == "html" and "demo-hero" in by_id[i]["props"]["value"]
    ]
    assert len(visible_heroes) == 1
    assert any(
        c["type"] == "html" and presentation.REPORT_URL in c["props"]["value"]
        for c in config["components"]
    )
    assert any(c["type"] == "downloadbutton" for c in config["components"])
    with TestClient(App.create_app(shell)) as client:
        for approved, expected in [(False, "blocked"), (True, "allowed")]:
            response = client.post("/gradio_api/run/consent_probe", json={"data": [approved]})
            assert response.status_code == 200
            assert response.json()["data"] == [expected]
