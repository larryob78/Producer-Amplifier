# P1-P4 Vertical Slice Design

**Date:** 2026-02-16
**Approach:** Vertical Slice — wire one complete path end-to-end across all layers

## Objective

Make the full Producer Breakdown Tool workflow functional:
Upload script → Claude analysis → UI display → Chat queries → Export

## Constraints

- No new dependencies
- No new files (modify existing only)
- ~195 lines across 3 files
- Smallest change that completes each layer

## Design

### Step 1: Analyze Endpoint (`app.py`)

Add `POST /api/script/analyze` that takes the uploaded script text and runs
`analyze_script_staged()` from `sba.llm.generator`. Returns the full
`BreakdownOutput` JSON (scenes with VFX categories, risk scores, cost estimates,
hidden cost radar, key questions).

The endpoint uses the in-memory `_current_script` text stored during upload.
If no script is loaded, returns 400.

### Step 2: Frontend Calls Analyze (`script-breakdown-ui.html`)

After `uploadToBackend()` succeeds, automatically call `/api/script/analyze`.
Show status text below the title during analysis. When the analysis response
arrives, pass it to `mapBreakdownToUI()` — the response format matches what
`mapBreakdownToUI` expects (it IS a `BreakdownOutput`).

### Step 3: Wire `_get_scene()` (`chat/tools.py`)

Import `_current_script` from `sba.app` and look up scene by number.
Return the scene dict if found, or "not loaded" message if not.

### Step 4: Implement `_check_schedule_conflict()` (`chat/tools.py`)

Compare two scenes from the loaded script data. Check for:
- Shared characters (cast turnaround risk)
- Same location (no company move needed — positive signal)
- INT vs EXT mismatch (lighting setup change)
- DAY vs NIGHT (turnaround violation risk)

Returns a list of conflicts with severity and description.

### Step 5: Export Endpoints (`app.py`)

- `GET /api/export/csv` — uses existing `sba.output.export_csv` on the current
  analysis data. Returns as file download with `Content-Disposition: attachment`.
- `GET /api/export/html` — uses existing `sba.output.export_html`. Returns
  standalone HTML (user can print-to-PDF from browser).

Both return 400 if no analysis has been run.

### Step 6: Export Buttons (`script-breakdown-ui.html`)

Two buttons in the header area: "Export CSV" and "Export HTML".
Each calls the corresponding endpoint and triggers a browser download.
Buttons are disabled/hidden until an analysis is loaded.

### Step 7: Status + Error Handling (`script-breakdown-ui.html`)

Replace all `alert()` calls with a `showStatus(message, type)` helper that
displays inline text below the title. Types: 'info' (neutral), 'success' (green),
'error' (red). Auto-clears success messages after 5 seconds.

## Files Modified

| File | Changes |
|------|---------|
| `src/sba/app.py` | +analyze endpoint, +export endpoints, store analysis result |
| `src/sba/chat/tools.py` | Wire `_get_scene`, implement `_check_schedule_conflict` |
| `script-breakdown-ui.html` | Call analyze, export buttons, showStatus helper |

## Risks

- Claude API call in `/api/script/analyze` could be slow (30-60s for a full script).
  Mitigation: show status text so user knows it's working.
- Analysis may fail on malformed scripts. Mitigation: return error JSON, show in UI.
- `_current_script` is in-memory and lost on server restart. Acceptable for MVP.

## Acceptance Criteria

1. Upload a .docx → see "Analyzing..." → see fully populated scene breakdown
2. Chat copilot can answer "What VFX does scene 3 need?" using real data
3. Export CSV downloads a file with scene-by-scene breakdown
4. Export HTML downloads a standalone report
5. Errors show inline, not in alert() popups
6. All 75 existing tests still pass
