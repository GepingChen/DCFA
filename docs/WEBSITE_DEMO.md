# Local, static, and Colab demo paths

DCFA now has four deliberately different presentation paths:

1. the repeatable local Gradio service for operator review;
2. a precomputed, independently verified static replay for GitHub Pages;
3. a pinned notebook for custom analysis in a visitor's own Colab runtime.
4. a development-only public Space using 3.5 API with local ZeroGPU v2 backup.

The static route and Colab entry are linked from the public portfolio. Static
replay makes no provider call. The Colab implementation uses the visitor's accounts, secrets,
quota, ephemeral filesystem, and explicit transfer confirmations. None of the
four paths is locked Track T evidence or a general causal-analysis service.

## Hugging Face ZeroGPU path

The canonical Space is `GPChen01/dcfa-zerogpu`. Its default **Example report**
tab displays a saved real cigarette analysis without login, an API key, a provider
request or GPU allocation. The CSV and original report ZIP are downloadable.
The report retains its run version, evidence appendix and interpretation warnings;
it is an exploratory Track T real-data demonstration, not a new analysis.

**Upload CSV** and **Run synthetic example** retain their live execution flows.
The Space requires Hugging Face login before live computation. The three
synthetic presets use a typed median contrast without Gemini; their statistics
use 3.5 API first and local v2 only after confirmed quota exhaustion.
It preloads and hash-checks `Prior-Labs/TabPFN-v2-reg` at revision
`4972a65a1b30806315c6f92499959ffbfc69a673`, uses one CUDA estimator, and
prominently displays the required `Built with PriorLabs-TabPFN` attribution.

For a bounded CSV conversation, a logged-in visitor may enter a temporary Gemini
API key in the canonical password field. Each message clarifies the variable roles
and supported objective; no model fitting starts until **Confirm and generate
report** is clicked on the final definition index. The card includes original
one-based column positions and user-provided variable meanings. Textual confirmation
in chat does not execute analysis. Changing the inputs invalidates the old card.

The key remains in the password field for the current conversation, and is cleared
on generation, reset, or fifteen minutes of inactivity. For each request DCFA
materializes it in a mode-600 temporary file and removes that file afterward. It is
excluded from conversation state, logs, traces, artifacts and ZIPs. Authorized
Y/X/Z rows go from the Hugging Face runtime to Prior Labs for 3.5 API execution.
After confirmed quota exhaustion, v2 restarts completely inside the Space.

A visitor who prefers server-side secret storage can instead duplicate the Space
and add `DCFA_GEMINI_API_KEY` as their own Space Secret; that mode hides the browser
key field. Gemini receives conversation text, three header names and optional role
overrides, including user-requested numeric interventions, but no CSV rows or
observed treatment values. Completed runs retain the
verified statistical report plus a `confirmed_plan.html` appendix; full chat
history is not exported. Uploads must be authorized, non-sensitive three-column
data. Results are available as a path-safe ZIP and uncompressed run directories
are removed. Existing cache cleanup and session expiry clear temporary data.

The Space installs DCFA from a pinned Git commit. Its entrypoint must set both
`DCFA_WEBSITE_GEMINI_CONFIG_FILE` (existing single-turn presets) and
`DCFA_SPACE_CSV_DIALOGUE_CONFIG_FILE` (Space CSV dialogue) to the corresponding
JSON files uploaded beside `app.py`; these repository-level profiles are not
included in the installed Python wheel. The dialogue profile reserves 4096
output tokens with low thinking because the previous 1024-token medium-thinking
budget was exhausted by a live clarification response, returning incomplete JSON.

CSV dialogue displays a waiting notice while Gemini prepares a plan. A failed
request restores the controls and reports a safe error category and HTTP status;
provider response bodies and credentials are not logged. HTTP 429 means the
visitor must check Gemini rate limits, quota, or billing. The pinned SDK's
Interactions retry count is explicitly zero: each Send action makes at most one
provider request, including when the provider returns a Retry-After header.

The ZeroGPU runtime is `development_only`. Its package, model revision, model
hash, Space commit, and DCFA commit are recorded, but it has no immutable
container-image digest and cannot enter locked Track T evidence.

## Default local API model and quota

`dcfa-ui` (alias `dcfa-website-demo`) uses TabPFN-3.5 through the official
`tabpfn-client==0.6.1`, selecting `v3.5_default` explicitly. The managed profile
uses one estimator, disables Thinking, retains 256 training / 400 prediction
row caps, and records the service-resolved model path and package version.
The existing service-version check expects `9.0.0`. Version mismatches stop.
Daily mode can switch only after confirmed token exhaustion as described below;
the existing fixed managed smoke and research entrypoints never switch models.
There is no subscription, credit purchase, or paid-provider switch in this path;
account billing and free entitlement are controlled by Prior Labs. Keep the
account on its free plan for free-only operation.

On 2026-10-03, an authenticated development account returned 5,000,000 daily and
20,000,000 monthly tokens, with zero Thinking fits. A real 128-row synthetic
analysis made three predictions and consumed 30,000 tokens. Dimension-only
server quotes for 256 training rows and 320 Stage-2 prediction rows also returned
10,000 tokens per request. At this bounded size, budget approximately 666
completed analyses per month (about 21 per day across a 31-day month), or at
most 166 in one day if monthly quota remains. Other clients share the allowance;
failed calls and reruns can consume it. This is an account-specific observation,
not a guaranteed public free-tier allowance or an estimate for large datasets.

Check current allowance at <https://platform.priorlabs.ai/account/usage>.
The API reports daily and monthly reset timestamps; do not assume the older
client README's daily-only reset applies to both. See
<https://github.com/PriorLabs/tabpfn-client#usage-limits> for dimension-only
`estimate_cost` queries. These are table-compute tokens, not Gemini text tokens;
Gemini has its own quota. Existing saved reports and cached runtime follow-ups
do not refit; launching a new analysis does.

## Daily analysis policy

The local UI offers **Analysis mode** with three choices:

| Mode | Execution and statistical data recipients |
|---|---|
| `api_preferred` (default) | Prior Labs 3.5 first; only confirmed quota exhaustion permits a complete v2 rerun at the configured GPU destination |
| `api_only` | Prior Labs 3.5 only; exhaustion stops the analysis |
| `v2_only` | Direct v2 at the configured GPU destination; no Prior Labs key read or API request |

The policy notice updates with the selection and changing modes clears previous
CSV consent. Users authorize the selected recipients before executing; an allowed
fallback needs no additional confirmation. The selector is disabled while running.
A Space conversation records its reviewed mode with the existing plan revision;
changing it invalidates old confirmation. Completed cached reports keep their
original mode/model even if the selector later changes. Reset for a new analysis.
Results and downloads name the selected policy, actual model and switch reason.
Existing Python entrypoints remain fixed managed unless `analysis_mode` is passed.
The shared Space source includes the selector, but this change is **not deployed**;
the running Space retains its previously deployed automatic API-first UI.
Research, locked evaluation and saved results do not automatically migrate.

Gemini receives only the existing allowed text/headers. Local remote fallback
sends the same Y/X/Z data and confirmed plan to the configured HF Space, without
sending the Gemini or Prior Labs key. The HF credential authenticates that request.
On the Space, uploaded rows are authorized for Prior Labs 3.5; fallback uses the
existing local ZeroGPU v2 runner without another service submission. The owner
configures `DCFA_TABPFN_API_KEY` as a Space Secret; it is materialized in a temporary
mode-600 file under the blocked secret directory only for the API attempt and
removed afterward. Missing credentials stop, rather than triggering fallback.
The compilation, interventions and seed stay unchanged; results may differ by
model. No statistical equivalence is asserted.

Client 0.6.1 flattens HTTP failures into generic exceptions. The scoped HTTP
adapter intercepts response status before that happens. It never searches error
text for `quota`. It recognizes exhaustion from the current authenticated
`daily_tokens_used/daily_token_limit` or
`monthly_tokens_used/monthly_token_limit` fields: either before execution, or
from a fresh usage response after HTTP 429. Missing/malformed usage, ordinary
429, 401/403, network/service failures, invalid data, version mismatches and
statistical/support failures never cause a model switch. A remaining balance
smaller than a request's cost is **not** inferred to be exhaustion from a quote.
Unrecognized provider error structures stop conservatively. No real exhausted
account response has been observed in this validation.

Run locally:

```bash
.venv/bin/dcfa-ui
# Equivalent: .venv/bin/dcfa-website-demo
```

| Setting | Default / purpose |
|---|---|
| `DCFA_V2_EXECUTOR` | `zerogpu`; explicitly set `local_cuda` for an existing CUDA runtime |
| `DCFA_V2_SPACE` | `GPChen01/dcfa-zerogpu`; HF Space ID, not an arbitrary HTTP destination |
| `DCFA_HF_TOKEN_FILE` | Optional repository-external mode-600 HF credential file; otherwise use the existing HF login cache |
| `DCFA_V2_MODEL_PATH` | Required only for `local_cuda`; exact existing v2 checkpoint |

There is no automatic change of v2 execution location, no CPU/sklearn substitute,
and no use of the provider's v2 API. This checkout's Mac environment has no
Torch/CUDA. A credential or endpoint availability check is not proof of GPU
allocation, sufficient HF quota or successful analysis.

### Remote v2 endpoint and deployment boundary

The new Gradio `/analyze_v2` endpoint accepts bounded data, its existing manifest
and the confirmed compiled plan. It validates HF identity using the supplied
`gr.OAuthToken`, rechecks the v2 development profile and input boundaries, and
runs both stages through the existing ZeroGPU prediction runner. Browser OAuth
requirements remain unchanged. The client uses Gradio's `token` and
`oauth_token` parameters; the latter explicitly passes the credential to the
endpoint for identity verification. The pinned website environment includes
Gradio 6.22.0 / gradio-client 2.6.0 and HF Hub 1.27.0.

The client submits once, records and polls the same queued job, retrieves an
origin-checked ZIP without forwarding credentials through redirects, safely
extracts it, and runs the existing artifact verifier plus confirmed-request and
model checks. Ambiguous timeouts or download failures never resubmit or refit.
Temporary server work is cleaned on success and failure; exported downloads use
the existing Gradio cache expiry. This remains an authorized non-sensitive-data
workflow, not a private-data hosting service.

The user authorized updating `GPChen01/dcfa-zerogpu` to this default and exposing
`/analyze_v2`. The Space requirements pin a committed DCFA revision and include
`tabpfn-client==0.6.1` alongside the existing v2/CUDA dependencies. Its browser flow
uses the in-process v2 executor; `/analyze_v2` remains fixed v2 for authenticated
remote callers. Neither route uses a provider v2 API or a CPU substitute.
Deployment/runtime evidence is recorded separately below; mocked tests alone do
not establish remote GPU execution or quota availability.

### Reports, records and validation evidence

Each daily run has its own directory with `daily_execution.json` and separate
`attempt-1-api` / `attempt-2-v2` directories (or a single v2 attempt).
`attempt.json` preserves a safe error code/stage and quota evidence. Completed
attempts retain the original statistical bundle, report and evidence. The added
`analysis_report.md` and downloadable `analysis_artifacts.zip` include the selected
policy, actual model and any switch, without rewriting the statistical report's
existing identities. Remote progress is recorded in `remote_job.json`.
Ordinary cached follow-ups retain their original specification/backend and never
consult current quota or refit. Historical results are not rewritten.

On 2026-10-03, the new daily coordinator completed two real 128-row synthetic
3.5 runs, each consuming 30,000 tokens and passing artifact verification at
execution. The second run validated the final SDK credential-cleanup fix and
produced the downloadable ZIP. Its account usage changed from 30,000 to 60,000
daily tokens and from 100,000 to 130,000 monthly tokens; limits remained
5,000,000 / 20,000,000. Both used a deterministic confirmed plan without a Gemini
request. This is execution evidence, not statistical validation. The earlier
run remains preserved with its earlier source identity.

Quota-before-run and Stage 1/Stage 2 exhaustion remain injected test conditions.
Fake estimator/transport tests establish switching and error-handling mechanics,
not model quality. The subsequent deployment validation below adds real GPU
evidence; actual server quota exhaustion has not been observed. Never drain the
account for a test.

### Authorized deployment validation (2026-10-03, local date)

- Source `2bc2c9d9e43fcc3ee49dcc32fd4c9db5236c87e9` was deployed to
  `GPChen01/dcfa-zerogpu` in Space commit
  `6c981377d67254a417be755365f3e96c791526b0`. Runtime reached `RUNNING`;
  the live DOM displayed Build `2bc2c9d`, the default policy and updated CSV
  consent, with no Analysis mode selector. `/analyze_v2` is exposed; anonymous
  invocation was rejected as login-required before computation.
- Full available pytest: **252 passed**. `ruff check src tests`,
  `ruff format --check src tests` and `git diff --check` passed. A broader
  repository-root Ruff invocation also scanned unrelated vendored code/notebooks
  and reported their pre-existing style issues; these files were not changed.
- A real 128-row primary call through `execute_space_dataset` completed locally
  with the same Space API/temporary-secret path, without GPU invocation. Actual
  model: `v3.5_default`; artifact verification passed. Usage changed from
  60,000 to 90,000 daily and 130,000 to 160,000 monthly tokens (30,000 consumed).
  Limits remained 5,000,000 daily / 20,000,000 monthly.
- An injected typed quota error then triggered a **real authenticated remote v2
  run** on the deployed ZeroGPU endpoint using the same 128-row synthetic data
  and seed 20260813. Both stages completed; the returned CUDA v2 checkpoint
  identity, unchanged request, numerical bundle and artifacts verified locally.
  The download includes separate failed API/successful v2 attempts, correct
  actual-model/fallback text, evidence and development/residual-dependence warnings.
  Its Gradio job ID was `ca99856884704029b1f1621688da6bbb`.
- The primary and fallback ZIPs contain 17 and 20 files respectively and passed
  credential scans. Local evidence is under the ignored directory
  `artifacts/local/space-daily-deployment-20261003/` (`real-primary/`,
  `injected-quota-real-v2/`, `deployment.json`, `online-default.jpg`).
- This establishes injected-quota-to-real-v2 transport/execution, not a naturally
  exhausted-account event or statistical equivalence. Browser OAuth required a
  fresh sign-in in this session, so a complete signed-in browser CSV/primary run
  was not repeated. The deployed UI and authentication boundary were checked;
  primary computation was measured through the identical code locally.

### Explicit selector acceptance (2026-10-03, local source only)

The restored selector passed 154 affected tests and three additional Space
callback dispatch cases. Local browser checks covered 1280px and 390px layouts,
all three choices, recipient updates and clearing previous consent. The Space
callback and OAuth boundaries were tested locally; the new selector has not been
deployed or replayed in an authenticated live Space browser session.

The ignored `artifacts/local/daily-mode-verification-v1/` directory contains:

- `api/verification.json`: real 128-row 3.5 execution, valid artifacts and ZIP,
  30,000 measured tokens (daily 90,000 -> 120,000; monthly 160,000 -> 190,000).
- `injected-quota-real-v2/verification.json`: injected typed quota error followed
  by real authenticated `GPChen01/dcfa-zerogpu` CUDA v2 execution, valid artifacts
  and ZIP containing both attempts. The injected error is explicitly labeled;
  no real quota exhaustion was induced or observed.
- Desktop/narrow screenshots of the local selector and recipient disclosure.

These are execution checks on synthetic data, not evidence of statistical
quality or equivalence between models. Results retain their evidence IDs,
support status, empirical warnings and `development_only` designation.


## What is ready

Run the website-oriented shell locally:

```bash
.venv/bin/python -m pip install -r requirements-website-demo.lock
.venv/bin/python -m pip install -e . --no-deps
chmod 600 ~/.config/dcfa/tabpfn_api_key
chmod 600 ~/.config/dcfa/gemini_api_key
.venv/bin/dcfa-website-demo
```

The demo defaults to one `gemini-3.6-flash` structured compilation request before
the deterministic runtime. Its natural-language question box supports a mean or
median summary at symbolic low, center, or high treatment, plus directed
contrasts between two distinct labels. Gemini may clarify or block an ambiguous
or out-of-scope question. It cannot choose a backend, add covariates, assess IV
validity, or calculate the displayed value.

The demo provides three synthetic paths:

- a supported median-contrast workflow with a resolvable evidence ID;
- a weak-IV path that keeps empirical warnings attached to the answer;
- an outside-support path that stops before Stage 2 and emits no numerical
  causal answer.

It also provides a local CSV tab for a bounded first-version workflow. The file
must have exactly three numeric columns and 120–256 data rows. By default, the
question states which header is the continuous outcome, continuous treatment,
and scalar instrument. Three optional text overrides can pin any role to an exact
header name. Gemini returns one role mapping constrained to the supplied headers;
local deterministic validation rejects missing, invented, duplicate, or
override-conflicting roles before TabPFN. Extra columns are rejected instead of
being silently dropped as W. Before execution, the user sees separate transfer
summaries and must confirm data authorization: question text, header names, and
optional overrides go to Google Gemini, while selected rows go to Prior Labs.
Uploading the file into the local page alone calls neither service; checking the
box and clicking **Run uploaded CSV** does.

The visitor progress summary is an explicit four-stage projection: understand
the question, check the data, run the analysis, and verify the result. Completed,
current, pending, and blocked states do not imply work that has not happened;
blocked runs identify the stopped visitor stage and a safe next action. Raw state
events, reasons, and tool counts are not sent to the default browser DOM. During
a run, the current stage is shown without a percentage and both submit buttons
are disabled. On desktop, the input occupies the wider column while workflow
state and results remain in one sticky companion panel; the two panels stack on
narrow screens. Local and ZeroGPU launches use the same restrained theme and CSS.

The result view begins with a direction-aware natural-language answer projected
from the validated `QueryResult` and the already validated symbolic Gemini
proposal. It does not recalculate the value. Data support, important mapped
warnings, and the development-only limitation follow without a duplicate
evidence card. The initial answer and detail components stay hidden, and blocked
or failed runs show a reason plus next action instead of an empty result. Display
rounding never changes the evidence-bound raw value. Explicit mappings cover the
allowed claim types, support states, warnings, and blocked errors; an unknown
code fails closed without a number or plot. Gradio, `google-genai`, and
`tabpfn-client` remain lazy optional dependencies, and importing the demo does
not import Hillstrom, Torch, or either service SDK. Every successful supported
path uses the official
managed TabPFN distribution output for both control-function stages. No Client
failure can select sklearn.

For a CSV run, Gemini receives the question, three bounded header names, optional
role overrides, the generic Y/X/Z role contract, and symbolic intervention
labels. It receives zero data rows and zero actual intervention values. A
successful run stores a non-secret `gemini_compilation.json` trace with
the versioned config hash, request/prompt hashes, proposal, interaction ID, token
usage, and latency. The presets contain generated synthetic `Y/X/Z` rows. The
local CSV route sends only its selected Y/X/Z rows and prediction grids to Prior
Labs after explicit confirmation. A supported run consumes both accounts'
service usage and records returned metadata. Credentials stay in external files
and are never copied into artifacts. Managed results remain
`local_development / tabpfn / development_only` because the service checkpoint
and runtime-image hashes are not available to DCFA.

The successful run directory keeps two plot projections. The original
`interventional_summary.png` is the identity-rich audit plot bound by the report
manifest. `website_interventional_summary.png` is derived directly from the same
validated bundle for visitor display and contains human-readable treatment,
mean, median, and cumulative-probability labels without bundle/evidence IDs or
backend identity. Full IDs, unrounded values, warning codes, state events,
service metadata, and the Gemini trace remain available only in the local
artifact and independent verifier. The default page shows “Result verified” and
never includes the complete audit JSON, even in a closed accordion.

## Static prepared-replay architecture

The personal site is a static Astro build on GitHub Pages. It receives only the
committed public-safe projection:

```text
one frozen prompt + redistributable synthetic CSV
  -> one independently verified live DCFA run before publication
  -> hash-bound visitor result and plot
  -> Astro build
  -> GitHub Pages replay with zero provider calls
```

The source bundle lives in `showcase/prepared_demo_v1/`. Freeze refuses to
overwrite an existing directory, and export refuses to replace an existing
visitor projection. Generate a new version rather than tuning or overwriting v1.
Offline verification never imports Gemini or `tabpfn-client`:

```bash
python -m dcfa_showcase verify showcase/prepared_demo_v1
```

The website copies the approved CSV, prompt, plot, and public verification
summary byte-for-byte. Its build-time JSON binds the DCFA release commit and the
hash of every copied asset. The page uses native static HTML disclosure rather
than simulating a live request; the answer and limitations remain in the document
without JavaScript.

## User-owned Colab workflow

`notebooks/DCFA_Custom_Analysis_Colab.ipynb` is the implemented custom-analysis
source. It installs one exact release commit, checks the DCFA source-tree
hash, reads `DCFA_GEMINI_API_KEY` and `DCFA_TABPFN_TOKEN` from Colab Secrets only
when the readiness cell runs, preflights one bounded CSV locally, and requires
separate confirmations before the two external transfers.

The adapter creates owner-only temporary credential files only because the
existing inspected provider boundaries accept files. They are deleted when the
call returns or raises. A successful result is independently verified, scanned
for both exact credential values, and archived for download. Missing secrets,
missing consent, unsupported input, outside support, provider failure, or
evidence failure returns no number and never selects sklearn. The notebook does
not mount Google Drive, launch Gradio, create a tunnel, expose SSH, or promise a
free or persistent runtime. After download, the user deletes the uploaded CSV and
chooses **Runtime → Disconnect and delete runtime**.

On 2026-08-20, `GepingChen/DCFA` became public. Anonymous checks returned 200 for
the GitHub notebook, raw notebook bytes, and the exact Colab URL. The public page
therefore restores `Open in Colab`. The retrieved notebook remains nbformat 4,
pins release `87b2b750d1c9a83497f5b16a7b0597758214d20a`, contains six code cells,
and has no saved outputs. This link/readiness verification did not execute a new
Gemini or managed TabPFN request with user credentials.

## Service and container operation

The default command binds only to `127.0.0.1:7860`. It exposes the demo at `/`,
a non-cached liveness response at `/healthz`, and a readiness response that also
checks whether the configured artifact destination can be created at `/readyz`:

```bash
.venv/bin/dcfa-website-demo
curl --fail http://127.0.0.1:7860/healthz
curl --fail http://127.0.0.1:7860/readyz
```

`127.0.0.1:7860` is the authoritative default local entry. Startup checks that
the configured address is available and reports a clear conflict instead of
leaving an older instance to represent the current source. The page displays the
short current Git revision when launched from the checkout. A packaged image
must receive the revision explicitly at build time.

Supported settings:

| Variable | Default | Purpose |
|---|---:|---|
| `DCFA_SERVER_NAME` | `127.0.0.1` | Bind address; use `0.0.0.0` only inside a reviewed container/service |
| `PORT` | `7860` | TCP port, validated in the range 1–65535 |
| `DCFA_OUTPUT_ROOT` | `artifacts/local/website-demo` | Ignored local directory for immutable result bundles |
| `DCFA_TABPFN_TOKEN_FILE` | `~/.config/dcfa/tabpfn_api_key` | External mode-600 Prior Labs token file |
| `DCFA_GEMINI_API_KEY_FILE` | `~/.config/dcfa/gemini_api_key` | External mode-600 Gemini API key file |
| `DCFA_WEBSITE_GEMINI_CONFIG_FILE` | repository profile | Versioned prompt/model/schema JSON; container defaults to `/app/evaluation/configs/website_demo_gemini_v2.json` |
| `DCFA_BUILD_REVISION` | current checkout or `unknown` | Seven-to-twelve character Git revision shown on the page; set explicitly for an image build |
| `DCFA_ACCESS_LOG` | `0` | Set to `1` only when request logs are operationally required |

Build and run the checked-in non-root container:

```bash
docker build \
  --build-arg DCFA_BUILD_REVISION="$(git rev-parse --short=8 HEAD)" \
  -t dcfa-development-demo:local .
docker run --rm --init \
  -p 127.0.0.1:7860:7860 \
  -e DCFA_GEMINI_API_KEY_FILE=/run/secrets/gemini_api_key \
  -e DCFA_TABPFN_TOKEN_FILE=/run/secrets/tabpfn_api_key \
  -v "$HOME/.config/dcfa/gemini_api_key:/run/secrets/gemini_api_key:ro" \
  -v "$HOME/.config/dcfa/tabpfn_api_key:/run/secrets/tabpfn_api_key:ro" \
  -v dcfa-demo-artifacts:/app/artifacts \
  dcfa-development-demo:local
```

Or use the equivalent local Compose profile:

```bash
export DCFA_TABPFN_TOKEN_FILE="$HOME/.config/dcfa/tabpfn_api_key"
export DCFA_GEMINI_API_KEY_FILE="$HOME/.config/dcfa/gemini_api_key"
export DCFA_BUILD_REVISION="$(git rev-parse --short=8 HEAD)"
docker compose up --build
docker compose ps
curl --fail http://127.0.0.1:7860/healthz
curl --fail http://127.0.0.1:7860/readyz
```

The container uses one process and the UI serializes analysis with a queue of at
most eight pending requests. Run directories are reserved atomically. Generated
artifacts live in an ignored directory or named volume; remove them only as an
explicit maintenance action because DCFA never overwrites prior runs. The
service adds basic no-sniff, referrer, and device-permission headers. TLS, rate
limiting, authentication, external retention, and reverse-proxy policy remain
the responsibility of any later reviewed host.

Readiness requires writable artifact storage, a valid versioned Gemini profile,
and valid owner-only files for both Gemini and managed TabPFN. The demo accepts
the three built-in synthetic scenarios or one local CSV with exactly three
selected numeric Y/X/Z columns and
120–256 rows, plus a bounded
unsigned 32-bit seed. CSVs with extra columns, missing/non-finite values, or fewer
than 20 distinct Y/X values are rejected before managed-client access. It has no
Hillstrom route, no general causal-method router, and no sklearn fallback. A
supported run uses three managed predictions; the outside-support path stops
after the Stage 1 distribution and emits no Stage 2 result or numerical answer.

## Local acceptance checks

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest tests/integration/test_website_demo.py
.venv/bin/python -m pytest
docker inspect --format '{{.Config.User}}' dcfa-development-demo:local
```

The website-specific tests execute all three guided paths and the standard CSV
path against a contract-faithful fake managed service, preserve warnings,
assert visitor/artifact value parity after display rounding, scan visitor output
and default Gradio config for forbidden machine fields, verify both plot
projections, and assert that outside-support execution emits no result directory
or number,
exercise concurrent directory reservation, reject invalid controls/CSV/consent
before fit, assert one-call/no-retry Gemini behavior, and validate `/healthz`,
`/readyz`, and service headers. Before handoff, also
inspect the running page at a desktop viewport and at 390 px, execute all three
paths, check for horizontal overflow and console errors, and independently
verify fresh strong/weak artifact directories with `dcfa verify-artifacts`.

## Publication gate

Publishing the website tool does not publish a scientific result. Release requires
the frozen current-source live artifact, public projection verification, notebook
static validation, cross-repository asset hashes, no-secret/private-path scans,
desktop/mobile/keyboard/reduced-motion/no-JavaScript review, both repository
quality gates, verified pushes, and the reviewed live GitHub Pages route. Public
copy must keep the replay precomputed and all prepared/Colab output
`development_only`. A locked Track T headline remains blocked on a reproducible
real TabPFN runtime, checkpoint hash, and image digest.
