"""JSON validation and repair pipeline for Claude's breakdown output.

Pipeline: direct parse → markdown fence extraction → json_repair → Pydantic validate.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from json_repair import repair_json
from pydantic import ValidationError

from sba.output.schema import BreakdownOutput


@dataclass
class ValidationResult:
    """Result of validating a breakdown JSON string."""

    is_valid: bool
    output: BreakdownOutput | None
    error_message: str = ""
    raw_json: str = ""
    repair_applied: bool = False


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _try_parse_json(text: str) -> tuple[dict | None, str]:
    """Attempt to parse JSON, returning (parsed_dict, error_message)."""
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data, ""
        return None, f"Expected JSON object, got {type(data).__name__}"
    except json.JSONDecodeError as e:
        return None, str(e)


def _try_repair_json(text: str) -> tuple[dict | None, str]:
    """Attempt to repair malformed JSON using json_repair library."""
    try:
        repaired = repair_json(text, return_objects=True)
        if isinstance(repaired, dict):
            return repaired, ""
        return None, f"Repaired JSON is not a dict: {type(repaired).__name__}"
    except Exception as e:
        return None, f"json_repair failed: {e}"


def validate_breakdown_json(raw_text: str) -> ValidationResult:
    """Validate and parse a JSON string into a BreakdownOutput model.

    Attempts multiple strategies:
    1. Direct JSON parse + Pydantic validation
    2. Strip markdown fences, then parse
    3. json_repair library, then Pydantic validation
    """
    stripped = _strip_markdown_fences(raw_text)

    # Attempt 1: Direct parse
    data, parse_error = _try_parse_json(stripped)
    if data is not None:
        try:
            output = BreakdownOutput.model_validate(data)
            return ValidationResult(is_valid=True, output=output, raw_json=stripped)
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                output=None,
                error_message=f"Pydantic validation failed: {e}",
                raw_json=stripped,
            )

    # Attempt 2: json_repair
    repaired_data, repair_error = _try_repair_json(stripped)
    if repaired_data is not None:
        try:
            output = BreakdownOutput.model_validate(repaired_data)
            return ValidationResult(
                is_valid=True,
                output=output,
                raw_json=json.dumps(repaired_data),
                repair_applied=True,
            )
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                output=None,
                error_message=f"Pydantic validation failed after repair: {e}",
                raw_json=json.dumps(repaired_data),
                repair_applied=True,
            )

    # All attempts failed
    return ValidationResult(
        is_valid=False,
        output=None,
        error_message=f"JSON parse failed: {parse_error}. Repair failed: {repair_error}",
        raw_json=raw_text,
    )
