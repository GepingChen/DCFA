"""Remote protocol and authentication tests; no real GPU inference."""

import json
import zipfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.pipeline import predict_backend
from dcfa_website_demo.daily import write_record
from dcfa_website_demo.v2_remote import (
    accept_result,
    decode_payload,
    execute_remote,
    make_payload,
    safe_extract,
    serve_v2,
)
from tests.integration import test_daily_analysis as daily_tests
from tests.integration.test_daily_analysis import FakeV2, executor


@pytest.fixture
def confirmed(tmp_path):
    return daily_tests.confirmed.__wrapped__(tmp_path)


def test_wire_roundtrip_excludes_trace_and_paths(confirmed):
    confirmed["compilation"].trace["private_credential"] = "SECRET"
    payload = make_payload(confirmed)
    assert "SECRET" not in json.dumps(payload)
    assert "output_root" not in payload
    decoded = decode_payload(payload)
    assert decoded["manifest"] == confirmed["manifest"]
    assert decoded["interventions"] == confirmed["interventions"]


@pytest.mark.parametrize("mutation", ["extra", "columns", "hash", "trace", "seed"])
def test_bad_requests_rejected(confirmed, mutation):
    payload = make_payload(confirmed)
    if mutation == "extra":
        payload["backend"] = "api"
    if mutation == "columns":
        payload["columns"]["W"] = [1] * 128
    if mutation == "hash":
        payload["manifest"]["dataset_hash"] = "bad"
    if mutation == "trace":
        payload["compilation"]["trace"] = {"secret": "no"}
    if mutation == "seed":
        payload["seed"] = -1
    with pytest.raises((ValueError, TypeError)):
        decode_payload(payload)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "folder/file"])
def test_zip_path_safety(tmp_path, name):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(name, "data")
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(ValueError):
        safe_extract(archive, out)
    assert not list(out.iterdir())


def test_server_auth_before_decode(tmp_path):
    with pytest.raises(DCFAError) as caught:
        serve_v2(
            {},
            "",
            model_path=tmp_path / "model",
            output_root=tmp_path,
            prediction_runner=Mock(),
            authenticate=Mock(),
        )
    assert caught.value.code == ErrorCode.DATA_ACCESS_BLOCKED


def test_remote_result_verified_and_request_bound(confirmed, tmp_path):
    directory = tmp_path / "v2"
    directory.mkdir()
    result = executor("v2", [])(confirmed, directory, {})
    write_record(directory / "remote_response.json", result.response)
    accepted = accept_result(directory, confirmed)
    assert accepted.response.queries == result.response.queries
    changed = dict(confirmed, seed=19)
    with pytest.raises(ValueError, match="specification"):
        accept_result(directory, changed)
    response = json.loads((directory / "remote_response.json").read_text())
    response["queries"][0]["value_raw"] += 1
    write_record(directory / "remote_response.json", response)
    with pytest.raises(ValueError, match="bundle"):
        accept_result(directory, confirmed)


def test_missing_endpoint_sends_no_data(confirmed, tmp_path, monkeypatch):
    import gradio_client

    client = Mock()
    client.view_api.return_value = {"named_endpoints": {}}
    monkeypatch.setattr(gradio_client, "Client", Mock(return_value=client))
    monkeypatch.setattr("dcfa_website_demo.v2_remote.remote_token", lambda: "SECRET")
    with pytest.raises(DCFAError) as caught:
        execute_remote(confirmed, tmp_path)
    assert caught.value.code == ErrorCode.V2_UNAVAILABLE
    client.submit.assert_not_called()


def test_timeout_never_resubmits(confirmed, tmp_path, monkeypatch):
    import gradio_client

    client = Mock()
    client.view_api.return_value = {"named_endpoints": {"/analyze_v2": {}}}
    client.submit.return_value.result.side_effect = TimeoutError("SECRET")
    client.submit.return_value.communicator.event_id = "job-123"
    monkeypatch.setattr(gradio_client, "Client", Mock(return_value=client))
    monkeypatch.setattr("dcfa_website_demo.v2_remote.remote_token", lambda: "SECRET")
    with pytest.raises(DCFAError) as caught:
        execute_remote(confirmed, tmp_path)
    client.submit.assert_called_once()
    assert "SECRET" not in json.dumps(caught.value.to_dict())
    assert json.loads((tmp_path / "remote_job.json").read_text())["job_id"] == "job-123"


def test_server_complete_archive_and_cleanup(confirmed, tmp_path, monkeypatch):
    monkeypatch.setenv("GRADIO_TEMP_DIR", str(tmp_path / "downloads"))
    monkeypatch.setattr(
        "dcfa_website_demo.v2_remote.make_local_tabpfn_v2_backend",
        lambda spec, model_path: FakeV2(seed=spec.seed),
    )
    metadata, archive = serve_v2(
        make_payload(confirmed),
        "SECRET",
        model_path=tmp_path / "model",
        output_root=tmp_path / "server",
        prediction_runner=predict_backend,
        authenticate=lambda **k: {"name": "tester"},
    )
    assert metadata["status"] == "completed"
    out = tmp_path / "downloaded"
    out.mkdir()
    safe_extract(Path(archive), out)
    assert accept_result(out, confirmed).response.status == "completed"
    assert not list((tmp_path / "server").rglob("report.md"))
    assert all(b"SECRET" not in p.read_bytes() for p in out.iterdir())


def test_client_downloads_and_verifies_complete_artifact(confirmed, tmp_path, monkeypatch):
    from contextlib import contextmanager

    import gradio_client
    import httpx

    server = tmp_path / "server"
    server.mkdir()
    result = executor("v2", [])(confirmed, server, {})
    write_record(server / "remote_response.json", result.response)
    archive = tmp_path / "remote.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        for path in server.iterdir():
            stream.write(path, path.name)
    client = Mock()
    client.src = "https://example.hf.space/"
    client.view_api.return_value = {"named_endpoints": {"/analyze_v2": {}}}
    client.submit.return_value.communicator.event_id = "job-42"
    client.submit.return_value.result.return_value = (
        {"status": "completed"},
        {"url": "https://example.hf.space/gradio_api/file=result.zip"},
    )
    monkeypatch.setattr(gradio_client, "Client", Mock(return_value=client))
    monkeypatch.setattr("dcfa_website_demo.v2_remote.remote_token", lambda: "SECRET")

    @contextmanager
    def download(method, url, **kwargs):
        assert kwargs["headers"] == {"Authorization": "Bearer SECRET"}
        assert not kwargs["follow_redirects"]
        yield httpx.Response(200, content=archive.read_bytes(), request=httpx.Request(method, url))

    monkeypatch.setattr(httpx, "stream", download)
    destination = tmp_path / "download"
    destination.mkdir()
    accepted = execute_remote(confirmed, destination)
    assert accepted.response.queries == result.response.queries
    assert accepted.plot_path.is_file()
    client.submit.assert_called_once()
    job_record = json.loads((destination / "remote_job.json").read_text())
    assert job_record["status"] == "completed" and job_record["job_id"] == "job-42"


def test_server_execution_failure_cleans_temporary_work(confirmed, tmp_path, monkeypatch):
    def broken(**kwargs):
        (kwargs["output_root"] / "private-partial.txt").write_text("private")
        raise RuntimeError("failure")

    monkeypatch.setattr("dcfa_website_demo.app._execute_compiled_dataset", broken)
    output = tmp_path / "server"
    with pytest.raises(RuntimeError):
        serve_v2(
            make_payload(confirmed),
            "SECRET",
            model_path=tmp_path / "model",
            output_root=output,
            prediction_runner=predict_backend,
            authenticate=lambda **kwargs: {"name": "tester"},
        )
    assert list(output.iterdir()) == []
