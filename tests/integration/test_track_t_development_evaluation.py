from __future__ import annotations

import json

import pytest

from dcfa.artifact_validation import verify_run_directory
from dcfa.canonical import file_sha256
from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.development_evaluation import run_development_evaluation


def test_development_oracle_evaluation_is_evidence_linked_and_not_tabcf(tmp_path) -> None:
    run = run_development_evaluation(seeds=(61,), rows=120, output_dir=tmp_path)
    assert run.bundle.data_label == "fallback_engineering_benchmark_not_tabcf"
    assert run.bundle.evidence_status.value == "development_only"
    assert run.bundle.estimator_backend.value == "sklearn_quantile_fallback"
    assert len(run.replications) == 2
    assert len(run.bundle.values) == 10
    assert len(run.ledger.records()) == 10
    assert all(estimate.evidence_id for estimate in run.bundle.values)
    assert verify_run_directory(tmp_path)["status"] == "valid"

    bundle_path = tmp_path / "result_bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["values"][0]["standard_error"] += 1.0
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_hashes"] = [
        [name, file_sha256(bundle_path) if name == "result_bundle" else digest]
        for name, digest in manifest["artifact_hashes"]
    ]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(DCFAError) as exc_info:
        verify_run_directory(tmp_path)
    assert exc_info.value.code is ErrorCode.EVIDENCE_MISMATCH
