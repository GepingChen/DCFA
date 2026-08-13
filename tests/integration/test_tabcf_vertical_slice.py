from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pytest

from dcfa.artifact_validation import verify_run_directory
from dcfa.canonical import file_sha256
from dcfa.constants import EstimatorBackend, EvidenceStatus, ExecutionProfile
from dcfa.errors import DCFAError, ErrorCode
from dcfa.evidence import validate_bundle_evidence, validate_track_t_release
from dcfa.schemas import AnalysisSpecification
from dcfa.tabcf_iv.development_dgp import DevelopmentIVDataset
from dcfa.tabcf_iv.pipeline import TabCFAnalysisEngine


def test_vertical_slice_outputs_are_coherent_evidence_linked_and_labeled(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    run = TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
        output_dir=tmp_path,
    )
    bundle = run.bundle
    assert run.backend_fit_calls == 3
    assert bundle.execution_profile is ExecutionProfile.LOCAL_DEVELOPMENT
    assert bundle.estimator_backend is EstimatorBackend.SKLEARN_QUANTILE_FALLBACK
    assert bundle.evidence_status is EvidenceStatus.DEVELOPMENT_ONLY
    cdf = np.asarray(bundle.interventional_cdf)
    assert np.all((cdf >= 0.0) & (cdf <= 1.0))
    assert np.all(np.diff(cdf, axis=1) >= 0.0)
    quantiles = np.asarray(bundle.interventional_quantiles)
    assert np.all(np.diff(quantiles, axis=1) >= 0.0)
    contrast = next(query for query in bundle.queries if query.query_id == "q50_contrast")
    assert np.isclose(contrast.value_raw, quantiles[3, 1] - quantiles[1, 1])
    assert all(query.evidence_id for query in bundle.queries)
    validate_bundle_evidence(bundle, run.ledger)
    artifact_names = {name for name, _ in run.artifact_paths}
    assert {
        "numerical_core",
        "specification",
        "dataset_manifest",
        "backend_manifest",
        "evidence",
        "result_bundle",
        "audit",
        "report",
        "plot",
        "report_manifest",
        "run_manifest",
    } <= artifact_names
    core = json.loads((tmp_path / "numerical_core.json").read_text())
    assert core["execution_profile"] == "local_development"
    assert core["estimator_backend"] == "sklearn_quantile_fallback"
    assert core["evidence_status"] == "development_only"
    report = (tmp_path / "report.md").read_text()
    assert "not a TabCF estimate" in report
    assert "do not prove" in report
    verification = verify_run_directory(tmp_path)
    assert verification["status"] == "valid"
    assert verification["evidence_count"] == len(bundle.queries)


def test_artifact_verifier_detects_tampering(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
        output_dir=tmp_path,
    )
    report_path = tmp_path / "report.md"
    report_path.write_text(report_path.read_text() + "tampered\n")
    with pytest.raises(DCFAError) as raised:
        verify_run_directory(tmp_path)
    assert raised.value.code is ErrorCode.HASH_MISMATCH


def test_artifact_verifier_recomputes_specification_and_numerical_core_ids(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
        output_dir=tmp_path,
    )

    def update_manifest_hash(artifact_name: str, artifact_path) -> None:
        manifest_path = tmp_path / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifact_hashes"] = [
            [name, file_sha256(artifact_path) if name == artifact_name else digest]
            for name, digest in manifest["artifact_hashes"]
        ]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    specification_path = tmp_path / "specification.json"
    original_specification = specification_path.read_text(encoding="utf-8")
    specification = json.loads(original_specification)
    specification["seed"] += 1
    specification_path.write_text(json.dumps(specification), encoding="utf-8")
    update_manifest_hash("specification", specification_path)
    with pytest.raises(DCFAError) as raised:
        verify_run_directory(tmp_path)
    assert raised.value.code is ErrorCode.HASH_MISMATCH

    specification_path.write_text(original_specification, encoding="utf-8")
    update_manifest_hash("specification", specification_path)
    assert verify_run_directory(tmp_path)["status"] == "valid"

    core_path = tmp_path / "numerical_core.json"
    numerical_core = json.loads(core_path.read_text(encoding="utf-8"))
    numerical_core["interventional_mean"][0] += 1.0
    core_path.write_text(json.dumps(numerical_core), encoding="utf-8")
    update_manifest_hash("numerical_core", core_path)
    with pytest.raises(DCFAError) as raised:
        verify_run_directory(tmp_path)
    assert raised.value.code is ErrorCode.HASH_MISMATCH


def test_artifact_verifier_recomputes_dataset_and_audit_bindings(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
        output_dir=tmp_path,
    )

    def update_manifest_hash(artifact_name: str, artifact_path) -> None:
        manifest_path = tmp_path / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifact_hashes"] = [
            [name, file_sha256(artifact_path) if name == artifact_name else digest]
            for name, digest in manifest["artifact_hashes"]
        ]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    dataset_path = tmp_path / "dataset_manifest.json"
    original_dataset = dataset_path.read_text(encoding="utf-8")
    dataset_manifest = json.loads(original_dataset)
    dataset_manifest["dataset_hash"] = "sha256:" + "0" * 64
    dataset_path.write_text(json.dumps(dataset_manifest), encoding="utf-8")
    update_manifest_hash("dataset_manifest", dataset_path)
    with pytest.raises(DCFAError) as raised:
        verify_run_directory(tmp_path)
    assert raised.value.code is ErrorCode.HASH_MISMATCH

    dataset_path.write_text(original_dataset, encoding="utf-8")
    update_manifest_hash("dataset_manifest", dataset_path)
    assert verify_run_directory(tmp_path)["status"] == "valid"

    audit_path = tmp_path / "audit.jsonl"
    audit_records = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    audit_records[0]["status"] = "tampered"
    audit_path.write_text(
        "\n".join(json.dumps(record) for record in audit_records) + "\n",
        encoding="utf-8",
    )
    update_manifest_hash("audit", audit_path)
    with pytest.raises(DCFAError) as raised:
        verify_run_directory(tmp_path)
    assert raised.value.code is ErrorCode.HASH_MISMATCH


def test_existing_result_directory_is_never_overwritten(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
        output_dir=tmp_path,
    )
    report_path = tmp_path / "report.md"
    original_hash = file_sha256(report_path)
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine().analyze(
            development_dataset.columns,
            specification_copy,
            development_dataset.manifest,
            output_dir=tmp_path,
        )
    assert raised.value.code is ErrorCode.OUTPUT_PATH_EXISTS
    assert file_sha256(report_path) == original_hash


def test_same_input_seed_produces_identical_bundle_and_values(
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    first = TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
    )
    second = TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
    )
    assert first.bundle.result_bundle_id == second.bundle.result_bundle_id
    assert first.bundle.interventional_cdf == second.bundle.interventional_cdf
    assert first.bundle.queries == second.bundle.queries


def test_cached_follow_up_and_second_analysis_do_not_refit(
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    created = []

    def factory(specification: AnalysisSpecification):
        from dcfa.tabcf_iv.backend import SklearnQuantileBackend

        backend = SklearnQuantileBackend(seed=specification.seed)
        created.append(backend)
        return backend

    engine = TabCFAnalysisEngine(backend_factory=factory)
    first = engine.analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
    )
    query = engine.follow_up(specification_copy, "mean_mid")
    second = engine.analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
    )
    assert query == first.bundle.queries[0]
    assert len(created) == 1
    assert created[0].fit_calls == 3
    assert second.bundle.cached
    assert second.backend_fit_calls == 0


def test_release_validator_rejects_development_fallback(
    development_dataset: DevelopmentIVDataset,
    specification_copy: AnalysisSpecification,
) -> None:
    run = TabCFAnalysisEngine().analyze(
        development_dataset.columns,
        specification_copy,
        development_dataset.manifest,
    )
    with pytest.raises(DCFAError) as raised:
        validate_track_t_release(run.bundle, run.ledger)
    assert raised.value.code is ErrorCode.RELEASE_GATE_FAILED


def test_outside_support_blocks_before_stage2_and_produces_no_artifacts(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    outside = float(np.max(development_dataset.columns["X"]) + 10.0)
    grid = (*development_specification.intervention_grid[:-1], outside)
    bad_query = replace(development_specification.queries[0], x=outside)
    spec = replace(development_specification, intervention_grid=grid, queries=(bad_query,))
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine().analyze(
            development_dataset.columns,
            spec,
            development_dataset.manifest,
            output_dir=tmp_path,
        )
    assert raised.value.code is ErrorCode.OUTSIDE_SUPPORT
    assert list(tmp_path.iterdir()) == []


def test_strict_support_blocks_unqueried_grid_points_before_stage2(
    tmp_path,
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    from dcfa.tabcf_iv.backend import SklearnQuantileBackend

    created: list[SklearnQuantileBackend] = []

    def factory(specification: AnalysisSpecification) -> SklearnQuantileBackend:
        backend = SklearnQuantileBackend(seed=specification.seed)
        created.append(backend)
        return backend

    outside = float(np.max(development_dataset.columns["X"]) + 10.0)
    specification = replace(
        development_specification,
        intervention_grid=(*development_specification.intervention_grid, outside),
    )
    with pytest.raises(DCFAError) as raised:
        TabCFAnalysisEngine(backend_factory=factory).analyze(
            development_dataset.columns,
            specification,
            development_dataset.manifest,
            output_dir=tmp_path,
        )
    assert raised.value.code is ErrorCode.OUTSIDE_SUPPORT
    assert len(created) == 1
    assert created[0].fit_calls == 1
    assert not list(tmp_path.iterdir())
