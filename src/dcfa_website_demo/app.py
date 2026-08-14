"""Website-oriented Gradio demo for the auditable TabCF Analyst workflow."""

from __future__ import annotations

import html
import importlib.metadata
import json
import os
import threading
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from dcfa.agent.compiler import CompilationRequest
from dcfa.agent.runtime import AgentResponse, CausalAgentRuntime
from dcfa.canonical import to_primitive
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

DEFAULT_OUTPUT_ROOT = Path("artifacts/local/website-demo")
DEFAULT_MANAGED_TOKEN_FILE = Path.home() / ".config" / "dcfa" / "tabpfn_api_key"
MIN_DEMO_ROWS = 120
MAX_DEMO_ROWS = 256
MIN_DEMO_SEED = 0
MAX_DEMO_SEED = 2**32 - 1
DEVELOPMENT_BOUNDARY_WARNING_CODES = {
    "DEVELOPMENT_FALLBACK_NOT_TABCF",
    "DEVELOPMENT_TABPFN_NOT_RELEASE_ELIGIBLE",
}
_OUTPUT_RESERVATION_LOCK = threading.Lock()


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
  max-width: 74rem !important;
  margin-inline: auto !important;
  padding: clamp(1rem, 3vw, 2.5rem) !important;
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif !important;
}

.demo-hero {
  padding: clamp(1.25rem, 4vw, 2.75rem) 0 1.5rem;
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
  max-width: 19ch;
  margin: 0 0 1rem;
  color: var(--demo-ink);
  font-size: clamp(2.15rem, 6vw, 4.2rem);
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

.demo-development-notice {
  max-width: 47rem;
  margin: 1rem 0 0;
  padding: .75rem .9rem;
  border-left: .25rem solid var(--demo-warning);
  background: #fff5e6;
  color: var(--demo-ink);
  font-size: .84rem;
  line-height: 1.55;
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

#run-demo-button {
  min-height: 3rem;
  border: 1px solid var(--demo-accent-deep) !important;
  border-radius: .3rem !important;
  background: var(--demo-accent-deep) !important;
  color: white !important;
  font-weight: 750 !important;
}

#run-demo-button:hover {
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
  background: var(--demo-accent);
  content: "";
  transform: translateY(-50%);
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

.demo-evidence-card h3 {
  margin: 0 0 .85rem;
  font-size: 1rem;
}

.demo-evidence-card dl {
  display: grid;
  margin: 0;
  gap: .65rem;
}

.demo-evidence-card dl > div {
  padding-bottom: .55rem;
  border-bottom: 1px solid var(--demo-line);
}

.demo-evidence-card dt {
  margin-bottom: .15rem;
  color: var(--demo-muted);
  font-size: .69rem;
  font-weight: 750;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.demo-evidence-card dd {
  margin: 0;
  color: var(--demo-ink);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .78rem;
  line-height: 1.5;
  overflow-wrap: anywhere;
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
}

@media (max-width: 30rem) {
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
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    token_file: Path | None = None,
    client_module: Any | None = None,
    client_version: str | None = None,
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
        client.set_access_token(credential)
        del credential
        selected = SCENARIOS[scenario]
        dataset = generate_development_iv(
            n=rows,
            seed=seed,
            instrument_strength=selected.instrument_strength,
        )
        manifest = replace(dataset.manifest, estimator_backend=EstimatorBackend.TABPFN)
        interventions = tuple(
            float(value)
            for value in np.quantile(dataset.columns["X"], selected.intervention_quantiles)
        )
        if selected.violate_support:
            interventions = (
                *interventions[:-1],
                float(np.max(dataset.columns["X"]) + 5.0),
            )

        request = CompilationRequest(
            dataset_hash=manifest.dataset_hash,
            outcome="Y",
            treatment="X",
            instrument="Z",
            objective="quantile_contrast",
            intervention_grid=interventions,
            x=interventions[-1],
            comparison_x=interventions[0],
            level=0.5,
            units="Y_units",
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

        output_dir = _reserve_output_directory(Path(output_root), scenario, seed)
        engine = TabCFAnalysisEngine(backend_factory=backend_factory)
        tool = _WebsiteAnalysisTool(output_dir, engine)
        response = CausalAgentRuntime(analysis_tool=tool).execute(
            request,
            dataset.columns,
            manifest,
        )
    except Exception:
        if "output_dir" in locals():
            _remove_empty_reservation(output_dir)
        raise
    finally:
        client.reset()
    if not any(output_dir.iterdir()):
        _remove_empty_reservation(output_dir)
    plot_path = output_dir / "interventional_summary.png"
    return PortfolioDemoResult(
        scenario=scenario,
        response=response,
        plot_path=plot_path if plot_path.is_file() else None,
        output_dir=output_dir if output_dir.is_dir() else None,
    )


def _status_html(result: PortfolioDemoResult) -> str:
    response = result.response
    if response.status == "blocked":
        error = response.error or {}
        code = html.escape(str(error.get("code", "BLOCKED")))
        message = html.escape(str(error.get("message", "The request was blocked.")))
        return (
            '<div class="demo-status demo-status--blocked" role="status">'
            f"<strong>Blocked safely · {code}</strong>{message} "
            "No numerical causal answer was returned.</div>"
        )
    warning_codes = {warning.code for warning in response.warnings}
    warning_codes.update(warning.code for query in response.queries for warning in query.warnings)
    diagnostic_warning_codes = warning_codes - DEVELOPMENT_BOUNDARY_WARNING_CODES
    if diagnostic_warning_codes:
        return (
            '<div class="demo-status demo-status--warning" role="status">'
            "<strong>Completed with empirical warnings</strong>"
            "The warnings remain attached to the answer and evidence record. This is a "
            "development-only managed TabPFN result, not locked Track T evidence.</div>"
        )
    return (
        '<div class="demo-status" role="status">'
        "<strong>Workflow completed and evidence validated</strong>"
        "The displayed value comes from the validated result bundle. This is a "
        "development-only managed TabPFN result, not locked Track T evidence.</div>"
    )


def _state_graph_html(response: AgentResponse) -> str:
    items = []
    for event in response.state_events:
        state = event.state.value
        label = state.replace("_", " ").title()
        reason = html.escape(event.reason.replace("_", " "))
        css_class = "blocked" if state == "blocked" else "completed"
        items.append(
            f'<li class="{css_class}"><span>{html.escape(label)}</span>'
            f'<span class="state-reason">{reason}</span></li>'
        )
    return '<ol class="state-graph" aria-label="Agent state trace">' + "".join(items) + "</ol>"


def _answer_markdown(response: AgentResponse) -> str:
    if not response.queries:
        return (
            "### No numerical answer\n\n"
            "The workflow stopped at a typed gate. Review the status and state trace for the "
            "exact reason."
        )
    query = response.queries[0]
    warning_count = len(query.warnings)
    warning_summary = (
        "None"
        if warning_count == 0
        else f"{warning_count} attached — inspect the evidence record below"
    )
    return (
        "### Evidence-linked answer\n\n"
        f"**{query.value_display} {query.units}**  \n"
        f"Claim: `{query.claim_type}`  \n"
        f"Evidence: `{query.evidence_id}`  \n"
        f"Support: `{query.support_status.value}`  \n"
        f"Warnings: {warning_summary}"
    )


def _evidence_card_html(response: AgentResponse) -> str:
    if not response.queries:
        return (
            '<div class="demo-evidence-card demo-evidence-placeholder">'
            "<h3>Evidence record</h3>"
            "No evidence record was emitted because the workflow returned no numerical answer."
            "</div>"
        )
    query = response.queries[0]
    fields = (
        ("Claim", query.claim_type),
        ("Value", f"{query.value_display} {query.units}"),
        ("Support", query.support_status.value),
        ("Evidence ID", query.evidence_id),
    )
    details = "".join(
        f"<div><dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd></div>"
        for label, value in fields
    )
    if query.warnings:
        warning_items = "".join(
            "<li>"
            f"<strong>{html.escape(warning.message)}</strong><br>"
            f"<code>{html.escape(warning.code)}</code>"
            "</li>"
            for warning in query.warnings
        )
        warning_html = (
            '<div class="demo-evidence-warnings"><h4>Attached warnings</h4>'
            f'<ul class="demo-warning-list">{warning_items}</ul></div>'
        )
    else:
        warning_html = "<p>No warnings are attached to this query.</p>"
    return (
        '<div class="demo-evidence-card"><h3>Evidence record</h3>'
        f"<dl>{details}</dl>{warning_html}</div>"
    )


def _input_error_outputs(message: str) -> tuple[str, str, str, str, None, str]:
    escaped = html.escape(message)
    return (
        '<div class="demo-status demo-status--blocked" role="status">'
        f"<strong>Input rejected safely</strong>{escaped} No workflow was run.</div>",
        '<div class="demo-status demo-status--idle">No state trace was created.</div>',
        "### No numerical answer\n\nCorrect the bounded demo controls and try again.",
        '<div class="demo-evidence-card demo-evidence-placeholder">'
        "<h3>Evidence record</h3>No evidence record was emitted.</div>",
        None,
        json.dumps({"status": "input_rejected", "message": message}, indent=2),
    )


def _execution_error_outputs(error: DCFAError) -> tuple[str, str, str, str, None, str]:
    message = html.escape(error.message)
    code = html.escape(error.code.value)
    return (
        '<div class="demo-status demo-status--blocked" role="status">'
        f"<strong>Execution blocked safely · {code}</strong>{message} "
        "No numerical causal answer was returned.</div>",
        '<div class="demo-status demo-status--idle">Execution stopped before a result.</div>',
        "### No numerical answer\n\nThe managed backend failed closed; sklearn was not used.",
        '<div class="demo-evidence-card demo-evidence-placeholder">'
        "<h3>Evidence record</h3>No evidence record was emitted.</div>",
        None,
        json.dumps({"status": "blocked", "error": error.to_dict()}, indent=2),
    )


def _audit_json(result: PortfolioDemoResult) -> str:
    payload = {
        "scenario": result.scenario,
        "status": result.response.status,
        "specification_id": result.response.specification_id,
        "result_bundle_id": result.response.result_bundle_id,
        "tool_calls": result.response.tool_calls,
        "retry_count": result.response.retry_count,
        "state_events": result.response.state_events,
        "error": result.response.error,
    }
    return json.dumps(to_primitive(payload), indent=2, sort_keys=True)


def format_portfolio_result(
    result: PortfolioDemoResult,
) -> tuple[str, str, str, str, str | None, str]:
    """Project a runtime response into display-only values without recomputing numbers."""
    return (
        _status_html(result),
        _state_graph_html(result.response),
        _answer_markdown(result.response),
        _evidence_card_html(result.response),
        None if result.plot_path is None else str(result.plot_path),
        _audit_json(result),
    )


def build_app(*, output_root: Path = DEFAULT_OUTPUT_ROOT) -> Any:
    """Build the optional website demo while keeping Gradio a lazy dependency."""
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            "Install the website demo with: python -m pip install -r requirements-website-demo.lock"
        ) from exc

    scenario_choices = [(item.label, key) for key, item in SCENARIOS.items()]
    with gr.Blocks(
        title="DCFA — auditable causal agent demo",
        analytics_enabled=False,
        fill_width=True,
    ) as app:
        gr.HTML(
            """
            <header class="demo-hero">
              <p class="demo-eyebrow">DCFA · Local development workflow demo</p>
              <h1>Trace a causal workflow. See every gate.</h1>
              <p class="demo-hero-copy">
                A narrow distributional-IV agent that compiles a typed request, calls a
                deterministic tool, blocks unsupported claims, and links each answer to
                reproducible evidence.
              </p>
              <div class="demo-badges" aria-label="Supported scope">
                <span>Continuous treatment X</span><span>Scalar instrument Z</span>
                <span>Continuous outcome Y</span><span>No baseline covariates W</span>
              </div>
              <p class="demo-development-notice" role="note">
                <strong>Synthetic and development-only.</strong> This workflow uses the official
                managed TabPFN service for the TabCF distributional stages. Inputs leave this
                machine, and the opaque service runtime cannot support a locked Track T or
                real-world causal claim.
              </p>
            </header>
            """
        )
        with gr.Row(elem_classes="demo-controls"):
            with gr.Column(scale=5, elem_classes="demo-panel"):
                gr.Markdown(
                    "### 1 · Choose a behavior",
                    elem_classes="demo-section-heading",
                )
                gr.Markdown(
                    "These are frozen, synthetic engineering scenarios—not uploaded data or "
                    "a general causal-method router.",
                    elem_classes="demo-section-copy",
                )
                scenario = gr.Radio(
                    choices=scenario_choices,
                    value="strong_iv",
                    label="Guided path",
                )
                question = gr.Textbox(
                    value=scenario_question("strong_iv"),
                    label="Example question",
                    lines=3,
                    interactive=False,
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
                    "Run the auditable workflow",
                    variant="primary",
                    elem_id="run-demo-button",
                )
            with gr.Column(scale=5, elem_classes="demo-panel"):
                gr.Markdown(
                    "### 2 · Inspect the state trace",
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

        gr.Markdown("## 3 · Inspect the validated output", elem_classes="demo-section-heading")
        status = gr.HTML(
            '<div class="demo-status demo-status--idle">'
            "No run yet. The demo never invents a numerical placeholder.</div>"
        )
        with gr.Row():
            with gr.Column(scale=4, elem_classes="demo-panel demo-answer"):
                answer = gr.Markdown(
                    "### Evidence-linked answer\n\nRun a scenario to populate this panel."
                )
            with gr.Column(scale=6, elem_classes="demo-panel"):
                evidence = gr.HTML(
                    '<div class="demo-evidence-card demo-evidence-placeholder">'
                    "<h3>Evidence record</h3>Run a scenario to populate this panel.</div>"
                )
        plot = gr.Image(
            type="filepath",
            label="Result-bundle distribution preview",
            visible=False,
        )
        with gr.Accordion("Machine-readable state and identity", open=False):
            audit = gr.Code(language="json", label="Agent trace", interactive=False)

        gr.HTML(
            """
            <section class="demo-boundary" aria-labelledby="boundary-title">
              <p class="demo-eyebrow" id="boundary-title">What this demo will not claim</p>
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

        def handle_run(selected_scenario: str, selected_rows: int, selected_seed: int):
            try:
                formatted = format_portfolio_result(
                    execute_portfolio_scenario(
                        selected_scenario,
                        selected_rows,
                        selected_seed,
                        output_root=output_root,
                    )
                )
            except DCFAError as exc:
                formatted = _execution_error_outputs(exc)
            except (TypeError, ValueError) as exc:
                formatted = _input_error_outputs(str(exc))
            status_value, state_value, answer_value, evidence_value, plot_value, audit_value = (
                formatted
            )
            return (
                status_value,
                state_value,
                answer_value,
                evidence_value,
                gr.update(value=plot_value, visible=plot_value is not None),
                audit_value,
            )

        run_button.click(
            fn=handle_run,
            inputs=(scenario, rows, seed),
            outputs=(status, state_graph, answer, evidence, plot, audit),
        )
    return app.queue(max_size=8, default_concurrency_limit=1)


def main() -> None:
    """Launch the bounded development service as a single-worker ASGI app."""
    from dcfa_website_demo.service import run_service

    run_service()


if __name__ == "__main__":
    main()
