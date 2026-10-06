"""Render the saved v3 cigarette run as standalone HTML; standard library only.

No estimator imports, fitting, provider requests, or edits to source artifacts.
Run from any directory; defaults are relative to this script's repository.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PREFIX = 'agentic-tabcf-submission-v3/'
RUN = 'results/cigarette-35/attempt-1-api/'
COLORS = ('#176c8c', '#b74b28')


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def pretty(value: object) -> str:
    return escaped(json.dumps(value, indent=2, ensure_ascii=False))


def render(archive: Path) -> str:
    with zipfile.ZipFile(archive) as source:
        def read(name: str) -> str:
            return source.read(PREFIX + name).decode('utf-8')

        bundle = json.loads(read(RUN + 'result_bundle.json'))
        projection = json.loads(read(RUN + 'distribution_results.json'))
        specification = json.loads(read(RUN + 'specification.json'))
        ledger = [json.loads(line) for line in read(RUN + 'evidence_records.jsonl').splitlines()]
        backend = json.loads(read(RUN + 'backend_manifest.json'))
        dataset = json.loads(read(RUN + 'dataset_manifest.json'))
        manifest = json.loads(read(RUN + 'run_manifest.json'))
        provenance = read('examples/cigarette/SOURCE.md')
        design = read('examples/cigarette/DESIGN.md')
        historical_report = read(RUN + 'report.md')
    distribution = projection['distribution']
    evidence = projection['evidence']
    metrics = {m['key']: m for m in distribution['metrics']}
    by_id = {e['evidence_id']: e for e in ledger}
    # Ordinary input consistency checks catch accidental cross-run projections.
    if bundle['distribution'] != distribution or specification['distribution'] != distribution['request']:
        raise ValueError('The saved bundle, projection, and specification disagree.')
    for key, metric in metrics.items():
        record = evidence[key]
        if record != by_id[record['evidence_id']] or record['value_raw'] != metric['value'] or record['units'] != metric['units']:
            raise ValueError(f'Inconsistent saved metric/evidence: {key}')
        for identity in ('run_id', 'result_bundle_id', 'specification_id', 'dataset_hash'):
            if record[identity] != bundle[identity]:
                raise ValueError(f'Cross-run evidence: {key}')
    request = distribution['request']
    prices = request['prices']
    threshold = request['threshold']
    units = escaped(request['outcome_units'])
    price_units = escaped(request['treatment_units'])

    def value(key: str) -> float:
        return metrics[key]['value']

    def number(key: str, multiplier: float = 1, suffix: str = '') -> str:
        raw = value(key)
        shown = f'{raw * multiplier:.1f}'
        if shown == '-0.0':
            shown = '0.0'
        eid = evidence[key]['evidence_id']
        return (f'<a class="metric" href="#{eid}" data-key="{key}" '
                f'data-value="{raw!r}" data-multiplier="{multiplier}" '
                f'title="Evidence: {eid}">{shown}{suffix}</a>')

    def legend() -> str:
        return '<div class="legend">' + ''.join(
            f'<span style="color:{color}"><b>{"━━" if i == 0 else "┅┅"}</b> Price {price}</span>'
            for i, (price, color) in enumerate(zip(prices, COLORS))) + '</div>'

    def chart(kind: str) -> str:
        cdf = kind == 'cdf'
        axis = distribution['outcome_axis']
        groups = distribution['curves'] if cdf else distribution['densities']
        field = 'cdf' if cdf else 'pdf'
        ymax = 1 if cdf else max(value(k) for g in groups for k in g[field]) * 1.1
        left, top, width, height = 65, 35, 620, 260
        def x(v: float) -> float:
            return left + width * (v - axis[0]) / (axis[-1] - axis[0])
        def y(v: float) -> float:
            return top + height * (1 - v / ymax)
        parts = [f'<svg viewBox="0 0 720 360" role="img" aria-label="{kind.upper()} by price on the evaluated sales grid">']
        parts.append(f'<text x="{left}" y="18">{"Cumulative probability · P(sales ≤ c)" if cdf else "Density · per pack/person/year"}</text>')
        for i in range(5):
            v = ymax * i / 4
            tick = f'{v:.2f}' if cdf else f'{v:.3f}'
            parts.append(f'<path d="M{left} {y(v)}h{width}" stroke="#dce3e5"/><text x="55" y="{y(v)+5}" text-anchor="end">{tick}</text>')
        for i in range(6):
            v = axis[0] + (axis[-1] - axis[0]) * i / 5
            parts.append(f'<text x="{x(v)}" y="321" text-anchor="middle">{v:.0f}</text>')
        parts.append(f'<text x="375" y="348" text-anchor="middle">Sales · {units}</text>')
        for i, group in enumerate(groups):
            keys = group[field]
            if cdf:
                points = [(axis[j], value(k)) for j, k in enumerate(keys)]
            else:
                # The saved finite-difference density applies over each interval.
                points = [(a, value(k)) for j, k in enumerate(keys) for a in (axis[j], axis[j+1])]
            coords = ' '.join(f'{x(a):.6f},{y(b):.6f}' for a, b in points)
            ids = ' '.join(evidence[k]['evidence_id'] for k in keys)
            dash = 'stroke-dasharray="7,4"' if i else ''
            parts.append(f'<polyline data-keys="{escaped(" ".join(keys))}" data-evidence="{ids}" fill="none" stroke="{COLORS[i]}" stroke-width="2.5" {dash} points="{coords}"/>')
        if cdf:
            parts.append(f'<path d="M{x(threshold)} {top}v{height}" stroke="#647078" stroke-dasharray="3,5"/>')
            for i, key in enumerate(distribution['threshold_cdf']):
                parts.append(f'<circle cx="{x(threshold)}" cy="{y(value(key))}" r="5" fill="{COLORS[i]}" data-key="{key}" data-value="{value(key)!r}"><title>Price {prices[i]}: P(sales ≤ {threshold}) = {value(key)!r}; {evidence[key]["evidence_id"]}</title></circle>')
        parts.append('</svg>')
        return '<div class="chart-scroll">' + ''.join(parts) + '</div>'

    rows = ''.join('<tr><th scope="row">' + f'{q["level"]:.0%}' + (' · median' if q['level'] == .5 else '') + '</th>' + ''.join(f'<td>{number(k)}</td>' for k in q['values'] + [q['difference']]) + '</tr>' for q in distribution['quantiles'])
    cards = ''.join(f'<div class="probability"><span>Price {prices[i]}</span><strong>{number(key, suffix="%")}</strong><div class="bar"><i style="width:{value(key)}%;background:{COLORS[i]}"></i></div><small>P(sales &gt; {threshold})</small></div>' for i, key in enumerate(distribution['probabilities']))
    med = next(q for q in distribution['quantiles'] if q['level'] == .5)
    summary_keys = [m['key'] for m in distribution['metrics'] if not m['key'].startswith(('cdf:', 'density:'))]
    evidence_rows = ''.join(f'<tr><td><code>{key}</code></td><td>{value(key)!r}</td><td>{escaped(metrics[key]["units"])}</td><td><a href="#{evidence[key]["evidence_id"]}">{evidence[key]["evidence_id"]}</a></td></tr>' for key in summary_keys)
    records = '\n'.join(f'<details id="{e["evidence_id"]}"><summary>{escaped(e["claim_type"])} · {e["evidence_id"]}</summary><pre>{pretty(e)}</pre></details>' for e in ledger)
    source_sections = ''.join(f'<details><summary>{escaped(name)}</summary><pre>{pretty(obj)}</pre></details>' for name, obj in [
        ('Original specification.json', specification), ('Original backend_manifest.json', backend),
        ('Original dataset_manifest.json', dataset), ('Original run_manifest.json', manifest),
        ('Distribution grid, metric keys and raw values', distribution)])
    warnings = ''.join(f'<li><code>{escaped(w["code"])}</code>: {escaped(w["message"])}</li>' for w in bundle['warnings'])
    assumptions = ''.join(f'<li>{escaped(a)}</li>' for a in bundle['assumptions'])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic TabCF · Cigarette sales example</title>
<style>
:root{{color-scheme:light;--ink:#17333e;--muted:#52656e;--teal:#176c8c}}*{{box-sizing:border-box}}body{{margin:0;background:#f4f5f1;color:var(--ink);font:17px/1.65 system-ui,-apple-system,sans-serif}}main{{max-width:960px;margin:auto;padding:40px 28px 70px}}header{{padding:25px 0 32px;border-bottom:2px solid #bfcfd0}}.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:750;color:var(--teal)}}h1{{font-size:clamp(32px,5vw,52px);line-height:1.12;max-width:770px;margin:18px 0}}h2{{font-size:27px;line-height:1.25;margin:0 0 16px}}h3{{font-size:20px;margin:26px 0 8px}}p{{margin:12px 0}}.lead{{font-size:20px;max-width:760px}}.badge{{display:inline-block;background:#dcece9;padding:4px 10px;border-radius:5px;font-size:13px}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin-top:24px}}a{{color:#125873;text-underline-offset:3px}}section{{margin-top:38px}}.step{{display:block;font-size:12px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px}}.panel{{background:white;border:1px solid #d9e1df;border-radius:14px;padding:26px}}.limits{{background:#fff5e5;border-left:4px solid #c38636;padding:17px 22px;margin:22px 0}}.limits p{{margin:5px 0}}.small,small{{font-size:14px;color:var(--muted)}}.metric{{font-variant-numeric:tabular-nums;white-space:nowrap;text-decoration-style:dotted}}table{{width:100%;border-collapse:collapse;font-size:16px}}th,td{{padding:13px 9px;border-bottom:1px solid #dce3e5;text-align:right}}th:first-child,td:first-child{{text-align:left}}thead{{background:#eef4f3}}caption{{text-align:left;font-size:14px;margin-bottom:10px}}.table-scroll,.chart-scroll{{overflow-x:auto}}svg{{width:100%;min-width:540px;display:block}}svg text{{font:14px system-ui;fill:#344d58}}.legend{{display:flex;gap:28px;flex-wrap:wrap;font-size:15px;margin:12px 0}}.probabilities{{display:grid;grid-template-columns:1fr 1fr;gap:25px;margin:20px 0}}.probability strong{{display:block;font-size:36px}}.bar{{height:10px;background:#e7edeb;border-radius:5px;margin:8px 0}}.bar i{{display:block;height:100%;border-radius:5px}}.reading{{background:#eef4f3;padding:14px 18px;font-size:15px}}ol{{padding-left:24px}}li{{margin:10px 0}}details{{border:1px solid #d2dcda;border-radius:8px;padding:12px 16px;margin:12px 0;background:#fff}}summary{{cursor:pointer;font-weight:650;overflow-wrap:anywhere}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.5;background:#f1f4f3;padding:14px;max-height:480px;overflow:auto}}code{{font-size:.85em;overflow-wrap:anywhere}}.technical table{{font-size:12px}}.technical td{{text-align:left;overflow-wrap:anywhere}}footer{{margin-top:40px;border-top:1px solid #c8d6d3;padding-top:20px;font-size:14px}}:target{{scroll-margin-top:24px;outline:2px solid #b77d2d}}a:focus-visible,summary:focus-visible{{outline:3px solid #b77d2d}}@media(max-width:600px){{main{{padding:20px 16px 40px}}.panel{{padding:18px 14px}}body{{font-size:16px}}.lead{{font-size:18px}}h2{{font-size:24px}}th,td{{padding:10px 6px;font-size:14px}}.probabilities{{gap:14px}}.probability strong{{font-size:30px}}nav{{gap:14px}}}}@media print{{body{{background:white}}main{{max-width:none}}details{{break-inside:avoid}}}}
</style></head><body><main>
<header><div class="eyebrow">Agentic TabCF · Saved example report</div><h1>If cigarette prices rose, how might the sales distribution change?</h1>
<p class="lead">Compare a price of <b>{prices[0]}</b> with <b>{prices[1]} {price_units}</b>. Look beyond an average: compare lower, middle and upper sales percentiles, then an explicitly requested sales threshold.</p>
<span class="badge">Track T · Real data · Exploratory point estimates</span><p class="small">Presentation of an existing TabPFN-3.5 run · development_only · no new analysis</p>
<nav aria-label="Report sections"><a href="#results">Results</a><a href="#curves">Read the curves</a><a href="#workflow">How it works</a><a href="#technical">Evidence &amp; details</a></nav></header>
<section id="data"><span class="step">The question and the data</span><h2>Sales across state–years, not individual smokers</h2>
<p>Each observation is a state in a year, and each receives equal weight. The uploaded example contains <b>{dataset['row_count']} observations</b>: the bundled source note selects 48 states in 1985, 1990 and 1995 from <b>Ecdat::Cigarette</b>, credited to Jonathan Gruber. Sales are measured in <b>{units}</b>; prices are in <b>{price_units}</b>.</p>
<p>The analysis uses logged sales, logged real price and a real sales-tax component as an instrument—a proposed source of price variation. Observed price–sales correlation alone cannot answer the price-change question: demand and other factors can affect both.</p>
<p class="small">Source and transformation details are preserved in <a href="#provenance">the embedded provenance note</a>. This is a related demonstration, not the exact TabCF paper sample, a population-weighted analysis, or an intervention on taxes.</p></section>
<section id="results" class="panel"><span class="step">What the saved model estimates show</span><h2>A lower median in the higher-price scenario</h2>
<p class="lead">The estimated median is {number(med['values'][0])} at price {prices[0]} and {number(med['values'][1])} at price {prices[1]}: a change of <b>{number(med['difference'])} {units}</b>.</p>
<div class="limits"><strong>Exploratory point estimates only.</strong><p>No confidence intervals or significance conclusions are available. A causal interpretation depends on unverified instrumental-variable and control-function assumptions. Income, state/year effects, omitted confounding and dependence across repeated observations of a state are not addressed. A control-rank calibration warning was recorded.</p><p>These estimates do not establish individual effects, policy benefits, or model superiority.</p></div>
<h3>Compare the same percentile in each distribution</h3><p>The median is the middle of a distribution. The lower and upper quartiles mark its quarter and three-quarter positions. A row compares two distribution positions; it does not follow the same people or define a group of “low consumers.”</p>
<div class="table-scroll"><table><caption>All values: {units}. Change = price {prices[1]} minus price {prices[0]}. Select any result to inspect its original evidence.</caption><thead><tr><th>Percentile</th><th>Price {prices[0]}</th><th>Price {prices[1]}</th><th>Change</th></tr></thead><tbody>{rows}</tbody></table></div>
<h3>How often would sales exceed the requested threshold?</h3><p>The specified threshold is <b>{threshold} {units}</b>. It is an illustrative value supplied for this example, not a health standard, an extreme-tail analysis or a policy target.</p>
<div class="probabilities">{cards}</div><p>Change in the probability of <b>strictly exceeding</b> the threshold: <b>{number(distribution['probability_difference'])} percentage points</b> (higher price minus lower price).</p></section>
<section id="curves" class="panel"><span class="step">The full evaluated distributions</span><h2>Two views of the same saved CDF</h2>{legend()}
<h3>Cumulative distribution function (CDF)</h3><p>At any sales value c, the height gives the estimated probability of sales <b>at or below</b> c. The dashed vertical line marks the requested threshold.</p>{chart('cdf')}
<div class="reading">At c = {threshold}, the marked CDF probabilities <b>P(sales ≤ {threshold})</b> are {number(distribution['threshold_cdf'][0], 100, '%')} at price {prices[0]} and {number(distribution['threshold_cdf'][1], 100, '%')} at price {prices[1]}. These are cumulative probabilities. The earlier bars show their complements, <b>P(sales &gt; {threshold}) = 1 − CDF</b>.</div>
<h3>CDF-derived approximate probability density (PDF)</h3><p>Height describes how concentrated probability is around a sales value; height itself is not a probability. Area over an interval approximates the probability in that interval.</p>{chart('pdf')}
<p class="small">The saved density is the change in the CDF between adjacent grid points divided by their sales-unit spacing. It is shown as an interval step plot, not a separately fitted curve. No smoothing, tail extrapolation or renormalization is applied. Both views stop at the evaluated grid; omitted tail mass means the density need not integrate to one over this displayed range. On narrow screens, swipe each chart horizontally for readable labels.</p></section>
<section id="workflow"><span class="step">What the product adds</span><h2>From a question to an inspectable answer</h2><ol>
<li><b>Specify and review.</b> The analyst supplies authorized data and an IV design. Gemini helps turn the question into proposed column roles, units and comparisons; the analyst checks the plan and confirms it.</li>
<li><b>Check and compute.</b> The workflow checks the supported scope. TabPFN-3.5 supplies predictive models: the treatment distribution given the instrument in Stage 1, and the outcome mean/distribution given treatment and control ranks in Stage 2. TabCF constructs the ranks and integrates predictions to estimate the requested distributions.</li>
<li><b>Explain and trace.</b> Deterministic code derives summaries and evidence. The report connects each displayed number to its saved record and keeps warnings visible. Gemini does not calculate the causal numbers. Ordinary follow-ups reuse completed results without fitting again.</li></ol>
<p>The value is a reviewable path from question to computation to a shareable, inspectable report. The TabCF method predates this entry; this example does not measure agent accuracy gains or user time savings.</p><p class="small">This page is a new presentation derived from an existing real run. Opening it performs none of the live workflow steps and needs no Python, API key, dependency installation, service or internet connection.</p></section>
<section id="technical" class="technical"><details><summary>Technical details · model, run, diagnostics and evidence</summary>
<h3>Original run identity</h3><p><code>{RUN}</code> inside <code>{escaped(archive.name)}</code></p><ul>{''.join(f'<li>{k}: <code>{escaped(bundle[k])}</code></li>' for k in ['run_id','result_bundle_id','specification_id','track','evidence_status'])}</ul>
<p>Model: <b>{escaped(dict(backend['parameters'])['model_path'])}</b> (TabPFN-3.5); client {escaped(dict(backend['package_versions'])['tabpfn-client'])}; expected service package {escaped(dict(backend['parameters'])['expected_service_package_version'])}. Seed: {specification['seed']}. Managed service metadata identifies the version, not locally available checkpoint bytes or a runtime image. This run cannot enter locked Track T evidence.</p>
<h3>Diagnostics and intervention support</h3><p>Both requested interventions have saved support assessments. These are empirical checks, not proof of IV validity or identification. The support X values are in stored natural-log price units.</p><pre>{pretty({'diagnostics':bundle['diagnostics'],'support':bundle['support']})}</pre>
<h3>Full warnings and assumptions</h3><ul>{warnings}{assumptions}</ul><p>Cross-state shopping, state policies and time trends are unresolved. No textbook replication or reliable tax-policy recommendation is established. Quantiles resolved on this run's grid do not remove uncertainty. The PDF remains a grid approximation with potentially omitted tail mass.</p>
<h3>Summary evidence index</h3><p>Rounded presentation values link to unchanged evidence IDs. Raw values, units and original source-artifact references are preserved below. Each SVG curve carries its ordered metric keys and evidence IDs; the embedded distribution records supply its axes.</p><div class="table-scroll"><table><thead><tr><th>Metric key</th><th>Unrounded value</th><th>Units</th><th>Evidence ID</th></tr></thead><tbody>{evidence_rows}</tbody></table></div>
<details id="all-evidence"><summary>Complete original evidence ledger · {len(ledger)} records</summary>{records}</details>
{source_sections}
<details id="provenance"><summary>Bundled data provenance and license note · SOURCE.md</summary><pre>{escaped(provenance)}</pre></details>
<details><summary>Bundled statistical interpretation and transformation recipe · DESIGN.md</summary><pre>{escaped(design)}</pre></details>
<details><summary>Original report.md · preserved historical text</summary><p class="small">The historical image reference is retained as text. The figures above are newly rendered from this run's saved metrics.</p><pre>{escaped(historical_report)}</pre></details>
</details></section><footer><a href="#data">Back to the question</a><p>Offline presentation derivative of a saved real run. Original results, evidence identities and historical reports were not modified. No estimator or model was called to create this page. This page does not establish release readiness.</p></footer>
</main><script>
// Open enclosing disclosures so direct evidence and provenance links work offline.
function revealFragment() {{
 const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
 if (!target) return;
 for (let node = target; node; node = node.parentElement) {{
  if (node.tagName === 'DETAILS') node.open = true;
 }}
 target.scrollIntoView({{block:'start'}});
}}
addEventListener('hashchange', revealFragment);
revealFragment();
</script></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'artifacts/local/agentic-tabcf-submission-v3.zip')
    parser.add_argument('--output', type=Path, default=ROOT / 'submission/reports/cigarette-tabpfn35.html')
    args = parser.parse_args()
    document = render(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding='utf-8')
    print(f'Wrote {args.output} ({len(document.encode("utf-8")):,} bytes); no refit or network calls.')


if __name__ == '__main__':
    main()
