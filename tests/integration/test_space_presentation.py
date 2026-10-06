"""The presentation shell must retain live event wiring without running a model."""

import importlib.util
from pathlib import Path

import gradio as gr
from fastapi.testclient import TestClient
from gradio.routes import App


def test_report_shell_keeps_existing_api_and_saved_report(tmp_path):
    source = Path(__file__).resolve().parents[2] / "deployment/huggingface/presentation.py"
    spec = importlib.util.spec_from_file_location("space_presentation", source)
    presentation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(presentation)
    report = tmp_path / "report.html"
    report.write_text("<h1>Saved report</h1>")
    with gr.Blocks() as live:
        consent = gr.Checkbox(label="Consent required")
        result = gr.Textbox()
        button = gr.Button("Confirm and generate report")
        button.click(
            lambda approved: "allowed" if approved else "blocked",
            consent,
            result,
            api_name="consent_probe",
            queue=False,
        )
    original_functions = list(live.fns.values())
    shell = presentation.build_presentation(live, report)
    assert list(shell.fns.values()) == original_functions
    config = shell.get_config_file()
    assert any(
        c["type"] == "tabs" and c["props"]["selected"] == "report35" for c in config["components"]
    )
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
