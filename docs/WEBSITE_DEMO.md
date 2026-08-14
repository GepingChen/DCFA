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
.venv/bin/dcfa-website-demo
```

The demo provides three frozen synthetic paths:

- a supported median-contrast workflow with a resolvable evidence ID;
- a weak-IV path that keeps empirical warnings attached to the answer;
- an outside-support path that stops before Stage 2 and emits no numerical
  causal answer.

The visible state trace is produced by `CausalAgentRuntime`; it is not a
decorative reconstruction. The answer table is projected from the validated
`QueryResult` and never recomputed in the UI. Gradio and `tabpfn-client` remain
lazy optional dependencies, and importing the demo does not import Hillstrom,
Torch, or the Client package. Every successful supported path uses the official
managed TabPFN distribution output for both control-function stages. No Client
failure can select sklearn.

The presets contain generated synthetic `Y/X/Z` rows only. A supported run sends
those rows and prediction grids to Prior Labs, consumes account usage credits,
and records returned service metadata. The credential stays in the external
token file and is never copied into an artifact. Managed results remain
`local_development / tabpfn / development_only` because the service checkpoint
and runtime-image hashes are not available to DCFA.

## Static-site architecture

The personal site is a static Astro build on GitHub Pages, so it cannot execute
the Python agent itself. The intended boundary is:

```text
Astro project page on GitHub Pages
  -> iframe or direct demo link
  -> separately hosted Gradio service
  -> typed DCFA agent runtime
  -> deterministic TabCF IV adapter
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

Supported settings:

| Variable | Default | Purpose |
|---|---:|---|
| `DCFA_SERVER_NAME` | `127.0.0.1` | Bind address; use `0.0.0.0` only inside a reviewed container/service |
| `PORT` | `7860` | TCP port, validated in the range 1–65535 |
| `DCFA_OUTPUT_ROOT` | `artifacts/local/website-demo` | Ignored local directory for immutable result bundles |
| `DCFA_TABPFN_TOKEN_FILE` | `~/.config/dcfa/tabpfn_api_key` | External mode-600 Prior Labs token file |
| `DCFA_ACCESS_LOG` | `0` | Set to `1` only when request logs are operationally required |

Build and run the checked-in non-root container:

```bash
docker build -t dcfa-development-demo:local .
docker run --rm --init \
  -p 127.0.0.1:7860:7860 \
  -e DCFA_TABPFN_TOKEN_FILE=/run/secrets/tabpfn_api_key \
  -v "$HOME/.config/dcfa/tabpfn_api_key:/run/secrets/tabpfn_api_key:ro" \
  -v dcfa-demo-artifacts:/app/artifacts \
  dcfa-development-demo:local
```

Or use the equivalent local Compose profile:

```bash
export DCFA_TABPFN_TOKEN_FILE="$HOME/.config/dcfa/tabpfn_api_key"
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

The demo accepts only the three built-in synthetic scenarios, 120–256 generated
rows, and a bounded unsigned 32-bit seed. It has no upload surface, no Hillstrom
route, no general causal-method router, and no sklearn fallback. A supported run
uses three managed predictions; the outside-support path stops after the Stage 1
distribution and emits no Stage 2 result or numerical answer.

## Local acceptance checks

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/python -m pytest tests/integration/test_website_demo.py
.venv/bin/python -m pytest
docker inspect --format '{{.Config.User}}' dcfa-development-demo:local
```

The website-specific tests execute all three paths against a contract-faithful
fake managed service, preserve warnings,
assert that outside-support execution emits no result directory or number,
exercise concurrent directory reservation, reject invalid controls before fit,
and validate `/healthz`, `/readyz`, and service headers. Before handoff, also
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
3. preserve evidence IDs, warnings, support blocking, and source-artifact links
   in the hosted view;
4. review the final HTTPS origin, framing policy, latency, concurrency limit,
   privacy text, and mobile layout;
5. add the reviewed URL to the personal-site project page and run that site's
   `npm run verify` gate before any authorized publication.

Until those steps are complete, this code is suitable for local review,
screenshots, and a clearly labeled engineering walkthrough—not a published
TabCF result.
