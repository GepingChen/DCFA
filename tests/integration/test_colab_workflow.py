from __future__ import annotations

from pathlib import Path

import pytest

from dcfa.agent.gemini_live import GOOGLE_GENAI_VERSION
from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.managed_client import MANAGED_CLIENT_VERSION
from dcfa_colab.workflow import (
    preflight_colab_csv,
    run_colab_analysis,
    validate_colab_notebook,
)
from dcfa_website_demo.csv_upload import STANDARD_DEMO_SEED, export_standard_demo_csv
from tests.provider_fakes import FakeClientModule, FakeGeminiClient

GEMINI_TEST_KEY = "test_gemini_key_that_is_not_a_real_secret"
TABPFN_TEST_TOKEN = "tabpfn_sk_test_only_not_a_real_secret"


def test_colab_missing_secret_or_consent_fails_before_output(tmp_path: Path) -> None:
    csv_path = export_standard_demo_csv(tmp_path / "prepared.csv")
    preflight = preflight_colab_csv(
        csv_path,
        outcome="Y",
        treatment="X",
        instrument="Z",
    )
    assert preflight == {
        "status": "ready_for_explicit_transfer_confirmation",
        "row_count": 128,
        "roles": {"outcome": "Y", "treatment": "X", "instrument": "Z"},
        "column_count": 3,
    }
    common = {
        "csv_file": csv_path,
        "outcome": "Y",
        "treatment": "X",
        "instrument": "Z",
        "question": "Estimate the median contrast from low to high treatment.",
        "seed": STANDARD_DEMO_SEED,
        "output_root": tmp_path / "runs",
        "client_module": FakeClientModule(),
        "client_version": MANAGED_CLIENT_VERSION,
        "gemini_client": FakeGeminiClient(),
        "gemini_sdk_version": GOOGLE_GENAI_VERSION,
    }
    with pytest.raises(DCFAError) as missing:
        run_colab_analysis(
            **common,
            gemini_api_key="",
            tabpfn_token=TABPFN_TEST_TOKEN,
            consent_google_transfer=True,
            consent_prior_labs_transfer=True,
        )
    assert missing.value.code == ErrorCode.DATA_ACCESS_BLOCKED
    with pytest.raises(DCFAError) as consent:
        run_colab_analysis(
            **common,
            gemini_api_key=GEMINI_TEST_KEY,
            tabpfn_token=TABPFN_TEST_TOKEN,
            consent_google_transfer=False,
            consent_prior_labs_transfer=True,
        )
    assert consent.value.code == ErrorCode.DATA_ACCESS_BLOCKED
    assert not (tmp_path / "runs").exists()


def test_colab_happy_path_verifies_archives_and_excludes_secrets(tmp_path: Path) -> None:
    csv_path = export_standard_demo_csv(tmp_path / "prepared.csv")
    client = FakeClientModule()
    result = run_colab_analysis(
        csv_file=csv_path,
        outcome="Y",
        treatment="X",
        instrument="Z",
        question="Estimate the median contrast from low to high treatment.",
        seed=STANDARD_DEMO_SEED,
        gemini_api_key=GEMINI_TEST_KEY,
        tabpfn_token=TABPFN_TEST_TOKEN,
        consent_google_transfer=True,
        consent_prior_labs_transfer=True,
        output_root=tmp_path / "runs",
        client_module=client,
        client_version=MANAGED_CLIENT_VERSION,
        gemini_client=FakeGeminiClient(),
        gemini_sdk_version=GOOGLE_GENAI_VERSION,
    )
    assert result.status == "completed"
    assert result.visitor_result["status"] == "completed"
    assert result.verification is not None
    assert result.verification["status"] == "valid"
    assert result.run_directory is not None
    assert result.archive_path is not None and result.archive_path.is_file()
    assert client.reset_called
    artifact_bytes = b"".join(
        path.read_bytes() for path in result.run_directory.rglob("*") if path.is_file()
    )
    assert GEMINI_TEST_KEY.encode() not in artifact_bytes
    assert TABPFN_TEST_TOKEN.encode() not in artifact_bytes


def test_committed_colab_notebook_is_pinned_output_free_and_not_a_web_service() -> None:
    result = validate_colab_notebook(
        Path("notebooks/DCFA_Custom_Analysis_Colab.ipynb"),
        release_commit="0" * 40,
    )
    assert result["status"] == "valid"
    assert result["code_cell_count"] == 6
