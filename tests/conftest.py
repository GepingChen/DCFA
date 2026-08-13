from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from dcfa.constants import EstimatorBackend, EvidenceStatus, ExecutionProfile
from dcfa.schemas import AnalysisSpecification, CausalRoles, QuerySpecification
from dcfa.tabcf_iv.development_dgp import DevelopmentIVDataset, generate_development_iv
from dcfa.tabcf_iv.pipeline import AnalysisRun, TabCFAnalysisEngine


@pytest.fixture(scope="session")
def development_dataset() -> DevelopmentIVDataset:
    return generate_development_iv(n=180, seed=9917, instrument_strength=1.8)


@pytest.fixture(scope="session")
def development_specification(development_dataset: DevelopmentIVDataset) -> AnalysisSpecification:
    x_grid = tuple(
        float(value)
        for value in np.quantile(development_dataset.columns["X"], [0.1, 0.3, 0.5, 0.7, 0.9])
    )
    threshold = float(np.median(development_dataset.columns["Y"]))
    return AnalysisSpecification(
        dataset_hash=development_dataset.manifest.dataset_hash,
        roles=CausalRoles(outcome="Y", treatment="X", instrument="Z"),
        queries=(
            QuerySpecification("mean_mid", "mean", x=x_grid[2], units="Y_units"),
            QuerySpecification(
                "q50_contrast",
                "quantile_contrast",
                x=x_grid[3],
                comparison_x=x_grid[1],
                level=0.5,
                units="Y_units",
            ),
            QuerySpecification(
                "risk_mid",
                "risk",
                x=x_grid[2],
                threshold=threshold,
                units="probability",
            ),
        ),
        intervention_grid=x_grid,
        quantile_levels=(0.1, 0.5, 0.9),
        risk_thresholds=(threshold,),
        execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
        estimator_backend=EstimatorBackend.SKLEARN_QUANTILE_FALLBACK,
        evidence_status=EvidenceStatus.DEVELOPMENT_ONLY,
        seed=77,
    )


@pytest.fixture()
def specification_copy(development_specification: AnalysisSpecification) -> AnalysisSpecification:
    return replace(development_specification)


@pytest.fixture(scope="session")
def completed_engine_run(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> tuple[TabCFAnalysisEngine, AnalysisRun]:
    engine = TabCFAnalysisEngine()
    run = engine.analyze(
        development_dataset.columns,
        development_specification,
        development_dataset.manifest,
    )
    return engine, run
