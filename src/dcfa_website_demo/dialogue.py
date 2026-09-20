"""Space-only, row-free dialogue compilation and ephemeral CSV session state."""

from __future__ import annotations

import html
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dcfa.agent.gemini_live import load_gemini_client, read_gemini_api_key
from dcfa.errors import DCFAError, ErrorCode
from dcfa_website_demo.csv_upload import (
    CSVDataBoundary,
    ValidatedCSVColumns,
    assign_csv_roles,
    read_authorized_csv_columns,
)
from dcfa_website_demo.gemini import (
    GOOGLE_GENAI_VERSION,
    GeminiWebsiteCompilation,
    _load_config,
    _role_context,
    _usage_payload,
    _validate_proposal,
)

DIALOGUE_VERSION = "space_csv_dialogue_v1"
DIALOGUE_CONFIG = Path(__file__).resolve().parents[2] / (
    "evaluation/configs/space_csv_dialogue_v1.json"
)
SESSION_SECONDS = 900
_SESSION_LOCK = threading.RLock()
ROLES = ("outcome", "treatment", "instrument")


@dataclass
class CSVConversation:
    """Server-side session data; never contains a credential or provider client."""

    history: list[dict[str, str]] = field(default_factory=list)
    validated: ValidatedCSVColumns | None = None
    compilation: GeminiWebsiteCompilation | None = None
    plan_html: str = ""
    status: str = "collecting"
    busy: bool = False
    touched: float = field(default_factory=time.monotonic)
    request_count: int = 0
    revision: int = 0
    upload_path: str | None = None
    overrides: dict[str, str | None] = field(default_factory=dict)
    owner: str | None = None

    def expired(self) -> bool:
        return not self.busy and time.monotonic() - self.touched >= SESSION_SECONDS

    def claim(self, *, ready: bool = False) -> None:
        with _SESSION_LOCK:
            if self.busy:
                raise ValueError("A request is already running in this conversation.")
            if self.expired():
                raise ValueError("This conversation expired. Reset and upload the CSV again.")
            if ready and (self.status != "ready" or self.compilation is None):
                raise ValueError("Prepare a complete plan before confirming it.")
            self.busy = True
            self.touched = time.monotonic()
            self.status = "running" if ready else "collecting"
            if not ready:
                self.revision += 1
                self.compilation = None
                self.plan_html = ""

    def release(self) -> None:
        self.busy = False
        self.touched = time.monotonic()

    def count_request(self) -> None:
        self.request_count += 1


def compile_csv_turn(
    history: list[dict[str, str]],
    columns: tuple[str, str, str],
    overrides: dict[str, str | None],
    *,
    api_key_file: Path,
    on_request: Any,
    client: Any | None = None,
) -> tuple[str, GeminiWebsiteCompilation | None]:
    """Make one structured request, counting even failed provider calls; never retry."""
    config, _ = _load_config(DIALOGUE_CONFIG, expected_version=DIALOGUE_VERSION)
    columns, normalized, _ = _role_context(columns, overrides)
    schema = config["response_schema"]
    proposal_schema = schema["properties"]["proposal"]["anyOf"][0]
    for role in ROLES:
        proposal_schema["properties"][role]["enum"] = (
            [normalized[role]] if role in normalized else list(columns)
        )
    key = read_gemini_api_key(api_key_file)
    if client is None:
        client, version = load_gemini_client(key)
        if version != GOOGLE_GENAI_VERSION:
            raise ValueError("The Gemini SDK does not match the supported Space profile.")
    try:
        on_request()
        interaction = client.interactions.create(
            api_version=config["api_version"],
            model=config["model"],
            store=False,
            system_instruction=config["system_instruction"],
            response_format={"type": "text", "mime_type": "application/json", "schema": schema},
            generation_config=config["generation_config"],
            input=json.dumps(
                {
                    "conversation": history,
                    "available_columns": columns,
                    "optional_role_overrides": normalized,
                }
            ),
            timeout=float(config["timeout_seconds"]),
        )
    except Exception as exc:
        raise DCFAError(
            ErrorCode.LLM_API_FAILED,
            "The dialogue request failed. Your previous messages are retained; you may retry.",
            stage="website_demo.dialogue",
        ) from exc
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass
    try:
        if interaction.status != "completed":
            raise ValueError("Incomplete response")
        raw = interaction.output_text
        if not isinstance(raw, str) or key in raw:
            raise ValueError("Invalid response")
        output = json.loads(raw)
        if set(output) != {"decision", "message", "proposal", "definitions"}:
            raise ValueError("Invalid shape")
        message = output["message"]
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 800:
            raise ValueError("Invalid message")
        definitions = output["definitions"]
        if not isinstance(definitions, dict) or set(definitions) != set(ROLES):
            raise ValueError("Invalid definitions")
        user_messages = [entry["content"] for entry in history if entry["role"] == "user"]
        for definition in definitions.values():
            if not isinstance(definition, str) or len(definition) > 300:
                raise ValueError("Invalid definition")
            if definition and not any(definition in text for text in user_messages):
                raise ValueError("Definitions must quote user-provided text")
        if output["decision"] in {"clarify", "block"}:
            if output["proposal"] is not None:
                raise ValueError("Unexpected executable proposal")
            return message, None
        if output["decision"] != "ready":
            raise ValueError("Invalid decision")
        proposal = output["proposal"]
        # Reuse the complete single-turn validator only at the ready boundary.
        from dcfa_website_demo.gemini import _parse_proposal

        proposal = _parse_proposal(json.dumps(proposal))
        values = _validate_proposal(
            proposal,
            columns=columns,
            role_overrides=normalized,
            csv_mode=True,
        )
        trace = {
            "protocol_version": DIALOGUE_VERSION,
            "provider": config["provider"],
            "model": config["model"],
            "sdk_version": GOOGLE_GENAI_VERSION,
            "store": False,
            "last_turn_usage": _usage_payload(interaction),
            "data_rows_sent_to_gemini": 0,
            "actual_intervention_values_sent_to_gemini": 0,
            "data_sent_to_gemini": ["conversation", "csv_column_names", "optional_role_overrides"],
            "proposal": proposal,
            "confirmed_roles": {
                role: {
                    "column": proposal[role],
                    "column_position": columns.index(proposal[role]) + 1,
                    "definition": definitions[role] or "Not provided",
                }
                for role in ROLES
            },
        }
        return message, GeminiWebsiteCompilation(*values, trace=trace)
    except (ValueError, TypeError, KeyError, AttributeError, DCFAError) as exc:
        raise DCFAError(
            ErrorCode.LLM_OUTPUT_INVALID,
            "The dialogue response was invalid. Your previous messages are retained; try again.",
            stage="website_demo.dialogue",
        ) from exc


def plan_html(compilation: GeminiWebsiteCompilation) -> str:
    """Render an escaped definition index from the same proposal used for execution."""
    rows = []
    for role, symbol in (("treatment", "X"), ("outcome", "Y"), ("instrument", "Z")):
        item = compilation.trace["confirmed_roles"][role]
        cells = (f"{symbol} ({role})", item["column"], item["column_position"], item["definition"])
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in cells) + "</tr>")
    objective = compilation.objective.replace("quantile", "median").replace("_", " ")
    direction = compilation.x_label
    if compilation.comparison_x_label:
        direction += f" minus {compilation.comparison_x_label}"
    return (
        '<div class="demo-confirmation-plan"><h3>Review the analysis plan</h3>'
        "<table><thead><tr><th>Role</th><th>CSV column</th>"
        "<th>Column position (1-based)</th><th>User-provided meaning</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
        + f"<p>Objective: {html.escape(objective)}. Treatment: {html.escape(direction)}.</p>"
        + "<p>Low / center / high refer to the observed treatment's 10th / 50th / 90th "
        "percentiles. Empirical support is checked during analysis.</p></div>"
    )


def prepare_turn(
    session: CSVConversation,
    path: str | None,
    message: str,
    overrides: dict[str, str | None],
    authorized: bool,
    transport: Any,
) -> None:
    """Prepare a proposal without constructing a statistical backend or output directory."""
    if not authorized:
        raise ValueError("Confirm data authorization before sending a message.")
    if not path:
        raise ValueError("Upload a CSV before starting the conversation.")
    if not isinstance(message, str) or not 1 <= len(message.strip()) <= 1000 or "\x00" in message:
        raise ValueError("Each message must contain 1–1000 plain-text characters.")
    if session.status == "completed":
        raise ValueError("This report is complete. Reset to start another analysis.")
    session.claim()
    try:
        if session.upload_path != path:
            session.history.clear()
            session.validated = None
            session.request_count = 0
        if session.validated is None:
            session.validated = read_authorized_csv_columns(
                path,
                confirmed=authorized,
                data_boundary=CSVDataBoundary.HF_ZEROGPU_LOCAL,
            )
        session.upload_path = path
        session.overrides = overrides.copy()
        _role_context(session.validated.header, overrides)
        history = [*session.history, {"role": "user", "content": message.strip()}]
        reply, compilation = transport(history, session.validated.header, overrides)
        if compilation is not None:
            assign_csv_roles(
                session.validated,
                outcome=compilation.outcome,
                treatment=compilation.treatment,
                instrument=compilation.instrument,
            )
            compilation.trace["model_request_count"] = session.request_count
            session.plan_html = plan_html(compilation)
            session.compilation = compilation
            session.status = "ready"
        session.history = [*history, {"role": "assistant", "content": reply}]
    finally:
        session.release()
