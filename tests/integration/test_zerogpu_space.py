from __future__ import annotations

import json
import zipfile
from pathlib import Path

import gradio as gr
import pytest

import dcfa_website_demo.app as app_module
import dcfa_website_demo.zerogpu as zerogpu_module
from dcfa.artifact_validation import verify_run_directory
from dcfa.constants import EstimatorBackend
from dcfa.tabcf_iv.backend import SklearnQuantileBackend
from dcfa_website_demo.app import (
    DEFAULT_CSV_QUESTION,
    DEMO_CSS,
    _input_error_outputs,
    build_app,
    execute_local_csv_upload,
    execute_local_portfolio_scenario,
    portfolio_ui_updates,
)
from dcfa_website_demo.csv_upload import export_standard_demo_csv
from dcfa_website_demo.zerogpu import zerogpu_launch_kwargs
from tests.provider_fakes import FakeGeminiClient


class FakeLocalTabPFNBackend(SklearnQuantileBackend):
    """Contract fake with TabPFN identity and deterministic CPU mechanics."""

    name = EstimatorBackend.TABPFN


@pytest.fixture(autouse=True)
def local_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        app_module,
        "make_local_tabpfn_v2_backend",
        lambda specification, model_path: FakeLocalTabPFNBackend(seed=specification.seed),
    )


def test_canonical_preset_uses_no_gemini_and_verifies_artifact(tmp_path: Path) -> None:
    result = execute_local_portfolio_scenario(
        "strong_iv",
        128,
        20260810,
        model_path=tmp_path / "unused-fake-model.ckpt",
        output_root=tmp_path / "runs",
    )

    assert result.response.status == "completed"
    assert result.llm_trace["provider"] == "none"
    assert result.llm_trace["model_request_count"] == 0
    assert result.llm_trace["data_rows_sent_to_gemini"] == 0
    assert result.output_dir is not None
    assert verify_run_directory(result.output_dir)["status"] == "valid"


def test_duplicate_csv_uses_local_boundary_and_one_gemini_call(tmp_path: Path) -> None:
    csv_path = export_standard_demo_csv(tmp_path / "standard.csv")
    gemini_key = tmp_path / "gemini-key"
    gemini_key.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini_key.chmod(0o600)
    client = FakeGeminiClient()

    result = execute_local_csv_upload(
        csv_path,
        "Y",
        "X",
        "Z",
        True,
        20260813,
        model_path=tmp_path / "unused-fake-model.ckpt",
        question="Estimate the median outcome contrast from high to low treatment.",
        output_root=tmp_path / "runs",
        gemini_api_key_file=gemini_key,
        gemini_client=client,
        gemini_sdk_version="2.18.1",
    )

    assert result.response.status == "completed"
    assert len(client.interactions.calls) == 1
    model_input = json.loads(client.interactions.calls[0]["input"])
    assert "rows" not in model_input
    assert result.output_dir is not None
    manifest = json.loads((result.output_dir / "dataset_manifest.json").read_text())
    assert manifest["source_kind"] == "user_authorized_hf_zerogpu_csv_upload"
    assert "Prior Labs" not in manifest["license_note"]
    assert verify_run_directory(result.output_dir)["status"] == "valid"


def test_archive_is_path_safe_and_secret_scan_blocks_leak(tmp_path: Path) -> None:
    run = tmp_path / "run-0001"
    run.mkdir()
    (run / "result.json").write_text('{"status":"valid"}', encoding="utf-8")
    archive = zerogpu_module._archive_run(run)
    with zipfile.ZipFile(archive) as stream:
        assert stream.namelist() == ["run-0001/result.json"]

    (run / "leak.txt").write_text("private-secret", encoding="utf-8")
    with pytest.raises(RuntimeError, match="credential reached"):
        zerogpu_module._scan_for_secret(run, "private-secret")


def test_preloaded_model_hash_mismatch_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkpoint = tmp_path / "model.ckpt"
    checkpoint.write_bytes(b"wrong")
    monkeypatch.setattr(zerogpu_module, "hf_hub_download", lambda **kwargs: str(checkpoint))
    with pytest.raises(RuntimeError, match="hash does not match"):
        zerogpu_module.resolve_preloaded_model()


def test_request_key_prefers_space_secret_and_validates_temporary_input() -> None:
    assert zerogpu_module._request_gemini_key("s" * 24, "t" * 24) == "s" * 24
    assert zerogpu_module._request_gemini_key(None, "t" * 24) == "t" * 24
    with pytest.raises(ValueError, match="temporary Gemini API key"):
        zerogpu_module._request_gemini_key(None, "short")


def test_temporary_key_file_is_owner_only_and_deleted() -> None:
    secret = "temporary_test_key_not_real"
    with zerogpu_module._temporary_gemini_file(secret) as key_file:
        assert key_file.read_text(encoding="utf-8") == secret
        assert key_file.stat().st_mode & 0o777 == 0o600
        parent = key_file.parent
    assert not parent.exists()


def test_every_terminal_ui_update_clears_the_temporary_key() -> None:
    updates = portfolio_ui_updates(
        _input_error_outputs("invalid request"),
        buttons_enabled=True,
    )
    assert updates[6]["value"] == ""
    running = portfolio_ui_updates(
        _input_error_outputs("running"),
        buttons_enabled=False,
        clear_api_key=False,
    )
    assert "value" not in running[6]


def test_canonical_space_config_requires_login_and_enables_temporary_key(
    tmp_path: Path,
) -> None:
    def authorize(profile: gr.OAuthProfile | None) -> None:
        del profile

    def authorize_csv(api_key: str, profile: gr.OAuthProfile | None) -> None:
        del api_key, profile

    def scenario_handler(*args):
        del args
        return ()

    def csv_handler(*args):
        del args
        return ()

    def header_handler(*args):
        del args
        return ()

    app = build_app(
        output_root=tmp_path,
        build_revision="12345678",
        deployment_mode="zerogpu_canonical",
        space_authorize_handler=authorize,
        space_csv_authorize_handler=authorize_csv,
        space_scenario_handler=scenario_handler,
        space_csv_handler=csv_handler,
        space_csv_header_handler=header_handler,
    )
    config = app.get_config_file()
    assert any(
        component.get("props", {}).get("value") == "Sign in with Hugging Face"
        for component in config["components"]
    )
    assert all(
        dependency.get("api_name") in {"js_fn", "_check_login_status"}
        or str(dependency.get("api_name", "")).startswith("false")
        for dependency in config["dependencies"]
    )
    serialized = json.dumps(config, ensure_ascii=False)
    assert "Frozen preset question · no live LLM call" in serialized
    key_components = [
        component
        for component in config["components"]
        if component.get("props", {}).get("label") == "Temporary Gemini API key"
    ]
    assert len(key_components) == 1
    assert key_components[0]["props"]["type"] == "password"
    assert key_components[0]["props"]["interactive"] is True
    assert "not intentionally persisted by DCFA" in serialized
    assert DEFAULT_CSV_QUESTION in serialized


def test_zerogpu_launch_configuration_includes_shared_theme_and_css() -> None:
    launch_kwargs = zerogpu_launch_kwargs()

    assert launch_kwargs["css"] == DEMO_CSS
    assert isinstance(launch_kwargs["theme"], gr.themes.Base)
    assert launch_kwargs["blocked_paths"] == [
        "/tmp/dcfa-zerogpu-runs",
        "/tmp/dcfa-zerogpu-secrets",
    ]
    assert launch_kwargs["enable_monitoring"] is False
    assert launch_kwargs["show_error"] is False


def test_duplicate_space_keeps_secret_mode_and_hides_browser_key(tmp_path: Path) -> None:
    app = build_app(
        output_root=tmp_path,
        build_revision="12345678",
        deployment_mode="zerogpu_duplicate",
        space_authorize_handler=lambda: None,
        space_csv_authorize_handler=lambda _key: None,
        space_scenario_handler=lambda *_args: (),
        space_csv_handler=lambda *_args: (),
        space_csv_header_handler=lambda *_args: (),
    )
    config = app.get_config_file()
    key_component = next(
        component
        for component in config["components"]
        if component.get("props", {}).get("label") == "Temporary Gemini API key"
    )
    assert key_component["props"]["visible"] is False
    assert "owner-provided" in json.dumps(config, ensure_ascii=False)
