import gradio as gr
from fastapi.testclient import TestClient

from dcfa_website_demo.app import build_app
from dcfa_website_demo.dialogue import CSVConversation
from dcfa_website_demo.service import build_service
from tests.integration.test_cigarette_distribution import CSV, PROMPT, compilation


def test_local_dialogue_uses_fixed_policy_without_oauth(tmp_path, monkeypatch):
    monkeypatch.setenv("GRADIO_TEMP_DIR", str(tmp_path))
    calls = []
    c = compilation()

    def chat(*args):
        return "Review plan", c

    def execute(validated, plan, seed, profile, *, analysis_mode):
        assert profile is None
        assert analysis_mode == "api_only"
        calls.append(seed)
        return tuple(gr.update(value="Cached result") for _ in range(9))

    monkeypatch.setattr(
        "dcfa_website_demo.local_dialogue.local_handlers",
        lambda **kw: (lambda profile: None, chat, execute),
    )
    app = build_app(
        local_csv_dialogue=True,
        fixed_analysis_mode="api_only",
        presentation_title="Entry title",
        output_root=tmp_path,
    )
    functions = {fn.fn.__name__: fn.fn for fn in app.fns.values() if fn.fn}
    session = CSVConversation()
    path = tmp_path / "input.csv"
    path.write_bytes(CSV.read_bytes())
    functions["local_talk"](session, str(path), "", "", "", "", True, PROMPT, "api_only")
    assert session.analysis_mode == "api_only"
    assert session.status == "ready"
    functions["local_talk"](session, str(path), "", "", "", "", True, "Confirm", "api_only")
    assert calls == []
    args = (session, str(path), "", "", "", True, 20260920, session.revision, "api_only")
    list(functions["local_generate"](*args))
    list(functions["local_generate"](*args))
    functions["local_talk"](session, None, "", "", "", "", True, "Explain", "api_only")
    assert calls == [20260920]
    assert session.cached_answer
    assert not path.exists()
    assert app.title == "Entry title"


def test_entry_health_and_default_service_remain_distinct(tmp_path, monkeypatch):
    monkeypatch.setenv("DCFA_OUTPUT_ROOT", str(tmp_path))
    with TestClient(
        build_service(fixed_analysis_mode="api_only", local_csv_dialogue=True)
    ) as client:
        health = client.get("/healthz").json()
        assert health["supported_modes"] == ["api_only"]
        assert health["default_mode"] == "api_only"
    with TestClient(build_service()) as client:
        assert client.get("/healthz").json()["default_mode"] == "api_preferred"
