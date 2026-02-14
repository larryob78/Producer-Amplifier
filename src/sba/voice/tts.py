"""Text-to-Speech via ElevenLabs API — uses Laurence's account and chosen voice."""

from __future__ import annotations

import httpx
from pathlib import Path

from sba.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"


async def text_to_speech(
    text: str,
    voice_id: str | None = None,
    model_id: str = "eleven_turbo_v2_5",
    output_path: Path | None = None,
) -> bytes:
    """Convert text to speech using ElevenLabs API.

    Args:
        text: The text to speak.
        voice_id: ElevenLabs voice ID. Defaults to configured voice.
        model_id: ElevenLabs model. Turbo v2.5 for low latency.
        output_path: Optional path to save the audio file.

    Returns:
        Raw audio bytes (mp3 format).
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not set")

    vid = voice_id or ELEVENLABS_VOICE_ID
    if not vid:
        raise ValueError("No voice ID configured. Set ELEVENLABS_VOICE_ID in .env")

    url = f"{ELEVENLABS_API_URL}/text-to-speech/{vid}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True,
                },
            },
            timeout=30.0,
        )
        response.raise_for_status()

    audio_bytes = response.content

    if output_path:
        output_path.write_bytes(audio_bytes)

    return audio_bytes


async def get_available_voices() -> list[dict]:
    """List available voices from ElevenLabs account."""
    if not ELEVENLABS_API_KEY:
        return []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_API_URL}/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10.0,
        )
        response.raise_for_status()

    data = response.json()
    return [
        {
            "voice_id": v["voice_id"],
            "name": v["name"],
            "category": v.get("category", ""),
            "labels": v.get("labels", {}),
        }
        for v in data.get("voices", [])
    ]
