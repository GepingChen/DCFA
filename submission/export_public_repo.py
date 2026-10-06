# Copyright 2026 Geping Chen. Licensed under the Apache License, Version 2.0.
"""Prepare a local readable-source contest repository without publishing it."""

from __future__ import annotations

import argparse
import io
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def write_member(output: Path, name: str, data: bytes) -> None:
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe archive member: {name}")
    destination = output.joinpath(*relative.parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


def export(archive: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as package:
        files = [name for name in package.namelist() if not name.endswith("/")]
        roots = {name.split("/")[0] for name in files}
        if len(roots) != 1:
            raise ValueError("Expected one top-level submission directory.")
        prefix = roots.pop() + "/"
        for member in files:
            name = member[len(prefix) :]
            if name in {
                "LICENSE",
                "NOTICE",
                "PARENT_MIT_LICENSE",
                "TABCF_MIT_LICENSE",
                "parent_commit.txt",
                "tabcf_commit.txt",
                "PROJECT.md",
                "DEMO_SCRIPT.md",
                "FORM_TEXT.md",
                "results/browser-acceptance.json",
                "results/browser-confirmation.jpg",
                "results/browser-result.jpg",
                "results/browser-report-detail.jpg",
            } or name.startswith(
                ("wheels/", "examples/", "reports/", "results/cigarette-35/attempt-1-api/")
            ):
                write_member(output, name, package.read(member))

        # Export installable parent source without unrelated experiments, logs,
        # traces, historical submission material or generated research artifacts.
        with tarfile.open(fileobj=io.BytesIO(package.read(prefix + "parent_source.tar"))) as source:
            for member in source.getmembers():
                if member.isfile() and (
                    member.name.startswith("src/")
                    or member.name in {"pyproject.toml", "README.md", "LICENSE"}
                ):
                    stream = source.extractfile(member)
                    assert stream is not None
                    write_member(output, "vendor/dcfa/" + member.name, stream.read())
                elif member.isfile() and member.name == "submission/pyproject.toml":
                    stream = source.extractfile(member)
                    assert stream is not None
                    write_member(output, "pyproject.toml", stream.read())

        # The installed entry wheel contains the original runtime configs, which
        # the historical source archive did not include in its entry package.
        wheel_name = prefix + "wheels/agentic_tabcf_entry-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(io.BytesIO(package.read(wheel_name))) as wheel:
            for name in wheel.namelist():
                if name.startswith("agentic_tabcf_entry/") and not name.endswith("/"):
                    write_member(output, "src/" + name, wheel.read(name))
        write_member(output, "requirements.lock", package.read(prefix + "requirements.lock"))

    write_member(output, "README.md", (ROOT / "submission/PUBLIC_README.md").read_bytes())
    project = (output / "PROJECT.md").read_text()
    project = project.replace(
        "The v6 submission ZIP includes this report and the current\n"
        "documentation. Earlier ZIPs remain unchanged.",
        "The focused source export includes this report and current documentation.\n"
        "The separate local v6 ZIP retains the larger historical measurement package.",
    ).replace(
        "## What the included measurements establish", "## Separate local development measurements"
    )
    project = project.replace(
        "The five-seed synthetic comparison uses",
        "The separate local ZIP's five-seed synthetic comparison uses",
    ).replace("bundled comparison\nresults", "separate local ZIP's comparison\nresults")
    (output / "PROJECT.md").write_text(project)
    script = (
        (output / "DEMO_SCRIPT.md")
        .read_text()
        .replace(
            "public/synthetic examples and five-seed comparison, including regressions or\n"
            "  missing pairs.",
            "public/synthetic examples. If showing the separate local five-seed comparison,\n"
            "  retain regressions or missing pairs.",
        )
    )
    (output / "DEMO_SCRIPT.md").write_text(script)
    write_member(
        output,
        ".gitignore",
        (
            b".DS_Store\n.venv/\n.venv-*/\n.env\n.env.*\n__pycache__/\n*.py[cod]\n"
            b"*.egg-info/\nbuild/\ndist/\n.pytest_cache/\n.ruff_cache/\n"
            b"artifacts/local/\nlogs/\n*.log\n"
        ),
    )
    write_member(
        output,
        "SOURCE_LAYOUT.md",
        (
            b"# Readable source export\n\n"
            b"Root src/ and pyproject.toml are the Apache-2.0 thin entry. Runtime files\n"
            b"and configs were copied unchanged from the accepted entry wheel.\n"
            b"vendor/dcfa/ contains the installable MIT parent source from parent_source.tar\n"
            b"at parent_commit.txt; its source and package assets were copied unchanged.\n"
            b"The original accepted wheels and dependency lock remain the default install\n"
            b"path. To rebuild locally: python -m pip wheel --no-deps ./vendor/dcfa .\n\n"
            b"TabCF's original separate source archive is retained in the local v6 ZIP.\n"
            b"The managed API entry executes the bundled DCFA adapter and does not import\n"
            b"that separate source tree. Its MIT license and recorded commit remain here.\n"
            b"No licenses were changed. Code outside the entry's permitted tool surface\n"
            b"is not exposed by agentic-tabcf.\n\n"
            b"Included example results are the original public cigarette development run.\n"
            b"The offline HTML is a presentation derivative; neither export refits models.\n"
            b"The full comparison, historical source archives and installation logs remain\n"
            b"in the separate local ZIP rather than this focused source repository.\n\n"
            b"This directory has not been published or submitted. Contest acceptance of\n"
            b"the Apache entry with separate MIT dependencies has not been confirmed.\n"
        ),
    )
    print(f"Prepared {output}: {sum(p.is_file() for p in output.rglob('*'))} files; not published.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    export(args.archive, args.output_dir)


if __name__ == "__main__":
    main()
