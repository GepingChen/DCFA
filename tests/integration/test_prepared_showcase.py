from __future__ import annotations

import json
from pathlib import Path

import pytest

from dcfa.agent.gemini_live import GOOGLE_GENAI_VERSION
from dcfa.tabcf_iv.managed_client import MANAGED_CLIENT_VERSION
from dcfa_showcase.prepared import (
    CSV_FILENAME,
    MANIFEST_FILENAME,
    PLOT_FILENAME,
    PREPARED_PROMPT,
    PROMPT_FILENAME,
    SUMMARY_FILENAME,
    VISITOR_FILENAME,
    export_prepared_showcase,
    freeze_prepared_demo,
    verify_prepared_showcase,
)
from dcfa_website_demo.app import execute_portfolio_scenario
from dcfa_website_demo.csv_upload import STANDARD_DEMO_ROWS, STANDARD_DEMO_SEED
from tests.provider_fakes import FakeClientModule, FakeGeminiClient


def _credentials(root: Path) -> tuple[Path, Path]:
    tabpfn = root / "tabpfn-token"
    tabpfn.write_text("tabpfn_sk_test_only_not_a_real_secret", encoding="utf-8")
    tabpfn.chmod(0o600)
    gemini = root / "gemini-key"
    gemini.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    gemini.chmod(0o600)
    return tabpfn, gemini


def test_prepared_showcase_freeze_export_verify_and_tamper_gate(tmp_path: Path) -> None:
    showcase = tmp_path / "prepared_demo_v1"
    freeze_prepared_demo(showcase, release_commit="a" * 40)
    assert (showcase / PROMPT_FILENAME).read_text(encoding="utf-8") == f"{PREPARED_PROMPT}\n"
    assert (showcase / CSV_FILENAME).read_text(encoding="utf-8").count("\n") == 129
    manifest = json.loads((showcase / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert manifest["input"]["row_count"] == 128
    assert manifest["gemini_profile"]["request_limit"] == 1
    assert manifest["managed_tabpfn_profile"]["fallback"] is None

    tabpfn, gemini = _credentials(tmp_path)
    source_result = execute_portfolio_scenario(
        "strong_iv",
        STANDARD_DEMO_ROWS,
        STANDARD_DEMO_SEED,
        question=PREPARED_PROMPT,
        output_root=tmp_path / "full-runs",
        token_file=tabpfn,
        client_module=FakeClientModule(),
        client_version=MANAGED_CLIENT_VERSION,
        gemini_api_key_file=gemini,
        gemini_client=FakeGeminiClient(),
        gemini_sdk_version=GOOGLE_GENAI_VERSION,
    )
    assert source_result.output_dir is not None
    exported = export_prepared_showcase(
        showcase,
        source_run_directory=source_result.output_dir,
    )
    assert exported["status"] == "valid"
    assert (showcase / VISITOR_FILENAME).is_file()
    assert (showcase / PLOT_FILENAME).is_file()
    assert (showcase / SUMMARY_FILENAME).is_file()
    visitor_text = (showcase / VISITOR_FILENAME).read_text(encoding="utf-8")
    assert "No API call is made" in visitor_text
    assert "evidence_" not in visitor_text
    assert "bundle_" not in visitor_text
    assert "/Users/" not in visitor_text

    visitor = json.loads(visitor_text)
    visitor["result"]["value_raw"] += 1.0
    (showcase / VISITOR_FILENAME).write_text(
        json.dumps(visitor, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="rounding|hash mismatch"):
        verify_prepared_showcase(showcase)


def test_prepared_showcase_refuses_overwrite(tmp_path: Path) -> None:
    showcase = tmp_path / "prepared_demo_v1"
    freeze_prepared_demo(showcase, release_commit="b" * 40)
    with pytest.raises(FileExistsError, match="overwrite"):
        freeze_prepared_demo(showcase, release_commit="b" * 40)
