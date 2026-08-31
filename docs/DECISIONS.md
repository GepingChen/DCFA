# Architecture and protocol decisions

Use this as an append-only, human-readable decision log. Record decisions that
change architecture, statistical protocol, data access, evaluation, stable
commands, or public claims. Routine implementation details belong in code and
tests instead.

For each new entry include: date, status, decision, rationale, affected tracks,
alternatives considered, verification or migration impact, and source/approval.
Do not rewrite an accepted entry when it changes; append a superseding entry.

## D-001 — Separate the three evidence tracks

- Date: 2026-08-08
- Status: Accepted by integrated research plan v2.0
- Decision: Report TabCF estimator evidence, Hillstrom policy evidence, and agent
  workflow evidence as separate tracks with explicit labels.
- Rationale: The designs have different treatment structures, identification
  assumptions, oracles, and valid conclusions.
- Affected tracks: T, H, A
- Verification impact: Reports and evidence records must carry a track label.
- Source: `plan/TabCF_Agent_Integrated_Research_Plan_ZH.md`, sections 0 and 5.

## D-002 — Keep two statistical adapters isolated

- Date: 2026-08-08
- Status: Accepted by integrated research plan v2.0
- Decision: Share the runtime, schemas, evidence, audit, errors, and reporting,
  while keeping the TabCF IV and Hillstrom policy adapters isolated.
- Rationale: Sharing engineering contracts is valid; pretending the statistical
  designs are interchangeable is not.
- Affected tracks: T, H, A
- Rejected alternative: A general LLM-selected causal-method router.
- Verification impact: Add boundary tests and ensure the public product exposes
  only the TabCF adapter.
- Source: plan sections 0.5, 1.4, 3.1, and 12.1.

## D-003 — Build deterministic vertical slices before orchestration

- Date: 2026-08-08
- Status: Accepted by integrated research plan v2.0
- Decision: Verify actual TabCF APIs, then implement deterministic TabCF and
  Hillstrom vertical slices before adding the LLM agent runtime.
- Rationale: Statistical behavior, evidence construction, and leakage controls
  must be independently testable and held fixed in the agent comparison.
- Affected tracks: T, H, A
- Verification impact: Each vertical slice must run end to end without an LLM.
- Source: plan sections 14 and 19.

## D-004 — Require evidence-linked numerical claims

- Date: 2026-08-08
- Status: Accepted by integrated research plan v2.0
- Decision: Block any numerical causal answer whose evidence ID does not resolve
  to the exact data, specification, tool/model version, unrounded value, support
  status, warnings, and source artifact.
- Rationale: Auditability and exact numerical fidelity are hard release gates.
- Affected tracks: T, H, A
- Verification impact: Unit, integration, reporting, and agent-behavior tests must
  exercise both valid and invalid evidence paths.
- Source: plan sections 3.4, 11, 12.3, and 13.

## D-005 — Defer canonical commands until the toolchain exists

- Date: 2026-08-08
- Status: Accepted repository bootstrap decision
- Decision: Do not claim install, lint, test, evaluation, or application commands
  are stable until dependency metadata and executable entry points are checked in
  and verified.
- Rationale: The current repository contains no implementation or dependency
  file, so invented commands would create false handoff confidence.
- Affected tracks: Repository-wide
- Verification impact: Update `docs/CODEBASE_MAP.md` and `AGENTS.md` as soon as
  real stable commands exist.
- Source: Direct repository inspection on 2026-08-08.

## D-006 — Pin the authoritative TabCF source as a submodule

- Date: 2026-08-08
- Status: Accepted for repository preparation
- Decision: Track `https://github.com/GepingChen/TabCF.git` at
  `third_party/TabCF` as a Git submodule. The initial inspected commit is
  `76e0d3eb9e97cebca381d1540db0333c1ef1016e`.
- Rationale: The upstream `tabcf_core` is script-first and not distributed as an
  installable package. Pinning the source preserves exact provenance and avoids
  copying or silently rewriting the statistical core.
- Affected tracks: T and the shared reproducibility boundary used by A.
- Alternatives considered: copying only `tabcf_core` into DCFA, reimplementing
  the estimator, or depending on an unpinned checkout. These would respectively
  break upstream layout assumptions, duplicate statistical logic, or lose
  reproducibility.
- Verification impact: Fresh clones must initialize the submodule. The DCFA
  adapter must bind the submodule commit in model/run/evidence metadata and use
  a thin import/process boundary until upstream exposes a package.
- Source: User authorization to prepare `tabcf_core` and direct inspection of the
  public TabCF repository on 2026-08-08.

## D-007 — Exclude baseline covariates from TabCF v1

- Date: 2026-08-08
- Status: Accepted by user
- Decision: TabCF Analyst v1 accepts exactly one outcome, one continuous
  treatment, one scalar instrument, and no baseline covariates `W`. A
  non-empty baseline-covariate role returns
  `UNSUPPORTED_BASELINE_COVARIATES` before Stage 1; the system may not drop
  `W`.
- Rationale: The inspected upstream core implements `F(X | Z)` and
  `F(Y | X,V)`, while a conditioned `W` path would require
  unverified statistical changes.
- Affected tracks: T and TabCF cases in A.
- Verification impact: Add schema, unit, integration, and agent-behavior tests
  for the empty-covariate invariant and fail-closed path.
- Source: User direction on 2026-08-08; integrated plan v2.1.

## D-008 — Permit an explicit macOS development fallback

- Date: 2026-08-08
- Status: Accepted by user for temporary development
- Decision: A deterministic `sklearn_quantile_fallback` may implement the
  distribution contract in the explicit macOS local-development profile.
  Fallback artifacts are `development_only`, may not be called TabCF, and
  may not enter locked Track T results. TabPFN failures never trigger automatic
  fallback.
- Rationale: The current macOS environment aborts while importing its installed
  PyTorch, which blocks local TabPFN execution but need not block schema,
  evidence, state-machine, cache, or report mechanics.
- Affected tracks: Local engineering for T and A; no change to publishable Track
  T statistical claims.
- Verification impact: Bind backend and execution profile in specifications,
  evidence, and manifests; test deterministic fallback CDF/quantile coherence,
  typed TabPFN-load failure, and release rejection of fallback evidence.
- Migration impact: A later version must repair macOS TabPFN or provide a pinned
  reproducible remote Linux/GPU runner, then rerun Track T before release.
- Source: User direction and local environment verification on 2026-08-08;
  integrated plan v2.1.

## D-009 — Promote verified local commands from bootstrap status

- Date: 2026-08-08
- Status: Accepted by implementation verification; supersedes D-005 for the
  commands listed in the README and codebase map
- Decision: Treat the locked local install, lint, test, CLI, artifact verifier,
  and optional UI commands as stable development commands.
- Rationale: Installable metadata, exact local locks, executable entry points,
  and tests now exist and have been run in a repository-local Python 3.11 venv.
- Affected tracks: Repository-wide
- Rejected alternative: Continue describing executable code as bootstrap-only.
- Verification impact: Re-run the full tests, Ruff, clean-process imports,
  artifact verifier, and `git diff --check` after boundary changes.
- Source: Direct implementation and local verification on 2026-08-08.

## D-010 — Enforce Hillstrom freeze-before-test in code

- Date: 2026-08-08
- Status: Accepted implementation of integrated plan v2.1
- Decision: Fit preprocessing/nuisance models on training, select thresholds on
  validation, refit on training plus validation, serialize a content-addressed
  policy, and only then unlock test outcomes for the matching dataset/split.
- Rationale: A narrative split convention is insufficient to prevent leakage.
- Affected tracks: H and Hillstrom cases in A
- Alternatives considered: Pass test arrays through the policy learner and rely
  on caller discipline, or select a threshold after viewing test value. Both are
  rejected.
- Verification impact: Leakage tests require disjoint/full split coverage,
  split-scoped preprocessing, policy identity checks, and audit event ordering.
- Source: Integrated plan sections 7.3, 12.4, and 13.2.

## D-011 — Do not auto-download Fulton or Hillstrom data

- Date: 2026-08-08
- Status: Accepted pending explicit data-use decisions
- Decision: Real-data loaders require a user-provided local file, exact source,
  retrieval date, raw hash, and usage/license note. DCFA does not download or
  redistribute these datasets automatically.
- Rationale: Fulton package metadata is GPL-3, but the Rdatasets archive warns
  that licenses for the underlying rows may be unclear. The official Hillstrom
  challenge is traceable, but no explicit dataset license/usage decision was
  supplied to this repository.
- Affected tracks: T-Real and H-Real
- Verification impact: Missing provenance fails before file access or model fit;
  generated fixtures remain clearly `development_only`.
- Source: Upstream repository inspection; the official
  [wooldridge package metadata](https://cran.r-project.org/package=wooldridge),
  [Rdatasets license warning](https://github.com/vincentarelbundock/Rdatasets),
  and [MineThatData challenge page](https://blog.minethatdata.com/2008/05/best-answer-e-mail-analytics-challenge.html),
  verified on 2026-08-08.

## D-012 — Bind locked TabPFN to model and image hashes

- Date: 2026-08-08
- Status: Accepted release-integrity requirement
- Decision: A locked TabPFN host must match exact Python/package versions, the
  pinned upstream commit, a checkpoint path and SHA-256, and a container image
  digest before import or fit.
- Rationale: Package availability or model agreement does not establish runtime
  identity or reproducibility.
- Affected tracks: T and live end-to-end A
- Rejected alternative: Use `model_path=auto`, download a checkpoint at runtime,
  or infer the environment from package imports.
- Verification impact: The checked-in manifest is a fail-closed template with
  required placeholders; release validation also requires the backend manifest.
- Source: Integrated plan freeze/reproducibility gates and local TabPFN probe.

## D-013 — Keep the public UI TabCF-only and lazy

- Date: 2026-08-08
- Status: Accepted product boundary implementation
- Decision: The public Gradio shell exposes only the no-W continuous-IV
  development workflow. Gradio loads only when the UI is built; Hillstrom,
  Torch, and TabPFN are absent from ordinary app-module imports.
- Rationale: The public product has one causal design and must not become a
  general method router or accidentally initialize unavailable backends.
- Affected tracks: TabCF Analyst product surface and T
- Verification impact: Clean-process tests assert lazy import and Hillstrom
  isolation; UI results preserve fallback/evidence markers.
- Source: Integrated plan sections 0.5, 3.1, and Week 6.

## D-014 — Version complete semi-synthetic metrics without oracle leakage

- Date: 2026-08-08
- Status: Accepted implementation of integrated plan v2.1
- Decision: Hillstrom semi-synthetic protocol v2 reports the complete planned
  metric vector, including action confusion, abstention coverage, selective
  regret, fallback-inclusive value, action-gap calibration error, and
  constraint violations. Capacity truncation for learned comparators ranks rows
  by fitted action values; true conditional utilities are used only to construct
  the constrained oracle and score policies.
- Rationale: Using known potential-outcome utilities to implement a learned
  comparator would leak the oracle into policy construction and bias the
  benchmark. Selective regret is defined against the row-wise unconstrained best
  action among non-fallback decisions; overall regret remains relative to the
  same-capacity oracle.
- Affected tracks: H-Semi-synthetic only
- Verification impact: Preserve v1 artifacts, write v2 to a new run directory,
  require 84 evidence-linked aggregates across four scenarios, assert confusion
  mass and nonnegative regret, and independently verify the artifact hashes.
- Source: Integrated plan section 7.8 and implementation leakage audit on
  2026-08-08.

## D-015 — Make Track A safety grading gold-aware

- Date: 2026-08-08
- Status: Accepted implementation correction
- Decision: Track A recorded protocol v2 counts a numerical answer as forbidden
  whenever the gold state requires clarification or blocking, even if the
  evaluated system incorrectly labels its own state as completed. It also
  reports per-case mean and worst-run success, between-run disagreement, failure
  taxonomy, explicit metric-vector fields, complex-case primary comparison, and
  seeded case-bootstrap intervals.
- Rationale: Conditioning the safety count on the system's reported final state
  misses exactly the failure where an unsafe workflow completes when it should
  stop. Repeated runs remain nested within case and are never treated as
  independent tasks.
- Affected tracks: A only
- Verification impact: Bind the output to the exact case-file hash, preserve
  both systems' raw traces, assert zero gold-aware forbidden numbers for the
  full runtime, and expose unavailable live-model/Policy-track metrics as not
  evaluated rather than assigning favorable zeros.
- Source: Integrated plan sections 8.6-8.8 and 9.1-9.6; implementation safety
  audit on 2026-08-08.

## D-016 — Bind every saved run to its backend manifest

- Date: 2026-08-08
- Status: Accepted evidence-integrity correction
- Decision: Saved Track H policy v2, Hillstrom semi-synthetic v3, and Track T
  development-evaluation v2 runs use the content ID of a persisted backend
  manifest in their run identity and run manifest. Backend manifests include
  protocol, DCFA tool, NumPy, scikit-learn, model-contract, and relevant policy
  identities. The independent verifier recomputes this ID and requires exact
  run/spec/data/bundle/evidence/report-manifest linkage.
- Rationale: A backend name or ad hoc version string does not prove which tool
  contract produced a number. The previous verifier could detect file changes
  but did not independently close every identity edge in the evidence graph.
- Affected tracks: T development artifacts and H; the existing typed TabCF
  backend manifest already used content-addressed identity.
- Verification impact: Preserve earlier local result directories, generate new
  versioned directories, require a one-to-one bundle/evidence ID mapping, and
  fail on any backend, run, specification, dataset, source, or report-manifest
  mismatch.
- Source: Repository evidence rules and implementation provenance audit on
  2026-08-08.

## D-017 — Make Track H audits and report propagation executable

- Date: 2026-08-08
- Status: Accepted implementation correction; supersedes D-016 protocol labels
  for newly generated local artifacts
- Decision: Hillstrom policy protocol v3 rejects missing/non-finite values,
  records a baseline-feature/randomized-assignment H0 audit without reading test
  outcomes, and carries frozen costs, capacity, test-row count, action counts and
  proportions, warnings, and assumptions into the validated bundle and report.
  Semi-synthetic v4 and Track T development-evaluation v3 reports likewise
  preserve assumptions. The verifier requires reported uncertainty, warnings,
  assumptions, action allocations, and balance diagnostics to agree with the
  hashed bundle.
- Rationale: Keeping these values only in a numerical core or policy artifact
  leaves the human-readable report incomplete and weakens the same-bundle
  guarantee. Strict missingness rejection avoids an undocumented imputation
  policy in the MVP.
- Affected tracks: H and development-only T reporting
- Verification impact: Add non-finite input, H0 audit, operational allocation,
  backend-ID tamper, report-propagation, and independent artifact checks; write
  results to new versioned directories without replacing earlier runs.
- Source: Integrated plan sections 7.6 and 7.8 plus repository evidence and
  warning-propagation rules; final implementation audit on 2026-08-08.

## D-018 — Make local result paths immutable

- Date: 2026-08-08
- Status: Accepted repository safety implementation
- Decision: Every deterministic run rejects an output directory that already
  contains material, and standalone benchmark/probe writers reject any existing
  destination. The public UI allocates monotonically numbered run directories.
- Rationale: Replacing a prior result can conceal negative outcomes, break hash
  provenance, and make a rerun appear cleaner than it was.
- Affected tracks: T, H, A, and the local UI
- Verification impact: Add an `OUTPUT_PATH_EXISTS` typed error and a regression
  test proving that a repeated run preserves the prior report hash.
- Source: Repository Git/collaboration and data-freeze rules.

## D-019 — Bind local evidence to the exact uncommitted source tree

- Date: 2026-08-08
- Status: Accepted provenance hardening; supersedes D-017 protocol labels for
  newly generated local artifacts
- Decision: Every backend and recorded benchmark manifest includes a SHA-256 of
  the relative paths and bytes of all `src/dcfa/**/*.py` files. The current
  verifier requires this hash to match the executing source tree. Current
  protocols are Hillstrom policy v4, Hillstrom semi-synthetic v5, Track T
  development evaluation v4, and Track A recorded v3; ordinary TabCF run IDs
  change through their typed backend-manifest content ID.
- Rationale: `dcfa==0.1.0` and the outer base commit do not uniquely identify an
  uncommitted implementation. A source-tree digest provides exact local code
  identity without pretending that the work has been committed.
- Affected tracks: T, H, and A
- Verification impact: Regenerate results in new immutable paths and fail
  independent verification when the backend/benchmark was produced by a
  different DCFA source tree.
- Source: Repository evidence requirement to bind tool version and final
  provenance audit on 2026-08-08.

## D-020 — Recompute input and evidence identities at every release boundary

- Date: 2026-08-08
- Status: Accepted integrity hardening; supersedes D-019 protocol labels for
  newly generated local artifacts
- Decision: Before fitting, TabCF recomputes the hash of the supplied Y/X/Z
  arrays and Hillstrom recomputes the hash of all raw columns; Track H also
  validates actual arm-stratified 60/20/20 membership. Strict TabCF support now
  covers the entire immutable intervention grid before Stage 2. Evidence IDs,
  audit IDs, specification/backend/split/policy/run/bundle IDs, and deterministic
  numerical-core projections are independently recomputed during validation.
  Locked model/image identifiers require exact 64-hex SHA-256 values and the
  executing host must present the frozen image digest before import. Current
  protocols are Hillstrom policy v5, Hillstrom semi-synthetic v6, Track T
  development evaluation v5, and Track A recorded v4.
- Rationale: Comparing only declared hashes or saved file hashes allows stale
  raw data, forged content IDs, ignored specification fields, or a rewritten
  bundle/report to retain superficially consistent labels. The strengthened
  graph binds current inputs to the numerical core and every reported number.
- Affected tracks: T, H, and A
- Alternatives considered: Trust dataclass type hints, accept nonempty digest
  placeholders, or treat the run-manifest file hash list as sufficient. These
  do not independently establish content or execution identity.
- Verification impact: Add fail-before-fit data/manifest tests, whole-grid
  support tests, real split-stratification tests, superseded-spec rejection,
  evidence/audit/content-ID tamper tests, and core-to-bundle aggregate
  recomputation. Regenerate all outputs in new immutable paths.
- Source: Integrated plan evidence, freeze, leakage, and hard-gate rules plus
  final requirement-level audit on 2026-08-08.

## D-021 — Keep the portfolio demo outside the statistical source boundary

- Date: 2026-08-10
- Status: Accepted presentation architecture; not a deployment authorization
- Decision: The website-oriented Gradio shell lives in the separate
  `dcfa_website_demo` package. It calls the existing typed compiler, state
  machine, deterministic analysis tool, and evidence validator, but does not
  change `src/dcfa` or enter the statistical source-tree hash. It exposes only
  frozen synthetic TabCF-IV scenarios and has no upload or Hillstrom route. The
  static Astro personal site receives a reusable iframe component and will not
  link it until a reviewed HTTPS service exists.
- Rationale: Pure presentation work must not invalidate evidence-bound
  statistical artifacts, while GitHub Pages cannot host the Python runtime.
- Affected tracks: TabCF Analyst public presentation only; no new Track T, H, or
  A evidence
- Verification impact: Assert lazy imports and Hillstrom isolation, test a
  completed evidence-linked path and an outside-support no-number path, verify
  wide/mobile rendering, and keep the current fallback labels visible. A final
  public endpoint still requires the locked real TabPFN and deployment review.
- Source: Integrated plan sections 0.5, 14, 15, 17, and 18; current static-site
  deployment boundary.

## D-021 — Rebind recorded traces to frozen cases during verification

- Date: 2026-08-10
- Status: Accepted evidence-integrity correction
- Decision: Independent Track A verification requires each raw trace's family,
  fixture behavior, expected final state, and expected tool-call bound to equal
  its frozen case definition. It then recomputes numerical fidelity, grader
  failures, and valid completion from the same deterministic grading function
  used during benchmark generation.
- Rationale: Recomputing aggregate tables from raw traces detects summary-only
  edits, but it does not detect a self-consistent rewrite of both traces and
  aggregates. The case manifest and grading rules are the independent gold
  boundary.
- Affected tracks: A only
- Verification impact: Add regression tests that rewrite frozen case metadata
  or grader outcomes, regenerate current source-bound artifacts in new immutable
  paths, and retain recorded protocol v4 because benchmark generation and its
  estimand are unchanged.
- Source: Integrated plan sections 8.4, 8.8, and 12.5 plus repository evidence
  invariants.

## D-022 — Isolate managed TabPFN as a fixed development smoke

- Date: 2026-08-12
- Status: Accepted development integration; not a locked Track T backend
- Decision: Add a separate `tabpfn-client==0.3.3` backend profile that is
  reachable only through a fixed 128-row synthetic agent smoke. Pin model
  `v2.5_default`, one estimator, and thinking mode off; cap row counts; batch
  Stage-2 predictions; require observed service package metadata; preserve
  service trace IDs; and disallow silent fallback or arbitrary file input.
- Rationale: The managed API can validate authenticated client, distributional
  output, typed agent routing, evidence, and artifact mechanics on this Mac
  without pretending that an opaque service runtime is a locally reproducible
  TabPFN installation.
- Affected tracks: Development mechanics for the public TabCF Analyst only. It
  establishes no Track T statistical result and does not change the recorded
  Track A comparison protocol.
- Verification impact: Require exact managed parameters and development status,
  test the NumPy bar-distribution CDF, assert three prediction calls for the
  full synthetic run, record observed service metadata in audit, independently
  verify the resulting artifact, and keep the locked release gate closed
  because checkpoint and runtime-image hashes are unavailable.
- Source: Integrated plan sections 5, 6, 8, 10, and 13; inspected
  `tabpfn-client` 0.3.3 and TabPFN 8.0.8 distribution contracts.

## D-023 — Package the portfolio shell as a bounded development service

- Date: 2026-08-13
- Status: Accepted local deployment implementation; not public release authorization
- Decision: Serve the website demo through one queued Gradio worker mounted on
  a health-checkable ASGI app. Reserve immutable run directories atomically,
  reject out-of-range controls before execution, run the container as a non-root
  user, persist only the ignored local artifact directory, and keep the visible
  `development_only / sklearn_quantile_fallback / not TabCF` boundary.
- Rationale: A repeatable local service needs operational checks and concurrent
  request safety, while adding a deployment wrapper must not change the
  evidence-bound statistical runtime or imply that fallback output is releasable.
- Affected tracks: TabCF Analyst local presentation only; no Track T, H, or A
  evidence changes.
- Verification impact: Require real end-to-end strong, weak, and support-block
  tests; atomic allocation and invalid-control tests; health and security-header
  checks; non-root container health; and desktop/mobile browser review.
- Source: User-authorized continuation of the development workflow demo and D-021.

## D-024 — Use managed TabPFN for the bounded local website demo

- Date: 2026-08-13
- Status: Accepted development integration; supersedes D-023's website-backend choice
- Decision: Route the three fixed synthetic website scenarios through the
  `tabpfn-client==0.3.3` managed TabPFN backend, pinned to `v2.5_default`, one
  estimator, and thinking mode off. Cap website inputs at 256 rows, keep full
  distribution predictions below the 400-row service limit, require an external
  mode-600 token file, and fail closed without any sklearn substitution. Use a
  combined website lock and make readiness depend on both artifact storage and
  credential-file validity.
- Rationale: The user requires actual TabPFN mechanics in the local demo. The
  existing managed distribution adapter already satisfies the TabCF Stage 1/2
  contract, while the sklearn presentation path no longer meets that goal.
- Affected tracks: TabCF Analyst local presentation and development mechanics
  only; no locked Track T, H, or A evidence changes.
- Verification impact: Exercise all three website paths with a contract-faithful
  fake service, assert managed backend identity and no-number blocking, validate
  the combined dependency lock, then run one bounded authenticated synthetic
  website scenario and independently verify its artifact.
- Source: User request on 2026-08-13; inspected `tabpfn-client` 0.3.3 API and
  Prior Labs regression/metering documentation.

## D-025 — Permit a consent-gated local CSV route in the website demo

- Date: 2026-08-13
- Status: Accepted local presentation extension; not a general upload service
- Decision: Add one local website route for a user-selected CSV with exactly
  three explicitly mapped numeric columns: continuous outcome Y, continuous
  treatment X, and scalar instrument Z. Accept 120–256 rows, reject extra
  columns rather than silently dropping potential W, require finite values and
  at least 20 distinct Y/X values, and require a visible authorization and
  Prior Labs transmission confirmation before managed-client access. Send only
  the three accepted role columns, bind them to the canonical dataset hash and
  a development-only manifest, and retain the exact D-024 TabPFN profile with no
  sklearn fallback.
- Rationale: A bounded local CSV makes the first end-to-end agent demo concrete
  while preserving the v1 no-W scope, data-transmission boundary, and typed
  evidence flow. Strict rejection is preferable to silently interpreting extra
  user fields or presenting this development service as a general real-data
  causal analysis product.
- Affected tracks: TabCF Analyst local presentation and development mechanics
  only; no locked Track T, H, or A evidence changes.
- Verification impact: Test the standard CSV through the full typed runtime,
  reject missing consent, extra columns, and discrete treatment before Client
  access, execute one authenticated browser upload, and independently verify the
  resulting artifact. Keep all outputs `development_only` because the managed
  checkpoint and runtime-image identities remain unavailable.
- Source: User-authorized local CSV demonstration request on 2026-08-13 and the
  existing TabCF v1 no-W, evidence, and managed-service boundaries.

## D-026 — Add a one-request Gemini Track A mechanics smoke

- Date: 2026-08-13
- Status: Accepted development integration; corrected live request not yet verified
- Decision: Add a separate one-request Gemini compiler smoke using
  `google-genai==2.18.1`, stable model `gemini-3.6-flash`, the Interactions API,
  medium thinking, structured JSON output, and a frozen clean synthetic prompt.
  Send only the prompt, Y/X/Z role contract, and symbolic intervention labels;
  do not send rows or actual intervention values. Require the proposal to match
  the frozen expected specification before mapping labels to locally calculated
  grid values and calling the existing deterministic state machine. Never retry
  the Gemini request or fall back after an API or output-validation failure.
- Rationale: One bounded live request verifies credential, SDK, prompt,
  structured-output, model-metadata, token, latency, typed-routing, and evidence
  mechanics without allowing the LLM to perform hidden numerical arithmetic or
  claiming that one clean case establishes agent superiority.
- Affected tracks: Track A development mechanics only. The underlying
  statistical result remains `local_development / sklearn_quantile_fallback /
  development_only` and is not Track T evidence.
- Verification impact: Pin the complete Python environment; validate an
  external mode-600 key file; test one-call/no-retry behavior, malformed output,
  key permissions, lazy SDK import, evidence agreement, and trace tampering;
  independently verify the saved trace and deterministic analysis without a
  second model call. A paired fixed/full live benchmark remains blocked on a
  separately frozen protocol.
- Initial live result: The one authorized request on 2026-08-13 returned HTTP
  400 before analysis because the implementation supplied the removed top-level
  `response_mime_type`. Official May 2026 migration guidance confirmed that MIME
  type belongs only inside unified `response_format`. The obsolete field was
  removed and the corrected request passes offline SDK serialization; no second
  network request was made without renewed authorization.
- Source: User authorization on 2026-08-13; integrated plan sections 8.1, 8.6,
  8.8, and 12.5; Google Gemini model, structured-output, usage, and pricing
  documentation inspected on 2026-08-13.

## D-027 — Make Gemini the default bounded compiler for the local website demo

- Date: 2026-08-15
- Status: Accepted development integration; live website request not yet verified
- Decision: Before every guided or authorized CSV website run, make exactly one
  structured `gemini-3.6-flash` request using the versioned
  `website_demo_gemini_v1` profile. Send only the user question, generic Y/X/Z
  role contract, and symbolic low/center/high labels. Permit mean and median
  summaries or directed contrasts only. Map labels to actual interventions in
  deterministic local code, then run the unchanged managed TabPFN and evidence
  pipeline. Require separate repository-external mode-600 Gemini and Prior Labs
  credentials; never retry or silently bypass either service.
- Rationale: The local product demo should expose real LLM-based specification
  compilation rather than present a preconstructed `CompilationRequest` as an
  LLM agent. Keeping the LLM upstream of deterministic numerical tools preserves
  numerical fidelity, support gates, evidence IDs, and the no-data-row Gemini
  boundary.
- Affected tracks: Local TabCF Analyst presentation and development mechanics
  only. This is not the paired Track A evaluation and does not make managed
  output eligible for locked Track T claims.
- Verification impact: Test that the proposal changes the deterministic query,
  requests use unified structured output once with `store=false`, no rows or
  actual interventions enter the Gemini trace, API failures stop before managed
  fitting, successful runs persist a non-secret compilation trace, and readiness
  fails unless both external credentials are valid.
- Source: User request on 2026-08-15 and integrated plan sections 3.2, 8.3,
  8.6, 12.5, and 13.4.

## D-028 — Repair the website Gemini request for the Developer API

- Date: 2026-08-19
- Status: Accepted compatibility repair; authenticated CSV rerun verified
- Decision: Omit the optional `labels` request metadata because the Gemini
  Developer API rejects it as Enterprise-only, and raise the bounded structured
  output budget from 384 to 1024 tokens so medium thinking leaves enough room
  for the required JSON object. Accept a completed stateless response without a
  server interaction ID and record that field as null instead of weakening the
  `store=false` privacy boundary; the local trace remains content-addressed.
  Preserve the model, prompt, response schema, one-request limit, symbolic
  intervention contract, and all deterministic numerical and evidence gates.
  The profile's content hash records the repaired request exactly.
- Rationale: An authenticated website CSV run failed before analysis on the
  unsupported `labels` field. After removing it, a diagnostic request used 366
  thought tokens and exhausted the former output budget, returning an incomplete
  interaction after only 14 visible output tokens. Neither failure reached the
  managed TabPFN service or emitted a numerical result.
- Affected tracks: Local TabCF Analyst presentation and development mechanics
  only; no locked Track T, H, or A protocol changes.
- Verification impact: Assert the Developer API request has no `labels`, retains
  unified structured output, uses the repaired token budget, and accepts the
  observed completed stateless response without an ID; rerun the full website
  integration test and one authenticated standard-CSV workflow, then independently
  verify the resulting artifact.
- Source: User-requested CSV plus language-prompt demo verification on
  2026-08-19; current `google-genai==2.18.1` SDK behavior and authenticated
  Gemini Developer API responses.

## D-029 — Version the managed demo profile for TabPFN service 8.3.0

- Date: 2026-08-19
- Status: Accepted development-profile update; authenticated full rerun verified
- Decision: Replace `tabpfn_client_managed_demo_v1`, which fails closed on the
  retired service package 8.0.8, with `tabpfn_client_managed_demo_v2`, which
  still pins `tabpfn-client==0.3.3`, model `v2.5_default`, one estimator,
  thinking mode off, and now requires observed service package 8.3.0. Retain
  the exact NumPy CDF implementation and all row, metadata, evidence, and
  development-only gates.
- Rationale: The managed service now reports package 8.3.0 and correctly caused
  v1 to block before a numerical answer. The official PyPI wheels for 8.0.8 and
  8.3.0 have SHA-256 values `b6c945c8bf23b86f595697fcfa4ce58d84105441baf7e1313edc7865d7d29658`
  and `650f16b7bc8df2e3218d47a221216c93bc3b6aca7bb2aeb6ea1ab05405768ddc`.
  Direct source comparison found the complete `FullSupportBarDistribution.cdf`
  method byte-for-byte identical and confirmed that full regression output
  retains the probability-to-logit and borders/logits contract used by DCFA.
- Affected tracks: Local TabCF Analyst presentation and managed development
  mechanics only. Prior v1 artifacts remain immutable and development-only; no
  locked Track T, H, or A result is promoted or replaced.
- Verification impact: Update fake-service metadata tests to 8.3.0, run unit
  and integration suites for the managed adapter and website demo, then execute
  and independently verify one fresh authenticated standard-CSV v2 artifact.
- Authenticated result: The fixed 128-row standard CSV completed one Gemini
  compile and three managed predictions with no retry. Independent artifact
  verification returned `status=valid` for result bundle
  `bundle_e4c5af51bae899cbcf213711` and evidence
  `evidence_545dc49741f6e4c6b1d9223f`; the result remains development-only and
  preserves its empirical warnings.
- Source: User-requested CSV demonstration on 2026-08-19; authenticated Prior
  Labs metadata and source inspection of official `tabpfn` 8.0.8 and 8.3.0
  wheels.

## D-030 — Separate the website visitor projection from machine audit artifacts

- Date: 2026-08-19
- Status: Accepted local presentation boundary; Phase 0 implemented
- Decision: Keep the default website language English and remove the complete
  agent/audit JSON plus evidence handles from the visitor page. Project every
  allowed claim type, support state, warning, and blocked error through explicit
  human-readable mappings; any unknown code suppresses the number and visitor
  plot. Apply three-significant-digit rounding only in the visitor projection,
  while preserving the evidence-bound raw and six-significant-digit values in
  artifacts. Generate a separate visitor plot from the validated result bundle
  and leave the original identity-rich audit plot unchanged. Show a short build
  revision and fail clearly when the configured local port is already occupied.
- Rationale: A closed accordion is not an information boundary, and formatting
  internal enums cannot supply stable product language. Two projections from one
  validated bundle let a visitor understand the result without weakening the
  evidence ledger, warning semantics, support gate, or independent verifier.
- Affected tracks: Local TabCF Analyst presentation only. No Track T, H, or A
  evidence, statistical estimator, Gemini request, managed TabPFN request, or
  release protocol changes.
- Verification impact: Exhaustively test the presentation maps and unknown-code
  behavior; scan strong, weak, blocked, input, and service-failure visitor output
  plus the default Gradio config for internal codes/IDs/trace fields; verify
  visitor-to-ledger value parity, both plot files, artifact validation, port
  conflict reporting, page build identity, full pytest, Ruff, format, and browser
  views at desktop and 390 px.
- Source: User-requested Phase 0 implementation of
  `plan/Website_Demo_UI_UX_Optimization_Plan_ZH.md` on 2026-08-19.

## D-031 — Make the website result-first and project four visitor stages

- Date: 2026-08-19
- Status: Accepted local presentation behavior; Phase 1 implemented
- Decision: Lead a successful visitor result with one direction-aware sentence
  derived from the validated query value and the already validated symbolic
  Gemini proposal. Follow it only with data support, important mapped warnings,
  and the development-only limitation. Replace raw workflow events with four
  visitor stages—understand the question, check the data, run the analysis, and
  verify the result—using completed, current, pending, and blocked states. A
  blocked state names its visitor stage and safe next action. Hide empty answer
  and detail components before the first run, disable both submit buttons during
  execution, suppress native percentage progress, and announce the final status
  through a live region. Keep the guided and CSV transfer summaries visible
  before their respective submit actions.
- Rationale: The local demo should answer the visitor's question before exposing
  method detail, while the runtime remains auditable and fail closed. Symbolic
  proposal labels supply direction and treatment wording but never replace the
  evidence-bound numerical value. A small exhaustive progress projection makes
  waiting and blocked states understandable without leaking state reasons,
  request metadata, or tool counts.
- Affected tracks: Local TabCF Analyst presentation only. No estimator,
  diagnostic threshold, support gate, evidence record, Gemini request, managed
  TabPFN request, retry policy, or Track T/H/A evidence changes.
- Verification impact: Test direction-aware answer phrasing and unknown-label
  fallback, all four progress stages, blocked-stage mapping, mutually exclusive
  initial/running/success/error states, submit-button locking, visitor redaction,
  weak/outside-support preservation, and desktop plus 390 px browser layouts.
- Source: User-requested Phase 1 implementation of
  `plan/Website_Demo_UI_UX_Optimization_Plan_ZH.md` on 2026-08-19.

## D-032 — Publish a static prepared replay and move custom execution to user-owned Colab

- Date: 2026-08-19
- Status: Static replay and public Colab CTA released; clean provider execution not repeated
- Decision: Supersede the unimplemented Hugging Face/public-service direction with
  two explicit paths. GitHub Pages receives one hash-bound, precomputed synthetic
  replay with no runtime, provider client, credential input, storage, or inference.
  Custom CSV analysis runs only inside a visitor's own Colab notebook, which pins
  the approved DCFA commit, uses the visitor's Colab Secrets, requires separate
  Google-question and Prior-Labs-row transfer confirmations, and returns an
  independently verified downloadable artifact. The local Gradio service remains
  a local operator workflow and is not embedded or publicly hosted.
- Rationale: A static replay is stable, zero-cost at replay time, and compatible
  with GitHub Pages. User-owned notebook execution removes owner key/quota/storage
  exposure without disguising Colab as a public application server or weakening
  the existing typed runtime.
- Affected tracks: TabCF Analyst public presentation only. Prepared and Colab
  results remain `local_development / tabpfn / development_only`; no Track T, H,
  or A evidence is created or promoted.
- Verification impact: Freeze prompt/CSV/profile/source identity before the live
  run; independently verify the full artifact; require raw-value, warning,
  support, and plot projection parity; reject tampering and private content;
  statically validate a full-commit-pinned, output-free notebook; test missing
  secrets/consents before provider construction; and prove the static site has no
  provider dependency or request path.
- Platform review: Current official documentation still describes GitHub Pages as
  static hosting, Colab as interactive notebook compute with unguaranteed limits
  and restrictions on bypassing the notebook UI, Gemini keys as protected caller
  credentials, and `tabpfn-client` as a cloud service that receives user data and
  consumes request credits.
- Source: Approved
  `plan/GitHub_Pages_Colab_Public_Demo_Release_Plan_ZH.md` v2.0 and user request to
  implement that plan on 2026-08-19.

## D-033 — Permit a development-only public ZeroGPU template with local TabPFN v2

- Date: 2026-08-30
- Status: Accepted implementation direction; live ZeroGPU acceptance pending
- Decision: Add a native Gradio Space that runs the permissively hosted TabPFN v2
  regression checkpoint on Hugging Face ZeroGPU. The canonical public Space requires
  Hugging Face login and exposes only three synthetic presets compiled from one frozen
  typed median-contrast proposal, with no live LLM call. Natural-language compilation
  and bounded CSV upload are enabled only after a visitor duplicates the Space and adds
  their own `DCFA_GEMINI_API_KEY` Secret. CSV rows remain in the duplicated Hugging Face
  runtime and are never sent to Prior Labs. Every run remains
  `local_development / tabpfn / development_only`, fails closed, and uses no sklearn or
  managed-client fallback.
- Rationale: Free ZeroGPU now provides a bounded public execution path, while TabPFN
  v2's Prior Labs License permits hosted use with prominent attribution. TabPFN 2.5 and
  2.6 explicitly prohibit a hosted service without a separate commercial license and
  are excluded. Requiring caller-owned Gemini Secrets avoids collecting keys in the
  canonical browser or charging an owner key.
- Affected tracks: TabCF Analyst public presentation only. This decision supersedes
  D-032 only for the newly authorized live Space; the prepared replay and user-owned
  Colab remain available and no Track T, H, or A evidence is created.
- Verification impact: Pin and hash-check the public v2 checkpoint before import; pin
  Python, Torch, TabPFN, Gradio, and the DCFA commit; require OAuth before GPU work;
  independently verify every completed artifact; scan downloadable archives for the
  Gemini Secret; delete uploaded files and uncompressed run directories; test the
  canonical no-LLM mode separately from the duplicate BYOK mode; and retain the locked
  runtime release gate because ZeroGPU supplies no immutable container image digest.
- Source: User-approved ZeroGPU implementation plan and the inspected Prior Labs v2 and
  v2.5 model licenses on 2026-08-30.
