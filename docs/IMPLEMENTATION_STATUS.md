# DCFA implementation status

Last updated: 2026-08-13

## Overall status

All repository-scoped macOS CPU implementation and verification work that can
be completed without inventing a research protocol, acquiring unapproved data,
or fabricating a locked model/runtime is complete for the current scope. A
bounded managed TabPFN Client path now exercises one fixed synthetic request
through the typed agent runtime, but it is development mechanics rather than a
locked Track T run. Publishable Track T, real-data Track T/H, and live-model
Track A remain explicitly blocked on the external inputs listed below.

Current executable source identity:
`sha256:03c2b585b2eb852087412257745875865c5a45c91b50a8cc3b5daedef405c9d9`.
This is the hash of relative paths and bytes for every `src/dcfa/**/*.py` file,
independent of the outer Git commit identity.

Current protocols:

- public TabCF specification: `tabcf_iv_v1`;
- managed-client smoke: `tabpfn_client_managed_smoke_v1`;
- Hillstrom policy: `hillstrom_policy_v5`;
- Hillstrom semi-synthetic: `hillstrom_semisynthetic_v6`;
- Track T fallback development evaluation:
  `track_t_development_evaluation_v5`;
- recorded Track A: `track_a_recorded_v4` with case manifest
  `track_a_cases_v1`.

## Requirement coverage

| Boundary | Implemented and locally verified | Honest limitation |
|---|---|---|
| Shared runtime | Immutable typed schemas, typed errors, content-addressed evidence, append-only audit, validated cache, atomic output, immutable result paths, source hashing, and independent artifact verification | No release claim follows from mechanics alone |
| TabCF scope | Exactly one continuous treatment, one continuous outcome, one scalar IV, and no `W`; unsupported treatments, role conflicts, unconfirmed specs, malformed grids, data/manifest hash mismatches, and nonempty `W` fail before backend construction or fit | Conditional `W` extension and general method routing are intentionally absent |
| TabCF deterministic slice | Explicit fallback or TabPFN backend selection; Stage 1 control rank; empirical diagnostics; whole-grid strict support gate before Stage 2; Stage 2 distribution/mean paths; CDF, means, quantiles, risks, and directed contrasts from one core | Local sklearn output is `development_only`, is not TabCF, and cannot enter locked Track T |
| Managed TabPFN smoke | Exact `tabpfn-client==0.3.3` profile; fixed 128-row synthetic data; typed agent route; three batched prediction calls; observed service package/trace metadata; transport-safe bar-distribution CDF; evidence-linked immutable artifact | `development_only`; no arbitrary upload; service checkpoint/image hashes are unavailable, so this cannot enter locked Track T |
| Locked TabPFN boundary | Lazy imports, no automatic fallback, pinned upstream commit, exact model/image SHA-256 validation, current-host image-digest check, package/runtime manifest validator, and release rejection of fallback evidence | No working local Torch/TabPFN/checkpoint/image is available; the bounded probe was not repeated |
| Track T development evaluation | Strong/weak engineering scenarios, exact DCFA-fixture oracle metrics, three frozen seeds in the current artifact, seed-level aggregation, warnings, assumptions, evidence, and independent recomputation | Not mapped to manuscript DGP codes; not a locked 12-cell study, estimator ranking, diagnostic calibration, or publishable TabCF result |
| Fulton | Provenance-required 97-row schema loader and development-only workflow command | No approved local CSV or usage decision was supplied; no Fulton result was run |
| Track H data/leakage | Exact raw-column hash, provenance/schema/missingness/action checks, real arm-stratified 60/20/20 verification, preprocessing-scope hashes, content-addressed split/policy, and matching-policy test gate | Current run uses generated RCT data, not Hillstrom |
| Track H policy | Training-only fit, validation-only best-uniform/threshold selection, train+validation refit, immutable policy freeze before test access, DR primary plus IPW/direct sensitivity, paired contrasts, randomized-arm effects, costs/capacity/allocation, 95% influence-score intervals, warnings, assumptions, and release gate | No approved real file, final one-time test run, real held-out policy value, or individual oracle claim |
| H semi-synthetic | Four prespecified DGPs, training-covariate resampling, same-constraint oracle, 50 replications per scenario, value/regret/accuracy/confusion/abstention/selective-regret/fallback/calibration/constraint metrics, and 84 evidence records | Covariates come from a development fixture, so the result is explicitly not Hillstrom-calibrated |
| Track A | Explicit state machine/compiler/runtime, clarification/approval/block/retry-once/evidence/cache behavior, identical recorded tools for fixed workflow and full runtime, 24 cases, five nested runs, gold-aware safety grading, case-bound trace verification, per-case/worst-run/disagreement/failure taxonomy, and seeded case bootstrap | This is deterministic orchestration evidence, not a live LLM comparison; live latency/tokens/cost and Hillstrom policy cases are unevaluated |
| Public UI | Lazy Gradio Blocks app, TabCF-only routing, no Hillstrom/Torch/TabPFN import on the core path, atomically reserved immutable run directories, bounded queue and controls, evidence-linked values/plot, mobile layout, liveness/readiness endpoints, non-root container and local Compose profile | Development workflow demonstration only; no public HTTPS deployment and not release-eligible |

The independent artifact verifier now checks saved file hashes and also
recomputes protocol versions, marker contracts, source identity,
specification/backend/split/policy/run/bundle/evidence/audit IDs, raw identity
cross-links, deterministic core-to-bundle projections, report evidence values,
uncertainty fields, warnings, assumptions, allocations, and balance diagnostics.
For Track A it also rebinds every raw trace to the frozen case definition and
recomputes the deterministic grader outcome. It never refits a model.

## Current independently verified artifacts

All paths below are ignored local artifacts and were created in fresh locations;
no earlier artifact was overwritten.

| Artifact | Identity | Evidence/result size | Status |
|---|---|---:|---|
| `artifacts/local/smoke-v4` | `run_e5c1ce8bc37022d74b1ec3aa` / `bundle_dfe07e54c995b7d728ceab09` | 3 evidence records | valid; strong-IV development fallback |
| `artifacts/local/weak-v4` | `run_2ee57ef016db78f0ce48a837` / `bundle_9330b46f5d8b3050ec400b1d` | 3 evidence records | valid; warning-preserving weak-IV development fallback |
| `artifacts/local/hillstrom-smoke-v6` | `hillstrom_run_f838f8d8397bd46c20d7cc60` / `policy_bundle_64fc146bb3c329956dacb147` | 31 evidence records | valid; generated RCT mechanics only |
| `artifacts/local/hillstrom-semisynthetic-v7` | `semisynth_run_7a8db6e67f6f23a4a7c451aa` / `semisynth_bundle_a9a3515715c845b45accfb29` | 4 scenarios x 50 replications; 84 evidence records | valid; development synthetic, not Hillstrom-calibrated |
| `artifacts/local/track-t-development-evaluation-v6` | `track_t_dev_run_88a5905393051e1d6100d36f` / `track_t_dev_bundle_1a6b4a3bb4a4e64fd9a7c4e0` | 2 scenarios x 3 seeds; 10 evidence records | valid; fallback engineering benchmark, not TabCF |
| `artifacts/local/agent-benchmark-recorded-v5.json` | `track_a_benchmark_7a9f5d47de217cfa7dd46a5e` | 24 cases x 5 runs x 2 systems = 240 traces | valid; `test_only` recorded orchestration evidence |
| `artifacts/local/ui/spec_b913cb89bcd0ed43f01ada67/run-0002` | same strong-IV run/bundle identity as `smoke-v4` | 3 evidence records | valid UI callback artifact |
| `artifacts/local/managed-agent-smoke-v1` | `run_9c4e6fcde2e09f931fa70e89` / `bundle_9357d0fa4628082b83048c47` | 1 evidence record; 3 service predictions | valid; fixed synthetic managed TabPFN mechanics only |

The bounded local-installation TabPFN probe remains
`artifacts/local/tabpfn-probe-20260808.json`. It recorded
`ModuleNotFoundError: torch` and `fallback_attempted: false`. The separate
managed-client run above succeeded without converting the service into a local
or hash-locked runtime.

## Verification evidence

Verified on macOS arm64 with Python 3.11.13:

```text
.venv/bin/ruff check src tests                         passed
.venv/bin/ruff format --check src tests                65 files already formatted
.venv/bin/python -m pytest                             86 passed in 37.23s
.venv/bin/python -m pip check                          no broken requirements
.venv-managed clean lock install + managed tests       6 passed; no broken requirements
.venv/bin/dcfa --help                                  passed
managed authenticated agent smoke                     completed; 3 predictions; 0 retries
managed artifact independent verification             status=valid
managed client cache after reset                       absent
clean core import                                      no gradio/torch/tabpfn/Hillstrom pipeline
Gradio build_app                                       Blocks constructed
website demo integration tests                         8 passed; all three real paths + service
Gradio browser QA                                      1280px/390px; no overflow or console issues
Gradio development callbacks                           fresh strong/weak valid; support blocked
ASGI liveness/readiness                                200; output path writable
Docker image/container                                 non-root 10001:10001; healthy
container strong artifact                              completed; independent status=valid
seven current artifact/benchmark verifier commands     all status=valid
```

Final handoff checks after documentation edits:

```text
git diff --check                                      passed
trailing-whitespace scan                              no matches
private-key/AWS/GitHub/OpenAI credential-pattern scan no matches
outer branch                                          main...origin/main
nested third_party/TabCF branch                       clean main...origin/main
nested TabCF commit                                   76e0d3eb9e97cebca381d1540db0333c1ef1016e
final source-tree hash                                 sha256:03c2b585b2eb852087412257745875865c5a45c91b50a8cc3b5daedef405c9d9
```

Repository policy now requires every completed, verified, in-scope change to be
committed and pushed on the current branch after an explicit-path staging and
sensitive-data review. This standing authorization does not extend to history
rewrites, tags, PRs, releases, deployments, or publication.

## External blockers and unverified claims

1. **Locked Track T runtime:** the managed client proves API mechanics only.
   Supply a real TabPFN package/checkpoint, exact checkpoint SHA-256, frozen
   Linux/GPU image digest, exact package versions, and a host that validates
   against the checked-in runtime contract.
2. **Track T research protocol:** supply the TabCF manuscript/predecessor
   materials needed to map the planned T1/T2/O1/O2/O3 labels to inspected
   upstream `A*`/`B*` implementations, then freeze development/final seeds,
   diagnostic thresholds, required baseline configuration, and report
   templates. The current hard-coded diagnostic thresholds are development
   warnings only.
3. **Fulton:** provide an approved local raw CSV, exact source/retrieval date,
   raw hash, and project-approved usage/license note.
4. **Hillstrom:** provide an approved raw file plus the same provenance/usage
   decision, then freeze the real split, policy protocol, and one-time locked
   test evaluation before claiming real policy value or Hillstrom-calibrated
   semi-synthetic evidence.
5. **Live Track A:** select and freeze the LLM, prompt, model settings, grader
   manifest, permissions, and cost/latency collection. The current case suite
   intentionally reports live-model and policy-track metrics as unevaluated.

Smoke tests and generated fixtures do not establish estimator quality,
coverage, identification, business lift, release readiness, or individual
optimal treatment. Negative, null, deferred, and blocked results remain visible.

## Next authorized step

For one genuinely live AI-agent test, the next required decision is a selected
LLM/API, prompt, model settings, permissions, and cost/latency manifest. For
publishable estimator evidence, the highest-priority path remains the frozen
TabPFN runtime plus manuscript DGP mapping. Repeating the current fixed managed
smoke under new names would add no research evidence.
