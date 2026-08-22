#!/usr/bin/env python3
"""Generate an editable SVG and a 4K PNG for the TabCF-Agent overview figure."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import cairosvg
import svgwrite

WIDTH = 3840
HEIGHT = 2160
FONT = "Arial"

OUT_DIR = Path(__file__).resolve().parent
SVG_PATH = OUT_DIR / "tabcf_agent_overview_editable.svg"
PNG_PATH = OUT_DIR / "tabcf_agent_overview_4k.png"

COLORS = {
    "bg": "#FCFCFB",
    "text": "#202734",
    "muted": "#5F6B7A",
    "grid": "#CBD5E1",
    "grid_light": "#E7ECF2",
    "blue": "#2A5BD7",
    "blue_dark": "#183E9D",
    "blue_fill": "#F4F7FF",
    "blue_lane": "#F6F8FD",
    "teal": "#12836E",
    "teal_dark": "#086451",
    "teal_fill": "#F2FBF7",
    "teal_lane": "#F5FBF8",
    "amber": "#D97706",
    "amber_fill": "#FFF7E8",
    "red": "#D83B35",
    "red_fill": "#FFF3F2",
    "violet": "#6B35B2",
    "violet_dark": "#4D2389",
    "violet_fill": "#F8F4FF",
    "violet_lane": "#FAF8FD",
    "white": "#FFFFFF",
}


def normalize_font_weight(weight: int | str) -> str:
    """Return an SVG-compatible font-weight value."""
    if isinstance(weight, int):
        rounded = max(100, min(900, int(round(weight / 100.0) * 100)))
        return str(rounded)
    return str(weight)


def normalize_weight(weight: int | str) -> str:
    """Map arbitrary numeric weights to SVG validator-compatible 100-step values."""
    if isinstance(weight, str):
        return weight
    allowed = [100, 200, 300, 400, 500, 600, 700, 800, 900]
    return str(min(allowed, key=lambda value: abs(value - weight)))


def add_text(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    text: str,
    *,
    size: float = 28,
    weight: int | str = 400,
    color: str | None = None,
    anchor: str = "start",
    italic: bool = False,
    letter_spacing: float | None = None,
    font_family: str | None = None,
) -> svgwrite.text.Text:
    attrs = {
        "font_family": font_family or FONT,
        "font_size": size,
        "font_weight": normalize_weight(weight),
        "fill": color or COLORS["text"],
        "text_anchor": anchor,
    }
    if italic:
        attrs["font_style"] = "italic"
    if letter_spacing is not None:
        attrs["letter_spacing"] = letter_spacing
    node = dwg.text(text, insert=(x, y), **attrs)
    dwg.add(node)
    return node


def add_multiline(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    lines: Sequence[str],
    *,
    size: float = 26,
    weight: int | str = 400,
    color: str | None = None,
    anchor: str = "start",
    line_height: float | None = None,
    italic: bool = False,
    font_family: str | None = None,
) -> svgwrite.text.Text:
    line_height = line_height or size * 1.28
    node = dwg.text(
        "",
        insert=(x, y),
        font_family=font_family or FONT,
        font_size=size,
        font_weight=normalize_font_weight(weight),
        fill=color or COLORS["text"],
        text_anchor=anchor,
        font_style="italic" if italic else "normal",
    )
    for idx, line in enumerate(lines):
        node.add(dwg.tspan(line, x=[x], dy=[0 if idx == 0 else line_height]))
    dwg.add(node)
    return node


def shadow_rect(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    radius: float = 20,
) -> None:
    dwg.add(
        dwg.rect(
            insert=(x + 5, y + 7),
            size=(w, h),
            rx=radius,
            ry=radius,
            fill="#0F172A",
            opacity=0.055,
        )
    )


def rounded_box(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    stroke: str,
    fill: str = "#FFFFFF",
    stroke_width: float = 3,
    radius: float = 22,
    shadow: bool = True,
    dash: str | None = None,
) -> svgwrite.shapes.Rect:
    if shadow:
        shadow_rect(dwg, x, y, w, h, radius=radius)
    attrs = {
        "insert": (x, y),
        "size": (w, h),
        "rx": radius,
        "ry": radius,
        "fill": fill,
        "stroke": stroke,
        "stroke_width": stroke_width,
    }
    if dash:
        attrs["stroke_dasharray"] = dash
    node = dwg.rect(**attrs)
    dwg.add(node)
    return node


def divider(dwg: svgwrite.Drawing, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
    dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=2, opacity=0.55))


def title_box(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    title: str,
    body: Sequence[str] = (),
    stroke: str,
    fill: str,
    title_color: str | None = None,
    title_size: float = 29,
    body_size: float = 23,
    title_y_offset: float = 42,
    body_y_offset: float = 84,
    line_height: float | None = None,
    shadow: bool = True,
) -> None:
    rounded_box(dwg, x, y, w, h, stroke=stroke, fill=fill, shadow=shadow)
    add_text(
        dwg,
        x + w / 2,
        y + title_y_offset,
        title,
        size=title_size,
        weight=700,
        color=title_color or stroke,
        anchor="middle",
    )
    if body:
        add_multiline(
            dwg,
            x + w / 2,
            y + body_y_offset,
            body,
            size=body_size,
            color=COLORS["text"],
            anchor="middle",
            line_height=line_height,
        )


def chip(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    stroke: str,
    fill: str = "#FFFFFF",
    size: float = 21,
    weight: int | str = 500,
) -> None:
    rounded_box(dwg, x, y, w, h, stroke=stroke, fill=fill, stroke_width=2.2, radius=14, shadow=False)
    add_text(dwg, x + w / 2, y + h / 2 + size * 0.34, text, size=size, weight=weight, anchor="middle")


def capsule(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    stroke: str,
    fill: str,
    size: float = 28,
    weight: int | str = 650,
) -> None:
    rounded_box(dwg, x, y, w, h, stroke=stroke, fill=fill, radius=h / 2, shadow=False)
    add_text(dwg, x + w / 2, y + h / 2 + size * 0.34, text, size=size, weight=weight, color=stroke, anchor="middle")


def arrow_path(
    dwg: svgwrite.Drawing,
    points: Sequence[tuple[float, float]],
    *,
    color: str,
    marker_id: str,
    width: float = 5,
    dash: str | None = None,
    opacity: float = 1.0,
) -> None:
    path_cmds = [f"M {points[0][0]} {points[0][1]}"]
    for px, py in points[1:]:
        path_cmds.append(f"L {px} {py}")
    attrs = {
        "d": " ".join(path_cmds),
        "fill": "none",
        "stroke": color,
        "stroke_width": width,
        "stroke_linecap": "round",
        "stroke_linejoin": "round",
        "marker_end": f"url(#{marker_id})",
        "opacity": opacity,
    }
    if dash:
        attrs["stroke_dasharray"] = dash
    dwg.add(dwg.path(**attrs))


def plain_path(
    dwg: svgwrite.Drawing,
    points: Sequence[tuple[float, float]],
    *,
    color: str,
    width: float = 4,
    dash: str | None = None,
) -> None:
    path_cmds = [f"M {points[0][0]} {points[0][1]}"]
    for px, py in points[1:]:
        path_cmds.append(f"L {px} {py}")
    attrs = {
        "d": " ".join(path_cmds),
        "fill": "none",
        "stroke": color,
        "stroke_width": width,
        "stroke_linecap": "round",
        "stroke_linejoin": "round",
    }
    if dash:
        attrs["stroke_dasharray"] = dash
    dwg.add(dwg.path(**attrs))


def shield(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    stroke: str,
    fill: str,
) -> None:
    shadow_points = [
        (x + w / 2 + 5, y + 7),
        (x + w + 5, y + 45),
        (x + w - 20 + 5, y + h - 90 + 7),
        (x + w / 2 + 5, y + h + 7),
        (x + 20 + 5, y + h - 90 + 7),
        (x + 5, y + 45 + 7),
    ]
    dwg.add(dwg.polygon(points=shadow_points, fill="#0F172A", opacity=0.055))
    points = [
        (x + w / 2, y),
        (x + w, y + 38),
        (x + w - 20, y + h - 90),
        (x + w / 2, y + h),
        (x + 20, y + h - 90),
        (x, y + 38),
    ]
    dwg.add(dwg.polygon(points=points, fill=fill, stroke=stroke, stroke_width=4))


def check_icon(dwg: svgwrite.Drawing, cx: float, cy: float, radius: float, color: str) -> None:
    dwg.add(dwg.circle(center=(cx, cy), r=radius, fill="#FFFFFF", stroke=color, stroke_width=3))
    dwg.add(
        dwg.path(
            d=f"M {cx-radius*0.45} {cy} L {cx-radius*0.1} {cy+radius*0.38} L {cx+radius*0.55} {cy-radius*0.42}",
            fill="none",
            stroke=color,
            stroke_width=4,
            stroke_linecap="round",
            stroke_linejoin="round",
        )
    )


def add_marker(dwg: svgwrite.Drawing, marker_id: str, color: str) -> None:
    marker = dwg.marker(
        id=marker_id,
        insert=(12, 6),
        size=(12, 12),
        orient="auto",
        markerUnits="userSpaceOnUse",
    )
    marker.add(dwg.path(d="M 0 0 L 12 6 L 0 12 z", fill=color))
    dwg.defs.add(marker)


def build_figure() -> svgwrite.Drawing:
    dwg = svgwrite.Drawing(str(SVG_PATH), size=(WIDTH, HEIGHT), viewBox=f"0 0 {WIDTH} {HEIGHT}")
    dwg.add(dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=COLORS["bg"]))

    for marker_id, color_key in [
        ("arrow_blue", "blue"),
        ("arrow_teal", "teal"),
        ("arrow_amber", "amber"),
        ("arrow_red", "red"),
        ("arrow_violet", "violet"),
    ]:
        add_marker(dwg, marker_id, COLORS[color_key])

    # Title region: normal SVG text avoids any artificial stretching or word gaps.
    add_text(dwg, WIDTH / 2, 105, "TabCF-Agent", size=92, weight=800, anchor="middle")
    add_text(
        dwg,
        WIDTH / 2,
        178,
        "An Auditable Causal Agent for Continuous-Treatment IV Analysis",
        size=44,
        weight=650,
        anchor="middle",
    )
    add_text(
        dwg,
        WIDTH / 2,
        228,
        "LLM compiles intent · deterministic tools compute · evidence gates decide what can be shown",
        size=30,
        weight=450,
        color=COLORS["muted"],
        anchor="middle",
        italic=True,
    )

    capsule(dwg, 750, 252, 570, 58, "LLM compiles intent", stroke=COLORS["blue"], fill=COLORS["blue_fill"], size=27)
    capsule(dwg, 1460, 252, 610, 58, "Deterministic tools compute", stroke=COLORS["teal"], fill=COLORS["teal_fill"], size=27)
    capsule(
        dwg,
        2230,
        252,
        900,
        58,
        "Evidence gates control every displayed number",
        stroke=COLORS["violet"],
        fill=COLORS["violet_fill"],
        size=27,
    )

    # Main grid geometry.
    x_edges = [30, 240, 660, 1130, 1580, 2610, 3400, 3810]
    header_y0, header_y1 = 330, 400
    grid_y0, lane1_y1, lane2_y1, grid_y1 = 400, 1010, 1480, 1990

    # Swimlane backgrounds.
    dwg.add(dwg.rect(insert=(30, grid_y0), size=(3780, lane1_y1 - grid_y0), fill=COLORS["blue_lane"]))
    dwg.add(dwg.rect(insert=(30, lane1_y1), size=(3780, lane2_y1 - lane1_y1), fill=COLORS["teal_lane"]))
    dwg.add(dwg.rect(insert=(30, lane2_y1), size=(3780, grid_y1 - lane2_y1), fill=COLORS["violet_lane"]))

    # Column header and grid lines.
    dwg.add(dwg.rect(insert=(30, header_y0), size=(3780, header_y1 - header_y0), fill=COLORS["white"], stroke=COLORS["grid"], stroke_width=2))
    for x in x_edges:
        dwg.add(dwg.line(start=(x, header_y0), end=(x, grid_y1), stroke=COLORS["grid"], stroke_width=2))
    for y in [header_y0, header_y1, lane1_y1, lane2_y1, grid_y1]:
        dwg.add(dwg.line(start=(30, y), end=(3810, y), stroke=COLORS["grid"], stroke_width=2))

    headers = [
        (450, "1. USER INPUT"),
        (895, "2. BOUNDED AI AGENT"),
        (1355, "3. EXPLICIT AGENT RUNTIME"),
        (2095, "4. DETERMINISTIC TABCF-IV ENGINE"),
        (3005, "5. RESULT BUNDLE & TRUST LAYER"),
        (3605, "6. TWO OUTPUT PROJECTIONS"),
    ]
    for cx, label in headers:
        add_text(dwg, cx, 375, label, size=27, weight=700, anchor="middle")

    # Swimlane labels are stacked but not rotated.
    add_multiline(dwg, 135, 645, ["AGENT", "CONTROL", "PLANE"], size=39, weight=750, color=COLORS["blue_dark"], anchor="middle", line_height=47)
    add_multiline(dwg, 135, 1195, ["DETERMINISTIC", "CAUSAL", "DATA PLANE"], size=32, weight=750, color=COLORS["teal_dark"], anchor="middle", line_height=42)
    add_multiline(dwg, 135, 1700, ["EVIDENCE,", "AUDIT &", "PRESENTATION"], size=32, weight=750, color=COLORS["violet_dark"], anchor="middle", line_height=42)

    # Column 1: user input.
    title_box(
        dwg,
        255,
        435,
        325,
        145,
        title="Natural-language question",
        body=["Mean or median · low / center /", "high treatment"],
        stroke=COLORS["blue"],
        fill=COLORS["white"],
        title_size=24,
        body_size=21,
        title_y_offset=42,
        body_y_offset=84,
    )
    title_box(
        dwg,
        255,
        710,
        325,
        170,
        title="Guided synthetic data",
        body=["or authorized CSV", "Exactly three numeric roles:", "Y, X, Z"],
        stroke=COLORS["blue"],
        fill=COLORS["white"],
        title_size=25,
        body_size=19,
        title_y_offset=40,
        body_y_offset=78,
        line_height=27,
    )
    rounded_box(dwg, 255, 910, 325, 155, stroke=COLORS["amber"], fill=COLORS["amber_fill"], shadow=True)
    add_text(dwg, 417.5, 952, "Scope lock", size=28, weight=750, color=COLORS["text"], anchor="middle")
    add_multiline(
        dwg,
        417.5,
        993,
        ["Continuous outcome Y", "continuous treatment X", "scalar instrument Z · W = ∅"],
        size=18,
        anchor="middle",
        line_height=27,
        font_family="DejaVu Sans",
    )
    rounded_box(dwg, 255, 1085, 325, 82, stroke=COLORS["grid"], fill=COLORS["white"], shadow=False, radius=16)
    add_multiline(
        dwg,
        417.5,
        1115,
        ["TabCF-IV only · no general causal router", "no Hillstrom path"],
        size=17,
        color=COLORS["muted"],
        anchor="middle",
        line_height=23,
    )

    # Question transfer to Gemini; raw data has no path to Gemini.
    rounded_box(dwg, 590, 405, 145, 72, stroke=COLORS["amber"], fill=COLORS["amber_fill"], shadow=False, radius=13)
    add_multiline(
        dwg,
        662.5,
        433,
        ["Question + generic roles", "+ symbolic labels only"],
        size=14,
        weight=600,
        color=COLORS["amber"],
        anchor="middle",
        line_height=19,
    )
    arrow_path(dwg, [(580, 500), (742, 500)], color=COLORS["amber"], marker_id="arrow_amber", width=4, dash="12 10")
    rounded_box(dwg, 590, 575, 145, 105, stroke=COLORS["amber"], fill=COLORS["amber_fill"], shadow=False, radius=14, dash="9 7")
    add_multiline(
        dwg,
        662.5,
        610,
        ["No data rows", "No actual intervention", "values"],
        size=15,
        weight=600,
        color=COLORS["amber"],
        anchor="middle",
        line_height=20,
    )

    # Column 2: bounded compiler, mapper, and immutable specification.
    rounded_box(dwg, 750, 420, 345, 300, stroke=COLORS["blue"], fill=COLORS["blue_fill"])
    add_text(dwg, 922.5, 463, "Bounded Gemini Compiler", size=25, weight=750, color=COLORS["blue_dark"], anchor="middle")
    add_multiline(dwg, 922.5, 510, ["Understand intent", "Choose an allowed summary", "Analyze · Clarify · Block"], size=23, anchor="middle", line_height=31)
    divider(dwg, 780, 612, 1065, 612, COLORS["blue"])
    add_multiline(dwg, 922.5, 648, ["mean / median", "low / center / high", "single structured request"], size=22, weight=520, color=COLORS["blue_dark"], anchor="middle", line_height=28)

    title_box(
        dwg,
        760,
        755,
        325,
        135,
        title="Local Deterministic Mapper",
        body=["Symbolic labels → actual", "intervention values"],
        stroke=COLORS["blue"],
        fill=COLORS["white"],
        title_size=22,
        body_size=20,
        title_y_offset=38,
        body_y_offset=79,
        line_height=28,
    )
    arrow_path(dwg, [(922.5, 720), (922.5, 750)], color=COLORS["blue"], marker_id="arrow_blue", width=5)

    rounded_box(dwg, 715, 930, 400, 280, stroke=COLORS["blue"], fill=COLORS["blue_fill"])
    add_multiline(dwg, 915, 968, ["Immutable Analysis", "Specification"], size=24, weight=750, color=COLORS["blue_dark"], anchor="middle", line_height=27)
    chip(dwg, 740, 1005, 165, 55, "Y / X / Z roles", stroke=COLORS["blue"], fill=COLORS["white"], size=20)
    chip(dwg, 925, 1005, 165, 55, "objective", stroke=COLORS["blue"], fill=COLORS["white"], size=20)
    chip(dwg, 740, 1075, 165, 55, "intervention grid", stroke=COLORS["blue"], fill=COLORS["white"], size=19)
    chip(dwg, 925, 1075, 165, 55, "backend profile", stroke=COLORS["blue"], fill=COLORS["white"], size=19)
    chip(dwg, 740, 1145, 165, 55, "dataset hash", stroke=COLORS["blue"], fill=COLORS["white"], size=20)
    chip(dwg, 925, 1145, 165, 55, "seed", stroke=COLORS["blue"], fill=COLORS["white"], size=20)
    arrow_path(dwg, [(915, 890), (915, 925)], color=COLORS["blue"], marker_id="arrow_blue", width=5)

    # Column 3: explicit runtime.
    rounded_box(dwg, 1160, 480, 390, 520, stroke=COLORS["blue"], fill=COLORS["blue_fill"])
    add_text(dwg, 1355, 528, "Causal Agent Runtime", size=30, weight=760, color=COLORS["blue_dark"], anchor="middle")
    rounded_box(dwg, 1185, 560, 340, 112, stroke=COLORS["blue"], fill=COLORS["white"], shadow=False, radius=16)
    add_multiline(dwg, 1355, 590, ["Received → Compile → Validate Spec", "→ Execute → Validate Evidence", "→ Complete"], size=17, weight=620, color=COLORS["blue_dark"], anchor="middle", line_height=25)

    for yy, label, stroke, fill in [
        (705, "Clarify", COLORS["blue"], COLORS["white"]),
        (775, "Approval required", COLORS["blue"], COLORS["white"]),
        (845, "Block", COLORS["red"], COLORS["red_fill"]),
    ]:
        rounded_box(dwg, 1205, yy, 300, 52, stroke=stroke, fill=fill, shadow=False, radius=14)
        add_text(dwg, 1355, yy + 35, label, size=23, weight=600, color=stroke if label == "Block" else COLORS["text"], anchor="middle")
    add_multiline(dwg, 1355, 935, ["Single bounded orchestrator", "Typed state transitions · fail closed"], size=21, color=COLORS["muted"], anchor="middle", line_height=25)

    arrow_path(dwg, [(1115, 1065), (1135, 1065), (1135, 690), (1155, 690)], color=COLORS["blue"], marker_id="arrow_blue", width=5)
    arrow_path(dwg, [(1550, 680), (1595, 680)], color=COLORS["blue"], marker_id="arrow_blue", width=5)

    # Dataset path to the local deterministic gate, intentionally bypassing Gemini.
    arrow_path(
        dwg,
        [(580, 795), (640, 795), (640, 1215), (1590, 1215), (1590, 930), (1618, 930)],
        color=COLORS["teal"],
        marker_id="arrow_teal",
        width=5,
    )

    # External managed backend.
    rounded_box(dwg, 1845, 415, 445, 150, stroke=COLORS["amber"], fill=COLORS["amber_fill"], dash="12 9")
    add_text(dwg, 2067.5, 457, "Prior Labs", size=28, weight=750, anchor="middle")
    add_text(dwg, 2067.5, 495, "Managed TabPFN", size=28, weight=750, color=COLORS["amber"], anchor="middle")
    add_text(dwg, 2067.5, 535, "Service-version-traceable backend", size=20, color=COLORS["muted"], anchor="middle")
    rounded_box(dwg, 2320, 430, 225, 118, stroke=COLORS["amber"], fill=COLORS["amber_fill"], dash="10 8", shadow=False, radius=16)
    add_multiline(dwg, 2432.5, 472, ["Separate transfer", "from Gemini"], size=21, weight=650, color=COLORS["amber"], anchor="middle", line_height=28)

    # Main deterministic engine.
    rounded_box(dwg, 1605, 610, 965, 780, stroke=COLORS["teal"], fill=COLORS["teal_fill"], stroke_width=4, radius=28)
    add_text(dwg, 2087.5, 660, "Deterministic TabCF-IV Engine", size=32, weight=780, color=COLORS["teal_dark"], anchor="middle")

    # Input and scope gate.
    rounded_box(dwg, 1625, 700, 175, 555, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_multiline(dwg, 1712.5, 742, ["Local Input &", "Scope Gates"], size=24, weight=750, color=COLORS["teal_dark"], anchor="middle", line_height=28)
    add_multiline(
        dwg,
        1712.5,
        820,
        [
            "Explicit Y / X / Z",
            "mapping",
            "Consent and numeric-data",
            "checks",
            "Role, hash, profile and",
            "backend checks",
            "Reject W, extra roles and",
            "unsupported treatments",
        ],
        size=16,
        anchor="middle",
        line_height=29,
    )

    # Stage 1.
    rounded_box(dwg, 1815, 770, 145, 220, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_text(dwg, 1887.5, 815, "Stage 1", size=25, weight=750, color=COLORS["teal_dark"], anchor="middle")
    add_multiline(dwg, 1887.5, 858, ["Estimate", "F(X | Z)", "Construct", "control rank V"], size=16, anchor="middle", line_height=27)

    # Diagnostics and support gate.
    rounded_box(dwg, 1975, 735, 215, 315, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_multiline(dwg, 2082.5, 780, ["Diagnostics &", "Joint Support Gate"], size=23, weight=750, color=COLORS["teal_dark"], anchor="middle", line_height=27)
    add_multiline(dwg, 2082.5, 846, ["First-stage relevance", "Control-rank calibration", "Residual dependence", "Intervention support"], size=16, anchor="middle", line_height=32)

    # Stage 2.
    rounded_box(dwg, 2205, 770, 155, 220, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_text(dwg, 2282.5, 815, "Stage 2", size=25, weight=750, color=COLORS["teal_dark"], anchor="middle")
    add_multiline(dwg, 2282.5, 858, ["Fit E[Y | X,V]", "and", "F(Y | X,V)"], size=16, anchor="middle", line_height=28)

    # Integration and interventional distribution share the right-most subcolumn.
    rounded_box(dwg, 2375, 730, 175, 155, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_multiline(dwg, 2462.5, 770, ["Deterministic", "integration", "over V"], size=19, weight=750, color=COLORS["teal_dark"], anchor="middle", line_height=29)

    rounded_box(dwg, 2375, 920, 175, 385, stroke=COLORS["teal"], fill=COLORS["white"], shadow=False, radius=18)
    add_multiline(dwg, 2462.5, 960, ["Interventional", "distribution", "F(Y | do(X = x))"], size=18, weight=750, color=COLORS["teal_dark"], anchor="middle", line_height=27)
    chip(dwg, 2392, 1045, 141, 48, "Mean", stroke=COLORS["teal"], fill=COLORS["teal_fill"], size=20)
    chip(dwg, 2392, 1105, 141, 48, "Median / Quantiles", stroke=COLORS["teal"], fill=COLORS["teal_fill"], size=14)
    chip(dwg, 2392, 1165, 141, 48, "Threshold risk", stroke=COLORS["teal"], fill=COLORS["teal_fill"], size=18)
    chip(dwg, 2392, 1225, 141, 48, "Directed contrast", stroke=COLORS["teal"], fill=COLORS["teal_fill"], size=14)

    # Deterministic pipeline arrows.
    arrow_path(dwg, [(1800, 875), (1810, 875)], color=COLORS["teal"], marker_id="arrow_teal", width=4)
    arrow_path(dwg, [(1960, 875), (1970, 875)], color=COLORS["teal"], marker_id="arrow_teal", width=4)
    arrow_path(dwg, [(2190, 875), (2200, 875)], color=COLORS["teal"], marker_id="arrow_teal", width=4)
    arrow_path(dwg, [(2360, 825), (2370, 825)], color=COLORS["teal"], marker_id="arrow_teal", width=4)
    arrow_path(dwg, [(2462.5, 885), (2462.5, 915)], color=COLORS["teal"], marker_id="arrow_teal", width=4)

    # Success and blocked branches.
    rounded_box(dwg, 1985, 1070, 200, 66, stroke=COLORS["teal"], fill=COLORS["teal_fill"], shadow=False, radius=15)
    add_multiline(dwg, 2085, 1096, ["Supported or", "weak support"], size=18, weight=650, color=COLORS["teal_dark"], anchor="middle", line_height=22)
    rounded_box(dwg, 2200, 1070, 160, 66, stroke=COLORS["amber"], fill=COLORS["amber_fill"], shadow=False, radius=15)
    add_multiline(dwg, 2280, 1096, ["Continue with", "warning"], size=18, weight=650, color=COLORS["amber"], anchor="middle", line_height=22)
    plain_path(dwg, [(2082.5, 1050), (2082.5, 1065)], color=COLORS["teal"], width=4)
    arrow_path(dwg, [(2185, 1103), (2195, 1103)], color=COLORS["teal"], marker_id="arrow_teal", width=4)
    arrow_path(dwg, [(2280, 1070), (2280, 1000), (2282.5, 995)], color=COLORS["teal"], marker_id="arrow_teal", width=4)

    rounded_box(dwg, 1945, 1170, 415, 150, stroke=COLORS["red"], fill=COLORS["red_fill"], stroke_width=3.5, radius=18)
    add_text(dwg, 2152.5, 1214, "Outside support — BLOCKED", size=25, weight=760, color=COLORS["red"], anchor="middle")
    add_multiline(dwg, 2152.5, 1253, ["Stops before Stage 2", "No number · No evidence · No plot"], size=20, anchor="middle", line_height=30)
    arrow_path(dwg, [(2082.5, 1050), (2082.5, 1155)], color=COLORS["red"], marker_id="arrow_red", width=4)

    # Managed service transfers to Stage 1 and Stage 2.
    add_multiline(dwg, 1825, 600, ["Authorized Y/X/Z rows", "+ prediction grids"], size=18, weight=650, color=COLORS["amber"], anchor="middle", line_height=23)
    add_multiline(dwg, 2310, 600, ["Authorized Y/X/Z rows", "+ prediction grids"], size=18, weight=650, color=COLORS["amber"], anchor="middle", line_height=23)
    arrow_path(dwg, [(1985, 565), (1805, 565), (1805, 720), (1887.5, 720), (1887.5, 760)], color=COLORS["amber"], marker_id="arrow_amber", width=4, dash="12 10")
    arrow_path(dwg, [(2160, 565), (2545, 565), (2545, 720), (2282.5, 720), (2282.5, 760)], color=COLORS["amber"], marker_id="arrow_amber", width=4, dash="12 10")

    # Result bundle and audit layer.
    rounded_box(dwg, 1900, 1530, 350, 350, stroke=COLORS["violet"], fill=COLORS["violet_fill"])
    add_multiline(dwg, 2075, 1580, ["Canonical Validated", "Result Bundle"], size=28, weight=760, color=COLORS["violet_dark"], anchor="middle", line_height=32)
    add_multiline(dwg, 2075, 1665, ["Interventional distributions", "Requested query result", "Diagnostics and support", "Warnings and assumptions", "Unrounded numerical values"], size=22, anchor="middle", line_height=38)

    # Engine output enters the canonical bundle.
    arrow_path(dwg, [(2462.5, 1305), (2462.5, 1450), (2075, 1450), (2075, 1525)], color=COLORS["teal"], marker_id="arrow_teal", width=5)

    audit_boxes = [
        (2290, 1530, "Evidence Ledger", ["IDs · hashes · raw values", "units · provenance"]),
        (2290, 1665, "Audit Trail", ["State events · backend metadata", "immutable run artifacts"]),
        (2290, 1800, "Validated Cache", ["Ordinary follow-ups", "without refitting"]),
    ]
    for x, y, title, body in audit_boxes:
        rounded_box(dwg, x, y, 300, 105, stroke=COLORS["violet"], fill=COLORS["white"], shadow=False, radius=17)
        add_text(dwg, x + 150, y + 35, title, size=24, weight=730, color=COLORS["violet_dark"], anchor="middle")
        add_multiline(dwg, x + 150, y + 66, body, size=18, anchor="middle", line_height=22)

    # Bundle to three audit components.
    arrow_path(dwg, [(2250, 1600), (2275, 1600), (2275, 1582), (2285, 1582)], color=COLORS["violet"], marker_id="arrow_violet", width=4)
    arrow_path(dwg, [(2250, 1705), (2285, 1705)], color=COLORS["violet"], marker_id="arrow_violet", width=4)
    arrow_path(dwg, [(2250, 1810), (2275, 1810), (2275, 1852), (2285, 1852)], color=COLORS["violet"], marker_id="arrow_violet", width=4)

    # Evidence validation gate.
    shield(dwg, 2640, 1505, 420, 390, stroke=COLORS["violet"], fill=COLORS["white"])
    add_multiline(dwg, 2850, 1565, ["Evidence", "Validation Gate"], size=30, weight=780, color=COLORS["violet_dark"], anchor="middle", line_height=33)
    add_multiline(dwg, 2850, 1658, ["Dataset hash matches", "Specification matches", "Bundle ↔ evidence agreement", "Unknown or mismatched values", "fail closed"], size=21, anchor="middle", line_height=36)
    check_icon(dwg, 2755, 1842, 22, COLORS["violet"])
    add_multiline(dwg, 2790, 1838, ["Independent artifact", "verifier"], size=17, weight=600, color=COLORS["violet_dark"], anchor="start", line_height=22)

    # Audit components to evidence gate.
    arrow_path(dwg, [(2590, 1582), (2630, 1582)], color=COLORS["violet"], marker_id="arrow_violet", width=4)
    arrow_path(dwg, [(2590, 1717), (2630, 1717)], color=COLORS["violet"], marker_id="arrow_violet", width=4)
    arrow_path(dwg, [(2590, 1852), (2630, 1852)], color=COLORS["violet"], marker_id="arrow_violet", width=4)

    # Column 6: two projections from one validated bundle.
    rounded_box(dwg, 3420, 515, 370, 370, stroke=COLORS["teal"], fill=COLORS["white"])
    add_text(dwg, 3605, 563, "Visitor-safe Demo", size=29, weight=760, color=COLORS["teal_dark"], anchor="middle")
    add_multiline(dwg, 3448, 625, ["Direct natural-language answer", "Data-support status", "Mapped warnings and limitations", "Human-readable distribution plot"], size=19, anchor="start", line_height=40)
    divider(dwg, 3448, 805, 3762, 805, COLORS["teal"])
    add_text(dwg, 3605, 848, "3-significant-digit display", size=21, weight=600, color=COLORS["teal_dark"], anchor="middle")

    # Shared-source bracket between the two output projections.
    plain_path(dwg, [(3435, 1030), (3425, 1030), (3425, 1175), (3445, 1175)], color=COLORS["violet"], width=4)
    plain_path(dwg, [(3775, 1030), (3795, 1030), (3795, 1175), (3775, 1175)], color=COLORS["violet"], width=4)
    add_multiline(dwg, 3605, 1080, ["Two projections ·", "one validated bundle"], size=25, weight=690, color=COLORS["violet_dark"], anchor="middle", line_height=32)

    rounded_box(dwg, 3420, 1530, 370, 340, stroke=COLORS["violet"], fill=COLORS["white"])
    add_text(dwg, 3605, 1578, "Operator Audit Artifacts", size=28, weight=760, color=COLORS["violet_dark"], anchor="middle")
    add_multiline(dwg, 3448, 1640, ["Unrounded values", "Evidence and specification IDs", "Gemini compilation trace", "Backend and service metadata", "Audit plot"], size=19, anchor="start", line_height=40)

    # Split from the validation gate to both projections.
    plain_path(dwg, [(3060, 1700), (3360, 1700)], color=COLORS["violet"], width=5)
    plain_path(dwg, [(3360, 700), (3360, 1700)], color=COLORS["violet"], width=5)
    arrow_path(dwg, [(3360, 700), (3415, 700)], color=COLORS["violet"], marker_id="arrow_violet", width=5)
    arrow_path(dwg, [(3360, 1700), (3415, 1700)], color=COLORS["violet"], marker_id="arrow_violet", width=5)

    # Legend.
    rounded_box(dwg, 680, 2020, 2480, 100, stroke=COLORS["grid"], fill=COLORS["white"], shadow=False, radius=18)
    legend_items = [
        (750, COLORS["blue"], False, "Blue — agent control"),
        (1220, COLORS["teal"], False, "Teal — deterministic computation"),
        (1800, COLORS["amber"], True, "Amber dashed — external transfer"),
        (2440, COLORS["red"], False, "Red — blocked path"),
        (2820, COLORS["violet"], False, "Violet — evidence and audit"),
    ]
    for x, color, dashed, label in legend_items:
        line_attrs = {
            "start": (x, 2070),
            "end": (x + 70, 2070),
            "stroke": color,
            "stroke_width": 5,
        }
        if dashed:
            line_attrs["stroke_dasharray"] = "13 9"
        dwg.add(dwg.line(**line_attrs))
        add_text(dwg, x + 88, 2079, label, size=20, weight=560, color=COLORS["text"])

    return dwg


def main() -> None:
    dwg = build_figure()
    dwg.save(pretty=True)
    cairosvg.svg2png(
        url=str(SVG_PATH),
        write_to=str(PNG_PATH),
        output_width=WIDTH,
        output_height=HEIGHT,
    )
    print(f"Created {SVG_PATH}")
    print(f"Created {PNG_PATH}")


if __name__ == "__main__":
    main()
