# Development workflow demo

The portfolio demo is implemented as a repeatable local service, but it is
intentionally not a public TabCF deployment. It is a presentation layer over
the existing typed agent runtime and deterministic TabCF Analyst development
workflow.

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
must have exactly three numeric columns, 120–256 data rows, and explicit mappings
for continuous outcome Y, continuous treatment X, and scalar instrument Z. Extra
columns are rejected instead of being silently dropped as W. Before execution,
the user sees separate transfer summaries and must confirm data authorization:
question text goes to Google Gemini, and selected rows go to Prior Labs. The
guided question field likewise states before submission that its text goes to
Gemini and warns against private or sensitive information. Uploading the file
into the local page alone calls neither service; checking the box and clicking
**Run uploaded CSV** does.

The visitor progress summary is an explicit four-stage projection: understand
the question, check the data, run the analysis, and verify the result. Completed,
current, pending, and blocked states do not imply work that has not happened;
blocked runs identify the stopped visitor stage and a safe next action. Raw state
events, reasons, and tool counts are not sent to the default browser DOM. During
a run, the current stage is shown without a percentage and both submit buttons
are disabled.

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

Gemini receives the question, generic Y/X/Z role contract, and symbolic
intervention labels. It receives zero data rows and zero actual intervention
values. A successful run stores a non-secret `gemini_compilation.json` trace with
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

## Static-site architecture

The personal site is a static Astro build on GitHub Pages, so it cannot execute
the Python agent itself. The intended boundary is:

```text
Astro project page on GitHub Pages
  -> iframe or direct demo link
  -> separately hosted Gradio service
  -> bounded Gemini specification compiler (question only)
  -> typed DCFA agent runtime
  -> deterministic TabCF IV adapter -> managed TabPFN (Y/X/Z rows)
```

An Astro component is prepared at
`/Users/chgp/Dropbox/nova/website/src/components/DcfaDemoEmbed.astro`. It is not
imported by any public page yet. After a reviewed HTTPS demo endpoint exists, a
project page can use it as follows:

```astro
---
import DcfaDemoEmbed from '../components/DcfaDemoEmbed.astro';
---

<DcfaDemoEmbed demoUrl="https://reviewed-demo-host.example/" />
```

Use a direct-link fallback if the eventual host disallows framing. Do not point
the component at a temporary share URL.

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
| `DCFA_WEBSITE_GEMINI_CONFIG_FILE` | repository profile | Versioned prompt/model/schema JSON; container defaults to `/app/evaluation/configs/website_demo_gemini_v1.json` |
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

The current local execution is real managed TabPFN mechanics but explicitly
`local_development / tabpfn / development_only`. It is not bitwise-reproducible
Track T evidence and is not eligible for a Track T headline or finished public
causal-demo claim. Before linking the personal website to a released TabCF demo:

1. supply and validate the frozen real TabPFN runtime, checkpoint hash, and
   image digest;
2. rerun and independently verify the chosen public preset under that locked
   backend;
3. preserve evidence IDs, warning codes, and source-artifact links in the
   operator artifact while keeping equivalent warnings and support blocking in
   the hosted visitor view;
4. review the final HTTPS origin, framing policy, latency, concurrency limit,
   privacy text, and mobile layout;
5. add the reviewed URL to the personal-site project page and run that site's
   `npm run verify` gate before any authorized publication.

Until those steps are complete, this code is suitable for local review,
screenshots, and a clearly labeled engineering walkthrough—not a published
TabCF result.
