# Exact-price distributional example

Editable demonstration design, updated 2026-09-29. No frozen research protocol.

## Question and estimands

Compare the estimated marginal interventional distributions at real prices
**100 and 120 CPI-deflated cents per pack**, using the unchanged 144-row CSV and
seed `20260920`. Write X = log(P), Y = log(C), where C is annual cigarette sales
in packs per capita. The instrument is the observed real sales-tax component.
The CSV is already logged; transform only the requested original-unit values.

- CDF: G_p(c) = F_Y(log(c); do(X = log(p))), c > 0.
- Approximate PDF: adjacent-point differences of G_p on the original-unit grid,
  divided by the corresponding grid widths. No smoothing or renormalization.
- Quantiles: q_p(tau) = exp(Q_Y(tau; do(X = log(p)))); tau = 0.25, 0.50, 0.75.
- Differences: q_120(tau) - q_100(tau), in packs/person/year.
- Only on explicit request: P(C > c) = 1 - G_p(c), and its second-minus-first
  change in percentage points. There is no default threshold.

The unit of analysis is the state-year aggregate, with equal observation weights.
This is not a distribution of individual smokers or individual treatment effects,
a population-weighted analysis, or an intervention on taxes.

## Default report

1. Vertically stacked two-panel figure: estimated CDFs and CDF-derived approximate
   PDFs, with actual prices, outcome units and a shared evaluated outcome range. A threshold marker
   and probability annotations appear only when explicitly requested.
2. One compact table: 25th, 50th and 75th percentiles under each price, plus
   price 120 minus price 100 differences. No duplicate quantile-change plot.
3. An optional table of the explicitly requested threshold probabilities.
4. Background before the figure: confirmed question, sample metadata, Y/X/Z,
   comparison direction, units and model/display scales. Generic CSV reports use
   only their own confirmed roles and dataset metadata.
5. A collapsed technical appendix: run/specification references, summary evidence
   references, stored support/diagnostic values and warning codes. Complete CDF/PDF
   grid evidence remains in `distribution_results.json` and `evidence_records.jsonl`;
   full diagnostics, support and raw warnings remain in `result_bundle.json`.
6. All warnings and interpretation limits at the end in smaller readable text.
   Known duplicate warnings are grouped by theme in the human projection only;
   unknown or changed warning text and all triggered warnings remain visible.
   The browser, cached answer and download retain the applicable warnings.

The saved example uses an explicitly labeled display-only derivative of its original
run. Its original report, figure, ZIP and identity metadata remain unchanged and
available separately. A readable ZIP includes the derivative and unchanged original
run files. This is a presentation refresh, not a new scientific result.

Do not generate automatic claims about narrowing/widening, larger upper-tail
changes, CDF crossings or stochastic dominance. The 90th percentile and its
change-minus-median summary are not part of new dialogue requests. Historical
four-quantile projections remain reproducible by the artifact verifier, without
reintroducing those summaries into the main report.

Display to one decimal place and normalize displayed negative zero to zero.
This formatting is not a significance or equivalence decision. Grid-limited
quantiles and dependent differences appear as “Not resolved on grid”; retain
unrounded endpoints and flags in technical records.

## Computation and verification

Keep exactly two interventions, the existing 18 integration nodes and the
161-point outcome grid construction. Do not change the estimator, support rules,
sample, backend or GPU duration. Optional thresholds use the existing threshold
prediction path. The original-scale quantile contrast is exp(q1) - exp(q0), not
exp(q1 - q0). Never exponentiate a log mean to obtain mean packs.

Fit Stage 1 once and share the Stage 2 mean/full estimator. CDF, PDF, quantiles,
unit conversion, tables and downloads reuse the same result bundle. There is no
bootstrap, parameter sweep or extra fit per output. Existing evidence validation
checks the projections without fitting; no new hashes, gates or protocol freezes.

## Interpretation limits

These are exploratory Track T real-data point estimates, without confidence
intervals or significance conclusions. The three-column model omits income,
state/year effects and within-state dependence. IV exclusion and exogeneity
remain assumptions; diagnostics do not establish identification. The displayed
outcome range may omit tail mass, so the approximate density need not integrate
to one over that range. Do not infer individual effects, textbook replication,
or a reliable tax-policy recommendation.

Tests use fake providers to verify compilation, arithmetic, support refusal,
shared fits, optional thresholds, suppressed numerical-noise narratives, warning
placement, cached follow-ups and exports. They do not establish a real cigarette
causal result or GPU timing; those require separate actual-run evidence.
