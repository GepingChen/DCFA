from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from dcfa.agent.gemini_live import (
    GOOGLE_GENAI_VERSION,
    run_gemini_live_smoke,
    verify_gemini_live_smoke,
)
from dcfa.errors import DCFAError, ErrorCode


def test_gemini_sdk_is_not_imported_by_the_core_module() -> None:
    assert "google.genai" not in sys.modules


@dataclass
class FakeUsage:
    total_input_tokens: int = 120
    total_output_tokens: int = 48
    total_thought_tokens: int = 32
    total_tokens: int = 200


@dataclass
class FakeInteraction:
    output_text: str
    status: str = "completed"
    id: str = "interaction_test_123"
    model: str = "gemini-3.6-flash"
    usage: FakeUsage = field(default_factory=FakeUsage)


class FakeInteractions:
    def __init__(self, output_text: str, *, raises: bool = False) -> None:
        self.output_text = output_text
        self.raises = raises
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> FakeInteraction:
        self.calls.append(kwargs)
        if self.raises:
            raise RuntimeError("synthetic API failure")
        return FakeInteraction(self.output_text)


class FakeClient:
    def __init__(self, output_text: str, *, raises: bool = False) -> None:
        self.interactions = FakeInteractions(output_text, raises=raises)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def _api_key_file(tmp_path: Path, *, mode: int = 0o600) -> Path:
    path = tmp_path / "gemini-key"
    path.write_text("test_gemini_key_that_is_not_a_real_secret", encoding="utf-8")
    path.chmod(mode)
    return path


def _valid_proposal() -> str:
    return json.dumps(
        {
            "comparison_x_label": "low",
            "decision": "analyze",
            "instrument": "Z",
            "level_label": "median",
            "objective": "quantile_contrast",
            "outcome": "Y",
            "treatment": "X",
            "treatment_type": "continuous",
            "x_label": "high",
        }
    )


def test_one_live_compile_call_precedes_evidence_validated_analysis(tmp_path: Path) -> None:
    client = FakeClient(_valid_proposal())
    output_dir = tmp_path / "gemini-live"
    result = run_gemini_live_smoke(
        api_key_file=_api_key_file(tmp_path),
        output_dir=output_dir,
        client=client,
        sdk_version=GOOGLE_GENAI_VERSION,
    )

    assert len(client.interactions.calls) == 1
    call = client.interactions.calls[0]
    assert call["model"] == "gemini-3.6-flash"
    assert call["store"] is False
    assert "response_mime_type" not in call
    assert call["response_format"]["mime_type"] == "application/json"
    assert call["generation_config"]["max_output_tokens"] == 256
    assert "test_gemini_key" not in json.dumps(call)
    assert client.closed
    assert result.response.status == "completed"
    assert result.response.tool_calls == 1
    assert len(result.response.queries) == 1
    assert result.response.queries[0].evidence_id
    assert result.usage.total_tokens == 200
    assert result.list_price_estimate_usd == "0.00078000"

    trace_text = result.trace_path.read_text(encoding="utf-8")
    assert "test_gemini_key" not in trace_text
    trace = json.loads(trace_text)
    assert trace["model_request_count"] == 1
    assert trace["data_rows_sent_to_gemini"] == 0
    assert trace["deterministic_analysis"]["queries"][0]["evidence_id"]
    assert verify_gemini_live_smoke(output_dir)["status"] == "valid"


def test_api_failure_is_not_retried_or_persisted(tmp_path: Path) -> None:
    client = FakeClient(_valid_proposal(), raises=True)
    output_dir = tmp_path / "gemini-failed"
    with pytest.raises(DCFAError) as raised:
        run_gemini_live_smoke(
            api_key_file=_api_key_file(tmp_path),
            output_dir=output_dir,
            client=client,
            sdk_version=GOOGLE_GENAI_VERSION,
        )
    assert raised.value.code == ErrorCode.LLM_API_FAILED
    assert raised.value.context["request_count"] == 1
    assert len(client.interactions.calls) == 1
    assert not output_dir.exists()


def test_invalid_proposal_fails_before_deterministic_tool(tmp_path: Path) -> None:
    proposal = json.loads(_valid_proposal())
    proposal["treatment_type"] = "binary"
    output_dir = tmp_path / "gemini-invalid"
    with pytest.raises(DCFAError) as raised:
        run_gemini_live_smoke(
            api_key_file=_api_key_file(tmp_path),
            output_dir=output_dir,
            client=FakeClient(json.dumps(proposal)),
            sdk_version=GOOGLE_GENAI_VERSION,
        )
    assert raised.value.code == ErrorCode.LLM_OUTPUT_INVALID
    assert raised.value.stage == "gemini.output_validation"
    assert not output_dir.exists()


def test_key_file_permissions_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(DCFAError) as raised:
        run_gemini_live_smoke(
            api_key_file=_api_key_file(tmp_path, mode=0o644),
            output_dir=tmp_path / "gemini-permissions",
            client=FakeClient(_valid_proposal()),
            sdk_version=GOOGLE_GENAI_VERSION,
        )
    assert raised.value.code == ErrorCode.DATA_ACCESS_BLOCKED
    assert raised.value.stage == "gemini.credentials"


def test_manifest_bytes_are_frozen(tmp_path: Path) -> None:
    manifest = json.loads(Path("evaluation/configs/gemini_live_smoke_v1.json").read_text())
    manifest["generation_config"]["max_output_tokens"] = 512
    manifest_path = tmp_path / "changed-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(DCFAError) as raised:
        run_gemini_live_smoke(
            api_key_file=_api_key_file(tmp_path),
            output_dir=tmp_path / "gemini-manifest",
            manifest_path=manifest_path,
            client=FakeClient(_valid_proposal()),
            sdk_version=GOOGLE_GENAI_VERSION,
        )
    assert raised.value.code == ErrorCode.LLM_OUTPUT_INVALID
    assert raised.value.stage == "gemini.manifest"


def test_verifier_rejects_trace_query_tampering(tmp_path: Path) -> None:
    output_dir = tmp_path / "gemini-tamper"
    result = run_gemini_live_smoke(
        api_key_file=_api_key_file(tmp_path),
        output_dir=output_dir,
        client=FakeClient(_valid_proposal()),
        sdk_version=GOOGLE_GENAI_VERSION,
    )
    trace = json.loads(result.trace_path.read_text(encoding="utf-8"))
    trace["deterministic_analysis"]["queries"][0]["value_raw"] = 999.0
    result.trace_path.write_text(json.dumps(trace), encoding="utf-8")
    with pytest.raises(DCFAError):
        verify_gemini_live_smoke(output_dir)
