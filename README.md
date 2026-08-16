# DCFA

DCFA is an auditable local runtime for **TabCF Analyst**, a deliberately narrow
continuous-treatment distributional-IV workflow. It separates three evidence
tracks that must never be merged in claims:

- **Track T:** TabCF estimator evidence for continuous treatment, continuous
  outcome, one scalar IV, and no baseline covariates `W`.
- **Track H:** held-out policy value in a categorical three-action randomized
  experiment, plus known-oracle semi-synthetic evaluation.
- **Track A:** workflow reliability for a fixed chain versus an explicit agent
  using identical recorded tools and fixtures.

Hillstrom is an offline companion evaluation environment. It is not a TabCF
validation dataset and is never exposed through the public TabCF UI.

## Implemented local scope

The repository now contains an installable Python package, pinned local
development environments, typed schemas/errors, immutable specifications,
content-addressed evidence, audit logs, cache validation, independent artifact
verification, and these deterministic entry points:

- a no-`W` TabCF IV vertical slice with an explicitly selected
  `sklearn_quantile_fallback`;
- a bounded, development-only `tabpfn-client` adapter for fixed synthetic agent
  smoke and website-demo paths, plus a default one-call Gemini compiler and an
  explicitly confirmed local CSV website route with exact Y/X/Z roles, strict
  row/column gates, and service metadata;
- mean, CDF, quantile, threshold-risk, contrast, diagnostic, and strict-support
  tools derived from one validated result bundle;
- strong-IV, weak-IV, unsupported-treatment, non-empty-`W`, and outside-support
  paths;
- an oracle-scored fallback engineering benchmark on a DCFA-only triangular
  DGP;
- a provenance-required Fulton Fish local-file loader, with no automatic data
  download;
- an isolated Hillstrom policy adapter with arm-stratified 60/20/20 splits,
  strict missingness and baseline-balance audit, split-scoped preprocessing,
  immutable policy freeze, a test-outcome access gate, uniform and
  uncertainty-aware policies, randomized-arm effects, DR/IPW/direct values,
  paired contrasts, costs, capacity, allocations, and release checks;
- four known-oracle semi-synthetic policy DGPs with constrained value/regret,
  action confusion, abstention/selective-regret, fallback-inclusive value, and
  action-gap calibration metrics;
- an explicit agent state machine and 24-case recorded Track A benchmark with
  five runs nested within each case;
- a one-request Gemini Track A smoke that compiles one frozen synthetic prompt
  into a typed proposal before the deterministic evidence-validated runtime;
- a lazy Gradio shell that imports neither Hillstrom nor model backends until
  their own paths are explicitly requested.

Every local sklearn TabCF result is labeled
`local_development / sklearn_quantile_fallback / development_only`. It is not a
TabCF result and is ineligible for locked Track T claims. Synthetic Track H
fixtures are likewise `development_only` and are not real Hillstrom evidence.

## Local setup

Core development and tests:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install -e . --no-deps
```

Managed TabPFN client smoke (networked and usage-credit consuming):

```bash
python3 -m venv .venv-managed
.venv-managed/bin/python -m pip install -r requirements-managed-client.lock
.venv-managed/bin/python -m pip install -e . --no-deps
chmod 600 ~/.config/dcfa/tabpfn_api_key
.venv-managed/bin/dcfa managed-agent-smoke \
  --token-file ~/.config/dcfa/tabpfn_api_key \
  --output-dir artifacts/local/managed-agent-smoke-v1
```

The token file must be outside this repository and contain only the API key.
The command sends one frozen 128-row synthetic IV fixture to the Prior Labs
service. It pins `tabpfn-client==0.3.3`, model `v2.5_default`, one estimator,
and thinking mode off. Stage-2 intervention rows are batched, so one successful
run makes three prediction API calls. It does not accept a CSV or user dataset.

Gemini live-agent smoke (one network request, with no data rows transmitted):

```bash
python3 -m venv .venv-gemini
.venv-gemini/bin/python -m pip install -r requirements-gemini.lock
.venv-gemini/bin/python -m pip install -e . --no-deps
chmod 600 ~/.config/dcfa/gemini_api_key
.venv-gemini/bin/dcfa gemini-agent-smoke \
  --api-key-file ~/.config/dcfa/gemini_api_key \
  --output-dir artifacts/local/gemini-live-smoke-v1
```

The Gemini key must remain outside the repository. The frozen
`gemini-3.6-flash` request sends only the prompt, Y/X/Z schema contract, and
symbolic intervention labels. Gemini never sees data rows or actual intervention
values and makes no numerical causal calculation. The local deterministic tool
produces the numerical result and evidence ID. API failure or unexpected output
stops without retry or backend fallback.

Managed TabPFN website-demo environment:

```bash
.venv/bin/python -m pip install -r requirements-website-demo.lock
.venv/bin/python -m pip install -e . --no-deps
chmod 600 ~/.config/dcfa/tabpfn_api_key
chmod 600 ~/.config/dcfa/gemini_api_key
```

Website-oriented guided demo (`development_only`; local service only):

```bash
.venv/bin/dcfa-website-demo
```

This presentation shell defaults to `gemini-3.6-flash` for one bounded structured
compile call per run, then uses the real typed agent state machine and official
managed TabPFN service. Gemini receives the natural-language question, Y/X/Z
contract, and symbolic `low/center/high` labels; it receives no rows or actual
intervention values and performs no numerical causal calculation. The page
supports mean or median summaries and directed contrasts within that symbolic
scope. It reads `~/.config/dcfa/gemini_api_key` and
`~/.config/dcfa/tabpfn_api_key` by default. CSV runs require confirmation before
the question goes to Google and selected rows go separately to Prior Labs. Any
Gemini or Client failure blocks without retry, LLM bypass, or sklearn fallback.
See [`docs/WEBSITE_DEMO.md`](docs/WEBSITE_DEMO.md) for the health-checkable
container workflow, cloud-data boundary, static Astro embed boundary, and release
prerequisites.

## Stable commands

```bash
# TabCF contract/demo branches; all local results are development-only.
dcfa tabcf-demo --scenario strong_iv --output-dir artifacts/local/tabcf-strong
dcfa tabcf-demo --scenario weak_iv --output-dir artifacts/local/tabcf-weak
dcfa tabcf-demo --scenario support_violation --output-dir artifacts/local/tabcf-blocked
dcfa track-t-development-evaluation \
  --seeds 101,202,303 --rows 200 \
  --output-dir artifacts/local/track-t-development-evaluation-v6

# Offline Track H mechanics; generated input is not real Hillstrom.
dcfa hillstrom-demo --output-dir artifacts/local/hillstrom-smoke-v6
dcfa hillstrom-semisynthetic --replications 50 \
  --output-dir artifacts/local/hillstrom-semisynthetic-v7

# Recorded Track A: 24 cases x 5 nested runs x 2 systems.
dcfa agent-benchmark --runs 5 \
  --output artifacts/local/agent-benchmark-recorded-v5.json

# One-call live Gemini mechanics; not a comparative Track A benchmark.
dcfa gemini-agent-smoke \
  --api-key-file ~/.config/dcfa/gemini_api_key \
  --output-dir artifacts/local/gemini-live-smoke-v1
dcfa verify-gemini-agent-smoke artifacts/local/gemini-live-smoke-v1

# Networked managed-client mechanics; fixed synthetic data, development-only.
dcfa managed-agent-smoke \
  --token-file ~/.config/dcfa/tabpfn_api_key \
  --output-dir artifacts/local/managed-agent-smoke-v1

# Independent verification never refits.
dcfa verify-artifacts artifacts/local/hillstrom-smoke-v6
dcfa verify-agent-benchmark artifacts/local/agent-benchmark-recorded-v5.json

# Quality gates.
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest
git diff --check
```

Result paths are immutable. Every CLI run must use a fresh versioned directory
or filename; an existing material path returns `OUTPUT_PATH_EXISTS`. The UI
allocates a new numbered run directory instead of replacing an earlier result.

## Repository delivery workflow

Completed and verified in-scope repository changes are committed and pushed to
the current branch by default. Each delivery must inspect and explicitly stage
the intended paths, exclude secrets, raw/private data, generated artifacts and
unrelated user work, run the applicable quality gates, make a normal commit, and
push without rewriting history. Pulls, rebases, merges, force-pushes, tags, PRs,
releases, deployments, and publication still require separate user direction.
See [`AGENTS.md`](AGENTS.md) for the full repository operating rule.

`dcfa fulton-local` requires a user-provided CSV plus exact source, retrieval
date, and usage/license note. `dcfa validate-tabpfn-runtime` requires a fully
frozen remote manifest described in
[`docs/REMOTE_TABPFN_RUNNER.md`](docs/REMOTE_TABPFN_RUNNER.md).

## Release blockers

The following are intentionally not represented as complete:

1. This macOS environment has no working local Torch/TabPFN installation. A
   separate managed-client development path can test mechanics against the
   Prior Labs service, but it does not expose a checkpoint hash or service
   image digest and is therefore not release-eligible. Publishable Track T must
   run in a validated, hashed runtime with the real model checkpoint.
2. The TabCF manuscript/predecessor artifacts needed to freeze the plan's
   conceptual DGP labels against upstream `A*`/`B*` codes are not in this
   repository.
3. No Fulton raw CSV or explicit data-use decision was supplied. The upstream
   package is GPL-3, while the Rdatasets archive warns that row-level data
   licensing may be unclear, so DCFA does not auto-download or redistribute it.
4. No approved Hillstrom raw file, exact hash, or dataset usage/license decision
   was supplied. Real-RCT and genuinely Hillstrom-calibrated results therefore
   remain blocked; only the loader/contracts and explicitly synthetic mechanics
   run locally.
5. Diagnostic warning/stop thresholds have not been calibrated on the frozen
   manuscript DGP suite. The current thresholds are development checks and have
   no locked Track T configuration ID.
6. One Gemini model/prompt manifest is frozen for a single clean synthetic smoke,
   and a separate versioned Gemini profile now powers the local website compiler.
   The first authenticated smoke request exposed a removed Interactions API
   parameter and stopped before analysis; the corrected request shape and website
   integration are offline-tested, but neither is a paired 24-case
   fixed-workflow/full-agent evaluation. Repeated live reliability, Hillstrom
   leakage, policy constraints, and final production cost/latency distributions
   remain unevaluated.

Read [`AGENTS.md`](AGENTS.md), the
[`integrated research plan`](plan/TabCF_Agent_Integrated_Research_Plan_ZH.md),
[`identification boundaries`](docs/IDENTIFICATION_BOUNDARIES.md), and the
[`codebase map`](docs/CODEBASE_MAP.md) before extending a research boundary.
The exact current coverage, verified artifact IDs, and external blockers are in
[`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md).
