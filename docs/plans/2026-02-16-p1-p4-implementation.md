# P1-P4 Vertical Slice Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire the full Producer Breakdown Tool end-to-end: upload → Claude analysis → UI display → chat queries → export.

**Architecture:** The backend already has `analyze_script_staged()` which calls Claude per-scene-batch and returns validated `BreakdownOutput`. The HTML export already renders a full production bible from `BreakdownOutput`. We wire these together via 2 new API endpoints, update the frontend upload flow, implement 2 stubbed chat tools, add 2 export endpoints, and replace `alert()` with inline status.

**Tech Stack:** Python 3.13, FastAPI, Anthropic Claude API, vanilla JS frontend

---

### Task 1: Add `/api/script/analyze` endpoint + store analysis result

**Files:**
- Modify: `src/sba/app.py:36` (add `_current_analysis` store)
- Modify: `src/sba/app.py:148-150` (add analyze endpoint after upload endpoint)

**Step 1: Add the in-memory analysis store and raw text store**

In `src/sba/app.py`, after line 36 (`_current_script = None`), add:

```python
_current_analysis = None
_current_raw_text = None
```

**Step 2: Store raw text during upload**

In the `upload_script` function, after `_current_script = result` (line 141), add:

```python
_current_raw_text = parsed.raw_text
```

Note: `parsed` is the `ParsedScript` object already in scope at that point.

**Step 3: Add the analyze endpoint**

After the `/api/script/current` endpoint (after line 158), add:

```python
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
```

**Step 4: Verify server starts**

```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
python3 -c "from sba.app import app; print('App imports OK')"
```

Expected: `App imports OK`

**Step 5: Commit**

```bash
git add src/sba/app.py
git commit -m "feat: add /api/script/analyze endpoint for Claude analysis"
```

---

### Task 2: Wire frontend to call analyze after upload

**Files:**
- Modify: `script-breakdown-ui.html` (the `handleScriptFile` function and add `showStatus` helper)

**Step 1: Add `showStatus()` helper**

Find the line `function handleScriptFile(file) {` and add BEFORE it:

```javascript
function showStatus(message, type) {
  var el = document.getElementById('statusLine');
  if (!el) {
    el = document.createElement('div');
    el.id = 'statusLine';
    el.style.cssText = 'text-align:center;font-family:var(--mono);font-size:12px;padding:8px 0;';
    var title = document.querySelector('.title-block');
    if (title) title.appendChild(el);
  }
  var colors = { info: 'var(--text-3)', success: 'var(--accent)', error: '#c4463a' };
  el.style.color = colors[type] || colors.info;
  el.textContent = message;
  if (type === 'success') {
    setTimeout(function() { el.textContent = ''; }, 5000);
  }
}
```

**Step 2: Update `handleScriptFile` to call analyze after upload**

Replace the `.then` handler in `handleScriptFile` (the `uploadToBackend(file).then(...)` block):

```javascript
  uploadToBackend(file)
    .then(function(data) {
      console.log('Backend parsed ' + file.name + ': ' + data.scene_count + ' scenes');
      showStatus('Parsed ' + data.scene_count + ' scenes. Analyzing with Claude...', 'info');
      // Show basic parse results immediately
      mapBreakdownToUI(backendToUI(data));
      // Then trigger Claude analysis
      return analyzeWithClaude();
    })
    .catch(function(backendErr) {
      console.warn('Backend unavailable (' + backendErr.message + '), falling back to client-side parsing');
      showStatus('Backend unavailable, using client-side parsing', 'info');
      parseClientSide(file);
    });
```

**Step 3: Add `analyzeWithClaude()` function**

Add after `backendToUI`:

```javascript
function analyzeWithClaude() {
  var apiBase = window.location.origin;
  return fetch(apiBase + '/api/script/analyze', { method: 'POST' })
    .then(function(resp) {
      if (!resp.ok) {
        return resp.json().then(function(err) {
          throw new Error(err.error || 'Analysis failed');
        });
      }
      return resp.json();
    })
    .then(function(data) {
      showStatus('Analysis complete. ' + (data.scenes || []).length + ' scenes with VFX breakdown.', 'success');
      mapBreakdownToUI(data);
    })
    .catch(function(err) {
      showStatus('Claude analysis failed: ' + err.message + '. Showing basic parse results.', 'error');
    });
}
```

**Step 4: Replace all `alert()` calls with `showStatus()`**

Find and replace these patterns:
- `alert('Unsupported file format: .' + ext)` → `showStatus('Unsupported file format: .' + ext, 'error')`
- `alert('PDF upload requires the backend server...')` → `showStatus('PDF upload requires the backend server. Start with: uvicorn sba.app:app --reload', 'error')`
- `alert('Failed to parse Word document: ' + err.message)` → `showStatus('Failed to parse Word document: ' + err.message, 'error')`
- `alert('Failed to parse Final Draft file: ' + err.message)` → `showStatus('Failed to parse Final Draft file: ' + err.message, 'error')`
- `alert('Invalid JSON:...')` → `showStatus('Invalid JSON format', 'error')`
- `alert('Failed to parse JSON: ' + err.message)` → `showStatus('Failed to parse JSON: ' + err.message, 'error')`

**Step 5: Verify JS integrity**

```bash
python3 -c "
with open('script-breakdown-ui.html') as f:
    c = f.read()
print('braces balanced:', c.count('{') == c.count('}'))
for fn in ['showStatus','handleScriptFile','analyzeWithClaude','uploadToBackend']:
    print(f'  {fn}:', 'function ' + fn in c)
"
```

**Step 6: Commit**

```bash
git add script-breakdown-ui.html
git commit -m "feat: wire frontend to Claude analysis with inline status"
```

---

### Task 3: Wire `_get_scene()` to loaded script data

**Files:**
- Modify: `src/sba/chat/tools.py:186-192`

**Step 1: Replace the `_get_scene` stub**

Replace lines 186-192:

```python
def _get_scene(scene_number: str) -> dict[str, Any]:
    """Get scene data from the currently loaded script."""
    from sba.app import _current_script, _current_analysis

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
```

**Step 2: Verify import works**

```bash
python3 -c "from sba.chat.tools import execute_tool; print(execute_tool('get_scene', {'scene_number': '1'}))"
```

Expected: `{'scene_number': '1', 'status': 'not_loaded', 'message': 'No script loaded...'}`

**Step 3: Commit**

```bash
git add src/sba/chat/tools.py
git commit -m "feat: wire get_scene tool to loaded script data"
```

---

### Task 4: Implement `_check_schedule_conflict()`

**Files:**
- Modify: `src/sba/chat/tools.py:231-238`

**Step 1: Replace the stub**

Replace lines 231-238:

```python
def _check_schedule_conflict(scene_a: str, scene_b: str) -> dict[str, Any]:
    """Check scheduling conflicts between two scenes using loaded script data."""
    from sba.app import _current_script, _current_analysis

    def find_scene(num):
        if _current_analysis:
            for s in _current_analysis.scenes:
                if s.scene_id == num:
                    return {
                        "scene_id": s.scene_id,
                        "slugline": s.slugline,
                        "int_ext": s.int_ext,
                        "day_night": s.day_night,
                        "characters": s.characters,
                        "location": getattr(s, "location_type", ""),
                    }
        if _current_script:
            for s in _current_script.get("scenes", []):
                if str(s.get("scene_number")) == num:
                    return s
        return None

    sa = find_scene(scene_a)
    sb = find_scene(scene_b)

    if not sa or not sb:
        missing = []
        if not sa:
            missing.append(scene_a)
        if not sb:
            missing.append(scene_b)
        return {"error": f"Scene(s) {', '.join(missing)} not found. Upload a script first."}

    conflicts = []

    # Shared characters = cast turnaround risk
    chars_a = set(sa.get("characters") or [])
    chars_b = set(sb.get("characters") or [])
    shared = chars_a & chars_b
    if shared:
        conflicts.append({
            "type": "shared_cast",
            "severity": "high",
            "detail": f"Shared characters: {', '.join(sorted(shared))}. Check turnaround if scheduled same day.",
        })

    # Day/night mismatch = lighting turnaround
    dn_a = (sa.get("day_night") or "").lower()
    dn_b = (sb.get("day_night") or "").lower()
    if dn_a and dn_b and dn_a != dn_b:
        conflicts.append({
            "type": "day_night_change",
            "severity": "medium",
            "detail": f"Scene {scene_a} is {dn_a.upper()}, scene {scene_b} is {dn_b.upper()}. Lighting setup change required.",
        })

    # INT/EXT mismatch = potential company move
    ie_a = (sa.get("int_ext") or "").lower()
    ie_b = (sb.get("int_ext") or "").lower()
    if ie_a and ie_b and ie_a != ie_b:
        conflicts.append({
            "type": "int_ext_change",
            "severity": "low",
            "detail": f"Scene {scene_a} is {ie_a.upper()}, scene {scene_b} is {ie_b.upper()}. May need company move.",
        })

    return {
        "scene_a": scene_a,
        "scene_b": scene_b,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "note": "No conflicts detected." if not conflicts else f"{len(conflicts)} potential conflict(s) found.",
    }
```

**Step 2: Verify**

```bash
python3 -c "from sba.chat.tools import execute_tool; print(execute_tool('check_schedule_conflict', {'scene_a': '1', 'scene_b': '2'}))"
```

Expected: error about no script loaded (correct behavior when no script loaded)

**Step 3: Commit**

```bash
git add src/sba/chat/tools.py
git commit -m "feat: implement schedule conflict detection tool"
```

---

### Task 5: Add export endpoints

**Files:**
- Modify: `src/sba/app.py` (add after the budget endpoints section)

**Step 1: Add CSV export endpoint**

```python
@app.get("/api/export/csv")
async def export_csv():
    """Export current analysis as CSV download."""
    if _current_analysis is None:
        return JSONResponse(status_code=400, content={"error": "No analysis loaded. Run /api/script/analyze first."})

    from sba.output.export_csv import export_scenes_csv_string

    csv_text = export_scenes_csv_string(_current_analysis)
    title = "breakdown"
    if _current_script:
        title = _current_script.get("title", "breakdown").replace(" ", "_").lower()

    return StreamingResponse(
        io.BytesIO(csv_text.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{title}_breakdown.csv"'},
    )


@app.get("/api/export/html")
async def export_html_endpoint():
    """Export current analysis as standalone HTML production bible."""
    if _current_analysis is None:
        return JSONResponse(status_code=400, content={"error": "No analysis loaded. Run /api/script/analyze first."})

    from sba.output.export_html import _build_html

    html = _build_html(_current_analysis)
    title = "breakdown"
    if _current_script:
        title = _current_script.get("title", "breakdown").replace(" ", "_").lower()

    return StreamingResponse(
        io.BytesIO(html.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{title}_bible.html"'},
    )
```

**Step 2: Verify**

```bash
python3 -c "from sba.app import app; print('Export endpoints OK')"
```

**Step 3: Commit**

```bash
git add src/sba/app.py
git commit -m "feat: add CSV and HTML export endpoints"
```

---

### Task 6: Add export buttons to UI

**Files:**
- Modify: `script-breakdown-ui.html`

**Step 1: Add export buttons to the title block**

Find the `title-meta` div in the HTML (the one with `id="metaScenes"` etc). Add export buttons after the meta line. Look for `<span id="metaScenes">` and after its parent div, add:

```html
<div id="exportButtons" style="margin-top:12px;display:none">
  <button onclick="exportCSV()" style="font-family:var(--mono);font-size:10px;padding:4px 12px;border:1px solid var(--rule-strong);border-radius:4px;background:var(--surface-2);color:var(--text-3);cursor:pointer;margin:0 4px">Export CSV</button>
  <button onclick="exportHTML()" style="font-family:var(--mono);font-size:10px;padding:4px 12px;border:1px solid var(--rule-strong);border-radius:4px;background:var(--surface-2);color:var(--text-3);cursor:pointer;margin:0 4px">Export HTML</button>
</div>
```

**Step 2: Add export JS functions**

Add near the other utility functions:

```javascript
function exportCSV() {
  window.location.href = window.location.origin + '/api/export/csv';
}
function exportHTML() {
  window.location.href = window.location.origin + '/api/export/html';
}
```

**Step 3: Show export buttons after analysis completes**

In the `analyzeWithClaude` `.then` handler, add after `mapBreakdownToUI(data)`:

```javascript
var expBtns = document.getElementById('exportButtons');
if (expBtns) expBtns.style.display = 'block';
```

**Step 4: Verify JS integrity**

```bash
python3 -c "
with open('script-breakdown-ui.html') as f:
    c = f.read()
print('braces balanced:', c.count('{') == c.count('}'))
for fn in ['exportCSV','exportHTML']:
    print(f'  {fn}:', 'function ' + fn in c)
"
```

**Step 5: Commit**

```bash
git add script-breakdown-ui.html
git commit -m "feat: add CSV and HTML export buttons"
```

---

### Task 7: Run all tests and verify

**Step 1: Run full test suite**

```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
python3 -m pytest tests/ -v
```

Expected: 75 passed

**Step 2: Verify server starts**

```bash
python3 -c "from sba.app import app; print([r.path for r in app.routes if hasattr(r, 'path')])"
```

Expected: list includes `/api/script/analyze`, `/api/export/csv`, `/api/export/html`

**Step 3: Verify JS integrity**

```bash
python3 -c "
with open('script-breakdown-ui.html') as f:
    c = f.read()
opens = c.count('{')
closes = c.count('}')
print(f'Braces: {{ = {opens}, }} = {closes}, balanced = {opens == closes}')
fns = ['showStatus','handleScriptFile','analyzeWithClaude','uploadToBackend','backendToUI','exportCSV','exportHTML','mapBreakdownToUI','parseClientSide']
for fn in fns:
    found = 'function ' + fn in c
    print(f'  {\"ok\" if found else \"MISSING\"}: {fn}')
"
```

**Step 4: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix: address test/lint issues from P1-P4 implementation"
```
