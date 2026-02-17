"""Tool definitions for the Producer Copilot — budget read/write, scene lookup, cost calculation."""

from __future__ import annotations

from typing import Any

# Tool definitions in Anthropic's tool-use format
TOOL_DEFINITIONS = [
    {
        "name": "read_budget",
        "description": (
            "Read a budget line item from the master Excel budget. "
            "Returns budget amount, actual spend, variance, and notes for the given account code."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_code": {
                    "type": "string",
                    "description": "The budget account code (e.g., '1100', '2500', '4300')",
                },
            },
            "required": ["account_code"],
        },
    },
    {
        "name": "get_scene",
        "description": (
            "Get the full SBA breakdown for a specific scene. "
            "Returns VFX categories, shot estimates, risk scores, characters, flags, and notes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_number": {
                    "type": "string",
                    "description": "The scene number (e.g., '1', '7', '17')",
                },
            },
            "required": ["scene_number"],
        },
    },
    {
        "name": "calculate_overtime",
        "description": (
            "Calculate overtime cost for crew. "
            "Uses standard industry rates with meal penalty and golden time rules."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "crew_count": {
                    "type": "integer",
                    "description": "Number of crew members affected",
                },
                "hours": {
                    "type": "number",
                    "description": "Number of overtime hours",
                },
                "rate_multiplier": {
                    "type": "number",
                    "description": "Overtime rate multiplier (1.5 for time-and-a-half, 2.0 for double time)",
                    "default": 1.5,
                },
                "base_hourly_rate": {
                    "type": "number",
                    "description": "Average base hourly rate for crew (default: $75)",
                    "default": 75,
                },
            },
            "required": ["crew_count", "hours"],
        },
    },
    {
        "name": "check_schedule_conflict",
        "description": (
            "Check for scheduling conflicts between two scenes. "
            "Looks at shared cast, shared locations, equipment overlaps, and turnaround violations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_a": {
                    "type": "string",
                    "description": "First scene number",
                },
                "scene_b": {
                    "type": "string",
                    "description": "Second scene number",
                },
            },
            "required": ["scene_a", "scene_b"],
        },
    },
    {
        "name": "search_hidden_costs",
        "description": (
            "Search for hidden or non-obvious costs associated with a scenario. "
            "Checks for overtime cascades, permit expirations, insurance triggers, "
            "turnaround violations, meal penalties, and transportation conflicts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "Description of the scenario to analyze for hidden costs",
                },
            },
            "required": ["scenario"],
        },
    },
    {
        "name": "update_budget",
        "description": (
            "Update a budget line item in the master Excel budget. "
            "IMPORTANT: This writes to the production's financial record. "
            "Always confirm with the producer before calling this tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_code": {
                    "type": "string",
                    "description": "The budget account code to update",
                },
                "field": {
                    "type": "string",
                    "enum": ["budget", "actual", "notes"],
                    "description": "Which field to update",
                },
                "value": {
                    "type": ["number", "string"],
                    "description": "The new value",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the change (logged in audit trail)",
                },
            },
            "required": ["account_code", "field", "value", "reason"],
        },
    },
]


# ── Tool execution stubs ──
# In production, these connect to the budget Excel reader/writer
# and the SBA data store. For now, they return structured mock data.


def execute_tool(name: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool by name and return its result."""
    handlers = {
        "read_budget": _read_budget,
        "get_scene": _get_scene,
        "calculate_overtime": _calculate_overtime,
        "check_schedule_conflict": _check_schedule_conflict,
        "search_hidden_costs": _search_hidden_costs,
        "update_budget": _update_budget,
    }

    handler = handlers.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}

    try:
        return handler(**inputs)
    except Exception as e:
        return {"error": str(e)}


def _read_budget(account_code: str) -> dict[str, Any]:
    """Read budget line from Excel. Stub — wire to budget/excel_reader.py."""
    from sba.budget.excel_reader import read_account
    try:
        return read_account(account_code)
    except Exception:
        return {
            "account_code": account_code,
            "status": "not_connected",
            "message": "Excel budget not connected. Load the master budget file first.",
        }


def _get_scene(scene_number: str) -> dict[str, Any]:
    """Get scene data from the currently loaded script."""
    from sba.app import _current_analysis, _current_script

    # Prefer analysis data (rich Claude output) over basic parse
    if _current_analysis is not None:
        for scene in _current_analysis.scenes:
            if scene.scene_id == scene_number:
                return scene.model_dump(mode="json")
        return {"error": f"Scene {scene_number} not found in analysis ({len(_current_analysis.scenes)} scenes loaded)"}

    if _current_script is not None:
        for scene in _current_script.get("scenes", []):
            if str(scene.get("scene_number")) == scene_number:
                return scene
        return {"error": f"Scene {scene_number} not found in parsed script ({len(_current_script.get('scenes', []))} scenes loaded)"}

    return {
        "scene_number": scene_number,
        "status": "not_loaded",
        "message": "No script loaded. Upload a screenplay first.",
    }


def _calculate_overtime(
    crew_count: int,
    hours: float,
    rate_multiplier: float = 1.5,
    base_hourly_rate: float = 75.0,
) -> dict[str, Any]:
    """Calculate overtime costs using industry standard rates."""
    base_cost = crew_count * hours * base_hourly_rate
    overtime_cost = base_cost * rate_multiplier
    meal_penalty = 0

    # Meal penalty if OT > 1 hour without break
    if hours > 1:
        meal_penalty = crew_count * 25  # $25 per person meal penalty

    # Golden time kicks in after 16 hours total
    golden_time_cost = 0
    if hours > 4:
        golden_hours = hours - 4
        golden_time_cost = crew_count * golden_hours * base_hourly_rate * 2.0

    total = overtime_cost + meal_penalty + golden_time_cost

    return {
        "crew_count": crew_count,
        "overtime_hours": hours,
        "rate_multiplier": rate_multiplier,
        "base_hourly_rate": base_hourly_rate,
        "overtime_cost": round(overtime_cost, 2),
        "meal_penalty": round(meal_penalty, 2),
        "golden_time_cost": round(golden_time_cost, 2),
        "total_cost": round(total, 2),
        "breakdown": f"{crew_count} crew x {hours}hrs x ${base_hourly_rate} x {rate_multiplier}x = ${overtime_cost:,.0f}",
    }


def _check_schedule_conflict(scene_a: str, scene_b: str) -> dict[str, Any]:
    """Check scheduling conflicts between scenes. Stub for now."""
    return {
        "scene_a": scene_a,
        "scene_b": scene_b,
        "conflicts": [],
        "message": "Schedule data not loaded. Connect the shooting schedule.",
    }


def _search_hidden_costs(scenario: str) -> dict[str, Any]:
    """Search for hidden costs. Returns common production cost traps."""
    common_triggers = [
        {
            "trigger": "night shoot",
            "costs": [
                "Crew overtime at 1.5x-2x after 12hrs",
                "Generator rental for off-grid locations",
                "Turnaround violation if <10hr gap to next call",
                "Transportation forced call for early morning crew",
                "Night differential for SAG performers",
            ],
        },
        {
            "trigger": "location change",
            "costs": [
                "Company move time (2-4 hours lost productivity)",
                "Transportation fuel and mileage",
                "Advance team for new location prep",
                "Permit transfer or new permit fees",
                "Catering relocation",
            ],
        },
        {
            "trigger": "added vfx",
            "costs": [
                "Artist overtime if delivery date unchanged",
                "Render farm capacity charges",
                "Additional review rounds with director",
                "Color science matching across shots",
                "Potential editorial cascade if shots change",
            ],
        },
        {
            "trigger": "weather delay",
            "costs": [
                "Full crew standby pay",
                "Equipment rental continues",
                "Location hold fee extension",
                "Cast hold day at SAG rates",
                "Schedule compression for remaining scenes",
            ],
        },
    ]

    relevant = []
    scenario_lower = scenario.lower()
    for trigger in common_triggers:
        if trigger["trigger"] in scenario_lower:
            relevant.append(trigger)

    return {
        "scenario": scenario,
        "hidden_cost_triggers": relevant,
        "note": "These are common patterns. The chatbot will reason about your specific scenario.",
    }


def _update_budget(
    account_code: str, field: str, value: Any, reason: str
) -> dict[str, Any]:
    """Update budget in Excel. Stub — wire to budget/excel_writer.py."""
    from sba.budget.excel_writer import update_account
    try:
        return update_account(account_code, field, value, reason)
    except Exception:
        return {
            "account_code": account_code,
            "status": "not_connected",
            "message": "Excel budget not connected for writing.",
        }
