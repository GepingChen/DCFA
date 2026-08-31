"""Native Hugging Face ZeroGPU entrypoint for local TabPFN v2 execution."""

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import gradio as gr
import spaces
from huggingface_hub import hf_hub_download

from dcfa.artifact_validation import verify_run_directory
from dcfa.canonical import file_sha256
from dcfa.errors import DCFAError
from dcfa.tabcf_iv.local_tabpfn import (
    LOCAL_TABPFN_V2_MODEL_FILENAME,
    LOCAL_TABPFN_V2_MODEL_HASH,
    LOCAL_TABPFN_V2_MODEL_REPO,
    LOCAL_TABPFN_V2_MODEL_REVISION,
)
from dcfa_website_demo.app import (
    _execution_error_outputs,
    _input_error_outputs,
    _log_operator_error,
    build_app,
    execute_local_csv_upload,
    execute_local_portfolio_scenario,
    format_portfolio_result,
    portfolio_ui_updates,
)
from dcfa_website_demo.csv_upload import inspect_csv_header

DEFAULT_ZEROGPU_OUTPUT_ROOT = Path("/tmp/dcfa-zerogpu-runs")
DEFAULT_GRADIO_TEMP_ROOT = Path("/tmp/gradio")
DEFAULT_SECRET_ROOT = Path("/tmp/dcfa-zerogpu-secrets")


def resolve_preloaded_model() -> Path:
    """Resolve and hash-check the build-preloaded TabPFN v2 checkpoint."""
    try:
        resolved = Path(
            hf_hub_download(
                repo_id=LOCAL_TABPFN_V2_MODEL_REPO,
                filename=LOCAL_TABPFN_V2_MODEL_FILENAME,
                revision=LOCAL_TABPFN_V2_MODEL_REVISION,
                local_files_only=True,
            )
        ).resolve(strict=True)
    except Exception as exc:
        raise RuntimeError("The frozen TabPFN v2 checkpoint was not preloaded.") from exc
    if file_sha256(resolved) != LOCAL_TABPFN_V2_MODEL_HASH:
        raise RuntimeError("The preloaded TabPFN v2 checkpoint hash does not match.")
    return resolved


def _gemini_secret() -> str | None:
    value = os.environ.get("DCFA_GEMINI_API_KEY")
    if value is None:
        return None
    if len(value) < 20 or any(character.isspace() for character in value):
        raise RuntimeError("DCFA_GEMINI_API_KEY is malformed.")
    return value


@contextmanager
def _temporary_gemini_file(secret: str) -> Iterator[Path]:
    secret_parent = Path(os.environ.get("DCFA_SECRET_ROOT", str(DEFAULT_SECRET_ROOT)))
    secret_parent.mkdir(parents=True, exist_ok=True)
    secret_parent.chmod(0o700)
    with tempfile.TemporaryDirectory(
        prefix="request-",
        dir=secret_parent,
    ) as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        path = root / "gemini_api_key"
        path.write_text(secret, encoding="utf-8")
        path.chmod(0o600)
        yield path


def _require_login(profile: gr.OAuthProfile | None) -> None:
    if profile is None:
        raise gr.Error("Sign in with Hugging Face before running this workflow.")


def _scan_for_secret(root: Path, secret: str | None) -> None:
    if secret is None:
        return
    encoded = secret.encode("utf-8")
    for path in root.rglob("*"):
        if path.is_file() and encoded in path.read_bytes():
            raise RuntimeError("A Gemini credential reached the run artifact.")


def _archive_run(root: Path) -> Path:
    archive_root = Path(os.environ.get("GRADIO_TEMP_DIR", str(DEFAULT_GRADIO_TEMP_ROOT)))
    archive_root.mkdir(parents=True, exist_ok=True)
    archive = archive_root / f"{root.name}-{uuid.uuid4().hex[:8]}.zip"
    with zipfile.ZipFile(archive, mode="x", compression=zipfile.ZIP_DEFLATED) as stream:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                stream.write(path, arcname=path.relative_to(root.parent))
    with zipfile.ZipFile(archive) as stream:
        names = stream.namelist()
    if not names or any(name.startswith("/") or ".." in Path(name).parts for name in names):
        archive.unlink(missing_ok=True)
        raise RuntimeError("The verified run archive failed its path-safety check.")
    return archive


def _public_plot_copy(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    target_root = Path(os.environ.get("GRADIO_TEMP_DIR", str(DEFAULT_GRADIO_TEMP_ROOT)))
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / f"dcfa-result-{uuid.uuid4().hex}.png"
    shutil.copy2(path, target)
    return str(target)


def _verified_projection(result: Any, secret: str | None) -> tuple[Any, ...]:
    archive: Path | None = None
    public_plot: str | None = None
    try:
        formatted = format_portfolio_result(result)
        if result.response.status == "completed" and result.output_dir is not None:
            verification = verify_run_directory(result.output_dir)
            if verification.get("status") != "valid":
                raise RuntimeError("The result did not pass independent artifact verification.")
            _scan_for_secret(result.output_dir, secret)
            public_plot = _public_plot_copy(result.plot_path)
            archive = _archive_run(result.output_dir)
            formatted = (*formatted[:4], public_plot)
        return portfolio_ui_updates(
            formatted,
            buttons_enabled=True,
            archive_path=str(archive) if archive is not None else None,
        )
    finally:
        if result.output_dir is not None and result.output_dir.is_dir():
            shutil.rmtree(result.output_dir)


def _safe_unlink_upload(path: str | None) -> None:
    if not path:
        return
    candidate = Path(path).resolve()
    temp_root = Path(os.environ.get("GRADIO_TEMP_DIR", str(DEFAULT_GRADIO_TEMP_ROOT))).resolve()
    if candidate.is_relative_to(temp_root):
        candidate.unlink(missing_ok=True)


def build_zerogpu_app(*, build_revision: str) -> Any:
    """Build the authenticated canonical or duplicated ZeroGPU application."""
    model_path = resolve_preloaded_model()
    secret = _gemini_secret()
    deployment_mode = "zerogpu_duplicate" if secret is not None else "zerogpu_canonical"
    output_root = Path(
        os.environ.get("DCFA_OUTPUT_ROOT", str(DEFAULT_ZEROGPU_OUTPUT_ROOT))
    ).resolve()

    def authorize(profile: gr.OAuthProfile | None) -> None:
        _require_login(profile)

    def inspect_header(
        csv_path: str | None,
        profile: gr.OAuthProfile | None,
    ) -> tuple[Any, Any, Any]:
        _require_login(profile)
        if not csv_path:
            raise gr.Error("Choose a CSV file before selecting roles.")
        try:
            columns = list(inspect_csv_header(csv_path))
        except ValueError as exc:
            raise gr.Error(str(exc)) from exc
        return (
            gr.Dropdown(choices=columns, value=None),
            gr.Dropdown(choices=columns, value=None),
            gr.Dropdown(choices=columns, value=None),
        )

    @spaces.GPU(duration=120)
    def run_scenario(
        scenario: str,
        question: str,
        rows: int,
        seed: int,
        profile: gr.OAuthProfile | None,
    ) -> tuple[Any, ...]:
        _require_login(profile)
        try:
            if secret is None:
                result = execute_local_portfolio_scenario(
                    scenario,
                    rows,
                    seed,
                    question=question,
                    model_path=model_path,
                    output_root=output_root,
                )
            else:
                with _temporary_gemini_file(secret) as secret_file:
                    result = execute_local_portfolio_scenario(
                        scenario,
                        rows,
                        seed,
                        question=question,
                        model_path=model_path,
                        output_root=output_root,
                        gemini_api_key_file=secret_file,
                    )
            return _verified_projection(result, secret)
        except DCFAError as exc:
            _log_operator_error(exc)
            return portfolio_ui_updates(_execution_error_outputs(exc), buttons_enabled=True)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            return portfolio_ui_updates(_input_error_outputs(str(exc)), buttons_enabled=True)

    @spaces.GPU(duration=120)
    def run_csv(
        csv_path: str | None,
        outcome: str,
        treatment: str,
        instrument: str,
        confirmed: bool,
        question: str,
        seed: int,
        profile: gr.OAuthProfile | None,
    ) -> tuple[Any, ...]:
        _require_login(profile)
        try:
            if secret is None:
                raise ValueError("Duplicate this Space and add DCFA_GEMINI_API_KEY first.")
            if not csv_path:
                raise ValueError("Choose a CSV file before running the workflow.")
            with _temporary_gemini_file(secret) as secret_file:
                result = execute_local_csv_upload(
                    csv_path,
                    outcome,
                    treatment,
                    instrument,
                    confirmed,
                    seed,
                    model_path=model_path,
                    question=question,
                    output_root=output_root,
                    gemini_api_key_file=secret_file,
                )
            return _verified_projection(result, secret)
        except DCFAError as exc:
            _log_operator_error(exc)
            return portfolio_ui_updates(_execution_error_outputs(exc), buttons_enabled=True)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            return portfolio_ui_updates(_input_error_outputs(str(exc)), buttons_enabled=True)
        finally:
            _safe_unlink_upload(csv_path)

    return build_app(
        output_root=output_root,
        build_revision=build_revision,
        deployment_mode=deployment_mode,
        space_authorize_handler=authorize,
        space_scenario_handler=run_scenario,
        space_csv_handler=run_csv if secret is not None else None,
        space_csv_header_handler=inspect_header if secret is not None else None,
    )
