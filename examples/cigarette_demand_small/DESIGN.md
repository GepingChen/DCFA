# Exact-price distributional example

Status: editable example design, 2026-09-21. No results or frozen protocol.

## Question and estimands

Let P denote real price in CPI-deflated cents per pack, C annual cigarette sales
in packs per capita, X = log(P), and Y = log(C). The instrument is the observed
real sales-tax component. Use the existing 144-row CSV and seed `20260920`.

Compare the marginal interventional distributions at **P = 100 and P = 120**:

- Model-scale interventions: x0 = ln(100), x1 = ln(120).
- CDF on the display scale: G_p(c) = F_Y(ln(c); do(X = ln(p))) for c > 0.
- Outcome quantiles: q_p(tau) = exp(Q_Y(tau; do(X = ln(p)))).
- Quantile difference: D(tau) = q_120(tau) - q_100(tau), in packs/person/year.
- Exceedance: R_p = 1 - G_p(120).
- Probability difference: 100 * (R_120 - R_100), in percentage points.

Use tau = 0.25, 0.50, 0.75 and 0.90. These are **outcome** quantiles, not price
percentiles. Natural logarithms must be computed from the exact requested prices,
not rounded constants. For reference, ln(100) = 4.605170185988092 and
ln(120) = 4.787491742782046. The CSV is already logged; do not transform it again.

The estimand is a distribution of the state-level aggregate, under the maintained
structural IV assumptions. Each state-year contributes equally. It is not a
within-person intervention, a population-weighted distribution of smokers, or
the distribution of individual treatment effects. It is a price intervention,
not an intervention that raises tax by 20 cents.

## Result presentation

### Figure 1: two interventional CDFs

One shared outcome axis in packs/person/year and a probability axis from 0 to 1.
Label the curves with actual prices and units. Add a vertical marker at 120 packs
and mark each curve's CDF value there. Use the existing evaluated Y grid, mapped
through exp; do not invent an additional density estimate or extrapolated tail.
Describe this as the estimated CDF over the evaluated range, not exact knowledge
of the entire unbounded distribution.

At a fixed outcome c, a larger G_120(c) means a larger probability of sales at or
below c under the higher price. If curves cross, report the crossing rather than
claiming a uniform downward shift or proven stochastic dominance.

### Table and Figure 2: where the quantile changes occur

The following is an **uncomputed output layout**, not mock numerical results.

| Outcome quantile | At price 100 | At price 120 | Difference: 120 minus 100 |
| --- | --- | --- | --- |
| 25th percentile | Pending | Pending | Pending |
| Median | Pending | Pending | Pending |
| 75th percentile | Pending | Pending | Pending |
| 90th percentile | Pending | Pending | Pending |

All cells use packs/person/year. Plot the four differences against quantile level,
with a horizontal zero line. Connecting lines are visual guides between the four
estimates, not additional estimated quantiles.

Compare D(0.50) with D(0.75) and D(0.90). As a compact upper-tail summary, report
D(0.90) - D(0.50), which also equals the change in the 90th-minus-median gap.
A negative value means that gap narrows. If both differences are negative and
D(0.90) is more negative, describe a larger estimated absolute reduction at the
upper quantile. If signs differ, or both are positive, describe that actual
pattern instead. This is an absolute pack-scale comparison, not a relative
percentage reduction or proof of an effect on the same high-consuming units.

### Table 2: high-sales probability

| Metric | At price 100 | At price 120 | Difference |
| --- | --- | --- | --- |
| Probability C > 120 packs/person/year | Pending (%) | Pending (%) | Pending (percentage points) |

120 packs is an illustrative threshold near the observed 75th percentile
(approximately 121.70 packs), not a clinical threshold. Keep the strict greater-than
event explicit. No expected sign or minimum effect size is imposed.

### Report and downloadable data

The intended package includes the two figures, the quantile table, the probability
table, machine-readable curve/table data, source result bundle, evidence records,
warnings and the confirmed analysis plan. Existing artifact verification must
cover the displayed/exported claims using the current evidence mechanism.
All three outputs reuse the same fit; download and explanation do not refit.

## Computation and implementation boundary

The intended computation uses exactly two intervention values, not the automatic
five-point sample-quantile grid. Preserve the existing 18 integration nodes and
161-point outcome-grid construction; set the four requested quantile levels and
the outcome threshold ln(120). Run the existing support checks for both prices
before Stage 2. Being inside the marginal observed range is not enough.

Stage 1 is fitted once and Stage 2 uses one local TabPFN estimator for mean/full
output. The existing full predictions yield both CDFs in one batched evaluation.
Additional quantiles, complements, unit conversions and tables are deterministic
CPU operations on that result, not separate GPU fits. Retain the existing GPU
duration declaration. No bootstrap or parameter sweep is part of this first run.

The inspected code already has numeric intervention grids, CDF output, configurable
quantile levels and threshold queries. The current **Space compiler and report
workflow do not expose this whole request**. Required follow-on work is:

1. Represent exact numeric prices with explicit original/model-scale units and
   transformations in compilation and in the user-confirmed plan. Do not infer a
   log transformation solely from a column name. Reject unsupported requests
   before fitting instead of substituting symbolic labels.
2. Compile the two exact grid points and all requested summaries into one analysis,
   rather than one new execution per question.
3. Derive and evidence-link the original-scale quantiles, their differences,
   upper-tail gap change and exceedance probabilities with deterministic tools.
   Keep LLM narration out of numerical arithmetic.
4. Render the new CDF/quantile views and exports on CPU from the same validated
   result, preserving existing confirmation, cleanup and session behavior.

Two important arithmetic details from the inspected core:

- Its current `risk` value is a **CDF probability at/below the threshold**.
  Exceedance must be complemented. The exceedance contrast has the opposite sign
  from the corresponding CDF contrast.
- The original-scale quantile difference is **exp(q1_log) - exp(q0_log)**.
  It is not exp(q1_log - q0_log), which would be a ratio. Do not exponentiate a
  log-scale mean to obtain mean packs.

The current quantile inversion can return an outcome-grid endpoint when a requested
probability is not covered. Such a quantile must be marked as boundary-limited and
excluded from an unqualified tail-versus-middle conclusion. Do not silently enlarge
the grid or present a clipped endpoint as a well-resolved upper quantile.

## What can and cannot be concluded

An implemented, supported run can give estimated CDFs, quantile changes, exceedance
probabilities and a descriptive comparison of middle versus upper-quantile changes.
The outcome may be a negative, null, positive, mixed or unsupported result.

The first run supplies **point estimates only**. Differences across outcome
quantiles are distributional features, not confidence intervals. No confidence
bands, p-values, significance claims or causal identification proof are promised.
Bootstrap uncertainty would require a separate design and additional fitting,
including attention to repeated observations within states.

The three-column model omits income, state/year effects and other potential
confounders. Instrument exclusion/exogeneity remain assumptions. Label outputs
Track T / real-data / development_only and exploratory; do not claim textbook
replication, individual effects or a reliable tax-policy recommendation.

## Design verification and execution status

The example CSV and license remain unchanged. Exact-value transformations,
probability signs and file links were checked during this documentation revision.
No new application feature, deployment, model fit, Gemini call or GPU run is
included. Every result cell above remains pending until implementation and a
successful supported execution. This document supersedes the former low/high
median-only example; its Git history remains available.
