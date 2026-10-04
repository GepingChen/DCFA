# Agentic TabCF: Distributional Causal Analysis with TabPFN

**TabPFN-3.5 powers both stages of a continuous-treatment distributional IV workflow.**
Ask a question, review roles and units, confirm once, then inspect complete outcome
CDFs, quantiles and threshold probabilities with evidence-linked warnings.

This is a local, runnable entry package, not a submitted contest entry. All results
remain `development_only`. See `PROJECT.md` for scope and limitations.

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

## Examples

- Upload `examples/cigarette/cigarette_144.csv`. Set seed **20260920** in Advanced
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
