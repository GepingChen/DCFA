# Exact-price distribution prompt

Use this prompt in the Space **Upload CSV** conversation after uploading
`cigarette_144.csv`, signing in, authorizing the upload and setting seed `20260920`.
It fits within the UI's 1000-character message limit.

```text
Roles:
Y = log_packs_per_capita; X = log_real_price; Z = real_sales_tax. No W.

Price change:
Compare real price from 100 to 120 CPI-deflated cents per pack. X and Y are already natural logs. Do not log the CSV again or replace prices with percentiles.

Distribution:
Show both CDFs and a finite-difference approximate PDF derived from the same CDF grid; no smoothing or tail extrapolation.

Quantiles:
Report the 25th, 50th, 75th, and 90th quantiles and their changes in packs per person per year.

Extreme value:
Report the probability exceeding 120 packs per person per year and its change in percentage points.

Upper vs. middle:
Report the 90th-quantile change minus the median change.

Reporting:
All changes are price 120 minus price 100. Use one analysis and point estimates only. Preserve support and identification warnings in the downloadable evidence and diagnostics; flag grid-limited quantiles. Show units and model inputs before execution.
```

If asked for scale clarification:

```text
The CSV X and Y are already natural logs. Prices are from 100 to 120 CPI-deflated cents per pack. The original outcome unit is packs per person per year; report probability exceeding 120 packs per person per year. Transform only the requested prices and threshold, never the CSV columns.
```

The confirmation card must show the Y/X/Z roles, no W, both original prices,
natural-log transform, model inputs approximately 4.605170185988092 and
4.787491742782046, both CDFs, the CDF-derived approximate PDF, all four outcome
quantiles, the 120-packs threshold and the second-minus-first direction. A
low/high card does not answer this question.

Click **Confirm and generate report** once. Typing “confirm” or “确认” does not
execute. The button makes no additional Gemini request. Keep the key in its
password field, never in chat. After success, download the ZIP; ordinary
follow-ups display the cached evidence-linked report without another fit or
provider call. Reset to request different interventions or a new analysis.

A support refusal or grid-limited tail is an admissible outcome. Do not edit the
CSV, substitute price percentiles, retry an exhausted GPU quota, or infer an
individual treatment effect from these aggregate quantile differences.
