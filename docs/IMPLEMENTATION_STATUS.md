# DCFA implementation status

Last updated: 2026-08-19

## Overall status

All repository-scoped macOS CPU implementation and verification work that can
be completed without inventing a research protocol, acquiring unapproved data,
or fabricating a locked model/runtime is complete for the current scope. A
bounded managed TabPFN Client path now exercises one fixed smoke request, three
website-demo presets, and an explicitly confirmed local Y/X/Z CSV route through
the typed agent runtime, but it is development mechanics rather than a locked
Track T run. A frozen Gemini profile implements one clean synthetic compile
smoke, while a separate versioned Gemini profile now compiles every local
website-demo question into a bounded mean or median summary/contrast before the
deterministic managed TabPFN runtime. The original authenticated smoke was
rejected before analysis by a removed API parameter; the corrected website
profile has since completed authenticated analysis. A hash-bound prepared replay
and a user-owned Colab workflow are implemented outside the statistical source
boundary. Publishable Track T,
real-data Track T/H, and the paired live-model Track A comparison remain
explicitly blocked on the external inputs listed below.

Current executable source identity:
`sha256:e1c86e9e7bd470f6f6e5c9d5ef9beaad8161e653355002d4ca47555484879791`.
This is the hash of relative paths and bytes for every `src/dcfa/**/*.py` file,
independent of the outer Git commit identity.

Current protocols:

- public TabCF specification: `tabcf_iv_v1`;
- managed-client demo: `tabpfn_client_managed_demo_v2`;
- Hillstrom policy: `hillstrom_policy_v5`;
- Hillstrom semi-synthetic: `hillstrom_semisynthetic_v6`;
- Track T fallback development evaluation:
  `track_t_development_evaluation_v5`;
- recorded Track A: `track_a_recorded_v4` with case manifest
  `track_a_cases_v1`;
- Gemini live smoke: `track_a_gemini_live_smoke_v1`.
- website Gemini compiler: `website_demo_gemini_v1`.
- prepared public replay: `prepared_demo_v1` / `dcfa_prepared_visitor_v1`;
- Colab custom workflow: DCFA release commit
  `87b2b750d1c9a83497f5b16a7b0597758214d20a`.

## Requirement coverage

| Boundary | Implemented and locally verified | Honest limitation |
|---|---|---|
| Shared runtime | Immutable typed schemas, typed errors, content-addressed evidence, append-only audit, validated cache, atomic output, immutable result paths, source hashing, and independent artifact verification | No release claim follows from mechanics alone |
| TabCF scope | Exactly one continuous treatment, one continuous outcome, one scalar IV, and no `W`; unsupported treatments, role conflicts, unconfirmed specs, malformed grids, data/manifest hash mismatches, and nonempty `W` fail before backend construction or fit | Conditional `W` extension and general method routing are intentionally absent |
| TabCF deterministic slice | Explicit fallback or TabPFN backend selection; Stage 1 control rank; empirical diagnostics; whole-grid strict support gate before Stage 2; Stage 2 distribution/mean paths; CDF, means, quantiles, risks, and directed contrasts from one core | Local sklearn output is `development_only`, is not TabCF, and cannot enter locked Track T |
| Managed TabPFN demo | Exact `tabpfn-client==0.3.3` profile; fixed synthetic and confirmed exact-Y/X/Z CSV website routes; default one-call Gemini compiler; strict 120–256-row/no-W gates; batched predictions; service/LLM trace metadata; transport-safe CDF; evidence-linked immutable artifacts | `development_only`; question text goes to Google and selected CSV rows go separately to Prior Labs; no LLM or sklearn fallback; service checkpoint/image hashes are unavailable, so this cannot enter locked Track T |
| Locked TabPFN boundary | Lazy imports, no automatic fallback, pinned upstream commit, exact model/image SHA-256 validation, current-host image-digest check, package/runtime manifest validator, and release rejection of fallback evidence | No working local Torch/TabPFN/checkpoint/image is available; the bounded probe was not repeated |
| Track T development evaluation | Strong/weak engineering scenarios, exact DCFA-fixture oracle metrics, three frozen seeds in the current artifact, seed-level aggregation, warnings, assumptions, evidence, and independent recomputation | Not mapped to manuscript DGP codes; not a locked 12-cell study, estimator ranking, diagnostic calibration, or publishable TabCF result |
| Fulton | Provenance-required 97-row schema loader and development-only workflow command | No approved local CSV or usage decision was supplied; no Fulton result was run |
| Track H data/leakage | Exact raw-column hash, provenance/schema/missingness/action checks, real arm-stratified 60/20/20 verification, preprocessing-scope hashes, content-addressed split/policy, and matching-policy test gate | Current run uses generated RCT data, not Hillstrom |
| Track H policy | Training-only fit, validation-only best-uniform/threshold selection, train+validation refit, immutable policy freeze before test access, DR primary plus IPW/direct sensitivity, paired contrasts, randomized-arm effects, costs/capacity/allocation, 95% influence-score intervals, warnings, assumptions, and release gate | No approved real file, final one-time test run, real held-out policy value, or individual oracle claim |
| H semi-synthetic | Four prespecified DGPs, training-covariate resampling, same-constraint oracle, 50 replications per scenario, value/regret/accuracy/confusion/abstention/selective-regret/fallback/calibration/constraint metrics, and 84 evidence records | Covariates come from a development fixture, so the result is explicitly not Hillstrom-calibrated |
| Track A | Explicit state machine/compiler/runtime; 24-case recorded benchmark; bounded Gemini 3.6 Flash clean-case implementation; frozen prompt/model/schema; no-row symbolic input; token/latency/list-price trace contract; evidence agreement verifier | The first live request failed before analysis on a removed API field; corrected serialization is offline-only, and no paired live fixed/full comparison exists |
| Public UI | Local Gradio operator shell plus a released hash-bound static prepared replay and pinned user-owned Colab notebook; the static path has no provider/runtime/storage code, while Colab preserves one-call/no-fallback, consent, evidence, and secret-scan gates | Static Pages replay is live; public Colab/GitHub CTAs are withheld because anonymous notebook-source access returns 404. Changing repository visibility or using a public mirror needs explicit authorization, then a clean Colab runtime QA |

The independent artifact verifier now checks saved file hashes and also
recomputes protocol versions, marker contracts, source identity,
specification/backend/split/policy/run/bundle/evidence/audit IDs, raw identity
cross-links, deterministic core-to-bundle projections, report evidence values,
uncertainty fields, warnings, assumptions, allocations, and balance diagnostics.
For Track A it also rebinds every raw trace to the frozen case definition and
recomputes the deterministic grader outcome. It never refits a model.

## Preserved independently verified artifacts

All paths below are ignored local artifacts and were created in fresh locations;
no earlier artifact was overwritten. They were valid against the exact source
snapshot recorded at creation, spanning source hashes `b401226d...`, `03c2b585...`,
and `c47d1a06...`. They are preserved evidence, not current-source artifacts:
the current verifier intentionally rejects them against `e1c86e9e...` rather
than silently treating an older run as current. No corrected Track A Gemini
smoke artifact exists because that authorized request stopped before analysis;
the separate prepared website run below did complete.

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
| `artifacts/local/website-demo-managed-live-v1/strong_iv/seed-20260813/run-0002` | `run_bb8a5a565c7b6d38caf297d2` / `bundle_eae050d60c35ecf11135d565` | 1 evidence record; 3 service predictions | valid; live managed TabPFN website path, development-only |
| `artifacts/local/website-demo-csv-browser-v1/csv-upload-4ba1adb3e0d8/seed-20260813/run-0001` | `run_bb8a5a565c7b6d38caf297d2` / `bundle_eae050d60c35ecf11135d565` | 1 evidence record; 3 service predictions | valid; browser-uploaded standard CSV, same canonical fixture/specification, development-only |
| `artifacts/local/prepared-demo-v1-release-87b2b750/strong_iv/seed-20260813/run-0001` | `run_4e08cc245c27a61264c1edd6` / `bundle_e4c5af51bae899cbcf213711` | 1 evidence record; 1 Gemini compile; 3 service predictions | valid; source for static `prepared_demo_v1`, development-only |

The bounded local-installation TabPFN probe remains
`artifacts/local/tabpfn-probe-20260808.json`. It recorded
`ModuleNotFoundError: torch` and `fallback_attempted: false`. The separate
managed-client run above succeeded without converting the service into a local
or hash-locked runtime.

## Verification evidence

Prior snapshot checks on macOS with Python 3.11.13:

```text
.venv/bin/ruff check src tests                         passed
.venv/bin/ruff format --check src tests                66 files already formatted
.venv/bin/python -m pytest                             91 passed in 38.81s
.venv/bin/python -m pip check                          no broken requirements
.venv-managed clean lock install + managed tests       6 passed; no broken requirements
.venv/bin/dcfa --help                                  passed
managed authenticated agent smoke                     completed; 3 predictions; 0 retries
managed artifact independent verification             status=valid
managed client cache after reset                       absent
clean core import                                      no gradio/torch/tabpfn/Hillstrom pipeline
Gradio build_app                                       Blocks constructed
website demo integration tests                        13 passed; guided/CSV paths + service
managed website authenticated run                     completed; 3 predictions; 0 retries
managed website artifact verification                 status=valid
managed CSV direct + browser-upload runs               completed; both artifacts status=valid
combined website lock clean install                   no broken requirements
Gradio browser QA                                     real CSV upload; 1280px/390px; no overflow/errors
Gradio development callbacks                           fresh strong/weak valid; support blocked
ASGI liveness/readiness                                200; output/token ready
Docker image/container                                 rebuilt; non-root 10001:10001; healthy/ready
container strong artifact                              completed; independent status=valid
seven artifact/benchmark verifier commands             valid against recorded snapshots
```

Current website Gemini integration checks:

```text
.venv/bin/ruff check src tests                         passed
.venv/bin/ruff format --check src tests                80 files already formatted
.venv/bin/python -m pytest                             119 passed in 45.17s
website and Gemini behavior tests                      26 passed
combined website lock install + pip check              no broken requirements
default external credentials                          both present, mode 0600
ASGI liveness/readiness                                200; output + profile + both credentials ready
Gradio browser QA                                     390px; editable questions; no overflow/errors
Gemini website request shape                          one call; store=false; unified response_format
Gemini website data boundary                          zero rows; zero actual intervention values
Gemini API failure                                    no retry; no managed fit/output/fallback
Gemini proposal routing                               mean proposal changed deterministic query
website artifact after Gemini trace                   independent status=valid
Gemini fake-client behavior tests                      7 passed; one-call/no-retry/tamper gates
Gemini authenticated smoke                            HTTP 400; no retry; no analysis/artifact
prepared authenticated website run                    completed; 1 Gemini + 3 predictions; 0 retries
prepared full artifact verification                   status=valid
prepared public projection verification               status=valid; release sha256:4b686a1e...
Colab notebook static validation                       output-free; exact release/source pin
Docker/Compose after dual-secret change                not verified; Docker CLI unavailable
```

Final handoff checks after documentation edits:

```text
git diff --check                                      passed
trailing-whitespace scan                              no matches
private-key/AWS/GitHub/OpenAI credential-pattern scan no matches
outer branch                                          main...origin/main
nested third_party/TabCF branch                       clean main...origin/main
nested TabCF commit                                   76e0d3eb9e97cebca381d1540db0333c1ef1016e
final statistical source-tree hash                     sha256:e1c86e9e7bd470f6f6e5c9d5ef9beaad8161e653355002d4ca47555484879791
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
5. **Live Track A:** extend the one-case Gemini mechanics profile into a separately
   frozen fixed/full protocol with identical models, prompts, permissions, tools,
   and cases; freeze the grader and production repetitions before running. The
   prepared website run is not this comparison, and the recorded case suite still
   reports comparative live-model and policy-track metrics as unevaluated.

Smoke tests and generated fixtures do not establish estimator quality,
coverage, identification, business lift, release readiness, or individual
optimal treatment. Negative, null, deferred, and blocked results remain visible.

## Next authorized step

For the public website tool, the next decision is explicit authorization either
to make `GepingChen/DCFA` anonymously readable or to use a versioned public
mirror. After that, run one clean Google Colab walkthrough with the user's own
Secrets before restoring the CTA. The static GitHub Pages replay is already
deployed and hash-verified. For a comparative live Track A result, the
next step remains a frozen paired Gemini
fixed-workflow/full-agent protocol and grader over the 24 cases.
For publishable estimator evidence, the highest-priority path remains the frozen
TabPFN runtime plus manuscript DGP mapping. Repeating either current one-case
smoke under new names would add no research evidence.
