# Cigarette demand: a distributional price intervention

Updated design: 2026-09-21.

> If the real price of a pack of cigarettes increases from 100 to 120 cents,
> how does the distribution of state-level annual sales per capita change?
> Is the change larger around the middle or in the upper part of the distribution?

**Status: implemented for the Space CSV dialogue, with fake-provider verification.**
The exact-price path accepts explicitly already-natural-log X and Y, keeps the
CSV unchanged, and computes all outputs from one validated result bundle.
No real GPU numerical analysis or timing result is supplied with this example.

## Files

- [DESIGN.md](DESIGN.md): precise estimands, result layout, calculation rules and
  the implementation work needed before a live run.
- [PROMPTS.md](PROMPTS.md): revised user prompt and clarification replies.
- [cigarette_144.csv](cigarette_144.csv): the same prepared three-column dataset.
- [SOURCE.md](SOURCE.md): source, selection, transformations and interpretation limits.
- [GPL-2.0.txt](GPL-2.0.txt): accompanying source-package license text.

## Data and units

Use all 144 observations: 48 US states in 1985, 1990 and 1995. Every state-year
has equal weight; this is not population weighting or a distribution of individual
smokers. The CSV remains unchanged, about 7.4 KB, with no extra columns.

| Position | CSV column | Role | Stored scale |
| --- | --- | --- | --- |
| 1 | `log_packs_per_capita` | Y | Natural log of annual packs per capita |
| 2 | `log_real_price` | X | Natural log of CPI-deflated cents per pack |
| 3 | `real_sales_tax` | Z | CPI-deflated sales-tax component per pack |

The input intervention is **100 to 120 CPI-deflated cents per pack**, not today's
nominal cents, not a tax increase, and not `X=100` to `X=120` on the log scale.
The corresponding model inputs are `log(100)` and `log(120)`.

The observed price's 25th/75th percentiles are approximately 99.43/121.82 real
cents. These descriptive values motivate interior price choices; they do not
replace the exact requested prices or establish joint support. Both interventions
must pass the existing support checks.

## Expected result package after implementation

1. Two interventional CDF curves, plus a CDF-derived approximate probability
   density (PDF), labeled **price = 100** and **price = 120** on an outcome axis
   in packs per person per year. The PDF uses finite differences only, with no
   smoothing or tail extrapolation.
2. A table and a quantile-change plot at the 25th, 50th, 75th and 90th percentiles,
   reporting both intervention-specific values and **120 minus 100** differences.
3. The probability of annual sales exceeding **120 packs per capita** under each
   price, and its difference in percentage points. This is an illustrative
   threshold near the observed outcome's 75th percentile, not a health standard.
4. A short comparison of the median change and upper-quantile changes, with all
   support, identification, weak-IV and numerical-grid warnings visible in the
   report as well as retained in the download.

The two occurrences of 120 have different units: **120 cents** is the intervention;
**120 packs per person per year** is the outcome threshold.

## One-run workflow

1. Open the [Space](https://huggingface.co/spaces/GPChen01/dcfa-zerogpu), sign in,
   and select **Upload CSV** (under **More tabs** on narrow screens).
2. Upload only `cigarette_144.csv`. Enter a Gemini key in its password field and
   review the transfer authorization. Keep keys out of chat and files.
3. Set the analysis seed to `20260920`, then paste the initial prompt from
   PROMPTS.md. Preparing or correcting the plan must not fit TabPFN.
4. Before confirmation, the card must explicitly show the three roles above,
   prices 100/120 in real cents, their log-scale mapping, the four outcome
   quantiles, both CDFs, the CDF-derived approximate PDF, the 120-packs threshold,
   and the contrast direction 120 minus 100. If it shows only low/high, a single
   median contrast, or missing units, stop.
5. Confirm once. All requested results should reuse the same two fitted stages
   and one validated result bundle; no separate fit per chart or statistic.
6. Download the verified ZIP: `report.md`, `interventional_summary.png` (CDF,
   CDF-derived PDF and quantile-change panels), `distribution_results.json`
   (curve/table/density values and evidence mapping),
   `result_bundle.json`, `evidence_records.jsonl`, warnings, specification and
   `confirmed_plan.html`. The figure and tables use the same bundle.
7. Ordinary chat follow-ups return the cached report without Gemini or fitting.
   Reset is required for a new analysis; the upload is deleted after completion.
   A CPU finalization failure is terminal and does not trigger another fit.

## Quota and interpretation

Keep the first run to two prices and four outcome quantiles. Do not add a price
sweep, seed search or bootstrap run. The first report contains point estimates,
not confidence bands or claims of statistical significance. Two fits do not
promise a particular wall-clock time; allocations and queueing add overhead.

If support is insufficient, retain the rejection. If quota is exhausted, wait
rather than repeatedly retrying; a failed later allocation can require repeating
Stage 1 on a new attempt. A report-finalization failure must not silently refit.

The result concerns the distribution of a state-level aggregate under hypothetical
price interventions, conditional on the maintained IV assumptions. It does not
identify which states or smokers benefit, or the distribution of individual
causal effects. The current three-column model omits income and state/year effects
and does not address within-state dependence. Treat this as an exploratory Track T
real-data demonstration (`development_only`), not a policy recommendation.

## Verification boundary

Tests use a fake Gemini response and fake TabPFN predictions. They cover exact
units, complements and contrast signs, a nontrivial hand-calculated example,
shared Stage 2 mean/full predictions with two total fits, support refusal before
Stage 2, endpoint flags, cached follow-ups, repeated clicks, finalization errors,
and independently verified artifacts. Fake broad control ranks exercise the
success path without changing CSV bytes or production support rules. They are
not evidence that the real cigarette analysis passes support or has any given
causal effect. Live deployment verification checks the build/UI only; a real
GPU analysis and its wall-clock timing remain unexecuted.
