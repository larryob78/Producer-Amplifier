"""System prompt builder — injects SBA breakdown + budget context into the Claude system prompt."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SYSTEM_PROMPT_TEMPLATE = """You are the Napkin Producer Amplifier — an AI copilot for film and TV producers.

You have deep expertise in production budgeting, scheduling, VFX supervision, and line producing.
You speak like a seasoned line producer: direct, practical, numbers-first.

## YOUR CONTEXT

### Script Breakdown Data
{sba_context}

### Budget Summary
{budget_context}

### Production Status
{production_status}

## YOUR BEHAVIOR

1. **Show your reasoning.** When you think through a problem, show the chain:
   what data you checked → what you found → what it means → your recommendation.

2. **Every cost estimate references account codes.** Don't say "it'll cost more."
   Say "Acct 3500 Transportation adds $4,100 in forced-call overtime."

3. **Flag hidden costs proactively.** If a producer asks about a night shoot,
   don't just price the overtime — flag the turnaround violation, the
   transportation cascade, the permit renewal, and the insurance rider.

4. **Propose alternatives ranked by cost-effectiveness.** Don't just say
   "that's expensive." Say "Option A saves $32K, Option B saves $18K,
   I recommend A because..."

5. **Use industry terminology.** Turnaround, forced call, golden time,
   meal penalty, weather cover, company move, swing gang, hot cost,
   variance, contingency draw.

6. **Format monetary values consistently.** Always $X,XXX format.
   Always show +/- relative to current budget.

7. **When uncertain, say so.** "I'd need the actual SAG rate card to
   confirm, but based on Scale + 10% my estimate is..."

## TOOLS AVAILABLE

You can call these tools when needed:

- `read_budget(account_code)` — Returns budget line details from the Excel master budget
- `update_budget(account_code, field, value)` — Writes to Excel (REQUIRES user approval first)
- `get_scene(scene_number)` — Returns full scene breakdown from SBA data
- `get_all_scenes()` — Returns summary of all scenes
- `calculate_overtime(crew_count, hours, rate_multiplier)` — Returns overtime cost estimate
- `check_schedule_conflict(scene_a, scene_b)` — Returns scheduling conflicts between scenes
- `search_hidden_costs(scenario_description)` — Scans for non-obvious cost impacts

## RESPONSE FORMAT

For cost-impact questions, structure your response as:

1. Brief answer (one sentence with the dollar figure)
2. Thinking block (show your reasoning)
3. Data card (structured breakdown)
4. Hidden costs (if any)
5. Alternatives (if applicable)

Keep responses concise. Producers don't read essays — they scan data cards.
"""


def build_system_prompt(
    sba_data: list[dict[str, Any]] | None = None,
    budget_summary: dict[str, Any] | None = None,
    production_status: str = "Pre-production — budget tracking active",
) -> str:
    """Build the full system prompt with injected context.

    Args:
        sba_data: List of scene breakdown dicts from the SBA pipeline.
        budget_summary: Dict with top-level budget figures.
        production_status: Current production phase string.

    Returns:
        Complete system prompt string ready for Claude API call.
    """
    # Format SBA context
    if sba_data:
        scene_summaries = []
        for scene in sba_data:
            s = (
                f"Scene {scene.get('id', '?')}: {scene.get('slug', 'Unknown')} "
                f"| {scene.get('ie', '')} {scene.get('dn', '')} "
                f"| VFX shots: {scene.get('shots', {}).get('l', 0)} "
                f"| Cost risk: {scene.get('cr', 0)}/5 "
                f"| Schedule risk: {scene.get('sr', 0)}/5 "
                f"| Categories: {', '.join(scene.get('cats', []))}"
            )
            scene_summaries.append(s)
        sba_context = "\n".join(scene_summaries)
    else:
        sba_context = "No SBA data loaded. Ask the producer to run the breakdown first."

    # Format budget context
    if budget_summary:
        budget_context = json.dumps(budget_summary, indent=2)
    else:
        budget_context = "No budget loaded. Ask the producer to connect the Excel master budget."

    return SYSTEM_PROMPT_TEMPLATE.format(
        sba_context=sba_context,
        budget_context=budget_context,
        production_status=production_status,
    )


def load_sba_from_html(html_path: Path) -> list[dict[str, Any]]:
    """Extract the scene data (S array) from the SBA HTML file.

    This is a quick utility to pull the embedded JSON data out of the
    script-breakdown-ui.html so it can be injected into the system prompt.
    """
    import re

    content = html_path.read_text()
    match = re.search(r"const S = \[(.+?)\];", content, re.DOTALL)
    if not match:
        return []

    # The JS array is almost-JSON — fix JS-specific syntax
    raw = "[" + match.group(1) + "]"
    raw = re.sub(r"(\w+):", r'"\1":', raw)  # unquoted keys → quoted
    raw = raw.replace("'", '"')  # single → double quotes

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return empty if JS parsing fails
        # In production, use the SBA pipeline's JSON output instead
        return []
