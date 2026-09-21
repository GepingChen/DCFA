# Prompt: price 100 to 120 and the outcome distribution

Updated: 2026-09-21. This replaces the previous low/high median-only example.
**Target behavior:** the current Space compiler does not support this complete
request. Save this prompt for the extended interface; do not approve an automatic
substitution of low/high percentiles for the exact prices.

## Initial prompt

```text
I want an exploratory distributional IV analysis of cigarette demand. If the real price per pack rises from 100 to 120 CPI-deflated cents, how does the distribution of state-level annual sales per capita change? Is the change larger near the median or in the upper part of the distribution?

Use log_packs_per_capita as outcome Y, log_real_price as continuous treatment X, and real_sales_tax as instrument Z. The CSV already contains natural-log sales and natural-log real prices. The treatment inputs must therefore be log(100) and log(120), not 100 and 120 on the stored scale. Use no baseline covariates.

Compare the two interventional CDFs. Report the 25th, 50th, 75th and 90th outcome quantiles under each price and their differences, always price 120 minus price 100. Show outcome quantiles and their differences in packs per person per year. Also report the probability of annual sales exceeding 120 packs per capita under each price, and the difference in percentage points.

Use the same fitted analysis for every output. Retain all support and identification warnings. These are illustrative state-year aggregate results, not individual effects or a claim that the instrument is proven valid. Do not substitute low/high labels or sample percentiles for my prices. If this request is not supported, explain that limitation before any fitting. Show me the complete plan with units before execution.
```

## Clarification replies, only if needed

**Price units and transformations:**

```text
The prices are 100 and 120 CPI-deflated cents per pack. The stored treatment is already log real price. Compute the natural logs once to form the intervention values; do not log the CSV again and do not replace my values with price percentiles.
```

**Roles:**

```text
Column 1, log_packs_per_capita, is Y. Column 2, log_real_price, is continuous treatment X. Column 3, real_sales_tax, is Z. There are no requested covariates.
```

**Threshold and comparison direction:**

```text
The outcome threshold is 120 packs per person per year, distinct from the price of 120 cents per pack. For both quantiles and exceedance probabilities, subtract the price-100 result from the price-120 result. Use percentage points for the probability difference.
```

**If the card offers only low/center/high:**

```text
That changes my question. Do not execute the low/high comparison. I need the exact real prices 100 and 120 and the requested distributional outputs. If the interface cannot represent them, stop before fitting and state the missing capability.
```

Review the full card before pressing **Confirm and generate report**. Typing
confirmation in chat must not execute the model. Keep API keys in the password
field; never paste them into a prompt.
