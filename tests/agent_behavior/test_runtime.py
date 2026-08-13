from __future__ import annotations

from dataclasses import replace

from dcfa.agent.compiler import CompilationOutcome, CompilationRequest, SpecificationCompiler
from dcfa.agent.runtime import CausalAgentRuntime
from dcfa.agent.state import AgentState
from dcfa.errors import DCFAError, ErrorCode
from dcfa.schemas import AnalysisSpecification
from dcfa.tabcf_iv.development_dgp import DevelopmentIVDataset
from dcfa.tabcf_iv.pipeline import AnalysisRun, TabCFAnalysisEngine


def _request(
    dataset: DevelopmentIVDataset,
    specification: AnalysisSpecification,
    **changes,
) -> CompilationRequest:
    values = {
        "dataset_hash": dataset.manifest.dataset_hash,
        "outcome": "Y",
        "treatment": "X",
        "instrument": "Z",
        "objective": "mean",
        "intervention_grid": specification.intervention_grid,
        "x": specification.intervention_grid[2],
        "seed": specification.seed,
    }
    values.update(changes)
    return CompilationRequest(**values)


class NeverCalledTool:
    def __init__(self) -> None:
        self.calls = 0

    def analyze(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError("Tool must not be called.")

    def follow_up(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError("Tool must not be called.")


class StaticCompiler:
    def __init__(self, specification: AnalysisSpecification) -> None:
        self.specification = specification

    def compile(self, request: CompilationRequest) -> CompilationOutcome:
        del request
        return CompilationOutcome(self.specification, ())


class InjectingTool:
    def __init__(self, run: AnalysisRun, failures: tuple[DCFAError, ...]) -> None:
        self.run = run
        self.failures = list(failures)
        self.calls = 0

    def analyze(self, *args, **kwargs) -> AnalysisRun:
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return self.run

    def follow_up(self, specification: AnalysisSpecification, query_id: str):
        del specification
        return next(query for query in self.run.bundle.queries if query.query_id == query_id)


def test_compiler_requests_required_clarification_without_tool_call(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    tool = NeverCalledTool()
    request = _request(
        development_dataset,
        development_specification,
        objective="quantile",
        level=None,
    )
    response = CausalAgentRuntime(analysis_tool=tool).execute(
        request,
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.CLARIFICATION_REQUIRED
    assert response.tool_calls == 0
    assert any("quantile level" in question for question in response.clarification_questions)
    assert tool.calls == 0


def test_compiler_blocks_nonempty_w_without_tool_call(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    tool = NeverCalledTool()
    request = _request(
        development_dataset,
        development_specification,
        baseline_covariates=("W1",),
    )
    response = CausalAgentRuntime(analysis_tool=tool).execute(
        request,
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.BLOCKED
    assert response.error is not None
    assert response.error["code"] == ErrorCode.UNSUPPORTED_BASELINE_COVARIATES.value
    assert response.tool_calls == 0
    assert tool.calls == 0


def test_unconfirmed_specification_requires_approval_without_tool_call(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    tool = NeverCalledTool()
    request = _request(
        development_dataset,
        development_specification,
        confirmed_by_user=False,
    )
    response = CausalAgentRuntime(analysis_tool=tool).execute(
        request,
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.APPROVAL_REQUIRED
    assert response.status == "approval_required"
    assert response.tool_calls == 0
    assert response.clarification_questions
    assert tool.calls == 0


def test_one_recoverable_failure_retries_once_then_preserves_warnings(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
    completed_engine_run: tuple[TabCFAnalysisEngine, AnalysisRun],
) -> None:
    _, completed = completed_engine_run
    failure = DCFAError(
        ErrorCode.BACKEND_PREDICT_FAILED,
        "injected recoverable timeout",
        stage="tool",
        recoverable=True,
    )
    tool = InjectingTool(completed, (failure,))
    runtime = CausalAgentRuntime(
        analysis_tool=tool,
        compiler=StaticCompiler(development_specification),  # type: ignore[arg-type]
    )
    response = runtime.execute(
        _request(development_dataset, development_specification),
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.COMPLETED
    assert response.retry_count == 1
    assert response.tool_calls == 2
    assert response.warnings == completed.bundle.warnings
    assert response.queries == completed.bundle.queries
    assert AgentState.RETRYING in [event.state for event in response.state_events]


def test_second_recoverable_failure_stops_after_one_retry(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
    completed_engine_run: tuple[TabCFAnalysisEngine, AnalysisRun],
) -> None:
    _, completed = completed_engine_run
    failure = DCFAError(
        ErrorCode.BACKEND_PREDICT_FAILED,
        "injected recoverable timeout",
        stage="tool",
        recoverable=True,
    )
    tool = InjectingTool(completed, (failure, failure))
    response = CausalAgentRuntime(
        analysis_tool=tool,
        compiler=StaticCompiler(development_specification),  # type: ignore[arg-type]
    ).execute(
        _request(development_dataset, development_specification),
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.BLOCKED
    assert response.retry_count == 1
    assert response.tool_calls == 2
    assert response.error is not None
    assert response.error["code"] == ErrorCode.BACKEND_PREDICT_FAILED.value


def test_evidence_mismatch_blocks_final_answer(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
    completed_engine_run: tuple[TabCFAnalysisEngine, AnalysisRun],
) -> None:
    _, completed = completed_engine_run
    forged_query = replace(
        completed.bundle.queries[0],
        value_raw=completed.bundle.queries[0].value_raw + 1.0,
    )
    forged_bundle = replace(
        completed.bundle,
        queries=(forged_query, *completed.bundle.queries[1:]),
    )
    forged_run = replace(completed, bundle=forged_bundle)
    response = CausalAgentRuntime(
        analysis_tool=InjectingTool(forged_run, ()),
        compiler=StaticCompiler(development_specification),  # type: ignore[arg-type]
    ).execute(
        _request(development_dataset, development_specification),
        development_dataset.columns,
        development_dataset.manifest,
    )
    assert response.final_state is AgentState.BLOCKED
    assert response.error is not None
    assert response.error["code"] == ErrorCode.EVIDENCE_MISMATCH.value
    assert response.queries == ()


def test_cached_follow_up_uses_cache_and_stale_id_is_typed(
    development_specification: AnalysisSpecification,
    completed_engine_run: tuple[TabCFAnalysisEngine, AnalysisRun],
) -> None:
    engine, completed = completed_engine_run
    runtime = CausalAgentRuntime(analysis_tool=engine)
    valid = runtime.follow_up(development_specification, completed.bundle.queries[0].query_id)
    assert valid.status == "completed_from_cache"
    assert valid.final_state is AgentState.COMPLETED
    assert valid.queries == (completed.bundle.queries[0],)

    stale = runtime.follow_up(development_specification, "query_stale")
    assert stale.final_state is AgentState.BLOCKED
    assert stale.error is not None
    assert stale.error["code"] == ErrorCode.STALE_ID.value


def test_compiler_builds_immutable_supported_specification(
    development_dataset: DevelopmentIVDataset,
    development_specification: AnalysisSpecification,
) -> None:
    request = _request(
        development_dataset,
        development_specification,
        objective="risk_contrast",
        comparison_x=development_specification.intervention_grid[1],
        threshold=0.0,
        units="probability",
    )
    outcome = SpecificationCompiler().compile(request)
    assert not outcome.requires_clarification
    assert outcome.specification is not None
    assert outcome.specification.roles.baseline_covariates == ()
    assert outcome.specification.queries[0].kind == "risk_contrast"
    assert outcome.specification.risk_thresholds == (0.0,)
