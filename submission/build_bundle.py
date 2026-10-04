# Copyright 2026 Geping Chen. Licensed under the Apache License, Version 2.0.
"""Export an identified parent commit into a local wheel-based entry bundle."""

import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        archive = temp / "parent.tar"
        subprocess.run(
            ["git", "archive", "--format=tar", "-o", str(archive), commit], cwd=root, check=True
        )
        source = temp / "parent"
        source.mkdir()
        with tarfile.open(archive) as stream:
            stream.extractall(source, filter="data")
        entry = source / "submission"
        configs = entry / "src/agentic_tabcf_entry/configs"
        configs.mkdir()
        for name in ("website_demo_gemini_v2.json", "space_csv_dialogue_v1.json"):
            shutil.copy2(source / "evaluation/configs" / name, configs / name)
        wheels = out / "wheels"
        for project in (source, entry):
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    "--no-deps",
                    str(project),
                    "--wheel-dir",
                    str(wheels),
                ],
                check=True,
            )
        for name in ("README.md", "PROJECT.md", "DEMO_SCRIPT.md", "LICENSE", "NOTICE"):
            shutil.copy2(entry / name, out / name)
        shutil.copy2(source / "requirements-website-demo.lock", out / "requirements.lock")
        with (out / "requirements.lock").open("a") as stream:
            stream.write("\n--find-links ./wheels\ndcfa==0.1.0\nagentic-tabcf-entry==0.1.0\n")
        shutil.copy2(source / "LICENSE", out / "PARENT_MIT_LICENSE")
        # git archive omits submodule contents. Export the parent's recorded
        # TabCF commit, not whatever happens to be checked out locally.
        tabcf_commit = subprocess.check_output(
            ["git", "ls-tree", commit, "third_party/TabCF"], cwd=root, text=True
        ).split()[2]
        tabcf_repository = root / "third_party/TabCF"
        license_text = subprocess.check_output(
            ["git", "show", f"{tabcf_commit}:LICENSE"], cwd=tabcf_repository
        )
        (out / "TABCF_MIT_LICENSE").write_bytes(license_text)
        subprocess.run(
            ["git", "archive", "--format=tar", "-o", str(out / "tabcf_source.tar"), tabcf_commit],
            cwd=tabcf_repository,
            check=True,
        )
        (out / "tabcf_commit.txt").write_text(tabcf_commit + "\n")
        shutil.copytree(source / "examples/cigarette_demand_small", out / "examples/cigarette")
        (out / "parent_commit.txt").write_text(commit + "\n")
        # Retain source alongside the wheels; no separate statistical implementation.
        shutil.copy2(archive, out / "parent_source.tar")
    import numpy as np

    from dcfa.tabcf_iv.development_dgp import generate_development_iv

    d = generate_development_iv(n=128, seed=20261004, instrument_strength=1.6)
    np.savetxt(
        out / "examples/synthetic.csv",
        np.column_stack([d.columns[k] for k in ("Y", "X", "Z")]),
        delimiter=",",
        header="Y,X,Z",
        comments="",
    )
    if args.results_dir:
        # Caller supplies only public/synthetic, verified artifacts, never credential directories.
        shutil.copytree(args.results_dir, out / "results")
    print(out)


if __name__ == "__main__":
    main()
