from __future__ import annotations

import asyncio
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from dcfa.agent.state import AgentState
from dcfa.errors import ErrorCode
from dcfa_website_demo.app import (
    MAX_DEMO_SEED,
    _input_error_outputs,
    _reserve_output_directory,
    execute_portfolio_scenario,
    format_portfolio_result,
)
from dcfa_website_demo.service import build_service


def test_website_demo_import_is_lazy_and_keeps_hillstrom_isolated() -> None:
    code = (
        "import sys; import dcfa_website_demo.app as app; "
        "assert 'gradio' not in sys.modules; "
        "assert 'torch' not in sys.modules; "
        "assert 'tabpfn' not in sys.modules; "
        "assert not any(name.startswith('dcfa.hillstrom_policy') for name in sys.modules); "
        "assert callable(app.build_app); assert callable(app.execute_portfolio_scenario)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_supported_website_scenario_returns_real_state_trace_and_evidence(
    tmp_path: Path,
) -> None:
    result = execute_portfolio_scenario(
        "strong_iv",
        160,
        20260810,
        output_root=tmp_path,
    )
    assert result.response.status == "completed"
    assert result.response.final_state is AgentState.COMPLETED
    assert result.response.result_bundle_id is not None
    assert len(result.response.queries) == 1
    assert result.response.queries[0].evidence_id.startswith("evidence_")
    assert result.plot_path is not None and result.plot_path.is_file()

    status, states, answer, evidence, plot, audit = format_portfolio_result(result)
    assert "development-only" in status
    assert "demo-status--warning" in status
    assert "Validating Evidence" in states
    assert result.response.queries[0].evidence_id in answer
    assert result.response.queries[0].evidence_id in evidence
    assert "inspect the evidence record" in answer
    assert "RESIDUAL_DEPENDENCE_EMPIRICAL_WARNING" in evidence
    assert plot == str(result.plot_path)
    assert result.response.result_bundle_id in audit


def test_weak_website_scenario_preserves_empirical_warnings(tmp_path: Path) -> None:
    result = execute_portfolio_scenario(
        "weak_iv",
        160,
        20260810,
        output_root=tmp_path,
    )
    warning_codes = {warning.code for warning in result.response.queries[0].warnings}
    assert result.response.status == "completed"
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" in warning_codes
    assert "WEAK_INTERVENTION_SUPPORT" in warning_codes
    status, _, answer, evidence, plot, _ = format_portfolio_result(result)
    assert "demo-status--warning" in status
    assert "inspect the evidence record" in answer
    assert "WEAK_FIRST_STAGE_EMPIRICAL_WARNING" in evidence
    assert plot is not None


def test_outside_support_executes_real_gate_and_renders_without_number(tmp_path: Path) -> None:
    result = execute_portfolio_scenario(
        "support_violation",
        160,
        20260810,
        output_root=tmp_path,
    )
    assert result.response.status == "blocked"
    assert result.response.final_state is AgentState.BLOCKED
    assert result.response.queries == ()
    assert result.response.error is not None
    assert result.response.error["code"] == ErrorCode.OUTSIDE_SUPPORT.value
    assert result.plot_path is None
    assert result.output_dir is None
    assert not list(tmp_path.rglob("run-*"))

    status, states, answer, evidence, plot, _ = format_portfolio_result(result)
    assert ErrorCode.OUTSIDE_SUPPORT.value in status
    assert "Blocked" in states
    assert "No numerical answer" in answer
    assert "No evidence record was emitted" in evidence
    assert plot is None


def test_run_directories_are_reserved_atomically(tmp_path: Path) -> None:
    def reserve(_: int) -> Path:
        return _reserve_output_directory(tmp_path, "strong_iv", 17)

    with ThreadPoolExecutor(max_workers=8) as executor:
        paths = tuple(executor.map(reserve, range(16)))

    assert len(paths) == len(set(paths)) == 16
    assert all(path.is_dir() for path in paths)
    assert {path.name for path in paths} == {f"run-{index:04d}" for index in range(1, 17)}


def test_bounded_controls_reject_invalid_values_before_allocating_output(tmp_path: Path) -> None:
    for rows, seed in ((119, 1), (601, 1), (160, -1), (160, MAX_DEMO_SEED + 1)):
        try:
            execute_portfolio_scenario("strong_iv", rows, seed, output_root=tmp_path)
        except ValueError as exc:
            status, states, answer, evidence, plot, audit = _input_error_outputs(str(exc))
        else:  # pragma: no cover - makes an unexpected fit an explicit test failure
            raise AssertionError("Invalid controls unexpectedly executed the workflow.")
        assert "Input rejected safely" in status
        assert "No state trace" in states
        assert "No numerical answer" in answer
        assert "No evidence record" in evidence
        assert plot is None
        assert '"status": "input_rejected"' in audit
    assert not list(tmp_path.rglob("run-*"))


def test_health_endpoint_identifies_development_service_and_security_headers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))

    async def get(path: str) -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)

    response = asyncio.run(get("/healthz"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["evidence_status"] == "development_only"
    assert response.json()["backend"] == "sklearn_quantile_fallback"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"

    ready = asyncio.run(get("/readyz"))
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["output_root_writable"] is True


def test_readiness_fails_when_output_root_has_no_directory_parent(monkeypatch) -> None:
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", "/dev/null/dcfa-output")

    async def get_readiness() -> httpx.Response:
        transport = httpx.ASGITransport(app=build_service())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/readyz")

    response = asyncio.run(get_readiness())
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["output_root_writable"] is False
