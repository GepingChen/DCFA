from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("GRADIO_TEMP_DIR", "/tmp/gradio")
os.environ.setdefault("GRADIO_RUN_HISTORY", "0")
os.environ.setdefault("DCFA_OUTPUT_ROOT", "/tmp/dcfa-zerogpu-runs")
os.environ.setdefault("DCFA_SECRET_ROOT", "/tmp/dcfa-zerogpu-secrets")
os.environ.setdefault(
    "DCFA_WEBSITE_GEMINI_CONFIG_FILE",
    str(Path(__file__).resolve().with_name("website_demo_gemini_v2.json")),
)

os.environ.setdefault(
    "DCFA_SPACE_CSV_DIALOGUE_CONFIG_FILE",
    str(Path(__file__).resolve().with_name("space_csv_dialogue_v1.json")),
)

import spaces  # noqa: F401, E402  # ZeroGPU must initialize before Gradio/DCFA imports.
from presentation import PRESENTATION_CSS, build_presentation

from dcfa_website_demo.zerogpu import build_zerogpu_app, zerogpu_launch_kwargs

live_demo = build_zerogpu_app(build_revision="2bc2c9d")
demo = build_presentation(live_demo, Path(__file__).resolve().with_name("cigarette-tabpfn35.html"))


if __name__ == "__main__":
    launch_options = zerogpu_launch_kwargs()
    launch_options["css"] += PRESENTATION_CSS
    demo.launch(**launch_options)
