"""
Thème CSS de l'application — Dark / Light mode.

Contient tous les styles CSS pour l'ensemble de l'application.
Pour modifier l'apparence d'un composant, chercher la section correspondante.

Sections :
  - Variables (dark / light)
  - Tabs, Cards, Upload Hero
  - Pipeline Card, Steps Grid
  - Badges, Files, Buttons
  - Chat (messages, welcome, features)
  - Logs, Preview, Section Headers
  - Scrollbar, Divider, Stats
  - Validated files, Chat alignment
  - Success popup, Pulse animation
  - Visualization
"""

from __future__ import annotations

import streamlit as st


def inject_theme_css(dark: bool) -> None:
    """Injecte le CSS de thème selon le mode choisi."""

    if dark:
        css = """
<style>
:root {
  --bg-dark:     #212121;
  --bg-card:     #212121;
  --bg-card2:    #2f2f2f;
  --bg-card3:    #383838;
  --accent:      #10a37f;
  --accent2:     #10a37f;
  --accent3:     #ef4444;
  --text-main:   #ececec;
  --text-muted:  #b4b4b4;
  --border:      #303030;
  --radius:      14px;
  --shadow:      0 4px 24px rgba(0,0,0,0.2);
  --log-bg:      #212121;
  --log-border:  #383838;
  --log-text:    #ececec;
  --upload-bg:   rgba(16,163,127,0.06);
  --upload-border: rgba(16,163,127,0.25);
  --upload-hover: rgba(16,163,127,0.12);
  --glass-bg:    #212121;
  --glass-border: #303030;
}
.stApp {
  background: var(--bg-dark) !important;
  color: var(--text-main) !important;
}
.stApp * {
  color: var(--text-main);
}
section[data-testid="stSidebar"] { background: #171717 !important; border-right: none !important; }
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }
"""
    else:
        css = """
<style>
:root {
  --bg-dark:     #ffffff;
  --bg-card:     #ffffff;
  --bg-card2:    #f4f4f4;
  --bg-card3:    #e5e5e5;
  --accent:      #10a37f;
  --accent2:     #10a37f;
  --accent3:     #e05555;
  --text-main:   #0d0d0d;
  --text-muted:  #666666;
  --border:      #e5e5e5;
  --radius:      14px;
  --shadow:      0 4px 24px rgba(0,0,0,0.05);
  --log-bg:      #f4f4f4;
  --log-border:  #e5e5e5;
  --log-text:    #0d0d0d;
  --upload-bg:   #f9f9f9;
  --upload-border: #e5e5e5;
  --upload-hover: #f0f0f0;
  --glass-bg:    #ffffff;
  --glass-border: #e5e5e5;
  --test-light-mode: 1;
}
.stApp {
  background: var(--bg-dark) !important;
  color: var(--text-main) !important;
}
.stApp * {
  color: var(--text-main);
}
section[data-testid="stSidebar"] { background: #f9f9f9 !important; border-right: none !important; }
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }
.hero-upload { background: var(--bg-card) !important; }
.rag-card { background: var(--bg-card) !important; }
.file-item { background: var(--bg-card2) !important; }
.step-row  { background: var(--bg-card2) !important; }
.pipeline-card { background: var(--bg-card) !important; }
.chat-welcome { background: var(--bg-card) !important; }

"""

    light_overrides = ""
    if not dark:
        light_overrides = """
<style>
/* ── Light Mode Forçage de priorité maximale ─────────────────────────── */
.stApp header[data-testid="stHeader"], .stApp .stAppHeader, .stApp header {
  display: none !important;
  visibility: hidden !important;
}

.stApp div[data-testid="stChatInput"],
.stApp div[data-testid="stChatInput"] > div,
.stApp div[data-testid="stChatInput"] .stChatInputContainer {
  background-color: #f4f4f4 !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}
.stApp div[data-testid="stChatInput"] *,
.stApp div[data-testid="stChatInput"] textarea,
.stApp div[data-testid="stChatInput"] input {
  color: #000000 !important;
  background-color: transparent !important;
  caret-color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
}
.stApp div[data-testid="stChatInput"] textarea::placeholder {
  color: #666666 !important;
  opacity: 1 !important;
}
.stApp div[data-testid="stChatInputSubmitButton"] {
  background-color: transparent !important;
}

.stApp div[data-testid="stFileUploader"],
.stApp div[data-testid="stFileUploader"] > section,
.stApp section[data-testid="stFileUploadDropzone"] {
  background-color: #f3f4f6 !important;
}
.stApp div[data-testid="stFileUploader"] * {
  color: #374151 !important;
}
.stApp div[data-testid="stFileUploader"] button {
  background-color: transparent !important;
  border: 1px solid #d1d5db !important;
}
</style>
"""

    # ── Partie commune (indépendante du thème) ───────────────────────────
    common = """
/* ── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 6px;
  gap: 6px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  border-radius: 12px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.6rem 1.4rem;
  transition: all 0.25s ease;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--accent), #9b59f5) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(108,99,255,0.3);
}

/* ── CARDS ────────────────────────────────────────────────── */
.rag-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.2rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

/* ── UPLOAD HERO ─────────────────────────────────────────── */
.hero-upload {
  border: 2px dashed var(--upload-border);
  border-radius: 20px;
  padding: 2.5rem 2rem;
  margin-bottom: 2rem;
  text-align: center;
  background: var(--upload-bg);
  transition: all 0.3s ease;
  box-shadow: var(--shadow);
}
.hero-upload:hover {
  background: var(--upload-hover);
  border-color: var(--accent);
  box-shadow: 0 6px 30px rgba(108,99,255,0.2);
}
.hero-upload h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 0.3rem;
}
.hero-upload .hero-subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  margin: 0 0 0.8rem;
}
.hero-upload .hero-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
  filter: drop-shadow(0 2px 8px rgba(108,99,255,0.3));
}
.hero-upload .supported-types {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-top: 1rem;
}
.hero-upload .type-tag {
  background: rgba(108,99,255,0.1);
  color: var(--accent);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  border: 1px solid rgba(108,99,255,0.15);
}

/* ── PIPELINE CARD ───────────────────────────────────────── */
.pipeline-card {
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem 2.2rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}
.pipeline-card h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 0.4rem;
  text-align: center;
}
.pipeline-card .pipeline-subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

/* ── BADGES ──────────────────────────────────────────────── */
.badge { display:inline-block; padding:.25rem .7rem; border-radius:20px; font-size:.78rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }
.badge-green  { background:rgba(0,212,170,.15); color:#00a98f; border:1px solid rgba(0,212,170,.3);}
.badge-yellow { background:rgba(255,190,50,.15); color:#b8860b; border:1px solid rgba(255,190,50,.3);}
.badge-red    { background:rgba(255,107,107,.15); color:var(--accent3); border:1px solid rgba(255,107,107,.3);}
.badge-blue   { background:rgba(108,99,255,.15); color:var(--accent); border:1px solid rgba(108,99,255,.3);}

/* ── FILES ───────────────────────────────────────────────── */
.file-item {
  display: flex; align-items: center; gap: .7rem;
  border: 1px solid var(--border); border-radius: 12px;
  padding: .65rem 1rem; margin-bottom: .5rem;
  transition: all 0.25s ease;
}
.file-item:hover { border-color: var(--accent); transform: translateX(4px); }
.file-icon { font-size: 1.4rem; }
.file-name { font-weight: 600; flex: 1; color: var(--text-main); }
.file-size { color: var(--text-muted); font-size: .82rem; }
.file-type-tag {
  background: rgba(108,99,255,0.1); color: var(--accent);
  padding: 2px 8px; border-radius: 12px;
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
}

/* empty state */
.empty-state { text-align: center; padding: 3rem 2rem; border: 1px solid var(--border); border-radius: 16px; }
.empty-state .empty-icon { font-size: 3.5rem; margin-bottom: 1rem; opacity: 0.7; }
.empty-state .empty-text { color: var(--text-muted); font-size: 1rem; }

/* ── STEPS (rows) ───────────────────────────────────────── */
.step-row {
  display: flex; align-items: center; gap: 1rem;
  padding: .7rem 1.2rem; border-radius: 12px;
  margin-bottom: .5rem; border: 1px solid var(--border);
  transition: all 0.3s ease;
}
.step-row.active  { border-color: var(--accent); background: rgba(108,99,255,.08); box-shadow: 0 0 12px rgba(108,99,255,0.1); }
.step-row.done    { border-color: #00a98f; background: rgba(0,169,143,.06); }
.step-row.pending { opacity: 0.45; }
.step-num {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .85rem;
  background: var(--bg-card); border: 2px solid var(--border);
  flex-shrink: 0; transition: all 0.3s ease;
}
.step-row.active .step-num { background: var(--accent); border-color: var(--accent); color: white; box-shadow: 0 0 10px rgba(108,99,255,0.4); }
.step-row.done   .step-num { background: #00a98f; border-color: #00a98f; color: #fff; }
.step-label { font-weight: 600; flex: 1; }
.step-desc  { color: var(--text-muted); font-size: .82rem; }

/* ── BUTTONS ─────────────────────────────────────────────── */
div.stButton > button { font-weight: 600; border-radius: 10px; transition: all .2s; }
div.stButton > button[kind="secondary"] { background-color: var(--bg-card) !important; color: var(--text-main) !important; border: 1px solid var(--border) !important; }
div.stButton > button[kind="secondary"]:hover { border-color: var(--accent) !important; color: var(--accent) !important; }
div.stButton > button[kind="primary"] { background: linear-gradient(135deg, var(--accent), #9b59f5) !important; color: white !important; border: none !important; }
div.stButton > button[kind="primary"]:hover { box-shadow: 0 4px 15px rgba(108,99,255,0.4) !important; transform: translateY(-1px); }

/* Big launch button */
.launch-btn-wrap div.stButton > button[kind="primary"] {
  font-size: 1.25rem !important;
  padding: 1rem 2.5rem !important;
  border-radius: 16px !important;
  font-weight: 800 !important;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: linear-gradient(135deg, var(--accent), #9b59f5, #e040fb, var(--accent2)) !important;
  background-size: 300% 300% !important;
  animation: megaLaunch 2s ease-in-out infinite, gradientShift 4s ease infinite;
  box-shadow: 0 6px 30px rgba(108,99,255,0.4), 0 0 60px rgba(108,99,255,0.15) !important;
  position: relative;
  overflow: hidden;
}
.launch-btn-wrap div.stButton > button[kind="primary"]::before {
  content: '';
  position: absolute;
  top: -50%; left: -50%; width: 200%; height: 200%;
  background: conic-gradient(transparent, rgba(255,255,255,0.15), transparent 30%);
  animation: rotateSweep 3s linear infinite;
}
.launch-btn-wrap div.stButton > button[kind="primary"]:hover {
  box-shadow: 0 10px 40px rgba(108,99,255,0.6), 0 0 80px rgba(155,89,245,0.3) !important;
  transform: scale(1.06);
}
@keyframes megaLaunch {
  0%   { transform: scale(1);    box-shadow: 0 6px 30px rgba(108,99,255,0.4), 0 0 60px rgba(108,99,255,0.15); }
  25%  { transform: scale(1.07); box-shadow: 0 10px 40px rgba(108,99,255,0.55), 0 0 80px rgba(155,89,245,0.25); }
  50%  { transform: scale(0.97); box-shadow: 0 4px 20px rgba(108,99,255,0.3), 0 0 40px rgba(108,99,255,0.1); }
  75%  { transform: scale(1.05); box-shadow: 0 8px 35px rgba(108,99,255,0.5), 0 0 70px rgba(155,89,245,0.2); }
  100% { transform: scale(1);    box-shadow: 0 6px 30px rgba(108,99,255,0.4), 0 0 60px rgba(108,99,255,0.15); }
}
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes rotateSweep {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ── CHAT ────────────────────────────────────────────────── */
div[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 1rem 0 !important;
}

div[data-testid="stChatInput"] {
  border-radius: 24px !important;
  border: 1px solid var(--border) !important;
  background: var(--bg-card) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
  position: sticky !important;
  bottom: 0 !important;
  z-index: 1000 !important;
}
.stChatInputContainer, div[data-testid="stBottomBlockContainer"] {
  position: fixed !important;
  bottom: 0 !important;
  z-index: 9999 !important;
  padding-bottom: 2rem !important;
  background: var(--bg-dark) !important;
}
.chat-welcome {
  background: transparent !important;
  border: none !important;
  padding: 4rem 1rem 2rem; 
  text-align: center;
  margin-bottom: 2rem; 
  box-shadow: none !important;
}
.chat-welcome h1 {
  font-size: 2.5rem; 
  font-weight: 600;
  color: var(--text-main);
  background: none;
  -webkit-text-fill-color: var(--text-main);
  margin: 0 0 0.8rem;
  letter-spacing: -0.02em;
}
.chat-welcome .chat-subtitle { color: var(--text-muted); font-size: 1.1rem; }
.chat-feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 3rem; }
.chat-feature {
  border: 1px solid var(--border); 
  border-radius: 14px;
  padding: 1rem 1.2rem; 
  text-align: left; 
  background: transparent;
  transition: background 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}
.chat-feature:hover { 
  background: var(--bg-card2); 
  transform: translateY(-2px); 
  border-color: var(--border);
}
.chat-feature .feat-icon { font-size: 1.4rem; margin-bottom: 0.5rem; opacity: 0.8; }
.chat-feature .feat-title { font-weight: 600; font-size: 0.95rem; color: var(--text-main); display: block; }
.chat-feature .feat-desc { color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem; display: block; }

/* ── LOGS ────────────────────────────────────────────────── */
.log-box {
  background: var(--log-bg); border: 1px solid var(--log-border);
  border-radius: 12px; padding: 1.2rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: .78rem; color: var(--log-text);
  max-height: 320px; overflow-y: auto; white-space: pre-wrap; line-height: 1.7;
}

/* ── PREVIEW ─────────────────────────────────────────────── */
.preview-box { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: var(--bg-card2); }

/* ── SECTION HEADERS ─────────────────────────────────────── */
.section-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; }
.section-header h3 { margin: 0; font-weight: 700; font-size: 1.15rem; }
.section-header .section-count { background: rgba(108,99,255,0.12); color: var(--accent); padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; }

/* ── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #a0a8c0; border-radius: 4px; }

/* ── DIVIDER ─────────────────────────────────────────────── */
.custom-divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* Stats pills */
.stat-pill {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--bg-card2); border: 1px solid var(--border);
  border-radius: 20px; padding: 4px 12px;
  font-size: 0.82rem; font-weight: 600; margin-right: 8px;
}

/* ── VALIDATED FILE STATE ────────────────────────────────── */
.file-item.validated { border-color: #00a98f !important; background: rgba(0,169,143,0.06) !important; }
.file-item.validated .file-name::after { content: ' ✅'; font-size: 0.85rem; }
.validated-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(0,212,170,0.12); color: #00a98f;
  border: 1px solid rgba(0,212,170,0.3);
  border-radius: 20px; padding: 4px 14px;
  font-size: 0.82rem; font-weight: 700; letter-spacing: 0.03em;
}

/* ── STEPS GRID (Pipeline) ──────────────────────────────── */
.steps-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.step-card {
  border: 1px solid var(--border); border-radius: 14px;
  padding: 1.2rem 1rem; text-align: center;
  transition: all 0.3s ease; position: relative; overflow: hidden;
}
.step-card.active { border-color: var(--accent); background: rgba(108,99,255,0.08); box-shadow: 0 0 16px rgba(108,99,255,0.15); }
.step-card.done { border-color: #00a98f; background: rgba(0,169,143,0.06); }
.step-card.pending { opacity: 0.45; }
.step-card .step-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.step-card .step-num-badge {
  width: 28px; height: 28px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.8rem;
  background: var(--bg-card); border: 2px solid var(--border); margin-bottom: 0.6rem;
}
.step-card.active .step-num-badge { background: var(--accent); border-color: var(--accent); color: white; }
.step-card.done .step-num-badge { background: #00a98f; border-color: #00a98f; color: white; }
.step-card .step-card-label { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.3rem; }
.step-card .step-card-desc { color: var(--text-muted); font-size: 0.78rem; }

/* ── CHAT ALIGNMENT ─────────────────────────────────────── */
/* Assistant message (ChatGPT style: transparent background, flush left) */
div[data-testid="stChatMessage"]:has(.msg-marker-assistant) {
  margin-right: 0 !important; 
  margin-left: 0 !important;
  flex-direction: row !important;
  align-items: flex-start !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
div[data-testid="stChatMessage"]:has(.msg-marker-assistant) div[data-testid="stChatMessageAvatar"] {
  background-color: transparent !important;
  margin-right: 0.8rem;
  margin-top: 10px !important;
}
div[data-testid="stChatMessage"]:has(.msg-marker-assistant) * {
  color: var(--text-main) !important;
}

/* User message (Avatar on right, grey bubble for text) */
div[data-testid="stChatMessage"]:has(.msg-marker-user) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  margin-left: auto !important;
  margin-right: 0 !important;
  max-width: 85% !important;
  width: fit-content !important;
  align-self: flex-end !important;
  float: right !important;
  clear: both;
  flex-direction: row-reverse !important; /* Put avatar on the right */
  align-items: flex-start !important;
  padding: 0 !important;
}
/* User avatar */
div[data-testid="stChatMessage"]:has(.msg-marker-user) div[data-testid="stChatMessageAvatar"] {
  display: flex !important;
  margin-left: 0.8rem !important;
  margin-right: 0 !important;
  margin-top: 10px !important;
  background-color: transparent !important;
}
/* User text bubble */
div[data-testid="stChatMessage"]:has(.msg-marker-user) > div:not([data-testid="stChatMessageAvatar"]) {
  background: var(--bg-card2) !important;
  border-radius: 20px !important;
  border-top-right-radius: 4px !important;
  padding: 0.8rem 1.4rem !important;
  text-align: left !important;
}
div[data-testid="stChatMessage"]:has(.msg-marker-user) * { 
  color: var(--text-main) !important; 
}

/* Chat Input styling */
div[data-testid="stChatInput"] > div {
  background-color: var(--bg-card2) !important;
  border-color: var(--border) !important;
  border-radius: 9999px !important;
  box-shadow: none !important;
}
div[data-testid="stChatInput"] * {
  color: var(--text-main) !important;
}
div[data-testid="stChatInput"] textarea, div[data-testid="stChatInput"] input {
  background-color: transparent !important;
  color: var(--text-main) !important;
  caret-color: var(--text-main) !important;
  -webkit-text-fill-color: var(--text-main) !important;
}

/* Make Send Button transparent instead of dark */
div[data-testid="stChatInputSubmitButton"] {
  background-color: transparent !important;
}
div[data-testid="stChatInputSubmitButton"] * {
  color: var(--text-main) !important;
  fill: var(--text-main) !important;
}

/* File Uploader styling */
div[data-testid="stFileUploader"] > section[data-testid="stFileUploadDropzone"] {
  background-color: var(--upload-bg) !important;
  border: 2px dashed var(--upload-border) !important;
}
div[data-testid="stFileUploader"] * {
  color: var(--text-main) !important;
}
section[data-testid="stFileUploadDropzone"] {
  background-color: var(--upload-bg) !important;
}
section[data-testid="stFileUploadDropzone"] * {
  color: var(--text-main) !important;
}

/* Selectbox styling */
div[data-baseweb="select"] > div {
  background-color: var(--bg-card) !important;
  border-color: var(--border) !important;
}
div[data-baseweb="select"] span {
  color: var(--text-main) !important;
}
ul[data-baseweb="menu"] li {
  background-color: var(--bg-card) !important;
  color: var(--text-main) !important;
}
ul[data-baseweb="menu"] li:hover {
  background-color: var(--bg-card2) !important;
}

/* ── SUCCESS POPUP ──────────────────────────────────────── */
.success-popup-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(6px);
  z-index: 9999; display: flex; align-items: center; justify-content: center;
}
.success-popup {
  background: var(--bg-card); border: 2px solid #00a98f;
  border-radius: 24px; padding: 3rem 3.5rem; text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
  animation: popupIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  max-width: 500px;
}
@keyframes popupIn { 0% { transform: scale(0.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.success-popup .popup-icon { font-size: 4rem; margin-bottom: 1rem; }
.success-popup h2 {
  font-size: 1.6rem; font-weight: 800; margin: 0 0 0.5rem;
  background: linear-gradient(90deg, #00a98f, var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.success-popup p { color: var(--text-muted); margin-bottom: 1.5rem; }

/* ── SOURCES BLOCK ────────────────────────────────────────── */
.sources-container {
  margin-top: 1.2rem;
  padding: 1rem 1.2rem;
  background: rgba(16, 163, 127, 0.05);
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  font-size: 0.85rem;
}
.sources-title {
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.8rem;
}
.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.source-tag {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-weight: 600;
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
}
.source-tag:hover {
  border-color: var(--accent);
}

/* ── ANIMATIONS ─────────────────────────────────────────── */
@keyframes spin { 100% { transform: rotate(360deg); } }
.spin-icon {
  display: inline-block;
  animation: spin 1.5s linear infinite;
}

/* ── PULSE BUTTON ANIMATION ─────────────────────────────── */
@keyframes pulseBtn {
  0%   { transform: scale(1);    box-shadow: 0 6px 24px rgba(108,99,255,0.35); }
  30%  { transform: scale(1.06); box-shadow: 0 10px 36px rgba(108,99,255,0.55); }
  60%  { transform: scale(0.96); box-shadow: 0 4px 18px rgba(108,99,255,0.25); }
  100% { transform: scale(1);    box-shadow: 0 6px 24px rgba(108,99,255,0.35); }
}
.pulse-btn div.stButton > button[kind="primary"] {
  animation: pulseBtn 1.5s ease-in-out infinite, gradientShift 3s ease infinite !important;
}

/* ── VISUALIZATION ──────────────────────────────────────── */
.viz-card {
  border: 1px solid var(--border); border-radius: 16px;
  padding: 1.5rem; margin-bottom: 1rem;
  box-shadow: var(--shadow); transition: all 0.3s ease;
}
.viz-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.viz-card h3 { margin: 0 0 0.8rem; font-weight: 700; font-size: 1.05rem; }
.viz-stat { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
.viz-stat:last-child { border-bottom: none; }
.viz-stat-label { color: var(--text-muted); font-size: 0.88rem; }
.viz-stat-value { font-weight: 700; font-size: 0.95rem; color: var(--accent); }
</style>
"""
    st.markdown(css + common + light_overrides, unsafe_allow_html=True)
