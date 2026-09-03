# DCFA repository operating rules

These instructions apply to the entire repository. A more deeply nested
`AGENTS.md`, if one is added later, may refine local implementation details but
must not weaken the explicit release, leakage, privacy, or security boundaries
here. The proportional-safeguards rules below control how broadly those
boundaries may be applied during ordinary development.

## Start every task here

1. Run `git status --short --branch` and preserve unrelated or uncommitted work.
2. Read this file and inspect only the source, tests, and documentation relevant
   to the requested change. Read the integrated plan or broader project docs only
   when the task touches their research design, architecture, data, evaluation,
   public-claim, or release boundary.
3. Inspect the actual code, tests, dependency files, and public APIs before
   proposing an implementation. Never invent a `tabcf_core` class, function,
   file layout, dataset location, or command from the plan.
4. Define the smallest verifiable success criterion before editing. Name an
   evidence track only when the request actually affects one.

Authority for intended research behavior is the integrated plan plus any later
explicitly frozen protocol manifest. Authority for current executable behavior
is the checked-in code and tests. If they disagree on a frozen estimand, held-out
evaluation, public claim, security boundary, or release decision, stop, document
the mismatch, and ask for a protocol decision. For ordinary implementation drift,
follow the inspected executable source, make the requested scoped change, and
record the discrepancy without creating a new gate.

## Proportional safeguards and execution priority

These rules govern every later reference in this file to hashes, contracts,
baselines, freezes, invariants, validation, evidence, or gates.

Here, a prohibited default "baseline" means an added snapshot, golden-output,
or acceptance barrier. A statistical comparator explicitly required by the
research question is an experiment arm and may be implemented without treating
it as a safety gate.

- Default to no new hash, frozen contract, baseline, invariant, manifest layer,
  approval step, or gate. Do not introduce one merely because it would make the
  system feel more auditable, deterministic, safe, or future-proof.
- Before adding one, name the concrete failure scenario it prevents, identify the
  irreversible, cross-system, security/privacy, held-out-evaluation, or formal-
  release boundary involved, and explain why Git identity, a version number, a
  run ID or primary key, transactions, uniqueness constraints, types, schemas,
  and ordinary tests do not already prevent or reveal that failure.
- Prefer one canonical identity per boundary. Do not stack a Git commit, source-
  tree hash, config hash, prompt hash, per-file hashes, and aggregate hash for the
  same purpose. A second identity mechanism requires a distinct failure scenario.
- A dirty working tree alone is not a reason to invent a source-tree hash. Either
  use the checked-in commit, record the diff as ordinary run metadata, or require
  a clean tree only at a formal release boundary.
- Hash externally downloaded artifacts only when their bytes are not controlled
  by Git and substitution would change execution or a formal claim. A provider
  model version or immutable build ID is sufficient when exact bytes are neither
  available nor required by the stated evidence level.
- Use frozen research protocols only after the task explicitly enters a named
  threshold/final evaluation or publication phase. Development configs, UI
  examples, exploratory runs, and smoke tests remain editable and versioned by
  normal Git history unless the user explicitly requests a freeze.
- Put hard gates only at irreversible actions, external publication/deployment,
  secret or private-data handling, unsupported causal execution, held-out test
  access, or formal result promotion. Use ordinary validation and clear errors
  for reversible local work.
- Preserve existing safeguards unless the user explicitly requests a reviewed
  simplification. Do not duplicate or extend them automatically. When touching
  an existing safeguard, keep its current scope instead of propagating it to new
  development paths.
- Complete all safe, reversible, in-scope work before asking for clarification or
  approval. Ask only when the missing choice would materially change a research
  protocol, external side effect, security/privacy posture, or public claim.

Classify work before choosing verification:

- **Development:** implement the requested behavior, run the smallest meaningful
  test or smoke, and stop once it passes. Do not run the full repository suite,
  regenerate frozen artifacts, or re-hash unrelated assets for a local UI,
  documentation, refactor, or isolated bug fix.
- **Research measurement:** prioritize the actual simulation or measurement.
  Before a long run, provide durable logging, incremental progress or checkpoints,
  and a restart path. Preflight work must not consume the task while the required
  run remains unstarted. Engineering acceptance is not a scientific result.
- **Release/security:** run the applicable full checks and existing release gates.
  Add new safeguards only under the concrete-failure test above.

Do not repeat a passed test, status check, diff check, hash computation, or
artifact verification unless code changed afterward, the previous result was
incomplete, or a newly observed failure justifies repetition.

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
- For a final or publicly promoted numerical claim, an evidence record must bind
  the value to the applicable immutable external inputs, specification version,
  tool and model version, result bundle, unrounded value, units, support status,
  warnings, and source artifact. Development and exploratory outputs may use a
  run ID, Git commit, configuration, and explicit evidence-status label; they do
  not require new hashes merely to exist.
- Text, tables, cards, and plots must be derived from the same validated result
  bundle. Never read a headline number from a plot or copy it manually.
- Evidence validation failure blocks promotion of the affected numerical answer
  or release. It must remain visible during local debugging and must not prevent
  unrelated computation needed to diagnose the failure.
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
  access notes, schemas, and transformation versions. Require a content hash when
  the data crosses systems or enters a final evaluation/release manifest, not for
  every temporary or generated development fixture.
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
- Fail closed on unsupported treatments, missing causal roles, outside-support
  interventions, leakage risk, security/privacy violations, or ambiguous high-
  consequence requests. Scope stale-ID, hash, and evidence-mismatch blocking to
  the artifact or release boundary that relies on that identity; do not stop an
  unrelated local workflow.
- Do not silently fall back between statistical models, from GPU to CPU, from a
  real backend to a fake backend, or from a failed estimator to a heuristic.
- Keep generated outputs separate from source. Do not commit datasets,
  checkpoints, caches, logs, local environments, or bulk traces.
- Match existing style and make surgical changes. Do not refactor unrelated code.

## Verification expectations

Run the smallest relevant checks during development. Run the full available suite
only when the change crosses a shared statistical/runtime boundary or is being
promoted for release. Once a relevant check passes, broaden or repeat it only
after new changes, failures, or unresolved evidence justify doing so. Until a
dependency file and stable commands are checked in, do not invent canonical
commands; update `docs/CODEBASE_MAP.md` only when a stable entry point, dependency,
or data flow actually changes.

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

A development change is complete when its requested behavior is implemented and
the smallest relevant verification passes. A research result additionally needs
the requested simulation or measurement artifact. A release additionally needs
its existing release gates, evidence and warning invariants, matching
documentation, and an explicit statement of what was not verified. Favor an
honest blocked or negative result over a plausible but unsupported claim, while
continuing all safe work that does not depend on the blocked boundary.
