"""FastAPI application — serves the Napkin Producer Amplifier."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from sba.chat.router import router as chat_router
from sba.config import MASTER_BUDGET_PATH, PROJECT_ROOT
from sba.parsing.pipeline import SUPPORTED_FORMATS

app = FastAPI(
    title="Napkin Producer Amplifier",
    description="AI-powered production intelligence for film producers",
    version="0.4.0",
)

# CORS — allow the NPA UI to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the chat router
app.include_router(chat_router)

# In-memory store for the currently loaded script
_current_script = None
_current_analysis = None
_current_raw_text = None


@app.on_event("startup")
async def startup():
    """Load budget on startup if path is configured."""
    if MASTER_BUDGET_PATH:
        from sba.budget.excel_reader import load_budget
        try:
            load_budget(MASTER_BUDGET_PATH)
            print(f"\u2713 Budget loaded from {MASTER_BUDGET_PATH}")
        except Exception as e:
            print(f"\u2717 Failed to load budget: {e}")


@app.get("/")
async def root():
    """Serve the integrated NPA UI."""
    html_path = PROJECT_ROOT / "script-breakdown-ui.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Napkin Producer Amplifier API", "docs": "/docs"}


@app.get("/npa-integration.js")
async def serve_integration_js():
    """Serve the NPA integration JavaScript."""
    js_path = PROJECT_ROOT / "npa-integration.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    return JSONResponse(status_code=404, content={"error": "npa-integration.js not found"})


# ================================================================
# SCRIPT UPLOAD — accepts any format
# ================================================================

@app.post("/api/script/upload")
async def upload_script(
    file: UploadFile = File(...),
    title: str = Form(""),
):
    """Upload and parse a screenplay in any format.

    Supported: .pdf, .docx, .fdx (Final Draft), .txt, .fountain, .rtf
    Returns the full parsed breakdown as JSON.
    """
    global _current_script

    from sba.parsing.pipeline import parse_script_file

    # Validate file extension
    filename = file.filename or "script.txt"
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Unsupported format: {suffix}",
                "supported": sorted(SUPPORTED_FORMATS),
            },
        )

    # Save to temp file for parsing
    contents = await file.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        parsed = parse_script_file(tmp_path, title=title or "")

        # Convert to serialisable dict
        result = {
            "title": parsed.title,
            "total_pages_estimate": parsed.total_pages_estimate,
            "scene_count": len(parsed.scenes),
            "character_count": len(parsed.all_characters),
            "characters": list(parsed.all_characters.keys()),
            "scenes": [],
        }

        for scene in parsed.scenes:
            s = {
                "scene_number": scene.scene_number,
                "slugline": scene.slugline,
                "int_ext": scene.int_ext,
                "day_night": scene.day_night,
                "location": scene.location,
                "characters": scene.characters,
                "word_count": scene.word_count,
                "vfx_triggers": [
                    {
                        "category": t.category,
                        "keyword": t.matched_keyword,
                        "severity": t.severity,
                        "context": t.context,
                    }
                    for t in scene.vfx_triggers
                ],
            }
            result["scenes"].append(s)

        _current_script = result
        global _current_raw_text
        _current_raw_text = parsed.raw_text
        return result

    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={"error": str(e), "filename": filename},
        )
    finally:
        tmp_path.unlink(missing_ok=True)


@app.get("/api/script/current")
async def get_current_script():
    """Return the currently loaded script data."""
    if _current_script is None:
        return {"error": "No script loaded. Upload one via /api/script/upload"}
    return _current_script


@app.post("/api/script/analyze")
async def analyze_script_endpoint():
    """Run Claude analysis on the currently loaded script.

    Requires a script to be loaded via /api/script/upload first.
    Returns the full BreakdownOutput JSON.
    """
    global _current_analysis

    if _current_raw_text is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No script loaded. Upload one via /api/script/upload first."},
        )

    from sba.llm.generator import analyze_script_staged

    try:
        title = _current_script.get("title", "Untitled") if _current_script else "Untitled"
        result = analyze_script_staged(
            text=_current_raw_text,
            title=title,
        )
        _current_analysis = result
        return result.model_dump(mode="json")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.get("/api/script/formats")
async def supported_formats():
    """Return the list of supported script formats."""
    return {
        "formats": sorted(SUPPORTED_FORMATS),
        "descriptions": {
            ".pdf": "PDF screenplay",
            ".docx": "Microsoft Word document",
            ".fdx": "Final Draft screenplay",
            ".txt": "Plain text",
            ".text": "Plain text",
            ".fountain": "Fountain markup (screenwriting format)",
            ".rtf": "Rich Text Format",
            ".doc": "Legacy Word (best-effort)",
        },
    }


# ================================================================
# HEALTH & BUDGET
# ================================================================

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    from sba.budget.excel_reader import _workbook
    return {
        "status": "ok",
        "budget_loaded": _workbook is not None,
        "script_loaded": _current_script is not None,
        "version": "0.4.0",
    }


@app.get("/api/budget/summary")
async def budget_summary():
    """Get the current budget summary for the budget bar."""
    from sba.budget.excel_reader import get_budget_summary
    try:
        return get_budget_summary()
    except RuntimeError as e:
        return {"error": str(e)}


@app.get("/api/budget/vfx")
async def budget_vfx():
    """Get VFX detail by scene."""
    from sba.budget.excel_reader import get_vfx_detail
    try:
        return get_vfx_detail()
    except RuntimeError as e:
        return {"error": str(e)}


@app.get("/api/budget/account/{code}")
async def budget_account(code: int):
    """Read a specific budget account by Hollywood code (1100-9000)."""
    from sba.budget.excel_reader import read_account
    try:
        return read_account(code)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/budget/update")
async def budget_update(
    account_code: int = Form(...),
    field: str = Form(...),
    value: float = Form(...),
    reason: str = Form("Manual update via NPA"),
):
    """Update a budget account value (writes to Excel with audit trail)."""
    from sba.budget.excel_writer import update_account
    try:
        result = update_account(account_code, field, value, reason)
        return result
    except Exception as e:
        return {"error": str(e)}


# ================================================================
# VOICE
# ================================================================

@app.post("/api/voice/transcribe")
async def voice_transcribe(audio: UploadFile = File(...)):
    """Transcribe voice audio to text via Whisper STT."""
    from sba.config import OPENAI_API_KEY
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set. Required for Whisper STT."}

    try:
        from sba.voice.stt import transcribe_audio
        audio_bytes = await audio.read()
        text = await transcribe_audio(audio_bytes)
        return {"text": text}
    except ImportError:
        return {"error": "Voice module not available. Run: pip install openai"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/voice/speak")
async def voice_speak(text: str = Form(...)):
    """Convert text to speech via ElevenLabs TTS. Returns audio stream."""
    from sba.config import ELEVENLABS_API_KEY
    if not ELEVENLABS_API_KEY:
        return {"error": "ELEVENLABS_API_KEY not set. Required for TTS."}

    try:
        from sba.voice.tts import synthesize_speech
        audio_bytes = await synthesize_speech(text)
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"},
        )
    except ImportError:
        return {"error": "Voice module not available. Run: pip install httpx"}
    except Exception as e:
        return {"error": str(e)}
