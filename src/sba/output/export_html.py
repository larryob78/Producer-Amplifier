"""HTML export: generates a self-contained production bible from BreakdownOutput."""

from __future__ import annotations

import json
from pathlib import Path

from sba.output.schema import BreakdownOutput


def _build_html(breakdown: BreakdownOutput) -> str:
    """Generate the full self-contained HTML document."""
    # Serialize data for JS injection
    data = breakdown.model_dump(mode="json")
    data_json = json.dumps(data, indent=2)

    title = data["project_summary"]["project_title"] or "Untitled Project"
    date = data["project_summary"]["date_analyzed"] or "—"
    pages = data["project_summary"]["script_pages_estimate"] or "—"
    scene_count = len(data["scenes"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SBA — {title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;0,800;1,400&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0f0e0d; --surface: #171614; --surface-2: #1e1d1a;
  --surface-3: #262522; --surface-raised: #2d2b27;
  --rule: rgba(255,245,230,0.06); --rule-strong: rgba(255,245,230,0.12);
  --text-1: #e8e4de; --text-2: #b0a99e; --text-3: #7a7368; --text-4: #4d473f;
  --r1: #5a9e6f; --r2: #8fb065; --r3: #c9a84c; --r4: #cf7a3a; --r5: #c4463a;
  --accent: #c9a84c; --accent-dim: rgba(201,168,76,0.10);
  --page-max: 920px; --gutter: 48px;
  --serif: 'Source Serif 4','Georgia',serif;
  --sans: 'Inter',-apple-system,sans-serif;
  --mono: 'JetBrains Mono','SF Mono',monospace;
  --ease: cubic-bezier(0.16,1,0.3,1);
}}
*,*::before,*::after {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ font-size:16px; -webkit-font-smoothing:antialiased; scroll-behavior:smooth; }}
body {{ font-family:var(--sans); background:var(--bg); color:var(--text-2); line-height:1.6; min-height:100vh; }}

.nav {{ position:fixed; top:0; left:0; right:0; height:44px; background:rgba(15,14,13,0.88); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); border-bottom:1px solid var(--rule); display:flex; align-items:center; justify-content:center; z-index:100; }}
.nav-inner {{ width:100%; max-width:calc(var(--page-max)+var(--gutter)*2); padding:0 var(--gutter); display:flex; align-items:center; justify-content:space-between; }}
.nav-brand {{ font-family:var(--mono); font-size:11px; font-weight:500; color:var(--text-4); letter-spacing:0.08em; text-transform:uppercase; }}
.nav-brand strong {{ color:var(--text-2); }}
.nav-links {{ display:flex; gap:24px; }}
.nav-links a {{ font-size:12px; font-weight:500; color:var(--text-4); text-decoration:none; transition:color 0.2s; }}
.nav-links a:hover {{ color:var(--text-2); }}
.nav-links a.active {{ color:var(--accent); }}

.page {{ max-width:var(--page-max); margin:0 auto; padding:44px var(--gutter) 80px; }}
.title-block {{ text-align:center; padding:72px 0 48px; border-bottom:1px solid var(--rule); }}
.title-block h1 {{ font-family:var(--serif); font-size:36px; font-weight:800; color:var(--text-1); letter-spacing:-0.02em; line-height:1.2; margin-bottom:12px; }}
.title-block .subtitle {{ font-family:var(--serif); font-size:16px; font-style:italic; color:var(--text-3); margin-bottom:24px; }}
.title-meta {{ display:flex; justify-content:center; gap:32px; font-family:var(--mono); font-size:11px; color:var(--text-4); }}
.title-meta .dot {{ display:inline-block; width:4px; height:4px; border-radius:50%; background:var(--text-4); vertical-align:middle; }}

.exec-summary {{ display:flex; justify-content:space-between; padding:28px 0; border-bottom:1px solid var(--rule); }}
.exec-stat {{ text-align:center; flex:1; }}
.exec-stat + .exec-stat {{ border-left:1px solid var(--rule); }}
.exec-val {{ font-family:var(--mono); font-size:28px; font-weight:600; color:var(--text-1); line-height:1; }}
.exec-label {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-4); margin-top:6px; }}
.exec-note {{ font-family:var(--mono); font-size:10px; color:var(--text-4); margin-top:2px; }}

.section {{ padding-top:48px; }}
.section-header {{ display:flex; align-items:baseline; gap:12px; margin-bottom:24px; padding-bottom:12px; border-bottom:1px solid var(--rule); }}
.section-num {{ font-family:var(--mono); font-size:11px; color:var(--text-4); }}
.section-title {{ font-family:var(--serif); font-size:22px; font-weight:700; color:var(--text-1); }}

.risk-timeline {{ padding:20px 0; }}
.timeline-bars {{ display:flex; gap:2px; height:80px; align-items:flex-end; }}
.t-bar {{ flex:1; border-radius:2px 2px 0 0; opacity:0.75; cursor:pointer; transition:opacity 0.15s; position:relative; }}
.t-bar:hover {{ opacity:1; filter:brightness(1.2); }}
.t-bar-tip {{ display:none; position:absolute; bottom:calc(100%+8px); left:50%; transform:translateX(-50%); background:var(--surface); border:1px solid var(--rule-strong); border-radius:6px; padding:8px 12px; font-size:11px; white-space:nowrap; z-index:10; box-shadow:0 8px 30px rgba(0,0,0,0.5); color:var(--text-2); pointer-events:none; }}
.t-bar:hover .t-bar-tip {{ display:block; }}
.t-bar-tip strong {{ color:var(--text-1); }}
.timeline-labels {{ display:flex; gap:2px; margin-top:4px; }}
.t-label {{ flex:1; text-align:center; font-family:var(--mono); font-size:9px; color:var(--text-4); }}
.timeline-legend {{ display:flex; justify-content:center; gap:20px; margin-top:12px; padding-top:12px; border-top:1px solid var(--rule); }}
.legend-item {{ display:flex; align-items:center; gap:6px; font-size:10px; color:var(--text-4); }}
.legend-dot {{ width:8px; height:8px; border-radius:2px; }}

.scene-sheet {{ border:1px solid var(--rule); border-radius:2px; margin-bottom:24px; background:var(--surface); transition:border-color 0.2s; }}
.scene-sheet:hover {{ border-color:var(--rule-strong); }}
.scene-head {{ display:flex; align-items:center; padding:14px 24px; background:var(--surface-2); border-bottom:1px solid var(--rule); gap:16px; flex-wrap:wrap; }}
.scene-number {{ font-family:var(--mono); font-size:13px; font-weight:600; color:var(--text-1); min-width:36px; }}
.scene-slug {{ font-family:var(--mono); font-size:13px; font-weight:600; color:var(--text-1); flex:1; }}
.scene-meta-pills {{ display:flex; gap:8px; align-items:center; }}
.meta-pill {{ font-family:var(--mono); font-size:10px; font-weight:500; padding:2px 8px; border-radius:2px; background:var(--surface-3); color:var(--text-3); border:1px solid var(--rule); }}
.risk-badge {{ font-family:var(--mono); font-size:10px; font-weight:600; padding:2px 8px; border-radius:2px; border:1px solid; }}

.scene-body {{ display:grid; grid-template-columns:1fr 1fr; }}
.scene-col {{ padding:20px 24px; }}
.scene-col + .scene-col {{ border-left:1px solid var(--rule); }}
.field {{ margin-bottom:18px; }}
.field:last-child {{ margin-bottom:0; }}
.field-label {{ font-size:9px; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:var(--text-4); margin-bottom:6px; }}
.field-text {{ font-size:13px; color:var(--text-2); line-height:1.65; }}

.char-tags {{ display:flex; flex-wrap:wrap; gap:4px; }}
.char-tag {{ font-family:var(--mono); font-size:10px; font-weight:500; padding:2px 8px; background:var(--surface-3); border:1px solid var(--rule); border-radius:2px; color:var(--text-2); }}

.vfx-tags {{ display:flex; flex-wrap:wrap; gap:4px; }}
.vfx-tag {{ font-size:10px; font-weight:600; padding:2px 8px; border-radius:2px; border:1px solid; display:flex; align-items:center; gap:5px; }}
.vfx-dot {{ width:5px; height:5px; border-radius:50%; }}

.shot-range {{ margin-top:4px; }}
.shot-bar-bg {{ width:100%; height:4px; background:var(--surface-3); border-radius:2px; position:relative; }}
.shot-bar-fill {{ position:absolute; height:100%; border-radius:2px; opacity:0.35; }}
.shot-bar-mid {{ position:absolute; width:2px; height:8px; top:-2px; border-radius:1px; background:var(--accent); }}
.shot-labels {{ display:flex; justify-content:space-between; margin-top:4px; font-family:var(--mono); font-size:10px; color:var(--text-4); }}
.shot-labels .likely {{ color:var(--accent); font-weight:600; }}

.reason-list {{ list-style:none; }}
.reason-list li {{ padding:5px 0; font-size:12px; color:var(--text-2); display:flex; gap:8px; line-height:1.5; }}
.reason-list li + li {{ border-top:1px solid var(--rule); }}
.reason-bullet {{ width:3px; height:3px; border-radius:50%; background:var(--text-4); margin-top:7px; flex-shrink:0; }}

.callout {{ padding:10px 14px; border-radius:2px; font-size:12px; line-height:1.6; border-left:2px solid; }}
.callout-capture {{ background:var(--accent-dim); border-color:var(--accent); color:var(--text-2); }}
.callout-notes {{ background:rgba(201,168,76,0.04); border-color:var(--r3); color:var(--text-3); font-style:italic; }}

.scene-flags {{ display:flex; flex-wrap:wrap; gap:4px; padding:12px 24px; border-top:1px solid var(--rule); }}
.s-flag {{ font-family:var(--mono); font-size:9px; font-weight:500; padding:2px 6px; border-radius:2px; color:var(--text-4); border:1px solid transparent; }}
.s-flag.on {{ color:var(--r4); background:rgba(207,122,58,0.06); border-color:rgba(207,122,58,0.12); }}

.cost-item {{ display:flex; gap:16px; padding:20px 0; border-bottom:1px solid var(--rule); align-items:flex-start; }}
.cost-item:last-child {{ border-bottom:none; }}
.cost-sev-badge {{ font-family:var(--mono); font-size:16px; font-weight:700; width:36px; height:36px; border-radius:4px; display:flex; align-items:center; justify-content:center; flex-shrink:0; border:1px solid; }}
.cost-content {{ flex:1; }}
.cost-title {{ font-family:var(--serif); font-size:15px; font-weight:600; color:var(--text-1); margin-bottom:4px; }}
.cost-desc {{ font-size:13px; color:var(--text-2); line-height:1.6; }}
.cost-affected {{ font-family:var(--mono); font-size:10px; color:var(--text-4); margin-top:6px; }}

.q-group {{ margin-bottom:28px; }}
.q-group-label {{ font-family:var(--serif); font-size:14px; font-weight:600; color:var(--text-3); margin-bottom:12px; font-style:italic; }}
.q-item {{ display:flex; gap:14px; padding:14px 0; border-bottom:1px solid var(--rule); align-items:flex-start; }}
.q-item:last-child {{ border-bottom:none; }}
.q-marker {{ font-family:var(--serif); font-size:16px; font-weight:700; color:var(--text-4); min-width:20px; }}
.q-text {{ font-size:13px; color:var(--text-2); line-height:1.6; flex:1; }}
.q-priority {{ font-family:var(--mono); font-size:9px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; padding:2px 8px; border-radius:2px; border:1px solid; flex-shrink:0; }}

.doc-footer {{ margin-top:48px; padding-top:24px; border-top:1px solid var(--rule); text-align:center; font-family:var(--mono); font-size:10px; color:var(--text-4); }}

@media (max-width:768px) {{
  :root {{ --gutter:20px; }}
  .scene-body {{ grid-template-columns:1fr; }}
  .scene-col + .scene-col {{ border-left:none; border-top:1px solid var(--rule); }}
  .exec-summary {{ flex-wrap:wrap; }}
  .exec-stat {{ min-width:45%; }}
  .title-block h1 {{ font-size:26px; }}
}}
@media print {{
  .nav {{ display:none; }}
  .page {{ padding-top:0; }}
  body {{ background:#fff; color:#222; }}
  .scene-sheet {{ break-inside:avoid; border-color:#ddd; }}
  .scene-head {{ background:#f5f5f0; }}
  .title-block h1 {{ color:#111; }}
  .field-text,.cost-desc,.q-text {{ color:#333; }}
}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <div class="nav-brand"><strong>SBA</strong>&nbsp;Script Breakdown</div>
    <div class="nav-links">
      <a href="#summary" class="active">Summary</a>
      <a href="#scenes">Scenes</a>
      <a href="#costs">Hidden Costs</a>
      <a href="#questions">Questions</a>
    </div>
  </div>
</nav>
<div class="page">
  <div class="title-block" id="summary">
    <h1>{title}</h1>
    <div class="subtitle">VFX Breakdown &amp; Production Risk Assessment</div>
    <div class="title-meta">
      <span>{date}</span>
      <span><span class="dot"></span></span>
      <span>{scene_count} scenes</span>
      <span><span class="dot"></span></span>
      <span>~{pages} est. pages</span>
      <span><span class="dot"></span></span>
      <span>claude-opus-4.6</span>
    </div>
  </div>
  <div class="exec-summary" id="execSummary"></div>
  <div class="section"><div class="section-header"><span class="section-num">I.</span><h2 class="section-title">Risk Timeline</h2></div><div class="risk-timeline"><div class="timeline-bars" id="timelineBars"></div><div class="timeline-labels" id="timelineLabels"></div><div class="timeline-legend"><div class="legend-item"><div class="legend-dot" style="background:var(--r1)"></div>Minimal</div><div class="legend-item"><div class="legend-dot" style="background:var(--r2)"></div>Mild</div><div class="legend-item"><div class="legend-dot" style="background:var(--r3)"></div>Moderate</div><div class="legend-item"><div class="legend-dot" style="background:var(--r4)"></div>High</div><div class="legend-item"><div class="legend-dot" style="background:var(--r5)"></div>Critical</div></div></div></div>
  <div class="section" id="scenes"><div class="section-header"><span class="section-num">II.</span><h2 class="section-title">Scene Breakdowns</h2></div><div id="sceneSheets"></div></div>
  <div class="section" id="costs"><div class="section-header"><span class="section-num">III.</span><h2 class="section-title">Hidden Cost Radar</h2></div><div id="costItems"></div></div>
  <div class="section" id="questions"><div class="section-header"><span class="section-num">IV.</span><h2 class="section-title">Key Questions for the Team</h2></div><div id="questionItems"></div></div>
  <div class="doc-footer">Generated by SBA · Script Breakdown Assistant · claude-opus-4.6 · {date}</div>
</div>
<script>
const DATA = {data_json};
const RC = ['','var(--r1)','var(--r2)','var(--r3)','var(--r4)','var(--r5)'];
const RH = ['','#5a9e6f','#8fb065','#c9a84c','#cf7a3a','#c4463a'];
const scenes = DATA.scenes || [];
const costs = DATA.hidden_cost_radar || [];
const qs = DATA.key_questions_for_team || {{}};

function clamp(v,lo,hi){{ return Math.max(lo,Math.min(hi,v)); }}

// Exec summary
!function(){{
  const total = scenes.length;
  const vfx = scenes.filter(s => (s.vfx_categories||[]).length > 0).length;
  const shots = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.likely||0), 0);
  const minS = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.min||0), 0);
  const maxS = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.max||0), 0);
  const avgC = total ? (scenes.reduce((a,s) => a + (s.cost_risk_score||1), 0) / total).toFixed(1) : '—';
  const high = scenes.filter(s => (s.cost_risk_score||1) >= 4).length;
  document.getElementById('execSummary').innerHTML = `
    <div class="exec-stat"><div class="exec-val">${{total}}</div><div class="exec-label">Scenes</div><div class="exec-note">${{vfx}} with VFX</div></div>
    <div class="exec-stat"><div class="exec-val">${{shots}}</div><div class="exec-label">Est. VFX Shots</div><div class="exec-note">${{minS}}–${{maxS}} range</div></div>
    <div class="exec-stat"><div class="exec-val" style="color:${{RH[clamp(Math.round(parseFloat(avgC)),1,5)]}}">${{avgC}}</div><div class="exec-label">Avg Cost Risk</div><div class="exec-note">1–5 scale</div></div>
    <div class="exec-stat"><div class="exec-val" style="color:${{RH[5]}}">${{high}}</div><div class="exec-label">High Risk</div><div class="exec-note">cost ≥ 4</div></div>`;
}}();

// Timeline
!function(){{
  const bars = document.getElementById('timelineBars');
  const labels = document.getElementById('timelineLabels');
  bars.innerHTML = scenes.map(s => {{
    const cr = clamp(s.cost_risk_score||1,1,5);
    const pct = 20 + (cr/5)*80;
    return `<div class="t-bar" style="height:${{pct}}%;background:${{RC[cr]}}"><div class="t-bar-tip"><strong>Scene ${{s.scene_id}}</strong><br>${{s.slugline}}<br>Cost ${{cr}}/5 · ${{s.vfx_shot_count_estimate?.likely||0}} shots</div></div>`;
  }}).join('');
  labels.innerHTML = scenes.map(s => `<div class="t-label">${{s.scene_id}}</div>`).join('');
}}();

// Scenes
!function(){{
  const el = document.getElementById('sceneSheets');
  const maxS = Math.max(...scenes.map(s => s.vfx_shot_count_estimate?.max||1), 1);
  el.innerHTML = scenes.map(s => {{
    const cr = clamp(s.cost_risk_score||1,1,5);
    const sr = clamp(s.schedule_risk_score||1,1,5);
    const est = s.vfx_shot_count_estimate || {{min:0,likely:0,max:0}};
    const rangeL = (est.min/maxS)*100;
    const rangeW = ((est.max-est.min)/maxS)*100;
    const likelyP = (est.likely/maxS)*100;
    const chars = (s.characters||[]).length ? `<div class="field"><div class="field-label">Characters</div><div class="char-tags">${{(s.characters||[]).map(c=>`<span class="char-tag">${{c}}</span>`).join('')}}</div></div>` : '';
    const cats = (s.vfx_categories||[]).length ? `<div class="field"><div class="field-label">VFX Categories</div><div class="vfx-tags">${{(s.vfx_categories||[]).map(c=>`<span class="vfx-tag" style="color:var(--text-3);border-color:var(--rule-strong);background:var(--surface-3)"><span class="vfx-dot" style="background:var(--text-3)"></span>${{c}}</span>`).join('')}}</div></div>` : '';
    const reasons = (s.risk_reasons||[]).map(r=>`<li><span class="reason-bullet"></span>${{r}}</li>`).join('');
    const capture = (s.suggested_capture||[]).join('. ');
    const notes = Array.isArray(s.notes_for_producer) ? s.notes_for_producer.join(' ') : (s.notes_for_producer||'');
    const flags = s.production_flags || {{}};
    const flagHTML = Object.entries(flags).map(([k,v])=>`<span class="s-flag${{v?' on':''}}">${{k.replace(/_/g,' ')}}</span>`).join('');
    return `<div class="scene-sheet" id="scene-${{s.scene_id}}">
      <div class="scene-head">
        <span class="scene-number">${{s.scene_id}}</span>
        <span class="scene-slug">${{s.slugline}}</span>
        <div class="scene-meta-pills">
          <span class="meta-pill">${{s.int_ext||'—'}}</span>
          <span class="meta-pill">${{s.day_night||'—'}}</span>
          <span class="meta-pill">${{s.page_count_eighths||0}}/8 pg</span>
          <span class="risk-badge" style="color:${{RC[cr]}};border-color:${{RC[cr]}};background:${{RC[cr]}}0a">COST ${{cr}}/5</span>
          <span class="risk-badge" style="color:${{RC[sr]}};border-color:${{RC[sr]}};background:${{RC[sr]}}0a">SCHED ${{sr}}/5</span>
        </div>
      </div>
      <div class="scene-body">
        <div class="scene-col">
          <div class="field"><div class="field-label">Summary</div><div class="field-text">${{s.scene_summary||''}}</div></div>
          ${{chars}}
          ${{cats}}
          <div class="field"><div class="field-label">VFX Shot Estimate</div><div class="shot-range"><div class="shot-bar-bg"><div class="shot-bar-fill" style="left:${{rangeL}}%;width:${{rangeW}}%;background:${{RC[cr]}}"></div><div class="shot-bar-mid" style="left:${{likelyP}}%"></div></div><div class="shot-labels"><span>${{est.min}}</span><span class="likely">${{est.likely}} likely</span><span>${{est.max}}</span></div></div></div>
        </div>
        <div class="scene-col">
          <div class="field"><div class="field-label">Risk Reasons</div><ul class="reason-list">${{reasons}}</ul></div>
          ${{capture ? `<div class="field"><div class="field-label">Suggested Capture</div><div class="callout callout-capture">${{capture}}</div></div>` : ''}}
          ${{notes ? `<div class="field"><div class="field-label">Notes for Producer</div><div class="callout callout-notes">${{notes}}</div></div>` : ''}}
        </div>
      </div>
      ${{flagHTML ? `<div class="scene-flags">${{flagHTML}}</div>` : ''}}
    </div>`;
  }}).join('');
}}();

// Costs
!function(){{
  const sevMap = {{critical:RH[5],high:RH[4],medium:RH[3],low:RH[1]}};
  document.getElementById('costItems').innerHTML = costs.map(c => {{
    const col = sevMap[c.severity] || RH[3];
    const sev = {{critical:5,high:4,medium:3,low:1}}[c.severity]||3;
    return `<div class="cost-item"><div class="cost-sev-badge" style="color:${{col}};border-color:${{col}}30;background:${{col}}0a">${{sev}}</div><div class="cost-content"><div class="cost-title">${{c.flag}}</div><div class="cost-desc">${{c.why_it_matters}}</div><div class="cost-affected">Affects: ${{(c.where||[]).join(', ')}}</div></div></div>`;
  }}).join('');
}}();

// Questions
!function(){{
  const depts = [['for_producer','Producer'],['for_vfx_supervisor','VFX Supervisor'],['for_dp_camera','DP / Camera'],['for_locations_art_dept','Locations / Art Dept']];
  document.getElementById('questionItems').innerHTML = depts.map(([key,label]) => {{
    const items = qs[key] || [];
    if (!items.length) return '';
    return `<div class="q-group"><div class="q-group-label">For the ${{label}}</div>${{items.map((q,i)=>`<div class="q-item"><span class="q-marker">${{i+1}}.</span><div class="q-text">${{q}}</div></div>`).join('')}}</div>`;
  }}).join('');
}}();

// Nav highlight
window.addEventListener('scroll',function(){{
  const ids=['summary','scenes','costs','questions'];
  const y=window.scrollY+100;
  let active='summary';
  for(const id of ids){{ const el=document.getElementById(id); if(el&&el.offsetTop<=y)active=id; }}
  document.querySelectorAll('.nav-links a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+active));
}},{{passive:true}});
</script>
</body>
</html>"""


def export_html(breakdown: BreakdownOutput, output_path: Path) -> Path:
    """Export breakdown as a self-contained HTML production bible.

    Returns the path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _build_html(breakdown)
    output_path.write_text(html, encoding="utf-8")
    return output_path
