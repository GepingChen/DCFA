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
    assert len(download_ids) == 3
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


def _saved_records():
    import zipfile

    with zipfile.ZipFile(prepared_report.ASSET_ROOT / "report.zip") as archive:
        return {
            name: json.loads(archive.read("run-0001/" + name + ".json"))
            for name in ("result_bundle", "specification", "dataset_manifest", "backend_manifest")
        }


def test_display_derivative_preserves_original_and_resolves_summary_evidence():
    import re
    import zipfile

    saved = prepared_report.load_prepared_report()
    assert "Display-only derivative" in saved.context
    assert "144 observations" in saved.context and "1985, 1990 and 1995" in saved.context
    assert "stored natural logs" in saved.context
    assert saved.warnings.count("<li>") == 5
    assert "original/run-0001/" in saved.appendix
    assert "](original/" not in saved.appendix + saved.context
    with (
        zipfile.ZipFile(saved.archive) as original,
        zipfile.ZipFile(saved.display_archive) as display,
    ):
        for name in original.namelist():
            assert display.read("original/" + name) == original.read(name)
        report = display.read("report.md").decode()
        assert report == (prepared_report.ASSET_ROOT / "display_report.md").read_text()
        for target in re.findall(r"\]\(([^)]+)\)", report):
            assert target in display.namelist()
        bundle = json.loads(original.read("run-0001/result_bundle.json"))
        by_id = {q["evidence_id"]: q for q in bundle["queries"]}
        ids = re.findall(r"`(evidence_[a-z0-9]+)`", report)
        assert len(ids) == 9
        for eid in ids:
            assert by_id[eid]["value_display"] in saved.appendix
        assert len(bundle["queries"]) == 651
        assert "103.655" in saved.appendix and "**supported**" in saved.appendix
        assert "Probability above" not in saved.report


def test_warning_projection_preserves_changed_unknown_and_triggered_warnings():
    from dcfa.distribution_reporting import distribution_warning_html
    from dcfa.reporting import report_boundary

    records = _saved_records()
    bundle = records["result_bundle"]
    boundary = report_boundary(bundle, records["backend_manifest"])
    bundle["warnings"] += [
        {"code": code, "message": message}
        for code, message in (
            ("WEAK_FIRST_STAGE", "The instrument has weak empirical relevance."),
            ("WEAK_INTERVENTION_SUPPORT", "An intervention has weak support."),
            ("QUANTILE_GRID_ENDPOINT", "A quantile is limited by the grid endpoint."),
            ("FUTURE_WARNING", "Unknown restriction with <special> text."),
            ("DISTRIBUTIONAL_POINT_ESTIMATES", "Changed known message must survive."),
        )
    ]
    bundle["assumptions"].append("Additional unknown assumption.")
    rendered = distribution_warning_html(bundle, boundary=boundary + " Additional restriction.")
    import html

    for warning in bundle["warnings"][-5:]:
        assert html.escape(warning["message"]) in rendered
    assert "Additional unknown assumption." in rendered
    assert "Additional restriction." in rendered
    assert "scalar monotonicity" in rendered and "omitted confounding" in rendered
    assert "not individual effects" in rendered and "not separately fitted" in rendered
    assert "no baseline covariates W" in rendered and "release claims" in rendered


@pytest.mark.parametrize("omission", ["evidence", "warning", "support", "grid_export"])
def test_compact_verifier_rejects_omissions_after_existing_hashes_are_updated(
    tmp_path, monkeypatch, omission
):
    import zipfile

    from dcfa.artifact_validation import verify_run_directory
    from dcfa.canonical import file_sha256
    from dcfa.distribution_reporting import distribution_report
    from dcfa.errors import DCFAError
    from dcfa.reporting import report_boundary

    with zipfile.ZipFile(prepared_report.ASSET_ROOT / "report.zip") as archive:
        archive.extractall(tmp_path)
    root = tmp_path / "run-0001"
    records = _saved_records()
    # Isolate format compatibility from the source-tree check (the untouched archive is
    # separately verified using its actual historical source in manual verification).
    monkeypatch.setattr(
        "dcfa.artifact_validation.dcfa_source_tree_hash",
        lambda: records["backend_manifest"]["dcfa_source_tree_hash"],
    )
    assert verify_run_directory(root)["status"] == "valid"  # Legacy format path.
    report = distribution_report(
        records["result_bundle"],
        specification=records["specification"],
        dataset_manifest=records["dataset_manifest"],
        boundary=report_boundary(records["result_bundle"], records["backend_manifest"]),
    )

    def save_projection(text):
        (root / "report.md").write_text(text)
        path = root / "report_manifest.json"
        manifest = json.loads(path.read_text())
        manifest["report_hash"] = file_sha256(root / "report.md")
        path.write_text(json.dumps(manifest))
        path = root / "run_manifest.json"
        run = json.loads(path.read_text())
        for entry in run["artifact_hashes"]:
            filenames = {
                "report": "report.md",
                "report_manifest": "report_manifest.json",
                "distribution_results.json": "distribution_results.json",
            }
            if entry[0] in filenames:
                entry[1] = file_sha256(root / filenames[entry[0]])
        path.write_text(json.dumps(run))

    save_projection(report)
    assert verify_run_directory(root)["status"] == "valid"
    if omission == "evidence":
        report = report.replace(records["result_bundle"]["queries"][0]["evidence_id"], "omitted")
    elif omission == "warning":
        report = report.replace("omitted confounding are not addressed", "confounding is addressed")
    elif omission == "support":
        report = report.replace("**supported**", "**unsupported**")
    else:
        path = root / "distribution_results.json"
        export = json.loads(path.read_text())
        del export["evidence"]["cdf:0:0"]
        path.write_text(json.dumps(export))
    save_projection(report)
    with pytest.raises(DCFAError, match="projection"):
        verify_run_directory(root)


def test_generic_report_context_does_not_invent_cigarette_metadata():
    from dcfa.distribution_reporting import distribution_context

    records = _saved_records()
    spec = records["specification"]
    spec["roles"].update(outcome="log_quantity", treatment="log_cost", instrument="weather")
    context = distribution_context(
        records["result_bundle"]["distribution"],
        specification=spec,
        dataset_manifest={"row_count": 97},
    )
    assert "97 observations" in context and "Z = `weather`" in context
    assert not any(word in context for word in ("cigarette", "state-year", "1985", "144"))
