# DCFA repository operating rules

These instructions apply to the entire repository. A more deeply nested
`AGENTS.md`, if one is added later, may refine local implementation details but
must not weaken the research-integrity, evidence, leakage, or safety rules here.

## Start every task here

1. Run `git status --short --branch` and preserve unrelated or uncommitted work.
2. Read `README.md`, this file, and the relevant part of
   `plan/TabCF_Agent_Integrated_Research_Plan_ZH.md`.
3. Read `docs/IDENTIFICATION_BOUNDARIES.md`, `docs/CODEBASE_MAP.md`, and
   `docs/DECISIONS.md` when the task touches research design, architecture, data,
   evaluation, or claims.
4. Inspect the actual code, tests, dependency files, and public APIs before
   proposing an implementation. Never invent a `tabcf_core` class, function,
   file layout, dataset location, or command from the plan.
5. Name the affected evidence track and define a small, verifiable success
   criterion before editing.

Authority for intended research behavior is the integrated plan plus any later
explicitly frozen protocol manifest. Authority for current executable behavior
is the checked-in code and tests. If they disagree, stop, document the mismatch,
and ask for a protocol decision; do not silently make one source match the other.

## Project identity and scope lock

DCFA has one public product, three evidence tracks, and one shared auditable
runtime:

| Area | Purpose | What it may establish |
|---|---|---|
| TabCF Analyst | Public continuous-treatment distributional-IV workflow | Bounded, evidence-linked IV analysis |
| Track T | TabCF synthetic and real-data evaluation | Estimator operating characteristics; real-data demonstration without oracle truth |
| Track H | Hillstrom real RCT and semi-synthetic evaluation | Frozen policy value; semi-synthetic oracle regret |
| Track A | Fixed workflow versus full agent | Incremental workflow reliability with statistical tools held fixed |

Non-negotiable boundaries:

- Do not implement a general causal-method router.
- Do not send binary or multi-arm treatments through the continuous-treatment
  TabCF adapter.
- Do not encode Hillstrom's three randomized actions as a continuous treatment.
- Do not describe Hillstrom as validation of TabCF.
- Do not let the public TabCF Analyst session access the Hillstrom policy adapter.
- Do not rewrite the TabCF statistical core unless an inspected, reproducible
  defect blocks the adapter and the user authorizes that scope.
- TabCF v1 has no baseline covariates `W`; reject a non-empty covariate
  role before Stage 1 and never drop it silently.
- A macOS `sklearn_quantile_fallback` is allowed only when explicitly
  selected by a local-development profile. Its outputs are not TabCF evidence
  and cannot enter locked Track T results.
- Do not add causal discovery, automatic IV discovery, invalid-IV repair, or
  high-risk autonomous policy deployment to v1.

## Architecture invariants

- Keep `tabcf_iv` and `hillstrom_policy` as isolated statistical adapters.
- Share only typed schemas, evidence, audit, error semantics, reporting, and the
  explicit agent runtime.
- Keep every numerical causal calculation inside deterministic, testable tools.
  The LLM may compile a specification, choose an allowed tool, route on typed
  status, and explain validated evidence; it may not calculate headline values.
- Use an explicit state machine. Variable roles, estimands, objectives,
  constraints, policies, and support decisions must not change silently.
- Retry a recoverable tool failure at most once unless a frozen protocol says
  otherwise. After that, take the typed fallback or stop with a visible reason.
- Ordinary follow-ups must query a cached validated result bundle rather than
  refitting.

Implementation order:

1. Repository/API reconnaissance and `docs/CODEBASE_MAP.md`.
2. Shared schemas, typed errors, evidence, and audit.
3. Deterministic TabCF vertical slice and support/diagnostic gates.
4. Deterministic Hillstrom policy-value vertical slice and leakage tests.
5. Explicit agent state machine and compiler.
6. Fixed-workflow/full-agent benchmark using identical tools and fixtures.
7. Semi-synthetic evaluation, UI, and report artifacts.

Do not add LLM orchestration merely to compensate for a missing deterministic
contract.

## Evidence and claim rules

- No numerical causal claim may appear without a resolvable evidence ID.
- An evidence record must bind the value to the exact data hash, immutable
  specification, tool and model version, result bundle, unrounded value, units,
  support status, warnings, and source artifact.
- Text, tables, cards, and plots must be derived from the same validated result
  bundle. Never read a headline number from a plot or copy it manually.
- Evidence validation failure blocks the numerical answer or release.
- Preserve support, weak-IV, uncertainty, cost, and identification warnings
  through every transformation and report.
- Describe relevance, residual-dependence, rank, and support checks as empirical
  diagnostics. They do not prove instrument validity or identification.
- Label every reported result by track. Keep synthetic, semi-synthetic, real-data,
  and agent-benchmark claims distinct.
- Preserve negative, null, deferred, and abstention results. Do not tune the
  protocol to obtain favorable lift or agent superiority.

## Data, splits, and protocol freezes

- Treat raw or licensed data as immutable inputs. Record provenance, license or
  access notes, hashes, schemas, and transformation versions in manifests.
- Keep secrets, tokens, private data, local model caches, and sensitive traces out
  of Git. Use ignored local paths and commit only schemas, tiny public fixtures,
  manifests, or explicitly approved derived artifacts.
- For Hillstrom, keep train, validation, and test indices disjoint. Fit
  preprocessing only on allowed data and never expose test outcomes before the
  policy is frozen.
- Randomized assignment is not an individual optimal-action label. On real
  Hillstrom data, report average policy value, not individual counterfactual
  correctness or oracle regret.
- Compare fixed workflow and full agent with the same data, estimator, model,
  tool permissions, fixtures or seeds, and tool outputs. Agent ablations may not
  alter the statistical estimator; statistical ablations may not alter prompts
  or routing at the same time.
- Respect the three freeze stages: development, threshold, and final. After final
  freeze, any change to prompts, cases, seeds, policies, tools, thresholds, model
  versions, or report templates creates a new version. Never overwrite a frozen
  result.
- Record seeds, split IDs, configuration IDs, package lock, model and prompt
  versions, commit SHA, and artifact hashes for every final run.

## Coding practices

- Prefer small typed modules, deterministic functions, explicit CLIs, and
  inspectable data flow over notebooks, hidden global state, or broad frameworks.
- Use English for identifiers, code comments, docstrings, schemas, and error
  messages. Research prose may be English or Chinese when the target artifact
  requires it.
- Use `pathlib`, type hints, dataclasses or validated schemas where they clarify
  contracts. Avoid speculative abstractions and compatibility layers.
- Keep random-number generation explicit and seeded. Pass generators or seeds
  through configuration rather than relying on ambient global state.
- Fail closed on unsupported treatments, missing roles, outside-support
  interventions, stale IDs, hash mismatches, evidence mismatches, leakage risk,
  or ambiguous high-consequence requests.
- Do not silently fall back between statistical models, from GPU to CPU, from a
  real backend to a fake backend, or from a failed estimator to a heuristic.
- Keep generated outputs separate from source. Do not commit datasets,
  checkpoints, caches, logs, local environments, or bulk traces.
- Match existing style and make surgical changes. Do not refactor unrelated code.

## Verification expectations

Run the smallest relevant checks during development, then the full available
suite for the affected boundary. Until a dependency file and stable commands are
checked in, do not invent canonical commands; update this section and
`docs/CODEBASE_MAP.md` when they become real.

Required test categories as implementation appears:

- Unit: CDF range/monotonicity, quantile inversion, contrast direction, evidence
  resolution, warning propagation, hashes, DR hand calculations, propensity,
  costs, constraints, fallback determinism, and immutable specifications.
- Leakage: disjoint splits, preprocessing scope, freeze-before-test-access,
  outcome exclusion, report isolation, and frozen prompt/threshold manifests.
- Statistical: simple known DGPs, Monte Carlo tolerances, paired intervals,
  feasible/constrained oracle comparisons, nonnegative regret, and exact parity
  between direct deterministic tools and agent-returned bundles.
- Agent behavior: clarification, refusal, approval, outside-support blocking,
  one-retry recovery/stop, stale IDs, hash/evidence mismatch, warning retention,
  cached follow-up, and no hidden numerical arithmetic.
- Integration: each deterministic vertical slice must work without an LLM before
  its agent wrapper is considered complete.

A smoke test proves mechanics only. It does not establish statistical quality,
coverage, policy improvement, or release readiness.

## Release gates

Any hard-gate failure blocks release; do not average it away. In particular,
release requires zero unsupported TabCF treatment execution, outside-support
causal claims, pre-freeze Hillstrom test-outcome access, post-treatment features,
silent role changes, constraint violations, or real-Hillstrom individual-optimum
claims. It also requires zero silent backend fallbacks and zero
development-fallback artifacts in Track T headline results, plus complete
numerical evidence coverage, evidence/tool agreement, warning preservation, and
correct track labels.

Soft performance misses may be published as negative results with a failure
analysis. They are not permission to change the frozen protocol after seeing the
test results.

## Git and collaboration

- This repository has standing user authorization to commit and push every
  completed, verified, in-scope change. Do not leave finished work only in the
  local worktree merely because the user did not repeat `commit` or `push` in
  the current request.
- The standing authorization covers an ordinary commit on the current branch
  followed by a non-force push to its configured upstream. It does not authorize
  pull, rebase, merge, branch switching, force-push, tag creation, PR creation,
  release publication, or deployment unless the user requests that operation.
- Before every commit, run the relevant verification, inspect the complete diff
  and `git status`, and stage explicit in-scope paths. Never include unrelated
  user work, secrets, raw/private data, generated bulk outputs, caches, logs, or
  local environments. If unrelated changes overlap the files that must be
  committed, stop and ask rather than sweeping them into the commit.
- After committing, push the current branch to its configured upstream and
  verify that local `HEAD` matches the upstream ref. If verification, commit, or
  push fails, fix the in-scope problem when possible and report the exact
  remaining blocker; never use force or history rewriting as a workaround.
- Do not delete or overwrite prior results to make a rerun look clean. Use a new
  versioned run directory and manifest.
- Update `docs/CODEBASE_MAP.md` when entry points, dependencies, data flows, or
  stable verification commands change.
- Append architecture or protocol decisions to `docs/DECISIONS.md`; do not edit
  history to conceal superseded choices.
- At handoff, report changed files, commands run, verification evidence,
  unverified boundaries, commit hash, push destination, current Git state, and
  the next concrete step.

## Definition of done

A change is complete only when its requested behavior is implemented, relevant
tests pass, evidence and warning invariants hold, leakage and scope boundaries are
unchanged or explicitly versioned, documentation matches current behavior, and
the handoff states what was not verified. Favor an honest blocked or negative
result over a plausible but unsupported claim.
