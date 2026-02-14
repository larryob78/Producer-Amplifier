"""FastAPI chat router — WebSocket + REST endpoints for the Producer Copilot."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any

import anthropic
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from sba.config import ANTHROPIC_API_KEY
from sba.chat.model_router import RouteDecision, route_query
from sba.chat.system_prompt import build_system_prompt
from sba.chat.tools import TOOL_DEFINITIONS, execute_tool

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thinking: str | None = None
    data_card: dict[str, Any] | None = None
    model_used: str
    route_reason: str
    cost_estimate_usd: float
    duration_ms: int


# In-memory conversation store (swap for Redis in production)
_conversations: dict[str, list[dict]] = {}


def _get_client() -> anthropic.Anthropic:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Rough cost estimate per query."""
    rates = {
        "claude-opus-4-6": (0.015, 0.075),
        "claude-sonnet-4-5-20250929": (0.003, 0.015),
        "claude-haiku-4-5-20251001": (0.0008, 0.004),
    }
    input_rate, output_rate = rates.get(model, (0.003, 0.015))
    return (input_tokens / 1000 * input_rate) + (output_tokens / 1000 * output_rate)


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest) -> ChatResponse:
    """Send a message to the Producer Copilot and get a response."""
    start = time.time()
    client = _get_client()

    # Route to optimal model
    decision: RouteDecision = route_query(req.message)

    # Build or retrieve conversation history
    conv_id = req.conversation_id or "default"
    if conv_id not in _conversations:
        _conversations[conv_id] = []

    history = _conversations[conv_id]
    history.append({"role": "user", "content": req.message})

    # Build system prompt with SBA + budget context
    system = build_system_prompt()

    # Make the API call
    kwargs: dict[str, Any] = {
        "model": decision.model,
        "max_tokens": decision.max_tokens,
        "temperature": decision.temperature,
        "system": system,
        "messages": history[-20:],  # Keep last 20 messages for context
        "tools": TOOL_DEFINITIONS,
    }

    # Enable extended thinking for Sonnet reasoning tasks
    if decision.use_thinking:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": 4096}

    response = client.messages.create(**kwargs)

    # Handle tool use in a loop (max 3 rounds)
    tool_rounds = 0
    while response.stop_reason == "tool_use" and tool_rounds < 3:
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        history.append({"role": "assistant", "content": response.content})
        history.append({"role": "user", "content": tool_results})

        response = client.messages.create(**kwargs | {"messages": history[-20:]})
        tool_rounds += 1

    # Extract response parts
    reply_text = ""
    thinking_text = None
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            reply_text += block.text

    # Save assistant response to history
    history.append({"role": "assistant", "content": reply_text})

    # Parse any data cards from the response (delimited by data-card markers)
    data_card = _extract_data_card(reply_text)

    duration_ms = int((time.time() - start) * 1000)
    cost = _estimate_cost(
        decision.model,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )

    return ChatResponse(
        reply=reply_text,
        thinking=thinking_text,
        data_card=data_card,
        model_used=decision.model,
        route_reason=decision.reason,
        cost_estimate_usd=cost,
        duration_ms=duration_ms,
    )


@router.websocket("/ws")
async def chat_websocket(ws: WebSocket):
    """WebSocket endpoint for streaming chat responses."""
    await ws.accept()
    client = _get_client()
    conv_id = "ws-default"
    _conversations.setdefault(conv_id, [])

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            query = msg.get("message", "")

            decision = route_query(query)
            _conversations[conv_id].append({"role": "user", "content": query})

            system = build_system_prompt()

            # Send route info
            await ws.send_json({
                "type": "route",
                "model": decision.model,
                "tier": decision.tier.value,
                "reason": decision.reason,
            })

            # Stream the response
            kwargs: dict[str, Any] = {
                "model": decision.model,
                "max_tokens": decision.max_tokens,
                "temperature": decision.temperature,
                "system": system,
                "messages": _conversations[conv_id][-20:],
            }
            if decision.use_thinking:
                kwargs["thinking"] = {"type": "enabled", "budget_tokens": 4096}

            with client.messages.stream(**kwargs) as stream:
                for event in stream:
                    if hasattr(event, "type"):
                        if event.type == "content_block_start":
                            block = event.content_block
                            if block.type == "thinking":
                                await ws.send_json({"type": "thinking_start"})
                            elif block.type == "text":
                                await ws.send_json({"type": "text_start"})
                        elif event.type == "content_block_delta":
                            delta = event.delta
                            if hasattr(delta, "thinking"):
                                await ws.send_json({
                                    "type": "thinking_delta",
                                    "text": delta.thinking,
                                })
                            elif hasattr(delta, "text"):
                                await ws.send_json({
                                    "type": "text_delta",
                                    "text": delta.text,
                                })

            full_response = stream.get_final_message()
            reply = "".join(
                b.text for b in full_response.content if b.type == "text"
            )
            _conversations[conv_id].append({"role": "assistant", "content": reply})

            await ws.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass


def _extract_data_card(text: str) -> dict[str, Any] | None:
    """Extract a JSON data card if the model included one."""
    import re
    match = re.search(r'```data-card\n(.+?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None
