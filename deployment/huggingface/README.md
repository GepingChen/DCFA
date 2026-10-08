---
title: Agentic TabCF
emoji: 📉
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 6.22.0
python_version: 3.12.12
app_file: app.py
pinned: false
license: mit
fullWidth: true
header: mini
hf_oauth: true
disable_embedding: false
models:
  - Prior-Labs/TabPFN-v2-reg
tags:
  - causal-inference
  - tabular
  - zerogpu
  - research
preload_from_hub:
  - Prior-Labs/TabPFN-v2-reg tabpfn-v2-regressor-v2_default.ckpt 4972a65a1b30806315c6f92499959ffbfc69a673
---

# Agentic TabCF

The default **Analyze your data** workspace keeps CSV upload, conversation,
plan confirmation, report generation and shared result controls together.
A single styled header and **Example reports** gallery replace the nested app.
The original theme, upload controls, OAuth, consent, reset and authenticated
callbacks remain in place. Data/model policy details are available inside the
analysis workspace; the explicit transfer consent remains beside the upload flow.

**Example reports** groups two independent saved cigarette analyses:

- **TabPFN 3.5** (selected first): saved v3 run
  `run_72e0e4a81aac75e7a91f3dbd`, embedded standalone HTML and offline download.
- **TabPFN v2 · Historical**: the separate historical ZeroGPU report with its
  own figure, CSV, original report ZIP and technical appendix.

Both use the same data and price question. Their numbers and artifacts remain
separate; differences do not establish model superiority. Reading either report
requires no login, API key, provider request or GPU allocation.
[Open the static 3.5 report](https://gepingchen.github.io/agentic-tabcf/cigarette-tabpfn35.html).

The public synthetic-example entry stays hidden while existing callbacks and
shared result components are retained. Local development retains the synthetic
scenarios. The statistical runtime pin, dependencies and credentials are unchanged.

Live computation in this canonical Space requires Hugging Face sign-in and runs
continuous-treatment IV analysis with TabPFN 3.5 API first. Only confirmed
API quota exhaustion triggers a complete rerun on local TabPFN v2 through ZeroGPU.
There is no model selector; results name the actual model and any switch.
Other failures stop without
changing models. No automatic purchase or upgrade is performed.

Every displayed number is derived from one validated result bundle and evidence
ledger. Unsupported interventions return no number. Results are
`local_development / tabpfn / development_only`; this is not locked Track T
evidence, production causal advice, or a general causal-method router.

## Run your own CSV

1. Sign in with Hugging Face and open **Analyze your data**.
2. Upload authorized, non-sensitive data with exactly three numeric columns and
   120–256 rows. Enter a temporary Gemini API key in the password field.
3. Approve the disclosed transfers, describe the analysis, and click **Send message**.
   Reply to the agent's questions until the roles and analysis objective are clear.
4. Review the X/Y/Z column names, original one-based positions, user-provided
   meanings and contrast direction. Continue chatting to correct anything.
5. Click **Confirm and generate report**. Only this button starts analysis;
   typing confirmation in the conversation does not run the analysis.

The key stays in the password field for the current conversation, and is cleared
when generation starts, on reset, or after fifteen idle minutes. Request-scoped
mode-600 key files are removed after every Gemini call. The key is excluded from
conversation state, logs, traces and ZIPs. With your authorization, Y/X/Z rows
go to Prior Labs for 3.5. On quota exhaustion, v2 reruns in this Space. Rows are
not sent to Google. Gemini receives conversation
text, headers and optional role overrides. Do not paste rows or secrets into chat.

Duplicate mode uses its owner's `DCFA_GEMINI_API_KEY` Space Secret instead of a
browser key. The owner supplies `DCFA_TABPFN_API_KEY` as a Space Secret for
statistical API execution. Completed reports include the actual model, fallback
record, final definition index and verified ZIP, without the complete chat history.
Temporary files are cleaned automatically. Authenticated remote v2 clients use
`/analyze_v2`; this endpoint always runs v2 and requires a valid HF token.

[Duplicate this Space](https://huggingface.co/spaces/GPChen01/dcfa-zerogpu?duplicate=true)
· [Source and documentation](https://github.com/GepingChen/DCFA)
· [Project and saved examples](https://gepingchen.github.io/projects/agentic-tabcf/)

## Model license

**Built with PriorLabs-TabPFN.** This Space uses TabPFN 3.5 API (`v3.5_default`,
one estimator, Thinking off; client 0.6.1), with the TabPFN v2 regression backup,
pinned to repository revision `4972a65a1b30806315c6f92499959ffbfc69a673`
and checkpoint SHA-256
`2ab5a07d5c41dfe6db9aa7ae106fc6de898326c2765be66505a07e2868c10736`.
See [LICENSE.txt](LICENSE.txt) for the Prior Labs License and attribution terms.

DCFA source is pinned to commit
`2bc2c9d9e43fcc3ee49dcc32fd4c9db5236c87e9`.


## Exact-price cigarette distribution example

The CSV dialogue now supports two explicitly specified original-unit prices when
both treatment and outcome columns are already natural logs. The confirmation
card shows the original units and exact model inputs. One analysis returns both
CDFs, a finite-difference approximate PDF derived from the evaluated CDF grid,
the 25th, 50th and 75th outcome quantiles and their original-unit differences.
The two-panel figure shows the CDF and CDF-derived approximate density.
An exceedance threshold is optional and reported only when explicitly requested.
No density smoothing or tail extrapolation is performed. Quantiles unresolved on
the evaluated grid are labeled explicitly. Support, identification and development
warnings appear at the end in small text. Visitor-facing tables use one decimal
place while the downloadable evidence appendix retains unrounded values.
All numerical results come from one validated bundle with downloadable evidence;
ordinary follow-ups read the cached report without refitting or another Gemini call.
Presets remain unchanged.

[Example and operating guide](https://github.com/GepingChen/DCFA/tree/main/examples/cigarette_demand_small)
contains the unchanged three-column CSV and a prompt that fits the message limit.
The default daily policy and remote endpoint have unit/integration coverage.
Live execution is assessed separately;
a successful deployment alone does not establish statistical quality.

## Historical v2 cigarette report

The stored report was produced on 2026-10-02 using the unchanged 144-row example,
seed 20260920, prices 100 and 120, and the three default quartiles. The original
report and ZIP are preserved with evidence and warnings. This is an exploratory
development demonstration; viewing is not a new statistical run.

[Report review and limitations](https://github.com/GepingChen/DCFA/blob/main/docs/CIGARETTE_REPORT_REVIEW_20261002.md).
