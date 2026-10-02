# Cigarette demand: a distributional price intervention

> Under the maintained IV assumptions, how does the estimated distribution of
> state-year annual cigarette sales per capita differ between real prices of
> 100 and 120 CPI-deflated cents per pack?

This is an exploratory Track T real-data demonstration. A real ZeroGPU run from
2026-10-02 is available in the Space's default **Example report** tab, without
login or an API key. See [the report review](../../docs/CIGARETTE_REPORT_REVIEW_20261002.md)
for verification and limitations. Engineering tests also use fake providers;
neither those tests nor the saved run establish statistical quality or a timing benchmark.

## Data

Use the unchanged `cigarette_144.csv`: 48 US states in 1985, 1990 and 1995, each
state-year equally weighted. No individual-smoker or population-weighted
interpretation is intended.

| Column | Role | Stored scale |
| --- | --- | --- |
| `log_packs_per_capita` | Y | Natural log of annual packs per capita |
| `log_real_price` | X | Natural log of CPI-deflated cents per pack |
| `real_sales_tax` | Z | CPI-deflated sales-tax component per pack |

The interventions are log(100) and log(120), computed from the exact original
prices. Do not log the CSV again. This is a price intervention, not a tax increase.
See [SOURCE.md](SOURCE.md) for provenance, selection, transformations and source
terms, and [GPL-2.0.txt](GPL-2.0.txt) for the accompanying license text.

## Run and report

1. Open the [Space](https://huggingface.co/spaces/GPChen01/dcfa-zerogpu), sign in,
   choose **Upload CSV**, upload the file and authorize the transfer. Keep a
   Gemini key in its password field; set seed `20260920`.
2. Paste the short default prompt from [PROMPTS.md](PROMPTS.md). The optional
   threshold sentence is separate; it is not needed to complete the default plan.
3. Review roles, units, exact prices, natural-log mapping and the three quartiles.
   Confirm once. Plan preparation must not fit TabPFN.
4. View the two-panel **CDF and approximate PDF** figure and the compact
   **25th/50th/75th percentile** table. Only an explicitly requested threshold
   adds probability annotations and a table. No upper-tail comparison, gap-change
   summary, crossing conclusion or duplicate quantile plot is generated.
5. Read the final small-text warnings. Download the verified ZIP containing
   `report.md`, `interventional_summary.png`, `distribution_results.json`,
   `result_bundle.json`, `evidence_records.jsonl`, specification and confirmed plan.
   Full diagnostics and evidence remain in the technical records.
6. Follow-ups return the cached report and warnings without another fit or provider
   request. Reset for a new analysis. Uploads are deleted after completion;
   CPU finalization failure does not trigger another fit.

## Interpretation and execution limits

The model omits income and state/year effects and does not address within-state
dependence. IV validity remains an assumption. Results are point estimates,
not confidence intervals, individual effects, or policy recommendations.
Grid-limited quantiles are marked as unresolved in the main table; their endpoint
values and flags remain available in the download.

Both prices must pass the existing empirical support checks; interior prices
alone do not establish joint support. Preserve support refusals. Do not edit the
sample, search seeds or retry exhausted GPU quota to force a favorable result.
Fake-provider tests establish software behavior only. See [DESIGN.md](DESIGN.md)
for the estimands, numerical projection and verification boundary.
