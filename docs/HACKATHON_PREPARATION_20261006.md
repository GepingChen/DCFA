# Submission preparation — 2026-10-06

Scope: local preparation, documentation, source export and the repository's
authorized commit/push. No new remote repository, license change, terms acceptance,
video upload, contest submission, deployment or model call was performed.

## Current official requirements

Read the live [hackathon page](https://platform.priorlabs.ai/hackathon-3.5) and its
Terms & Conditions modal on 2026-10-06. Section 3 requires TabPFN-3.5 as a core
component, a public Apache-2.0 source repository, a sufficiently detailed project
description, runnable code/instructions and input data or a public data URL.
Video is optional. The deadline is 2026-10-06 23:59 CEST / 16:59 America/Chicago;
provider receipt time is decisive. The latest update before closing counts.

The live unauthenticated login page offered Email/Password, GitHub, Google and
Sign up. The authenticated submission form and its exact controls/limits were not
observed. No participant age, rights, social profile or terms acceptance was inferred.
GitHub's public repository API reported `GepingChen/DCFA` as public with MIT;
that root repository was not relabeled Apache for the competition.

## Prepared material

- `HACKATHON_SUBMISSION_GUIDE_ZH.md`: complete Chinese tutorial with publishing,
  optional live reproduction/video, form mapping and receipt verification.
- `submission/FORM_TEXT.md`: title, one-line/short/full English descriptions and
  instructions for actual links and participant-owned fields.
- `submission/CIGARETTE_PROMPTS.md`: external-key-file local instructions and
  the complete existing specification prompt, including the requested threshold.
- `submission/PUBLIC_README.md` and `submission/export_public_repo.py`: a focused
  local repository export with readable Apache entry/config source and the
  installable MIT parent source, plus original wheels/lock and the public example.
- Presentation refresh includes the guide/text/correct local prompt. The v6 ZIP
  retains historical runtime/source/results; v3/v4/v5 remain untouched.

The local source export omits historical full source archives, comparison bulk
outputs and installation logs; they remain in the separate full local ZIP.
The export includes the existing public cigarette result/evidence and historical
browser acceptance. Root Apache licensing applies to the entry/new material;
MIT dependency notices and the separate data/model terms remain. Organizer
acceptance of that combination has not been confirmed.

## Verification

- Ruff check and format check passed for `export_public_repo.py` and
  `build_bundle.py`. Refresh ran successfully with ZIP integrity and byte-readback
  checks; its original-member preservation check distinguishes changed prose
  from unchanged runtime/results.
- The actual local source export rebuilt both wheels using
  `.venv-hackathon-validation/bin/python -m pip wheel --no-deps ./vendor/dcfa .`
  with a separate output directory. The source matched all original accepted
  runtime/package members: 3 entry members and 68 parent members.
- Original dependency lock, wheel installation identities, licenses, report and
  parent/TabCF commit references were retained. Text secret-pattern/local-path
  inspection found no credential match or local user path in the export;
  installation logs were excluded. This is scoped inspection, not a security proof.
- The complete example prompt is 540 characters, below the existing 1000-character
  conversation limit. All 37 HTML fragment links resolve to element IDs.
- Served the exported unchanged report on localhost with Python's static server.
  Browser observation verified the saved-3.5/development labels, readable layout,
  result sections and warnings. Clicking a displayed median opened its original
  evidence anchor and expanded technical details. No provider call was made.

No new hash, research freeze, numerical baseline, approval layer or gate was
added. The full statistical/runtime suite was not rerun for this packaging/prose
change. Historical live installation and model-run evidence remains historical;
these checks do not establish a fresh live 3.5 run, final Track T evidence, public
contest acceptance or formal submission.

Next external step: publish the reviewed dedicated source directory under the
participant's chosen public repository, then have the participant accept terms,
fill the official form and verify a submitted entry before the deadline.
