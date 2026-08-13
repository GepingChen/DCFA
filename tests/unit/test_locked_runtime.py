from __future__ import annotations

import json
from pathlib import Path

import pytest

from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.locked_runtime import load_locked_runtime_manifest


def test_runtime_template_fails_closed_while_placeholders_remain() -> None:
    with pytest.raises(DCFAError) as exc_info:
        load_locked_runtime_manifest(Path("evaluation/configs/tabpfn_locked_runtime.example.json"))
    assert exc_info.value.code is ErrorCode.INVALID_SPECIFICATION


def test_runtime_manifest_rejects_wrong_upstream_commit(tmp_path) -> None:
    payload = {
        "model_artifact_hash": "sha256:" + "1" * 64,
        "model_path": "model.ckpt",
        "package_versions": {
            "numpy": "1.0",
            "scikit-learn": "1.0",
            "scipy": "1.0",
            "tabpfn": "1.0",
            "torch": "1.0",
        },
        "protocol_version": "tabpfn_locked_runtime_v1",
        "python_version": "3.11.13",
        "runtime_image_digest": "sha256:" + "2" * 64,
        "source_checkout": "source",
        "upstream_source_commit": "wrong",
    }
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(DCFAError) as exc_info:
        load_locked_runtime_manifest(path)
    assert exc_info.value.code is ErrorCode.HASH_MISMATCH


def test_runtime_manifest_rejects_malformed_digest(tmp_path) -> None:
    payload = {
        "model_artifact_hash": "sha256:short",
        "model_path": "model.ckpt",
        "package_versions": {
            "numpy": "1.0",
            "scikit-learn": "1.0",
            "scipy": "1.0",
            "tabpfn": "1.0",
            "torch": "1.0",
        },
        "protocol_version": "tabpfn_locked_runtime_v1",
        "python_version": "3.11.13",
        "runtime_image_digest": "sha256:" + "2" * 64,
        "source_checkout": "source",
        "upstream_source_commit": "76e0d3eb9e97cebca381d1540db0333c1ef1016e",
    }
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(DCFAError) as exc_info:
        load_locked_runtime_manifest(path)
    assert exc_info.value.code is ErrorCode.INVALID_SPECIFICATION
