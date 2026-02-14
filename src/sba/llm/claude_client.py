"""Anthropic API wrapper for Claude interactions."""

from __future__ import annotations

import anthropic

from sba.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS


def get_anthropic_client() -> anthropic.Anthropic:
    """Create an Anthropic client."""
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to .env or set the environment variable."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_claude(
    system_prompt: str,
    user_prompt: str,
    client: anthropic.Anthropic | None = None,
    model: str = CLAUDE_MODEL,
    max_tokens: int | None = None,
    temperature: float = 0.2,
) -> str:
    """Make a single Claude API call and return the text response.

    Args:
        system_prompt: The system prompt.
        user_prompt: The user message.
        client: Optional pre-created Anthropic client.
        model: Model identifier.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature (low for structured output).

    Returns:
        The text content of Claude's response.
    """
    client = client or get_anthropic_client()
    if max_tokens is None:
        max_tokens = MAX_TOKENS

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extract text from response
    text_parts = []
    for block in message.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts)
