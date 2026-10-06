# Agentic TabCF: From a price question to a traceable analysis

**“If we raise the price, how would sales change?”** Agentic TabCF helps analysts
with an appropriate research design turn that question into a plan they can
review, statistical calculations, and a report they can inspect and share.

Observed prices and sales can move together because of demand or other factors;
that association alone does not tell us what changing the price would do. An
average change can also hide differences between outcome distributions. Alongside
mean questions, Agentic TabCF supports comparing lower, middle and upper points
of the outcome distribution and the probability of exceeding a user-specified
threshold. These comparisons describe distributions, not effects on particular
people or groups.

## Who it is for, and what goes in

This development prototype is for analysts who already have a defensible
instrumental-variable (IV) design: a source of variation that affects the treatment
and meets the assumptions needed to separate its effect from confounding. The app
does not discover or establish a valid instrument, and uploading a CSV alone does
not make an analysis causal.

Supply an authorized CSV, identify the outcome (Y), continuous treatment (X) and
instrument (Z), and describe the comparison, units and any outcome threshold in
plain language. The current upload accepts exactly three numeric columns and
120–256 rows, with continuous outcome and treatment; it does not support additional
adjustment variables (W). Do not remove variables that your research design needs
just to fit this interface. Requested interventions must pass support checks.

## What the user gets

1. **A plan to check before running.** Review the column roles, units, treatment
   values and comparison direction, then confirm with the dedicated button. This
   lets you catch a wrong column or a log-versus-original-unit misunderstanding
   before the calculation.
2. **A report with inspectable results.** For a distribution request, compare
   outcome curves, selected quantiles and, when requested, threshold probabilities.
   Tables, plots and downloads retain evidence references and warnings so you can
   trace a displayed result back to the calculation and see its limitations.
3. **Clear limits and reusable results.** Support checks stop unsupported
   comparisons instead of presenting them as answers. Ordinary follow-ups reuse
   the completed report without fitting again; a different analysis requires reset.

Gemini helps turn the conversation into a reviewable plan. **TabPFN-3.5 supplies
the predictive models in both stages of the existing TabCF statistical method.**
TabCF code computes the intervention comparisons; the report layer presents the
validated results. Gemini does not calculate the causal numbers. See
[Project description](PROJECT.md) for the division of work and statistical limits.

This is a local, runnable entry package, not a submitted contest entry. All results
remain `development_only`. The paths and commands below refer to an extracted
submission bundle; saved results can be read without making provider calls.
For a short walkthrough, see the [Demo script](DEMO_SCRIPT.md).

The v4 package updates these submission documents while retaining v3's runtime,
source archives and saved results. `parent_commit.txt` identifies that retained
runtime, not the newer prose; `PACKAGE_ACCEPTANCE.json` records the documentation
revision and distinguishes this update from the historical runtime checks.
Documentation inside the retained source archives is historical.

## Run (Python 3.11)

From the extracted bundle directory:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
chmod 600 ~/.config/dcfa/gemini_api_key ~/.config/dcfa/tabpfn_api_key
.venv/bin/agentic-tabcf
```

Put your existing Gemini and Prior Labs API keys in those two files **outside this
bundle** first. Alternate locations use `DCFA_GEMINI_API_KEY_FILE` and
`DCFA_TABPFN_TOKEN_FILE` (see the parent's credential documentation for the exact
supported environment names). Credentials are never part of examples or reports.
Open <http://127.0.0.1:7860>. `PORT` selects another local port. The entry uses only
3.5; exhausted quota stops execution. It does not buy credits or switch models.
Gemini receives conversation and column names; Prior Labs receives selected Y/X/Z
rows. Use only authorized shareable inputs and review the transfer consent.

## Examples and reproduction

- The cigarette example is an exploratory comparison of **state–year per-capita
  sales**, not individual smoking. Upload `examples/cigarette/cigarette_144.csv`.
  Set seed **20260920** in Advanced
  settings. Paste the main prompt in `examples/cigarette/PROMPTS.md` and append its
  explicit probability-above-120 sentence. Review the exact 100→120 prices,
  natural-log storage, quartiles and direction before clicking Confirm.
- Upload `examples/synthetic.csv`: Y is the outcome, X is continuous treatment,
  Z is the instrument; no W. Ask for the mean at a high versus low intervention.
  This is the public, generated 128-row strong-IV fixture, seed 20261004.
- Saved results under `results/` are replays and cost no provider tokens to read.
  A live execution creates a new local output directory. Earlier v2 results are
  labeled v2, never 3.5. Do not infer confidence intervals from point estimates.

The five-seed comparison is available through the parent command
`dcfa compare-tabpfn --output-dir <new-directory> --source-ref <parent-git-commit>`
from a Git checkout. `--resume` skips saved attempts and never silently resubmits
an interrupted remote job. Use a runtime commit matching the existing remote v2
service; the included comparison identifies its exact runtime in
`results/comparison/runtime_commit.txt`. This comparison also requires an existing
Hugging Face credential and available CUDA quota. The entry UI itself needs neither.

## Attribution and licensing

The thin entry and new submission prose are Apache-2.0. Parent and TabCF code keep
MIT, and data/model licenses are separate; see `NOTICE`, `PARENT_MIT_LICENSE`,
`TABCF_MIT_LICENSE`, and the example source/license files. `parent_commit.txt`
identifies the bundled parent wheel; `parent_source.tar` contains its source.
`tabcf_source.tar` and `tabcf_commit.txt` preserve the separately licensed TabCF
submodule at the parent's recorded commit.
Contest eligibility of this mixed-license package must be checked before submission.
