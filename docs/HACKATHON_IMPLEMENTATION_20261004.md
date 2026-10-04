# Parent workflow and local submission implementation — 2026-10-04

This is development work and a local entry package, not a release, deployment or
contest submission. Original v2 previews and their identities remain unchanged.

## Implemented changes

- Optional local CSV dialogue reuses the Space's reviewed-plan workflow. Local
  credential files replace the Space's OAuth/temporary-key adapter; Space
  authorization remains unchanged. A fixed API-only entry cannot switch to v2.
- Website execution records client stage/total duration and backend observations;
  unavailable provider-server time is explicitly null. Daily attempts retain
  measured duration, selected/actual model and API usage.
- `dcfa compare-tabpfn` measures the five planned paired seeds, writes each arm
  incrementally and resumes without silently resubmitting completed or ambiguous
  attempts. Risk is the canonical CDF-interpolated P(Y <= sample Y median).
- `submission/` builds a thin Apache-2.0 entry against an identified MIT parent
  wheel. It includes source, runtime prompt configs, separate notices/licenses,
  public/synthetic examples and a demonstration script. Parent licensing is unchanged.

## Distribution interface

The published PyPI `tabpfn==9.0.0` wheel was inspected. FullSupportBarDistribution
inherits BarDistribution.cdf; the formula matches the existing NumPy adapter.
Full-support means have separate tail handling and continue to use the service's
mean output. No estimator formula changed. A direct numerical check against the
published method (seed 20261004, 7 rows each, 2/8/64 bins, irregular borders and
boundary/outside points) had maximum absolute error 3.33e-16 in float64.
The reference Torch import emitted a NumPy ABI warning, so tensors were explicitly
constructed from lists and checked through `tolist()`, not a NumPy/Torch bridge.
Source and check output remain in the ignored local implementation directory.

## Measured model comparison

All five paired runs completed using the same statistical runtime commit
`cd48df92` (full identity is in `runtime_commit.txt`) and independent verification.
The source export is required because the deployed v2 runtime is older than the
new local driver; the existing source-identity verifier was not weakened.
Both arms use the same archived parent estimator, settings, input rows and grids.
The current changes affect the driver/presentation, not the compared estimator.

Artifacts: `artifacts/local/hackathon-implementation-v2/comparison/`.
Each reported metric resolves to `comparison:<seed>:<mode>:<metric>` in the
measurement/summary JSON and from there to its validated result bundle. Aggregate
IDs are `comparison:paired:<metric>` with their contributing arm IDs.

| Metric | Mean RMSE: 3.5 | Mean RMSE: v2 | Paired difference | Seed SE |
|---|---:|---:|---:|---:|
| CDF | 0.0194028 | 0.0208968 | -0.00149402 | 0.00443355 |
| Mean | 0.139167 | 0.147485 | -0.00831763 | 0.0229651 |
| Quantile | 0.211730 | 0.210513 | +0.00121657 | 0.0602752 |
| Probability | 0.0485987 | 0.0537299 | -0.00513121 | 0.0130973 |

Negative differences favor 3.5; quantile error increased slightly on average.
This five-seed, single-DGP result supports neither general superiority nor formal
Track T validation. It is not an agent benchmark. All warnings remain in bundles.

The five completed API arms consumed 150,000 computation tokens (30,000 each).
Their client wall times ranged 19.04–97.25 seconds; remote CUDA v2 ranged
5.36–7.30 seconds. These include distinct hosting/queue/finalization costs and
are not intrinsic model-speed measurements. Remote server-stage timing and a
comparable token cost for v2 are unavailable.

An earlier attempt in `hackathon-implementation-v1/comparison/` was interrupted
after source-identity failures: local files changed during the first API run,
and the deployed v2 source differed from the worktree. Those attempted calls and
records were retained, not counted among the five completed pairs. The subsequent
run uses a stable source export for both arms. The 150,000 figure excludes those
aborted attempts and the separate cigarette/installation acceptance runs.

## Real cigarette browser acceptance

The local API-only browser journey completed with the original 144-row public
CSV, seed 20260920, exact prices 100/120, quartiles and the explicitly requested
exceedance threshold 120 packs/person/year. Gemini first requested missing roles
and prices; textual confirmation returned a button instruction without fitting.
The dedicated button produced a real v3.5_default report. Downloaded ZIP readback
passed independent verification with 656 evidence records, run
`run_72e0e4a81aac75e7a91f3dbd`, bundle `bundle_1ad75ce59ff0d82cc0aaa651`.
A subsequent ordinary follow-up returned the cached report; the run count stayed 1.
Warnings, original/log units and 120-minus-100 direction remain visible.

The analysis/report client wall time was 170.389 seconds, including three API
predictions costing 30,000 computation tokens. Gemini made three planning calls;
its separate planning latency is not part of that analysis timer. Server time
was unavailable. Screenshots and `browser-acceptance.json` are preserved under
`artifacts/local/hackathon-implementation-v1/`; the original v2 assets are untouched.

## Verification and delivery

The original focused checks passed 25/25 after repairing the obsolete callback
fake. The final full suite passed 273/273. A subsequently added measurement-write-failure
regression check passed separately (one additional test). Subsequent local-dialogue/entry,
daily-mode, Space, website and comparison checks passed 135/135, including the
new recovery and fixed-policy cases. Final packaging and real-browser acceptance
are recorded separately in the local delivery artifacts; a successful source test
alone does not establish either of those outcomes.

No new source hash, freeze, snapshot baseline or promotion gate was introduced.
Existing independent verification remains strict. No new public repository,
Space deployment, contest terms acceptance or contest submission was performed.
