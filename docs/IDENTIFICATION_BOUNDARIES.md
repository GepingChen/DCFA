# Identification and claim boundaries

This is the short operational companion to the integrated research plan. It is
not a substitute for that plan or for a frozen protocol manifest.

## Evidence map

| Track | Design and oracle | Valid primary conclusion | Invalid extrapolation |
|---|---|---|---|
| T-Synthetic | Continuous-treatment IV simulation with known interventional distributions | TabCF error and diagnostic-policy operating characteristics under the stated DGP | Universal estimator validity or real-world IV validity |
| T-Real | Fulton Fish IV application without oracle truth | Bounded real-data workflow, diagnostics, support, and stability demonstration | Oracle error, proved identification, or individual causal truth |
| H-Real | Randomized three-arm Hillstrom experiment; average policy value identifiable | Held-out average value of a policy frozen before test outcomes | TabCF validation, individual optimal-action accuracy, or oracle regret |
| H-Semi-synthetic | Hillstrom covariates with a known simulated outcome DGP | Oracle action values, regret, and constrained-policy behavior in that DGP | Observed business lift or real individual counterfactual truth |
| A-Benchmark | Scripted cases with gold workflow state and fixed tools/fixtures | Incremental orchestration reliability | Estimator superiority, policy revenue lift, or causal identification |

## TabCF IV boundary

The public estimator target is a continuous-treatment distributional control
function problem. A representative estimand is the interventional distribution
`F_{Y(x)}(y)` and derived means, quantiles, tail risks, or contrasts on a supported
intervention grid.

Requirements:

- treatment is continuous and the IV role is explicit;
- v1 has one outcome, one continuous treatment, one scalar instrument, and no
  baseline covariates `W`;
- a non-empty baseline-covariate role stops before Stage 1 with
  `UNSUPPORTED_BASELINE_COVARIATES`; `W` must never be dropped silently;
- every point in the immutable intervention grid must pass the strict support
  assessment before Stage 2, including grid points not named by a scalar query;
- empirical diagnostics and their calibrated thresholds travel with the result;
- unsupported requests, missing roles, and outside-support interventions stop;
- real-data diagnostics must never be phrased as proof that an IV is valid.

Binary/multi-arm treatment, automatic IV discovery, invalid-IV repair, and
general causal-method routing are outside v1. Conditioning on baseline
covariates is deferred to a separately versioned post-MVP extension.

The macOS development profile may explicitly select a deterministic
`sklearn_quantile_fallback` to test contracts and workflow mechanics. Its
artifacts are `development_only`: they are not TabCF estimates and cannot enter
locked Track T results or public headline claims. A TabPFN load failure must
remain a typed error rather than trigger an automatic fallback. Publishable
Track T evidence requires a reproducible real TabPFN environment.

The bounded managed-client profile may send its frozen synthetic fixtures or an
explicitly authorized local website CSV to the Prior Labs service. The CSV route
accepts exactly three user-mapped numeric Y/X/Z columns, 120–256 rows, no W or
extra columns, and a continuous Y/X presentation preflight. It requires a visible
transmission confirmation before client access. It is also `development_only`:
the exact client/model settings and observed service package/trace metadata are
recorded, but the service checkpoint hash and runtime image digest are not
available to DCFA. Service traceability is not bitwise reproducibility, so this
path tests agent/backend mechanics only and cannot enter locked Track T evidence
or support an automatic real-data causal claim.

## Hillstrom RCT boundary

Hillstrom is a randomized three-action policy environment, not an IV problem.
The primary real-data object is the average value of a policy evaluated on an
untouched test split with paired DR estimates and IPW/direct-method checks.

Requirements:

- retain the three actions as categorical actions;
- use only pre-treatment features for policy learning;
- fit preprocessing and nuisance models on permitted splits;
- freeze the policy, costs, constraints, thresholds, and manifest before test
  outcomes are read;
- call `spend` spend unless an explicit margin/cost objective supports a profit
  interpretation;
- do not treat randomized assignment as the person's optimal action;
- do not report individual regret or optimal-action accuracy on the real RCT.

The current repository has no approved real Hillstrom raw file or dataset-use
decision. Local `hillstrom-demo` artifacts use a generated randomized fixture
and are `development_only`; they cannot support a real-RCT policy-value claim.
Likewise, semi-synthetic artifacts are called
`hillstrom_calibrated_semisynthetic` only when their resampled covariates come
from a provenance-complete real Hillstrom training split. Development fixtures
use the label `development_synthetic_not_hillstrom_calibrated`.

## Real-data ingestion boundary

DCFA never interprets a package or webpage license as automatic permission to
redistribute underlying data rows. Fulton and Hillstrom loaders require a local
file plus exact source, retrieval date, raw hash, and a project-approved
usage/license note. Missing provenance blocks before model fit. A Fulton run has
no oracle and may demonstrate diagnostics/stability only; it cannot report
estimator truth error or prove IV validity.

## Agent benchmark boundary

Track A isolates workflow value. The fixed workflow and full agent must receive
the same statistical models, permissions, fixtures or seeds, and tool outputs.
Cases—not repeated stochastic runs—are the primary inference units; repeated
runs are nested within a case.

The agent may add value through clarification, typed specification, routing,
approval, recovery, caching, constraint handling, and evidence validation. It
must not gain an advantage through a different estimator, test-data access, or
hidden arithmetic.

The Gemini live path is a one-request synthetic mechanics smoke, not the Track A
comparison. It sends only a frozen user request, the Y/X/Z schema contract, and
symbolic intervention labels; no data rows or actual intervention values leave
the machine. Gemini may propose a typed specification but cannot calculate or
rewrite a causal number. The deterministic runtime must independently validate
the proposal, result bundle, warnings, and evidence IDs. API failure or a
nonmatching proposal stops without retry, refit, or statistical fallback.

## Claim checklist

Before publishing a number or sentence, verify:

1. Which track produced it?
2. Is the data real, synthetic, or semi-synthetic?
3. What is identifiable or known in that design?
4. Does a resolvable evidence ID bind the number to data, specification, tool,
   version, unrounded value, units, support status, and warnings?
5. Was the relevant policy, threshold, prompt, or model frozen before test access?
6. Does the language preserve uncertainty, support, cost, and identification
   limitations?

If any answer is missing, block the claim and report what evidence is required.
