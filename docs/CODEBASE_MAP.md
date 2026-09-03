# DCFA codebase map

Last verified: 2026-08-30

This map describes checked-in executable behavior. The integrated plan remains
the authority for intended research behavior; code and tests are the authority
for current behavior.

## Repository inventory

| Path | Current role |
|---|---|
| `src/dcfa/schemas.py` | Immutable TabCF, policy, semi-synthetic, evidence, backend, and run contracts |
| `src/dcfa/evidence.py` | Shared ledger validation and Track T/H release gates |
| `src/dcfa/audit.py`, `cache.py`, `artifact_validation.py` | Typed audit, validated cache, and no-refit artifact verifier |
| `src/dcfa/tabcf_iv/` | Isolated continuous-treatment IV adapter, local fallback, frozen local TabPFN v2 profile, bounded managed-client demo/smoke, diagnostics, estimands, real-file loader, and locked runtime validator |
| `src/dcfa/hillstrom_policy/` | Isolated three-action RCT policy adapter, leakage gate, DR/IPW/direct estimators, policies, and four semi-synthetic DGPs |
| `src/dcfa/agent/` | Explicit compiler/state/runtime, identical-recorded-tool harness, and bounded Gemini live-smoke adapter |
| `src/dcfa/app.py` | Public TabCF-only lazy Gradio shell |
| `src/dcfa_website_demo/` | Visitor-safe presentation mappings/plot, one-call Gemini compiler, strict CSV ingress, native ZeroGPU wrapper, and health-checkable local ASGI wrapper; outside the statistical source hash |
| `src/dcfa_showcase/` | Offline freeze/export/verifier for the hash-bound public prepared replay; outside the statistical source hash |
| `src/dcfa_colab/` | Secret-scoped notebook adapter, local CSV preflight, verified archive export, and notebook static validator; outside the statistical source hash |
| `showcase/prepared_demo_v1/` | Committed public-safe prompt, synthetic CSV, visitor projection, plot, and verification manifest |
| `notebooks/DCFA_Custom_Analysis_Colab.ipynb` | Pinned user-owned Colab workflow with no saved outputs or public web-service path |
| `evaluation/agent_benchmark/cases/` | Frozen 24-case Track A MVP fixture |
| `evaluation/configs/` | Fail-closed locked TabPFN runtime template, frozen Gemini smoke manifest, and versioned website Gemini profile |
| `tests/` | Unit, leakage, statistical, agent-behavior, and integration gates |
| `third_party/TabCF` | Authoritative upstream source pinned at `76e0d3eb9e97cebca381d1540db0333c1ef1016e` |
| `requirements-dev.lock`, `requirements-ui.lock`, `requirements-managed-client.lock`, `requirements-website-demo.lock`, `requirements-gemini.lock`, `requirements-zerogpu.lock` | Python 3.11 local locks plus the exact direct Python 3.12 ZeroGPU dependencies |
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
and one explicitly confirmed local CSV route through the existing typed agent
state machine. `csv_upload.py` accepts exactly three mapped numeric Y/X/Z
columns, 120–256 rows, no extras/W, finite values, and continuous Y/X presentation
checks before any Client call. The managed profile requires exact
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

`agent/gemini_live.py` adds one separate Track A mechanics smoke. The frozen
manifest binds `google-genai==2.18.1`, stable model `gemini-3.6-flash`, prompt,
JSON schema, model settings, one-request limit, symbolic clean-case proposal,
and list-price rates. The request contains no rows or actual intervention
values. A schema-valid proposal must exactly match the frozen expected
specification before the existing deterministic compiler/runtime can run. The
saved trace records the prompt/model/source identities, API interaction ID,
token usage, latency, list-price estimate, proposal, and evidence-linked query;
its verifier rebinds the trace to the manifest and independently validates the
underlying analysis directory without another model call or refit. This one
clean smoke is not the paired 24-case live Track A comparison. The original
authenticated smoke request was rejected because it included the removed
top-level `response_mime_type`; the implementation now follows the unified
`response_format` contract. The separately versioned website profile has since
completed an authenticated standard-CSV compile and managed analysis.

## Verified commands

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest
.venv/bin/dcfa --help
.venv-managed/bin/dcfa managed-agent-smoke --token-file <outside-repo-file> --output-dir <fresh-directory>
.venv-gemini/bin/dcfa gemini-agent-smoke --api-key-file <outside-repo-file> --output-dir <fresh-directory>
.venv/bin/dcfa verify-gemini-agent-smoke <run-directory>
.venv/bin/dcfa verify-artifacts <run-directory>
.venv/bin/dcfa verify-agent-benchmark <benchmark-json>
python -m dcfa_showcase verify showcase/prepared_demo_v1
```

See the README for complete runnable examples. A smoke test proves mechanics,
not statistical quality or release readiness.

The website demo is deliberately separate from the evidence-bound statistical
runtime. `dcfa_website_demo/gemini.py` makes one structured
`gemini-3.6-flash` call per UI run using a versioned prompt/model/schema profile.
It sends only the natural-language question, generic Y/X/Z contract, and
symbolic intervention labels. The validated proposal selects a mean or median
summary/contrast; local deterministic code maps labels to actual values, and
Gemini never sees rows or calculates the result. Clarification, block, API,
schema, or credential failures stop with no retry or non-LLM fallback.

The local demo accepts synthetic TabCF-IV scenarios plus a strictly bounded, locally
selected Y/X/Z CSV and uses the managed `tabpfn-client` profile. Its explicit
presentation mappings project approved claim, support, warning, and error
semantics from the validated query while unknown codes fail closed. The visitor
plot is derived from the validated bundle; the original identity-rich report,
plot, evidence ledger, and agent/LLM audit remain artifact-only. The default DOM
receives no trace, specification/bundle/evidence IDs, backend error context, or
service metadata. There is no Hillstrom, W, general-router, or sklearn fallback
route. For CSV runs, Gemini maps the three locally inspected header names from
the question plus optional exact-name overrides; a dynamic enum schema and local
validation reject invented, duplicate, or conflicting roles. No upload event
mutates role controls. CSV confirmation distinguishes question/header transfer
to Google from selected rows sent to Prior Labs. The approved public architecture
uses the stored replay and user-owned Colab workflow below rather than this local
service.

The website projection is result-first: an approved Gemini symbolic proposal is
matched to the validated query to phrase a direction-aware answer without
recomputing its value. The visitor then sees only support, mapped warnings, and
the development-only limitation. A four-stage progress projection marks
completed/current/pending/blocked states, locates blocked requests with a safe
next action, and never exposes state reasons or tool counts. Gradio generator
events hide native percentage progress, disable both submit buttons during a
run, and use a live result status; the initial answer/detail components remain
hidden rather than displaying duplicate placeholders. The input uses a wider
desktop column while the workflow and result share one sticky companion panel;
the columns stack without horizontal overflow on narrow viewports. The local
service and native ZeroGPU entrypoint consume the same `build_demo_theme()` and
`DEMO_CSS` launch configuration instead of maintaining separate visual defaults.

`dcfa_website_demo.service` mounts the queued Gradio app on a single-worker
FastAPI service and exposes `/healthz` plus output-path- and credential-aware
`/readyz`; readiness requires the versioned Gemini profile and both external
mode-600 service credential files. Startup preflights the configured port so an
older process cannot silently represent the current source, and the page shows a
short Git/build revision for browser acceptance. UI run directories are reserved
atomically and never overwrite prior material. The container runs as UID 10001,
stores generated artifacts under a dedicated volume, disables Gradio monitoring
and public sharing, and remains a local deployment artifact rather than a public
release authorization.

The public portfolio path is a separate stored projection. `dcfa_showcase`
freezes the exact prompt, redistributable synthetic CSV, profiles, source hash,
and DCFA release commit before one live run. Export first invokes the independent
full-artifact verifier, reconstructs the typed bundle and evidence ledger, renders
the visitor plot from that validated pair, and writes only human-readable support,
warning, answer, release, and asset-hash fields. Its offline verifier rejects
source/profile drift, asset tampering, private paths, credential-like strings,
machine audit identifiers, or visitor rounding that no longer matches the raw
verified value.

`dcfa_colab` reuses the strict CSV ingress and typed managed runtime without
starting Gradio or any tunnel. It checks both user-owned secret values and two
separate transfer confirmations before provider construction or output allocation,
writes credentials only to owner-only temporary files, resets the managed client,
independently verifies successful artifacts, scans them for both secret byte
strings, and creates a path-safe downloadable ZIP. The committed notebook pins a
full DCFA commit and source-tree hash, has no saved outputs, and documents runtime
cleanup. These presentation paths remain `development_only` and add no evidence
track.

## Unresolved inputs and decisions

- immutable Torch/TabPFN container image and image digest for locked Track T evidence;
- manuscript/predecessor artifacts for upstream `A*`/`B*` DGP mapping;
- approved Fulton local data and usage/license note;
- approved Hillstrom raw data, exact source/hash, and usage/license decision;
- calibrated and frozen diagnostic thresholds for a locked Track T protocol;
- a frozen paired live-LLM protocol for the full fixed-workflow versus agent
  case suite; the Gemini smoke and website profiles do not cover that comparison.

These gaps block the corresponding release claims. They do not authorize a
silent fallback, fabricated manifest, or reinterpretation of local synthetic
artifacts.
