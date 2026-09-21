# Exact-price distribution prompt

Use this prompt in the Space **Upload CSV** conversation after uploading
`cigarette_144.csv`, signing in, authorizing the upload and setting seed `20260920`.
It fits within the UI's 1000-character message limit.

```text
Use log_packs_per_capita as outcome Y, log_real_price as continuous treatment X, and real_sales_tax as instrument Z; no W. Compare real price from 100 to 120 CPI-deflated cents per pack. The CSV already contains natural-log sales and natural-log real prices. Do not log the CSV again or substitute percentiles. Return both CDFs, outcome quantiles 0.25, 0.50, 0.75, 0.90 and their differences in packs per person per year; probability exceeding 120 packs per person per year and its difference in percentage points; and 90th quantile change minus median change. All differences are price 120 minus price 100. Use one analysis, point estimates only, preserve support and identification warnings, and flag grid-limited quantiles. Show the exact units and model inputs before execution.
```

If asked for scale clarification:

```text
The CSV X and Y are already natural logs. Prices are from 100 to 120 CPI-deflated cents per pack. The original outcome unit is packs per person per year; report probability exceeding 120 packs per person per year. Transform only the requested prices and threshold, never the CSV columns.
```

The confirmation card must show the Y/X/Z roles, no W, both original prices,
natural-log transform, model inputs approximately 4.605170185988092 and
4.787491742782046, all four outcome quantiles, the 120-packs threshold and the
second-minus-first direction. A low/high card does not answer this question.

Click **Confirm and generate report** once. Typing “confirm” or “确认” does not
execute. The button makes no additional Gemini request. Keep the key in its
password field, never in chat. After success, download the ZIP; ordinary
follow-ups display the cached evidence-linked report without another fit or
provider call. Reset to request different interventions or a new analysis.

A support refusal or grid-limited tail is an admissible outcome. Do not edit the
CSV, substitute price percentiles, retry an exhausted GPU quota, or infer an
individual treatment effect from these aggregate quantile differences.
