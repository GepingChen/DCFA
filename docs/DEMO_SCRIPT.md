# Three-minute local development demo

This script demonstrates engineering behavior, not publishable causal results.

## 0:00–0:35 — Scope

Open the architecture diagram. Explain that the public product supports one
continuous treatment, one continuous outcome, one scalar instrument, and no
baseline covariates. Point out that Hillstrom is an offline randomized-policy
track and cannot validate TabCF.

## 0:35–1:15 — Supported result with evidence

Run:

```bash
dcfa tabcf-demo --scenario strong_iv \
  --output-dir artifacts/local/demo-strong
dcfa verify-artifacts artifacts/local/demo-strong
```

Show one query value, its evidence ID, the execution/backend/evidence markers,
and the same bundle-derived report and plot. State clearly that the local
sklearn backend is an engineering fallback and not TabCF.

## 1:15–1:45 — Correct failure

Run:

```bash
dcfa tabcf-demo --scenario support_violation \
  --output-dir artifacts/local/demo-blocked
dcfa tabcf-demo --scenario nonempty_w \
  --output-dir artifacts/local/demo-blocked-w
```

Show `OUTSIDE_SUPPORT` and `UNSUPPORTED_BASELINE_COVARIATES`. Emphasize that no
numerical causal answer or result directory is produced for these requests.

## 1:45–2:25 — Agent workflow isolation

Run:

```bash
dcfa agent-benchmark --runs 5 \
  --output artifacts/local/agent-benchmark-recorded-v5.json
```

Show 24 cases, five runs nested within each case, identical recorded tool
fixtures, the gold-aware forbidden-numeric safety field, per-case/worst-run
outcomes, and the case-level bootstrap comparison. Describe the output as
test-only orchestration evidence, not estimator or business-lift evidence.

## 2:25–3:00 — Offline policy boundary and honest blockers

Show the frozen-policy/test-gate ordering in a verified `hillstrom-demo` audit
and the four semi-synthetic DGP labels. State that current inputs are generated
and not real Hillstrom. Close with the six release/evaluation blockers in the
README: locked real TabPFN, manuscript DGP mapping, approved Fulton data,
approved Hillstrom data, calibrated Track T diagnostic thresholds, and a frozen
live LLM/prompt manifest.
