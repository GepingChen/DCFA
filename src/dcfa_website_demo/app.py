"""Website-oriented Gradio demo for the auditable TabCF Analyst workflow."""

from __future__ import annotations

import html
import importlib.metadata
import logging
import os
import re
import subprocess
import threading
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from dcfa.agent.compiler import CompilationRequest
from dcfa.agent.runtime import AgentResponse, CausalAgentRuntime
from dcfa.constants import EstimatorBackend, EvidenceStatus, ExecutionProfile
from dcfa.errors import DCFAError, ErrorCode
from dcfa.schemas import AnalysisSpecification, DatasetManifest
from dcfa.tabcf_iv.development_dgp import generate_development_iv
from dcfa.tabcf_iv.managed_client import (
    MANAGED_BACKEND_PARAMETERS,
    MANAGED_CLIENT_VERSION,
    TabPFNClientBackend,
)
from dcfa.tabcf_iv.managed_smoke import (
    load_managed_client_module,
    read_managed_token_file,
)
from dcfa.tabcf_iv.pipeline import AnalysisRun, TabCFAnalysisEngine
from dcfa_website_demo.csv_upload import (
    MAX_UPLOAD_ROWS,
    MIN_UPLOAD_ROWS,
    load_authorized_csv,
)
from dcfa_website_demo.gemini import (
    GEMINI_MODEL,
    compile_website_question,
    write_compilation_trace,
)
from dcfa_website_demo.presentation import (
    answer_sentence,
    present_error,
    present_query,
    render_visitor_plot,
)

DEFAULT_OUTPUT_ROOT = Path("artifacts/local/website-demo")
DEFAULT_MANAGED_TOKEN_FILE = Path.home() / ".config" / "dcfa" / "tabpfn_api_key"
DEFAULT_GEMINI_API_KEY_FILE = Path.home() / ".config" / "dcfa" / "gemini_api_key"
MIN_DEMO_ROWS = 120
MAX_DEMO_ROWS = 256
MIN_DEMO_SEED = 0
MAX_DEMO_SEED = 2**32 - 1
_OUTPUT_RESERVATION_LOCK = threading.Lock()
_BUILD_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,12}$")
_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DemoScenario:
    label: str
    description: str
    question: str
    instrument_strength: float
    intervention_quantiles: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)
    violate_support: bool = False


@dataclass(frozen=True)
class PortfolioDemoResult:
    scenario: str
    response: AgentResponse
    plot_path: Path | None
    output_dir: Path | None
    llm_trace: dict[str, Any]


SCENARIOS: dict[str, DemoScenario] = {
    "strong_iv": DemoScenario(
        label="Supported workflow",
        description="A strong first stage reaches an evidence-linked answer.",
        question=(
            "How does the median outcome change between a low and a high supported "
            "treatment intervention?"
        ),
        instrument_strength=1.6,
    ),
    "weak_iv": DemoScenario(
        label="Weak-IV warning",
        description="The workflow completes while preserving empirical warnings.",
        question=(
            "Estimate the same median contrast, and keep any weak-instrument or support "
            "warnings attached to the answer."
        ),
        instrument_strength=0.02,
        intervention_quantiles=(0.3, 0.4, 0.5, 0.6, 0.7),
    ),
    "support_violation": DemoScenario(
        label="Outside-support block",
        description="An unsupported intervention stops before Stage 2 and returns no number.",
        question=("Estimate the median contrast at an intervention beyond the observed support."),
        instrument_strength=1.6,
        violate_support=True,
    ),
}


DEMO_CSS = """
:root {
  --demo-paper: #fffdf8;
  --demo-surface: #ffffff;
  --demo-muted-surface: #f5f1e9;
  --demo-ink: #242320;
  --demo-muted: #68645e;
  --demo-accent: #35685c;
  --demo-accent-deep: #254f47;
  --demo-line: #ddd7ce;
  --demo-warning: #9a5d17;
  --demo-danger: #9b3f35;
}

body,
.gradio-container {
  background: var(--demo-paper) !important;
  color: var(--demo-ink) !important;
}

.gradio-container {
  width: 100% !important;
  max-width: 74rem !important;
  min-width: 0 !important;
  margin-inline: auto !important;
  padding: clamp(1rem, 3vw, 2.5rem) !important;
  box-sizing: border-box !important;
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif !important;
}

.gradio-container > .main {
  width: 100% !important;
  min-width: 0 !important;
  box-sizing: border-box !important;
}

.demo-hero {
  padding: clamp(1rem, 3vw, 2rem) 0 1.25rem;
  border-bottom: 1px solid var(--demo-line);
}

.demo-eyebrow {
  margin: 0 0 .7rem;
  color: var(--demo-accent-deep);
  font-size: .76rem;
  font-weight: 750;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.demo-hero h1 {
  max-width: 21ch;
  margin: 0 0 .75rem;
  color: var(--demo-ink);
  font-size: clamp(2rem, 5vw, 3.6rem);
  line-height: 1.02;
  letter-spacing: -.045em;
}

.demo-hero-copy {
  max-width: 47rem;
  margin: 0 0 1rem;
  color: var(--demo-muted);
  font-family: Charter, Georgia, serif;
  font-size: clamp(1.02rem, 2vw, 1.18rem);
  line-height: 1.65;
}

.demo-hero-actions {
  display: flex;
  align-items: center;
  margin: 1rem 0;
  gap: .75rem;
}

.demo-primary-link {
  display: inline-flex;
  min-height: 2.8rem;
  align-items: center;
  padding: 0 1rem;
  border-radius: .3rem;
  background: var(--demo-accent-deep);
  color: white !important;
  font-size: .9rem;
  font-weight: 750;
  text-decoration: none !important;
}

.demo-privacy-summary,
.demo-transfer-note {
  max-width: 47rem;
  margin: .75rem 0 0;
  padding: .75rem .9rem;
  border-left: .25rem solid var(--demo-warning);
  background: #fff5e6;
  color: var(--demo-ink);
  font-size: .84rem;
  line-height: 1.55;
}

.demo-privacy-summary summary {
  cursor: pointer;
  font-weight: 700;
}

.demo-privacy-summary p,
.demo-transfer-note p {
  margin: .45rem 0 0;
}

.demo-badges {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
}

.demo-badges span {
  padding: .35rem .65rem;
  border: 1px solid var(--demo-line);
  border-radius: 999px;
  background: var(--demo-surface);
  color: var(--demo-muted);
  font-size: .76rem;
  font-weight: 650;
}

.demo-section-heading {
  margin: 0 0 .35rem !important;
  font-size: 1.15rem !important;
  letter-spacing: -.01em;
}

.demo-section-copy {
  margin-bottom: 1rem !important;
  color: var(--demo-muted) !important;
  font-size: .92rem !important;
}

.demo-panel {
  padding: clamp(1rem, 2.5vw, 1.4rem) !important;
  border: 1px solid var(--demo-line) !important;
  border-radius: .65rem !important;
  background: var(--demo-surface) !important;
  box-shadow: none !important;
}

.demo-controls {
  margin-top: 1.4rem;
}

#run-demo-button,
#run-csv-button {
  min-height: 3rem;
  border: 1px solid var(--demo-accent-deep) !important;
  border-radius: .3rem !important;
  background: var(--demo-accent-deep) !important;
  color: white !important;
  font-weight: 750 !important;
}

#run-demo-button:hover,
#run-csv-button:hover {
  background: var(--demo-accent) !important;
}

.demo-status {
  padding: .9rem 1rem;
  border-left: .28rem solid var(--demo-accent);
  border-radius: .25rem;
  background: #edf4f1;
  color: var(--demo-ink);
  line-height: 1.55;
}

.demo-status strong {
  display: block;
  margin-bottom: .15rem;
}

.demo-status--warning {
  border-left-color: var(--demo-warning);
  background: #fff5e6;
}

.demo-status--blocked {
  border-left-color: var(--demo-danger);
  background: #fff0ee;
}

.demo-status--idle {
  border-left-color: var(--demo-line);
  background: var(--demo-muted-surface);
}

.state-graph {
  display: grid;
  margin: 0;
  padding: 0;
  gap: .55rem;
  list-style: none;
}

.state-graph li {
  position: relative;
  padding: .7rem .8rem .7rem 2.2rem;
  border: 1px solid var(--demo-line);
  border-radius: .35rem;
  background: var(--demo-surface);
  color: var(--demo-muted);
  font-size: .82rem;
  font-weight: 650;
}

.state-graph li::before {
  position: absolute;
  top: 50%;
  left: .8rem;
  width: .65rem;
  height: .65rem;
  border-radius: 50%;
  background: var(--demo-line);
  content: "";
  transform: translateY(-50%);
}

.state-graph li.completed {
  color: var(--demo-ink);
}

.state-graph li.completed::before {
  background: var(--demo-accent);
}

.state-graph li.current {
  border-color: var(--demo-accent);
  background: #edf4f1;
  color: var(--demo-ink);
}

.state-graph li.current::before {
  background: var(--demo-accent);
  box-shadow: 0 0 0 .22rem #d7e6e1;
}

.state-graph li.pending {
  color: var(--demo-muted);
}

.state-graph li.blocked::before {
  background: var(--demo-danger);
}

.state-reason {
  display: block;
  margin-top: .14rem;
  color: var(--demo-muted);
  font-size: .72rem;
  font-weight: 450;
}

.demo-answer {
  margin-top: .65rem;
}

.demo-answer h3 {
  margin-bottom: .55rem !important;
  color: var(--demo-muted) !important;
  font-size: .78rem !important;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.demo-answer p {
  max-width: 52rem;
  margin-bottom: 0 !important;
  font-family: Charter, Georgia, serif;
  font-size: clamp(1.35rem, 3vw, 2rem);
  line-height: 1.35;
}

.demo-answer code {
  overflow-wrap: anywhere;
  white-space: normal;
}

.demo-warning-list {
  margin: .55rem 0 0;
  padding-left: 1.15rem;
}

.demo-warning-list li + li {
  margin-top: .35rem;
}

.demo-evidence-card {
  height: 100%;
}

.demo-result-details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .8rem;
}

.demo-result-detail {
  padding: .9rem;
  border: 1px solid var(--demo-line);
  border-radius: .35rem;
  background: var(--demo-surface);
}

.demo-result-detail h3 {
  margin: 0 0 .45rem;
  font-size: .78rem;
  letter-spacing: .05em;
  text-transform: uppercase;
}

.demo-result-detail p {
  margin: .4rem 0 0;
  color: var(--demo-muted);
  font-size: .84rem;
  line-height: 1.5;
}

.demo-result-detail--development {
  border-left: .25rem solid var(--demo-warning);
  background: #fff5e6;
}

.demo-evidence-card h3 {
  margin: 0 0 .85rem;
  font-size: 1rem;
}

.demo-evidence-placeholder {
  color: var(--demo-muted);
  font-family: Charter, Georgia, serif;
}

.demo-boundary {
  margin-top: 1.5rem;
  padding-top: 1.4rem;
  border-top: 1px solid var(--demo-line);
}

.demo-boundary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: .75rem;
}

.demo-boundary-item {
  padding: .85rem;
  border: 1px solid var(--demo-line);
  border-radius: .35rem;
  background: var(--demo-surface);
}

.demo-boundary-item strong {
  display: block;
  margin-bottom: .25rem;
  font-size: .8rem;
}

.demo-boundary-item span {
  color: var(--demo-muted);
  font-family: Charter, Georgia, serif;
  font-size: .82rem;
  line-height: 1.45;
}

@media (max-width: 48rem) {
  .gradio-container {
    padding: .8rem !important;
  }

  .demo-boundary-grid {
    grid-template-columns: 1fr 1fr;
  }

  .demo-result-details {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 30rem) {
  .demo-hero {
    padding-top: .45rem;
  }

  .demo-hero-copy {
    line-height: 1.45;
  }

  .demo-boundary-grid {
    grid-template-columns: 1fr;
  }
}
"""


class _WebsiteAnalysisTool:
    """Presentation-only adapter that preserves the runtime's tool contract."""

    def __init__(self, output_dir: Path, engine: TabCFAnalysisEngine) -> None:
        self.output_dir = output_dir
        self.engine = engine
        self.last_run: AnalysisRun | None = None

    def analyze(
        self,
        data: dict[str, np.ndarray],
        specification: AnalysisSpecification,
        dataset_manifest: DatasetManifest,
        *,
        output_dir: Any = None,
    ) -> AnalysisRun:
        del output_dir
        self.last_run = self.engine.analyze(
            data,
            specification,
            dataset_manifest,
            output_dir=self.output_dir,
        )
        return self.last_run

    def follow_up(self, specification: AnalysisSpecification, query_id: str):
        return self.engine.follow_up(specification, query_id)


def scenario_question(scenario: str) -> str:
    """Return the visible example question for a frozen portfolio scenario."""
    try:
        return SCENARIOS[scenario].question
    except KeyError as exc:
        raise ValueError(f"Unknown demo scenario: {scenario}") from exc


def managed_token_file_from_environment() -> Path:
    """Resolve the repository-external managed-client credential file."""
    return Path(os.environ.get("DCFA_TABPFN_TOKEN_FILE", str(DEFAULT_MANAGED_TOKEN_FILE)))


def gemini_api_key_file_from_environment() -> Path:
    """Resolve the repository-external Gemini credential file."""
    return Path(os.environ.get("DCFA_GEMINI_API_KEY_FILE", str(DEFAULT_GEMINI_API_KEY_FILE)))


def _reserve_output_directory(root: Path, scenario: str, seed: int) -> Path:
    """Atomically reserve a fresh immutable run directory for a UI request."""
    run_root = root / scenario / f"seed-{seed}"
    with _OUTPUT_RESERVATION_LOCK:
        run_root.mkdir(parents=True, exist_ok=True)
        run_index = 1
        while True:
            output_dir = run_root / f"run-{run_index:04d}"
            try:
                output_dir.mkdir()
            except FileExistsError:
                run_index += 1
                continue
            return output_dir


def _remove_empty_reservation(output_dir: Path) -> None:
    """Remove only the empty leaf reserved by this request after a blocked run."""
    try:
        output_dir.rmdir()
    except OSError:
        return


def execute_portfolio_scenario(
    scenario: str,
    rows: int,
    seed: int,
    *,
    question: str | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    token_file: Path | None = None,
    client_module: Any | None = None,
    client_version: str | None = None,
    gemini_api_key_file: Path | None = None,
    gemini_client: Any | None = None,
    gemini_sdk_version: str | None = None,
) -> PortfolioDemoResult:
    """Execute one frozen guided scenario through managed TabPFN and the typed runtime."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown demo scenario: {scenario}")
    rows = int(rows)
    seed = int(seed)
    if not MIN_DEMO_ROWS <= rows <= MAX_DEMO_ROWS:
        raise ValueError(f"Demo rows must be between {MIN_DEMO_ROWS} and {MAX_DEMO_ROWS}.")
    if not MIN_DEMO_SEED <= seed <= MAX_DEMO_SEED:
        raise ValueError(f"Demo seed must be between {MIN_DEMO_SEED} and {MAX_DEMO_SEED}.")

    selected = SCENARIOS[scenario]
    dataset = generate_development_iv(
        n=rows,
        seed=seed,
        instrument_strength=selected.instrument_strength,
    )
    manifest = replace(dataset.manifest, estimator_backend=EstimatorBackend.TABPFN)
    interventions = tuple(
        float(value) for value in np.quantile(dataset.columns["X"], selected.intervention_quantiles)
    )
    if selected.violate_support:
        interventions = (
            *interventions[:-1],
            float(np.max(dataset.columns["X"]) + 5.0),
        )
    return _execute_managed_dataset(
        result_scenario=scenario,
        output_scenario=scenario,
        columns=dataset.columns,
        manifest=manifest,
        outcome="Y",
        treatment="X",
        instrument="Z",
        question=question or selected.question,
        interventions=interventions,
        seed=seed,
        output_root=output_root,
        token_file=token_file,
        client_module=client_module,
        client_version=client_version,
        gemini_api_key_file=gemini_api_key_file,
        gemini_client=gemini_client,
        gemini_sdk_version=gemini_sdk_version,
    )


def execute_csv_upload(
    csv_file: str | Path,
    outcome: str,
    treatment: str,
    instrument: str,
    confirmed: bool,
    seed: int,
    *,
    question: str | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    token_file: Path | None = None,
    client_module: Any | None = None,
    client_version: str | None = None,
    gemini_api_key_file: Path | None = None,
    gemini_client: Any | None = None,
    gemini_sdk_version: str | None = None,
) -> PortfolioDemoResult:
    """Execute a confirmed, strictly bounded local Y/X/Z CSV through managed TabPFN."""
    seed = int(seed)
    if not MIN_DEMO_SEED <= seed <= MAX_DEMO_SEED:
        raise ValueError(f"Demo seed must be between {MIN_DEMO_SEED} and {MAX_DEMO_SEED}.")
    dataset = load_authorized_csv(
        csv_file,
        outcome=outcome,
        treatment=treatment,
        instrument=instrument,
        confirmed=bool(confirmed),
    )
    interventions = tuple(
        float(value)
        for value in np.quantile(dataset.columns[dataset.treatment], (0.1, 0.3, 0.5, 0.7, 0.9))
    )
    digest_suffix = dataset.manifest.dataset_hash.split(":", maxsplit=1)[1][:12]
    return _execute_managed_dataset(
        result_scenario="csv_upload",
        output_scenario=f"csv-upload-{digest_suffix}",
        columns=dataset.columns,
        manifest=dataset.manifest,
        outcome=dataset.outcome,
        treatment=dataset.treatment,
        instrument=dataset.instrument,
        question=(
            question
            or "Estimate the median outcome contrast at high treatment versus low treatment."
        ),
        interventions=interventions,
        seed=seed,
        output_root=output_root,
        token_file=token_file,
        client_module=client_module,
        client_version=client_version,
        gemini_api_key_file=gemini_api_key_file,
        gemini_client=gemini_client,
        gemini_sdk_version=gemini_sdk_version,
    )


def _execute_managed_dataset(
    *,
    result_scenario: str,
    output_scenario: str,
    columns: dict[str, np.ndarray],
    manifest: DatasetManifest,
    outcome: str,
    treatment: str,
    instrument: str,
    question: str,
    interventions: tuple[float, ...],
    seed: int,
    output_root: Path,
    token_file: Path | None,
    client_module: Any | None,
    client_version: str | None,
    gemini_api_key_file: Path | None,
    gemini_client: Any | None,
    gemini_sdk_version: str | None,
) -> PortfolioDemoResult:
    """Run one already-validated no-W dataset through the shared managed profile."""
    credential = read_managed_token_file(token_file or managed_token_file_from_environment())
    client = client_module or load_managed_client_module()
    observed_client_version = client_version or importlib.metadata.version("tabpfn-client")
    if observed_client_version != MANAGED_CLIENT_VERSION:
        raise DCFAError(
            ErrorCode.UNSUPPORTED_BACKEND_PROFILE,
            "The installed tabpfn-client version does not match the frozen website profile.",
            stage="managed_client.version",
            context={
                "expected": MANAGED_CLIENT_VERSION,
                "observed": observed_client_version,
            },
        )

    try:
        llm_compilation = compile_website_question(
            question,
            api_key_file=gemini_api_key_file or gemini_api_key_file_from_environment(),
            client=gemini_client,
            sdk_version=gemini_sdk_version,
        )
        label_values = {
            "low": interventions[0],
            "center": interventions[len(interventions) // 2],
            "high": interventions[-1],
        }
        client.set_access_token(credential)
        del credential
        request = CompilationRequest(
            dataset_hash=manifest.dataset_hash,
            outcome=outcome,
            treatment=treatment,
            instrument=instrument,
            objective=llm_compilation.objective,
            intervention_grid=interventions,
            x=label_values[llm_compilation.x_label],
            comparison_x=(
                None
                if llm_compilation.comparison_x_label is None
                else label_values[llm_compilation.comparison_x_label]
            ),
            level=llm_compilation.level,
            units=f"{outcome}_units",
            confirmed_by_user=True,
            execution_profile=ExecutionProfile.LOCAL_DEVELOPMENT,
            estimator_backend=EstimatorBackend.TABPFN,
            evidence_status=EvidenceStatus.DEVELOPMENT_ONLY,
            backend_parameters=MANAGED_BACKEND_PARAMETERS,
            seed=seed,
        )

        def backend_factory(specification: AnalysisSpecification) -> TabPFNClientBackend:
            return TabPFNClientBackend.from_specification(
                specification,
                regressor_class=client.TabPFNRegressor,
                client_version=observed_client_version,
            )

        output_dir = _reserve_output_directory(Path(output_root), output_scenario, seed)
        engine = TabCFAnalysisEngine(backend_factory=backend_factory)
        tool = _WebsiteAnalysisTool(output_dir, engine)
        response = CausalAgentRuntime(analysis_tool=tool).execute(
            request,
            columns,
            manifest,
        )
        visitor_plot_path = output_dir / "website_interventional_summary.png"
        if response.status == "completed":
            if tool.last_run is None:
                raise DCFAError(
                    ErrorCode.EVIDENCE_MISMATCH,
                    "The completed website run has no validated result bundle.",
                    stage="website.presentation",
                )
            if response.queries and present_query(response.queries[0]).allow_numeric:
                render_visitor_plot(tool.last_run.bundle, tool.last_run.ledger, visitor_plot_path)
    except Exception:
        if "output_dir" in locals():
            _remove_empty_reservation(output_dir)
        raise
    finally:
        client.reset()
    if not any(output_dir.iterdir()):
        _remove_empty_reservation(output_dir)
    elif response.status == "completed":
        write_compilation_trace(output_dir, llm_compilation.trace)
    return PortfolioDemoResult(
        scenario=result_scenario,
        response=response,
        plot_path=visitor_plot_path if visitor_plot_path.is_file() else None,
        output_dir=output_dir if output_dir.is_dir() else None,
        llm_trace=llm_compilation.trace,
    )


def _status_html(result: PortfolioDemoResult) -> str:
    response = result.response
    if response.status == "blocked":
        presentation = present_error((response.error or {}).get("code"))
        return (
            '<div class="demo-status demo-status--blocked" role="status" aria-live="polite">'
            f"<strong>{html.escape(presentation.title)}</strong>"
            "No numerical result was returned.</div>"
        )
    if not response.queries or not present_query(response.queries[0]).allow_numeric:
        presentation = present_error(ErrorCode.EVIDENCE_MISMATCH)
        return (
            '<div class="demo-status demo-status--blocked" role="status" aria-live="polite">'
            f"<strong>{html.escape(presentation.title)}</strong>"
            "No numerical result is displayed.</div>"
        )
    presented = present_query(response.queries[0])
    if any(item.severity == "caution" for item in presented.warnings):
        return (
            '<div class="demo-status demo-status--warning" role="status" aria-live="polite">'
            "<strong>Completed with important limitations</strong>"
            "The result passed evidence validation; review the warnings below.</div>"
        )
    return (
        '<div class="demo-status" role="status" aria-live="polite">'
        "<strong>Result verified</strong>"
        "The displayed value comes from the validated result bundle.</div>"
    )


_VISITOR_STAGES = (
    "Understand the question",
    "Check the data",
    "Run the analysis",
    "Verify the result",
)


def _progress_html(
    states: tuple[str, str, str, str],
    *,
    blocked_stage: int | None = None,
    blocked_title: str = "",
    blocked_action: str = "",
) -> str:
    rendered: list[str] = []
    for index, (label, state) in enumerate(zip(_VISITOR_STAGES, states, strict=True)):
        detail = ""
        if index == blocked_stage:
            detail = (
                f'<span class="state-reason">{html.escape(blocked_title)}. '
                f"{html.escape(blocked_action)}</span>"
            )
        rendered.append(f'<li class="{state}"><span>{html.escape(label)}</span>{detail}</li>')
    return '<ol class="state-graph" aria-label="Analysis progress">' + "".join(rendered) + "</ol>"


def _error_stage_index(code: str | ErrorCode | None) -> int:
    try:
        error_code = code if isinstance(code, ErrorCode) else ErrorCode(str(code))
    except ValueError:
        return 3
    if error_code in {
        ErrorCode.LLM_IMPORT_FAILED,
        ErrorCode.LLM_API_FAILED,
        ErrorCode.LLM_OUTPUT_INVALID,
    }:
        return 0
    if error_code in {
        ErrorCode.INVALID_SPECIFICATION,
        ErrorCode.MISSING_CAUSAL_ROLE,
        ErrorCode.ROLE_CONFLICT,
        ErrorCode.UNSUPPORTED_BASELINE_COVARIATES,
        ErrorCode.UNSUPPORTED_TREATMENT,
        ErrorCode.INVALID_DATA,
        ErrorCode.OUTSIDE_SUPPORT,
        ErrorCode.DATA_ACCESS_BLOCKED,
        ErrorCode.CONSTRAINT_VIOLATION,
        ErrorCode.OUTPUT_PATH_EXISTS,
    }:
        return 1
    if error_code in {
        ErrorCode.UNSUPPORTED_BACKEND_PROFILE,
        ErrorCode.BACKEND_IMPORT_FAILED,
        ErrorCode.BACKEND_LOAD_FAILED,
        ErrorCode.BACKEND_FIT_FAILED,
        ErrorCode.BACKEND_PREDICT_FAILED,
    }:
        return 2
    return 3


def _blocked_progress_html(code: str | ErrorCode | None) -> str:
    stage_index = _error_stage_index(code)
    presentation = present_error(code)
    states = tuple(
        "completed" if index < stage_index else "blocked" if index == stage_index else "pending"
        for index in range(len(_VISITOR_STAGES))
    )
    return _progress_html(
        states,
        blocked_stage=stage_index,
        blocked_title=presentation.title,
        blocked_action=presentation.action,
    )


def _running_outputs() -> tuple[str, str, str, str, None]:
    """Return one stable waiting state without implying completed work or a percentage."""
    return (
        '<div class="demo-status" role="status" aria-live="polite">'
        "<strong>Analysis in progress</strong>Understanding the question before any result "
        "is shown."
        "</div>",
        _progress_html(("current", "pending", "pending", "pending")),
        "",
        "",
        None,
    )


def _state_graph_html(response: AgentResponse, llm_trace: dict[str, Any]) -> str:
    del llm_trace
    visitor_result_allowed = (
        response.status == "completed"
        and bool(response.queries)
        and present_query(response.queries[0]).allow_numeric
    )
    if visitor_result_allowed:
        return _progress_html(("completed", "completed", "completed", "completed"))
    return _blocked_progress_html((response.error or {}).get("code"))


def _answer_markdown(response: AgentResponse, llm_trace: dict[str, Any]) -> str:
    if not response.queries:
        presentation = present_error((response.error or {}).get("code"))
        return (
            "### No numerical answer\n\n"
            f"**{presentation.title}.** {presentation.explanation} {presentation.action}"
        )
    presented = present_query(response.queries[0])
    if not presented.allow_numeric:
        return (
            "### No numerical answer\n\n"
            "**Result verification failed.** Do not use a numerical result; inspect the run "
            "with the local verifier."
        )
    return f"### Answer\n\n**{answer_sentence(response.queries[0], llm_trace.get('proposal'))}**"


def _evidence_card_html(response: AgentResponse) -> str:
    if not response.queries:
        return (
            '<div class="demo-evidence-card demo-evidence-placeholder">'
            "<h3>What to do next</h3>"
            "Use the action in the answer above; no evidence record or chart was created."
            "</div>"
        )
    presented = present_query(response.queries[0])
    if not presented.allow_numeric:
        return (
            '<div class="demo-evidence-card demo-evidence-placeholder">'
            "<h3>Result details</h3>"
            "This result requires local artifact review and is not available for visitor display."
            "</div>"
        )
    support_html = (
        '<section class="demo-result-detail"><h3>Data support</h3>'
        f"<strong>{html.escape(presented.support.title)}</strong>"
        f"<p>{html.escape(presented.support.explanation)} "
        f"{html.escape(presented.support.action)}</p></section>"
    )
    visible_warnings = tuple(
        warning for warning in presented.warnings if warning.title != "Development result"
    )
    if visible_warnings:
        warning_items = "".join(
            "<li>"
            f"<strong>{html.escape(warning.title)}</strong><br>"
            f"{html.escape(warning.explanation)} {html.escape(warning.action)}"
            "</li>"
            for warning in visible_warnings
        )
        warning_html = (
            '<section class="demo-result-detail demo-evidence-warnings">'
            "<h3>Important warnings</h3>"
            f'<ul class="demo-warning-list">{warning_items}</ul></section>'
        )
    else:
        warning_html = (
            '<section class="demo-result-detail"><h3>Important warnings</h3>'
            "<p>No additional empirical warning was triggered.</p></section>"
        )
    development_html = (
        '<section class="demo-result-detail demo-result-detail--development">'
        "<h3>Development-only</h3>"
        "<p>This managed-service result is for local demonstration, not published or "
        "production causal evidence.</p></section>"
    )
    return (
        '<div class="demo-evidence-card demo-result-details">'
        f"{support_html}{warning_html}{development_html}</div>"
    )


def _input_error_outputs(message: str) -> tuple[str, str, str, str, None]:
    del message
    presentation = present_error(ErrorCode.INVALID_DATA)
    return (
        '<div class="demo-status demo-status--blocked" role="status" aria-live="polite">'
        f"<strong>{html.escape(presentation.title)}</strong>No workflow was run.</div>",
        _blocked_progress_html(ErrorCode.INVALID_DATA),
        f"### No numerical answer\n\n**{presentation.title}.** {presentation.explanation}",
        '<div class="demo-evidence-card demo-evidence-placeholder">'
        f"<h3>What to do next</h3>{html.escape(presentation.action)}</div>",
        None,
    )


def _execution_error_outputs(error: DCFAError) -> tuple[str, str, str, str, None]:
    presentation = present_error(error.code)
    return (
        '<div class="demo-status demo-status--blocked" role="status" aria-live="polite">'
        f"<strong>{html.escape(presentation.title)}</strong>"
        "No numerical result was returned.</div>",
        _blocked_progress_html(error.code),
        f"### No numerical answer\n\n**{presentation.title}.** {presentation.explanation}",
        '<div class="demo-evidence-card demo-evidence-placeholder">'
        f"<h3>What to do next</h3>{html.escape(presentation.action)} "
        "The workflow did not use a fallback model.</div>",
        None,
    )


def _log_operator_error(error: DCFAError) -> None:
    """Keep the typed failure diagnosable without sending its context to the browser."""
    _LOGGER.warning(
        "Website demo run stopped with code=%s at stage=%s",
        error.code.value,
        error.stage,
    )


def format_portfolio_result(
    result: PortfolioDemoResult,
) -> tuple[str, str, str, str, str | None]:
    """Project a runtime response into display-only values without recomputing numbers."""
    if result.response.error:
        _LOGGER.warning(
            "Website demo workflow blocked with code=%s at stage=%s",
            result.response.error.get("code", "unknown"),
            result.response.error.get("stage", "unknown"),
        )
    presented = present_query(result.response.queries[0]) if result.response.queries else None
    return (
        _status_html(result),
        _state_graph_html(result.response, result.llm_trace),
        _answer_markdown(result.response, result.llm_trace),
        _evidence_card_html(result.response),
        (
            str(result.plot_path)
            if result.plot_path is not None and presented is not None and presented.allow_numeric
            else None
        ),
    )


def resolve_build_revision() -> str:
    """Return a short local build identity without exposing a health payload."""
    configured = os.environ.get("DCFA_BUILD_REVISION", "").strip().lower()
    if _BUILD_REVISION_PATTERN.fullmatch(configured):
        return configured
    if configured == "unknown":
        return configured
    repository_root = Path(__file__).resolve().parents[2]
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=repository_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unknown"
    revision = completed.stdout.strip().lower()
    return (
        revision
        if completed.returncode == 0 and _BUILD_REVISION_PATTERN.fullmatch(revision)
        else "unknown"
    )


def build_app(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    build_revision: str | None = None,
) -> Any:
    """Build the optional website demo while keeping Gradio a lazy dependency."""
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            "Install the website demo with: python -m pip install -r requirements-website-demo.lock"
        ) from exc

    scenario_choices = [(item.label, key) for key, item in SCENARIOS.items()]
    visible_revision = html.escape(build_revision or resolve_build_revision())
    with gr.Blocks(
        title="DCFA — auditable causal agent demo",
        analytics_enabled=False,
        fill_width=True,
    ) as app:
        gr.HTML(
            f"""
            <header class="demo-hero">
              <p class="demo-eyebrow">DCFA · Local demo · Build {visible_revision}</p>
              <h1>Ask how outcomes change under treatment.</h1>
              <p class="demo-hero-copy">
                Turn one bounded continuous-treatment question into an evidence-checked answer,
                with unsupported claims stopped before a number is shown.
              </p>
              <div class="demo-badges" aria-label="Supported scope">
                <span>Continuous Y / X / Z only</span><span>Development-only</span>
              </div>
              <div class="demo-hero-actions">
                <a class="demo-primary-link" href="#guided-input">Try a guided example</a>
              </div>
              <details class="demo-privacy-summary" role="note">
                <summary>Question text goes to Google Gemini; approved CSV rows go
                separately to Prior Labs.</summary>
                <p>Built-in examples are synthetic. Gemini receives no data rows or actual
                intervention values. A CSV leaves this machine only after explicit confirmation.
                This local result is development-only and cannot create an automatic real-world
                causal claim.</p>
              </details>
            </header>
            """
        )
        with gr.Row(elem_classes="demo-controls", elem_id="guided-input"):
            with gr.Column(scale=5, elem_classes="demo-panel"):
                gr.Markdown("### 1 · Choose an input", elem_classes="demo-section-heading")
                with gr.Tabs():
                    with gr.Tab("Guided scenarios"):
                        gr.Markdown(
                            "Frozen synthetic engineering paths for a quick walkthrough.",
                            elem_classes="demo-section-copy",
                        )
                        scenario = gr.Radio(
                            choices=scenario_choices,
                            value="strong_iv",
                            label="Guided path",
                        )
                        question = gr.Textbox(
                            value=scenario_question("strong_iv"),
                            label=f"Natural-language question · compiled by {GEMINI_MODEL}",
                            info=(
                                "Ask for a mean or median summary/contrast at low, center, or "
                                "high treatment. Gemini receives the question, not data rows."
                            ),
                            lines=3,
                            interactive=True,
                        )
                        gr.HTML(
                            '<div class="demo-transfer-note" role="note">'
                            "<strong>Before you run:</strong> Your question text will be sent to "
                            "Google Gemini. Do not enter private "
                            "or sensitive information. Gemini receives no data rows or actual "
                            "treatment values.</div>"
                        )
                        with gr.Accordion("Reproducibility controls", open=False):
                            rows = gr.Slider(
                                MIN_DEMO_ROWS,
                                MAX_DEMO_ROWS,
                                value=128,
                                step=8,
                                label="Synthetic rows",
                            )
                            seed = gr.Number(
                                value=20260810,
                                precision=0,
                                minimum=MIN_DEMO_SEED,
                                maximum=MAX_DEMO_SEED,
                                label="Seed",
                            )
                        run_button = gr.Button(
                            "Run the guided workflow",
                            variant="primary",
                            elem_id="run-demo-button",
                        )
                    with gr.Tab("Upload local CSV"):
                        gr.Markdown(
                            f"Upload exactly three numeric columns and {MIN_UPLOAD_ROWS}–"
                            f"{MAX_UPLOAD_ROWS} rows. Extra columns are rejected rather than "
                            "silently treated as W. The file stays local until you confirm and "
                            "run.",
                            elem_classes="demo-section-copy",
                        )
                        csv_file = gr.File(
                            label="Local Y/X/Z CSV",
                            file_types=[".csv"],
                            type="filepath",
                        )
                        with gr.Row():
                            csv_outcome = gr.Textbox(value="Y", label="Outcome Y column")
                            csv_treatment = gr.Textbox(value="X", label="Treatment X column")
                            csv_instrument = gr.Textbox(value="Z", label="Instrument Z column")
                        csv_seed = gr.Number(
                            value=20260813,
                            precision=0,
                            minimum=MIN_DEMO_SEED,
                            maximum=MAX_DEMO_SEED,
                            label="Analysis seed",
                        )
                        csv_question = gr.Textbox(
                            value=(
                                "Estimate the median outcome contrast at high treatment versus "
                                "low treatment."
                            ),
                            label=f"Natural-language question · compiled by {GEMINI_MODEL}",
                            info=(
                                "Use Y, X, and Z as conceptual roles. Gemini receives this text, "
                                "not the selected CSV rows or actual intervention values."
                            ),
                            lines=3,
                        )
                        csv_confirmed = gr.Checkbox(
                            value=False,
                            label="I am authorized to use this data and approve both transfers.",
                        )
                        gr.HTML(
                            '<div class="demo-transfer-note" role="note">'
                            "<strong>Two separate transfers:</strong> the question text goes to "
                            "Google Gemini with no CSV rows; the selected "
                            "Y/X/Z rows go to Prior Labs for managed TabPFN inference. Do not use "
                            "private or sensitive data in this local demo.</div>"
                        )
                        csv_run_button = gr.Button(
                            "Run uploaded CSV",
                            variant="primary",
                            elem_id="run-csv-button",
                        )
            with gr.Column(scale=5, elem_classes="demo-panel"):
                gr.Markdown(
                    "### 2 · Follow the workflow",
                    elem_classes="demo-section-heading",
                )
                gr.Markdown(
                    "A result is shown only after typed scope, support, and evidence gates.",
                    elem_classes="demo-section-copy",
                )
                state_graph = gr.HTML(
                    '<div class="demo-status demo-status--idle">'
                    "<strong>Ready</strong>Choose a path and run the frozen workflow.</div>"
                )

        gr.Markdown("## 3 · Review the answer", elem_classes="demo-section-heading")
        answer = gr.Markdown("", visible=False, elem_classes="demo-panel demo-answer")
        status = gr.HTML("", visible=False)
        evidence = gr.HTML("", visible=False)
        plot = gr.Image(
            type="filepath",
            label="Estimated outcome distributions and summaries",
            visible=False,
        )
        gr.HTML(
            """
            <section class="demo-boundary" aria-labelledby="boundary-title">
              <p class="demo-eyebrow" id="boundary-title">Scope and limitations</p>
              <div class="demo-boundary-grid">
                <div class="demo-boundary-item"><strong>Not a general router</strong>
                  <span>Only the continuous-treatment IV contract is public.</span></div>
                <div class="demo-boundary-item"><strong>No silent W drop</strong>
                  <span>Non-empty baseline covariates are rejected before fitting.</span></div>
                <div class="demo-boundary-item"><strong>Hillstrom stays separate</strong>
                  <span>The randomized-policy track is not TabCF validation.</span></div>
                <div class="demo-boundary-item"><strong>Managed TabPFN</strong>
                  <span>Service-traceable TabCF mechanics, not locked release evidence.</span></div>
              </div>
            </section>
            """
        )

        scenario.change(
            fn=scenario_question,
            inputs=scenario,
            outputs=question,
            queue=False,
        )

        def ui_updates(
            formatted: tuple[str, str, str, str, str | None],
            *,
            buttons_enabled: bool,
        ) -> tuple[Any, ...]:
            status_value, state_value, answer_value, evidence_value, plot_value = formatted
            return (
                gr.update(value=answer_value, visible=bool(answer_value)),
                gr.update(value=status_value, visible=bool(status_value)),
                gr.update(value=state_value),
                gr.update(value=evidence_value, visible=bool(evidence_value)),
                gr.update(value=plot_value, visible=plot_value is not None),
                gr.update(interactive=buttons_enabled),
                gr.update(interactive=buttons_enabled),
            )

        def handle_run(
            selected_scenario: str,
            selected_question: str,
            selected_rows: int,
            selected_seed: int,
        ):
            yield ui_updates(_running_outputs(), buttons_enabled=False)
            try:
                formatted = format_portfolio_result(
                    execute_portfolio_scenario(
                        selected_scenario,
                        selected_rows,
                        selected_seed,
                        question=selected_question,
                        output_root=output_root,
                    )
                )
            except DCFAError as exc:
                _log_operator_error(exc)
                formatted = _execution_error_outputs(exc)
            except (TypeError, ValueError) as exc:
                formatted = _input_error_outputs(str(exc))
            yield ui_updates(formatted, buttons_enabled=True)

        run_button.click(
            fn=handle_run,
            inputs=(scenario, question, rows, seed),
            outputs=(
                answer,
                status,
                state_graph,
                evidence,
                plot,
                run_button,
                csv_run_button,
            ),
            scroll_to_output=True,
            show_progress="hidden",
            trigger_mode="once",
        )

        def handle_csv_run(
            selected_file: str | None,
            selected_outcome: str,
            selected_treatment: str,
            selected_instrument: str,
            selected_confirmation: bool,
            selected_question: str,
            selected_seed: int,
        ):
            yield ui_updates(_running_outputs(), buttons_enabled=False)
            try:
                if not selected_file:
                    raise ValueError("Choose a local CSV file before running the workflow.")
                formatted = format_portfolio_result(
                    execute_csv_upload(
                        selected_file,
                        selected_outcome,
                        selected_treatment,
                        selected_instrument,
                        selected_confirmation,
                        selected_seed,
                        question=selected_question,
                        output_root=output_root,
                    )
                )
            except DCFAError as exc:
                _log_operator_error(exc)
                formatted = _execution_error_outputs(exc)
            except (OSError, TypeError, ValueError) as exc:
                formatted = _input_error_outputs(str(exc))
            yield ui_updates(formatted, buttons_enabled=True)

        csv_run_button.click(
            fn=handle_csv_run,
            inputs=(
                csv_file,
                csv_outcome,
                csv_treatment,
                csv_instrument,
                csv_confirmed,
                csv_question,
                csv_seed,
            ),
            outputs=(
                answer,
                status,
                state_graph,
                evidence,
                plot,
                run_button,
                csv_run_button,
            ),
            scroll_to_output=True,
            show_progress="hidden",
            trigger_mode="once",
        )
    return app.queue(max_size=8, default_concurrency_limit=1)


def main() -> None:
    """Launch the bounded development service as a single-worker ASGI app."""
    from dcfa_website_demo.service import run_service

    run_service()


if __name__ == "__main__":
    main()
