# Verification and evidence status

Last updated: 2026-08-13

## Verified locally

- Editable install in a repository-local Python 3.11 venv.
- Core and UI dependency locks on macOS arm64.
- Ruff lint and format checks.
- All 86 unit, leakage, statistical, agent-behavior, and integration tests.
- Strong/weak/support TabCF development branches and independent artifact
  verification.
- Track T oracle engineering evaluation for two scenarios and three seeds,
  labeled as non-TabCF development evidence.
- Hillstrom policy protocol v5 synthetic vertical slice with strict missingness
  validation, H0 baseline-balance audit, freeze-before-test ordering, frozen
  cost/capacity and action-allocation reporting, 31 evidence records, complete
  assumptions/warnings, and independent artifact verification.
- Four-scenario semi-synthetic benchmark with 50 replications per DGP and 84
  evidence-linked scalar/confusion-matrix aggregates under protocol v6.
- Track A protocol v4 with 24 cases, five runs per case, two systems, identical
  recorded tools, gold-aware forbidden-numeric checks, per-case/worst-run
  outcomes, disagreement/failure taxonomies, and deterministic case-bootstrap
  comparisons. Independent verification binds every raw trace to the frozen
  case metadata and recomputes its grader outcome. Live-model latency, token,
  and cost fields remain explicitly unevaluated.
- Every current result backend/benchmark is bound to the exact
  `src/dcfa/**/*.py` source-tree SHA-256 and fails verification under a different
  local source tree. The verifier also recomputes specification, backend,
  split, policy, run, bundle, evidence, and audit IDs and checks deterministic
  numerical-core projections.
- Website demo strong/weak/outside-support execution, atomic run reservation,
  bounded controls, ASGI liveness/readiness, wide/mobile browser QA, and a
  healthy non-root container with independently verified output.

Current verified source-tree identity:
`sha256:03c2b585b2eb852087412257745875865c5a45c91b50a8cc3b5daedef405c9d9`.
See `docs/IMPLEMENTATION_STATUS.md` for current run and bundle IDs.

## Explicitly unverified or unavailable

- Real TabPFN import, checkpoint load, GPU execution, or locked Track T results.
  The one bounded local probe found no installed `torch` and made no fallback
  attempt.
- Full TabCF manuscript DGP mapping and locked simulation budget.
- A user-approved Fulton raw input or actual Fulton local run.
- A user-approved Hillstrom raw input, real held-out policy value, or genuinely
  Hillstrom-calibrated semi-synthetic run.
- A live frozen LLM/model/prompt benchmark. Track A currently isolates workflow
  logic using deterministic recorded fixtures.
- Statistical coverage or publishable performance inferred from smoke tests.

## Final gate sequence

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest
.venv/bin/dcfa --help
.venv/bin/dcfa verify-artifacts artifacts/local/smoke-v4
.venv/bin/dcfa verify-artifacts artifacts/local/weak-v4
.venv/bin/dcfa verify-artifacts artifacts/local/hillstrom-smoke-v6
.venv/bin/dcfa verify-artifacts artifacts/local/hillstrom-semisynthetic-v7
.venv/bin/dcfa verify-artifacts artifacts/local/track-t-development-evaluation-v6
.venv/bin/dcfa verify-agent-benchmark \
  artifacts/local/agent-benchmark-recorded-v5.json
git diff --check
git status --short --branch
```

Passing these gates establishes local mechanics and provenance consistency only.
Release gates remain closed until the missing real data and locked TabPFN inputs
are supplied and verified.

After the applicable gates pass, inspect the complete diff and sensitive-data
scan, stage only the intended paths, commit, push the current branch without
force, and verify that local `HEAD` matches its upstream ref. This is the default
delivery workflow for completed repository changes.
