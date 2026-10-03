# Agentic TabCF: Distributional Causal Analysis with TabPFN

Implementation plan — 2026-10-03

Status: planning document; implementation and submission are not initiated by saving this file.

## Agreed direction

The user approved the title above and the following sequence:

1. Improve the existing Agentic TabCF parent project first.
2. Extract a focused, reproducible submission subproject from the improved parent.
3. Submit that subproject to the TabPFN-3.5 Hackathon when it is ready and submission is authorized.

Keep reusable statistical, agent, reporting and usability improvements in the parent.
Do not prematurely fork the implementation or redesign the parent around a contest.
The approved title does not itself authorize renaming packages, repositories or deployments.

## Competition requirements and timing

The official terms inspected in this conversation specify:

- TabPFN-3.5 must be a core component of a working project.
- Submit a public Apache-2.0 source repository, a project description, runnable
  instructions, and input data or a public data URL. A demo video is optional.
- Judging: TabPFN-3.5 showcase 50%; creativity, originality and practical value
  30%; technical quality and reproducibility 20%.
- Deadline: 2026-10-06, 23:59 CEST / 16:59 America/Chicago.
- The inspected terms do not explicitly prohibit extending an existing project.
  Disclose the prior TabCF method and the new work accurately.

Source: [official hackathon page and Terms & Conditions](https://platform.priorlabs.ai/hackathon-3.5).
Recheck the terms before submission. As of this plan, approximately three days
remain; the earlier two-week preparation estimate is obsolete. Parent-project
quality takes priority. If the focused entry is not ready, do not rush changes,
weaken safeguards or claim completion merely to meet the deadline.

## Current starting point

This snapshot comes from repository inspection, not a fresh provider experiment.
Repository HEAD at inspection: `d4b46cf`. Existing uncommitted work is preserved.

- The current working tree upgrades the local managed path to explicit
  `v3.5_default`, client 0.6.1, one estimator and Thinking disabled. Its decision
  log records a real 128-row synthetic API run consuming 30,000 tokens across
  three predictions. These changes are in progress, not a verified release of
  the entire product.
- The repository documents a saved real cigarette report as the public Space's
  default preview, readable without login, an API key or GPU allocation.
- The dedicated ZeroGPU path remains a local TabPFN v2 path. Its saved report
  must not be relabeled as a TabPFN-3.5 result.
- The parent already has bounded CSV clarification, explicit confirmation,
  deterministic distributional calculations, evidence-linked reporting,
  support checks and cached-result behavior.
- Historical recorded-tool Track A checks do not establish superiority of a
  live LLM agent. Existing research and development evidence retain their labels.

References: [README](../README.md), [website workflow](WEBSITE_DEMO.md),
[decisions](DECISIONS.md), [implementation status](IMPLEMENTATION_STATUS.md),
and [cigarette example](../examples/cigarette_demand_small/README.md).
Status documents contain historical sections; inspect current code and artifacts
before scheduling work that may already be complete.

## Phase 1 — Improve the parent project

### 1. Stabilize the TabPFN-3.5 managed path

- Complete the existing migration and its relevant tests without including
  unrelated work in commits.
- Verify the full distribution interface used by both stages, including CDF
  evaluation, means, quantile inversion, threshold probabilities and contrasts.
  A model-name change alone is insufficient.
- Keep the selected model explicit and record the service-reported model and
  configuration. Preserve no-silent-fallback behavior and existing evidence status.
- Exercise one supported real analysis end to end, including report download
  and the existing independent verifier. Preserve the actual result and warnings.
- Measure total latency, provider time where available, prediction count and
  token usage. Do not infer speed from fit counts alone.

Completion evidence: relevant tests plus a real 3.5 result bundle, downloadable
report and measured execution record. A smoke run establishes mechanics only.

### 2. Complete the user-facing analysis workflow

- Check upload, missing-information clarification, role and unit review,
  explicit confirmation, computation, report rendering and download together.
- Ask only for missing information. Textual confirmation must not execute a fit;
  retain the dedicated confirmation button.
- Present intervention values, original/log units, outcome definitions and
  contrast direction clearly. All displayed numbers must derive from the same bundle.
- Verify that follow-ups use the validated cached result rather than refitting.
  Clearly distinguish supported follow-up behavior from a new analysis request.
- Make quota, provider, support and finalization failures understandable without
  changing the requested analysis or silently switching models.
- Preserve the current visual style and useful saved-report preview.

Completion evidence: one successful user journey and focused checks of changed
failure paths, including report/ZIP readback. Do not rerun unrelated checks.

### 3. Strengthen the distributional case study

Use the existing cigarette-demand case where appropriate: price interventions
at 100 and 120 CPI-deflated cents, with transformations and units shown explicitly.
Produce a new 3.5 run rather than overwriting or relabeling the earlier v2 report.

The main presentation should explain two interventional CDFs, selected quantiles,
their directed differences, and an explicitly defined exceedance probability.
Use the quantiles supported by the actual reviewed specification; do not imply
that an older report contains newly requested statistics.

Preserve the exploratory interpretation: these are state-level aggregates under
maintained IV assumptions. The bounded model does not resolve omitted income,
state/year effects or within-state dependence. Do not claim individual causal
effects, instrument validity, statistical significance or policy effectiveness
from this demonstration. If support fails, show the rejection honestly.

### 4. Add proportionate evidence for the model's contribution

After the end-to-end workflow is stable, run a bounded comparison using the same
data, seeds, estimands, grids and settings except for the intended model change.
Start with the existing older-model path versus 3.5; add another statistical
comparator only if it answers a concrete question and time permits.

- On synthetic data with oracle truth, measure CDF, quantile and risk errors,
  together with latency and token cost. Include more than a single favorable seed.
- On real data, demonstrate usability and interpretation without claiming oracle accuracy.
- State model variants, ensemble settings, replication counts and limitations.
  Retain null results and regressions; do not search for a favorable showcase seed.
- Keep estimator comparisons separate from agent comparisons. A claim of agent
  superiority requires the appropriate paired live evaluation with fixed tools.
- For longer measurements, provide durable logs, incremental output and a restart path.

Follow existing research/release rules when promoting results. Do not create
new hashes, freezes, baselines or gates merely to manage this plan.

## Phase 2 — Extract the submission subproject

Start extraction after the parent has a complete, evidenced 3.5 workflow.
Select the packaging approach then: a thin entry package tied to an identifiable
parent version, or a self-contained minimal export with attribution. Avoid a
second independently maintained statistical implementation. Creation of a new
public repository, deployment and submission remain separate authorized actions.

### Submission scope

- Use the approved title exactly: **Agentic TabCF: Distributional Causal Analysis with TabPFN**.
- Make TabPFN-3.5 prominent in the subtitle, model information and demonstration.
- Focus on continuous-treatment distributional IV analysis with one Y, X and Z.
- Include the natural-language workflow, deterministic two-stage computation,
  distribution report, one real/public example and one transparent synthetic example.
- Preserve no-W validation, support/weak-IV warnings, confirmation and data-transfer controls.
- Exclude Hillstrom, general causal routing, autonomous policy deployment and
  unrelated research machinery from the submission presentation.

### Reproducibility and licensing

- Resolve Apache-2.0 licensing for the submitted code with the relevant rights
  holders; retain third-party notices and separate data/model licenses. Do not
  assume changing parent package metadata resolves all rights.
- Provide a tested clean-environment installation and a short run command using
  the actual implemented entry point. Document API credentials and quota requirements.
- Include public/synthetic input data or stable public retrieval instructions.
  Preserve the cigarette source attribution and accompanying license information.
- Include a clear architecture explanation separating LLM compilation, TabPFN
  predictions, deterministic causal computation and validated presentation.
- Label saved previews and live execution distinctly. Verify the exact artifact
  or hosted path the judges will use, not only local unit tests.

### Demonstration and submission materials

Prepare a two-to-three-minute video: domain question, role/unit confirmation,
real 3.5 execution or honestly labeled replay, distribution results, and one
unsupported request handled clearly. Show why a distribution is useful beyond
a mean-only summary. Keep audit details available without making them the opening story.

Deliver a concise README, project description, setup instructions, reproducible
example, measured comparison where available, model/evidence labels, limitations,
and optional video link. Apply the existing release checks to the public package.
Submit only supported claims; a polished demonstration is not a statistical validation.

## API usage assumptions

Ordinary free API access is independent of hackathon participation. Official
documentation checked on 2026-10-03 lists default daily/monthly budgets of
5 million / 20 million computation tokens. Account-specific limits control actual
availability. Additional hackathon credits are not a permanent entitlement;
the launch discount ended on September 29. Estimate intended workloads and
record actual usage instead of promising a fixed number of free analyses.

The API sends data to Prior Labs; use only authorized shareable inputs. Gemini
is a separate service with separate credentials, data boundaries and quotas.

Sources: [pricing](https://priorlabs.ai/pricing),
[metering](https://docs.priorlabs.ai/api-reference/metering),
[3.5 release notes](https://docs.priorlabs.ai/changelog/tabpfn-3.5),
[client and data guidance](https://github.com/PriorLabs/tabpfn-client).

## Next implementation step

Finish and verify the parent project's in-progress managed 3.5 workflow first,
then establish which remaining usability and reporting issues actually block a
complete user journey. Update this plan from observed results before extraction.
Saving this plan does not start experiments, change licensing, deploy a service,
accept contest terms or submit an entry.
