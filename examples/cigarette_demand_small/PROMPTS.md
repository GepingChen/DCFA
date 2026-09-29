# Exact-price distribution prompt

Upload `cigarette_144.csv` in the Space's **Upload CSV** conversation, sign in,
authorize the upload and set seed `20260920`. The default prompt is below the
1000-character message limit.

```text
Y = log_packs_per_capita; X = log_real_price; Z = real_sales_tax. No W.
Compare real price from 100 to 120 CPI-deflated cents per pack. X and Y are already natural logs. Do not transform the CSV again.
Show both CDFs and their CDF-derived approximate PDFs. Report the 25th, 50th and 75th quantiles and their differences in packs per person per year, price 120 minus price 100.
Use one analysis. Place warnings at the end in small text.
```

Only if a threshold probability is part of your question, append:

```text
Also report the probability exceeding 120 packs per person per year and its change in percentage points.
```

This is a specified-threshold probability, not an extreme-value analysis. The
threshold is illustrative, not a health or policy standard. Without this explicit
request, the plan and report must contain no threshold probability or marker.

Before execution, the confirmation card must show the roles, no W, original prices,
log-scale model inputs, both CDFs and approximate PDFs, the three quartiles and
second-minus-first direction. A low/high card does not answer this question.

Click **Confirm and generate report** once. Textual confirmation does not execute.
Keep credentials in the password field. Download the verified ZIP after success;
ordinary follow-ups return the cached report and warnings without refitting.
Reset to request another analysis.

Support refusal is an admissible outcome. Do not manipulate the CSV or replace
prices to force acceptance. Grid-limited quantiles are marked as unresolved in
the main table; their numerical endpoints remain in the technical records.
