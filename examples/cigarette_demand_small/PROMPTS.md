# Prompts for cigarette_144.csv

## Initial prompt: copy this block

```text
Please prepare an exploratory continuous-treatment IV analysis of this cigarette-demand CSV.

Outcome Y is log_packs_per_capita: the natural log of annual cigarette sales in packs per capita.
Treatment X is log_real_price: the natural log of average cigarette price per pack divided by CPI.
Instrument Z is real_sales_tax: the sales-tax component per pack, calculated as (tax including sales tax minus excise tax) divided by CPI.

Compare the median outcome under the high treatment intervention minus the median outcome under the low treatment intervention. Use the observed treatment's high and low levels offered by this workflow. Report the contrast in log packs per capita, not as an elasticity.

The data contain 144 state-year observations from 48 US states in 1985, 1990 and 1995. I am intentionally requesting the supported three-column model with no baseline covariates. This is an illustrative real-data analysis, not a controlled replication or a claim that the instrument is proven valid. Preserve all support and identification warnings. Show me the plan before execution.
```

## Only if asked to clarify

**Roles or column positions:**

```text
Column 1, log_packs_per_capita, is Y. Column 2, log_real_price, is continuous treatment X. Column 3, real_sales_tax, is instrument Z. No baseline covariates.
```

**Objective or comparison direction:**

```text
Use a median outcome contrast (quantile level 0.5), high price minus low price. The outcome unit is log packs per capita. I am not requesting an elasticity or an effect per one-unit price increase.
```

**Meaning of “high” and “low”:**

```text
Use the workflow's observed-treatment high and low settings: the 90th and 10th percentiles of log_real_price. Keep the existing support checks.
```

Review the card, then use **Confirm and generate report** exactly once. Do not
paste every clarification block unless needed. Chat turns use Gemini; the button
starts the GPU computation and should not request another Gemini compilation.
