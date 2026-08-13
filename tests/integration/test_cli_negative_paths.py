from __future__ import annotations

import json

from dcfa.cli import main


def test_support_violation_cli_blocks_without_artifacts(tmp_path, capsys) -> None:
    output_dir = tmp_path / "blocked"
    exit_code = main(
        [
            "tabcf-demo",
            "--scenario",
            "support_violation",
            "--rows",
            "120",
            "--seed",
            "71",
            "--output-dir",
            str(output_dir),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert payload["error"]["code"] == "OUTSIDE_SUPPORT"
    assert not output_dir.exists()
