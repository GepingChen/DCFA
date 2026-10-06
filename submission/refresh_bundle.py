"""Package current submission prose/report while retaining an accepted runtime.

This presentation-only path reads an existing ZIP and never rebuilds models,
wheels, source archives, examples, or saved results. Standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION_FILES = {
    'README.md': 'submission/README.md',
    'PROJECT.md': 'submission/PROJECT.md',
    'DEMO_SCRIPT.md': 'submission/DEMO_SCRIPT.md',
    'reports/cigarette-tabpfn35.html': 'submission/reports/cigarette-tabpfn35.html',
    'report_tools/generate_example_report.py': 'submission/generate_example_report.py',
}


def refresh(base_zip: Path, output: Path) -> None:
    revision = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True
    ).strip()
    replacements = {name: (ROOT / path).read_bytes() for name, path in PRESENTATION_FILES.items()}
    replacements['START_HERE.txt'] = (
        'Agentic TabCF — start here\n\n'
        'Extract this entire ZIP. Double-click reports/cigarette-tabpfn35.html\n'
        'or choose File > Open File in your browser. No installation, API key,\n'
        'service, or internet connection is needed to read this saved report.\n\n'
        'README.md explains the product and optional live installation.\n'
        'PROJECT.md explains the statistical scope. Live computation requires\n'
        'your own authorized provider credentials and available quota.\n\n'
        'All results remain development_only. This package is prepared for\n'
        'upload; contest submission, eligibility and live deployment are separate.\n'
    ).encode()
    with zipfile.ZipFile(base_zip) as source:
        files = [n for n in source.namelist() if not n.endswith('/')]
        roots = {n.split('/')[0] for n in files}
        if len(roots) != 1:
            raise ValueError('Expected one top-level submission directory.')
        prefix = roots.pop() + '/'
        acceptance = json.loads(source.read(prefix + 'PACKAGE_ACCEPTANCE.json'))
        acceptance['presentation_update'] = {
            'package_name': output.stem,
            'source_commit': revision,
            'base_package': base_zip.name,
            'updated_files': list(replacements),
            'scope': 'Current prose and offline report; original runtime and results retained byte-for-byte.',
            'verification': 'ZIP integrity, retained-member byte equality, and presentation-file equality checked by this script.',
            'runtime_validation': 'Original runtime acceptance records are historical; this script does not execute models or install dependencies.',
            'browser_validation': 'Local file rendering and interaction were not verified: browser tool security policy blocks file URLs.',
            'release_status': 'Development-only local upload package; no contest submission or deployment implied.',
        }
        replacements['PACKAGE_ACCEPTANCE.json'] = (json.dumps(acceptance, indent=2) + '\n').encode()
        members = {n[len(prefix):]: source.read(n) for n in files}
    members.update(replacements)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in sorted(members.items()):
            target.writestr(output.stem + '/' + name, data)
    with zipfile.ZipFile(output) as target:
        if target.testzip() is not None:
            raise ValueError('ZIP integrity check failed.')
        for name, data in members.items():
            if target.read(output.stem + '/' + name) != data:
                raise ValueError(f'Packaged bytes differ: {name}')
    print(f'{output}: {len(members)} files; {len(members) - len(replacements)} retained unchanged.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-zip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    refresh(args.base_zip, args.output)


if __name__ == '__main__':
    main()
