"""Space dialogue and confirmation behavior with no external provider requests."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import gradio as gr
import pytest

from dcfa.errors import DCFAError
from dcfa_website_demo.app import build_app, execute_prepared_local_csv
from dcfa_website_demo.csv_upload import export_standard_demo_csv
from dcfa_website_demo.dialogue import CSVConversation, compile_csv_turn, prepare_turn
from tests.provider_fakes import FakeGeminiClient


@pytest.fixture
def fixture(tmp_path):
    path = export_standard_demo_csv(tmp_path / "sample.csv")
    key = tmp_path / "key"
    key.write_text("test_key_not_a_real_credential")
    key.chmod(0o600)
    client = FakeGeminiClient()
    proposal = json.loads(client.interactions.output_text)
    ready = {
        "decision": "ready",
        "message": "Review your plan.",
        "proposal": proposal,
        "definitions": {"outcome": "", "treatment": "", "instrument": ""},
    }
    session = CSVConversation()

    def transport(history, columns, overrides):
        return compile_csv_turn(
            history,
            columns,
            overrides,
            api_key_file=key,
            client=client,
            on_request=session.count_request,
        )

    return SimpleNamespace(
        path=str(path), key=key, client=client, ready=ready, session=session, transport=transport
    )


def turn(f, text="Y is outcome; X is treatment; Z is instrument. Median high minus low."):
    prepare_turn(f.session, f.path, text, {}, True, f.transport)


def test_multiturn_then_correction_and_no_statistics(fixture, monkeypatch):
    f = fixture
    monkeypatch.setattr(
        "dcfa_website_demo.app.make_local_tabpfn_v2_backend",
        lambda *a, **k: pytest.fail("No fit before confirmation"),
    )
    f.client.interactions.output_text = json.dumps(
        {
            **f.ready,
            "decision": "clarify",
            "message": "Which column is the outcome?",
            "proposal": None,
        }
    )
    turn(f, "Help me analyze this.")
    assert f.session.status == "collecting"
    assert f.session.compilation is None
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f)
    assert f.session.status == "ready"
    assert f.session.compilation.trace["model_request_count"] == 2
    assert f.session.compilation.trace["confirmed_roles"]["treatment"]["column_position"] == 2
    assert "Not provided" in f.session.plan_html
    payload = json.loads(f.client.interactions.calls[-1]["input"])
    assert len(payload["conversation"]) == 3
    assert set(payload) == {"conversation", "available_columns", "optional_role_overrides"}
    f.ready["proposal"].update(x_label="low", comparison_x_label="high")
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f, "Actually, use low minus high.")
    assert "low minus high" in f.session.plan_html
    assert f.session.compilation.trace["model_request_count"] == 3


def test_invalid_response_retains_history_revokes_ready_and_counts_request(fixture):
    f = fixture
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f)
    history = list(f.session.history)
    f.client.interactions.output_text = "not JSON"
    with pytest.raises(DCFAError):
        turn(f, "Change the objective")
    assert f.session.history == history
    assert f.session.compilation is None
    assert f.session.status == "collecting"
    assert not f.session.busy
    assert f.session.request_count == 2


def test_provider_failure_counts_once_and_does_not_retry(fixture):
    f = fixture

    def fail(**kwargs):
        f.client.interactions.calls.append(kwargs)
        raise RuntimeError("provider failure")

    f.client.interactions.create = fail
    with pytest.raises(DCFAError, match="request failed"):
        turn(f)
    assert f.session.request_count == 1
    assert len(f.client.interactions.calls) == 1
    assert f.session.history == [] and not f.session.busy


def test_quoted_definition_and_escaped_card(fixture):
    f = fixture
    f.ready["definitions"]["outcome"] = "crop <yield>"
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f, "Y means crop <yield>; X treatment; Z instrument; median high minus low.")
    assert "crop &lt;yield&gt;" in f.session.plan_html
    assert "<yield>" not in f.session.plan_html


def test_block_is_a_nonexecuting_conversation_reply(fixture):
    f = fixture
    f.client.interactions.output_text = json.dumps(
        {
            **f.ready,
            "decision": "block",
            "proposal": None,
            "message": "Binary treatments are outside this workflow.",
        }
    )
    turn(f, "Analyze a binary treatment.")
    assert f.session.compilation is None and f.session.status == "collecting"
    assert "Binary" in f.session.history[-1]["content"]


@pytest.mark.parametrize("change", ["invented", "duplicate", "definition", "override"])
def test_invalid_role_or_definition_is_not_confirmable(fixture, change):
    f = fixture
    overrides = {}
    if change == "invented":
        f.ready["proposal"]["outcome"] = "missing"
    elif change == "duplicate":
        f.ready["proposal"]["outcome"] = "X"
    elif change == "definition":
        f.ready["definitions"]["outcome"] = "invented business meaning"
    else:
        overrides = {"outcome": "X"}
    f.client.interactions.output_text = json.dumps(f.ready)
    with pytest.raises(DCFAError):
        prepare_turn(f.session, f.path, "Please analyze the data", overrides, True, f.transport)
    assert f.session.compilation is None


def test_authorization_expiry_and_isolation(fixture):
    f = fixture
    with pytest.raises(ValueError, match="authorization"):
        prepare_turn(f.session, f.path, "Help", {}, False, f.transport)
    assert not f.client.interactions.calls
    f.session.touched = time.monotonic() - 901
    with pytest.raises(ValueError, match="expired"):
        turn(f)
    other = CSVConversation()
    assert other.history == [] and not other.expired()


def handlers(chat_handler, execute_handler, authorize=None):
    def no_auth(profile: gr.OAuthProfile | None):
        pass

    authorize = authorize or no_auth
    app = build_app(
        deployment_mode="zerogpu_canonical",
        build_revision="12345678",
        space_authorize_handler=authorize,
        space_csv_authorize_handler=lambda *a: None,
        space_csv_handler=execute_handler or (lambda *a: ()),
        space_csv_chat_handler=chat_handler,
        space_scenario_handler=lambda *a: (),
    )
    return {block.fn.__name__: block.fn for block in app.fns.values() if block.fn is not None}


def test_button_only_executes_once_and_clears_key(fixture):
    f = fixture
    f.client.interactions.output_text = json.dumps(f.ready)
    executions = []
    h = handlers(
        lambda history, columns, overrides, key, count: f.transport(history, columns, overrides),
        lambda *args: executions.append(args) or tuple(gr.update(value="report") for _ in range(9)),
    )
    profile = SimpleNamespace(username="alice")
    result = h["talk"](
        f.session,
        f.path,
        "password-not-logged",
        "",
        "",
        "",
        True,
        "Y outcome, X treatment, Z instrument; median high minus low",
        profile,
    )
    assert result[4]["interactive"]
    assert "value" not in result[5]  # Preserve the browser password without returning it.
    old_revision = f.session.revision
    h["talk"](f.session, f.path, "password-not-logged", "", "", "", True, "确认", profile)
    assert not executions
    stale = list(h["generate"](f.session, f.path, "", "", "", True, 123, old_revision, profile))
    assert "plan changed" in stale[0][3]
    assert not executions
    generator = h["generate"](f.session, f.path, "", "", "", True, 123, f.session.revision, profile)
    running = next(generator)
    assert running[5]["value"] == ""
    assert not running[4]["interactive"]
    assert f.session.status == "running"
    list(h["generate"](f.session, f.path, "", "", "", True, 123, f.session.revision, profile))
    assert not executions
    completed = next(generator)
    assert len(executions) == 1
    assert f.session.status == "completed"
    assert f.session.validated is None
    assert completed[5]["value"] == ""
    list(h["generate"](f.session, f.path, "", "", "", True, 123, f.session.revision, profile))
    assert len(executions) == 1
    assert len(f.client.interactions.calls) == 2


def test_ui_invalidation_reset_expiry_login(fixture):
    f = fixture
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f)
    h = handlers(None, None)
    h["invalidate"](f.session, f.path, "X", "Y", "Z", True)
    assert f.session.compilation is None
    turn(f)
    changed = h["file_changed"](f.session, "another.csv", "", "", "", True)
    assert changed[0].history == [] and changed[0].compilation is None
    assert changed[5]["value"] == ""
    f.session.touched = time.monotonic() - 901
    expired = h["expire"](f.session)
    assert "expired" in expired[3]
    assert expired[5]["value"] == ""
    assert expired[0].validated is None
    missing_state = h["expire"](None)
    assert missing_state[5]["value"] == ""
    assert "expired" in missing_state[3]
    from dcfa_website_demo.zerogpu import _require_login

    h = handlers(None, None, _require_login)
    denied = h["talk"](CSVConversation(), f.path, "", "", "", "", True, "Hello", None)
    assert "Sign in" in denied[3]


def test_prepared_analysis_has_no_gemini_call_and_verifies_artifact(fixture, tmp_path, monkeypatch):
    from dcfa.artifact_validation import verify_run_directory
    from tests.integration.test_zerogpu_space import FakeLocalTabPFNBackend

    f = fixture
    f.client.interactions.output_text = json.dumps(f.ready)
    turn(f)
    monkeypatch.setattr(
        "dcfa_website_demo.app.make_local_tabpfn_v2_backend",
        lambda specification, **k: FakeLocalTabPFNBackend(seed=specification.seed),
    )
    result = execute_prepared_local_csv(
        f.session.validated,
        f.session.compilation,
        123,
        model_path=Path("unused"),
        output_root=tmp_path / "run",
    )
    assert len(f.client.interactions.calls) == 1
    assert result.response.status == "completed"
    assert verify_run_directory(result.output_dir)["status"] == "valid"
    trace = json.loads((result.output_dir / "gemini_compilation.json").read_text())
    assert trace["confirmed_roles"]["outcome"]["column_position"] == 1
    assert trace["model_request_count"] == 1
    assert "history" not in trace and "conversation" not in trace
