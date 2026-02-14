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
/* ================================================================
   PRODUCTION BIBLE — Design System v2
   Warm dark palette - collapsible scenes - search - filters
   ================================================================ */

:root {{
  --bg: #0f0e0d;
  --surface: #171614;
  --surface-2: #1e1d1a;
  --surface-3: #262522;
  --surface-raised: #2d2b27;

  --rule: rgba(255,245,230,0.06);
  --rule-strong: rgba(255,245,230,0.12);
  --rule-accent: rgba(255,245,230,0.18);

  /* Text — improved contrast */
  --text-1: #e8e4de;
  --text-2: #b0a99e;
  --text-3: #948d82;
  --text-4: #5e574d;

  /* Risk spectrum */
  --r1: #5a9e6f; --r2: #8fb065; --r3: #c9a84c; --r4: #cf7a3a; --r5: #c4463a;

  --accent: #c9a84c;
  --accent-dim: rgba(201,168,76,0.10);

  --page-max: 920px;
  --gutter: 48px;

  --serif: 'Source Serif 4', 'Georgia', serif;
  --sans: 'Inter', -apple-system, sans-serif;
  --mono: 'JetBrains Mono', 'SF Mono', monospace;

  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}}

/* ===== RESET ===== */
*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ font-size: 16px; -webkit-font-smoothing: antialiased; scroll-behavior: smooth; }}
body {{
  font-family: var(--sans);
  background: var(--bg);
  color: var(--text-2);
  line-height: 1.6;
  min-height: 100vh;
}}

/* ================================================================
   STICKY NAV
   ================================================================ */
.nav {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 44px;
  background: rgba(15,14,13,0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--rule);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}}
.nav-inner {{
  width: 100%;
  max-width: calc(var(--page-max) + var(--gutter)*2);
  padding: 0 var(--gutter);
  display: flex;
  align-items: center;
  gap: 16px;
}}
.nav-brand {{
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-4);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}}
.nav-brand strong {{ color: var(--text-2); }}
.nav-links {{
  display: flex;
  gap: 20px;
  flex: 1;
}}
.nav-links a {{
  font-size: 12px;
  font-weight: 500;
  color: var(--text-4);
  text-decoration: none;
  letter-spacing: 0.02em;
  transition: color 0.2s;
}}
.nav-links a:hover {{ color: var(--text-2); }}
.nav-links a.active {{ color: var(--accent); }}

/* Search in nav */
.nav-search {{
  position: relative;
  margin-left: auto;
}}
.nav-search input {{
  font-family: var(--mono);
  font-size: 11px;
  width: 180px;
  padding: 4px 10px 4px 28px;
  border-radius: 4px;
  border: 1px solid var(--rule-strong);
  background: var(--surface-2);
  color: var(--text-2);
  outline: none;
  transition: border-color 0.2s, width 0.3s var(--ease);
}}
.nav-search input:focus {{
  border-color: var(--accent);
  width: 220px;
}}
.nav-search input::placeholder {{ color: var(--text-4); }}
.nav-search-icon {{
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: var(--text-4);
  pointer-events: none;
}}
.search-count {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
  white-space: nowrap;
  margin-left: 8px;
  display: none;
}}
.search-count.visible {{ display: inline; }}

/* Jump-to-scene dropdown */
.jump-dropdown {{
  position: relative;
}}
.jump-btn {{
  font-family: var(--mono);
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid var(--rule-strong);
  background: var(--surface-2);
  color: var(--text-3);
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.2s;
}}
.jump-btn:hover {{ border-color: var(--accent); color: var(--text-2); }}
.jump-menu {{
  display: none;
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 6px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  max-height: 400px;
  overflow-y: auto;
  width: 320px;
  z-index: 200;
}}
.jump-menu.open {{ display: block; }}
.jump-item {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 12px;
  color: var(--text-2);
}}
.jump-item:hover {{ background: var(--surface-2); }}
.jump-item-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}}
.jump-item-id {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
  min-width: 28px;
}}
.jump-item-slug {{
  font-family: var(--mono);
  font-size: 11px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

/* Hamburger for mobile */
.nav-hamburger {{
  display: none;
  cursor: pointer;
  width: 20px;
  height: 16px;
  flex-direction: column;
  justify-content: space-between;
}}
.nav-hamburger span {{
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text-3);
  border-radius: 1px;
  transition: transform 0.2s, opacity 0.2s;
}}
.nav-mobile-menu {{
  display: none;
  position: fixed;
  top: 44px;
  left: 0;
  right: 0;
  background: rgba(15,14,13,0.96);
  border-bottom: 1px solid var(--rule);
  padding: 16px var(--gutter);
  z-index: 99;
  flex-direction: column;
  gap: 12px;
}}
.nav-mobile-menu.open {{ display: flex; }}
.nav-mobile-menu a {{
  font-size: 14px;
  font-weight: 500;
  color: var(--text-3);
  text-decoration: none;
  padding: 4px 0;
}}
.nav-mobile-menu a:hover {{ color: var(--text-1); }}

/* View toggle */
.view-toggle {{
  display: flex;
  gap: 2px;
  background: var(--surface-2);
  border: 1px solid var(--rule-strong);
  border-radius: 4px;
  padding: 2px;
}}
.view-toggle button {{
  font-family: var(--mono);
  font-size: 10px;
  padding: 3px 10px;
  border: none;
  border-radius: 3px;
  background: transparent;
  color: var(--text-4);
  cursor: pointer;
  transition: all 0.15s;
}}
.view-toggle button.active {{
  background: var(--surface-raised);
  color: var(--text-1);
}}

/* ================================================================
   PAGE CONTAINER
   ================================================================ */
.page {{
  max-width: var(--page-max);
  margin: 0 auto;
  padding: 44px var(--gutter) 80px;
}}

/* ================================================================
   TITLE BLOCK
   ================================================================ */
.title-block {{
  text-align: center;
  padding: 72px 0 48px;
  border-bottom: 1px solid var(--rule);
}}
.title-block h1 {{
  font-family: var(--serif);
  font-size: 36px;
  font-weight: 800;
  color: var(--text-1);
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin-bottom: 12px;
}}
.title-block .subtitle {{
  font-family: var(--serif);
  font-size: 16px;
  font-weight: 400;
  font-style: italic;
  color: var(--text-3);
  margin-bottom: 24px;
}}
.title-meta {{
  display: flex;
  justify-content: center;
  gap: 32px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-4);
  letter-spacing: 0.03em;
}}
.title-meta span {{ display: flex; align-items: center; gap: 6px; }}
.title-meta .dot {{
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--text-4);
}}

/* ================================================================
   EXECUTIVE SUMMARY
   ================================================================ */
.exec-summary {{
  display: flex;
  justify-content: space-between;
  padding: 28px 0;
  border-bottom: 1px solid var(--rule);
}}
.exec-stat {{ text-align: center; flex: 1; }}
.exec-stat + .exec-stat {{ border-left: 1px solid var(--rule); }}
.exec-val {{
  font-family: var(--mono);
  font-size: 28px;
  font-weight: 600;
  color: var(--text-1);
  line-height: 1;
  letter-spacing: -0.03em;
}}
.exec-label {{
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-4);
  margin-top: 6px;
}}
.exec-note {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
  margin-top: 2px;
}}

/* ================================================================
   SECTION HEADERS
   ================================================================ */
.section {{ padding-top: 48px; }}
.section-header {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--rule);
}}
.section-num {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-4);
  min-width: 20px;
}}
.section-title {{
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.01em;
}}

/* Section toolbar */
.section-toolbar {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}}
.expand-all-btn {{
  font-family: var(--mono);
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid var(--rule-strong);
  background: transparent;
  color: var(--text-3);
  cursor: pointer;
  transition: all 0.15s;
}}
.expand-all-btn:hover {{ border-color: var(--accent); color: var(--text-2); }}

/* Active filter indicator */
.filter-indicator {{
  display: none;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent);
  padding: 6px 12px;
  border: 1px solid var(--accent);
  border-radius: 4px;
  background: var(--accent-dim);
  margin-bottom: 16px;
}}
.filter-indicator.visible {{ display: flex; }}
.filter-clear {{
  cursor: pointer;
  color: var(--text-3);
  font-weight: 600;
  transition: color 0.15s;
}}
.filter-clear:hover {{ color: var(--text-1); }}

/* ================================================================
   RISK TIMELINE — with animations
   ================================================================ */
.risk-timeline {{ padding: 20px 0; margin-bottom: 8px; }}
.timeline-bars {{
  display: flex;
  gap: 2px;
  height: 80px;
  align-items: flex-end;
}}
.t-bar {{
  flex: 1;
  border-radius: 2px 2px 0 0;
  cursor: pointer;
  transition: opacity 0.15s, filter 0.15s, transform 0.15s;
  opacity: 0.75;
  position: relative;
  transform-origin: bottom center;
  animation: growUp 0.6s var(--ease) both;
}}
.t-bar:hover {{ opacity: 1; filter: brightness(1.2); transform: scaleY(1.05); }}
.t-bar.flash {{ animation: barFlash 0.4s ease; }}

@keyframes growUp {{
  from {{ transform: scaleY(0); opacity: 0; }}
  to {{ transform: scaleY(1); opacity: 0.75; }}
}}
@keyframes barFlash {{
  0%,100% {{ filter: brightness(1); }}
  50% {{ filter: brightness(1.8); }}
}}

.t-bar-tip {{
  display: none;
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 11px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  pointer-events: none;
  color: var(--text-2);
}}
.t-bar:hover .t-bar-tip {{ display: block; }}
.t-bar-tip strong {{ color: var(--text-1); }}

.timeline-labels {{ display: flex; gap: 2px; margin-top: 4px; }}
.t-label {{
  flex: 1;
  text-align: center;
  font-family: var(--mono);
  font-size: 9px;
  color: var(--text-4);
}}
.timeline-legend {{
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--rule);
}}
.legend-item {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--text-4);
}}
.legend-dot {{ width: 8px; height: 8px; border-radius: 2px; }}
.risk-scale-header {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
  margin-right: 8px;
}}

/* ================================================================
   SCENE BREAKDOWN SHEET — collapsible
   ================================================================ */
.scene-sheet {{
  border: 1px solid var(--rule);
  border-radius: 2px;
  margin-bottom: 16px;
  background: var(--surface);
  transition: border-color 0.2s, box-shadow 0.2s, opacity 0.3s, transform 0.4s var(--ease);
  border-left: 3px solid var(--rule);
}}
.scene-sheet:hover {{ border-color: var(--rule-strong); box-shadow: 0 2px 12px rgba(0,0,0,0.15); }}
.scene-sheet.hidden {{ display: none; }}
.scene-sheet.dimmed {{ opacity: 0.3; pointer-events: none; }}

/* IntersectionObserver fade-in */
.scene-sheet.animate-in {{
  opacity: 0;
  transform: translateY(12px);
}}
.scene-sheet.animate-in.visible {{
  opacity: 1;
  transform: translateY(0);
}}

/* Scene header — clickable for collapse */
.scene-head {{
  display: flex;
  align-items: center;
  padding: 14px 24px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--rule);
  gap: 12px;
  flex-wrap: wrap;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}}
.scene-head:hover {{ background: var(--surface-3); }}
.scene-number {{
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
  min-width: 36px;
}}
.scene-slug {{
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
  letter-spacing: -0.01em;
  flex: 1;
}}
.scene-meta-pills {{
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}}
.scene-head-shots {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
}}
.chevron {{
  width: 16px;
  height: 16px;
  color: var(--text-4);
  transition: transform 0.25s var(--ease);
  flex-shrink: 0;
}}
.scene-sheet.collapsed .chevron {{ transform: rotate(-90deg); }}
.meta-pill {{
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 2px;
  background: var(--surface-3);
  color: var(--text-3);
  border: 1px solid var(--rule);
}}
.risk-badge {{
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 2px;
  border: 1px solid;
}}

/* Scene body — collapsible */
.scene-content {{
  overflow: hidden;
  max-height: 2000px;
  transition: max-height 0.4s var(--ease), opacity 0.3s;
  opacity: 1;
}}
.scene-sheet.collapsed .scene-content {{
  max-height: 0;
  opacity: 0;
}}

.scene-body {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}}
.scene-col {{ padding: 20px 24px; }}
.scene-col + .scene-col {{ border-left: 1px solid var(--rule); }}

.field {{ margin-bottom: 18px; }}
.field:last-child {{ margin-bottom: 0; }}
.field-label {{
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-4);
  margin-bottom: 6px;
}}
.field-text {{
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.65;
}}

/* Character tags — interactive */
.char-tags {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.char-tag {{
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
  background: var(--surface-3);
  border: 1px solid var(--rule);
  border-radius: 2px;
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.15s;
}}
.char-tag:hover {{ border-color: var(--accent); color: var(--accent); }}
.char-tag.active {{ border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }}

/* VFX category pills — interactive */
.vfx-tags {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.vfx-tag {{
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 2px;
  border: 1px solid;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: all 0.15s;
}}
.vfx-tag:hover {{ filter: brightness(1.3); }}
.vfx-tag.active {{ filter: brightness(1.3); box-shadow: 0 0 6px rgba(201,168,76,0.3); }}
.vfx-dot {{ width: 5px; height: 5px; border-radius: 50%; }}

/* Shot estimate range bar */
.shot-range {{ margin-top: 4px; }}
.shot-bar-bg {{
  width: 100%;
  height: 6px;
  background: var(--surface-3);
  border-radius: 3px;
  position: relative;
}}
.shot-bar-fill {{
  position: absolute;
  height: 100%;
  border-radius: 3px;
  opacity: 0.35;
}}
.shot-bar-mid {{
  position: absolute;
  width: 8px;
  height: 8px;
  top: -1px;
  margin-left: -4px;
  border-radius: 1px;
  background: var(--accent);
  transform: rotate(45deg);
}}
.shot-labels {{
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
}}
.shot-labels .likely {{ color: var(--accent); font-weight: 600; }}

/* Risk reasons list */
.reason-list {{ list-style: none; }}
.reason-list li {{
  padding: 5px 0;
  font-size: 12px;
  color: var(--text-2);
  display: flex;
  gap: 8px;
  line-height: 1.5;
}}
.reason-list li + li {{ border-top: 1px solid var(--rule); }}
.reason-bullet {{
  width: 3px; height: 3px;
  border-radius: 50%;
  background: var(--text-4);
  margin-top: 7px;
  flex-shrink: 0;
}}

/* Capture & notes callouts */
.callout {{
  padding: 10px 14px;
  border-radius: 2px;
  font-size: 12px;
  line-height: 1.6;
  border-left: 2px solid;
}}
.callout-capture {{
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--text-2);
}}
.callout-notes {{
  background: rgba(201,168,76,0.04);
  border-color: var(--r3);
  color: var(--text-3);
  font-style: italic;
}}

/* Scene flags footer */
.scene-flags {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 12px 24px;
  border-top: 1px solid var(--rule);
  background: var(--surface);
}}
.s-flag {{
  font-family: var(--mono);
  font-size: 9px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 2px;
  color: var(--text-4);
  background: transparent;
  border: 1px solid transparent;
}}
.s-flag.on {{
  color: var(--r4);
  background: rgba(207,122,58,0.06);
  border-color: rgba(207,122,58,0.12);
}}

/* ================================================================
   TABLE VIEW
   ================================================================ */
.table-view {{ display: none; overflow-x: auto; }}
.table-view.active {{ display: block; }}
.card-view.hidden {{ display: none; }}

.scene-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}}
.scene-table th {{
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-3);
  text-align: left;
  padding: 10px 12px;
  border-bottom: 2px solid var(--rule-strong);
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
  white-space: nowrap;
}}
.scene-table th:hover {{ color: var(--text-1); }}
.scene-table th.sorted {{ color: var(--accent); }}
.scene-table th .sort-arrow {{
  display: inline-block;
  margin-left: 4px;
  font-size: 8px;
  vertical-align: middle;
}}
.scene-table td {{
  padding: 10px 12px;
  border-bottom: 1px solid var(--rule);
  color: var(--text-2);
  vertical-align: top;
}}
.scene-table tr {{
  cursor: pointer;
  transition: background 0.15s;
}}
.scene-table tr:hover {{ background: var(--surface-2); }}
.scene-table .risk-cell {{
  font-family: var(--mono);
  font-weight: 600;
  text-align: center;
}}

/* ================================================================
   HIDDEN COST ITEMS
   ================================================================ */
.cost-item {{
  display: flex;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid var(--rule);
  align-items: flex-start;
}}
.cost-item:last-child {{ border-bottom: none; }}
.cost-sev-badge {{
  font-family: var(--mono);
  font-size: 16px;
  font-weight: 700;
  width: 36px; height: 36px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid;
}}
.cost-content {{ flex: 1; min-width: 0; }}
.cost-title {{
  font-family: var(--serif);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1);
  margin-bottom: 4px;
}}
.cost-desc {{
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.6;
}}
.cost-affected {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
  margin-top: 6px;
}}
.severity-header {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}}
.severity-header span {{
  display: flex;
  align-items: center;
  gap: 4px;
}}

/* ================================================================
   KEY QUESTIONS
   ================================================================ */
.q-group {{ margin-bottom: 28px; }}
.q-group-label {{
  font-family: var(--serif);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-3);
  margin-bottom: 12px;
  font-style: italic;
}}
.q-item {{
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--rule);
  align-items: flex-start;
}}
.q-item:last-child {{ border-bottom: none; }}
.q-marker {{
  font-family: var(--serif);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-4);
  min-width: 20px;
  line-height: 1.4;
}}
.q-text {{
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.6;
  flex: 1;
}}
.q-priority {{
  font-family: var(--mono);
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 8px;
  border-radius: 2px;
  border: 1px solid;
  flex-shrink: 0;
}}

/* ================================================================
   FOOTER
   ================================================================ */
.doc-footer {{
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--rule);
  text-align: center;
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-4);
}}

/* ================================================================
   BACK TO TOP
   ================================================================ */
.back-to-top {{
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-raised);
  border: 1px solid var(--rule-strong);
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s, transform 0.3s, background 0.15s;
  z-index: 50;
}}
.back-to-top.visible {{ opacity: 1; transform: translateY(0); }}
.back-to-top:hover {{ background: var(--surface-3); color: var(--text-1); }}

/* ================================================================
   RESPONSIVE
   ================================================================ */
@media (max-width: 768px) {{
  :root {{ --gutter: 20px; }}
  .scene-body {{ grid-template-columns: 1fr; }}
  .scene-col + .scene-col {{ border-left: none; border-top: 1px solid var(--rule); }}
  .exec-summary {{ flex-wrap: wrap; }}
  .exec-stat {{ min-width: 45%; }}
  .exec-stat + .exec-stat {{ border-left: none; }}
  .title-block h1 {{ font-size: 26px; }}
  .title-meta {{ flex-wrap: wrap; justify-content: center; gap: 12px; }}

  .nav-links, .nav-search, .jump-dropdown, .view-toggle {{ display: none; }}
  .nav-hamburger {{ display: flex; }}
  .nav-mobile-menu a.active {{ color: var(--accent); }}

  .timeline-bars {{ overflow-x: auto; min-width: 0; }}
  .t-bar {{ min-width: 18px; }}
  .timeline-labels {{ overflow-x: auto; }}
  .t-label {{ min-width: 18px; }}

  .scene-table {{ font-size: 11px; }}
}}

/* ================================================================
   PRINT
   ================================================================ */
@media print {{
  .nav, .back-to-top, .nav-mobile-menu {{ display: none !important; }}
  .page {{ padding-top: 0; }}
  body {{ background: #fff; color: #222; }}
  .scene-sheet {{
    break-inside: avoid;
    border-color: #ddd;
    border-left-width: 1px;
  }}
  .scene-sheet.collapsed .scene-content {{ max-height: none; opacity: 1; }}
  .scene-head {{ background: #f5f5f0; }}
  .title-block h1 {{ color: #111; }}
  .field-text, .cost-desc, .q-text {{ color: #333; }}
  .t-bar-tip {{ display: none !important; }}
  .chevron {{ display: none; }}
  .filter-indicator, .section-toolbar {{ display: none !important; }}
  .search-count {{ display: none !important; }}
  .view-toggle {{ display: none !important; }}
  .table-view {{ display: none !important; }}
  .card-view.hidden {{ display: block !important; }}
  .scene-sheet.dimmed {{ opacity: 1; pointer-events: auto; }}
  .scene-sheet.hidden {{ display: block; }}
}}
</style>
</head>
<body>

<!-- ===== STICKY NAV ===== -->
<nav class="nav">
  <div class="nav-inner">
    <div class="nav-brand"><strong>SBA</strong>&nbsp;Script Breakdown</div>
    <div class="nav-links">
      <a href="#summary" class="active">Summary</a>
      <a href="#scenes">Scenes</a>
      <a href="#costs">Hidden Costs</a>
      <a href="#questions">Questions</a>
    </div>
    <div class="nav-search">
      <svg class="nav-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="searchInput" placeholder="Search scenes..." />
    </div>
    <span class="search-count" id="searchCount"></span>
    <div class="jump-dropdown">
      <button class="jump-btn" id="jumpBtn">Jump to Scene &#9662;</button>
      <div class="jump-menu" id="jumpMenu"></div>
    </div>
    <div class="nav-hamburger" id="hamburger" onclick="toggleMobileMenu()">
      <span></span><span></span><span></span>
    </div>
  </div>
</nav>
<div class="nav-mobile-menu" id="mobileMenu">
  <a href="#summary" onclick="closeMobileMenu()">Summary</a>
  <a href="#scenes" onclick="closeMobileMenu()">Scenes</a>
  <a href="#costs" onclick="closeMobileMenu()">Hidden Costs</a>
  <a href="#questions" onclick="closeMobileMenu()">Questions</a>
</div>

<!-- ===== PAGE ===== -->
<div class="page">

  <!-- TITLE BLOCK -->
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

  <!-- EXECUTIVE SUMMARY -->
  <div class="exec-summary" id="execSummary"></div>

  <!-- RISK TIMELINE -->
  <div class="section" id="risk-timeline-section">
    <div class="section-header">
      <span class="section-num">I.</span>
      <h2 class="section-title">Risk Timeline</h2>
    </div>
    <div class="risk-timeline">
      <div class="timeline-bars" id="timelineBars"></div>
      <div class="timeline-labels" id="timelineLabels"></div>
      <div class="timeline-legend">
        <span class="risk-scale-header">Risk Scale:</span>
        <div class="legend-item"><div class="legend-dot" style="background:var(--r1)"></div>1 Minimal</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--r2)"></div>2 Mild</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--r3)"></div>3 Moderate</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--r4)"></div>4 High</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--r5)"></div>5 Critical</div>
      </div>
    </div>
  </div>

  <!-- SCENE BREAKDOWNS -->
  <div class="section" id="scenes">
    <div class="section-header">
      <span class="section-num">II.</span>
      <h2 class="section-title">Scene Breakdowns</h2>
      <div class="section-toolbar">
        <div class="view-toggle">
          <button class="active" id="cardViewBtn" onclick="setView('card')">Cards</button>
          <button id="tableViewBtn" onclick="setView('table')">Table</button>
        </div>
        <button class="expand-all-btn" id="expandAllBtn" onclick="toggleExpandAll()">Expand All</button>
      </div>
    </div>
    <div class="filter-indicator" id="filterIndicator">
      <span id="filterText"></span>
      <span class="filter-clear" onclick="clearFilter()">&#10005; Clear</span>
    </div>
    <div class="card-view" id="cardView">
      <div id="sceneSheets"></div>
    </div>
    <div class="table-view" id="tableView">
      <table class="scene-table" id="sceneTable">
        <thead>
          <tr>
            <th data-sort="id" onclick="sortTable('id')">ID <span class="sort-arrow"></span></th>
            <th data-sort="slug" onclick="sortTable('slug')">Slugline <span class="sort-arrow"></span></th>
            <th data-sort="cr" onclick="sortTable('cr')">Cost <span class="sort-arrow"></span></th>
            <th data-sort="sr" onclick="sortTable('sr')">Sched <span class="sort-arrow"></span></th>
            <th data-sort="shots" onclick="sortTable('shots')">Shots <span class="sort-arrow"></span></th>
            <th>Categories</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </div>

  <!-- HIDDEN COSTS -->
  <div class="section" id="costs">
    <div class="section-header">
      <span class="section-num">III.</span>
      <h2 class="section-title">Hidden Cost Radar</h2>
    </div>
    <div class="severity-header">
      <span><span class="legend-dot" style="background:var(--r5);display:inline-block;width:8px;height:8px;border-radius:2px;vertical-align:middle"></span> 5 Critical</span>
      <span><span class="legend-dot" style="background:var(--r4);display:inline-block;width:8px;height:8px;border-radius:2px;vertical-align:middle"></span> 4 High</span>
      <span><span class="legend-dot" style="background:var(--r3);display:inline-block;width:8px;height:8px;border-radius:2px;vertical-align:middle"></span> 3 Medium</span>
      <span><span class="legend-dot" style="background:var(--r1);display:inline-block;width:8px;height:8px;border-radius:2px;vertical-align:middle"></span> 1 Low</span>
    </div>
    <div id="costItems"></div>
  </div>

  <!-- KEY QUESTIONS -->
  <div class="section" id="questions">
    <div class="section-header">
      <span class="section-num">IV.</span>
      <h2 class="section-title">Key Questions for the Team</h2>
    </div>
    <div id="questionItems"></div>
  </div>

  <!-- FOOTER -->
  <div class="doc-footer">Generated by SBA &middot; Script Breakdown Assistant &middot; claude-opus-4.6 &middot; {date}</div>

</div>

<!-- Back to top -->
<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 15l-6-6-6 6"/></svg>
</button>

<script>
// ================================================================
// DATA
// ================================================================
const DATA = {data_json};
const RC = ['','var(--r1)','var(--r2)','var(--r3)','var(--r4)','var(--r5)'];
const RH = ['','#5a9e6f','#8fb065','#c9a84c','#cf7a3a','#c4463a'];
const scenes = DATA.scenes || [];
const costs = DATA.hidden_cost_radar || [];
const qs = DATA.key_questions_for_team || {{}};

// ================================================================
// STATE
// ================================================================
let allExpanded = false;
let currentView = 'card';
let activeFilter = null;
let searchQuery = '';
let sortState = {{ col: null, asc: true }};

// ================================================================
// UTILITIES
// ================================================================
function clamp(v,lo,hi){{ return Math.max(lo,Math.min(hi,v)); }}
function esc(s){{ if(typeof s!=='string')return String(s??''); return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }}

// ================================================================
// EXEC SUMMARY
// ================================================================
!function(){{
  const total = scenes.length;
  const vfx = scenes.filter(s => (s.vfx_categories||[]).length > 0).length;
  const shots = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.likely||0), 0);
  const minS = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.min||0), 0);
  const maxS = scenes.reduce((a,s) => a + (s.vfx_shot_count_estimate?.max||0), 0);
  const avgC = total ? (scenes.reduce((a,s) => a + (s.cost_risk_score||1), 0) / total).toFixed(1) : '---';
  const high = scenes.filter(s => (s.cost_risk_score||1) >= 4).length;
  document.getElementById('execSummary').innerHTML = `
    <div class="exec-stat"><div class="exec-val">${{total}}</div><div class="exec-label">Scenes</div><div class="exec-note">${{vfx}} with VFX</div></div>
    <div class="exec-stat"><div class="exec-val">${{shots}}</div><div class="exec-label">Est. VFX Shots</div><div class="exec-note">${{minS}}--${{maxS}} range</div></div>
    <div class="exec-stat"><div class="exec-val" style="color:${{RH[clamp(Math.round(parseFloat(avgC)),1,5)]}}">${{avgC}}</div><div class="exec-label">Avg Cost Risk</div><div class="exec-note">1--5 scale</div></div>
    <div class="exec-stat"><div class="exec-val" style="color:${{RH[5]}}">${{high}}</div><div class="exec-label">High Risk Scenes</div><div class="exec-note">cost &ge; 4</div></div>`;
}}();

// ================================================================
// TIMELINE — clickable bars that scroll to scene
// ================================================================
!function(){{
  const bars = document.getElementById('timelineBars');
  const labels = document.getElementById('timelineLabels');
  bars.innerHTML = scenes.map((s, i) => {{
    const cr = clamp(s.cost_risk_score||1,1,5);
    const pct = 20 + (cr/5)*80;
    const slug = esc(s.slugline||'');
    return `<div class="t-bar" data-scene="${{esc(s.scene_id)}}" style="height:${{pct}}%;background:${{RC[cr]}};animation-delay:${{i*0.04}}s" onclick="jumpToScene('${{esc(s.scene_id)}}')"><div class="t-bar-tip"><strong>Scene ${{esc(s.scene_id)}}</strong><br>${{slug}}<br>Cost ${{cr}}/5 &middot; ${{s.vfx_shot_count_estimate?.likely||0}} shots</div></div>`;
  }}).join('');
  labels.innerHTML = scenes.map(s => `<div class="t-label">${{esc(s.scene_id)}}</div>`).join('');
}}();

// ================================================================
// SCENE CARDS — collapsible, with interactive pills
// ================================================================
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
    const borderColor = RH[cr];

    const chars = (s.characters||[]).length ? `<div class="field"><div class="field-label">Characters</div><div class="char-tags">${{(s.characters||[]).map(c=>`<span class="char-tag" onclick="event.stopPropagation();filterBy('char','${{esc(c)}}')">${{esc(c)}}</span>`).join('')}}</div></div>` : '';

    const cats = (s.vfx_categories||[]).length ? `<div class="field"><div class="field-label">VFX Categories</div><div class="vfx-tags">${{(s.vfx_categories||[]).map(c=>{{
      return `<span class="vfx-tag" onclick="event.stopPropagation();filterBy('cat','${{esc(c)}}')" style="color:var(--text-3);border-color:var(--rule-strong);background:var(--surface-3)"><span class="vfx-dot" style="background:var(--text-3)"></span>${{esc(c)}}</span>`;
    }}).join('')}}</div></div>` : '';

    const reasons = (s.risk_reasons||[]).map(r=>`<li><span class="reason-bullet"></span>${{esc(r)}}</li>`).join('');
    const capture = (s.suggested_capture||[]).map(c=>esc(c)).join('. ');
    const notes = Array.isArray(s.notes_for_producer) ? s.notes_for_producer.map(n=>esc(n)).join(' ') : esc(s.notes_for_producer||'');
    const flags = s.production_flags || {{}};
    const flagHTML = Object.entries(flags).map(([k,v])=>`<span class="s-flag${{v?' on':''}}">${{esc(k.replace(/_/g,' '))}}</span>`).join('');

    return `<div class="scene-sheet collapsed animate-in" id="scene-${{esc(s.scene_id)}}" data-scene="${{esc(s.scene_id)}}" style="border-left-color:${{borderColor}}">
      <div class="scene-head" onclick="toggleScene('${{esc(s.scene_id)}}')">
        <span class="scene-number">${{esc(s.scene_id)}}</span>
        <span class="scene-slug">${{esc(s.slugline)}}</span>
        <div class="scene-meta-pills">
          <span class="meta-pill">${{esc(s.int_ext||'---')}}</span>
          <span class="meta-pill">${{esc(s.day_night||'---')}}</span>
          <span class="meta-pill">${{s.page_count_eighths||0}}/8 pg</span>
          <span class="risk-badge" style="color:${{RC[cr]}};border-color:${{RC[cr]}};background:${{RC[cr]}}0a">COST ${{cr}}/5</span>
          <span class="risk-badge" style="color:${{RC[sr]}};border-color:${{RC[sr]}};background:${{RC[sr]}}0a">SCHED ${{sr}}/5</span>
          <span class="scene-head-shots">${{est.likely}} shots</span>
        </div>
        <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
      </div>
      <div class="scene-content">
        <div class="scene-body">
          <div class="scene-col">
            <div class="field"><div class="field-label">Summary</div><div class="field-text">${{esc(s.scene_summary||'')}}</div></div>
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
      </div>
    </div>`;
  }}).join('');
}}();

// ================================================================
// TABLE VIEW — sortable
// ================================================================
function renderTable(){{
  const tbody = document.getElementById('tableBody');
  const sorted = [...scenes];

  if (sortState.col) {{
    sorted.sort((a,b) => {{
      let va, vb;
      switch(sortState.col) {{
        case 'id': va = parseInt(a.scene_id)||0; vb = parseInt(b.scene_id)||0; break;
        case 'slug': va = a.slugline||''; vb = b.slugline||''; break;
        case 'cr': va = a.cost_risk_score||0; vb = b.cost_risk_score||0; break;
        case 'sr': va = a.schedule_risk_score||0; vb = b.schedule_risk_score||0; break;
        case 'shots': va = a.vfx_shot_count_estimate?.likely||0; vb = b.vfx_shot_count_estimate?.likely||0; break;
        default: return 0;
      }}
      if (va < vb) return sortState.asc ? -1 : 1;
      if (va > vb) return sortState.asc ? 1 : -1;
      return 0;
    }});
  }}

  tbody.innerHTML = sorted.map(s => {{
    const cr = clamp(s.cost_risk_score||1,1,5);
    const sr = clamp(s.schedule_risk_score||1,1,5);
    const shots = s.vfx_shot_count_estimate?.likely||0;
    const catTags = (s.vfx_categories||[]).map(c =>
      `<span class="vfx-tag" style="color:var(--text-3);border-color:var(--rule-strong);background:var(--surface-3);cursor:default;font-size:9px;padding:1px 6px"><span class="vfx-dot" style="background:var(--text-3)"></span>${{esc(c)}}</span>`
    ).join('');
    return `<tr onclick="setView('card');setTimeout(()=>jumpToScene('${{esc(s.scene_id)}}'),100)">
      <td style="font-family:var(--mono);font-weight:600">${{esc(s.scene_id)}}</td>
      <td style="font-family:var(--mono);font-size:11px">${{esc(s.slugline)}}</td>
      <td class="risk-cell" style="color:${{RH[cr]}}">${{cr}}</td>
      <td class="risk-cell" style="color:${{RH[sr]}}">${{sr}}</td>
      <td style="font-family:var(--mono);text-align:center">${{shots}}</td>
      <td><div class="vfx-tags">${{catTags}}</div></td>
    </tr>`;
  }}).join('');
}}

// ================================================================
// COSTS
// ================================================================
!function(){{
  const sevMap = {{critical:RH[5],high:RH[4],medium:RH[3],low:RH[1]}};
  document.getElementById('costItems').innerHTML = costs.map(c => {{
    const col = sevMap[c.severity] || RH[3];
    const sev = {{critical:5,high:4,medium:3,low:1}}[c.severity]||3;
    return `<div class="cost-item"><div class="cost-sev-badge" style="color:${{col}};border-color:${{col}}30;background:${{col}}0a">${{sev}}</div><div class="cost-content"><div class="cost-title">${{esc(c.flag)}}</div><div class="cost-desc">${{esc(c.why_it_matters)}}</div><div class="cost-affected">Affects: ${{(c.where||[]).map(w=>esc(w)).join(', ')}}</div></div></div>`;
  }}).join('');
}}();

// ================================================================
// QUESTIONS
// ================================================================
!function(){{
  const depts = [['for_producer','Producer'],['for_vfx_supervisor','VFX Supervisor'],['for_dp_camera','DP / Camera'],['for_locations_art_dept','Locations / Art Dept']];
  document.getElementById('questionItems').innerHTML = depts.map(([key,label]) => {{
    const items = qs[key] || [];
    if (!items.length) return '';
    return `<div class="q-group"><div class="q-group-label">For the ${{esc(label)}}</div>${{items.map((q,i)=>`<div class="q-item"><span class="q-marker">${{i+1}}.</span><div class="q-text">${{esc(q)}}</div></div>`).join('')}}</div>`;
  }}).join('');
}}();

// ================================================================
// JUMP MENU
// ================================================================
!function(){{
  const menu = document.getElementById('jumpMenu');
  menu.innerHTML = scenes.map(s => {{
    const cr = clamp(s.cost_risk_score||1,1,5);
    const col = RH[cr];
    const slug = esc(s.slugline||'');
    return `<div class="jump-item" onclick="jumpToScene('${{esc(s.scene_id)}}');closeJumpMenu()">
      <span class="jump-item-dot" style="background:${{col}}"></span>
      <span class="jump-item-id">${{esc(s.scene_id)}}</span>
      <span class="jump-item-slug">${{slug}}</span>
    </div>`;
  }}).join('');
}}();

// ================================================================
// INTERACTIONS
// ================================================================
function toggleScene(id){{
  const el = document.getElementById('scene-' + id);
  if (el) el.classList.toggle('collapsed');
  updateExpandBtn();
}}

function toggleExpandAll(){{
  allExpanded = !allExpanded;
  document.querySelectorAll('.scene-sheet').forEach(el => {{
    el.classList.toggle('collapsed', !allExpanded);
  }});
  updateExpandBtn();
}}

function updateExpandBtn(){{
  const total = document.querySelectorAll('.scene-sheet').length;
  const collapsed = document.querySelectorAll('.scene-sheet.collapsed').length;
  allExpanded = collapsed === 0;
  document.getElementById('expandAllBtn').textContent = allExpanded ? 'Collapse All' : 'Expand All';
}}

function jumpToScene(id){{
  const el = document.getElementById('scene-' + id);
  if (!el) return;
  el.classList.remove('collapsed');
  updateExpandBtn();
  el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  const bar = document.querySelector(`.t-bar[data-scene="${{id}}"]`);
  if (bar) {{
    bar.classList.add('flash');
    setTimeout(() => bar.classList.remove('flash'), 400);
  }}
}}

function setView(view){{
  currentView = view;
  document.getElementById('cardViewBtn').classList.toggle('active', view === 'card');
  document.getElementById('tableViewBtn').classList.toggle('active', view === 'table');
  document.getElementById('cardView').classList.toggle('hidden', view !== 'card');
  document.getElementById('tableView').classList.toggle('active', view === 'table');
  if (view === 'table') renderTable();
}}

function sortTable(col){{
  if (sortState.col === col) {{
    sortState.asc = !sortState.asc;
  }} else {{
    sortState.col = col;
    sortState.asc = true;
  }}
  document.querySelectorAll('.scene-table th').forEach(th => {{
    const arrow = th.querySelector('.sort-arrow');
    th.classList.remove('sorted');
    if (arrow) arrow.textContent = '';
    if (th.dataset.sort === col) {{
      th.classList.add('sorted');
      if (arrow) arrow.textContent = sortState.asc ? '\u25b2' : '\u25bc';
    }}
  }});
  renderTable();
}}

// ================================================================
// FILTERING — interactive pills
// ================================================================
function filterBy(type, value){{
  if (activeFilter && activeFilter.type === type && activeFilter.value === value) {{
    clearFilter();
    return;
  }}
  activeFilter = {{ type: type, value: value }};
  applyFilter();
}}

function clearFilter(){{
  activeFilter = null;
  applyFilter();
}}

function applyFilter(){{
  const indicator = document.getElementById('filterIndicator');
  const filterText = document.getElementById('filterText');

  if (!activeFilter) {{
    indicator.classList.remove('visible');
    document.querySelectorAll('.scene-sheet').forEach(el => {{
      el.classList.remove('dimmed');
    }});
    document.querySelectorAll('.char-tag, .vfx-tag').forEach(el => el.classList.remove('active'));
    return;
  }}

  const label = activeFilter.type === 'char'
    ? `Character: ${{activeFilter.value}}`
    : `Category: ${{activeFilter.value}}`;
  filterText.textContent = `Filtering by ${{label}}`;
  indicator.classList.add('visible');

  document.querySelectorAll('.char-tag').forEach(el => {{
    el.classList.toggle('active', activeFilter.type === 'char' && el.textContent.trim() === activeFilter.value);
  }});
  document.querySelectorAll('.vfx-tag').forEach(el => {{
    const catName = el.textContent.trim();
    el.classList.toggle('active', activeFilter.type === 'cat' && activeFilter.value === catName);
  }});

  scenes.forEach(s => {{
    const el = document.getElementById('scene-' + s.scene_id);
    if (!el) return;
    let match = false;
    if (activeFilter.type === 'char') {{
      match = (s.characters||[]).includes(activeFilter.value);
    }} else if (activeFilter.type === 'cat') {{
      match = (s.vfx_categories||[]).includes(activeFilter.value);
    }}
    el.classList.toggle('dimmed', !match);
  }});
}}

// ================================================================
// SEARCH — real-time filtering with counter
// ================================================================
function handleSearch(query){{
  searchQuery = query.toLowerCase().trim();
  const counter = document.getElementById('searchCount');

  if (!searchQuery) {{
    counter.classList.remove('visible');
    document.querySelectorAll('.scene-sheet').forEach(el => el.classList.remove('hidden'));
    return;
  }}

  let visible = 0;
  scenes.forEach(s => {{
    const el = document.getElementById('scene-' + s.scene_id);
    if (!el) return;
    const text = [s.slugline, s.scene_summary, ...(s.characters||[]), ...(s.risk_reasons||[]), ...(s.suggested_capture||[]), ...(Array.isArray(s.notes_for_producer)?s.notes_for_producer:[s.notes_for_producer||'']), ...(s.vfx_categories||[])].join(' ').toLowerCase();
    const match = text.includes(searchQuery);
    el.classList.toggle('hidden', !match);
    if (match) visible++;
  }});

  counter.textContent = `${{visible}} of ${{scenes.length}}`;
  counter.classList.add('visible');
}}

// ================================================================
// NAV — scroll highlight + mobile menu
// ================================================================
function updateNav(){{
  const sections = ['summary','scenes','costs','questions'];
  const y = window.scrollY + 100;
  let active = 'summary';
  for (const id of sections) {{
    const el = document.getElementById(id);
    if (el && el.offsetTop <= y) active = id;
  }}
  document.querySelectorAll('.nav-links a').forEach(a => {{
    a.classList.toggle('active', a.getAttribute('href') === '#' + active);
  }});
  document.querySelectorAll('.nav-mobile-menu a').forEach(a => {{
    a.classList.toggle('active', a.getAttribute('href') === '#' + active);
  }});
}}

function updateBackToTop(){{
  document.getElementById('backToTop').classList.toggle('visible', window.scrollY > 400);
}}

function toggleMobileMenu(){{
  document.getElementById('mobileMenu').classList.toggle('open');
}}
function closeMobileMenu(){{
  document.getElementById('mobileMenu').classList.remove('open');
}}

// Jump menu events
document.getElementById('jumpBtn').addEventListener('click', function(){{
  document.getElementById('jumpMenu').classList.toggle('open');
}});
function closeJumpMenu(){{
  document.getElementById('jumpMenu').classList.remove('open');
}}
document.addEventListener('click', function(e){{
  if (!e.target.closest('.jump-dropdown')) closeJumpMenu();
}});

// Search input
document.getElementById('searchInput').addEventListener('input', function(){{
  handleSearch(this.value);
}});

// Scroll listeners
window.addEventListener('scroll', function(){{
  updateNav();
  updateBackToTop();
}}, {{ passive: true }});

// ================================================================
// INTERSECTION OBSERVER — fade-in animation
// ================================================================
!function(){{
  if (!('IntersectionObserver' in window)) {{
    document.querySelectorAll('.animate-in').forEach(el => el.classList.add('visible'));
    return;
  }}
  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }}
    }});
  }}, {{ threshold: 0.05, rootMargin: '0px 0px -40px 0px' }});
  document.querySelectorAll('.animate-in').forEach(el => observer.observe(el));
}}();

updateExpandBtn();
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
