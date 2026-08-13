from __future__ import annotations

import subprocess
import sys


def test_public_app_import_is_lazy_and_has_no_hillstrom_router() -> None:
    code = (
        "import sys; import dcfa.app as app; "
        "assert 'gradio' not in sys.modules; "
        "assert not any(name.startswith('dcfa.hillstrom_policy') for name in sys.modules); "
        "assert callable(app.run_development_analysis)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
