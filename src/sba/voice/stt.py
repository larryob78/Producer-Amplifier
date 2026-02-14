"""Speech-to-Text via OpenAI Whisper API — converts producer voice to text queries."""

from __future__ import annotations

import httpx
from pathlib import Path

from sba.config import OPENAI_API_KEY

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"


async def speech_to_text(
    audio_bytes: bytes,
    language: str = "en",
    filename: str = "audio.webm",
) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            WHISPER_API_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"file": (filename, audio_bytes)},
            data={
                "model": "whisper-1",
                "language": language,
                "response_format": "text",
                "prompt": (
                    "Film production budget discussion. "
                    "Terms: VFX, SFX, ADR, foley, gaffer, best boy, "
                    "key grip, turnaround, forced call, golden time, "
                    "meal penalty, company move, swing gang."
                ),
            },
            timeout=30.0,
        )
        response.raise_for_status()

    return response.text.strip()


async def transcribe_file(audio_path: Path, language: str = "en") -> str:
    audio_bytes = audio_path.read_bytes()
    return await speech_to_text(audio_bytes, language, audio_path.name)
