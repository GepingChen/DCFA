from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from dcfa.agent.benchmark import benchmark_summary, load_benchmark_cases, run_recorded_benchmark
from dcfa.artifact_validation import verify_agent_benchmark_file
from dcfa.canonical import file_sha256, to_primitive
from dcfa.errors import DCFAError

CASE_PATH = Path("evaluation/agent_benchmark/cases/track_a_cases_v1.json")


def test_24_case_recorded_benchmark_hard_safety_and_tool_parity() -> None:
    cases = load_benchmark_cases(CASE_PATH)
    traces = run_recorded_benchmark(cases)
    assert len(cases) == 24
    assert len(traces) == 48

    full_agent = [trace for trace in traces if trace.system == "full_agent"]
    fixed = [trace for trace in traces if trace.system == "fixed_workflow"]
    assert all(trace.valid_completion for trace in full_agent)
    assert sum(trace.valid_completion for trace in fixed) < len(fixed)
    assert all(
        not trace.values
        for trace in traces
        if trace.final_state in {"blocked", "clarification_required"}
    )

    for case in cases:
        if case.family != "clean_supported" or case.mode != "analysis":
            continue
        full_trace = next(trace for trace in full_agent if trace.case_id == case.case_id)
        fixed_trace = next(trace for trace in fixed if trace.case_id == case.case_id)
        assert full_trace.values == fixed_trace.values
        assert full_trace.evidence_ids == fixed_trace.evidence_ids

    summary = benchmark_summary(traces)
    assert summary["track"] == "agent_benchmark"
    assert summary["case_count"] == 24
    assert summary["runs_per_case"] == 1
    assert summary["systems"]["full_agent"]["forbidden_numeric_after_block"] == 0
    assert summary["systems"]["fixed_workflow"]["forbidden_numeric_after_block"] == 0
    assert summary["systems"]["full_agent"]["forbidden_numeric_when_gold_requires_no_answer"] == 0
    assert (
        summary["systems"]["fixed_workflow"]["forbidden_numeric_when_gold_requires_no_answer"] == 1
    )
    assert summary["systems"]["full_agent"]["numerical_fidelity_rate"] == 1.0
    assert summary["systems"]["full_agent"]["evidence_resolution_rate"] == 1.0


def test_final_repeated_harness_nests_five_runs_within_each_case() -> None:
    cases = load_benchmark_cases(CASE_PATH)
    traces = run_recorded_benchmark(cases, repetitions=5)
    assert len(traces) == 24 * 5 * 2
    summary = benchmark_summary(traces)
    assert summary["runs_per_case"] == 5
    assert summary["systems"]["full_agent"]["valid_completion_count"] == 24 * 5
    assert {trace.run_index for trace in traces} == set(range(5))
    assert summary["systems"]["full_agent"]["between_run_disagreement_case_count"] == 0
    assert summary["primary_case_level_comparison"]["analysis_unit"] == "case"
    assert summary["primary_case_level_comparison"]["case_bootstrap_resamples"] == 10_000


def test_recorded_benchmark_artifact_is_independently_recomputed(tmp_path) -> None:
    cases = load_benchmark_cases(CASE_PATH)
    traces = run_recorded_benchmark(cases, repetitions=5)
    payload = {
        **benchmark_summary(traces),
        "case_version": "track_a_cases_v1",
        "case_file_hash": file_sha256(CASE_PATH),
        "traces": tuple(to_primitive(trace) for trace in traces),
    }
    path = tmp_path / "benchmark.json"
    path.write_text(json.dumps(to_primitive(payload)), encoding="utf-8")
    verified = verify_agent_benchmark_file(path, CASE_PATH)
    assert verified["status"] == "valid"

    tampered = to_primitive(payload)
    tampered["systems"]["full_agent"]["valid_completion_count"] = 0
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(DCFAError):
        verify_agent_benchmark_file(path, CASE_PATH)


@pytest.mark.parametrize("tamper_kind", ["case_metadata", "grader_outcome"])
def test_recorded_benchmark_verifier_rejects_trace_level_tampering(
    tmp_path, tamper_kind: str
) -> None:
    cases = load_benchmark_cases(CASE_PATH)
    traces = run_recorded_benchmark(cases)
    if tamper_kind == "case_metadata":
        tampered_trace = replace(traces[0], fixture_behavior="forged_fixture")
        trace_index = 0
    else:
        trace_index = next(
            index for index, trace in enumerate(traces) if not trace.valid_completion
        )
        tampered_trace = replace(
            traces[trace_index],
            valid_completion=True,
            grader_failures=(),
        )
    tampered_traces = (
        *traces[:trace_index],
        tampered_trace,
        *traces[trace_index + 1 :],
    )
    payload = {
        **benchmark_summary(tampered_traces),
        "case_version": "track_a_cases_v1",
        "case_file_hash": file_sha256(CASE_PATH),
        "traces": tuple(to_primitive(trace) for trace in tampered_traces),
    }
    path = tmp_path / f"{tamper_kind}.json"
    path.write_text(json.dumps(to_primitive(payload)), encoding="utf-8")

    with pytest.raises(DCFAError) as raised:
        verify_agent_benchmark_file(path, CASE_PATH)
    assert raised.value.stage == "agent_benchmark.validation"
