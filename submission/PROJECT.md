# Project description

Many interventions change the shape of an outcome distribution, not just its
mean. Agentic TabCF makes a bounded continuous-treatment instrumental-variable
analysis accessible through a reviewed natural-language workflow.

## Architecture

1. Gemini compiles a question into explicit Y/X/Z roles, units and estimands.
2. The user reviews the plan and confirms with a dedicated button.
3. TabPFN-3.5 estimates F(X|Z); deterministic code constructs control ranks V.
4. TabPFN-3.5 estimates E[Y|X,V] and F(Y|X,V).
5. Deterministic integration produces interventional distributions. Quantiles,
   probabilities and directed contrasts come from the validated result bundle.
6. Reports, plots and downloads retain evidence, empirical diagnostics and warnings.

The LLM performs no numerical causal calculations. Ordinary follow-ups use the
cached report; a different analysis requires reset. Unsupported treatment types,
non-empty W and unsupported interventions are rejected. The statistical method
predates this entry: new work is the managed 3.5 workflow, user journey, measurements
and reproducible packaging, not an invention of TabCF.

## Evidence and limitations

The real cigarette example describes equally weighted state-year aggregates under
maintained IV assumptions. Income, state/year effects and within-state dependence
are not resolved by this bounded no-W model. Diagnostics do not establish IV
validity. There are no claims of individual effects, significance or policy benefit.

The five-seed synthetic comparison uses a fixed known DGP and shared inputs,
estimands and grids. It compares existing v2 CUDA and 3.5 API execution, so timing
includes different hosting environments. Null findings, regressions, refusals and
missing pairs remain visible. This small development measurement is not formal
Track T validation or evidence of agent superiority. See the measured report.

Hillstrom, general method routing, automatic IV discovery and autonomous policy
deployment are outside the submission. Saved previews and live execution are
separate; real provider access requires credentials and available account quota.
