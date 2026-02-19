"""NPA Parallel Analysis v2.1 — chunk-based, no regex splitting."""

from __future__ import annotations
import json, os, re, time, logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import anthropic
from sba.output.schema import (
    BreakdownOutput, Scene, ProjectSummary, GlobalFlags,
    KeyQuestions, HiddenCostItem, VfxCategory,
)

logger = logging.getLogger(__name__)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HAIKU_MODEL = "claude-haiku-4-5-20251001"
MAX_WORKERS = 6
CHUNK_SIZE = 15000
MAX_RETRIES = 2
_client = None

def _get_client():
    global _client
    if _client is None:
        key = API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        _client = anthropic.Anthropic(api_key=key)
    return _client

VFX_CATEGORIES_LIST = ", ".join([c.value for c in VfxCategory])

ANALYSIS_SYSTEM_PROMPT = f"""You are a VFX Pre-Viz Supervisor analyzing a screenplay excerpt.

Find ALL scenes in the text. A new scene starts at each scene heading (INT., EXT., INT./EXT., etc).

For EACH scene found, produce a JSON object with these fields:
- scene_id: string (sequential number)
- slugline: string (the full scene heading line)
- int_ext: "INT" or "EXT" or "INT_EXT"
- day_night: "DAY" or "NIGHT" or "DAWN" or "DUSK" or "UNSPECIFIED"
- scene_summary: string (1-2 sentences)
- characters: [character names]
- vfx_triggers: [specific VFX needs in plain language]
- vfx_categories: [from: {VFX_CATEGORIES_LIST}]
- production_flags: {{stunts: bool, creatures: bool, vehicles: bool, crowds: bool, water: bool, fire_smoke: bool, destruction: bool, weather: bool, complex_lighting: bool, space_or_zero_g: bool, heavy_costume_makeup: bool}}
- vfx_shot_count_estimate: {{min: int, likely: int, max: int}}
- cost_risk_score: integer 1-5 (1=cheap dialogue, 5=massive VFX)
- schedule_risk_score: integer 1-5
- risk_reasons: [strings]
- suggested_capture: [on-set recommendations]
- notes_for_producer: [producer notes]
- uncertainties: [things needing clarification]

RULES:
- Return ONLY a JSON array. No markdown, no explanation, no code fences.
- Find EVERY scene in the text, even short ones.
- If no VFX needed, set cost_risk_score=1, vfx_categories=[].
- Include invisible VFX: wire removal, sky replacement, set extension, cleanup."""

GLOBAL_SYSTEM_PROMPT = """You are a VFX Pre-Viz Supervisor creating a project summary.
Given scene analysis data, produce a JSON object with:
- global_flags: {{overall_vfx_heaviness: "low"|"medium"|"high"|"extreme", likely_virtual_production_fit: "low"|"medium"|"high", top_risk_themes: [strings]}}
- hidden_cost_radar: [{{flag: string, severity: "low"|"medium"|"high", where: [scene IDs], why_it_matters: string, mitigation_ideas: [strings]}}]
- key_questions_for_team: {{for_producer: [strings], for_vfx_supervisor: [strings], for_dp_camera: [strings], for_locations_art_dept: [strings]}}
Return ONLY valid JSON. No markdown."""

def _call_claude(model, system, user_msg, max_tokens=8192):
    client = _get_client()
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = client.messages.create(
                model=model, max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return resp.content[0].text
        except Exception as e:
            logger.warning(f"API attempt {attempt+1} failed: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(2 ** attempt)
    return ""

def _parse_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for pat in [r"\[[\s\S]*\]", r"\{[\s\S]*\}"]:
            m = re.search(pat, text)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    continue
        logger.error(f"JSON parse failed: {text[:300]}")
        return []

def _chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into overlapping chunks, breaking at paragraph boundaries."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at a double newline near the boundary
            break_point = text.rfind("\n\n", start + chunk_size - 2000, end + 500)
            if break_point > start:
                end = break_point
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks

def _analyze_chunk(chunk_text, chunk_num, total_chunks):
    logger.info(f"  -> Chunk {chunk_num}/{total_chunks}: {len(chunk_text)} chars")
    t0 = time.time()
    user_msg = (
        f"This is chunk {chunk_num} of {total_chunks} from a screenplay. "
        f"Find and analyze ALL scenes in this text:\n\n{chunk_text}"
    )
    raw = _call_claude(HAIKU_MODEL, ANALYSIS_SYSTEM_PROMPT, user_msg, max_tokens=16000)
    parsed = _parse_json_response(raw)
    elapsed = time.time() - t0
    count = len(parsed) if isinstance(parsed, list) else 1
    logger.info(f"  OK Chunk {chunk_num}: found {count} scenes in {elapsed:.1f}s")
    if isinstance(parsed, list):
        return parsed
    elif isinstance(parsed, dict) and "scenes" in parsed:
        return parsed["scenes"]
    elif isinstance(parsed, dict):
        return [parsed]
    return []

def _generate_global_summary(scenes, title):
    logger.info("  -> Global summary...")
    t0 = time.time()
    summaries = []
    for s in scenes:
        summaries.append({
            "scene_id": s.scene_id, "slugline": s.slugline,
            "cost_risk_score": s.cost_risk_score,
            "vfx_categories": s.vfx_categories,
            "vfx_triggers": s.vfx_triggers[:3],
        })
    user_msg = f"Project: {title}\nScenes: {len(scenes)}\n\n{json.dumps(summaries, indent=1)}"
    raw = _call_claude(HAIKU_MODEL, GLOBAL_SYSTEM_PROMPT, user_msg, max_tokens=4096)
    parsed = _parse_json_response(raw)
    logger.info(f"  OK Global summary in {time.time()-t0:.1f}s")
    return parsed if isinstance(parsed, dict) else {}

def analyze_script_staged(text, title="Untitled"):
    total_start = time.time()
    logger.info(f"=== NPA v2.1 Parallel Analysis: '{title}' ===")
    logger.info(f"  Text length: {len(text)} chars")

    # Chunk the text instead of regex splitting
    chunks = _chunk_text(text)
    logger.info(f"  Split into {len(chunks)} chunks of ~{CHUNK_SIZE} chars")

    # Fire all chunks in parallel
    all_scene_dicts = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(_analyze_chunk, chunk, i+1, len(chunks)): i
            for i, chunk in enumerate(chunks)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results = future.result()
                all_scene_dicts.extend(results)
            except Exception as e:
                logger.error(f"  FAIL Chunk {idx+1}: {e}")

    # Renumber scenes sequentially and deduplicate
    seen_slugs = set()
    unique_scenes = []
    for sd in all_scene_dicts:
        slug = str(sd.get("slugline", "")).strip().upper()
        summary = str(sd.get("scene_summary", "")).strip()[:50]
        key = f"{slug}|{summary}"
        if key not in seen_slugs:
            seen_slugs.add(key)
            unique_scenes.append(sd)

    # Convert to Scene models with sequential IDs
    scenes = []
    for i, sd in enumerate(unique_scenes):
        sd["scene_id"] = str(i + 1)
        try:
            scenes.append(Scene(**sd))
        except Exception as e:
            logger.warning(f"  Scene parse error: {e}")
            try:
                scenes.append(Scene(
                    scene_id=str(i+1),
                    slugline=str(sd.get("slugline", "")),
                    scene_summary=str(sd.get("scene_summary", "")),
                ))
            except Exception:
                pass

    logger.info(f"  Total: {len(scenes)} unique scenes")

    # Global summary
    global_data = {}
    if scenes:
        try:
            global_data = _generate_global_summary(scenes, title)
        except Exception as e:
            logger.error(f"  Global summary failed: {e}")

    total_elapsed = time.time() - total_start
    logger.info(f"=== Done: {len(scenes)} scenes in {total_elapsed:.1f}s ===")

    return BreakdownOutput(
        project_summary=ProjectSummary(
            project_title=title,
            date_analyzed=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_scene_count=len(scenes),
        ),
        global_flags=GlobalFlags(
            **global_data.get("global_flags", {})
        ) if "global_flags" in global_data else GlobalFlags(),
        scenes=scenes,
        hidden_cost_radar=[
            HiddenCostItem(**item)
            for item in global_data.get("hidden_cost_radar", [])
            if isinstance(item, dict)
        ],
        key_questions_for_team=KeyQuestions(
            **global_data.get("key_questions_for_team", {})
        ) if "key_questions_for_team" in global_data else KeyQuestions(),
    )
