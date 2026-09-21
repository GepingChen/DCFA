# Cigarette demand: a distributional price intervention

Updated design: 2026-09-21.

> If the real price of a pack of cigarettes increases from 100 to 120 cents,
> how does the distribution of state-level annual sales per capita change?
> Is the change larger around the middle or in the upper part of the distribution?

**Status: example design, not yet executable through the current Space dialogue.**
The current interface accepts only low/center/high and mean/median summaries.
It cannot faithfully compile this numeric-price, multi-result request. Do not
confirm a card that silently replaces 100/120 with sample percentiles. This update
changes the example documents only; it does not extend or deploy the application.

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

1. Two interventional CDF curves, labeled **price = 100** and **price = 120**, on
   an outcome axis in packs per person per year.
2. A table and a quantile-change plot at the 25th, 50th, 75th and 90th percentiles,
   reporting both intervention-specific values and **120 minus 100** differences.
3. The probability of annual sales exceeding **120 packs per capita** under each
   price, and its difference in percentage points. This is an illustrative
   threshold near the observed outcome's 75th percentile, not a health standard.
4. A short comparison of the median change and upper-quantile changes, with all
   support, identification, weak-IV and numerical-grid warnings retained.

The two occurrences of 120 have different units: **120 cents** is the intervention;
**120 packs per person per year** is the outcome threshold.

## Intended one-run workflow, after the interface supports it

1. Open the [Space](https://huggingface.co/spaces/GPChen01/dcfa-zerogpu), sign in,
   and select **Upload CSV** (under **More tabs** on narrow screens).
2. Upload only `cigarette_144.csv`. Enter a Gemini key in its password field and
   review the transfer authorization. Keep keys out of chat and files.
3. Set the analysis seed to `20260920`, then paste the initial prompt from
   PROMPTS.md. Preparing or correcting the plan must not fit TabPFN.
4. Before confirmation, the card must explicitly show the three roles above,
   prices 100/120 in real cents, their log-scale mapping, the four outcome
   quantiles, the 120-packs threshold, and the contrast direction 120 minus 100.
   If it shows only low/high, a single median contrast, or missing units, stop.
5. Confirm once. All requested results should reuse the same two fitted stages
   and one validated result bundle; no separate fit per chart or statistic.
6. Download the report, tables/curve data and verified ZIP. Inspect cached results
   rather than rerunning to change wording or colors.

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

## What has been verified

The existing data preparation checks remain applicable: 144 genuine state-year
records, correct source transforms, no missing values, and acceptance by the
current CSV ingress and role-mapping functions. For this revision, the exact-price
log transforms, probability-difference sign, document links and unchanged CSV
were checked. No TabPFN fit, Gemini call or GPU call was made. No actual causal
results have been computed for this revised question.
