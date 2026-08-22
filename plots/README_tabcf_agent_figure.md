# TabCF-Agent overview figure

This package contains a reproducible, editable version of the architecture figure.

## Files

- `tabcf_agent_overview_editable.svg` — editable vector source. Open it directly in Figma, Adobe Illustrator, Inkscape, Affinity Designer, or a browser.
- `tabcf_agent_overview_4k.png` — 3840 × 2160 raster export for a website hero section, slides, or manuscripts.
- `generate_tabcf_agent_overview.py` — deterministic Python generator for both files.

## Regenerate

```bash
python -m pip install svgwrite cairosvg
python generate_tabcf_agent_overview.py
```

The script writes the SVG and PNG into the same directory as the script.

## Modify

The generator is organized into:

1. global canvas, typography, and color constants;
2. reusable drawing helpers (`rounded_box`, `chip`, `arrow_path`, `shield`, and text helpers);
3. one `build_figure()` function containing the figure text and coordinates.

For text edits, search for the visible label inside `build_figure()` and replace the string. For layout edits, change the associated `x`, `y`, `w`, and `h` values. For theme edits, change the `COLORS` dictionary near the top of the file.

The SVG uses normal vector text without `textLength`, horizontal scaling, or stretched glyphs. This avoids the abnormal word spacing and distorted typography that appeared in the earlier raster-generated version.

## Output specification

- Aspect ratio: 16:9
- Raster resolution: 3840 × 2160
- Primary font: Inter
- Mathematical-symbol fallback: DejaVu Sans
- Vector format: SVG 1.1-compatible geometry and text
