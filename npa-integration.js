/**
 * NPA Integration — connects the UI to the FastAPI backend.
 * Adds: Chat panel, Budget bar, Voice input.
 * Auto-injects UI components on DOMContentLoaded.
 */
(function() {
  'use strict';

  const API_BASE = window.location.origin;
  let isRecording = false;
  let mediaRecorder = null;

  // ================================================================
  // INJECT UI COMPONENTS
  // ================================================================
  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .budget-bar { position:fixed; bottom:0; left:0; right:0; height:48px; background:var(--surface-raised,#1a1918); border-top:1px solid var(--border,#2a2826); display:flex; align-items:center; padding:0 20px; gap:24px; font-family:var(--mono,'JetBrains Mono',monospace); font-size:11px; z-index:200; }
      .budget-bar.hidden { display:none; }
      .budget-item { display:flex; align-items:center; gap:6px; }
      .budget-label { color:var(--text-3,#777); text-transform:uppercase; letter-spacing:0.5px; }
      .budget-value { color:var(--text-1,#eee); font-weight:600; }
      .budget-value.over { color:#e74c3c; }
      .budget-value.under { color:#2ecc71; }
      .budget-status { margin-left:auto; display:flex; align-items:center; gap:8px; }
      .budget-dot { width:8px; height:8px; border-radius:50%; }
      .budget-dot.connected { background:#2ecc71; }
      .budget-dot.disconnected { background:#e74c3c; }

      .chat-toggle { position:fixed; bottom:20px; right:20px; width:52px; height:52px; border-radius:50%; background:var(--accent,#c9a84c); color:var(--bg,#0f0e0d); border:none; cursor:pointer; z-index:300; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 16px rgba(0,0,0,0.5); transition:all 0.2s; }
      .chat-toggle:hover { transform:scale(1.1); }
      .chat-panel { position:fixed; bottom:20px; right:20px; width:400px; height:540px; background:var(--bg,#0f0e0d); border:1px solid var(--border,#2a2826); border-radius:12px; display:none; flex-direction:column; z-index:400; box-shadow:0 8px 32px rgba(0,0,0,0.6); overflow:hidden; }
      .chat-panel.open { display:flex; }
      .chat-header { padding:12px 16px; background:var(--surface-raised,#1a1918); border-bottom:1px solid var(--border,#2a2826); display:flex; align-items:center; justify-content:space-between; }
      .chat-header h3 { margin:0; font-size:14px; color:var(--accent,#c9a84c); font-family:var(--heading,'Source Serif 4',serif); }
      .model-badge { font-family:var(--mono,monospace); font-size:9px; padding:2px 8px; border-radius:3px; background:rgba(201,168,76,0.15); color:var(--accent,#c9a84c); }
      .chat-messages { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:8px; }
      .chat-msg { max-width:85%; padding:10px 14px; border-radius:10px; font-size:13px; line-height:1.5; font-family:var(--body,'Inter',sans-serif); }
      .chat-msg.user { align-self:flex-end; background:rgba(201,168,76,0.15); color:var(--text-1,#eee); border-bottom-right-radius:2px; }
      .chat-msg.assistant { align-self:flex-start; background:var(--surface-raised,#1a1918); color:var(--text-2,#bbb); border-bottom-left-radius:2px; }
      .chat-msg.thinking { align-self:flex-start; background:transparent; color:var(--text-3,#777); font-style:italic; font-size:11px; border-left:2px solid rgba(201,168,76,0.3); padding-left:10px; }
      .chat-input-area { padding:10px 12px; border-top:1px solid var(--border,#2a2826); display:flex; gap:8px; align-items:center; }
      .chat-input-area input { flex:1; background:var(--surface,#151413); border:1px solid var(--border,#2a2826); border-radius:8px; padding:10px 14px; color:var(--text-1,#eee); font-family:var(--body,'Inter',sans-serif); font-size:13px; outline:none; }
      .chat-input-area input:focus { border-color:var(--accent,#c9a84c); }
      .chat-send-btn { background:var(--accent,#c9a84c); border:none; border-radius:8px; padding:10px 16px; color:var(--bg,#0f0e0d); cursor:pointer; font-weight:700; font-size:12px; }
      .voice-btn { background:transparent; border:1px solid var(--border,#2a2826); border-radius:8px; padding:8px; color:var(--text-3,#777); cursor:pointer; }
      .voice-btn:hover { color:var(--accent,#c9a84c); border-color:var(--accent,#c9a84c); }
      .voice-btn.recording { color:#e74c3c; border-color:#e74c3c; animation:npa-pulse 1s infinite; }
      @keyframes npa-pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    `;
    document.head.appendChild(style);
  }

  function injectHTML() {
    const wrapper = document.createElement('div');
    wrapper.id = 'npa-integration';
    wrapper.innerHTML = `
      <div class="budget-bar hidden" id="budgetBar">
        <div class="budget-item"><span class="budget-label">Total Budget</span><span class="budget-value" id="budgetTotal">--</span></div>
        <div class="budget-item"><span class="budget-label">Actual</span><span class="budget-value" id="budgetActual">--</span></div>
        <div class="budget-item"><span class="budget-label">Variance</span><span class="budget-value" id="budgetVariance">--</span></div>
        <div class="budget-status"><div class="budget-dot disconnected" id="budgetDot"></div><span class="budget-label" id="budgetStatusText">Budget: Checking...</span></div>
      </div>
      <button class="chat-toggle" id="chatToggle" title="Producer Copilot">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
      </button>
      <div class="chat-panel" id="chatPanel">
        <div class="chat-header">
          <h3>Producer Copilot</h3>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="model-badge" id="modelBadge">SONNET</span>
            <button id="chatClose" style="background:none;border:none;color:var(--text-3,#777);cursor:pointer;font-size:20px">\u00D7</button>
          </div>
        </div>
        <div class="chat-messages" id="chatMessages">
          <div class="chat-msg assistant">Hey producer. I'm your AI copilot. Ask me about budget lines, scene costs, overtime, or hidden cost risks.</div>
        </div>
        <div class="chat-input-area">
          <button class="voice-btn" id="voiceBtn" title="Voice input">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
          </button>
          <input type="text" id="chatInput" placeholder="Ask about budget, scenes, costs..." />
          <button class="chat-send-btn" id="chatSendBtn">Send</button>
        </div>
      </div>
    `;
    document.body.appendChild(wrapper);
  }

  // ================================================================
  // CHAT
  // ================================================================
  function toggleChat() {
    var panel = document.getElementById('chatPanel');
    var toggle = document.getElementById('chatToggle');
    panel.classList.toggle('open');
    toggle.style.display = panel.classList.contains('open') ? 'none' : 'flex';
  }

  function addMsg(text, role) {
    var messages = document.getElementById('chatMessages');
    var msg = document.createElement('div');
    msg.className = 'chat-msg ' + role;
    msg.textContent = text;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
    return msg;
  }

  function sendChat() {
    var input = document.getElementById('chatInput');
    var text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMsg(text, 'user');

    fetch(API_BASE + '/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.thinking) addMsg(data.thinking.substring(0, 200) + '...', 'thinking');
      var badge = document.getElementById('modelBadge');
      if (data.model_used) {
        if (data.model_used.indexOf('opus') > -1) badge.textContent = 'OPUS';
        else if (data.model_used.indexOf('haiku') > -1) badge.textContent = 'HAIKU';
        else badge.textContent = 'SONNET';
      }
      addMsg(data.reply || data.error || 'No response', 'assistant');
    })
    .catch(function() {
      addMsg('Backend not running. Start with: uvicorn sba.app:app --reload', 'assistant');
    });
  }

  // ================================================================
  // BUDGET BAR
  // ================================================================
  function loadBudget() {
    fetch(API_BASE + '/api/budget/summary')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.error) {
        document.getElementById('budgetStatusText').textContent = 'No budget file loaded';
        return;
      }
      var fmt = function(n) { return '$' + Number(n).toLocaleString('en-US', {maximumFractionDigits:0}); };
      document.getElementById('budgetTotal').textContent = fmt(data.total_budget);
      document.getElementById('budgetActual').textContent = fmt(data.total_actual);
      var v = data.total_variance;
      var el = document.getElementById('budgetVariance');
      el.textContent = (v >= 0 ? '+' : '') + fmt(v);
      el.className = 'budget-value ' + (v >= 0 ? 'under' : 'over');
      document.getElementById('budgetDot').className = 'budget-dot connected';
      document.getElementById('budgetStatusText').textContent = 'Budget: Connected';
      document.getElementById('budgetBar').classList.remove('hidden');
    })
    .catch(function() {});
  }

  // ================================================================
  // VOICE
  // ================================================================
  function toggleVoice() {
    var btn = document.getElementById('voiceBtn');
    if (isRecording) {
      isRecording = false;
      btn.classList.remove('recording');
      if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
      return;
    }
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function(stream) {
      mediaRecorder = new MediaRecorder(stream);
      var chunks = [];
      mediaRecorder.ondataavailable = function(e) { chunks.push(e.data); };
      mediaRecorder.onstop = function() {
        stream.getTracks().forEach(function(t) { t.stop(); });
        var blob = new Blob(chunks, { type: 'audio/webm' });
        var fd = new FormData();
        fd.append('audio', blob, 'voice.webm');
        fetch(API_BASE + '/api/voice/transcribe', { method: 'POST', body: fd })
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.text) { document.getElementById('chatInput').value = data.text; sendChat(); }
        })
        .catch(function() { addMsg('Voice transcription requires the backend.', 'assistant'); });
      };
      mediaRecorder.start();
      isRecording = true;
      btn.classList.add('recording');
      setTimeout(function() { if (isRecording) toggleVoice(); }, 15000);
    })
    .catch(function() { addMsg('Microphone access denied.', 'assistant'); });
  }

  // ================================================================
  // INIT
  // ================================================================
  function init() {
    injectStyles();
    injectHTML();

    document.getElementById('chatToggle').addEventListener('click', toggleChat);
    document.getElementById('chatClose').addEventListener('click', toggleChat);
    document.getElementById('chatSendBtn').addEventListener('click', sendChat);
    document.getElementById('chatInput').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') sendChat();
    });
    document.getElementById('voiceBtn').addEventListener('click', toggleVoice);

    // Check backend
    fetch(API_BASE + '/api/health')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.status === 'ok') {
        loadBudget();
        console.log('NPA Backend connected v' + data.version);
      }
    })
    .catch(function() {
      console.log('NPA standalone mode. Run: uvicorn sba.app:app --reload');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
