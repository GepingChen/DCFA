from __future__ import annotations

import json
from pathlib import Path

import pytest

from dcfa_website_demo import prepared_report
from dcfa_website_demo.app import build_app


def test_missing_saved_report_does_not_start_analysis(tmp_path: Path, monkeypatch) -> None:
    loader = prepared_report.load_prepared_report

    def unavailable():
        return loader(tmp_path)

    monkeypatch.setattr(prepared_report, "load_prepared_report", unavailable)
    app = _space_app()
    config = json.dumps(app.config, default=str)
    assert "The saved example report is unavailable" in config
    assert "Download full report ZIP" not in config


def _space_app():
    def forbidden(*args, **kwargs):
        raise AssertionError("Viewing the example must not call a provider or analysis handler")

    return build_app(
        build_revision="deadbee",
        deployment_mode="zerogpu_canonical",
        space_authorize_handler=forbidden,
        space_csv_authorize_handler=forbidden,
        space_scenario_handler=forbidden,
        space_csv_handler=forbidden,
        space_csv_chat_handler=forbidden,
    )


def test_saved_report_is_default_and_has_no_execution_events() -> None:
    saved = prepared_report.load_prepared_report()
    app = _space_app()
    components = app.config["components"]
    tabs = [c["props"]["label"] for c in components if c["type"] == "tabitem"]
    assert tabs == ["Example report", "Upload CSV", "Run synthetic example"]
    assert (
        next(c for c in components if c["type"] == "tabs")["props"]["selected"] == "saved_example"
    )
    config = json.dumps(app.config, default=str)
    assert saved.report in [c["props"].get("value") for c in components]
    assert saved.warnings in [c["props"].get("value") for c in components]
    assert "No API key or Hugging Face sign-in" in config
    download_ids = {c["id"] for c in components if c["type"] == "downloadbutton"}
    assert len(download_ids) == 2
    for dependency in app.config["dependencies"]:
        assert not download_ids.intersection(dependency["inputs"])
        assert not download_ids.intersection(dependency["outputs"])
        assert not any(target[0] in download_ids for target in dependency["targets"])


def test_saved_public_files_match_original_archive() -> None:
    import zipfile

    saved = prepared_report.load_prepared_report()
    with zipfile.ZipFile(saved.archive) as archive:
        for name in ("report.md", "interventional_summary.png"):
            entry = next(n for n in archive.namelist() if n.endswith("/" + name))
            assert archive.read(entry) == (prepared_report.ASSET_ROOT / name).read_bytes()
    source_csv = (
        Path(__file__).resolve().parents[2] / "examples/cigarette_demand_small/cigarette_144.csv"
    )
    assert saved.csv.read_bytes() == source_csv.read_bytes()
    assert "Warnings and interpretation limits" in saved.warnings
    assert "Evidence ID" in saved.appendix


def test_missing_asset_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No analysis was started"):
        prepared_report.load_prepared_report(tmp_path)
