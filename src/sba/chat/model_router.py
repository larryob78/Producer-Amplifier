"""Intelligent model routing — picks Haiku, Sonnet, or Opus based on query complexity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from sba.config import CLAUDE_MODEL_HAIKU, CLAUDE_MODEL_OPUS, CLAUDE_MODEL_SONNET


class QueryTier(Enum):
    LOOKUP = "lookup"
    REASONING = "reasoning"
    BUDGET_OPS = "budget_ops"


@dataclass
class RouteDecision:
    tier: QueryTier
    model: str
    use_thinking: bool
    max_tokens: int
    temperature: float
    reason: str


# Patterns that indicate heavy budget operations (→ Opus)
BUDGET_OPS_PATTERNS = [
    r"regenerat\w*\s+.*budget",
    r"recalculat\w*",
    r"full\s+cost\s+report",
    r"week.over.week\s+burn",
    r"cash\s*flow\s+projection",
    r"update\s+.*excel",
    r"write\s+.*budget",
    r"reforecast",
    r"compare\s+.*scenarios",
]

# Patterns that indicate simple lookups (→ Haiku)
LOOKUP_PATTERNS = [
    r"^what\s+(is|are)\s+the\s+\w+\s+(for|in|of)\s+scene",
    r"^how\s+many\s+(shots|days|crew)",
    r"^show\s+me\s+scene",
    r"^list\s+(all\s+)?(scenes|characters|locations)",
    r"^what\s+scene\s+(is|has|contains)",
    r"^who\s+(is\s+in|appears)",
    r"^(vfx|budget)\s+(for|of)\s+scene\s+\d+$",
]


def route_query(query: str) -> RouteDecision:
    q = query.lower().strip()

    for pattern in BUDGET_OPS_PATTERNS:
        if re.search(pattern, q):
            return RouteDecision(
                tier=QueryTier.BUDGET_OPS,
                model=CLAUDE_MODEL_OPUS,
                use_thinking=False,
                max_tokens=16384,
                temperature=0.1,
                reason=f"Budget operation detected (matched: {pattern})",
            )

    for pattern in LOOKUP_PATTERNS:
        if re.search(pattern, q):
            return RouteDecision(
                tier=QueryTier.LOOKUP,
                model=CLAUDE_MODEL_HAIKU,
                use_thinking=False,
                max_tokens=2048,
                temperature=0.1,
                reason=f"Simple lookup (matched: {pattern})",
            )

    return RouteDecision(
        tier=QueryTier.REASONING,
        model=CLAUDE_MODEL_SONNET,
        use_thinking=True,
        max_tokens=8192,
        temperature=1.0,
        reason="Reasoning task — using Sonnet with extended thinking",
    )
