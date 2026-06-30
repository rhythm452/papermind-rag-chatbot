import streamlit as st
import requests
import re
import json
import random
import streamlit.components.v1 as components

API_URL = "http://localhost:8000"

st.set_page_config(page_title="PaperMind", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# ── Theme ──────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "lang" not in st.session_state:
    st.session_state.lang = "English"

D = st.session_state.dark_mode
BG      = "#0a0a0f" if D else "#f8fafc"
BG2     = "#0f0f1a" if D else "#ffffff"
BG3     = "#1e1e2e" if D else "#f1f5f9"
BORDER  = "#1e1e2e" if D else "#e2e8f0"
BORDER2 = "#2d2d44" if D else "#cbd5e1"
TEXT    = "#e2e8f0" if D else "#0f172a"
TEXT2   = "#94a3b8" if D else "#475569"
TEXT3   = "#475569" if D else "#94a3b8"
CARD    = "#0f0f1a" if D else "#ffffff"
AI_BG   = "#0f0f1a" if D else "#f8fafc"
AI_BORDER = "#1e1e2e" if D else "#e2e8f0"
AI_TEXT = "#cbd5e1" if D else "#1e293b"
IN_BG   = "#0f0f1a" if D else "#ffffff"
TOGGLE_BG = "#1e1e2e" if D else "#f1f5f9"
TOGGLE_LABEL = "☀️ Light" if D else "🌙 Dark"
ACCENT  = "#818cf8"
ACCENT2 = "#a78bfa"
ACCENT3 = "#38bdf8"
BTN     = "linear-gradient(135deg,#4f46e5,#7c3aed)"
robot_body = "#1e1e3a" if D else "#e8eeff"
robot_eye_bg = "#0a0a0f" if D else "#c7d2fe"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"], p, div, span, label, input, textarea, button {{font-family:'Inter',sans-serif!important;}}
[data-testid="stExpanderToggleIcon"], [class*="material-icons"], [data-testid="stIconMaterial"] {{font-family:'Material Symbols Rounded' !important;}}
.stApp{{background:{BG}!important;transition:background 0.3s;}}
[data-testid="stSidebar"]{{background:{BG2}!important;border-right:1px solid {BORDER}!important;position:relative;z-index:2;}}
.main .block-container{{padding:1.5rem 2rem;max-width:1200px;position:relative;z-index:2;}}

/* Animated gradient background */
.gradient-bg{{
    position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;
    background:linear-gradient(45deg,{"#0a0a0f,#15102c,#0a0a0f,#0f0a20,#0a0a0f" if D else "#f8fafc,#eef0ff,#f8fafc,#f5eeff,#f8fafc"});
    background-size:400% 400%;
    animation:gradientShift 12s ease infinite;
}}
@keyframes gradientShift{{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}

/* Robot */
.robot-wrap{{position:relative;width:72px;height:72px;animation:float 3s ease-in-out infinite;filter:drop-shadow(0 0 8px {ACCENT}44);}}
@keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}
.robot-eye{{animation:blink 4s ease-in-out infinite;transform-origin:center;}}
@keyframes blink{{0%,44%,56%,100%{{transform:scaleY(1);}}50%{{transform:scaleY(0.05);}}}}
.robot-antenna{{animation:wiggle 2.5s ease-in-out infinite;transform-origin:bottom center;}}
@keyframes wiggle{{0%,100%{{transform:rotate(0);}}25%{{transform:rotate(8deg);}}75%{{transform:rotate(-8deg);}}}}

/* Neon active tab */
.stTabs [data-baseweb="tab-list"]{{background:{BG2}!important;border-radius:12px;padding:4px;gap:2px;border:1px solid {BORDER}!important;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;color:{TEXT3}!important;font-weight:500;font-size:0.85rem;padding:8px 18px;transition:all 0.2s;}}
.stTabs [aria-selected="true"]{{
    background:{BG3}!important;color:{ACCENT2}!important;
    box-shadow:0 0 16px 2px {ACCENT}77, 0 0 32px 4px {ACCENT}33, inset 0 0 8px {ACCENT}22!important;
    border:1.5px solid {ACCENT}aa!important;
    animation:neonPulse 2.5s ease-in-out infinite;
}}
@keyframes neonPulse{{
    0%,100%{{box-shadow:0 0 16px 2px {ACCENT}77, 0 0 32px 4px {ACCENT}33, inset 0 0 8px {ACCENT}22;}}
    50%{{box-shadow:0 0 22px 4px {ACCENT}99, 0 0 44px 8px {ACCENT}44, inset 0 0 12px {ACCENT}33;}}
}}
.stTabs [data-baseweb="tab-highlight"]{{background-color:{ACCENT}!important;height:2px!important;box-shadow:0 0 8px {ACCENT}!important;}}
.stTabs [data-baseweb="tab-panel"]{{padding-top:1.5rem;}}

/* Cards */
.card{{background:{CARD};border:1px solid {BORDER};border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1rem;transition:border-color 0.2s,box-shadow 0.2s;}}
.card:hover{{border-color:{BORDER2};box-shadow:0 4px 20px rgba(0,0,0,0.15);}}
.card-title{{font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:{TEXT3};margin-bottom:0.75rem;}}

/* Stat pills */
.stat-row{{display:flex;gap:8px;flex-wrap:wrap;margin:0.75rem 0 1.25rem;}}
.stat-pill{{background:{BG2};border:1px solid {BORDER};border-radius:20px;padding:4px 12px;font-size:0.76rem;color:{TEXT2};font-weight:500;transition:all 0.2s;}}
.stat-pill:hover{{border-color:{ACCENT2};color:{ACCENT2};}}
.stat-pill span{{color:{ACCENT2};font-weight:600;}}

/* Mode badges */
.mode-badge-resume{{display:inline-block;background:#1a1a3e;border:1px solid #3730a3;color:#a5b4fc;border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:600;}}
.mode-badge-doc{{display:inline-block;background:#0f2a1a;border:1px solid #166534;color:#86efac;border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:600;}}

/* Chat */
.chat-user{{display:flex;justify-content:flex-end;margin:0.75rem 0;}}
.chat-user .bubble{{background:{BTN};color:#fff;border-radius:18px 18px 4px 18px;padding:10px 16px;max-width:70%;font-size:0.88rem;line-height:1.5;box-shadow:0 2px 12px rgba(79,70,229,0.4);}}
.chat-ai{{display:flex;justify-content:flex-start;margin:0.75rem 0;gap:10px;align-items:flex-start;}}
.chat-ai .avatar{{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,{ACCENT},{ACCENT3});display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;box-shadow:0 0 8px {ACCENT}66;}}
.chat-ai .bubble{{background:{AI_BG};border:1px solid {AI_BORDER};color:{AI_TEXT};border-radius:4px 18px 18px 18px;padding:10px 16px;max-width:75%;font-size:0.88rem;line-height:1.6;}}

/* Typing animation */
.typing-cursor{{display:inline-block;width:2px;height:14px;background:{ACCENT};animation:cursor 0.8s infinite;vertical-align:middle;margin-left:2px;}}
@keyframes cursor{{0%,100%{{opacity:1;}}50%{{opacity:0;}}}}

/* Follow-up questions */
.followup-wrap{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}}
.followup-btn{{background:{BG3};border:1px solid {ACCENT}44;color:{ACCENT2};border-radius:20px;padding:5px 14px;font-size:0.78rem;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;}}
.followup-btn:hover{{background:{ACCENT}22;border-color:{ACCENT};}}

/* Score card */
.score-ring-wrap{{display:flex;flex-direction:column;align-items:center;gap:4px;}}
.score-ring{{position:relative;width:80px;height:80px;}}
.score-ring svg{{transform:rotate(-90deg);}}
.score-ring .ring-bg{{fill:none;stroke:{BG3};stroke-width:6;}}
.score-ring .ring-fill{{fill:none;stroke-width:6;stroke-linecap:round;transition:stroke-dashoffset 1s ease;}}
.score-ring .ring-text{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.1rem;font-weight:700;color:{TEXT};}}
.score-label-text{{font-size:0.72rem;color:{TEXT3};font-weight:500;text-align:center;}}
.score-comment{{font-size:0.76rem;color:{TEXT2};text-align:center;margin-top:4px;line-height:1.4;max-width:200px;}}
.score-ring-wrap{{padding:0 6px;}}

/* Timeline */
.timeline-item{{display:flex;gap:16px;margin-bottom:20px;position:relative;}}
.timeline-dot{{width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,{ACCENT},{ACCENT2});flex-shrink:0;margin-top:4px;box-shadow:0 0 8px {ACCENT}88;}}
.timeline-line{{position:absolute;left:5px;top:16px;bottom:-20px;width:2px;background:linear-gradient(180deg,{ACCENT}66,transparent);}}
.timeline-content{{flex:1;}}
.timeline-title{{font-weight:600;color:{TEXT};font-size:0.88rem;}}
.timeline-company{{color:{ACCENT2};font-size:0.8rem;}}
.timeline-date{{color:{TEXT3};font-size:0.75rem;}}
.timeline-desc{{color:{TEXT2};font-size:0.8rem;margin-top:4px;line-height:1.5;}}

/* Word cloud */
.wordcloud-wrap{{display:flex;flex-wrap:wrap;gap:8px;padding:1rem;align-items:center;justify-content:center;}}
.wc-word{{border-radius:8px;padding:4px 12px;font-weight:600;transition:transform 0.2s;cursor:default;}}
.wc-word:hover{{transform:scale(1.1);}}

/* Confetti */
.confetti-wrap{{position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:9999;overflow:hidden;}}
.confetti-piece{{position:absolute;width:10px;height:10px;border-radius:2px;animation:confettiFall linear forwards;}}
@keyframes confettiFall{{0%{{top:-20px;opacity:1;transform:rotate(0deg);}}100%{{top:100vh;opacity:0;transform:rotate(720deg);}}}}

/* Skill badges */
.skill-wrap{{display:flex;flex-wrap:wrap;gap:6px;margin:0.5rem 0;}}
.skill-badge{{background:#1a1a3e;border:1px solid #3730a3;color:#a5b4fc;border-radius:6px;padding:3px 10px;font-size:0.75rem;font-weight:500;}}

/* Section label */
.section-label{{font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:{TEXT3};margin:1rem 0 0.5rem;}}
.fancy-divider{{height:1px;background:linear-gradient(90deg,transparent,{BORDER},transparent);margin:1rem 0;}}

/* Score box */
.score-box{{background:{BG2};border:1px solid #3730a3;border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1rem;}}
.score-number-big{{font-size:3.5rem;font-weight:700;line-height:1;}}

/* Candidate row */
.candidate-row{{display:flex;align-items:center;background:{BG2};border:1px solid {BORDER};border-radius:10px;padding:10px 14px;margin-bottom:6px;transition:border-color 0.2s;}}
.candidate-row.active{{border-color:#4f46e5;background:#0f0f2a;}}
.candidate-name{{font-size:0.85rem;font-weight:500;color:{TEXT};}}
.candidate-id{{font-size:0.72rem;color:{TEXT3};font-family:monospace;}}

/* Inputs */
.stTextInput input,.stTextArea textarea{{background:{IN_BG}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important;font-family:'Inter',sans-serif!important;}}
.stTextInput input:focus,.stTextArea textarea:focus{{border-color:{ACCENT}!important;box-shadow:0 0 0 3px {ACCENT}22!important;}}

/* Buttons */
.stButton button{{background:{BTN}!important;border:none!important;border-radius:10px!important;color:#fff!important;font-weight:600!important;font-family:'Inter',sans-serif!important;padding:0.5rem 1.25rem!important;box-shadow:0 2px 12px rgba(79,70,229,0.4)!important;transition:opacity 0.2s,transform 0.1s!important;}}
.stButton button:hover{{opacity:0.88!important;transform:translateY(-1px)!important;}}

/* File uploader */
[data-testid="stFileUploader"]{{background:{BG2}!important;border:1px dashed {BORDER2}!important;border-radius:12px!important;}}

/* Expander */
.streamlit-expanderHeader{{background:{BG2}!important;border:1px solid {BORDER}!important;border-radius:8px!important;color:{TEXT3}!important;font-size:0.8rem!important;}}

/* Logo */
.logo-text{{font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,{ACCENT},{ACCENT2},{ACCENT3});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.logo-sub{{color:{TEXT3};font-size:0.72rem;margin-top:2px;}}
.hero-title{{font-size:1.8rem;font-weight:700;background:linear-gradient(135deg,{ACCENT},{ACCENT2},{ACCENT3});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;line-height:1.2;}}
.hero-sub{{color:{TEXT2};font-size:0.82rem;margin-top:2px;}}

#MainMenu,footer,header{{visibility:hidden;}}
</style>
<div class="gradient-bg"></div>
""", unsafe_allow_html=True)

# ── Typing animation function ───────────────────────────────────────────────
def typing_effect(text, container, speed=0.008):
    """Render text with a letter-by-letter typing animation inside a chat bubble."""
    import time
    displayed = ""
    placeholder = container.empty()
    # Type in small chunks for performance (whole words, not every single char)
    words = text.split(" ")
    chunk = ""
    for i, word in enumerate(words):
        chunk += word + " "
        displayed = chunk
        cursor = '<span class="typing-cursor"></span>' if i < len(words) - 1 else ""
        placeholder.markdown(f"""
        <div class='chat-ai'>
            <div class='avatar'>🧠</div>
            <div class='bubble'>{displayed}{cursor}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(speed * max(1, len(word) // 3))
    return placeholder

# ── Confetti function ───────────────────────────────────────────────────────
def voice_input_widget(lang_code="en-US", key="voice"):
    """
    Voice input that directly types the transcript into Streamlit's real
    chat_input box (in the parent DOM, same-origin) and auto-presses Enter.
    Works because the components iframe and main Streamlit app are same-origin,
    so window.parent.document access is allowed (no cross-origin block).
    """
    html_code = f"""
    <div style="display:flex;align-items:center;gap:10px;padding:6px 0;">
        <button id="mic-btn-{key}" onclick="startVoice_{key}()"
            style="background:linear-gradient(135deg,#4f46e5,#7c3aed);border:none;border-radius:50%;
            width:46px;height:46px;cursor:pointer;display:flex;align-items:center;justify-content:center;
            box-shadow:0 2px 12px rgba(79,70,229,0.4);transition:transform 0.15s;font-size:20px;flex-shrink:0;">
            🎤
        </button>
        <span id="mic-status-{key}" style="font-size:0.8rem;color:#94a3b8;font-family:Inter,sans-serif;">Click and speak — it will type and submit automatically</span>
    </div>
    <script>
    var recognition_{key} = null;
    var isListening_{key} = false;

    function findChatInput_{key}() {{
        // Streamlit's chat_input renders a <textarea> with this data-testid in the parent document
        const doc = window.parent.document;
        return doc.querySelector('textarea[data-testid="stChatInputTextArea"]')
            || doc.querySelector('[data-testid="stChatInput"] textarea')
            || doc.querySelector('textarea[placeholder]');
    }}

    function setNativeValue(element, value) {{
        const valueSetter = Object.getOwnPropertyDescriptor(element, 'value');
        const prototype = Object.getPrototypeOf(element);
        const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value');
        if (valueSetter && valueSetter.set !== prototypeValueSetter.set) {{
            prototypeValueSetter.set.call(element, value);
        }} else if (prototypeValueSetter && prototypeValueSetter.set) {{
            prototypeValueSetter.set.call(element, value);
        }} else {{
            element.value = value;
        }}
    }}

    function startVoice_{key}() {{
        const btn = document.getElementById('mic-btn-{key}');
        const status = document.getElementById('mic-status-{key}');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {{
            status.innerText = '❌ Not supported. Use Chrome or Edge.';
            return;
        }}
        if (isListening_{key}) {{
            status.innerText = 'Already listening...';
            return;
        }}

        navigator.mediaDevices.getUserMedia({{ audio: true }})
            .then(function(stream) {{
                stream.getTracks().forEach(track => track.stop());
                runRecognition();
            }})
            .catch(function(err) {{
                status.innerText = '❌ Mic permission denied. Click 🔒 in address bar → allow microphone.';
            }});

        function runRecognition() {{
            recognition_{key} = new SpeechRecognition();
            recognition_{key}.lang = '{lang_code}';
            recognition_{key}.interimResults = true;
            recognition_{key}.maxAlternatives = 1;
            recognition_{key}.continuous = false;

            isListening_{key} = true;
            btn.style.transform = 'scale(1.15)';
            btn.style.boxShadow = '0 0 0 6px rgba(79,70,229,0.3)';
            status.innerText = '🔴 Listening... speak now';

            recognition_{key}.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                const isFinal = event.results[0].isFinal;
                status.innerText = isFinal ? ('✓ Heard: ' + transcript + ' — typing it now...') : ('Hearing: ' + transcript + '...');

                if (isFinal) {{
                    const input = findChatInput_{key}();
                    if (!input) {{
                        status.innerText = '⚠️ Could not find chat box. Result: ' + transcript;
                        return;
                    }}
                    input.focus();
                    setNativeValue(input, transcript);
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));

                    setTimeout(function() {{
                        const enterEvent = new KeyboardEvent('keydown', {{
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13, which: 13
                        }});
                        input.dispatchEvent(enterEvent);
                        status.innerText = '✅ Submitted: ' + transcript;
                    }}, 200);
                }}
            }};

            recognition_{key}.onerror = function(event) {{
                if (event.error === 'aborted') {{
                    status.innerText = 'Stopped. Click mic to try again.';
                }} else if (event.error === 'no-speech') {{
                    status.innerText = '⚠️ No speech detected. Click mic and try again.';
                }} else if (event.error === 'not-allowed') {{
                    status.innerText = '❌ Mic blocked. Allow microphone access in browser settings.';
                }} else {{
                    status.innerText = '❌ Error: ' + event.error;
                }}
                isListening_{key} = false;
                btn.style.transform = 'scale(1)';
                btn.style.boxShadow = '0 2px 12px rgba(79,70,229,0.4)';
            }};

            recognition_{key}.onend = function() {{
                isListening_{key} = false;
                btn.style.transform = 'scale(1)';
                btn.style.boxShadow = '0 2px 12px rgba(79,70,229,0.4)';
            }};

            try {{
                recognition_{key}.start();
            }} catch(e) {{
                status.innerText = '❌ Could not start: ' + e.message;
                isListening_{key} = false;
            }}
        }}
    }}
    </script>
    """
    components.html(html_code, height=60)


def show_confetti():
    colors = ["#818cf8","#a78bfa","#38bdf8","#f472b6","#fb923c","#22c55e","#fbbf24"]
    pieces = ""
    for i in range(80):
        color = random.choice(colors)
        left = random.randint(0, 100)
        delay = random.uniform(0, 2)
        duration = random.uniform(2, 4)
        size = random.randint(6, 14)
        pieces += f'<div class="confetti-piece" style="left:{left}%;background:{color};width:{size}px;height:{size}px;animation-duration:{duration}s;animation-delay:{delay}s;"></div>'
    st.markdown(f'<div class="confetti-wrap">{pieces}</div>', unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
for key, default in {
    "docs":{}, "active_doc_id":None, "active_label":None,
    "active_mode":None, "chat_history":[], "messages":[], "doc_stats":{},
    "followups":[], "show_confetti": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0 0.5rem'>
        <div class='logo-text'>🧠 PaperMind</div>
        <div class='logo-sub'>Resume & Document AI · RAG powered</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

    # Language selector
    st.markdown("<div class='section-label'>🌐 Language</div>", unsafe_allow_html=True)
    lang = st.selectbox("lang", ["English", "Hindi", "Spanish", "French", "German"],
        label_visibility="collapsed", index=["English","Hindi","Spanish","French","German"].index(st.session_state.lang))
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Upload PDF</div>", unsafe_allow_html=True)

    mode = st.radio("type", ["📄 Document / Article / Paper", "👤 Resume / CV"],
        label_visibility="collapsed", horizontal=False)
    is_resume = "Resume" in mode
    mode_key = "resume" if is_resume else "document"

    label = st.text_input("label",
        placeholder="e.g. Rhythm Jain" if is_resume else "e.g. Attention Is All You Need",
        label_visibility="collapsed")
    uploaded_file = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")

    if uploaded_file and label and st.button("⚡ Ingest Resume" if is_resume else "⚡ Ingest Document", use_container_width=True):
        with st.spinner(f"Processing '{label}'..."):
            r = requests.post(f"{API_URL}/upload", files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")})
        if r.status_code == 200:
            data = r.json()
            st.session_state.docs[label] = {"doc_id": data["doc_id"], "mode": mode_key}
            st.session_state.doc_stats[data["doc_id"]] = {"pages": data["total_pages"], "chunks": data["total_chunks"]}
            st.session_state.active_doc_id = data["doc_id"]
            st.session_state.active_label = label
            st.session_state.active_mode = mode_key
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.success(f"✓ {data['total_pages']} pages · {data['total_chunks']} chunks")
        else:
            st.error(r.json().get("detail", "Upload failed"))

    if st.session_state.docs:
        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Uploaded files</div>", unsafe_allow_html=True)
        for lbl, info in st.session_state.docs.items():
            is_active = info["doc_id"] == st.session_state.active_doc_id
            icon = "👤" if info["mode"] == "resume" else "📄"
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"""<div class='candidate-row {"active" if is_active else ""}'>
                    <div><div class='candidate-name'>{"●" if is_active else "○"} {icon} {lbl}</div>
                    <div class='candidate-id'>{info['doc_id']}</div></div></div>""", unsafe_allow_html=True)
            with c2:
                if st.button("→", key=f"sel_{info['doc_id']}"):
                    st.session_state.active_doc_id = info["doc_id"]
                    st.session_state.active_label = lbl
                    st.session_state.active_mode = info["mode"]
                    st.session_state.chat_history = []
                    st.session_state.messages = []
                    st.rerun()

    if st.session_state.messages:
        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
        if st.button("🗑 Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.rerun()

# ── current mode ───────────────────────────────────────────────────────────
current_display_mode = "resume" if is_resume else "document"
hero_title = "Resume Intelligence" if current_display_mode == "resume" else "Document Intelligence"
hero_sub = "Chat · Parse · Score · Timeline · Wordcloud · Fit · Compare" if current_display_mode == "resume" else "Chat · Summarise · Extract · Compare"

# ── Top bar ────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 7, 2])
with c1:
    st.markdown(f"""
    <div class="robot-wrap" style="margin-top:6px">
      <svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g class="robot-antenna">
          <line x1="36" y1="4" x2="36" y2="14" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="36" cy="3" r="3.5" fill="{ACCENT2}"/>
          <circle cx="36" cy="3" r="1.5" fill="#fff" opacity="0.6"/>
        </g>
        <rect x="10" y="14" width="52" height="34" rx="11" fill="{robot_body}" stroke="{ACCENT}" stroke-width="1.5"/>
        <rect x="10" y="14" width="52" height="34" rx="11" fill="url(#robotGrad)" opacity="0.3"/>
        <defs><linearGradient id="robotGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{ACCENT}"/><stop offset="100%" stop-color="{ACCENT3}"/></linearGradient></defs>
        <g class="robot-eye">
          <ellipse cx="25" cy="28" rx="6" ry="6.5" fill="{robot_eye_bg}"/>
          <ellipse cx="25" cy="28" rx="3.5" ry="4" fill="{ACCENT}"/>
          <circle cx="26.5" cy="26.5" r="1.2" fill="#ffffff"/>
          <circle cx="24" cy="29" r="0.8" fill="{ACCENT3}" opacity="0.7"/>
        </g>
        <g class="robot-eye">
          <ellipse cx="47" cy="28" rx="6" ry="6.5" fill="{robot_eye_bg}"/>
          <ellipse cx="47" cy="28" rx="3.5" ry="4" fill="{ACCENT}"/>
          <circle cx="48.5" cy="26.5" r="1.2" fill="#ffffff"/>
          <circle cx="46" cy="29" r="0.8" fill="{ACCENT3}" opacity="0.7"/>
        </g>
        <rect x="21" y="37" width="30" height="5" rx="2.5" fill="{BG3}"/>
        <rect x="25" y="38.5" width="7" height="2" rx="1" fill="{ACCENT2}"/>
        <rect x="36" y="38.5" width="5" height="2" rx="1" fill="{ACCENT3}"/>
        <rect x="43" y="38.5" width="4" height="2" rx="1" fill="#f472b6"/>
        <rect x="14" y="48" width="11" height="18" rx="5.5" fill="{robot_body}" stroke="{ACCENT}" stroke-width="1.5"/>
        <rect x="47" y="48" width="11" height="18" rx="5.5" fill="{robot_body}" stroke="{ACCENT}" stroke-width="1.5"/>
        <rect x="16" y="57" width="7" height="7" rx="3.5" fill="{ACCENT2}"/>
        <rect x="49" y="57" width="7" height="7" rx="3.5" fill="{ACCENT3}"/>
        <rect x="24" y="49" width="24" height="3" rx="1.5" fill="{robot_body}" stroke="{ACCENT}" stroke-width="1"/>
      </svg>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div style="padding-top:10px">
        <div class="hero-title">{hero_title}</div>
        <div class="hero-sub">{hero_sub} · {st.session_state.lang}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if st.button(TOGGLE_LABEL, key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown(f"<div style='height:1px;background:linear-gradient(90deg,transparent,{BORDER},{ACCENT}44,{BORDER},transparent);margin:0.5rem 0 1rem'></div>", unsafe_allow_html=True)

# ── Stat pills ─────────────────────────────────────────────────────────────
if st.session_state.active_doc_id:
    stats = st.session_state.doc_stats.get(st.session_state.active_doc_id, {})
    mode_badge = "<span class='mode-badge-resume'>👤 Resume</span>" if st.session_state.active_mode == "resume" else "<span class='mode-badge-doc'>📄 Document</span>"
    st.markdown(f"""<div class='stat-row'>
        {mode_badge}
        <div class='stat-pill'>🏷 <span>{st.session_state.active_label}</span></div>
        <div class='stat-pill'>📄 <span>{stats.get('pages','?')}</span> pages</div>
        <div class='stat-pill'>🧩 <span>{stats.get('chunks','?')}</span> chunks</div>
        <div class='stat-pill'>🤖 LLaMA 3.1</div>
        <div class='stat-pill'>🌐 {st.session_state.lang}</div>
    </div>""", unsafe_allow_html=True)

# ── Show confetti if needed ────────────────────────────────────────────────
if st.session_state.show_confetti:
    show_confetti()
    st.session_state.show_confetti = False

# ── Tabs ───────────────────────────────────────────────────────────────────
if current_display_mode == "resume":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💬 Chat", "🔍 Parse", "⭐ Score Card", "🕐 Timeline", "📊 Fit Score", "⚖️ Compare"])
else:
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📝 Summarise", "🔑 Key Points", "⚖️ Compare"])

# ── TAB 1: Chat ────────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.active_doc_id:
        st.markdown(f"""<div class='card' style='text-align:center;padding:4rem 2rem'>
            <div style='font-size:3.5rem;margin-bottom:1rem;animation:float 3s ease-in-out infinite;display:inline-block'>📂</div>
            <div style='color:{TEXT2};font-size:1rem;font-weight:500'>Upload a PDF in the sidebar to get started</div>
            <div style='color:{TEXT3};font-size:0.82rem;margin-top:0.5rem'>Resumes · Research papers · Articles · Reports</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Language-aware preset questions
        lang_note = f" (answer in {st.session_state.lang})" if st.session_state.lang != "English" else ""
        if current_display_mode == "resume":
            presets = [
                f"🛠 Top technical skills?{lang_note}", f"💼 Work experience summary?{lang_note}",
                f"🚀 Projects built?{lang_note}", f"🎓 Highest qualification?{lang_note}",
                f"✅ Fit for Python developer?{lang_note}", f"📅 Years of experience?{lang_note}",
            ]
        else:
            presets = [
                f"📌 What is this about?{lang_note}", f"🔍 Key findings?{lang_note}",
                f"🧠 Methodology used?{lang_note}", f"📊 Data & results?{lang_note}",
                f"💡 Main conclusions?{lang_note}", f"❓ Problem solved?{lang_note}",
            ]

        st.markdown("<div class='card-title'>Quick questions</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, q in enumerate(presets):
            if cols[i % 3].button(q, key=f"preset_{i}", use_container_width=True):
                st.session_state._preset_question = q

        # Follow-up questions
        if st.session_state.followups:
            st.markdown("<div class='card-title' style='margin-top:0.5rem'>💡 Suggested follow-ups</div>", unsafe_allow_html=True)
            fu_cols = st.columns(len(st.session_state.followups))
            for i, fq in enumerate(st.session_state.followups):
                if fu_cols[i].button(fq, key=f"fu_{i}_{fq[:10]}", use_container_width=True):
                    st.session_state._preset_question = fq

        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        last_idx = len(st.session_state.messages) - 1
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-user'><div class='bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
            else:
                # Typing animation only for the freshest assistant message
                if idx == last_idx and msg.get("_just_added"):
                    bubble_container = st.empty()
                    typing_effect(msg["content"], bubble_container, speed=0.006)
                    msg["_just_added"] = False  # only animate once
                else:
                    st.markdown(f"""<div class='chat-ai'>
                        <div class='avatar'>🧠</div>
                        <div class='bubble'>{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)
                if msg.get("sources"):
                    with st.expander(f"📎 {len(msg['sources'])} source chunks · click to see"):
                        for i, src in enumerate(msg["sources"], 1):
                            st.markdown(f"**Chunk {i} · Page {src['page']}** · score `{src['score']:.4f}`")
                            st.markdown(f"> {src['text'][:350]}{'...' if len(src['text'])>350 else ''}")

        preset_q = st.session_state.pop("_preset_question", None)
        lang_placeholder = {
            "Hindi": "इस दस्तावेज़ के बारे में कुछ भी पूछें...",
            "Spanish": "Pregunta cualquier cosa sobre este documento...",
            "French": "Posez n'importe quelle question sur ce document...",
            "German": "Stellen Sie beliebige Fragen zu diesem Dokument...",
        }.get(st.session_state.lang, "Ask anything about this document...")

        # ── Voice input ──
        voice_lang_map = {"English": "en-US", "Hindi": "hi-IN", "Spanish": "es-ES", "French": "fr-FR", "German": "de-DE"}
        with st.expander("🎤 Ask by voice instead of typing"):
            voice_input_widget(lang_code=voice_lang_map.get(st.session_state.lang, "en-US"), key="chat_voice")

        prompt = st.chat_input(lang_placeholder) or preset_q

        if prompt:
            lang_suffix = f"\n\nPlease respond in {st.session_state.lang}." if st.session_state.lang != "English" else ""
            full_question = prompt + lang_suffix

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                r = requests.post(f"{API_URL}/ask", json={
                    "doc_id": st.session_state.active_doc_id,
                    "question": full_question,
                    "chat_history": st.session_state.chat_history,
                    "mode": st.session_state.active_mode or "document",
                })
            if r.status_code == 200:
                data = r.json()
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": data["answer"]})
                st.session_state.messages.append({"role": "assistant", "content": data["answer"], "sources": data["sources"], "_just_added": True})
                st.session_state.followups = data.get("followup_questions", [])
            else:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {r.json().get('detail','Unknown error')}", "_just_added": True})
                st.session_state.followups = []
            st.rerun()

# ── RESUME TABS ────────────────────────────────────────────────────────────
if current_display_mode == "resume":

    # TAB 2: Parse
    with tab2:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a resume first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>Structured extraction · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            if st.button("⚡ Extract structured data"):
                with st.spinner("Parsing with LLM..."):
                    r = requests.post(f"{API_URL}/parse", json={"doc_id": st.session_state.active_doc_id})
                if r.status_code == 200:
                    parsed = r.json()["parsed"]
                    if "error" in parsed:
                        st.error(parsed["error"])
                    else:
                        col1, col2 = st.columns([1, 1], gap="large")
                        with col1:
                            st.markdown(f"""<div class='card'>
                                <div style='font-size:1.3rem;font-weight:700;color:{TEXT}'>{parsed.get('name','—')}</div>
                                <div style='color:{TEXT3};font-size:0.82rem;margin-top:6px'>
                                    {'📧 ' + parsed.get('email','') if parsed.get('email') else ''}
                                    {'&nbsp;&nbsp;📞 ' + parsed.get('phone','') if parsed.get('phone') else ''}
                                    {'&nbsp;&nbsp;📍 ' + parsed.get('location','') if parsed.get('location') else ''}
                                </div>
                                {f'<div style="margin-top:10px;color:{TEXT2};font-size:0.83rem;line-height:1.5">{parsed.get("summary","")}</div>' if parsed.get('summary') else ''}
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<div class='section-label'>Skills</div>", unsafe_allow_html=True)
                            skills_html = "".join(f"<span class='skill-badge'>{s}</span>" for s in parsed.get("skills", []))
                            st.markdown(f"<div class='skill-wrap'>{skills_html}</div>", unsafe_allow_html=True)

                            # Word Cloud
                            if parsed.get("skills"):
                                st.markdown("<div class='section-label'>🌤 Skill Word Cloud</div>", unsafe_allow_html=True)
                                wc_colors = ["#818cf8","#a78bfa","#38bdf8","#f472b6","#22c55e","#fb923c","#fbbf24"]
                                wc_html = "<div class='wordcloud-wrap'>"
                                for i, skill in enumerate(parsed.get("skills", [])):
                                    size = random.randint(12, 22)
                                    color = wc_colors[i % len(wc_colors)]
                                    opacity = random.uniform(0.7, 1.0)
                                    wc_html += f"<span class='wc-word' style='font-size:{size}px;color:{color};opacity:{opacity};background:{color}22;border:1px solid {color}44'>{skill}</span>"
                                wc_html += "</div>"
                                st.markdown(wc_html, unsafe_allow_html=True)

                            if parsed.get("certifications"):
                                st.markdown("<div class='section-label'>Certifications</div>", unsafe_allow_html=True)
                                for c in parsed["certifications"]:
                                    st.markdown(f"<div style='color:{TEXT2};font-size:0.83rem'>🏅 {c}</div>", unsafe_allow_html=True)

                        with col2:
                            if parsed.get("experience"):
                                st.markdown("<div class='section-label'>Experience</div>", unsafe_allow_html=True)
                                for exp in parsed["experience"]:
                                    st.markdown(f"""<div class='card' style='margin-bottom:8px;padding:1rem'>
                                        <div style='font-weight:600;color:{TEXT};font-size:0.88rem'>{exp.get('title','')}</div>
                                        <div style='color:#a78bfa;font-size:0.8rem'>{exp.get('company','')}</div>
                                        <div style='color:{TEXT3};font-size:0.76rem'>{exp.get('duration','')}</div>
                                        <div style='color:{TEXT2};font-size:0.8rem;margin-top:4px'>{exp.get('description','')}</div>
                                    </div>""", unsafe_allow_html=True)
                            if parsed.get("education"):
                                st.markdown("<div class='section-label'>Education</div>", unsafe_allow_html=True)
                                for edu in parsed["education"]:
                                    st.markdown(f"""<div class='card' style='padding:0.85rem 1rem;margin-bottom:6px'>
                                        <div style='font-weight:600;color:{TEXT};font-size:0.85rem'>{edu.get('degree','')}</div>
                                        <div style='color:{TEXT3};font-size:0.78rem'>{edu.get('institution','')} · {edu.get('year','')}</div>
                                    </div>""", unsafe_allow_html=True)
                            if parsed.get("projects"):
                                st.markdown("<div class='section-label'>Projects</div>", unsafe_allow_html=True)
                                for proj in parsed["projects"]:
                                    techs = "".join(f"<span class='skill-badge'>{t}</span>" for t in proj.get("technologies", []))
                                    st.markdown(f"""<div class='card' style='padding:0.85rem 1rem;margin-bottom:6px'>
                                        <div style='font-weight:600;color:{TEXT};font-size:0.85rem'>🚀 {proj.get('name','')}</div>
                                        <div style='color:{TEXT2};font-size:0.8rem;margin:4px 0'>{proj.get('description','')}</div>
                                        <div class='skill-wrap'>{techs}</div>
                                    </div>""", unsafe_allow_html=True)

                        # Export to PDF button
                        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
                        export_data = f"""# Resume: {parsed.get('name','Unknown')}
Email: {parsed.get('email','—')} | Phone: {parsed.get('phone','—')} | Location: {parsed.get('location','—')}

## Summary
{parsed.get('summary','—')}

## Skills
{', '.join(parsed.get('skills', []))}

## Experience
{''.join([f"- {e.get('title')} @ {e.get('company')} ({e.get('duration')}): {e.get('description')}" + chr(10) for e in parsed.get('experience',[])])}

## Education
{''.join([f"- {e.get('degree')} from {e.get('institution')} ({e.get('year')})" + chr(10) for e in parsed.get('education',[])])}

## Projects
{''.join([f"- {p.get('name')}: {p.get('description')}" + chr(10) for p in parsed.get('projects',[])])}
"""
                        st.download_button(
                            "📥 Export as Markdown Report",
                            data=export_data,
                            file_name=f"{parsed.get('name','resume').replace(' ','_')}_report.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                else:
                    st.error(r.json().get("detail", "Parse failed"))

    # TAB 3: Score Card
    with tab3:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a resume first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>AI Resume Score Card · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{TEXT2};font-size:0.85rem;margin-bottom:1rem'>Auto-rates your resume on 5 categories out of 10</div>", unsafe_allow_html=True)
            if st.button("⭐ Generate Score Card"):
                with st.spinner("Evaluating resume..."):
                    r = requests.post(f"{API_URL}/scorecard", json={"doc_id": st.session_state.active_doc_id})
                if r.status_code == 200:
                    sc = r.json()["scorecard"]
                    if "error" in sc:
                        st.error(sc["error"])
                    else:
                        categories = ["skills", "experience", "education", "projects", "overall"]
                        ring_colors = [ACCENT, ACCENT2, ACCENT3, "#f472b6", "#22c55e"]
                        cols = st.columns(5)

                        overall_score = sc.get("overall", {}).get("score", 0)
                        if overall_score >= 8:
                            st.session_state.show_confetti = True
                            st.success(f"🎉 Excellent resume! Score: {overall_score}/10")

                        for i, (cat, color) in enumerate(zip(categories, ring_colors)):
                            data = sc.get(cat, {})
                            score = data.get("score", 0)
                            comment = data.get("comment", "")
                            pct = score * 10
                            circumference = 2 * 3.14159 * 30
                            offset = circumference * (1 - pct / 100)

                            with cols[i]:
                                st.markdown(f"""
                                <div class='score-ring-wrap'>
                                    <div class='score-ring'>
                                        <svg width="80" height="80" viewBox="0 0 80 80">
                                            <circle class='ring-bg' cx="40" cy="40" r="30"/>
                                            <circle class='ring-fill' cx="40" cy="40" r="30"
                                                stroke="{color}"
                                                stroke-dasharray="{circumference}"
                                                stroke-dashoffset="{offset}"
                                                style="transform:rotate(-90deg);transform-origin:center;"/>
                                        </svg>
                                        <div class='ring-text' style='color:{color}'>{score}</div>
                                    </div>
                                    <div class='score-label-text'>{cat.upper()}</div>
                                    <div class='score-comment'>{comment}</div>
                                </div>""", unsafe_allow_html=True)
                        if st.session_state.show_confetti:
                            show_confetti()
                            st.session_state.show_confetti = False
                else:
                    st.error(r.json().get("detail", "Score card failed"))

    # TAB 4: Timeline
    with tab4:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a resume first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>Experience Timeline · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            if st.button("🕐 Generate Timeline"):
                with st.spinner("Building timeline..."):
                    r = requests.post(f"{API_URL}/parse", json={"doc_id": st.session_state.active_doc_id})
                if r.status_code == 200:
                    parsed = r.json()["parsed"]
                    experience = parsed.get("experience", [])
                    education = parsed.get("education", [])

                    if not experience and not education:
                        st.warning("No experience or education found in this resume.")
                    else:
                        st.markdown(f"<div class='section-label'>Work Experience</div>", unsafe_allow_html=True)
                        for i, exp in enumerate(experience):
                            is_last = i == len(experience) - 1
                            st.markdown(f"""
                            <div class='timeline-item'>
                                <div style='display:flex;flex-direction:column;align-items:center'>
                                    <div class='timeline-dot'></div>
                                    {"" if is_last else f"<div style='width:2px;flex:1;background:linear-gradient(180deg,{ACCENT}66,transparent);margin-top:4px'></div>"}
                                </div>
                                <div class='timeline-content'>
                                    <div class='timeline-title'>{exp.get('title','')}</div>
                                    <div class='timeline-company'>🏢 {exp.get('company','')}</div>
                                    <div class='timeline-date'>📅 {exp.get('duration','')}</div>
                                    <div class='timeline-desc'>{exp.get('description','')}</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                        if education:
                            st.markdown(f"<div class='section-label' style='margin-top:1.5rem'>Education</div>", unsafe_allow_html=True)
                            for i, edu in enumerate(education):
                                is_last = i == len(education) - 1
                                st.markdown(f"""
                                <div class='timeline-item'>
                                    <div style='display:flex;flex-direction:column;align-items:center'>
                                        <div class='timeline-dot' style='background:linear-gradient(135deg,{ACCENT3},#22c55e)'></div>
                                        {"" if is_last else f"<div style='width:2px;flex:1;background:linear-gradient(180deg,{ACCENT3}66,transparent);margin-top:4px'></div>"}
                                    </div>
                                    <div class='timeline-content'>
                                        <div class='timeline-title'>🎓 {edu.get('degree','')}</div>
                                        <div class='timeline-company'>{edu.get('institution','')}</div>
                                        <div class='timeline-date'>📅 {edu.get('year','')}</div>
                                    </div>
                                </div>""", unsafe_allow_html=True)
                else:
                    st.error("Could not generate timeline.")

    # TAB 5: Fit Score
    with tab5:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a resume first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>Job fit scoring · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            job_desc = st.text_area("jd", height=180, placeholder="Paste job description here...", label_visibility="collapsed")
            if st.button("📊 Score Fit") and job_desc:
                with st.spinner("Analysing fit..."):
                    r = requests.post(f"{API_URL}/fit", json={"doc_id": st.session_state.active_doc_id, "job_description": job_desc})
                if r.status_code == 200:
                    analysis = r.json()["analysis"]
                    score_match = re.search(r'\b([0-9]{1,3})\s*(?:/\s*100|out of 100)', analysis)
                    if score_match:
                        score = int(score_match.group(1))
                        color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
                        if score >= 80:
                            st.session_state.show_confetti = True
                            show_confetti()
                            st.session_state.show_confetti = False
                        st.markdown(f"""<div class='score-box'>
                            <div class='score-number-big' style='background:linear-gradient(135deg,{color},{color}aa);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>{score}</div>
                            <div class='score-label'>out of 100</div>
                        </div>""", unsafe_allow_html=True)
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(analysis)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(r.json().get("detail", "Fit scoring failed"))

    # TAB 6: Compare
    with tab6:
        all_docs = st.session_state.docs
        if len(all_docs) < 2:
            st.markdown(f"""<div class='card' style='text-align:center;padding:3rem'>
                <div style='font-size:2.5rem;margin-bottom:0.75rem'>⚖️</div>
                <div style='color:{TEXT2};font-size:0.88rem;font-weight:500'>Upload at least 2 resumes to compare</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div class='card-title'>Compare candidates</div>", unsafe_allow_html=True)
            role = st.text_input("role", placeholder="e.g. ML Engineer Intern", label_visibility="collapsed")
            selected = st.multiselect("sel", options=list(all_docs.keys()), default=list(all_docs.keys())[:2], label_visibility="collapsed")
            if st.button("⚡ Compare") and role and len(selected) >= 2:
                doc_ids = [all_docs[n]["doc_id"] for n in selected]
                with st.spinner("Comparing candidates..."):
                    r = requests.post(f"{API_URL}/compare", json={"doc_ids": doc_ids, "names": selected, "role": role})
                if r.status_code == 200:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(r.json()["analysis"])
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(r.json().get("detail", "Comparison failed"))

# ── DOCUMENT TABS ──────────────────────────────────────────────────────────
else:
    with tab2:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a document first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>Summarise · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            summary_type = st.radio("type", ["Short (3-5 sentences)", "Detailed (full overview)", "Bullet points"], horizontal=True, label_visibility="collapsed")
            if st.button("📝 Generate Summary"):
                prompts = {
                    "Short (3-5 sentences)": "Summarise this document in 3-5 concise sentences covering the main idea.",
                    "Detailed (full overview)": "Write a detailed summary covering background, methodology, findings, and conclusions.",
                    "Bullet points": "Summarise as clear bullet points covering all major sections and findings.",
                }
                lang_note = f" Respond in {st.session_state.lang}." if st.session_state.lang != "English" else ""
                with st.spinner("Summarising..."):
                    r = requests.post(f"{API_URL}/ask", json={
                        "doc_id": st.session_state.active_doc_id,
                        "question": prompts[summary_type] + lang_note, "chat_history": [], "mode": "document"})
                if r.status_code == 200:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(r.json()["answer"])
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(r.json().get("detail", "Summarisation failed"))

    with tab3:
        if not st.session_state.active_doc_id:
            st.markdown(f"<div class='card' style='text-align:center;padding:3rem;color:{TEXT2}'>Upload a document first</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='card-title'>Key points · {st.session_state.active_label}</div>", unsafe_allow_html=True)
            extract_type = st.radio("ext", [
                "🔑 Key concepts & definitions", "📊 Data, numbers & statistics",
                "✅ Conclusions & recommendations", "❓ Open questions & future work",
            ], label_visibility="collapsed")
            if st.button("🔑 Extract Key Points"):
                prompts = {
                    "🔑 Key concepts & definitions": "List all key concepts, terms, and definitions with brief explanations.",
                    "📊 Data, numbers & statistics": "Extract all important numbers, statistics, metrics, and data points.",
                    "✅ Conclusions & recommendations": "What are the main conclusions and recommendations?",
                    "❓ Open questions & future work": "What open questions, limitations, or future work are mentioned?",
                }
                lang_note = f" Respond in {st.session_state.lang}." if st.session_state.lang != "English" else ""
                with st.spinner("Extracting..."):
                    r = requests.post(f"{API_URL}/ask", json={
                        "doc_id": st.session_state.active_doc_id,
                        "question": prompts[extract_type] + lang_note, "chat_history": [], "mode": "document"})
                if r.status_code == 200:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(r.json()["answer"])
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(r.json().get("detail", "Extraction failed"))

    with tab4:
        all_docs = st.session_state.docs
        if len(all_docs) < 2:
            st.markdown(f"""<div class='card' style='text-align:center;padding:3rem'>
                <div style='font-size:2.5rem;margin-bottom:0.75rem'>⚖️</div>
                <div style='color:{TEXT2};font-size:0.88rem;font-weight:500'>Upload at least 2 documents to compare</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div class='card-title'>Compare documents</div>", unsafe_allow_html=True)
            topic = st.text_input("topic", placeholder="e.g. Compare methodologies and findings", label_visibility="collapsed")
            selected = st.multiselect("sel", options=list(all_docs.keys()), default=list(all_docs.keys())[:2], label_visibility="collapsed")
            if st.button("⚡ Compare") and topic and len(selected) >= 2:
                doc_ids = [all_docs[n]["doc_id"] for n in selected]
                with st.spinner("Comparing..."):
                    r = requests.post(f"{API_URL}/compare", json={"doc_ids": doc_ids, "names": selected, "role": topic})
                if r.status_code == 200:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(r.json()["analysis"])
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(r.json().get("detail", "Comparison failed"))