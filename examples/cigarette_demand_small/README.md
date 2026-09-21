# Small real-data example: cigarette demand

Start with this guide, copy the first prompt from [PROMPTS.md](PROMPTS.md), and upload
only [cigarette_144.csv](cigarette_144.csv) to the
[DCFA ZeroGPU Space](https://huggingface.co/spaces/GPChen01/dcfa-zerogpu).

## The question and data

How does the median of log cigarette sales per capita change between a high and a
low real cigarette price, using the sales-tax component as an instrument for price?

This is a small version of the classic Stock–Watson cigarette-demand example.
It uses **144 genuine state-year observations: all 48 continental US states in
1985, 1990 and 1995**. The original TabCF cigarette example uses the 96 observations
in 1985 and 1995. We add the midpoint year from the public Ecdat panel because the
Space requires at least 120 rows. No rows are duplicated, simulated or jittered.
See [SOURCE.md](SOURCE.md) for provenance, transformations and limitations.

| CSV position | Column | Role | Meaning |
| --- | --- | --- | --- |
| 1 | `log_packs_per_capita` | Outcome Y | Natural log of annual cigarette sales in packs per capita |
| 2 | `log_real_price` | Continuous treatment X | Natural log of average price per pack divided by CPI |
| 3 | `real_sales_tax` | Instrument Z | Tax including sales tax minus excise tax, divided by CPI |

The CSV is about **7.4 KB**. It has one header row and 144 data rows, no index
column, no missing values, and no additional covariates. Use it as supplied.

## One-run walkthrough

1. Open the Space and sign in with Hugging Face. The optimization was deployed as
   build `A88468F`; a later build may have a different label.
2. Choose **Upload CSV**. On a narrow screen, open **More tabs** first.
3. Upload **cigarette_144.csv** from this folder. Do not upload the Markdown or
   license files, and do not add state/year columns to the upload.
4. Enter your Gemini key in **Temporary Gemini API key**. Keep the key out of chat
   and these files. Gemini API usage is separate from free ZeroGPU usage.
5. Read and check the data-transfer authorization. The numeric rows go to Hugging
   Face for local TabPFN execution; Gemini receives your conversation, column names
   and any role overrides. The temporary key passes through Hugging Face to Gemini.
6. Leave **Optional column overrides** blank initially. Set **Analysis seed** to
   `20260920` once, then leave it unchanged.
7. Copy the **initial prompt** from [PROMPTS.md](PROMPTS.md), paste it in the message
   field and click **Send message** once. This uses Gemini but does not fit TabPFN.
8. If clarification is needed, use only the relevant short reply in PROMPTS.md.
   Review the plan: the table above must match all three roles and column positions,
   the objective must be a **median/quantile contrast**, and the direction must be
   **high minus low**. No baseline covariates should be requested.
9. Click **Confirm and generate report** once. Typing “confirm” in chat does not
   start analysis. The key field should clear when generation begins.
10. Wait for completion. Save the displayed report/plot and the verified ZIP if
    available. Stop after this single run to conserve quota.

## What to expect and how to save quota

- A supported local TabPFN analysis uses one Stage 1 fit and one shared Stage 2 fit.
  The two stages request GPU allocations separately; CPU reporting and ZIP creation
  occur outside those allocations. Small data do not eliminate queue/allocation
  overhead or guarantee a particular runtime.
- Before confirmation there should be no fitted result. The execution button
  should not make another Gemini request.
- Low/high refer to the observed treatment's 10th/90th percentiles. The intervention
  grid also contains intermediate percentiles. The whole grid must pass support
  checks, so even an in-range price can be rejected for insufficient joint support.
- If quota is insufficient, wait for the displayed reset time. Do not repeatedly
  click or change the seed. If Stage 1 ran before Stage 2 allocation failed, a later
  retry can repeat Stage 1; it is not a free continuation.
- If support is rejected, keep the warning as the outcome of this example. Do not
  duplicate observations, trim data or search seeds merely to obtain a report.
- If CPU finalization fails, the app cleans temporary results and ends that CSV
  attempt. Resetting starts a new analysis and may spend GPU quota again.
- To ask someone to interpret a completed result, share the downloaded report/ZIP.
  Do not rerun fitting just to rephrase the explanation. Never share an API key.

## Reading the result correctly

The requested contrast is in **log packs per capita**, not packs, smoking
prevalence, a percentage, or a price elasticity. Do not label it as an elasticity.
A negative contrast would mean a lower fitted median log-sales outcome at the
higher price; a positive or unsupported result must also be retained.

This is a pooled, three-variable, real-data demonstration with no known causal
ground truth. The Space does not adjust for income, state/year effects or repeated
observations within states. Instrument validity and common support are substantive
assumptions; a tax-price association alone does not establish them. This is not a
replication of Stock–Watson or a publication-ready policy estimate.

## Verification already performed

- 144 distinct state-year records, 48 in each selected year.
- 144 distinct Y values, 144 distinct X values, 117 distinct Z values.
- Independent recomputation of every transformed value from the public source.
- The 96 overlapping records match TabCF's shipped cigarette analysis data to
  floating-point precision (largest absolute difference below `2e-13`).
- Current Space CSV ingress and role-assignment functions accepted the file.
- **Zero model fits, zero Gemini calls and zero GPU calls during preparation.**

Real TabPFN support checks, a live report, and post-optimization timing for this
specific CSV remain untested. A successful file check does not promise a successful
causal analysis.
