# Shared local environments

Use one existing Conda environment for projects with compatible dependencies.
A Conda environment is already a Python environment; it does not need to be
converted into a venv. Keep shared environments outside source repositories and
Dropbox. Select a separate environment when Python or dependency requirements
conflict, rather than upgrading packages used by unrelated projects.

## Run core development without installing the project

Activate a compatible environment, then run these commands from the repository
root. Core dependency ranges are in `pyproject.toml`.

```bash
conda activate <existing-compatible-environment>
PYTHONPATH="$PWD/src" python -m dcfa.cli --help
PYTHONPATH="$PWD/src" python -m pytest -q \
  tests/integration/test_tabcf_vertical_slice.py \
  tests/integration/test_cli_negative_paths.py
```

For a credential-free local mechanics run, choose a fresh output directory:

```bash
PYTHONPATH="$PWD/src" python -m dcfa.cli tabcf-demo \
  --scenario strong_iv \
  --output-dir artifacts/local/shared-env-smoke-v1
```

The command-scoped `PYTHONPATH` selects this checkout without adding a persistent
editable install to the shared environment. Other checkouts can use the same
interpreter with their own source path. Do not export this project's source path
globally. Console scripts such as `dcfa` still require an installed package; use
the module command above for this workflow.

## Compatibility and optional features

This is a development-only convenience, not a replacement for the existing
Python 3.11 lock files or locked evaluation/runtime requirements. The local
`sklearn_quantile_fallback` remains explicitly selected and its outputs are not
TabCF evidence. A passing core test does not validate Gemini, managed TabPFN,
Gradio, ZeroGPU, or a formal evaluation environment.

On 2026-09-19, the local native ARM64 Anaconda base environment had Python
3.14.6, NumPy 2.4.6, SciPy 1.18.0, scikit-learn 1.9.0, and Matplotlib 3.11.0.
It already supplied the core numerical dependencies but lacked `google-genai`,
`tabpfn-client`, and `gradio`. This inventory is machine-specific; do not install
the repository's lock files into base to force it to match. Its pytest 9.0.3
also differs from the declared `dev` extra (`pytest>=8,<9`).
The two core integration test files above passed (11 tests) in this environment.
No packages were installed or upgraded for that check.

For full local demos, use a compatible shared environment containing the optional
dependencies, or keep the existing isolated demo environment. When provisioning
a shared demo environment, install dependencies once outside the repository and
validate the relevant demo before retiring its old environment. Existing lock
files remain available for that setup. Separate environments should reflect
dependency compatibility, not automatically correspond one-to-one with projects.

## Storage and cleanup

Conda can hard-link package files from its cache into multiple environments on
the same filesystem, so separate compatible package installations may already
share disk blocks. Pip-installed packages do not automatically gain this Conda
deduplication. Moving an environment outside Dropbox reduces project sync scope;
moving alone does not reduce total local storage.

Do not simply move an existing venv: its installed scripts contain absolute
interpreter paths. Recreate it at its intended shared location if needed.
Retire `.venv` or `.venv-gemini` only after the replacement covers the features
you still use. Keep historical results and the lock files. Bytecode and test
caches are disposable but regenerate with use.

References: [Conda environments](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)
and [Python venv portability](https://docs.python.org/3.12/library/venv.html).
