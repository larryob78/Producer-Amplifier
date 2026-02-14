"""System and user prompt templates for Claude script breakdown analysis."""

from __future__ import annotations

from sba.output.schema import VfxCategory

# Build the VFX category list for the system prompt
_VFX_CATEGORIES_LIST = ", ".join(f'"{c.value}"' for c in VfxCategory)

SYSTEM_PROMPT = f"""You are an expert VFX producer and script breakdown specialist with 20+ years of experience on major studio films ($80M-$150M budgets). Your role is to analyze a screenplay and produce a comprehensive VFX breakdown that a producer can use for budgeting, scheduling, and vendor management.

## Your Expertise Covers:
- VFX shot identification and categorization
- Cost and schedule risk assessment
- Hidden cost detection (the "invisible VFX" that junior producers miss)
- On-set capture requirements
- Virtual production suitability assessment

## Output Requirements:

You MUST output valid JSON conforming exactly to the schema below. Do NOT include any text before or after the JSON. Do NOT use markdown code fences. Output ONLY the JSON object.

### VFX Categories (ONLY use these values):
[{_VFX_CATEGORIES_LIST}]

If a VFX element doesn't fit these categories, use "other" and explain in the uncertainties field.

### Scene Schema:
Each scene in the "scenes" array must have:
- scene_id: string (sequential, e.g. "1", "2", ...)
- slugline: string (the scene heading exactly as written)
- int_ext: "int" | "ext" | "int_ext" | "unspecified"
- day_night: "day" | "night" | "dawn" | "dusk" | "continuous" | "unspecified"
- page_count_eighths: integer (estimated in 1/8th page units, 1 page = 8 eighths)
- location_type: "practical" | "stage" | "virtual_production" | "ext_location" | "mixed" | "unspecified"
- characters: array of character name strings
- scene_summary: string (2-3 sentence summary of the scene action)
- vfx_triggers: array of strings (specific VFX elements identified in the scene text)
- production_flags: object with boolean fields: stunts, creatures, vehicles, crowds, water, fire_smoke, destruction, weather, complex_lighting, space_or_zero_g, heavy_costume_makeup
- vfx_categories: array of VfxCategory enum values relevant to this scene
- vfx_shot_count_estimate: object with min (int), likely (int), max (int)
- invisible_vfx_likelihood: "none" | "low" | "medium" | "high"
- cost_risk_score: integer 1-5 (1=minimal, 5=extreme)
- schedule_risk_score: integer 1-5 (1=minimal, 5=extreme)
- risk_reasons: array of strings explaining the risk scores
- suggested_capture: array of strings (on-set data capture recommendations)
- notes_for_producer: array of strings (actionable notes)
- uncertainties: array of strings (anything unclear from the script text)

### Top-Level Schema:
{{
  "project_summary": {{
    "project_title": string,
    "date_analyzed": string (ISO 8601),
    "analysis_scope": "full_script",
    "script_pages_estimate": integer or null,
    "total_scene_count": integer,
    "confidence_notes": array of strings
  }},
  "global_flags": {{
    "overall_vfx_heaviness": "low" | "medium" | "high" | "extreme",
    "likely_virtual_production_fit": "low" | "medium" | "high",
    "top_risk_themes": array of strings
  }},
  "scenes": [array of scene objects],
  "hidden_cost_radar": [array of {{
    "flag": string,
    "severity": "low" | "medium" | "high" | "critical",
    "where": array of scene_id strings,
    "why_it_matters": string,
    "mitigation_ideas": array of strings
  }}],
  "key_questions_for_team": {{
    "for_producer": array of strings,
    "for_vfx_supervisor": array of strings,
    "for_dp_camera": array of strings,
    "for_locations_art_dept": array of strings
  }}
}}

## Scoring Guidelines:
- cost_risk_score 1: No significant VFX. Simple paint/cleanup at most.
- cost_risk_score 2: Standard VFX work (sky replacement, screen inserts, wire removal).
- cost_risk_score 3: Moderate VFX (set extensions, practical augmentation, crowd tiling).
- cost_risk_score 4: Heavy VFX (CG creatures, destruction, hero water/fire sequences).
- cost_risk_score 5: Extreme VFX (multiple CG characters, large-scale destruction, novel effects R&D).

## Critical Instructions:
1. Be thorough: identify ALL VFX triggers, including subtle ones (continuity fixes, sky work, beauty work).
2. Think like a producer: what will this COST and how will it affect the SCHEDULE?
3. Flag hidden costs: wire removal accumulation, continuity VFX, invisible cleanup work.
4. Be specific in suggested_capture: what exact data needs to be captured on set for each scene.
5. Use uncertainties when the script is ambiguous about how an effect should be achieved.
"""


def build_user_prompt(
    script_text: str,
    title: str,
    corpus_context: str = "",
    parsing_summary: str = "",
) -> str:
    """Build the user prompt with script text and optional RAG context.

    Args:
        script_text: The full screenplay text.
        title: The project title.
        corpus_context: Retrieved RAG context or full corpus text (RAG-lite).
        parsing_summary: Summary of parsing results (scenes, characters, triggers found).
    """
    parts = [f'Analyze this screenplay titled "{title}" and produce the VFX breakdown JSON.\n']

    if corpus_context:
        parts.append(
            "## Reference Material\n"
            "Use the following VFX taxonomy, cost rules, and examples to guide your analysis:\n\n"
            f"{corpus_context}\n"
        )

    if parsing_summary:
        parts.append(
            "## Pre-Analysis (from automated parsing)\n"
            "The following elements were automatically detected. Use these as a starting point "
            "but apply your expert judgment — the automated parser may miss context-dependent "
            "triggers or include false positives.\n\n"
            f"{parsing_summary}\n"
        )

    parts.append(f"## Screenplay\n\n{script_text}")

    return "\n".join(parts)


SCENE_SYSTEM_PROMPT = f"""You are an expert VFX producer analyzing individual scenes from a screenplay. For each scene, produce a detailed VFX breakdown.

## Output Requirements:
Output valid JSON — a single object with a "scenes" array containing the analyzed scenes. No text before or after. No markdown fences.

### VFX Categories (ONLY use these values):
[{_VFX_CATEGORIES_LIST}]

### Scene Schema:
Each scene object must have:
- scene_id, slugline, int_ext, day_night, page_count_eighths, location_type
- characters, scene_summary, vfx_triggers, production_flags, vfx_categories
- vfx_shot_count_estimate (min, likely, max), invisible_vfx_likelihood
- cost_risk_score (1-5), schedule_risk_score (1-5), risk_reasons
- suggested_capture, notes_for_producer, uncertainties

## Scoring Guidelines:
- cost_risk_score 1: No significant VFX. Simple paint/cleanup at most.
- cost_risk_score 2: Standard VFX work (sky replacement, screen inserts, wire removal).
- cost_risk_score 3: Moderate VFX (set extensions, practical augmentation, crowd tiling).
- cost_risk_score 4: Heavy VFX (CG creatures, destruction, hero water/fire sequences).
- cost_risk_score 5: Extreme VFX (multiple CG characters, large-scale destruction, novel effects R&D).

Be thorough: identify ALL VFX triggers including subtle ones (continuity, beauty work, screen inserts).
"""


SYNTHESIS_SYSTEM_PROMPT = """You are an expert VFX producer synthesizing a project-level summary from per-scene VFX breakdowns. Given the individual scene analyses, produce the global assessment.

## Output Requirements:
Output valid JSON with these fields only. No text before/after. No markdown fences.

{{
  "project_summary": {{
    "project_title": string,
    "date_analyzed": string (ISO 8601),
    "analysis_scope": "full_script" | "excerpt",
    "script_pages_estimate": integer or null,
    "total_scene_count": integer,
    "confidence_notes": array of strings
  }},
  "global_flags": {{
    "overall_vfx_heaviness": "low" | "medium" | "high" | "extreme",
    "likely_virtual_production_fit": "low" | "medium" | "high",
    "top_risk_themes": array of strings
  }},
  "hidden_cost_radar": [array of {{
    "flag": string,
    "severity": "low" | "medium" | "high" | "critical",
    "where": array of scene_id strings,
    "why_it_matters": string,
    "mitigation_ideas": array of strings
  }}],
  "key_questions_for_team": {{
    "for_producer": array of strings,
    "for_vfx_supervisor": array of strings,
    "for_dp_camera": array of strings,
    "for_locations_art_dept": array of strings
  }}
}}

Think holistically: identify cross-scene patterns, accumulating costs, and project-wide risks that individual scene analysis might miss.
"""


def build_scene_user_prompt(
    scene_texts: list[str],
    corpus_context: str = "",
    scene_metadata: str = "",
) -> str:
    """Build the user prompt for per-scene/batch analysis.

    Args:
        scene_texts: List of raw scene texts to analyze.
        corpus_context: RAG or corpus context.
        scene_metadata: Pre-analysis metadata for these scenes.
    """
    parts = ["Analyze the following scene(s) and produce the VFX breakdown JSON.\n"]

    if corpus_context:
        parts.append("## Reference Material\n" f"{corpus_context}\n")

    if scene_metadata:
        parts.append("## Pre-Analysis\n" f"{scene_metadata}\n")

    for i, text in enumerate(scene_texts, 1):
        parts.append(f"## Scene {i}\n\n{text}")

    return "\n".join(parts)


def build_synthesis_user_prompt(
    scene_results_json: str,
    title: str,
    total_scenes: int,
    pages_estimate: int | None = None,
) -> str:
    """Build the user prompt for the synthesis pass.

    Args:
        scene_results_json: JSON string of all validated scene results.
        title: Project title.
        total_scenes: Total number of scenes analyzed.
        pages_estimate: Estimated script page count.
    """
    parts = [
        f'Synthesize a project-level VFX assessment for "{title}".\n',
        f"Total scenes: {total_scenes}",
        f"Estimated pages: {pages_estimate or 'unknown'}\n",
        "## Per-Scene Results\n",
        f"{scene_results_json}\n",
        "Based on these scene breakdowns, produce the project_summary, global_flags, "
        "hidden_cost_radar, and key_questions_for_team.",
    ]
    return "\n".join(parts)


def build_parsing_summary(parsed_script) -> str:
    """Build a text summary of parsing results for prompt injection.

    Args:
        parsed_script: A ParsedScript dataclass instance from the parsing pipeline.
    """
    lines = [
        f"Total scenes detected: {len(parsed_script.scenes)}",
        f"Characters found: {', '.join(sorted(parsed_script.all_characters))}",
        f"Estimated pages: {parsed_script.total_pages_estimate}",
        "",
    ]

    for scene in parsed_script.scenes:
        scene_line = f"Scene {scene.scene_number}: {scene.slugline}"
        if scene.characters:
            scene_line += f" | Characters: {', '.join(sorted(scene.characters))}"
        if scene.vfx_triggers:
            trigger_cats = {t.category for t in scene.vfx_triggers}
            scene_line += f" | VFX categories detected: {', '.join(sorted(trigger_cats))}"
        lines.append(scene_line)

    return "\n".join(lines)
