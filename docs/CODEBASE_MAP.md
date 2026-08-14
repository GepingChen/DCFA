# DCFA codebase map

Last verified: 2026-08-12

This map describes checked-in executable behavior. The integrated plan remains
the authority for intended research behavior; code and tests are the authority
for current behavior.

## Repository inventory

| Path | Current role |
|---|---|
| `src/dcfa/schemas.py` | Immutable TabCF, policy, semi-synthetic, evidence, backend, and run contracts |
| `src/dcfa/evidence.py` | Shared ledger validation and Track T/H release gates |
| `src/dcfa/audit.py`, `cache.py`, `artifact_validation.py` | Typed audit, validated cache, and no-refit artifact verifier |
| `src/dcfa/tabcf_iv/` | Isolated continuous-treatment IV adapter, local fallback, bounded managed-client demo/smoke, diagnostics, estimands, real-file loader, and locked runtime validator |
| `src/dcfa/hillstrom_policy/` | Isolated three-action RCT policy adapter, leakage gate, DR/IPW/direct estimators, policies, and four semi-synthetic DGPs |
| `src/dcfa/agent/` | Explicit compiler/state/runtime and identical-recorded-tool Track A harness |
| `src/dcfa/app.py` | Public TabCF-only lazy Gradio shell |
| `src/dcfa_website_demo/` | Portfolio presentation layer and health-checkable ASGI wrapper over the typed public runtime; outside the statistical source hash |
| `evaluation/agent_benchmark/cases/` | Frozen 24-case Track A MVP fixture |
| `evaluation/configs/` | Fail-closed locked TabPFN runtime template |
| `tests/` | Unit, leakage, statistical, agent-behavior, and integration gates |
| `third_party/TabCF` | Authoritative upstream source pinned at `76e0d3eb9e97cebca381d1540db0333c1ef1016e` |
| `requirements-dev.lock`, `requirements-ui.lock`, `requirements-managed-client.lock`, `requirements-website-demo.lock` | Verified Python 3.11 core, UI, managed-client, and combined website-demo environments |
| `Dockerfile`, `compose.yaml`, `.dockerignore` | Non-root, single-worker local deployment package for the development-only website demo |

Generated outputs go under ignored `artifacts/local/`. Raw/private data,
checkpoints, local environments, caches, and logs are ignored. Result paths are
immutable: deterministic runners reject an existing material directory, and
standalone benchmark/probe artifacts reject an existing filename.

## TabCF IV data flow

```text
typed no-W specification + Y/X/Z arrays + dataset manifest
  -> pre-fit role/profile/backend/actual-array-hash/manifest gates
  -> explicit backend construction (never automatic fallback)
  -> Stage 1 distribution F(X|Z) and paired control rank
  -> empirical diagnostics + joint support gate
  -> Stage 2 mean and distribution fits on (X,V)
  -> fixed Gauss-Legendre intervention integration
  -> one canonical clipped/monotone CDF
  -> means, quantiles, risks, directed contrasts
  -> result bundle + evidence ledger + audit + report/plot
  -> independent ID/hash/core-to-bundle/evidence/audit/report verification
```

The fallback uses fixed seeded
`HistGradientBoostingRegressor` mean/quantile models and a fixed 11-level
quantile grid. Its import path does not import Torch or TabPFN. The real TabPFN
backend lazily imports packages and fails with a typed error; locked execution
also requires a hashed checkpoint and runtime image digest before import.

`managed_client.py` is a separate development-only implementation of the same
backend contract. `managed_smoke.py` exposes one fixed 128-row synthetic fixture;
`dcfa_website_demo` reuses the same profile for three bounded synthetic presets
through the existing typed agent state machine. It requires exact
client/model parameters, caps fit/prediction row counts, batches the Stage-2
grid into two calls, derives CDFs from service borders/logits with a tested
NumPy implementation of the service distribution contract, restores only the
observed JSON-null representation of exact zero-probability logits, records
service trace/package metadata, and never silently falls back. One completed smoke
performs three prediction calls total. Service checkpoint and image identities
remain unavailable, so its backend manifest cannot satisfy a locked Track T
release gate.

The upstream `tabcf_core` remains unmodified. Inspected APIs include
`CondCDFModel.fit`, `FullDataStructuralFunctionModel.fit_full`,
`ConditionalCDFEstimator.fit_full`, `compute_interventional_cdf`, and the
separate quantile inversion utilities. DCFA wraps their statistical contract;
it does not invent baseline-covariate support or rewrite their core.

## Hillstrom policy data flow

```text
provenance-complete three-arm dataset
  -> strict feature/outcome/action validation + baseline balance audit
  -> immutable arm-stratified 60/20/20 split
  -> training-only preprocessing and outcome models
  -> validation-only threshold/best-uniform selection
  -> train+validation deterministic refit
  -> serialized content-addressed frozen policy
  -> test-outcome gate unlocks only for the matching frozen policy
  -> randomized-arm effects + paired held-out DR (primary), IPW, and direct estimates
  -> evidence-linked values/contrasts + cost/capacity/allocation report rendering
```

The public app never imports or routes to this adapter. Real-RCT results never
contain individual regret or optimal-action accuracy. Those metrics exist only
in `semisynthetic.py`, where all potential outcomes and same-constraint oracles
are known. Semi-synthetic v6 emits action confusion, abstention
coverage, non-fallback selective regret, fallback-inclusive value, action-gap
calibration error, and constraint violations. Learned comparator capacity
ranking uses fitted values; oracle utilities are reserved for scoring. Track H
policy v5 and semi-synthetic v6 bind exact backend manifests, package/tool
versions, and the exact DCFA Python source-tree hash into run identity.
Track T development evaluation v5 and recorded Track A v4 use the same source
identity boundary. Saved numerical cores now also bind warnings and assumptions.

## Track A flow

Each versioned case supplies the same request, data identity, recorded tool
behavior, numerical fixture, and permissions to both systems. The full runtime
may clarify, retry once, validate evidence, and use cached follow-ups; the fixed
runner uses one fixed chain. Deterministic graders check state, typed error,
calls/refits, warning retention, evidence IDs, and gold-aware numerical silence.
The summary preserves per-case means, worst runs, disagreement, failure
taxonomy, explicit unevaluated metrics, and seeded case-bootstrap intervals.
Independent validation binds every trace's case metadata to the frozen manifest
and recomputes its gold-aware grader outcome before accepting the summary.
Final local recorded-v4 runs use five repetitions nested within each of 24
TabCF-only cases; case is the primary comparison unit. Live-model and Track H
case metrics remain explicitly unevaluated.

## Verified commands

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest
.venv/bin/dcfa --help
.venv-managed/bin/dcfa managed-agent-smoke --token-file <outside-repo-file> --output-dir <fresh-directory>
.venv/bin/dcfa verify-artifacts <run-directory>
.venv/bin/dcfa verify-agent-benchmark <benchmark-json>
```

See the README for complete runnable examples. A smoke test proves mechanics,
not statistical quality or release readiness.

The website demo is deliberately separate from `src/dcfa/`: presentation-only
changes do not rewrite the evidence-bound statistical runtime. It accepts only
frozen synthetic TabCF-IV scenarios, uses the managed `tabpfn-client` profile,
renders the actual agent state events and validated query records, and has no
Hillstrom, arbitrary-upload, or sklearn fallback route. The static personal site
can only embed or link a separately hosted instance; it cannot execute this
Python service on GitHub Pages.

`dcfa_website_demo.service` mounts the queued Gradio app on a single-worker
FastAPI service and exposes `/healthz` plus output-path- and credential-aware
`/readyz`. UI run
directories are reserved atomically and never overwrite prior material. The container runs as UID 10001,
stores generated artifacts under a dedicated volume, disables Gradio monitoring
and public sharing, and remains a local deployment artifact rather than a public
release authorization.

## Unresolved inputs and decisions

- real Torch/TabPFN image, exact package lock, checkpoint, and image digest;
- manuscript/predecessor artifacts for upstream `A*`/`B*` DGP mapping;
- approved Fulton local data and usage/license note;
- approved Hillstrom raw data, exact source/hash, and usage/license decision;
- calibrated and frozen diagnostic thresholds for a locked Track T protocol;
- a chosen/frozen LLM and prompt manifest for a live, rather than recorded,
  end-to-end agent comparison.

These gaps block the corresponding release claims. They do not authorize a
silent fallback, fabricated manifest, or reinterpretation of local synthetic
artifacts.
