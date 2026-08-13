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
