import base64
import gzip
import hashlib
import hmac
import html as html_lib
import io
import json
import os
import zipfile
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, time as dt_time
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from email.utils import formatdate
from urllib.parse import parse_qs, quote, quote_plus, unquote, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup
from fpdf import FPDF
import pandas as pd
from pydantic import BaseModel, Field
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# DESIGN SYSTEM (theme, CSS & HTML components)
# ==========================================

APP_NAME = "Sales Hub"
APP_TAGLINE = "South Wales Telecoms · customers, calls & deals"

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0A0E1A;
  --surface: #111827;
  --surface-2: #161F33;
  --surface-3: #1C2740;
  --border: rgba(148, 163, 184, 0.14);
  --border-strong: rgba(148, 163, 184, 0.26);
  --text: #E7EAF3;
  --muted: #8C98B0;
  --faint: #5E6A82;
  --accent: #F0645A;
  --accent-2: #FDBA74;
  --accent-soft: rgba(240, 100, 90, 0.14);
  --good: #34D399;
  --warn: #FBBF24;
  --risk: #FB923C;
  --bad: #F87171;
  --radius: 14px;
  --grad: linear-gradient(135deg, #F0645A 0%, #FDBA74 100%);
}

html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}
.stApp {
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(253, 186, 116, 0.07), transparent 60%),
    radial-gradient(900px 500px at 10% -20%, rgba(240, 100, 90, 0.10), transparent 60%),
    var(--bg);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
footer { visibility: hidden; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; max-width: 1500px; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D1322 0%, #0A0E1A 100%);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 0.6rem; }
[data-testid="stSidebarUserContent"] { padding-top: 1rem; }

/* ---------- Typography ---------- */
h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; }
p, li, label, .stMarkdown { color: var(--text); }
[data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }
[data-testid="stWidgetLabel"] p {
  font-size: 0.76rem !important; font-weight: 600 !important; color: var(--muted) !important;
  text-transform: uppercase; letter-spacing: 0.06em;
}

/* ---------- Cards (bordered containers) ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]),
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: var(--radius) !important;
}
.st-key-card-queue { margin-top: 18px; }
.st-key-card-left, .st-key-card-select, .st-key-card-right, .st-key-card-login, .st-key-card-queue {
  background: linear-gradient(180deg, rgba(22, 31, 51, 0.85) 0%, rgba(17, 24, 39, 0.85) 100%);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius);
  padding: 22px 22px 18px 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 40px -24px rgba(0,0,0,0.6);
}

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 10px !important;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within, [data-baseweb="textarea"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color: var(--text) !important; }
[data-baseweb="input"] > div, [data-baseweb="base-input"] { background: transparent !important; }
textarea { font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important; line-height: 1.55 !important; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 10px !important; font-weight: 600 !important; padding: 0.55rem 1.1rem !important;
  border: 1px solid var(--border-strong) !important; background: var(--surface-2) !important;
  color: var(--text) !important; transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--accent) !important; color: #fff !important; transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"], .stFormSubmitButton > button,
[data-testid="stBaseButton-primary"] {
  background: var(--grad) !important; border: none !important; color: #0A0E1A !important;
  box-shadow: 0 8px 24px -10px rgba(240, 100, 90, 0.8);
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
  filter: brightness(1.08); color: #0A0E1A !important;
}
.stButton > button[kind="primary"] p, [data-testid="stBaseButton-primary"] p, .stFormSubmitButton > button p { color: #0A0E1A !important; font-weight: 700 !important; }

.stLinkButton a, [data-testid^="stBaseLinkButton"] {
  border-radius: 10px !important; font-weight: 700 !important; padding: 0.55rem 1.1rem !important;
}
[data-testid="stBaseLinkButton-primary"], .stLinkButton a[kind="primary"] {
  background: var(--grad) !important; border: none !important; color: #0A0E1A !important;
  box-shadow: 0 8px 24px -10px rgba(240, 100, 90, 0.8);
}
[data-testid="stBaseLinkButton-primary"] p, .stLinkButton a[kind="primary"] p { color: #0A0E1A !important; font-weight: 700 !important; }
[data-testid="stBaseLinkButton-primary"]:hover { filter: brightness(1.08); }

/* ---------- Tabs ---------- */
[data-testid="stTabs"] [role="tablist"], [data-baseweb="tab-list"] {
  gap: 4px; background: var(--surface); padding: 4px; border-radius: 12px; border: 1px solid var(--border);
}
[data-testid="stTabs"] [role="tab"], [data-baseweb="tab"] {
  border-radius: 9px !important; padding: 8px 16px !important; height: auto !important;
  color: var(--muted) !important; background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] { background: var(--surface-3) !important; color: var(--text) !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"], [data-testid="stTabs"] .react-aria-SelectionIndicator { display: none !important; }
[data-testid="stTabs"] [role="tab"] p { font-weight: 600; font-size: 0.86rem; }
[data-testid="stTabs"] [role="tablist"] { width: fit-content; margin-bottom: 6px; }

/* ---------- Table, expanders, alerts ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
[data-testid="stExpander"] details { background: var(--surface); border: 1px solid var(--border) !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary p { font-size: 0.85rem; color: var(--muted); font-weight: 600; }
[data-testid="stAlert"] { border-radius: 12px !important; border: 1px solid var(--border) !important; }
[data-testid="stCode"] pre, .stCode pre { background: var(--surface) !important; border: 1px solid var(--border); border-radius: 12px; }
hr { border-color: var(--border) !important; }

/* ================= Custom components ================= */
.pe-hero { display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap;
  padding: 6px 2px 22px 2px; margin-bottom: 18px; border-bottom: 1px solid var(--border); }
.pe-eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent-2); margin-bottom: 8px; }
.pe-eyebrow .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good); box-shadow: 0 0 0 4px rgba(52,211,153,.15); }
.pe-title { font-size: 2.05rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.1; margin: 0; color: var(--text); }
.pe-title span { background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent; }
.pe-sub { color: var(--muted); font-size: 0.95rem; margin-top: 8px; max-width: 620px; }

.pe-stepper { display: flex; align-items: center; gap: 6px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 6px; }
.pe-step { display: flex; align-items: center; gap: 8px; padding: 7px 14px 7px 7px; border-radius: 999px;
  font-size: 0.82rem; font-weight: 600; color: var(--faint); white-space: nowrap; }
.pe-step .num { width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; font-size: 0.72rem;
  font-weight: 700; border: 1px solid var(--border-strong); color: var(--faint); }
.pe-step.done { color: var(--muted); }
.pe-step.done .num { background: rgba(52,211,153,.14); border-color: rgba(52,211,153,.45); color: var(--good); }
.pe-step.active { background: var(--surface-3); color: var(--text); }
.pe-step.active .num { background: var(--grad); border: none; color: #0A0E1A; }
.pe-step-sep { width: 14px; height: 1px; background: var(--border-strong); }

.pe-section { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.pe-section .badge { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
  background: var(--accent-soft); color: var(--accent); font-weight: 800; font-size: 0.85rem; border: 1px solid rgba(240, 100, 90,.3); }
.pe-section .t { font-size: 1.08rem; font-weight: 700; color: var(--text); line-height: 1.2; }
.pe-section .s { font-size: 0.82rem; color: var(--muted); margin-top: 2px; }

.pe-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.pe-chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 0.76rem;
  font-weight: 600; background: var(--surface-3); color: var(--text); border: 1px solid var(--border); white-space: nowrap; }
.pe-chip.accent { background: var(--accent-soft); color: #B9BDFF; border-color: rgba(240, 100, 90,.3); }
.pe-chip.good { background: rgba(52,211,153,.12); color: var(--good); border-color: rgba(52,211,153,.3); }
.pe-chip.warn { background: rgba(251,191,36,.12); color: var(--warn); border-color: rgba(251,191,36,.3); }
.pe-chip.risk { background: rgba(251,146,60,.12); color: var(--risk); border-color: rgba(251,146,60,.3); }
.pe-chip.bad { background: rgba(248,113,113,.12); color: var(--bad); border-color: rgba(248,113,113,.3); }
.pe-chip.muted { background: transparent; color: var(--muted); }

.pe-vertical { display: flex; gap: 14px; align-items: flex-start; background: var(--surface); border: 1px dashed var(--border-strong);
  border-radius: 12px; padding: 12px 14px; margin: 2px 0 14px 0; }
.pe-vertical .lbl { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--faint); margin-bottom: 6px; }

.pe-kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 4px 0 14px 0; }
.pe-kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.pe-kpi .v { font-size: 1.35rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
.pe-kpi .l { font-size: 0.72rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }

.pe-selected { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--accent-soft);
  border: 1px solid rgba(240, 100, 90,.35); border-radius: 12px; padding: 12px 14px; margin: 14px 0 10px 0; }
.pe-selected .n { font-weight: 700; color: var(--text); }
.pe-selected .m { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
.pe-hint { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 0.86rem; background: var(--surface);
  border: 1px dashed var(--border-strong); border-radius: 12px; padding: 12px 14px; margin-top: 12px; }

.pe-empty { text-align: center; padding: 48px 24px 40px 24px; }
.pe-empty .t { font-size: 1.1rem; font-weight: 700; color: var(--text); margin-top: 14px; }
.pe-empty .s { font-size: 0.88rem; color: var(--muted); margin: 6px auto 20px auto; max-width: 360px; line-height: 1.5; }
.pe-empty ol { text-align: left; display: inline-block; margin: 0 auto; padding: 0; list-style: none; counter-reset: s; }
.pe-empty li { counter-increment: s; color: var(--muted); font-size: 0.86rem; margin: 8px 0; display: flex; align-items: center; gap: 10px; }
.pe-empty li::before { content: counter(s); width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  background: var(--surface-3); border: 1px solid var(--border-strong); font-size: 0.72rem; font-weight: 700; color: var(--text); }

.pe-firm { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 14px; }
.pe-firm .name { font-size: 1.35rem; font-weight: 800; letter-spacing: -0.025em; color: var(--text); line-height: 1.2; }
.pe-firm .meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.pe-firm .blurb { color: var(--muted); font-size: 0.86rem; line-height: 1.5; margin-top: 10px; font-style: italic; }

.pe-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
@media (max-width: 1100px) { .pe-grid2 { grid-template-columns: 1fr; } .pe-kpis { grid-template-columns: 1fr 1fr 1fr; } }
.pe-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px; }
.pe-cols { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 0 18px; }
@media (max-width: 1250px) { .pe-cols { grid-template-columns: 1fr; } }
.pe-hook { margin-bottom: 10px; }
.pe-panel .h { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--faint); margin-bottom: 10px; }

.pe-contact { display: flex; align-items: center; gap: 12px; }
.pe-avatar { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-weight: 800; font-size: 0.95rem;
  background: var(--grad); color: #0A0E1A; flex-shrink: 0; }
.pe-contact .n { font-weight: 700; font-size: 1.02rem; color: var(--text); }
.pe-contact .r { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }

.pe-row { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-top: 1px solid var(--border); font-size: 0.86rem; }
.pe-row:first-of-type { border-top: none; }
.pe-row svg { color: var(--accent-2); flex-shrink: 0; }
.pe-row a, .pe-row span { color: var(--text) !important; text-decoration: none; overflow-wrap: anywhere; }
.pe-row .tag { color: var(--faint) !important; white-space: nowrap; }
.pe-row a.trunc { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; overflow-wrap: normal; }
.pe-row a:hover { color: var(--accent-2) !important; }
.pe-row .tag { margin-left: auto; font-size: 0.68rem; color: var(--faint); font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
.pe-none { color: var(--faint); font-size: 0.84rem; font-style: italic; }

.pe-officer { display: flex; justify-content: space-between; gap: 8px; padding: 6px 0; border-top: 1px solid var(--border); font-size: 0.84rem; }
.pe-officer:first-of-type { border-top: none; }
.pe-officer .who { color: var(--text); font-weight: 600; }
.pe-officer .since { color: var(--faint); font-size: 0.76rem; white-space: nowrap; }

.pe-hook { background: linear-gradient(135deg, rgba(240, 100, 90,.12), rgba(253, 186, 116,.06)); border: 1px solid rgba(240, 100, 90,.28);
  border-radius: 12px; padding: 14px 16px; }
.pe-hook .h { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #B9BDFF; }
.pe-hook .t { font-weight: 700; color: var(--text); margin: 4px 0 10px 0; }
.pe-hook ul { margin: 0; padding-left: 0; list-style: none; }
.pe-hook li { font-size: 0.85rem; color: var(--text); padding: 4px 0 4px 24px; position: relative; }
.pe-hook li::before { content: ""; position: absolute; left: 4px; top: 10px; width: 8px; height: 8px; border-radius: 50%; background: var(--grad); }

/* Workspace switch in sidebar */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; margin-bottom: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 9px 12px !important; margin: 0 !important; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { border-color: rgba(240, 100, 90,.55); background: var(--accent-soft); }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-weight: 600 !important; font-size: .88rem !important; color: var(--text) !important;
  text-transform: none !important; letter-spacing: 0 !important; }
/* LinkedIn panel */
.st-key-card-linkedin { background: var(--surface); border: 1px solid rgba(10,102,194,.45) !important; border-radius: 12px;
  padding: 14px 14px 10px 14px; margin-bottom: 10px; }
.li-head { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.li-head .t { font-weight: 700; color: var(--text); font-size: .95rem; }
.li-head .s { font-size: .8rem; color: var(--muted); margin-top: 1px; }
.li-badge { width: 30px; height: 30px; border-radius: 7px; background: #0A66C2; color: #fff; font-weight: 800; font-size: .95rem;
  display: grid; place-items: center; flex-shrink: 0; font-family: Arial, sans-serif; }
.li-mini { width: 15px; height: 15px; border-radius: 3px; background: #0A66C2; color: #fff; font-weight: 800; font-size: .62rem;
  display: grid; place-items: center; flex-shrink: 0; font-family: Arial, sans-serif; }
/* Sidebar components */
.pe-brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 18px 0; border-bottom: 1px solid var(--border); margin-bottom: 16px; }
.pe-logo { width: 40px; height: 40px; border-radius: 12px; background: var(--grad); display: grid; place-items: center; color: #0A0E1A;
  box-shadow: 0 10px 24px -10px rgba(240, 100, 90,.9); }
.pe-brand .n { font-weight: 800; font-size: 1.05rem; color: var(--text); letter-spacing: -0.02em; }
.pe-brand .s { font-size: 0.75rem; color: var(--muted); }
.pe-side-h { font-size: 0.68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--faint); margin: 18px 0 8px 0; }
.pe-status { display: flex; align-items: center; justify-content: space-between; font-size: 0.84rem; color: var(--text); padding: 7px 0; }
.pe-status .st { display: inline-flex; align-items: center; gap: 6px; font-size: 0.76rem; font-weight: 600; }
.pe-status .st.ok { color: var(--good); } .pe-status .st.off { color: var(--bad); } .pe-status .st.idle { color: var(--muted); }
.pe-status .st::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.pe-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.pe-stat { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 10px; text-align: center; }
.pe-stat .v { font-weight: 800; font-size: 1.1rem; color: var(--text); }
.pe-stat .l { font-size: 0.64rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; font-weight: 600; margin-top: 2px; }

/* Login */
.pe-login-head { text-align: center; margin: 8vh 0 22px 0; }
.pe-login-head .pe-logo { width: 54px; height: 54px; margin: 0 auto 16px auto; border-radius: 16px; }
.pe-login-head .t { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: var(--text); }
.pe-login-head .s { color: var(--muted); font-size: 0.92rem; margin-top: 6px; }
</style>
"""

_ICON_PATHS = {
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "pointer": '<path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/>',
}


def _full_width_kwargs() -> Dict[str, Any]:
    """Full-width buttons: 'width' on Streamlit 1.46+, 'use_container_width' before that."""
    import inspect
    try:
        if "width" in inspect.signature(st.button).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


FULL_WIDTH = _full_width_kwargs()


def icon(name: str, size: int = 16, stroke: float = 2) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        f' stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{_ICON_PATHS[name]}</svg>'
    )


def esc(value: Any) -> str:
    """Escapes scraped/registry text before it goes into HTML."""
    return html_lib.escape(str(value if value is not None else ""), quote=True)


def render_html(markup: str, target=None) -> None:
    """Renders HTML via markdown. Lines are flattened so markdown never treats indentation as code."""
    flat = "".join(line.strip() for line in markup.splitlines())
    (target or st).markdown(flat, unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def chip(text: str, tone: str = "") -> str:
    return f'<span class="pe-chip {tone}">{esc(text)}</span>'


def section_header(num: str, title: str, subtitle: str = "") -> None:
    render_html(
        f'<div class="pe-section"><div class="badge">{num}</div><div>'
        f'<div class="t">{esc(title)}</div>'
        + (f'<div class="s">{esc(subtitle)}</div>' if subtitle else "")
        + "</div></div>"
    )


def hero_html(active_step: int) -> str:
    steps = ["Target", "Select", "Enrich", "Pitch"]
    parts = []
    for i, label in enumerate(steps, start=1):
        state = "done" if i < active_step else "active" if i == active_step else ""
        num = icon("check", 12, 3) if state == "done" else str(i)
        parts.append(f'<div class="pe-step {state}"><span class="num">{num}</span>{label}</div>')
    stepper = '<div class="pe-step-sep"></div>'.join(parts)
    return (
        '<div class="pe-hero"><div>'
        '<div class="pe-eyebrow"><span class="dot"></span>Live UK registry · Open web intelligence</div>'
        '<div class="pe-title">Prospect Discovery <span>&amp; Dossier Engine</span></div>'
        '<div class="pe-sub">Find active UK firms by sector, surface the decision-maker and their'
        ' direct channels, then generate a CRM-integration pitch and a one-page dossier.</div>'
        f'</div><div class="pe-stepper">{stepper}</div></div>'
    )


def confidence_chip(confidence: Optional[str]) -> str:
    tones = {
        "High": ("good", "High-confidence match"),
        "Medium": ("warn", "Medium-confidence match"),
        "Low": ("risk", "Low-confidence match"),
        "Manual": ("accent", "Website entered manually"),
    }
    tone, label = tones.get(confidence or "", ("bad", "Website not found"))
    return chip(label, tone)


def display_officer_name(raw: str) -> str:
    """'BYWATER, Paul James' -> 'Paul James Bywater'; company officers are just title-cased."""
    if "," in raw:
        surname, forenames = raw.split(",", 1)
        return f"{forenames.strip().title()} {surname.strip().title()}".strip()
    return raw.title()


def initials(name: str) -> str:
    words = [w for w in re.split(r"[\s&/]+", name or "") if w and w[0].isalpha()]
    return ("".join(w[0] for w in words[:2]) or "?").upper()


# ==========================================
# 0. PASSWORD GATEWAY (STREAMLIT SECRETS)
# ==========================================


def quick_add_logins() -> List[Tuple[str, str]]:
    """Quick add passwords from Secrets: QUICK_ADD_PASSWORD (shared), and/or [QUICK_ADD_USERS] name = "password"."""
    out: List[Tuple[str, str]] = []
    try:
        shared = st.secrets.get("QUICK_ADD_PASSWORD")
        if shared:
            out.append(("", str(shared)))
        users = st.secrets.get("QUICK_ADD_USERS") or {}
        out += [(str(k), str(v)) for k, v in dict(users).items() if v]
    except Exception:
        pass
    return out


def check_password() -> bool:
    # Fail CLOSED: if the secret is missing or misconfigured, nobody gets in.
    try:
        configured_password = st.secrets["APP_PASSWORD"]
    except Exception:
        configured_password = None
    if not configured_password:
        st.set_page_config(page_title=f"{APP_NAME} · Locked", page_icon="🎯", layout="centered")
        inject_css()
        render_html(
            f'<div class="pe-login-head"><div class="pe-logo">{icon("lock", 24, 2.2)}</div>'
            '<div class="t">App locked</div>'
            '<div class="s">APP_PASSWORD isn\'t set in Streamlit Secrets, so access is blocked.</div></div>'
        )
        st.error("Add APP_PASSWORD under App settings → Secrets, then reload.")
        return False

    def password_entered():
        typed = st.session_state.get("password", "").encode("utf-8")
        role, who = None, ""
        if hmac.compare_digest(typed, str(configured_password).encode("utf-8")):
            role = "full"
        if not role:  # Named logins: [HUB_USERS] Name = "password" in Secrets; their name goes on every call they log
            try:
                for name, pw in dict(st.secrets.get("HUB_USERS") or {}).items():
                    if pw and hmac.compare_digest(typed, str(pw).encode("utf-8")):
                        role, who = "full", str(name)
                        st.session_state["hub_user"] = str(name)
                        break
            except Exception:
                pass
        if not role:  # Telemarketers: their own password opens Quick add only
            for name, pw in quick_add_logins():
                if pw and hmac.compare_digest(typed, pw.encode("utf-8")):
                    role, who = "quick", name
                    break
        if role:
            st.session_state["password_correct"] = True
            st.session_state["role"], st.session_state["quick_user"] = role, who
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.set_page_config(page_title=f"{APP_NAME} · Sign in", page_icon="🎯", layout="centered")
    inject_css()
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        render_html(
            f'<div class="pe-login-head"><div class="pe-logo">{icon("target", 26, 2.2)}</div>'
            f'<div class="t">{APP_NAME}</div>'
            f'<div class="s">{APP_TAGLINE} · Authorised users only</div></div>'
        )
        with st.container(key="card-login"):
            with st.form("Credentials", border=False):
                st.text_input("Access password", type="password", key="password",
                              placeholder="Enter your password")
                st.form_submit_button("Sign in", on_click=password_entered,
                                      type="primary", **FULL_WIDTH)
            if (
                "password_correct" in st.session_state
                and not st.session_state["password_correct"]
            ):
                st.error("Incorrect password. Please try again.")

    return False


if not check_password():
    st.stop()

# ==========================================
# 1. VERTICALS, CRMS & PITCH PLAYBOOKS
# ==========================================

VERTICAL_PRESETS = {
    "Estate & Lettings Agents": {
        "sic_codes": ["68310"],
        "description": "Real estate agencies & letting operations",
        "search_hint": "Estate Agents",
        "crms": ["Street", "Alto", "Reapit", "Dezrez", "Jupix"],
        "primary_hook": "CRM Integration (Street / Alto / Reapit)",
        "fallback_greeting": "Lettings & Sales Team",
        "pitch_bullets": [
            "Screen pop-up of every client or landlord record the moment they call",
            "Automatic voice recording syncing directly to the property file",
            "Click to dial directly inside your CRM / property portal",
            "Every lead, missed call & call note tracked automatically",
        ],
        "default_cta": "Let me know how many phones or softphone users you have, and I'll send over a quote.",
    },
    "Dental Practices": {
        "sic_codes": ["86230"],
        "description": "Dental practice activities",
        "search_hint": "Dental Practice",
        "crms": ["Dentally", "EXACT", "Carestream R4"],
        "primary_hook": "PMS Integration (Dentally / EXACT / R4)",
        "fallback_greeting": "Practice Manager",
        "pitch_bullets": [
            "Patient records pop up on reception screens when the phone rings",
            "Calls log automatically against the right patient chart",
            "Missed calls are flagged instantly for follow up and recall retention",
            "Call recordings are stored compliantly against the patient file",
        ],
        "default_cta": "How many handsets does the practice currently use? I can send over a no obligation quote.",
    },
    "Solicitors & Legal Practices": {
        "sic_codes": ["69102"],
        "description": "Solicitors & legal service providers",
        "search_hint": "Solicitors",
        "crms": ["Clio", "LEAP", "Proclaim", "Actionstep"],
        "primary_hook": "Matter Management Integration (Clio / LEAP)",
        "fallback_greeting": "Practice Manager",
        "pitch_bullets": [
            "Dial straight from the active client or matter record",
            "Mobile & desktop softphone app so fee earners can take calls securely anywhere",
            "One unified system across reception, every fee earner and all branch offices",
            "Call recordings & billable duration synced back to the matter file",
        ],
        "default_cta": "Let me know which system you run and roughly how many users you have, and I'll send over a quote.",
    },
    "Accountants & Auditors": {
        "sic_codes": ["69201"],
        "description": "Accounting, bookkeeping & tax consultancy",
        "search_hint": "Accountants",
        "crms": ["Iris", "CCH", "TaxCalc", "Xero Practice Manager"],
        "primary_hook": "Client Portal & Time Tracking Integration",
        "fallback_greeting": "Practice Partner",
        "pitch_bullets": [
            "Client identification card pops on screen the moment they call",
            "Automatic call logging against client tax and year-end audit folders",
            "Seamless transfer between desk phones and laptop softphones for hybrid staff",
            "Consolidated line rental and cloud voice to reduce fixed telecom overheads",
        ],
        "default_cta": "Let me know your approximate team size and I can send over an indicative quote.",
    },
    "General Medical Clinics": {
        "sic_codes": ["86210"],
        "description": "General medical practice activities",
        "search_hint": "Clinic",
        "crms": ["EMIS Web", "SystmOne", "Semble", "Heydoc"],
        "primary_hook": "Clinical System Integration & Triage Routing",
        "fallback_greeting": "Clinic Manager",
        "pitch_bullets": [
            "Patient record screen-pop to accelerate inbound triage",
            "Automated call queueing & peak-time patient callback features",
            "Encrypted, compliant voice recordings stored per patient file",
            "Direct transfer lines between triage staff, clinicians, and administration",
        ],
        "default_cta": "How many lines or handsets do you operate? I can send over a no obligation overview.",
    },
}


class OfficerInfo(BaseModel):
    name: str
    role: str  # Friendly label, e.g. "Director"
    raw_role: str = ""  # Companies House value, e.g. "llp-designated-member"
    appointed_on: Optional[str] = None
    is_owner: bool = False  # Also a Person with Significant Control


class ScrapedLead(BaseModel):
    company_name: str
    company_number: Optional[str] = None
    sic_codes: List[str] = Field(default_factory=list)
    sector_guess: str = "General B2B"
    registered_address: Optional[str] = None
    website_url: Optional[str] = None
    phones_found: List[str] = Field(default_factory=list)
    emails_found: List[str] = Field(default_factory=list)
    officers: List[OfficerInfo] = Field(default_factory=list)
    site_meta_description: Optional[str] = None
    trading_name: Optional[str] = None  # From Google Maps, e.g. "J Dent Dental Care"
    contact_name: Optional[str] = None  # Added by a person after checking LinkedIn etc.
    contact_role: Optional[str] = None
    contact_email: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_confidence: Optional[str] = None  # High / Medium / Low / Manual
    website_reasons: List[str] = Field(default_factory=list)
    discovery_notes: List[str] = Field(default_factory=list)
    other_emails: List[str] = Field(default_factory=list)  # Third-party addresses (agencies, regulators)
    pages_checked: List[str] = Field(default_factory=list)


# ==========================================
# 2. ENRICHMENT & SCRAPING ENGINE
# ==========================================


# ------------------------------------------------------------------
# Web discovery & extraction helpers
# ------------------------------------------------------------------

LEGAL_SUFFIX_WORDS = {
    "LTD", "LIMITED", "PLC", "LLP", "LP", "GROUP", "HOLDINGS", "UK", "(UK)",
    "CO", "COMPANY", "THE", "T/A", "INTERNATIONAL",
}

# Words too common to identify a firm on their own (kept for the full-name match)
GENERIC_NAME_WORDS = {
    "and", "the", "of", "dental", "dentist", "dentists", "practice", "practices",
    "surgery", "clinic", "clinics", "medical", "health", "healthcare", "care",
    "solicitors", "solicitor", "law", "legal", "lawyers", "partners", "partnership",
    "accountants", "accountancy", "accounting", "tax", "bookkeeping", "associates",
    "estate", "estates", "agents", "agency", "lettings", "letting", "property",
    "properties", "residential", "sales", "services", "consultants", "consultancy",
    "management", "uk", "ltd", "limited", "llp", "plc", "group", "holdings", "co",
}

# Directories, portals, social media, regulators and review sites — never a firm's own site.
BLOCKED_DOMAINS = {
    "company-information.service.gov.uk", "gov.uk", "companieshouse.gov.uk",
    "endole.co.uk", "duedil.com", "opencorporates.com", "companycheck.co.uk",
    "checkcompany.co.uk", "companiesintheuk.co.uk", "bizdb.co.uk", "companieslist.co.uk",
    "company-data.co.uk", "ukcompanieslist.com", "find-and-update.company-information.service.gov.uk",
    "linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "youtube.com", "tiktok.com", "pinterest.com", "wikipedia.org",
    "yell.com", "thomsonlocal.com", "scoot.co.uk", "192.com", "cylex-uk.co.uk",
    "freeindex.co.uk", "hotfrog.co.uk", "yelp.co.uk", "yelp.com", "trustpilot.com",
    "google.com", "google.co.uk", "bing.com", "duckduckgo.com", "maps.apple.com",
    "rightmove.co.uk", "zoopla.co.uk", "onthemarket.com", "primelocation.com",
    "allagents.co.uk", "getagent.co.uk", "homipi.co.uk", "propertymark.co.uk",
    "whatclinic.com", "doctify.com", "topdoctors.co.uk", "cqc.org.uk", "gdc-uk.org",
    "lawsociety.org.uk", "solicitors.lawsociety.org.uk", "sra.org.uk",
    "reviewsolicitors.co.uk", "solicitors.guru", "icaew.com", "accaglobal.com",
    "checkatrade.com", "ratedpeople.com", "bark.com", "mybuilder.com",
    "indeed.com", "indeed.co.uk", "glassdoor.co.uk", "reed.co.uk", "totaljobs.com",
    "zoominfo.com", "rocketreach.co", "apollo.io", "dnb.com", "kompass.com",
    "crunchbase.com", "bloomberg.com", "misterwhat.co.uk", "brownbook.net",
    "fyple.co.uk", "opendi.co.uk", "tuugo.co.uk", "infobel.com", "cybo.com",
    "n49.com", "businessmagnet.co.uk", "streetcheck.co.uk", "amazon.co.uk",
    "ebay.co.uk", "gumtree.com", "tripadvisor.co.uk", "118118.com", "ukphonebook.com",
}
# Blocked only as the exact domain (their subdomains can be real practice sites, e.g. xyzsurgery.nhs.uk)
BLOCKED_EXACT_ONLY = {"nhs.uk"}

FREE_MAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "hotmail.com", "hotmail.co.uk", "outlook.com",
    "live.co.uk", "live.com", "yahoo.com", "yahoo.co.uk", "btinternet.com",
    "btconnect.com", "icloud.com", "me.com", "aol.com", "sky.com", "virginmedia.com",
    "talktalk.net", "nhs.net",
}

# Link hints for pages worth scraping, most useful first
CONTACT_PAGE_HINTS = [
    "contact", "get-in-touch", "get in touch", "getintouch", "find-us", "find us",
    "our-team", "our team", "meet-the-team", "meet the team", "team", "our-people",
    "people", "branches", "offices", "about",
]

JUNK_EMAIL_MARKERS = (
    "example.", "sentry", "wixpress", "domain.com", "yourname", "youremail",
    "email.com", "@2x", "noreply", "no-reply", "donotreply", "u003e", "godaddy",
    "wordpress", "schema.org", "@sentry", "@ingest", "test@",
)
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+'-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,24}")
PHONE_TEXT_RE = re.compile(
    r"(?:\+\s?44\s?(?:\(0\)\s?)?|0044\s?|\(?0)\d[\d \-\(\)]{7,14}\d"
)


def domain_of(url: str) -> Optional[str]:
    if not url:
        return None
    if "://" not in url:
        url = "https://" + url
    host = (urlparse(url).hostname or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host or None


FOREIGN_OK_TLDS = {"uk", "co", "io", "me", "ai", "tv", "eu", "ly", "fm", "cc"}
BLOCKED_DOMAINS |= {
    "zhihu.com", "baidu.com", "quora.com", "reddit.com", "medium.com", "weibo.com", "bilibili.com", "vk.com",
    "naver.com", "yahoo.com", "msn.com", "imdb.com", "booking.com", "expedia.co.uk", "trivago.co.uk",
    "github.com", "apple.com", "microsoft.com", "wikimedia.org", "wiktionary.org", "britannica.com",
    "find-open.co.uk", "yably.co.uk", "locallife.co.uk", "companieshousedata.co.uk", "ukbusinessforums.co.uk",
    "bizstats.co.uk", "companydatashop.com", "checkcompany.uk", "find-and-update.company-information.service.gov.uk",
}


def is_blocked_domain(domain: str) -> bool:
    domain = domain.lower()
    if domain in BLOCKED_EXACT_ONLY:
        return True
    tld = domain.rsplit(".", 1)[-1]
    if len(tld) == 2 and tld not in FOREIGN_OK_TLDS:
        return True  # Another country's site (.cn, .de, .ru…): never a UK firm's own website
    return any(domain == b or domain.endswith("." + b) for b in BLOCKED_DOMAINS)


def domain_label(domain: str) -> str:
    """'www.hart-new-homes.co.uk' -> 'hartnewhomes'"""
    parts = domain.lower().split(".")
    for suffix_len in (3, 2, 1):  # handles .co.uk, .org.uk, .com etc
        tail = ".".join(parts[-suffix_len:])
        if tail in {"co.uk", "org.uk", "me.uk", "ltd.uk", "plc.uk", "nhs.uk", "net.uk"} and len(parts) > 2:
            return re.sub(r"[^a-z0-9]", "", parts[-3])
    return re.sub(r"[^a-z0-9]", "", parts[-2] if len(parts) >= 2 else parts[0])


def distinctive_name_tokens(company_name: str) -> List[str]:
    """'HART NEW HOMES (WALSALL) LIMITED' -> ['hart', 'new', 'homes', 'walsall']"""
    words = re.sub(r"[^a-z0-9 ]", " ", company_name.lower().replace("&", " and ")).split()
    words = [w for w in words if w.upper() not in LEGAL_SUFFIX_WORDS]
    distinct = [w for w in words if w not in GENERIC_NAME_WORDS]
    return distinct or words


def guess_domains(company_name: str) -> List[str]:
    """Likely domains straight from the name — a fallback when search engines block us."""
    words = [w for w in re.sub(r"[^a-z0-9& ]", " ", company_name.lower()).split()
             if w.upper() not in LEGAL_SUFFIX_WORDS and w != "&"]
    if not words:
        return []
    joined, hyphen = "".join(words), "-".join(words)
    distinct = [w for w in words if w not in GENERIC_NAME_WORDS]
    guesses = [f"{joined}.co.uk", f"{joined}.com", f"{hyphen}.co.uk", f"{joined}.uk"]
    if distinct and distinct != words:
        short = "".join(distinct)
        if len(short) >= 5:
            guesses.append(f"{short}.co.uk")
    return [g for g in dict.fromkeys(guesses) if len(g) <= 70]


def decode_cfemail(hex_string: str) -> Optional[str]:
    """Decodes Cloudflare's 'email protection' obfuscation."""
    try:
        data = bytes.fromhex(hex_string)
        key = data[0]
        return "".join(chr(b ^ key) for b in data[1:])
    except (ValueError, IndexError):
        return None


def clean_email(raw: str) -> Optional[str]:
    em = unquote(raw or "").strip().strip(".,;:()<>[]'\"").lower()
    em = em.split("?")[0]
    m = EMAIL_RE.fullmatch(em)
    if not m or len(em) > 80:
        return None
    if em.endswith(IMAGE_EXTS) or any(j in em for j in JUNK_EMAIL_MARKERS):
        return None
    return em


def extract_emails(soup: BeautifulSoup, html: str) -> Set[str]:
    found: Set[str] = set()
    # 1. mailto: links
    for a in soup.select('a[href^="mailto:" i]'):
        em = clean_email(a["href"].split(":", 1)[1])
        if em:
            found.add(em)
    # 2. Cloudflare-protected emails
    for el in soup.select("[data-cfemail]"):
        em = clean_email(decode_cfemail(el.get("data-cfemail", "")) or "")
        if em:
            found.add(em)
    for a in soup.select('a[href*="/cdn-cgi/l/email-protection#"]'):
        em = clean_email(decode_cfemail(a["href"].split("#", 1)[1]) or "")
        if em:
            found.add(em)
    # 3. Visible text, including "name [at] firm [dot] co.uk" style
    text = soup.get_text(" ")
    text = re.sub(r"\s*[\[\(\{]\s*at\s*[\]\)\}]\s*", "@", text, flags=re.I)
    text = re.sub(r"\s*[\[\(\{]\s*dot\s*[\]\)\}]\s*", ".", text, flags=re.I)
    # 4. Structured data (JSON-LD "email": "...")
    for script in soup.find_all("script", type="application/ld+json"):
        text += " " + (script.string or "")
    for raw in EMAIL_RE.findall(text):
        em = clean_email(raw)
        if em:
            found.add(em)
    found |= spelled_out_emails(text)
    return found



# Emails worded out to dodge spam bots: "kieran at klmtyres dot co dot uk"
SPELLED_EMAIL_RE = re.compile(r"\b([a-z0-9._%+-]{2,40})\s+at\s+([a-z0-9-]{2,40}(?:\s+dot\s+[a-z]{2,10}){1,3})\b", re.I)
# Other organisations' addresses that turn up on firms' sites (regulators, schemes, portals, web hosts)
THIRD_PARTY_EMAIL_MARKERS = (
    "gov.uk", "ico.org.uk", "fca.org.uk", "sra.org.uk", "cqc.org.uk", "nhs.uk", "police.uk", "citizensadvice",
    "ombudsman", "propertymark", "tpos.co.uk", "theprs.co.uk", "rics.org", "trustpilot", "checkatrade",
    "trustatrader", "yell.com", "which.co.uk", "safeagent", "depositprotection", "mydeposits", "tenancydeposit",
    "rightmove", "zoopla", "onthemarket", "wix.com", "squarespace", "godaddy", "123-reg", "ionos", "google.com",
    "facebook", "instagram", "linkedin", "companieshouse", "lawsociety", "bark.com", "nextdoor",
)
# "Website by Acme Digital", "Designed by…", "Powered by…": that link is the web agency, not the firm
CREDIT_RE = re.compile(r"\b(website|site|web\s*design|designed|developed|built|powered|hosted|created|seo|marketing|managed)"
                       r"\s+(by|with)\b", re.I)


def raw_html_emails(html: str) -> Set[str]:
    """Addresses anywhere in the page source (attributes, scripts). Only trusted when they match the firm."""
    found: Set[str] = set()
    for raw in EMAIL_RE.findall(html or ""):
        em = clean_email(raw)
        if em:
            found.add(em)
    return found


def spelled_out_emails(text: str) -> Set[str]:
    found: Set[str] = set()
    for local, rest in SPELLED_EMAIL_RE.findall(text or ""):
        dom = re.sub(r"\s+dot\s+", ".", rest, flags=re.I)
        em = clean_email(local + "@" + dom)
        if em:
            found.add(em)
    return found


def credited_domains(soup: BeautifulSoup) -> Set[str]:
    """Domains linked from 'Website by…' style credits (web agencies)."""
    out: Set[str] = set()
    for a in soup.find_all("a", href=True):
        ctx = a.get_text(" ", strip=True) + " " + (a.parent.get_text(" ", strip=True)[:160] if a.parent else "")
        if CREDIT_RE.search(ctx):
            d = domain_of(a["href"]) if a["href"].startswith("http") else None
            if d:
                out.add(d)
    return out


def _email_label(domain: str) -> str:
    """'klmtyres.co.uk' -> 'klmtyres'; 'mail.smith-law.com' -> 'smithlaw'."""
    parts = (domain or "").lower().split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "org", "ltd", "plc", "me", "net", "ac", "gov", "nhs"):
        label = parts[-3]
    else:
        label = parts[-2] if len(parts) >= 2 else parts[0]
    return re.sub(r"[^a-z0-9]", "", label)


def domain_matches_business(domain: str, names: List[str]) -> bool:
    """Does an email's domain look like the firm's own name? e.g. klmtyres.co.uk for 'KLM TYRES LIMITED'."""
    lab = _email_label(domain)
    if len(lab) < 3:
        return False
    for name in names:
        if not name:
            continue
        words = [w for w in re.sub(r"[^a-z0-9 ]", " ", name.lower().replace("&", " and ")).split()
                 if w.upper() not in LEGAL_SUFFIX_WORDS and w not in ("and", "the")]
        core = "".join(words)
        if len(core) >= 4 and (core == lab or core in lab or (len(lab) >= 5 and lab in core)):
            return True
        if words and len(core) >= 4 and all(w in lab for w in words):
            return True
        distinct = [t for t in distinctive_name_tokens(name) if len(t) >= 3]
        if distinct and sum(len(t) for t in distinct) >= 4 and all(t in lab for t in distinct):
            return True
    return False


def is_third_party_email(email: str, agency_domains: Set[str]) -> bool:
    dom = email.split("@", 1)[-1]
    return any(m in dom for m in THIRD_PARTY_EMAIL_MARKERS) or any(dom == a or dom.endswith("." + a) for a in agency_domains)


def normalise_uk_phone(raw: str) -> Optional[str]:
    """Any UK format -> standard display format, e.g. '+44 (0)1922 123456' -> '01922 123456'."""
    if not raw:
        return None
    raw = unquote(raw).replace("(0)", "")
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0044"):
        digits = "0" + digits[4:]
    elif digits.startswith("44") and len(digits) == 12:
        digits = "0" + digits[2:]
    if not digits.startswith("0") or len(digits) not in (10, 11) or digits[1] not in "123578":
        return None
    d = digits
    if len(d) == 10:
        return f"{d[:5]} {d[5:]}"
    if d.startswith("02"):
        return f"{d[:3]} {d[3:7]} {d[7:]}"            # 020 7946 0000
    if d.startswith(("03", "08")):
        return f"{d[:4]} {d[4:7]} {d[7:]}"            # 0800 123 4567
    if d.startswith("07"):
        return f"{d[:5]} {d[5:]}"                     # 07700 900123
    if d[2] == "1" or d[3] == "1":
        return f"{d[:4]} {d[4:7]} {d[7:]}"            # 0121 234 5678
    return f"{d[:5]} {d[5:]}"                         # 01922 123456


def extract_phones(soup: BeautifulSoup, html: str) -> List[Tuple[str, int]]:
    """Returns (phone, weight). Clickable tel: links count more than plain text."""
    out: List[Tuple[str, int]] = []
    for a in soup.select('a[href^="tel:" i], a[href^="callto:" i]'):
        ph = normalise_uk_phone(a["href"].split(":", 1)[1])
        if ph:
            out.append((ph, 3))
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    for raw in PHONE_TEXT_RE.findall(soup.get_text(" ")):
        ph = normalise_uk_phone(raw)
        if ph:
            out.append((ph, 1))
    return out


def _describe_ch_error(resp: requests.Response) -> str:
    """Turns a Companies House HTTP error into a plain-English message."""
    code = resp.status_code
    if code == 401:
        return "Companies House rejected the API key (401). Check COMPANIES_HOUSE_KEY in Secrets."
    if code == 403:
        return "Companies House refused access (403). The key may not be a REST API key."
    if code == 404:
        return "No matching companies found (404)."
    if code == 416:
        return "Too many results requested. Narrow the search and try again."
    if code == 429:
        return "Companies House rate limit hit (600 requests / 5 mins). Wait a few minutes and retry."
    if code >= 500:
        return f"Companies House is having problems right now ({code}). Try again shortly."
    return f"Companies House returned an unexpected error ({code})."



# What each sector looks like on Google Maps (place types) and in business names
SECTOR_PLACE_RULES: Dict[str, Dict[str, Any]] = {
    "Estate & Lettings Agents": {
        "types": {"real_estate_agency"},
        "words": ("estate", "letting", "lettings", "lets", "property", "properties", "homes",
                  "residential", "realty", "agents", "sales"),
    },
    "Dental Practices": {
        "types": {"dentist", "dental_clinic"},
        "words": ("dental", "dentist", "dentistry", "orthodont", "smile", "teeth", "implant"),
    },
    "Solicitors & Legal Practices": {
        "types": {"lawyer"},
        "words": ("solicitor", "solicitors", "law", "legal", "lawyers", "conveyancing", "notary"),
    },
    "Accountants & Auditors": {
        "types": {"accounting"},
        "words": ("accountant", "accountants", "accounting", "accountancy", "tax", "bookkeeping",
                  "audit", "payroll", "chartered"),
    },
    "General Medical Clinics": {
        "types": {"doctor", "medical_clinic", "medical_center", "hospital", "general_hospital",
                  "physiotherapist", "health"},
        "words": ("clinic", "medical", "health", "surgery", "doctor", "gp", "physio", "practice"),
    },
}
GENERIC_PLACE_TYPES = {"point_of_interest", "establishment", "store", "service", "business"}


def sector_fit(place: Dict[str, Any], rules: Dict[str, Any]) -> Optional[bool]:
    """True = Google lists it as this sector; False = clearly a different business
    (e.g. a locksmith when we want estate agents); None = can't tell."""
    if not rules:
        return None
    types = set(place.get("types") or [])
    if place.get("primaryType"):
        types.add(place["primaryType"])
    if types & rules["types"]:
        return True
    specific = types - GENERIC_PLACE_TYPES
    if not specific:
        return None  # Google only says "business", so don't judge
    name = ((place.get("displayName") or {}).get("text") or "").lower()
    if any(w in name for w in rules["words"]):
        return None  # Name says it's in the sector even if Google's category differs
    return False


class LeadEnricher:

    def __init__(self, ch_api_key: Optional[str] = None):
        self.ch_api_key = ch_api_key.strip() if ch_api_key else None
        self.base_url = "https://api.company-information.service.gov.uk"
        self.headers = self._get_auth_headers()
        self.web_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        }
        self.session = requests.Session()
        self.session.headers.update(self.web_headers)

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.ch_api_key:
            return {}
        token = base64.b64encode(f"{self.ch_api_key}:".encode("utf-8")).decode(
            "utf-8"
        )
        return {"Authorization": f"Basic {token}"}

    def browse_vertical(
        self,
        sic_codes: List[str],
        location_keyword: Optional[str] = None,
        company_name_includes: Optional[str] = None,
        limit: int = 25,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Returns (results, error_message). error_message is None on success."""
        if not self.ch_api_key:
            return [], "No Companies House API key configured."

        url = f"{self.base_url}/advanced-search/companies"
        params: Dict[str, Any] = {
            "sic_codes": ",".join(sic_codes),
            "company_status": "active",
            "size": limit,
        }

        if location_keyword and location_keyword.strip():
            params["location"] = location_keyword.strip()

        if company_name_includes and company_name_includes.strip():
            params["company_name_includes"] = company_name_includes.strip()

        try:
            resp = requests.get(
                url, headers=self.headers, params=params, timeout=12
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                results = []
                for item in items:
                    addr = item.get("registered_office_address", {})
                    loc_parts = [
                        addr.get("locality"),
                        addr.get("postal_code"),
                    ]
                    location_str = ", ".join([p for p in loc_parts if p])
                    results.append(
                        {
                            "Company Name": item.get("company_name", ""),
                            "Company Number": item.get("company_number", ""),
                            "Incorporated": item.get(
                                "date_of_creation", "N/A"
                            ),
                            "Town / Postcode": location_str or "UK",
                            "Status": item.get("company_status", "").title(),
                            "Companies House": (
                                "https://find-and-update.company-information.service.gov.uk/company/"
                                + item.get("company_number", "")
                            ),
                        }
                    )
                return results, None
            if resp.status_code == 404:
                # Advanced search answers 404 when nothing matches.
                return [], None
            return [], _describe_ch_error(resp)
        except requests.exceptions.Timeout:
            return [], "Companies House didn't respond in time. Please try again."
        except requests.exceptions.RequestException as exc:
            return [], f"Couldn't reach Companies House ({exc.__class__.__name__})."
        except ValueError:
            return [], "Companies House returned an unreadable response."

    def get_company_details(self, company_number: str) -> Dict[str, Any]:
        if not self.ch_api_key:
            return {}
        url = f"{self.base_url}/company/{company_number}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {}

    def get_officers(self, company_number: str) -> List[OfficerInfo]:
        if not self.ch_api_key:
            return []
        url = f"{self.base_url}/company/{company_number}/officers"
        officers = []
        self.last_officer_error = None
        try:
            # NB: don't send register_view=true. Companies House answers 400/404 for most firms,
            # which silently returned no directors. Resigned officers are filtered out below instead.
            resp = requests.get(
                url,
                headers=self.headers,
                params={"items_per_page": 100},
                timeout=10,
            )
            if resp.status_code == 429:  # Rate limited during a big batch: wait and retry once
                time.sleep(2)
                resp = requests.get(url, headers=self.headers, params={"items_per_page": 100}, timeout=10)
            if resp.status_code != 200:
                self.last_officer_error = f"Companies House officers lookup failed ({resp.status_code})"
            if resp.status_code == 200:
                for item in resp.json().get("items", []):
                    if not item.get("resigned_on"):
                        raw_role = (item.get("officer_role") or "").lower()
                        officers.append(
                            OfficerInfo(
                                name=item.get("name", "Unknown"),
                                role=format_role(raw_role),
                                raw_role=raw_role,
                                appointed_on=item.get("appointed_on"),
                            )
                        )
        except Exception as exc:
            self.last_officer_error = f"Companies House officers lookup failed ({exc.__class__.__name__})"
        return officers

    # ------------------------------------------------------------------
    # WEBSITE DISCOVERY (search results + domain guesses, verified & scored)
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str, timeout: int = 7) -> Optional[Tuple[str, str]]:
        """GETs a page. Returns (final_url_after_redirects, html) or None."""
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            ctype = resp.headers.get("Content-Type", "").lower()
            if resp.status_code == 200 and ("html" in ctype or not ctype):
                return resp.url, resp.text
        except requests.exceptions.RequestException:
            pass
        return None

    def _search_duckduckgo(self, query: str) -> Tuple[List[str], Optional[str]]:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        try:
            resp = self.session.get(url, timeout=7)
        except requests.exceptions.RequestException:
            return [], "DuckDuckGo unreachable"
        if resp.status_code != 200 or "anomaly" in resp.text.lower()[:5000]:
            return [], "DuckDuckGo blocked the request"
        soup = BeautifulSoup(resp.text, "html.parser")
        urls: List[str] = []
        for a in soup.select("a.result__a[href]"):
            href = a["href"]
            if "uddg=" in href:
                href = unquote(parse_qs(urlparse(href).query).get("uddg", [""])[0])
            if href.startswith("//"):
                href = "https:" + href
            urls.append(href)
        if not urls:  # Older markup: display URL only
            for span in soup.select(".result__url"):
                urls.append("https://" + span.get_text().strip())
        return urls, None

    def _search_bing(self, query: str) -> Tuple[List[str], Optional[str]]:
        url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=en-GB&cc=GB"
        try:
            resp = self.session.get(url, timeout=7)
        except requests.exceptions.RequestException:
            return [], "Bing unreachable"
        if resp.status_code != 200:
            return [], "Bing blocked the request"
        soup = BeautifulSoup(resp.text, "html.parser")
        urls: List[str] = []
        for a in soup.select("li.b_algo h2 a[href]"):
            href = a["href"]
            if "bing.com/ck/a" in href:  # Bing tracking wrapper: u=a1<base64url>
                u = parse_qs(urlparse(href).query).get("u", [""])[0]
                if u.startswith("a1"):
                    try:
                        b64 = u[2:] + "=" * (-len(u[2:]) % 4)
                        href = base64.urlsafe_b64decode(b64).decode("utf-8", "ignore")
                    except Exception:
                        continue
            urls.append(href)
        return urls, None

    def _score_candidate(
        self, domain: str, html: str, company_name: str,
        company_number: Optional[str], postcode: Optional[str], town: Optional[str],
    ) -> Tuple[int, List[str]]:
        """Scores how likely a site belongs to this company. Returns (score, reasons)."""
        score, reasons = 0, []
        tokens = distinctive_name_tokens(company_name)
        compact = "".join(tokens)
        label = domain_label(domain)

        # 1. Domain vs company name
        if compact and len(compact) >= 4 and (compact in label or (len(label) >= 5 and label in compact)):
            score += 45
            reasons.append("domain matches company name")
        else:
            hits = [t for t in tokens if len(t) >= 3 and t in label]
            if hits:
                score += min(15 * len(hits), 30)
                reasons.append(f"domain contains '{', '.join(hits)}'")

        soup = BeautifulSoup(html, "html.parser")
        title = (soup.title.get_text(" ", strip=True) if soup.title else "").lower()
        og = soup.find("meta", attrs={"property": "og:site_name"})
        if og and og.get("content"):
            title += " " + og["content"].lower()
        text = soup.get_text(" ", strip=True)
        text_l = text.lower()
        text_compact = re.sub(r"\s+", "", text_l)

        # 2. Page title / site name
        title_hits = [t for t in tokens if len(t) >= 3 and t in title]
        if title_hits:
            score += min(10 * len(title_hits), 20)
            reasons.append("name in page title")

        # 3. UK companies must show their registered number on their website
        if company_number:
            num = company_number.lstrip("0")
            if re.search(rf"(?<!\d)0*{re.escape(num)}(?!\d)", text_compact) and len(num) >= 5:
                score += 50
                reasons.append(f"company number {company_number} shown on site")

        # 4. Legal name / location on page
        legal = re.sub(r"\s+", " ", company_name.lower()).strip()
        if legal and legal in text_l:
            score += 20
            reasons.append("full legal name on site")
        if postcode and postcode.replace(" ", "").lower() in text_compact:
            score += 15
            reasons.append(f"registered postcode {postcode} on site")
        elif town and len(town) > 3 and town.lower() in text_l:
            score += 5
            reasons.append(f"mentions {town}")
        return score, reasons

    # ------------------------------------------------------------------
    # GOOGLE PLACES (trading name, real website & main phone number)
    # ------------------------------------------------------------------

    PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
    PLACES_FIELDS = (
        "places.displayName,places.websiteUri,places.nationalPhoneNumber,"
        "places.formattedAddress,places.businessStatus,"
        "places.types,places.primaryType,places.primaryTypeDisplayName"
    )

    def places_lookup(self, company_name: str, town: Optional[str],
                      vertical: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Finds the firm on Google Maps. Returns {name, website, phone, address} or None.
        Only runs when GOOGLE_PLACES_API_KEY is set in Secrets (1 billable lookup per firm)."""
        self.last_places_note = None
        key = _secret_value("GOOGLE_PLACES_API_KEY")
        if not key:
            return None
        clean = " ".join(w for w in re.sub(r"[^\w&' ]", " ", company_name).split()
                         if w.upper() not in LEGAL_SUFFIX_WORDS)
        body = {
            "textQuery": f"{clean} {town or ''}".strip(),
            "regionCode": "GB",
            "languageCode": "en-GB",
            "pageSize": 5,
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": self.PLACES_FIELDS,
        }
        try:
            resp = requests.post(self.PLACES_URL, json=body, headers=headers, timeout=8)
        except requests.exceptions.RequestException as exc:
            self.last_places_note = f"Google Maps lookup failed ({exc.__class__.__name__})"
            return None
        if resp.status_code != 200:
            hint = {400: "check the request", 403: "API key not allowed. Enable Places API (New) and billing",
                    429: "quota reached"}.get(resp.status_code, "")
            self.last_places_note = f"Google Maps lookup failed ({resp.status_code}{': ' + hint if hint else ''})"
            return None

        tokens = distinctive_name_tokens(company_name)
        key_tokens = [t for t in tokens if len(t) >= 3] or tokens
        rules = SECTOR_PLACE_RULES.get(vertical or "", {})
        best, best_score = None, 0.0
        wrong_sector: List[str] = []
        for place in resp.json().get("places", []) or []:
            if place.get("businessStatus") == "CLOSED_PERMANENTLY":
                continue
            fit = sector_fit(place, rules)
            if fit is False:  # Google lists it as a different kind of business
                label = ((place.get("primaryTypeDisplayName") or {}).get("text")
                         or (place.get("primaryType") or "other business").replace("_", " "))
                wrong_sector.append(f"'{(place.get('displayName') or {}).get('text', '')}' ({label.lower()})")
                continue
            name = (place.get("displayName") or {}).get("text", "")
            words = re.sub(r"[^a-z0-9 ]", " ", name.lower().replace("&", " and ")).split()
            compact = "".join(words)
            hits = [t for t in key_tokens if t in words or (len(t) >= 4 and t in compact)]
            score = len(hits) / max(1, len(key_tokens))
            web_label = domain_label(domain_of(place.get("websiteUri", "")) or "")
            if web_label and any(len(t) >= 4 and t in web_label for t in key_tokens):
                score += 0.5
            if fit is True:
                score += 0.25  # Right kind of business: extra confidence
            if score > best_score:
                best, best_score = place, score
        if not best or best_score < 0.5:
            self.last_places_note = (
                "Google Maps: ignored " + ", ".join(wrong_sector[:2]) + " (wrong type of business)"
                if wrong_sector else "Google Maps: no listing confidently matched this company"
            )
            return None
        found = {
            "name": (best.get("displayName") or {}).get("text", ""),
            "website": best.get("websiteUri", ""),
            "phone": normalise_uk_phone(best.get("nationalPhoneNumber", "")) or "",
            "address": best.get("formattedAddress", ""),
        }
        self.last_places_note = f"Google Maps: matched '{found['name']}'"
        return found

    def auto_discover_website(
        self,
        company_name: str,
        location: Optional[str] = None,
        company_number: Optional[str] = None,
        postcode: Optional[str] = None,
        places_website: Optional[str] = None,
        trading_name: Optional[str] = None,
        listing_source: str = "Google Maps",
    ) -> Dict[str, Any]:
        """Finds the firm's own website. Returns url, confidence, reasons and notes."""
        places_domain = domain_of(places_website) if places_website else None
        notes: List[str] = []
        clean_name = " ".join(w for w in re.sub(r"[^\w&' ]", " ", company_name).split()
                              if w.upper() not in LEGAL_SUFFIX_WORDS)
        query = f"{clean_name} {location or ''}".strip()

        # A. Search engines (DuckDuckGo, then Bing as a fallback)
        search_urls: List[str] = []
        engines = () if places_domain else (self._search_duckduckgo, self._search_bing)  # Listed site: no need to search
        for engine in engines:
            urls, err = engine(query)
            if err:
                notes.append(err)
            search_urls.extend(urls)
            if urls:
                break

        candidates: List[str] = []
        for u in search_urls:
            d = domain_of(u)
            if d and not is_blocked_domain(d) and d not in candidates:
                candidates.append(d)
        candidates = candidates[:6]

        # B. Domain guesses (works even when search engines block us)
        guessed_only: Set[str] = set()
        for guess in guess_domains(company_name) + (guess_domains(trading_name) if trading_name else []):
            if guess not in candidates:
                candidates.append(guess)
                guessed_only.add(guess)
        # The Google Maps listing's own website goes first
        if places_domain and not is_blocked_domain(places_domain):
            candidates = [places_domain] + [c for c in candidates if c != places_domain]

        # C. Fetch & score candidates in parallel
        rejected_guesses: List[str] = []

        def check(domain: str):
            page = self._fetch_html(f"https://{domain}") or self._fetch_html(f"http://{domain}")
            if not page:
                return None
            final_url, html = page
            final_domain = domain_of(final_url) or domain
            if is_blocked_domain(final_domain):
                return None
            score, reasons = self._score_candidate(
                final_domain, html, company_name, company_number, postcode, location
            )
            if trading_name:
                t_score, t_reasons = self._score_candidate(
                    final_domain, html, trading_name, company_number, postcode, location
                )
                if t_score > score:
                    score, reasons = t_score, t_reasons
            on_listing = bool(places_domain and final_domain in (places_domain, "www." + places_domain))
            if on_listing:
                score += 35
                reasons = [f"website on the firm's {listing_source} listing"] + reasons
            elif domain in guessed_only:
                # A guessed address (e.g. elliott.com) must prove it's this firm: a matching name in the
                # web address or page title isn't enough, since big unrelated sites share common names.
                strong = ("company number", "full legal name", "registered postcode", "mentions ")
                if not any(r.startswith(strong) for r in reasons):
                    rejected_guesses.append(final_domain)
                    return None
            return final_url, final_domain, score, reasons

        results = []
        with ThreadPoolExecutor(max_workers=6) as pool:
            for res in pool.map(check, candidates):
                if res:
                    results.append(res)

        if not results:
            if places_website and places_domain and not is_blocked_domain(places_domain):
                notes.append(f"Website didn't respond to us, but it's on the firm's {listing_source} listing")
                parsed_p = urlparse(places_website if "://" in places_website else "https://" + places_website)
                return {"url": f"{parsed_p.scheme}://{parsed_p.netloc}", "confidence": "Medium",
                        "reasons": [f"website on the firm's {listing_source} listing"], "notes": notes}
            if rejected_guesses:
                notes.append("Ignored " + ", ".join(sorted(set(rejected_guesses))[:3])
                             + ": nothing on the site ties it to this company")
            else:
                notes.append("No candidate website responded")
            return {"url": None, "confidence": None, "reasons": [], "notes": notes}

        results.sort(key=lambda r: r[2], reverse=True)
        final_url, final_domain, score, reasons = results[0]
        if score < 35:
            notes.append(f"Best candidate {final_domain} scored too low to trust")
            return {"url": None, "confidence": None, "reasons": reasons, "notes": notes,
                    "rejected": final_domain}

        confidence = "High" if score >= 80 else "Medium" if score >= 55 else "Low"
        parsed = urlparse(final_url)
        return {
            "url": f"{parsed.scheme}://{parsed.netloc}",
            "confidence": confidence,
            "reasons": reasons,
            "notes": notes,
        }

    # ------------------------------------------------------------------
    # CONTACT SCRAPING (contact/about/team pages, hidden emails, clean phones)
    # ------------------------------------------------------------------

    def _find_contact_pages(self, soup: BeautifulSoup, root: str) -> List[str]:
        root_host = domain_of(root)
        ranked: List[Tuple[int, str]] = []
        for a in soup.find_all("a", href=True):
            href = urljoin(root + "/", a["href"].strip())
            if not href.startswith("http") or domain_of(href) != root_host:
                continue
            path_and_text = (urlparse(href).path + " " + a.get_text(" ", strip=True)).lower()
            for rank, hint in enumerate(CONTACT_PAGE_HINTS):
                if hint in path_and_text:
                    clean = href.split("#")[0].rstrip("/")
                    if clean != root.rstrip("/"):
                        ranked.append((rank, clean))
                    break
        seen, pages = set(), []
        for _, url in sorted(ranked):
            if url not in seen:
                seen.add(url)
                pages.append(url)
        return pages[:4]

    def scrape_contact_channels(self, base_url: str, names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Emails and phones from the firm's site: home page, contact/about/team pages, then (if still no email)
        privacy, terms and the usual contact addresses. `names` (company / trading name) lets an email on a
        different domain count when it's clearly the firm's own, e.g. kieran@klmtyres.co.uk on millomtyrecentre.co.uk."""
        empty = {"emails": [], "other_emails": [], "phones": [], "description": "",
                 "resolved_url": None, "pages_checked": [], "notes": []}
        if not base_url:
            return empty
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        names = [n for n in (names or []) if n]

        home = self._fetch_html(base_url)
        if not home and base_url.startswith("https://"):
            home = self._fetch_html("http://" + base_url[len("https://"):])
        if not home:
            return {**empty, "resolved_url": base_url}

        final_url, home_html = home
        parsed = urlparse(final_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        site_domain = domain_of(root)
        home_soup = BeautifulSoup(home_html, "html.parser")

        extra_pages = self._find_contact_pages(home_soup, root)
        if not extra_pages:
            extra_pages = [urljoin(root, p) for p in ("/contact", "/contact-us", "/about", "/about-us")]

        pages_html = [(final_url, home_html)]
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url, page in zip(extra_pages, pool.map(self._fetch_html, extra_pages)):
                if page:
                    pages_html.append((page[0], page[1]))

        email_hits: Dict[str, int] = {}   # seen on the page itself (links, text, Cloudflare-protected)
        raw_hits: Set[str] = set()        # anywhere in the page source
        agencies: Set[str] = set()
        phone_scores: Dict[str, int] = {}
        description = ""
        notes: List[str] = []

        def read_pages(pages: List[Tuple[str, str]]) -> None:
            nonlocal description
            for _, html in pages:
                soup = BeautifulSoup(html, "html.parser")
                if not description:
                    for attrs in ({"name": "description"}, {"property": "og:description"}):
                        tag = soup.find("meta", attrs=attrs)
                        if tag and tag.get("content"):
                            description = tag["content"].strip()
                            break
                for em in extract_emails(soup, html):
                    email_hits[em] = email_hits.get(em, 0) + 1
                raw_hits.update(raw_html_emails(html))
                agencies.update(credited_domains(soup))
                for ph, weight in extract_phones(soup, html):
                    phone_scores[ph] = phone_scores.get(ph, 0) + weight

        def is_own(dom: str) -> bool:
            return bool(site_domain) and (dom == site_domain or dom.endswith("." + site_domain) or site_domain.endswith("." + dom))

        def sort_out() -> Tuple[List[str], List[str], List[str]]:
            own, freemail, other = [], [], []
            for em in sorted(set(email_hits) | raw_hits):
                dom = em.split("@", 1)[1]
                seen = em in email_hits
                if is_own(dom):
                    own.append(em)
                elif is_third_party_email(em, agencies - {site_domain}):
                    if seen:
                        other.append(em)
                elif domain_matches_business(dom, names):
                    own.append(em)
                elif dom in FREE_MAIL_DOMAINS:
                    if seen:
                        freemail.append(em)
                elif seen:
                    other.append(em)
            return own, freemail, other

        read_pages(pages_html)
        own, freemail, other = sort_out()

        # Still nothing: privacy/terms pages and the usual contact addresses often carry the email
        if not own and not freemail:
            fetched = {u.rstrip("/") for u, _ in pages_html} | {u.rstrip("/") for u in extra_pages}
            more: List[str] = []
            for a in home_soup.find_all("a", href=True):
                href = urljoin(root + "/", a["href"].strip()).split("#")[0].rstrip("/")
                label = (urlparse(href).path + " " + a.get_text(" ", strip=True)).lower()
                if domain_of(href) == site_domain and any(w in label for w in ("privacy", "terms", "legal", "gdpr", "imprint")):
                    more.append(href)
            more += [urljoin(root, p).rstrip("/") for p in ("/contact", "/contact-us", "/contactus", "/get-in-touch",
                                                           "/about", "/about-us", "/privacy-policy", "/privacy")]
            more = [u for u in dict.fromkeys(more) if u not in fetched][:6]
            if more:
                second: List[Tuple[str, str]] = []
                with ThreadPoolExecutor(max_workers=4) as pool:
                    for url, page in zip(more, pool.map(self._fetch_html, more)):
                        if page:
                            second.append((page[0], page[1]))
                read_pages(second)
                pages_html += second
                own, freemail, other = sort_out()

        # Last check for a lone address on another domain: does that domain lead back to this site?
        if not own and not freemail and other:
            for dom in list(dict.fromkeys(e.split("@", 1)[1] for e in other))[:2]:
                if self._domain_points_to(dom, site_domain):
                    moved = [e for e in other if e.split("@", 1)[1] == dom]
                    own += moved
                    other = [e for e in other if e not in moved]
                    notes.append(f"Email on {dom} accepted: that address's website leads back to {site_domain}")
                    break
        for em in own:
            dom = em.split("@", 1)[1]
            if not is_own(dom) and not any(dom in n for n in notes):
                notes.append(f"Email on {dom} accepted: the domain matches the business name")

        phones = sorted(phone_scores, key=lambda p: (-phone_scores[p], p))[:5]
        return {
            "emails": sorted(set(own)) + sorted(set(freemail)),
            "other_emails": sorted(set(other)),
            "phones": phones,
            "description": description,
            "resolved_url": root,
            "pages_checked": [u for u, _ in pages_html],
            "notes": notes,
        }

    def _domain_points_to(self, email_domain: str, site_domain: Optional[str]) -> bool:
        """True if the email's domain redirects to, or links to, the firm's website."""
        if not site_domain or any(m in email_domain for m in THIRD_PARTY_EMAIL_MARKERS):
            return False
        for url in (f"https://{email_domain}", f"https://www.{email_domain}"):
            page = self._fetch_html(url, timeout=5)
            if page:
                final_dom = domain_of(page[0]) or ""
                return final_dom == site_domain or site_domain in page[1][:300000]
        return False

    def enrich_selected_company(
        self,
        company_number: str,
        sector_name: str,
        manual_website: Optional[str] = None,
    ) -> ScrapedLead:
        ch_data = self.get_company_details(company_number)
        company_name = ch_data.get("company_name", company_number)

        address_dict = ch_data.get("registered_office_address", {})
        address_parts = [
            address_dict.get(k)
            for k in [
                "premises",
                "address_line_1",
                "locality",
                "region",
                "postal_code",
            ]
            if address_dict.get(k)
        ]
        registered_address = (
            ", ".join(address_parts) if address_parts else None
        )
        town = address_dict.get("locality")
        postcode = address_dict.get("postal_code")

        officers = mark_owners(self.get_officers(company_number), psc_owner_names(self.ch_api_key, company_number))

        # Free sources first (sector register, then OpenStreetMap); Google Maps only if they leave gaps
        free, free_notes = free_intel(company_name, postcode or "", sector_name,
                                      sra_data=getattr(self, "sra_data", None))
        need_google = not (free and free.get("website") and free.get("phone"))
        places = self.places_lookup(company_name, town or postcode, sector_name) if need_google else None
        if not need_google:
            self.last_places_note = "Google Maps: not needed (free sources had the website and phone)"
        trading_name = (places["name"] if places and places.get("name") else None) or (
            free["name"] if free and free.get("name") and _sim(free["name"], company_name) < 1 else None)

        listed_site, listed_source = None, "Google Maps"
        if places and places.get("website"):
            listed_site = places["website"]
        elif free and free.get("website"):
            listed_site, listed_source = free["website"], free["source"]

        target_website = manual_website.strip() if manual_website else None
        discovery: Dict[str, Any] = {"confidence": "Manual", "reasons": ["entered by you"], "notes": []}
        if not target_website:
            discovery = self.auto_discover_website(
                company_name,
                location=town or postcode,
                company_number=company_number,
                postcode=postcode,
                places_website=listed_site,
                trading_name=trading_name,
                listing_source=listed_source,
            )
            target_website = discovery.get("url")

        site_contacts = (
            self.scrape_contact_channels(target_website, names=[company_name, trading_name or ""])
            if target_website
            else {"emails": [], "other_emails": [], "phones": [], "description": "",
                  "resolved_url": None, "pages_checked": [], "notes": []}
        )
        notes = free_notes + list(discovery.get("notes", [])) + list(site_contacts.get("notes") or [])
        if getattr(self, "last_places_note", None):
            notes.insert(len(free_notes), self.last_places_note)
        phones = list(site_contacts["phones"])
        for listed in (free, places):  # Listed numbers are usually the main switchboard
            if listed and listed.get("phone"):
                phones = [listed["phone"]] + [p for p in phones if p != listed["phone"]]
        emails = list(site_contacts["emails"])
        if free and free.get("email") and free["email"] not in emails:
            emails.insert(0, free["email"])
        emails, dead = filter_deliverable(emails)
        if dead:
            notes.append("Dropped (domain can't receive email): " + ", ".join(dead[:3]))
        owners = [display_officer_name(o.name) for o in officers if getattr(o, "is_owner", False)]
        if owners:
            notes.append("Companies House: " + ", ".join(owners[:2]) + (" is" if len(owners) == 1 else " are")
                         + " a director and owner")
        if getattr(self, "last_officer_error", None):
            notes.append(self.last_officer_error)
        if target_website and not site_contacts.get("pages_checked"):
            notes.append("Website didn't respond when scraping contacts")

        return ScrapedLead(
            company_name=company_name,
            company_number=company_number,
            sic_codes=ch_data.get("sic_codes", []),
            sector_guess=sector_name,
            registered_address=registered_address,
            website_url=site_contacts.get("resolved_url") or target_website,
            phones_found=phones,
            emails_found=emails,
            trading_name=trading_name,
            officers=officers,
            site_meta_description=site_contacts["description"],
            website_confidence=discovery.get("confidence") if target_website else None,
            website_reasons=discovery.get("reasons", []),
            discovery_notes=notes,
            other_emails=site_contacts.get("other_emails", []),
            pages_checked=site_contacts.get("pages_checked", []),
        )


# ==========================================
# FREE INTELLIGENCE: no-cost sources tried before Google Maps
#   Companies House owners (PSC) · FCA & SRA registers · OpenStreetMap · DNS email checks
# ==========================================
FREE_HEADERS = {"User-Agent": "SalesHub/1.0 (business directory lookups)"}
_FREE_CACHE: Dict[str, Any] = {}
FCA_SECTORS = {"Financial Advisers & Mortgage Brokers", "Insurance Brokers"}
SRA_SECTORS = {"Solicitors & Legal Practices"}
CQC_SECTORS = {"Care Homes & Home Care", "General Medical Clinics", "Dental Practices"}
# Where a person can double-check a firm by hand (registers without a usable free search API)
REGISTER_LINKS = {
    "Care Homes & Home Care": ("CQC register", "https://www.cqc.org.uk/search/all?query={q}"),
    "General Medical Clinics": ("CQC register", "https://www.cqc.org.uk/search/all?query={q}"),
    "Dental Practices": ("CQC register", "https://www.cqc.org.uk/search/all?query={q}"),
    "Financial Advisers & Mortgage Brokers": ("FCA register", "https://register.fca.org.uk/s/search?q={q}&type=Companies"),
    "Insurance Brokers": ("FCA register", "https://register.fca.org.uk/s/search?q={q}&type=Companies"),
    "Solicitors & Legal Practices": ("SRA register", "https://www.sra.org.uk/consumers/register/"),
    "Veterinary Practices": ("RCVS Find a Vet", "https://findavet.rcvs.org.uk/find-a-vet-practice/?filter-keyword={q}"),
}


def register_link(sector: str, company: str) -> Optional[Tuple[str, str]]:
    entry = REGISTER_LINKS.get(sector)
    if not entry:
        return None
    return entry[0], entry[1].format(q=quote_plus(friendly_company_name(company)))


def _sim(a: str, b: str) -> float:
    ta, tb = set(distinctive_name_tokens(a or "")), set(distinctive_name_tokens(b or ""))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def _free_get_json(url: str, **kwargs) -> Optional[Any]:
    try:
        resp = requests.get(url, headers={**FREE_HEADERS, **kwargs.pop("headers", {})}, timeout=kwargs.pop("timeout", 10), **kwargs)
        if resp.status_code != 200:
            return None
        return resp.json()
    except (requests.exceptions.RequestException, ValueError):
        return None


def postcode_location(postcode: str) -> Optional[Tuple[float, float]]:
    """Latitude/longitude of a UK postcode (postcodes.io, free, no key)."""
    pc = (postcode or "").replace(" ", "").upper()
    if not pc:
        return None
    key = f"pc:{pc}"
    if key not in _FREE_CACHE:
        data = _free_get_json(f"https://api.postcodes.io/postcodes/{pc}")
        res = (data or {}).get("result") or {}
        _FREE_CACHE[key] = (res["latitude"], res["longitude"]) if res.get("latitude") else None
    return _FREE_CACHE[key]


def dns_has(domain: str, rtype: str) -> Optional[bool]:
    """True/False if the domain has records of this type (Google DNS-over-HTTPS, free). None if unknown."""
    key = f"dns:{domain}:{rtype}"
    if key not in _FREE_CACHE:
        data = _free_get_json("https://dns.google/resolve", params={"name": domain, "type": rtype}, timeout=6)
        if data is None:
            _FREE_CACHE[key] = None
        elif data.get("Status") == 3:  # NXDOMAIN: the domain doesn't exist
            _FREE_CACHE[key] = False
        else:
            _FREE_CACHE[key] = any(a.get("type") in (15 if rtype == "MX" else 1, 5) for a in (data.get("Answer") or []))
    return _FREE_CACHE[key]


def email_domain_ok(email: str) -> Optional[bool]:
    """Can this address receive mail? False only when DNS says the domain has no mail server at all."""
    domain = (email or "").rsplit("@", 1)[-1].lower()
    if not domain:
        return False
    mx = dns_has(domain, "MX")
    if mx is not False:
        return mx
    return dns_has(domain, "A")  # Mail can still be delivered to the domain's A record


def filter_deliverable(emails: List[str]) -> Tuple[List[str], List[str]]:
    """(kept, dropped): drops addresses whose domain can't receive email (typos, dead domains)."""
    kept, dropped = [], []
    for e in emails:
        (dropped if email_domain_ok(e) is False else kept).append(e)
    return kept, dropped


def osm_lookup(company: str, postcode: str, trading_name: str = "") -> Optional[Dict[str, Any]]:
    """The business on OpenStreetMap near its postcode (Overpass API, free, no key)."""
    loc = postcode_location(postcode)
    tokens = [t for t in distinctive_name_tokens(trading_name or company) if len(t) >= 4] or \
             distinctive_name_tokens(trading_name or company)
    if not loc or not tokens:
        return None
    token = re.escape(max(tokens, key=len))
    query = (f'[out:json][timeout:12];nwr(around:3000,{loc[0]},{loc[1]})["name"~"{token}",i];out tags 20;')
    key = f"osm:{query}"
    if key not in _FREE_CACHE:
        try:
            resp = requests.post("https://overpass-api.de/api/interpreter", data={"data": query},
                                 headers=FREE_HEADERS, timeout=15)
            _FREE_CACHE[key] = resp.json().get("elements", []) if resp.status_code == 200 else None
        except (requests.exceptions.RequestException, ValueError):
            _FREE_CACHE[key] = None
    elements = _FREE_CACHE[key]
    if not elements:
        return None
    best, best_score = None, 0.0
    for el in elements:
        tags = el.get("tags") or {}
        score = max(_sim(company, tags.get("name", "")), _sim(trading_name, tags.get("name", "")) if trading_name else 0)
        if score > best_score:
            best, best_score = tags, score
    if not best or best_score < 0.5:
        return None
    site = best.get("website") or best.get("contact:website") or best.get("url") or ""
    phone = best.get("phone") or best.get("contact:phone") or ""
    email = best.get("email") or best.get("contact:email") or ""
    if not (site or phone or email):
        return None
    return {"name": best.get("name", ""), "website": site, "phone": normalise_uk_phone(phone.split(";")[0]) or "",
            "email": clean_email(email.split(";")[0]) if email else None, "source": "OpenStreetMap"}


def _pick(d: Dict[str, Any], *words: str) -> str:
    """First non-empty value whose key contains any of the words (register APIs vary their field names)."""
    for k, v in (d or {}).items():
        if any(w in k.lower() for w in words) and isinstance(v, (str, int)) and str(v).strip():
            return str(v).strip()
    return ""


def fca_lookup(company: str, postcode: str) -> Optional[Dict[str, Any]]:
    """FCA Financial Services Register (free key: FCA_API_EMAIL + FCA_API_KEY in Secrets)."""
    email, key = _secret_value("FCA_API_EMAIL"), _secret_value("FCA_API_KEY")
    if not (email and key):
        return None
    hdr = {"X-Auth-Email": email, "X-Auth-Key": key, "Content-Type": "application/json"}
    base = "https://register.fca.org.uk/services/V0.1"
    data = _free_get_json(f"{base}/Search", params={"q": friendly_company_name(company), "type": "firm"}, headers=hdr)
    rows = (data or {}).get("Data") or []
    ranked = sorted(
        [r for r in rows if "authorised" in _pick(r, "status").lower() or not _pick(r, "status")],
        key=lambda r: -_sim(company, _pick(r, "name")))
    for r in ranked[:3]:
        if _sim(company, _pick(r, "name")) < 0.6:
            break
        frn = _pick(r, "reference number", "frn")
        addr = _free_get_json(f"{base}/Firm/{frn}/Address", headers=hdr) if frn else None
        offices = (addr or {}).get("Data") or []
        pc = (postcode or "").replace(" ", "").upper()
        office = next((o for o in offices if pc and _pick(o, "postcode").replace(" ", "").upper() == pc), None) \
            or (offices[0] if offices else {})
        site, phone = _pick(office, "website"), _pick(office, "phone")
        if site or phone:
            return {"name": _pick(r, "name"), "website": site, "phone": normalise_uk_phone(phone) or phone,
                    "email": None, "source": f"FCA register (FRN {frn})"}
    return None


@st.cache_resource(ttl=86400, show_spinner="Downloading the SRA register (once a day)…")
def sra_register() -> List[Dict[str, Any]]:
    """Every SRA-regulated firm with its offices (free key: SRA_API_KEY in Secrets). Cached for a day."""
    key = _secret_value("SRA_API_KEY")
    if not key:
        return []
    try:
        resp = requests.get("https://sra-prod-apim.azure-api.net/datashare/api/V1/organisation/GetAll",
                            headers={"Ocp-Apim-Subscription-Key": key, **FREE_HEADERS}, timeout=90)
        body = resp.json() if resp.status_code == 200 else {}
    except (requests.exceptions.RequestException, ValueError):
        body = {}
    orgs = body.get("Organisations") or body.get("organisations") or (body if isinstance(body, list) else [])
    return [o for o in orgs if isinstance(o, dict)]


def sra_lookup(company: str, postcode: str, register: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not register:
        return None
    pc = (postcode or "").replace(" ", "").upper()
    best, best_score, best_office = None, 0.0, {}
    for org in register:
        name = _pick(org, "practicename", "name")
        score = _sim(company, name)
        if score < 0.6:
            continue
        offices = org.get("Offices") or org.get("offices") or []
        office = next((o for o in offices if pc and _pick(o, "postcode").replace(" ", "").upper() == pc), None)
        if office:
            score += 0.3
        if score > best_score:
            best, best_score, best_office = org, score, office or (offices[0] if offices else {})
    if not best:
        return None
    site, phone, email = _pick(best_office, "website"), _pick(best_office, "phone"), _pick(best_office, "email")
    if not (site or phone or email):
        return None
    return {"name": _pick(best, "practicename", "name"), "website": site, "phone": normalise_uk_phone(phone) or phone,
            "email": clean_email(email) if email else None, "source": f"SRA register (SRA {_pick(best, 'sranumber')})"}


def free_intel(company: str, postcode: str, sector: str, trading_name: str = "",
               sra_data: Optional[List[Dict[str, Any]]] = None) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Tries the free sources in order: the sector's register, then OpenStreetMap. Returns (found, notes)."""
    notes: List[str] = []
    found = None
    if sector in FCA_SECTORS and _secret_value("FCA_API_KEY"):
        found = fca_lookup(company, postcode)
        notes.append(f"FCA register: matched '{found['name']}'" if found else "FCA register: no confident match")
    elif sector in SRA_SECTORS and sra_data:
        found = sra_lookup(company, postcode, sra_data)
        notes.append(f"SRA register: matched '{found['name']}'" if found else "SRA register: no confident match")
    if not found:
        found = osm_lookup(company, postcode, trading_name)
        if found:
            notes.append(f"OpenStreetMap: matched '{found['name']}'")
    if found and found.get("website") and not found["website"].startswith("http"):
        found["website"] = "https://" + found["website"]
    return found, notes


def psc_owner_names(ch_api_key: str, company_number: str) -> List[str]:
    """Active individual owners (People with Significant Control) from Companies House, as 'forename surname'."""
    if not ch_api_key or not company_number:
        return []
    try:
        resp = requests.get(
            f"https://api.company-information.service.gov.uk/company/{company_number}/persons-with-significant-control",
            auth=(ch_api_key, ""), timeout=10)
        items = resp.json().get("items", []) if resp.status_code == 200 else []
    except (requests.exceptions.RequestException, ValueError):
        return []
    out = []
    for it in items:
        if it.get("ceased_on") or "individual" not in (it.get("kind") or ""):
            continue
        ne = it.get("name_elements") or {}
        name = " ".join(x for x in [ne.get("forename"), ne.get("surname")] if x) or it.get("name", "")
        if name:
            out.append(name.lower())
    return out


def mark_owners(officers: List[Any], owners: List[str]) -> List[Any]:
    """Flags directors who are also owners, so the pitch goes to the person who signs things off."""
    if not owners:
        return officers
    for o in officers:
        disp = display_officer_name(o.name).lower().split()
        if disp and any(disp[0] in own.split() and disp[-1] in own.split() for own in owners):
            o.is_owner = True
            if "owner" not in (o.role or "").lower():
                o.role = f"{o.role} & owner"
    return officers


# ==========================================
# 3. PITCH SYNTHESIZER & PDF BUILDER
# ==========================================


def sanitize_pdf_text(text: str) -> str:
    """Replaces Unicode bullets, smart quotes, and dashes with Latin-1 equivalents for FPDF."""
    if not text:
        return ""
    replacements = {
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
        "•": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="replace").decode("latin-1")


# Companies House officer_role values, best decision-maker first.
# Secretaries and all "corporate-*" roles (companies, not people) are excluded.
DECISION_MAKER_ROLES = [
    "director",
    "llp-designated-member",
    "llp-member",
    "managing-officer",
    "member",
]

ROLE_LABELS = {
    "director": "Director",
    "llp-designated-member": "Designated Member (LLP)",
    "llp-member": "Member (LLP)",
    "managing-officer": "Managing Officer",
    "member": "Member",
    "secretary": "Company Secretary",
    "nominee-director": "Nominee Director",
}

NAME_TITLES = {"mr", "mrs", "ms", "miss", "dr", "sir", "dame", "prof", "professor", "lord", "lady", "rev"}


def format_role(raw_role: str) -> str:
    raw_role = (raw_role or "").strip().lower()
    return ROLE_LABELS.get(raw_role, raw_role.replace("-", " ").title() or "Officer")


def first_name_from_officer(raw_name: str) -> Optional[str]:
    """Companies House lists people as 'SURNAME, Forename Middle'.
    Returns the forename, e.g. 'BYWATER, Paul James' -> 'Paul'."""
    if not raw_name:
        return None
    if "," in raw_name:
        forenames = raw_name.split(",", 1)[1]
    else:
        forenames = raw_name  # Rare 'Paul BYWATER' style: first word is the forename
    for token in forenames.replace(".", " ").split():
        clean = re.sub(r"[^A-Za-z'\-]", "", token)
        if clean and clean.lower() not in NAME_TITLES and len(clean) > 1:
            return "-".join(p[:1].upper() + p[1:].lower() for p in clean.split("-"))
    return None


def pick_decision_maker(officers: List["OfficerInfo"]) -> Optional["OfficerInfo"]:
    """Chooses the most senior active person (directors first, longest-serving first)."""
    for wanted in DECISION_MAKER_ROLES:
        matches = [o for o in officers if o.raw_role == wanted]
        if matches:
            return sorted(matches, key=lambda o: (not getattr(o, "is_owner", False), o.appointed_on or "9999"))[0]
    return None


GENERIC_EMAIL_PREFIXES = {
    "info", "information", "enquiries", "enquiry", "enq", "sales", "lettings", "letting",
    "rentals", "lets", "office", "admin", "administration", "contact", "contactus",
    "mail", "post", "reception", "frontdesk", "support", "help", "hello", "hi", "team",
    "accounts", "account", "finance", "billing", "invoices", "payments", "bookings",
    "booking", "appointments", "appts", "careers", "jobs", "recruitment", "hr",
    "marketing", "newsletter", "news", "press", "media", "privacy", "dpo", "data",
    "gdpr", "complaints", "feedback", "service", "services", "customerservice",
    "customerservices", "general", "manager", "management", "partners", "property",
    "properties", "valuations", "valuation", "maintenance", "repairs", "lettingsteam",
    "salesteam", "dental", "dentist", "surgery", "practice", "practicemanager",
    "clinic", "patients", "patient", "law", "legal", "conveyancing", "probate",
    "family", "tax", "payroll", "bookkeeping", "audit", "web", "webmaster", "website",
    "it", "tech", "office1", "branch", "new", "newbusiness", "referrals", "clients",
}


def first_name_from_email(email: str) -> Optional[str]:
    """'david.mann@x.co.uk' -> 'David'. Returns None for inboxes like info@ or accounts@."""
    prefix = email.split("@", 1)[0].lower()
    compact = re.sub(r"[^a-z]", "", prefix)
    if not compact or compact in GENERIC_EMAIL_PREFIXES:
        return None
    first = re.split(r"[._\-]", prefix)[0]
    first = re.sub(r"[^a-z]", "", first)
    # Must look like a first name: letters only, 3-12 chars, not a generic word
    if 3 <= len(first) <= 12 and first not in GENERIC_EMAIL_PREFIXES and first.isalpha():
        # 'dmann' style (initial + surname) can't be trusted as a first name
        has_separator = any(sep in prefix for sep in "._-")
        if not has_separator:
            if len(first) > 8:
                return None
            # Two leading consonants that rarely start a first name = initial + surname ('dmann', 'pbywater')
            vowels = set("aeiouy")
            ok_clusters = {"br", "ch", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "kr",
                           "ph", "pr", "sc", "sh", "st", "th", "tr", "bl", "chr", "sk"}
            if first[0] not in vowels and first[1] not in vowels and first[:2] not in ok_clusters:
                return None
        return first.capitalize()
    return None


def pick_primary_email(lead: "ScrapedLead", first_name: Optional[str] = None) -> Optional[str]:
    """The best single email for the dossier: the contact's own inbox, else the main inbox."""
    if getattr(lead, "contact_email", None):
        return lead.contact_email
    if not lead.emails_found:
        return None
    if first_name:
        for em in lead.emails_found:
            if em.split("@", 1)[0].lower().startswith(first_name.lower()):
                return em
    for preferred in ("info", "enquiries", "hello", "contact", "office", "reception"):
        for em in lead.emails_found:
            if em.split("@", 1)[0].lower() == preferred:
                return em
    return lead.emails_found[0]


def infer_contact_name_and_role(
    lead: ScrapedLead, vertical_key: str
) -> Tuple[str, str]:
    """Smart contact resolver: extracts personal names from officers or email prefixes."""
    vert_cfg = VERTICAL_PRESETS.get(
        vertical_key, VERTICAL_PRESETS["Estate & Lettings Agents"]
    )

    # 0. A contact a person has confirmed (e.g. via LinkedIn) always wins
    manual = (getattr(lead, "contact_name", None) or "").strip()
    if manual:
        first = re.sub(r"[^A-Za-z'\-]", "", manual.split()[0]) if manual.split() else ""
        if first:
            return first[:1].upper() + first[1:], (getattr(lead, "contact_role", None) or "Confirmed contact")

    # 1. Primary Officer match — only real people in decision-making roles
    officer = pick_decision_maker(lead.officers)
    if officer:
        first_name = first_name_from_officer(officer.name)
        if first_name:
            return first_name, officer.role

    # 2. Email Prefix Extraction (e.g. sarah@firm.co.uk or david.mann@firm.co.uk -> Sarah / David)
    for em in lead.emails_found:
        name_candidate = first_name_from_email(em)
        if name_candidate:
            return name_candidate, f"Direct Contact ({em})"

    # 3. Fallback to vertical-specific role
    return vert_cfg["fallback_greeting"], "Team / Branch Management"


# ------------------------------------------------------------------
# South Wales Telecoms brand & sector copy (email + overview PDF). Contact details come from Secrets.
# ------------------------------------------------------------------

def _brand_secret(key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(key, default) or default)
    except Exception:
        return default


SENDER_COMPANY = _brand_secret("COMPANY_NAME", "South Wales Telecoms")
BRAND_WORDS = (_brand_secret("BRAND_WORD_1", "South Wales"), _brand_secret("BRAND_WORD_2", "Telecoms"))
BRAND_INITIALS = _brand_secret("BRAND_INITIALS", "SW")
BRAND_FILE = re.sub(r"[^A-Za-z0-9]+", "_", SENDER_COMPANY).strip("_") or "Sales"
BRAND_HOME = _brand_secret("BRAND_HOME_LINE", "A South Wales team you can actually speak to.")
SENDER_DEFAULTS = {
    "name": "",
    "title": _brand_secret("SENDER_TITLE", "Business Solutions Consultant"),
    "phone": _brand_secret("SENDER_PHONE", ""),
    "email": _brand_secret("SENDER_EMAIL", "sales@southwalestelecoms.co.uk"),
    "website": _brand_secret("SENDER_WEBSITE", "www.southwalestelecoms.co.uk"),
    "address": _brand_secret("SENDER_ADDRESS", ""),
}
BRAND_PURPLE = (16, 35, 63)       # #10233f  South Wales Telecoms navy
BRAND_PURPLE_2 = (28, 52, 88)     # #1c3458
BRAND_TEAL = (224, 71, 59)        # #e0473b  South Wales Telecoms red
SWITCHOVER_LINE = (
    "With BT's analogue phone network switching off by January 2027, it's a good moment to"
    " move to a system that actually works with your software."
)

# Per-sector copy. Keys match VERTICAL_PRESETS.
SECTOR_COPY: Dict[str, Dict[str, Any]] = {
    "Estate & Lettings Agents": {
        "sector_plural": "estate and lettings agents",
        "subject": "Stop missing applicant calls at {company}",
        "pain": "Most agencies still ask who's calling, then search {crms} while the caller waits. And calls missed during viewings often go to the agent down the road.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which system you use and how many staff take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Calls missed during viewings", "Applicants who can't get through rarely leave a message; they ring the next agent."),
            ("No caller context", "Staff answer blind, then search the CRM while the landlord or tenant waits."),
            ("No record of what was agreed", "Call notes live in people's heads, not on the property or tenancy file."),
        ],
        "outcomes": [
            ("Screen-pop on every call", "The landlord, vendor or applicant record opens the moment the phone rings."),
            ("Click-to-dial from your CRM", "Call straight from the property, applicant or tenancy record. No retyping numbers."),
            ("Calls logged automatically", "Every call, duration and recording saved against the right record for compliance and disputes."),
            ("Missed-call recovery", "Missed calls are flagged instantly with the caller's record, so no lead goes cold."),
        ],
    },
    "Dental Practices": {
        "sector_plural": "dental practices",
        "subject": "Fewer missed patient calls at {company}",
        "pain": "Reception gets swamped at 8.30am, patients who can't get through don't always call back, and staff search {crms} on every call.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which system you use and how many handsets you have, and I'll send a no-obligation quote.",
        "challenges": [
            ("Morning call peaks", "Reception is overwhelmed at opening and patients give up or go elsewhere."),
            ("Lost recalls and bookings", "Missed calls mean missed appointments and gaps in the diary."),
            ("Searching while the patient waits", "Staff look up records manually on every call."),
        ],
        "outcomes": [
            ("Patient screen-pop", "The patient's record appears on the reception screen as the phone rings."),
            ("Call queueing & callbacks", "Smart queues and messages manage the morning rush without losing callers."),
            ("Missed-call follow-up", "Every missed call is flagged so reception can ring back and protect recalls."),
            ("Compliant call recording", "Recordings stored securely and linked to the patient record."),
        ],
    },
    "Solicitors & Legal Practices": {
        "sector_plural": "law firms",
        "subject": "Calls logged straight to the matter at {company}",
        "pain": "Fee earners are rarely at their desk, clients expect to reach the right person first time, and phone time often never reaches the matter in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which system you run and roughly how many users, and I'll send an indicative quote.",
        "challenges": [
            ("Fee earners away from the desk", "Calls bounce around the office or go to voicemail."),
            ("Unrecorded billable time", "Phone time isn't captured against the matter, so it's never billed."),
            ("Multiple offices, multiple systems", "Branches that can't transfer calls between each other easily."),
        ],
        "outcomes": [
            ("Dial from the matter", "Click-to-call from the client or matter record in your case management system."),
            ("Softphone anywhere", "Fee earners take calls on laptop or mobile securely, on the firm's number."),
            ("Duration & recordings on file", "Call time and recordings logged against the matter for billing and compliance."),
            ("One system, every office", "Reception, fee earners and branches on one platform with simple transfers."),
        ],
    },
    "Accountants & Auditors": {
        "sector_plural": "accountancy practices",
        "subject": "Client calls logged automatically at {company}",
        "pain": "Around deadlines the phones don't stop, clients expect you to know who they are, and call time rarely gets captured in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with your team size and practice software, and I'll send an indicative quote.",
        "challenges": [
            ("Deadline call surges", "January and year-end bring call spikes the team can't keep up with."),
            ("Unbilled advice time", "Quick calls add up but rarely make it onto a timesheet."),
            ("Hybrid teams", "Staff split between home and office struggle to transfer calls smoothly."),
        ],
        "outcomes": [
            ("Client identified on arrival", "The client's details pop up before you say hello."),
            ("Automatic call logging", "Calls logged against the client record, with duration for time tracking."),
            ("Desk to laptop in one tap", "Seamless transfers between desk phones and softphones for hybrid staff."),
            ("Lower fixed costs", "Line rental and call costs consolidated onto one cloud platform."),
        ],
    },
    "General Medical Clinics": {
        "sector_plural": "clinics",
        "subject": "Shorter phone queues for patients at {company}",
        "pain": "Peak-hour queues put pressure on the front desk, and staff often have to search {crms} before they can help.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many lines or handsets you run, and I'll send a no-obligation overview.",
        "challenges": [
            ("Peak-hour queues", "The phones spike at opening and patients abandon the call."),
            ("Triage without context", "Staff answer without the patient's details in front of them."),
            ("Sensitive conversations", "Calls need to be recorded and stored securely."),
        ],
        "outcomes": [
            ("Patient screen-pop", "The patient's record appears as the call arrives to speed up triage."),
            ("Queueing & callbacks", "Patients hear their queue position or get a callback instead of an engaged tone."),
            ("Secure call recording", "Encrypted recordings stored against the patient record."),
            ("Easy internal transfers", "Direct routes between reception, clinicians and admin."),
        ],
    },
}

# ---- Extra sectors (added Oct 2026) ----
NEW_PRESETS = {
    "Recruitment Agencies": {
        "sic_codes": ["78100", "78200", "78300"],
        "description": "Employment placement & temporary staffing agencies",
        "search_hint": "Recruitment",
        "crms": ["Bullhorn", "Vincere", "Firefish", "Mercury"],
        "primary_hook": "ATS / CRM Integration (Bullhorn / Vincere / Firefish)",
        "fallback_greeting": "Recruitment Team",
        "pitch_bullets": [
            "Candidate and client records pop up the moment they call",
            "Click-to-dial from your ATS, with every call logged automatically",
            "Call recording for compliance, coaching and disputes",
            "Call stats per consultant, ready for your KPI boards",
        ],
        "default_cta": "Let me know which ATS you use and how many consultants you have, and I'll send an indicative quote.",
    },
    "Financial Advisers & Mortgage Brokers": {
        "sic_codes": ["66190"],
        "description": "Financial advice, mortgage & wealth management activities",
        "search_hint": "Financial",
        "crms": ["Intelliflo", "Iress Xplan", "Mortgage Brain", "Salesforce"],
        "primary_hook": "Back-office Integration (Intelliflo / Xplan) & FCA-ready recording",
        "fallback_greeting": "Advice Team",
        "pitch_bullets": [
            "Secure call recording to support FCA record-keeping",
            "Client record screen-pop from your back-office system",
            "Click-to-dial and automatic call logging against the client file",
            "Calls routed to the right adviser, wherever they're working",
        ],
        "default_cta": "Let me know which back-office system you use and how many advisers you have, and I'll send an indicative quote.",
    },
    "Insurance Brokers": {
        "sic_codes": ["66220"],
        "description": "Activities of insurance agents & brokers",
        "search_hint": "Insurance",
        "crms": ["Acturis", "Applied Epic", "OpenGI", "SSP"],
        "primary_hook": "Broking Platform Integration (Acturis / Applied Epic / OpenGI)",
        "fallback_greeting": "Broking Team",
        "pitch_bullets": [
            "Policyholder record pops up before you answer",
            "Recorded calls stored for compliance and claims disputes",
            "Renewal and claims calls queued to the right team",
            "Missed calls flagged so renewals don't slip away",
        ],
        "default_cta": "Let me know which broking platform you use and roughly how many staff take calls, and I'll send a quote.",
    },
    "Car Dealers & Garages": {
        "sic_codes": ["45111", "45112", "45200"],
        "description": "Motor vehicle sales, servicing & repair",
        "search_hint": "Motors",
        "crms": ["Keyloop", "Pinewood", "MAM Autowork", "GarageHive"],
        "primary_hook": "DMS Integration (Keyloop / Pinewood / MAM)",
        "fallback_greeting": "Sales & Service Team",
        "pitch_bullets": [
            "Customer and vehicle record on screen as the phone rings",
            "Sales, service and parts calls routed to the right desk",
            "Missed-call alerts so no sales enquiry goes cold",
            "Call recording to settle disputes and coach the team",
        ],
        "default_cta": "Let me know which DMS you use and how many handsets you run, and I'll send an indicative quote.",
    },
    "Veterinary Practices": {
        "sic_codes": ["75000"],
        "description": "Veterinary activities",
        "search_hint": "Vets",
        "crms": ["RxWorks", "Provet Cloud", "Robovet", "VetIT"],
        "primary_hook": "Practice System Integration (RxWorks / Provet / Robovet)",
        "fallback_greeting": "Practice Team",
        "pitch_bullets": [
            "Client and pet record pops up the moment they call",
            "Smart queues for the morning rush and emergency calls",
            "Out-of-hours routing to your on-call vet or partner service",
            "Missed calls flagged so every booking is followed up",
        ],
        "default_cta": "Let me know which practice system you use and how many handsets you have, and I'll send a no-obligation quote.",
    },
    "Opticians": {
        "sic_codes": ["47782"],
        "description": "Retail sale by opticians",
        "search_hint": "Opticians",
        "crms": ["Optix", "Ocuco Acuitas", "Opticabase", "Optisoft"],
        "primary_hook": "Practice System Integration (Optix / Acuitas / Opticabase)",
        "fallback_greeting": "Practice Team",
        "pitch_bullets": [
            "Patient record on screen before you answer",
            "Recall and appointment calls queued, not lost",
            "Missed calls flagged so bookings are always returned",
            "One number across branches, routed to whoever's free",
        ],
        "default_cta": "Let me know which practice system you use and how many branches you have, and I'll send an indicative quote.",
    },
    "Property & Block Management": {
        "sic_codes": ["68320"],
        "description": "Management of real estate on a fee or contract basis",
        "search_hint": "Property Management",
        "crms": ["Qube", "Fixflo", "PropertyFile", "Arthur Online"],
        "primary_hook": "Property System Integration (Qube / Fixflo / Arthur)",
        "fallback_greeting": "Property Management Team",
        "pitch_bullets": [
            "Resident, landlord or block record pops up on every call",
            "Out-of-hours and emergency repair calls routed correctly",
            "Every call logged against the property for an audit trail",
            "Peak-time queues so residents aren't left on hold",
        ],
        "default_cta": "Let me know which system you manage your portfolio in and how many staff take calls, and I'll send a quote.",
    },
    "Hotels & Hospitality": {
        "sic_codes": ["55100", "56101", "56302"],
        "description": "Hotels, restaurants, pubs & bars",
        "search_hint": "Hotel",
        "crms": ["Guestline", "Mews", "ResDiary", "OpenTable"],
        "primary_hook": "Booking System Integration (Guestline / Mews / ResDiary)",
        "fallback_greeting": "Reservations Team",
        "pitch_bullets": [
            "Guest booking details on screen as the phone rings",
            "Reservation calls answered even when the team is busy",
            "Room-to-reception and kitchen extensions that just work",
            "Missed booking calls flagged so revenue isn't lost",
        ],
        "default_cta": "Let me know which booking system you use and how many handsets you need, and I'll send an indicative quote.",
    },
    "Care Homes & Home Care": {
        "sic_codes": ["87100", "87300", "88100"],
        "description": "Residential care, nursing homes & domiciliary care",
        "search_hint": "Care",
        "crms": ["Person Centred Software", "Birdie", "CareDocs", "Access Care Planning"],
        "primary_hook": "Care System Integration & Reliable Family Contact",
        "fallback_greeting": "Care Team",
        "pitch_bullets": [
            "Families reach the right person first time, day or night",
            "Calls routed to carers' mobiles when they're on the floor",
            "Recorded calls for safeguarding and complaints",
            "Reliable lines ahead of the January 2027 analogue switch-off",
        ],
        "default_cta": "Let me know how many sites and handsets you run, and I'll send a no-obligation quote.",
    },
    "Trades & Building Services": {
        "sic_codes": ["43220", "43210"],
        "description": "Plumbing, heating & electrical installation",
        "search_hint": "Heating",
        "crms": ["simPRO", "Commusoft", "Joblogic", "ServiceM8"],
        "primary_hook": "Job Management Integration (simPRO / Commusoft / Joblogic)",
        "fallback_greeting": "Office Team",
        "pitch_bullets": [
            "Customer and job history on screen as they call",
            "Calls follow engineers to their mobiles on site",
            "Every missed call flagged, because a missed call is a missed job",
            "Call recording to settle quote and booking disputes",
        ],
        "default_cta": "Let me know which job management system you use and how many engineers and office staff you have, and I'll send a quote.",
    },
    "Contact Centres & Customer Service": {
        "sic_codes": ["82200"],
        "description": "Activities of call centres",
        "search_hint": "Contact Centre",
        "crms": ["Salesforce", "Zendesk", "Freshdesk", "HubSpot"],
        "primary_hook": "Contact Centre Platform (queues, wallboards, CRM integration)",
        "fallback_greeting": "Operations Team",
        "pitch_bullets": [
            "Live wallboards and real-time queue stats",
            "Skills-based routing to the right agent first time",
            "Call recording and quality scoring with Call Scope",
            "Screen-pop and logging into Salesforce, Zendesk or HubSpot",
        ],
        "default_cta": "Let me know how many agents you run and which CRM you use, and I'll send an indicative quote.",
    },
}

NEW_COPY = {
    "Recruitment Agencies": {
        "sector_plural": "recruitment agencies",
        "subject": "Every candidate call logged in your ATS, {company}",
        "pain": "Consultants live on the phone, but calls rarely make it into {crms}, and a missed call from a candidate or client often goes to a competitor.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which ATS you use and how many consultants you have, and I'll send an indicative quote.",
        "challenges": [
            ("Calls missing from the ATS", "Consultants forget to log calls, so the record is never complete."),
            ("Missed candidate calls", "Candidates who can't get through accept the next agency's offer."),
            ("No view of activity", "Managers can't see call volumes per consultant without chasing spreadsheets."),
        ],
        "outcomes": [
            ("Screen-pop from your ATS", "The candidate or client record opens the moment the phone rings."),
            ("Automatic call logging", "Every call, duration and recording saved against the right record."),
            ("Consultant call stats", "Live call activity per consultant for KPIs and coaching."),
            ("Missed-call recovery", "Missed calls flagged instantly so no placement slips away."),
        ],
    },
    "Financial Advisers & Mortgage Brokers": {
        "sector_plural": "financial advisers and mortgage brokers",
        "subject": "FCA-ready call recording for {company}",
        "pain": "Advisers move between the office, home and client meetings, calls need to be recorded for compliance, and client notes still end up typed into {crms} by hand.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which back-office system you use and how many advisers you have, and I'll send an indicative quote.",
        "challenges": [
            ("Recording obligations", "Calls need to be recorded and easy to find when compliance asks."),
            ("Advisers on the move", "Clients struggle to reach the right adviser away from the office."),
            ("Manual file notes", "Call details are retyped into the back-office system after the fact."),
        ],
        "outcomes": [
            ("Secure call recording", "Every call recorded, stored securely and easy to retrieve."),
            ("Client screen-pop", "The client file opens from your back-office system as the phone rings."),
            ("Calls on any device", "Advisers take calls on the business number from desk, laptop or mobile."),
            ("Automatic call logging", "Calls saved against the client record, ready for reviews."),
        ],
    },
    "Insurance Brokers": {
        "sector_plural": "insurance brokers",
        "subject": "Faster renewals and claims calls at {company}",
        "pain": "Renewal season brings call peaks, claims callers are often stressed, and staff still search {crms} while the client waits.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which broking platform you use and how many staff take calls, and I'll send a quote.",
        "challenges": [
            ("Renewal peaks", "Clients who can't get through at renewal time shop around."),
            ("Searching while clients wait", "Staff look up policies manually on every call."),
            ("Evidence for disputes", "Without recordings, it's your word against theirs."),
        ],
        "outcomes": [
            ("Policyholder screen-pop", "The client and policy record opens as the phone rings."),
            ("Renewal & claims routing", "Calls go straight to the right team, with queues for busy times."),
            ("Compliant call recording", "Recordings stored securely and linked to the client."),
            ("Missed-call follow-up", "Every missed call is flagged so renewals aren't lost."),
        ],
    },
    "Car Dealers & Garages": {
        "sector_plural": "car dealers and garages",
        "subject": "No more missed sales calls at {company}",
        "pain": "Sales, service and parts calls all land on the same lines, enquiries get missed when the team is with customers, and nobody can see the caller's history in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which DMS you use and how many handsets you run, and I'll send an indicative quote.",
        "challenges": [
            ("Missed sales enquiries", "A buyer who can't get through rings the next dealer on the list."),
            ("Calls to the wrong desk", "Service and parts calls bounce around before reaching the right person."),
            ("No caller history", "Staff can't see the customer's vehicle or last visit when they answer."),
        ],
        "outcomes": [
            ("Customer & vehicle screen-pop", "Their record from your DMS appears as the phone rings."),
            ("Department routing", "Sales, service and parts calls reach the right team first time."),
            ("Missed-call alerts", "Every missed enquiry is flagged for a quick call back."),
            ("Call recording", "Settle disputes and coach the team with recorded calls."),
        ],
    },
    "Veterinary Practices": {
        "sector_plural": "veterinary practices",
        "subject": "Fewer missed client calls at {company}",
        "pain": "Mornings are a scramble, urgent calls need to reach a vet fast, and reception searches {crms} on every call.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which practice system you use and how many handsets you have, and I'll send a no-obligation quote.",
        "challenges": [
            ("Morning call peaks", "Clients wait on hold or give up while reception is busy."),
            ("Urgent calls", "Emergencies need to reach the right person immediately."),
            ("Searching while the client waits", "Staff look up client and pet records on every call."),
        ],
        "outcomes": [
            ("Client & pet screen-pop", "The record appears on screen as the phone rings."),
            ("Smart queues & priority routing", "Urgent calls jump the queue and reach a vet quickly."),
            ("Out-of-hours routing", "Calls go to your on-call vet or partner service automatically."),
            ("Missed-call follow-up", "Every missed call is flagged so bookings are returned."),
        ],
    },
    "Opticians": {
        "sector_plural": "opticians",
        "subject": "Every recall call answered at {company}",
        "pain": "Recall and appointment calls come in while staff are with patients, missed calls rarely leave a message, and records sit in {crms} rather than on screen.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which practice system you use and how many branches you have, and I'll send an indicative quote.",
        "challenges": [
            ("Calls while staff are with patients", "The phone rings out during testing and dispensing."),
            ("Lost recall bookings", "Patients who can't get through put their eye test off."),
            ("Multi-branch juggling", "Calls don't reach the branch or colleague who's free."),
        ],
        "outcomes": [
            ("Patient screen-pop", "The patient record appears as the phone rings."),
            ("Call queueing", "Callers hold briefly instead of ringing out."),
            ("Missed-call follow-up", "Every missed call is flagged so bookings are returned."),
            ("One number, every branch", "Calls routed to whichever branch or colleague is free."),
        ],
    },
    "Property & Block Management": {
        "sector_plural": "property and block managers",
        "subject": "Every resident call logged at {company}",
        "pain": "Residents call about repairs at all hours, landlords expect quick answers, and call details rarely reach {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which system you manage your portfolio in and how many staff take calls, and I'll send a quote.",
        "challenges": [
            ("Out-of-hours emergencies", "Urgent repair calls need to reach someone, whatever the time."),
            ("No audit trail", "Disputes are hard to settle without a record of who said what."),
            ("Answering blind", "Staff search for the block or resident while the caller waits."),
        ],
        "outcomes": [
            ("Resident & property screen-pop", "The block, unit or landlord record appears as the phone rings."),
            ("Emergency routing", "Out-of-hours calls go straight to the on-call team."),
            ("Calls logged to the property", "Every call and recording saved for a clear audit trail."),
            ("Queues for busy periods", "Residents hold briefly instead of ringing out."),
        ],
    },
    "Hotels & Hospitality": {
        "sector_plural": "hotels and hospitality businesses",
        "subject": "Never miss a booking call at {company}",
        "pain": "Reservation calls come in while the team is busy with guests, missed calls are lost bookings, and guest details sit in {crms} rather than on screen.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which booking system you use and how many handsets you need, and I'll send an indicative quote.",
        "challenges": [
            ("Missed reservation calls", "Guests who can't get through book somewhere else."),
            ("Busy front desk", "Reception juggles guests in person and on the phone."),
            ("Outdated room phones", "Old internal systems are costly and unreliable."),
        ],
        "outcomes": [
            ("Guest screen-pop", "Booking details appear as the phone rings."),
            ("Overflow & queueing", "Busy calls overflow to another team instead of ringing out."),
            ("Modern extensions", "Reception, rooms, kitchen and office on one simple system."),
            ("Missed-call alerts", "Every missed booking call is flagged for a call back."),
        ],
    },
    "Care Homes & Home Care": {
        "sector_plural": "care providers",
        "subject": "Families reach the right carer at {company}",
        "pain": "Families want reassurance, carers are rarely near a desk phone, and many homes still rely on lines affected by the analogue switch-off.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many sites and handsets you run, and I'll send a no-obligation quote.",
        "challenges": [
            ("Calls ringing out", "Carers are with residents, so the phone goes unanswered."),
            ("Night and weekend cover", "Calls need to reach whoever is on shift."),
            ("Analogue lines", "Alarms and lines need to be ready for the January 2027 switch-off."),
        ],
        "outcomes": [
            ("Calls on carers' mobiles", "The care line rings on mobiles or cordless handsets around the home."),
            ("Shift-based routing", "Calls follow your rota, day and night."),
            ("Call recording", "Recordings support safeguarding and complaint handling."),
            ("Future-proof lines", "Digital phones ready for the analogue switch-off."),
        ],
    },
    "Trades & Building Services": {
        "sector_plural": "trade and building services firms",
        "subject": "A missed call is a missed job, {company}",
        "pain": "Engineers are on site, the office is stretched, and customers who can't get through call the next firm on Google. Job details stay locked in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which job management system you use and how many engineers and office staff you have, and I'll send a quote.",
        "challenges": [
            ("Missed new-job calls", "Customers ring the next firm if nobody answers."),
            ("Engineers away from the office", "Calls can't reach the right person on site."),
            ("No job history to hand", "The office searches for the customer while they wait."),
        ],
        "outcomes": [
            ("Customer & job screen-pop", "Their history from your job system appears as the phone rings."),
            ("Calls on engineers' mobiles", "The business number follows the team on site."),
            ("Missed-call alerts", "Every missed call is flagged so no job is lost."),
            ("Call recording", "Settle quote and booking disputes with recorded calls."),
        ],
    },
    "Contact Centres & Customer Service": {
        "sector_plural": "contact centres",
        "subject": "Live queue insight for {company}",
        "pain": "Queues build without warning, supervisors can't see who's free, and agents switch between the phone and {crms} on every call.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many agents you run and which CRM you use, and I'll send an indicative quote.",
        "challenges": [
            ("Queues you can't see", "Supervisors only find out about waits when customers complain."),
            ("Calls to the wrong agent", "Callers are transferred around before they reach the right skill."),
            ("Quality checks by hand", "Listening back and scoring calls takes hours."),
        ],
        "outcomes": [
            ("Live wallboards", "Calls waiting, wait times and agent status in real time."),
            ("Skills-based routing", "Callers reach the right agent first time."),
            ("Call Scope quality scoring", "Recordings, analytics and QC in one place."),
            ("CRM screen-pop", "Customer records open automatically, with every call logged."),
        ],
    },
}

NEW_PLACE_RULES = {
    "Recruitment Agencies": {"types": {"employment_agency"},
                             "words": ("recruitment", "recruit", "staffing", "personnel", "resourcing", "talent", "careers")},
    "Financial Advisers & Mortgage Brokers": {"types": {"finance"},
                                              "words": ("financial", "wealth", "mortgage", "mortgages", "advisers", "advisors", "ifa", "planning", "finance")},
    "Insurance Brokers": {"types": {"insurance_agency"}, "words": ("insurance", "brokers", "broker", "insure")},
    "Car Dealers & Garages": {"types": {"car_dealer", "car_repair"},
                              "words": ("motors", "motor", "garage", "autos", "auto", "cars", "car", "vehicle", "vehicles", "tyres", "mot")},
    "Veterinary Practices": {"types": {"veterinary_care"}, "words": ("vet", "vets", "veterinary", "animal", "pet")},
    "Opticians": {"types": {"optician"}, "words": ("optician", "opticians", "eyecare", "optometrist", "optometrists", "eyewear", "vision", "eye")},
    "Property & Block Management": {"types": {"real_estate_agency"},
                                    "words": ("property", "properties", "management", "block", "estates", "residential", "lettings")},
    "Hotels & Hospitality": {"types": {"lodging", "hotel", "restaurant", "bar", "pub"},
                             "words": ("hotel", "inn", "restaurant", "bar", "kitchen", "lodge", "arms", "tavern", "bistro")},
    "Care Homes & Home Care": {"types": {"nursing_home"},
                               "words": ("care", "nursing", "healthcare", "residential", "homecare", "living", "carers")},
    "Trades & Building Services": {"types": {"plumber", "electrician", "general_contractor"},
                                   "words": ("plumbing", "heating", "electrical", "electrics", "gas", "building", "services", "installations", "boilers")},
    "Contact Centres & Customer Service": {"types": set(),
                                           "words": ("contact", "centre", "call", "customer", "service", "communications", "telemarketing", "support")},
}

# Lead Revival: words that point a CRM lead at each sector pitch
NEW_KEYWORDS = {
    "Recruitment Agencies": ("recruit", "staffing", "personnel", "resourcing", "employment agency"),
    "Financial Advisers & Mortgage Brokers": ("financial advi", "wealth", "mortgage", "ifa ", "financial planning"),
    "Insurance Brokers": ("insurance",),
    "Car Dealers & Garages": ("motors", "garage", "car sales", "autos", "vehicle", "tyres", "automotive"),
    "Veterinary Practices": ("veterinar", " vets", "vet group", "animal hospital"),
    "Opticians": ("optician", "optometr", "eyecare", "eye care"),
    "Property & Block Management": ("block management", "property management", "residential management"),
    "Hotels & Hospitality": ("hotel", "restaurant", "hospitality", " inn", "tavern"),
    "Care Homes & Home Care": ("care home", "nursing home", "home care", "homecare", "domiciliary", "care services"),
    "Trades & Building Services": ("plumbing", "heating", "electrical", "electrician", "gas services", "boiler"),
    "Contact Centres & Customer Service": ("contact centre", "call centre", "telemarketing", "customer service"),
}

# ---- More sectors: office-based firms that almost always publish an email address ----
MORE_PRESETS = {
    "Architects & Surveyors": {
        "sic_codes": ["71111", "71112", "74902"],
        "description": "Architectural, planning & quantity surveying practices",
        "search_hint": "Architects",
        "crms": ["Archioffice", "Synergy", "Mosaic", "Microsoft 365"],
        "primary_hook": "Project-based call logging & mobile working",
        "fallback_greeting": "Practice Team",
        "pitch_bullets": [
            "Client and project calls logged against the right job automatically",
            "Architects on site take office calls on their mobile app, on the business number",
            "Call recording for instructions, variations and disputes",
            "One number for every office, routed to whoever's free",
        ],
        "default_cta": "Let me know how many people take calls across the practice, and I'll send an indicative quote.",
    },
    "Physiotherapy & Private Clinics": {
        "sic_codes": ["86900", "86220"],
        "description": "Physiotherapy, chiropractic, osteopathy & private specialist clinics",
        "search_hint": "Clinic",
        "crms": ["Cliniko", "Jane", "WriteUpp", "Semble"],
        "primary_hook": "Booking System Integration (Cliniko / Jane / WriteUpp)",
        "fallback_greeting": "Clinic Team",
        "pitch_bullets": [
            "Patient record on screen the moment they call",
            "Calls queue instead of ringing out while practitioners are treating",
            "Missed calls flagged so every booking enquiry is returned",
            "Practitioners take calls on the clinic number from their mobile",
        ],
        "default_cta": "Let me know which booking system you use and how many people answer the phone, and I'll send a quote.",
    },
    "Funeral Directors": {
        "sic_codes": ["96030"],
        "description": "Funeral and related activities",
        "search_hint": "Funeral",
        "crms": ["Funeral Manager", "Arka", "Halo", "Microsoft 365"],
        "primary_hook": "24/7 call handling that never misses a family",
        "fallback_greeting": "Funeral Team",
        "pitch_bullets": [
            "Calls follow the on-call director to their mobile, day and night",
            "Every call answered, with overflow to a trained answering team if needed",
            "One number across every branch",
            "Recorded calls for arrangements and peace of mind",
        ],
        "default_cta": "Let me know how many branches and directors take calls, and I'll send an indicative quote.",
    },
    "Nurseries & Childcare": {
        "sic_codes": ["85100", "88910"],
        "description": "Pre-school, nursery & child day-care providers",
        "search_hint": "Nursery",
        "crms": ["Famly", "Blossom", "iConnect", "Connect Childcare"],
        "primary_hook": "Parent calls answered, even when staff are in the room",
        "fallback_greeting": "Nursery Manager",
        "pitch_bullets": [
            "Calls ring the office and the manager's mobile together",
            "Calls queue instead of ringing out during drop-off and pick-up",
            "Missed calls from parents and new enquiries flagged straight away",
            "One number across every setting",
        ],
        "default_cta": "Let me know how many settings you run and who answers the phone, and I'll send a quote.",
    },
    "Marketing & Creative Agencies": {
        "sic_codes": ["73110", "74100", "70210"],
        "description": "Advertising, design, PR & communications agencies",
        "search_hint": "Agency",
        "crms": ["HubSpot", "Pipedrive", "Salesforce", "Monday.com"],
        "primary_hook": "CRM Integration (HubSpot / Pipedrive / Salesforce)",
        "fallback_greeting": "Agency Team",
        "pitch_bullets": [
            "Click-to-dial from HubSpot or Pipedrive, with every call logged",
            "Softphone on laptop and mobile for a hybrid team",
            "Client calls routed to the account manager, wherever they are",
            "Call recording for briefs, approvals and new business calls",
        ],
        "default_cta": "Let me know which CRM you use and how many people are in the team, and I'll send an indicative quote.",
    },
    "Business Consultants": {
        "sic_codes": ["70229"],
        "description": "Management & business consultancy",
        "search_hint": "Consulting",
        "crms": ["HubSpot", "Salesforce", "Pipedrive", "Microsoft Dynamics"],
        "primary_hook": "A professional business number on every device",
        "fallback_greeting": "Consulting Team",
        "pitch_bullets": [
            "One business number on desk, laptop and mobile",
            "Calls logged in your CRM automatically",
            "Recorded calls for client instructions and coaching",
            "Call routing so clients always reach a person",
        ],
        "default_cta": "Let me know how many consultants you have and which CRM you use, and I'll send a quote.",
    },
    "Cleaning & Facilities Services": {
        "sic_codes": ["81210", "81221", "81222", "81229"],
        "description": "Commercial cleaning, window cleaning & facilities services",
        "search_hint": "Cleaning",
        "crms": ["CleanDesk", "Swept", "Jobber", "ServiceM8"],
        "primary_hook": "Job-system integration & mobile teams",
        "fallback_greeting": "Operations Team",
        "pitch_bullets": [
            "New contract enquiries answered, not lost to voicemail",
            "Supervisors take office calls on their mobile app",
            "Every call logged against the client and site",
            "Out-of-hours calls routed to whoever is on duty",
        ],
        "default_cta": "Let me know how many office staff and supervisors take calls, and I'll send an indicative quote.",
    },
    "Removals & Storage": {
        "sic_codes": ["49420", "52103"],
        "description": "Removal services, self-storage & warehousing",
        "search_hint": "Removals",
        "crms": ["MoveMan", "Moveware", "Removals Manager", "SpaceManager"],
        "primary_hook": "Quote enquiries answered first time",
        "fallback_greeting": "Removals Team",
        "pitch_bullets": [
            "Every quote enquiry answered, even when the team is out on a move",
            "Calls ring the office and surveyors' mobiles together",
            "Missed calls flagged so no booking goes to a competitor",
            "Recorded calls for quotes, inventories and disputes",
        ],
        "default_cta": "Let me know how many people take bookings, and I'll send an indicative quote.",
    },
    "Travel Agents": {
        "sic_codes": ["79110", "79120", "79909"],
        "description": "Travel agencies & tour operators",
        "search_hint": "Travel",
        "crms": ["Travelport", "Dolphin Dynamics", "Inspiretec", "TravelPerk"],
        "primary_hook": "Booking-system screen-pop & homeworker routing",
        "fallback_greeting": "Travel Team",
        "pitch_bullets": [
            "Customer booking on screen as the phone rings",
            "Homeworkers on the same number, with calls routed to them",
            "Calls recorded for bookings, changes and complaints",
            "Queue messages and callbacks at busy times",
        ],
        "default_cta": "Let me know how many consultants (including homeworkers) you have, and I'll send a quote.",
    },
    "Pharmacies": {
        "sic_codes": ["47730"],
        "description": "Dispensing chemists & independent pharmacies",
        "search_hint": "Pharmacy",
        "crms": ["PharmOutcomes", "ProScript", "Titan", "Positive Solutions"],
        "primary_hook": "Prescription calls queued, not lost",
        "fallback_greeting": "Pharmacy Team",
        "pitch_bullets": [
            "Calls queue with a message instead of ringing out at the counter",
            "Options to route prescription, delivery and GP calls",
            "Missed calls flagged so patients get a call back",
            "One number across every branch",
        ],
        "default_cta": "Let me know how many branches and phones you have, and I'll send an indicative quote.",
    },
    "Charities & Membership Organisations": {
        "sic_codes": ["88990", "94990"],
        "description": "Charities, community groups & membership bodies",
        "search_hint": "Trust",
        "crms": ["Beacon", "Donorfy", "Salesforce Nonprofit", "Raiser's Edge"],
        "primary_hook": "Lower costs and staff, volunteers and helplines on one system",
        "fallback_greeting": "Office Team",
        "pitch_bullets": [
            "Staff and volunteers on one system, on desk, laptop or mobile",
            "Helpline calls queued and routed to whoever's available",
            "Calls logged against supporters in your CRM",
            "Lower monthly costs than traditional lines",
        ],
        "default_cta": "Let me know how many staff and volunteers take calls, and I'll send an indicative quote.",
    },
    "Training & Education Providers": {
        "sic_codes": ["85590", "85600"],
        "description": "Training companies, tutors & education support services",
        "search_hint": "Training",
        "crms": ["Accelerate", "Arlo", "HubSpot", "Bud"],
        "primary_hook": "Course enquiries answered and logged",
        "fallback_greeting": "Training Team",
        "pitch_bullets": [
            "Every course enquiry answered and logged",
            "Trainers take calls on the business number while out delivering",
            "Click-to-dial from your CRM",
            "Call stats to see how many enquiries you're getting",
        ],
        "default_cta": "Let me know how many people take enquiries, and I'll send an indicative quote.",
    },
    "Gyms & Fitness Studios": {
        "sic_codes": ["93130"],
        "description": "Gyms, fitness studios & leisure facilities",
        "search_hint": "Fitness",
        "crms": ["Glofox", "Mindbody", "TeamUp", "ClubRight"],
        "primary_hook": "Membership enquiries answered while staff are on the floor",
        "fallback_greeting": "Studio Team",
        "pitch_bullets": [
            "Calls ring reception and staff mobiles together",
            "Membership enquiries never lost to voicemail",
            "Missed calls flagged so new members are called back",
            "Wi-Fi and phones from one supplier",
        ],
        "default_cta": "Let me know how many sites and staff take calls, and I'll send an indicative quote.",
    },
    "Hair & Beauty Salons": {
        "sic_codes": ["96020"],
        "description": "Hairdressers, barbers & beauty salons",
        "search_hint": "Salon",
        "crms": ["Phorest", "Fresha", "Timely", "Treatwell"],
        "primary_hook": "Bookings answered while you're with clients",
        "fallback_greeting": "Salon Team",
        "pitch_bullets": [
            "Calls ring reception and the salon mobile together",
            "Callers hear a message and queue instead of ringing out",
            "Missed booking calls flagged so you can call back",
            "Card-payment-ready broadband and Wi-Fi",
        ],
        "default_cta": "Let me know how many salons and phones you have, and I'll send an indicative quote.",
    },
}

MORE_COPY = {
    "Architects & Surveyors": {
        "sector_plural": "architects and surveyors",
        "subject": "Never miss a client call on site, {company}",
        "pain": "Your team spends much of the week on site or at meetings, clients call the office for updates, and call notes rarely make it into {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many people take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Out on site", "Clients can't reach the architect or surveyor they need."),
            ("Instructions by phone", "Changes agreed on calls aren't recorded anywhere."),
            ("Several offices", "Calls don't reach the person who's free."),
        ],
        "outcomes": [
            ("Mobile app on the business number", "Take and make office calls from site."),
            ("Call recording", "Instructions and variations recorded for reference."),
            ("Smart routing", "Calls ring the right person, wherever they are."),
            ("Call logging", "Every call saved against the client or project."),
        ],
    },
    "Physiotherapy & Private Clinics": {
        "sector_plural": "physiotherapy and private clinics",
        "subject": "Every booking call answered at {company}",
        "pain": "Practitioners are with patients most of the day, so calls ring out, new enquiries go elsewhere, and records live in {crms} instead of on screen.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which booking system you use and how many people answer the phone, and I'll send a quote.",
        "challenges": [
            ("Calls during treatment", "The phone rings out while everyone is with a patient."),
            ("Lost new patients", "Enquiries that can't get through book with another clinic."),
            ("Typing notes after calls", "Call details are added to the record by hand."),
        ],
        "outcomes": [
            ("Patient screen-pop", "The record appears as the phone rings."),
            ("Call queueing", "Callers hold briefly instead of ringing out."),
            ("Missed-call follow-up", "Every missed call flagged so bookings are returned."),
            ("Calls on any device", "Practitioners use the clinic number on their mobile."),
        ],
    },
    "Funeral Directors": {
        "sector_plural": "funeral directors",
        "subject": "Every family's call answered, day and night, at {company}",
        "pain": "Families call at any hour, the on-call director is often out, and a missed call at the worst moment is hard to recover from.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many branches and directors take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Out-of-hours calls", "Calls need to reach whoever is on call, instantly."),
            ("Several branches", "Families call one branch while staff are at another."),
            ("Directors away from the desk", "Arrangements and services take people out of the office."),
        ],
        "outcomes": [
            ("On-call routing", "Calls follow the duty director to their mobile."),
            ("Overflow answering", "A trained team picks up if nobody can."),
            ("One number, every branch", "Calls reach whoever is free."),
            ("Recorded calls", "Arrangements kept on record for peace of mind."),
        ],
    },
    "Nurseries & Childcare": {
        "sector_plural": "nurseries and childcare providers",
        "subject": "Parent calls answered at {company}, even at drop-off",
        "pain": "Staff are in the rooms with the children, the office phone rings out at the busiest times, and new parents who can't get through call the next nursery.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many settings you run, and I'll send a quote.",
        "challenges": [
            ("Busy drop-off and pick-up", "Calls ring out when everyone is with the children."),
            ("Lost enquiries", "New parents who can't get through look elsewhere."),
            ("Manager away from the office", "Important calls wait until they're back."),
        ],
        "outcomes": [
            ("Ring office and mobile together", "Whoever is free picks up."),
            ("Call queueing", "Parents hear a message instead of ringing out."),
            ("Missed-call alerts", "Every missed call flagged for a call back."),
            ("One number, every setting", "Calls routed to the right nursery."),
        ],
    },
    "Marketing & Creative Agencies": {
        "sector_plural": "marketing and creative agencies",
        "subject": "Every client call logged in your CRM, {company}",
        "pain": "Your team works from the studio, home and client sites, calls rarely make it into {crms}, and clients can't always reach their account manager.",
        "cta": "Worth a quick 15-minute demo? Or just reply with which CRM you use and how many people are in the team, and I'll send an indicative quote.",
        "challenges": [
            ("Hybrid working", "Calls don't follow people between studio, home and clients."),
            ("Calls missing from the CRM", "New business and client calls aren't logged."),
            ("Mobile numbers everywhere", "Clients call personal mobiles, and you lose the history."),
        ],
        "outcomes": [
            ("CRM click-to-dial", "Dial from your CRM, with every call logged."),
            ("Softphone everywhere", "The business number on laptop and mobile."),
            ("Account routing", "Clients reach their account manager first."),
            ("Call recording", "Briefs and approvals kept on record."),
        ],
    },
    "Business Consultants": {
        "sector_plural": "business consultants",
        "subject": "One professional business number for {company}",
        "pain": "Consultants spend their days at client sites, clients call mobile numbers that change when people leave, and calls rarely get logged in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many consultants you have, and I'll send a quote.",
        "challenges": [
            ("Always at client sites", "Calls reach personal mobiles or nobody at all."),
            ("Lost history", "Client calls aren't logged anywhere central."),
            ("No cover", "If someone is busy, the client waits."),
        ],
        "outcomes": [
            ("Business number on any device", "Desk, laptop and mobile, one number."),
            ("CRM call logging", "Every client call saved automatically."),
            ("Call routing", "Clients always reach someone."),
            ("Call recording", "Instructions and coaching on record."),
        ],
    },
    "Cleaning & Facilities Services": {
        "sector_plural": "cleaning and facilities firms",
        "subject": "New contract enquiries answered at {company}",
        "pain": "Supervisors are out on sites, the office is small, and new contract enquiries or client issues often land in a voicemail nobody checks.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many people take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Team out on sites", "Calls go unanswered while supervisors are working."),
            ("Client issues", "Complaints need answering quickly to keep contracts."),
            ("Out-of-hours calls", "Urgent calls need to reach whoever is on duty."),
        ],
        "outcomes": [
            ("Mobile app on the business number", "Supervisors answer office calls anywhere."),
            ("Duty routing", "Out-of-hours calls go to the right person."),
            ("Missed-call alerts", "Every enquiry flagged for a call back."),
            ("Call logging", "Calls saved against the client and site."),
        ],
    },
    "Removals & Storage": {
        "sector_plural": "removals and storage companies",
        "subject": "Every quote enquiry answered at {company}",
        "pain": "The team is out on moves and surveys, quote enquiries come in all day, and a missed call usually means a booking with someone else.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many people take bookings, and I'll send an indicative quote.",
        "challenges": [
            ("Out on moves", "Calls ring out while the team is on the road."),
            ("Price shoppers", "Customers ring three firms and book the first to answer."),
            ("Disputes", "Without recordings, it's your word against theirs."),
        ],
        "outcomes": [
            ("Office and mobiles together", "Whoever is free answers."),
            ("Missed-call alerts", "Every enquiry flagged for a call back."),
            ("Call recording", "Quotes and agreements kept on record."),
            ("Call stats", "See how many enquiries you get, and when."),
        ],
    },
    "Travel Agents": {
        "sector_plural": "travel agents",
        "subject": "Customer bookings on screen as they call {company}",
        "pain": "Customers call about bookings and changes, homeworkers need the same number as the shop, and staff search {crms} while the customer waits.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many consultants you have, and I'll send a quote.",
        "challenges": [
            ("Searching while customers wait", "Staff look bookings up on every call."),
            ("Homeworkers", "Calls don't reach consultants working from home."),
            ("Busy periods", "Peak seasons bring queues and lost calls."),
        ],
        "outcomes": [
            ("Booking screen-pop", "The customer's booking appears as the phone rings."),
            ("Homeworker routing", "Everyone on the same number, wherever they work."),
            ("Call recording", "Bookings and changes kept on record."),
            ("Queues and callbacks", "Callers wait or get a call back at busy times."),
        ],
    },
    "Pharmacies": {
        "sector_plural": "independent pharmacies",
        "subject": "Prescription calls queued, not lost, at {company}",
        "pain": "The phone rings constantly with prescription and delivery queries while the team is serving at the counter, so calls ring out and patients get frustrated.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many branches and phones you have, and I'll send an indicative quote.",
        "challenges": [
            ("Calls at the counter", "Staff can't serve and answer the phone at once."),
            ("Repeat queries", "The same prescription questions tie up the line."),
            ("Several branches", "Calls don't reach the branch that can help."),
        ],
        "outcomes": [
            ("Call queueing", "Patients hear a message instead of ringing out."),
            ("Call options", "Prescription, delivery and GP calls routed separately."),
            ("Missed-call alerts", "Patients get a call back."),
            ("One number, every branch", "Calls reach whoever is free."),
        ],
    },
    "Charities & Membership Organisations": {
        "sector_plural": "charities and membership organisations",
        "subject": "Lower phone costs and one system for {company}",
        "pain": "Staff and volunteers work from the office, home and out in the community, helplines need answering, and every pound spent on phone lines matters.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many staff and volunteers take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Rising line costs", "Old phone lines cost more every year."),
            ("People in different places", "Staff and volunteers can't share one number."),
            ("Helpline cover", "Calls need routing to whoever is available."),
        ],
        "outcomes": [
            ("Lower monthly costs", "Cloud phones cost less than old lines."),
            ("One system for everyone", "Desk, laptop or mobile, one number."),
            ("Helpline routing", "Calls queue and go to whoever's free."),
            ("CRM call logging", "Calls saved against supporters and members."),
        ],
    },
    "Training & Education Providers": {
        "sector_plural": "training providers",
        "subject": "Every course enquiry answered at {company}",
        "pain": "Trainers are out delivering courses, enquiries come in while nobody's at the desk, and calls rarely get logged in {crms}.",
        "cta": "Worth a quick 15-minute demo? Or just reply with how many people take enquiries, and I'll send an indicative quote.",
        "challenges": [
            ("Trainers out delivering", "Nobody's at the desk when enquiries come in."),
            ("Lost bookings", "Callers who can't get through book elsewhere."),
            ("No enquiry figures", "You can't see how many calls you get."),
        ],
        "outcomes": [
            ("Calls on any device", "Trainers answer on the business number anywhere."),
            ("CRM click-to-dial", "Dial from your CRM, with calls logged."),
            ("Missed-call alerts", "Every enquiry flagged for a call back."),
            ("Call stats", "See enquiry volumes at a glance."),
        ],
    },
    "Gyms & Fitness Studios": {
        "sector_plural": "gyms and fitness studios",
        "subject": "Membership enquiries answered at {company}",
        "pain": "Staff are on the gym floor or teaching classes, the phone rings out, and new members who can't get through join somewhere else.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many sites and staff take calls, and I'll send an indicative quote.",
        "challenges": [
            ("Staff on the floor", "Nobody's at reception to answer."),
            ("Lost new members", "Enquiries go to the gym down the road."),
            ("Patchy Wi-Fi", "Members and staff expect it to just work."),
        ],
        "outcomes": [
            ("Reception and mobiles together", "Whoever is free answers."),
            ("Missed-call alerts", "Every enquiry flagged for a call back."),
            ("Call queueing", "Callers hear a message instead of ringing out."),
            ("Business Wi-Fi", "Reliable Wi-Fi from the same supplier."),
        ],
    },
    "Hair & Beauty Salons": {
        "sector_plural": "hair and beauty salons",
        "subject": "Booking calls answered while you're with clients at {company}",
        "pain": "Everyone is with a client when the phone rings, callers hang up, and a missed booking call is lost income.",
        "cta": "Worth a quick 15-minute chat? Or just reply with how many salons and phones you have, and I'll send an indicative quote.",
        "challenges": [
            ("Hands full", "Nobody can answer mid-appointment."),
            ("Lost bookings", "Callers book with the next salon instead."),
            ("Card machines and Wi-Fi", "Payments and bookings depend on a good connection."),
        ],
        "outcomes": [
            ("Reception and mobile together", "Whoever is free answers."),
            ("Call queueing", "Callers hear a message instead of ringing out."),
            ("Missed-call alerts", "Every booking call flagged for a call back."),
            ("Reliable broadband", "Card payments and booking apps that just work."),
        ],
    },
}

MORE_PLACE_RULES = {
    "Architects & Surveyors": {"types": {"architect"}, "words": ("architect", "architects", "architecture", "design", "surveyor", "surveyors", "surveying", "planning")},
    "Physiotherapy & Private Clinics": {"types": {"physiotherapist", "chiropractor", "medical_clinic", "health"},
                                        "words": ("physio", "physiotherapy", "chiropractic", "chiropractor", "osteopath", "osteopathy", "clinic", "podiatry", "sports injury", "therapy")},
    "Funeral Directors": {"types": {"funeral_home"}, "words": ("funeral", "funerals", "undertaker", "undertakers", "memorial")},
    "Nurseries & Childcare": {"types": {"preschool", "child_care_agency"}, "words": ("nursery", "nurseries", "childcare", "child care", "pre-school", "preschool", "kids", "little")},
    "Marketing & Creative Agencies": {"types": {"marketing_agency"}, "words": ("marketing", "creative", "design", "digital", "media", "agency", "studio", "branding", "pr")},
    "Business Consultants": {"types": {"consultant"}, "words": ("consulting", "consultancy", "consultants", "advisory", "solutions", "partners", "management")},
    "Cleaning & Facilities Services": {"types": set(), "words": ("cleaning", "cleaners", "clean", "hygiene", "facilities", "janitorial", "window")},
    "Removals & Storage": {"types": {"moving_company", "storage"}, "words": ("removals", "removal", "storage", "movers", "moving", "relocation")},
    "Travel Agents": {"types": {"travel_agency"}, "words": ("travel", "holidays", "tours", "cruises", "journeys", "voyages")},
    "Pharmacies": {"types": {"pharmacy", "drugstore"}, "words": ("pharmacy", "chemist", "chemists", "pharmacies")},
    "Charities & Membership Organisations": {"types": set(), "words": ("trust", "charity", "foundation", "association", "society", "community", "support")},
    "Training & Education Providers": {"types": {"school"}, "words": ("training", "academy", "learning", "education", "tutors", "tuition", "courses", "skills")},
    "Gyms & Fitness Studios": {"types": {"gym", "fitness_center"}, "words": ("gym", "fitness", "studio", "pilates", "yoga", "crossfit", "strength", "boxing")},
    "Hair & Beauty Salons": {"types": {"hair_salon", "beauty_salon", "barber_shop", "hair_care", "spa"},
                             "words": ("salon", "hair", "beauty", "barber", "barbers", "nails", "spa", "aesthetics")},
}

MORE_KEYWORDS = {
    "Architects & Surveyors": ("architect", "surveyor", "surveying", "planning consult"),
    "Physiotherapy & Private Clinics": ("physio", "chiropract", "osteopath", "podiatr", "sports injury"),
    "Funeral Directors": ("funeral", "undertaker"),
    "Nurseries & Childcare": ("nursery", "childcare", "child care", "pre-school", "preschool"),
    "Marketing & Creative Agencies": ("marketing", "creative agency", "design agency", "digital agency", "advertising"),
    "Business Consultants": ("consultancy", "consulting", "management consult"),
    "Cleaning & Facilities Services": ("cleaning", "cleaners", "facilities management", "hygiene"),
    "Removals & Storage": ("removals", "removal", "self storage", "storage"),
    "Travel Agents": ("travel", "holidays", "tour operator"),
    "Pharmacies": ("pharmacy", "chemist"),
    "Charities & Membership Organisations": ("charity", "charitable", "foundation", "association"),
    "Training & Education Providers": ("training", "academy", "tuition", "tutoring"),
    "Gyms & Fitness Studios": ("gym", "fitness", "pilates", "yoga"),
    "Hair & Beauty Salons": ("salon", "hair", "beauty", "barber", "aesthetic"),
}
for _sector in ("Architects & Surveyors", "Funeral Directors", "Nurseries & Childcare", "Business Consultants",
                "Cleaning & Facilities Services", "Removals & Storage", "Pharmacies", "Charities & Membership Organisations",
                "Gyms & Fitness Studios", "Hair & Beauty Salons"):
    MORE_COPY[_sector]["intro"] = "never miss a call, wherever the team is working."
    MORE_COPY[_sector]["lead_in"] = "Our cloud phone systems give you:"
NEW_PRESETS.update(MORE_PRESETS)
NEW_COPY.update(MORE_COPY)
NEW_PLACE_RULES.update(MORE_PLACE_RULES)
NEW_KEYWORDS.update(MORE_KEYWORDS)

VERTICAL_PRESETS.update(NEW_PRESETS)
SECTOR_PLACE_RULES.update(NEW_PLACE_RULES)
SECTOR_COPY.update(NEW_COPY)

EVERYTHING_WE_DO = [
    "Cloud phone systems & softphones",
    "Desk, DECT & headset hardware",
    "Business broadband & connectivity",
    "Business mobiles",
    "Networking & Wi-Fi",
    "CCTV, security & access control",
]


def friendly_company_name(legal_name: str) -> str:
    """'HART NEW HOMES (WALSALL) LIMITED' -> 'Hart New Homes (Walsall)'."""
    name = re.sub(r"\b(LIMITED|LTD\.?|PLC|LLP|L\.L\.P\.)\s*$", "", legal_name.strip(), flags=re.I).strip(" ,.")
    if name.isupper():
        name = " ".join(
            w if (w in {"&", "UK"} or (len(w) <= 3 and not any(c in "AEIOU" for c in w) and w.isalpha()))
            else w.title()
            for w in name.split()
        )
    return name.replace(" And ", " and ").replace(" Of ", " of ").replace(" The ", " the ")


def lead_display_name(lead: "ScrapedLead") -> str:
    """The name the firm actually trades under (Google Maps) if known, else a tidied legal name."""
    trading = (getattr(lead, "trading_name", None) or "").strip()
    if trading and len(trading) <= 60:
        return trading
    return friendly_company_name(lead.company_name)


def looks_like_company_name(name: str) -> bool:
    """True if someone typed the company (e.g. 'SYComms', 'SY Comms') where their own name goes."""
    flat = re.sub(r"[^a-z]", "", (name or "").lower())
    return bool(flat) and (flat.startswith("sycom") or flat in ("sy", "sw", "sycommunications", "sycomms", "sycoms")
                           or "communications" in flat or "telecoms" in flat or flat.startswith("southwales"))


def get_sender() -> Dict[str, str]:
    sender = dict(SENDER_DEFAULTS)
    sender.update({k: v for k, v in st.session_state.get("sender_profile", {}).items() if v})
    if looks_like_company_name(sender.get("name", "")):
        sender["name"] = ""  # Sign as the company, never "I'm SYComms from SY Communications"
    return sender


def build_signature(sender: Dict[str, str]) -> str:
    lines = ["Kind regards,"]
    if sender.get("name"):
        lines.append("")
        lines.append(sender["name"])
        if sender.get("title"):
            lines.append(sender["title"])
    lines.append(SENDER_COMPANY)
    contact = " | ".join(x for x in (sender.get("phone"), sender.get("email")) if x)
    if contact:
        lines.append(contact)
    if sender.get("website"):
        lines.append(sender["website"])
    return "\n".join(lines)


def build_email_subject(lead: ScrapedLead, vertical_key: str) -> str:
    copy = SECTOR_COPY.get(vertical_key, SECTOR_COPY["Estate & Lettings Agents"])
    crms = VERTICAL_PRESETS.get(vertical_key, VERTICAL_PRESETS["Estate & Lettings Agents"])["crms"]
    return copy["subject"].format(company=lead_display_name(lead), crm1=crms[0])


def build_email_pitch(
    lead: ScrapedLead,
    vertical_key: str,
    include_attachment_line: bool = True,
    include_switchover: bool = True,
) -> str:
    config = VERTICAL_PRESETS.get(vertical_key, VERTICAL_PRESETS["Estate & Lettings Agents"])
    copy = SECTOR_COPY.get(vertical_key, SECTOR_COPY["Estate & Lettings Agents"])
    sender = get_sender()
    first_name, _ = infer_contact_name_and_role(lead, vertical_key)
    greeting_name = first_name if first_name != config["fallback_greeting"] else "there"
    company = lead_display_name(lead)
    crms = config["crms"]
    crms_str = ", ".join(crms[:2]) + f" or {crms[2]}" if len(crms) >= 3 else " or ".join(crms)

    who = f"I'm {sender['name']} from {SENDER_COMPANY}" if sender.get("name") else f"It's {SENDER_COMPANY} here"
    bullets = "\n".join(f"- {title}" for title, _ in copy["outcomes"][:4])

    parts = [
        f"Hi {greeting_name},",
        f"{who}. We help {copy['sector_plural']} like {company} "
        + copy.get("intro", "connect their phones to the software they already use."),
        copy["pain"].format(crms=crms_str),
        copy.get("lead_in", "We connect your phones to whichever system you use, so you get:"),
        bullets,
    ]
    if include_switchover:
        parts.append(SWITCHOVER_LINE)
    if include_attachment_line:
        parts.append(
            "I've attached a one-page overview of how it works."
        )
    parts.append(copy["cta"])
    parts.append(build_signature(sender))
    parts.append(
        "P.S. If this isn't relevant, just reply \"no thanks\" and I won't get in touch again."
    )
    return "\n\n".join(parts)


def _email_plain_html(body: str) -> str:
    """Plain look: the email as simple paragraphs, bullets and signature (like a personal email)."""
    blocks, out = [b for b in body.replace("\r\n", "\n").split("\n\n")], []
    for block in blocks:
        lines = [l for l in block.split("\n") if l.strip() != ""] or [""]
        if all(l.lstrip().startswith("- ") for l in lines):
            items = "".join(f"<li>{html_lib.escape(l.lstrip()[2:])}</li>" for l in lines)
            out.append(f'<ul style="margin:0 0 14px 0;padding-left:20px">{items}</ul>')
        else:
            text = "<br>".join(html_lib.escape(l) for l in block.split("\n"))
            text = re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', text)
            style = "margin:0 0 14px 0"
            if block.startswith("P.S."):
                style += ";color:#6b7280;font-size:12px"
            out.append(f'<p style="{style}">{text}</p>')
    return (
        '<html><body style="font-family:Calibri,Arial,sans-serif;font-size:14px;line-height:1.45;color:#1f2937">'
        + "".join(out) + "</body></html>"
    )


def _hex(rgb: Tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def _email_branded_html(body: str, subject: str = "") -> str:
    """Branded look: SY Communications header, feature tiles, switch-off callout, a demo button and a
    proper signature. Built from the (editable) plain-text email, using tables and inline styles only,
    so it renders in Outlook, Gmail, Apple Mail and Zoho alike. No images, so nothing is blocked."""
    purple, purple2, teal = _hex(BRAND_PURPLE), _hex(BRAND_PURPLE_2), _hex(BRAND_TEAL)
    font = "font-family:'Segoe UI',Calibri,Arial,Helvetica,sans-serif"
    sender = get_sender()
    e = html_lib.escape
    blocks = [b.strip("\n") for b in body.replace("\r\n", "\n").split("\n\n")]
    rows: List[str] = []
    sig_lines: List[str] = []
    ps = ""
    in_sig = False

    def para(text: str, extra: str = "") -> str:
        inner = "<br>".join(e(l) for l in text.split("\n"))
        return (f'<tr><td style="padding:0 36px 16px 36px;{font};font-size:15px;line-height:1.6;color:#1f2937;{extra}">'
                f"{inner}</td></tr>")

    for block in blocks:
        if not block.strip():
            continue
        first = block.lstrip()
        if first.startswith("P.S."):
            ps = block
            continue
        if in_sig or first.lower().startswith(("kind regards", "best regards", "many thanks", "regards")):
            in_sig = True
            sig_lines += [l for l in block.split("\n") if l.strip()]
            continue
        lines = [l for l in block.split("\n") if l.strip()]
        if lines and all(l.lstrip().startswith("- ") for l in lines):
            items = [l.lstrip()[2:] for l in lines]
            cells = ""
            for i in range(0, len(items), 2):
                pair = items[i:i + 2]
                tds = "".join(
                    f'<td width="50%" valign="top" style="padding:5px">'
                    f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                    f'<td style="background:#f4f2fb;border-left:4px solid {teal};border-radius:6px;padding:12px 14px;'
                    f'{font};font-size:14px;font-weight:600;color:{purple}">'
                    f'<span style="color:{teal};font-weight:700">&#10003;</span>&nbsp; {e(it)}</td></tr></table></td>'
                    for it in pair)
                if len(pair) == 1:
                    tds += '<td width="50%"></td>'
                cells += f"<tr>{tds}</tr>"
            rows.append(f'<tr><td style="padding:0 31px 14px 31px"><table role="presentation" width="100%" '
                        f'cellpadding="0" cellspacing="0" border="0">{cells}</table></td></tr>')
            continue
        low = first.lower()
        if "analogue" in low and "2027" in low:
            rows.append(
                f'<tr><td style="padding:2px 36px 18px 36px"><table role="presentation" width="100%" cellpadding="0" '
                f'cellspacing="0" border="0"><tr><td style="background:#fff7e8;border:1px solid #f5c26b;border-radius:8px;'
                f'padding:14px 16px;{font};font-size:14px;line-height:1.55;color:#7a4b00">'
                f'<strong style="color:#b45309">&#9200; BT switch-off: January 2027</strong><br>{e(block)}</td></tr></table></td></tr>')
            continue
        if low.startswith("worth a quick") or ("demo" in low and "?" in first and len(first) < 260):
            head, _, rest = first.partition("?")
            href = _secret_value("DEMO_BOOKING_URL") or (
                f"mailto:{sender.get('email', '')}?subject={quote('Demo request: ' + (subject or 'phone system'))}")
            label = "Book a 15-minute demo" if "15" in head else "Book a quick demo"
            rows.append(
                f'<tr><td align="center" style="padding:8px 36px 6px 36px">'
                f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td align="center" bgcolor="{teal}" style="border-radius:8px">'
                f'<a href="{e(href)}" style="display:inline-block;padding:13px 30px;{font};font-size:15px;font-weight:700;'
                f'color:#ffffff;text-decoration:none;border-radius:8px">{label} &rarr;</a></td></tr></table></td></tr>')
            if rest.strip():
                rows.append(para(rest.strip(), "text-align:center;font-size:14px;color:#4b5563;padding-top:10px"))
            continue
        m_link = re.match(r"^(.*?):\s*(https?://\S+)\s*$", first)
        if m_link and "\n" not in first and "form" in m_link.group(1).lower():
            rows.append(
                f'<tr><td align="center" style="padding:8px 36px 18px 36px">'
                f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td align="center" bgcolor="{teal}" style="border-radius:8px">'
                f'<a href="{e(m_link.group(2))}" style="display:inline-block;padding:13px 30px;{font};font-size:15px;'
                f'font-weight:700;color:#ffffff;text-decoration:none;border-radius:8px">{e(m_link.group(1).strip())} &rarr;</a>'
                f'</td></tr></table></td></tr>')
            continue
        if low.startswith("i've attached"):
            rows.append(para("\U0001F4CE " + block, "font-size:14px;color:#4b5563"))
            continue
        rows.append(para(block))

    # Signature block
    sig_html = ""
    if sig_lines:
        closing, rest_lines = sig_lines[0], sig_lines[1:]
        name_lines = [l for l in rest_lines if l.strip() != SENDER_COMPANY and "|" not in l and "www." not in l]
        contact = next((l for l in rest_lines if "|" in l), "")
        site = next((l for l in rest_lines if "www." in l), "")
        who = "".join(
            f'<div style="{font};font-size:{15 if i == 0 else 13}px;font-weight:{700 if i == 0 else 400};'
            f'color:{purple if i == 0 else "#4b5563"}">{e(l)}</div>' for i, l in enumerate(name_lines))
        site_html = (f'<a href="https://{e(site.strip().replace("https://", "").replace("http://", ""))}" '
                     f'style="color:{teal};text-decoration:none;font-weight:600">{e(site.strip())}</a>' if site else "")
        sig_html = (
            f'<tr><td style="padding:10px 36px 26px 36px">'
            f'<div style="{font};font-size:15px;color:#1f2937;margin-bottom:12px">{e(closing)}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="border-left:3px solid {teal};padding:2px 0 2px 14px">{who}'
            f'<div style="{font};font-size:14px;font-weight:700;color:{purple};margin-top:{4 if who else 0}px">{e(SENDER_COMPANY)}</div>'
            f'<div style="{font};font-size:13px;color:#4b5563;margin-top:2px">{e(contact)}</div>'
            f'<div style="{font};font-size:13px;margin-top:2px">{site_html}</div>'
            f"</td></tr></table></td></tr>")

    header = (
        f'<tr><td bgcolor="{purple}" style="background:{purple};padding:22px 36px;border-radius:12px 12px 0 0">'
        f'<div style="{font};font-size:20px;font-weight:800;color:#ffffff;letter-spacing:.2px">'
        f'{e(BRAND_WORDS[0])} <span style="color:{teal}">{e(BRAND_WORDS[1])}</span></div>'
        f'<div style="{font};font-size:12px;color:#c9c3ec;margin-top:3px">Business phones that work with your software</div>'
        f'</td></tr>'
        f'<tr><td height="4" bgcolor="{teal}" style="background:{teal};font-size:0;line-height:0">&nbsp;</td></tr>'
        f'<tr><td style="padding:28px 0 0 0;font-size:0;line-height:0">&nbsp;</td></tr>'
    )
    footer = (
        f'<tr><td style="padding:14px 36px 0 36px;{font};font-size:12px;line-height:1.5;color:#8a8fa3">{e(ps)}</td></tr>'
        if ps else "")
    address = SENDER_DEFAULTS.get("address", "")
    return (
        '<html><body style="margin:0;padding:0;background:#f1f0f7">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f1f0f7" '
        'style="background:#f1f0f7"><tr><td align="center" style="padding:24px 12px">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'style="width:100%;max-width:600px">'
        '<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" '
        f'style="background:#ffffff;border-radius:12px;border:1px solid #e4e1f0">{header}{"".join(rows)}{sig_html}</table></td></tr>'
        f"{footer}"
        + (f'<tr><td style="padding:6px 36px 0 36px;{font};font-size:11px;color:#a3a7b8">{e(SENDER_COMPANY)} · {e(address)}</td></tr>'
           if address else "")
        + "</table></td></tr></table></body></html>"
    )


def _email_body_html(body: str, subject: str = "") -> str:
    """The HTML version of an email: branded (default) or plain, per the 'Branded email design' switch."""
    try:
        branded = st.session_state.get("opt_branded", True)
    except Exception:
        branded = True
    return _email_branded_html(body, subject) if branded else _email_plain_html(body)


def build_eml_draft(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[Tuple[str, bytes]]] = None,
) -> bytes:
    """A ready-to-send email draft (.eml) with attachments.

    Outlook for Windows opens it as an unsent draft (thanks to the X-Unsent header),
    with the To, Subject, formatted body and PDF already in place.
    """
    msg = EmailMessage()
    if to:
        msg["To"] = to
    msg["Subject"] = subject or ""
    msg["Date"] = formatdate(localtime=True)
    msg["X-Unsent"] = "1"  # Tells Outlook to open this as a new draft, not a received email
    msg.set_content(body.replace("\r\n", "\n"))
    msg.add_alternative(_email_body_html(body, subject or ""), subtype="html")
    for filename, data in attachments or []:
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=filename)
    return msg.as_bytes()


def build_mailto(to: str, subject: str, body: str) -> str:
    """mailto: link that opens the user's default email app with everything filled in."""
    body_crlf = body.replace("\r\n", "\n").replace("\n", "\r\n")
    return (
        f"mailto:{quote(to or '', safe='@.+-_')}"
        f"?subject={quote(subject or '', safe='')}"
        f"&body={quote(body_crlf, safe='')}"
    )



# ------------------------------------------------------------------
# SY Communications sector overview (the "About us" email attachment)
# ------------------------------------------------------------------


def _box(pdf: FPDF, x: float, y: float, w: float, h: float, style: str = "F", radius: float = 2.5) -> None:
    try:
        pdf.rect(x, y, w, h, style=style, round_corners=True, corner_radius=radius)
    except TypeError:  # Older fpdf2 without rounded corners
        pdf.rect(x, y, w, h, style=style)


def create_sector_overview_pdf(lead: Optional[ScrapedLead], vertical_key: str) -> bytes:
    """One-page, branded SY Communications solutions overview, personalised to the prospect."""
    copy = SECTOR_COPY.get(vertical_key, SECTOR_COPY["Estate & Lettings Agents"])
    cfg = VERTICAL_PRESETS.get(vertical_key, VERTICAL_PRESETS["Estate & Lettings Agents"])
    sender = get_sender()
    T = sanitize_pdf_text
    purple, purple2, teal = BRAND_PURPLE, BRAND_PURPLE_2, BRAND_TEAL
    ink, grey, light = (30, 30, 46), (95, 100, 120), (244, 243, 250)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()
    W = 210
    L, R = 14, 196
    CW = R - L

    # ---------- Header band ----------
    pdf.set_fill_color(*purple)
    pdf.rect(0, 0, W, 50, "F")
    pdf.set_fill_color(*purple2)
    pdf.rect(0, 46, W, 4, "F")
    pdf.set_fill_color(*teal)
    pdf.rect(0, 50, W, 1.2, "F")
    # Logo mark: teal circle with 'SY'
    pdf.set_fill_color(*teal)
    pdf.ellipse(L, 13, 14, 14, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(L, 17.5)
    pdf.cell(14, 5, BRAND_INITIALS, align="C")
    pdf.set_xy(L + 18, 13)
    pdf.set_font("Helvetica", "B", 17)
    pdf.cell(100, 8, sanitize_pdf_text(SENDER_COMPANY))
    pdf.set_xy(L + 18, 21)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(190, 184, 230)
    pdf.cell(100, 5, "Business telecoms, connectivity & security")
    pdf.set_xy(L, 31)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(108, 6, T(f"Phone systems built for {copy['sector_plural']}"), align="L")
    # Prepared-for panel
    if lead:
        pdf.set_fill_color(*purple2)
        _box(pdf, 128, 11, 68, 26)
        pdf.set_xy(132, 14)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*teal)
        pdf.cell(60, 4, "PREPARED FOR")
        pdf.set_xy(132, 19)
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(255, 255, 255)
        pdf.multi_cell(61, 4.6, T(lead_display_name(lead)[:60]), align="L")
        pdf.set_xy(132, 30.5)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(190, 184, 230)
        pdf.cell(60, 4, T(pd.Timestamp.now().strftime("%B %Y")))

    # ---------- Intro ----------
    crms = cfg["crms"]
    y = 58
    pdf.set_xy(L, y)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*ink)
    pdf.multi_cell(
        CW, 5.2,
        T(
            f"We connect your phone system directly to {', '.join(crms[:-1])} and {crms[-1]}, so every call"
            " arrives with context, gets logged automatically and never slips through the cracks."
        ),
        align="L",
    )

    def heading(text: str, yy: float) -> float:
        pdf.set_xy(L, yy)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*teal)
        pdf.cell(CW, 4, text.upper())
        pdf.set_draw_color(*teal)
        pdf.set_line_width(0.5)
        pdf.line(L, yy + 5.2, L + 10, yy + 5.2)
        return yy + 8

    # ---------- The challenge (3 cards) ----------
    y = heading("The challenge", pdf.get_y() + 4)
    gap = 4
    cw3 = (CW - 2 * gap) / 3
    for i, (title, desc) in enumerate(copy["challenges"][:3]):
        x = L + i * (cw3 + gap)
        pdf.set_fill_color(*light)
        _box(pdf, x, y, cw3, 24)
        pdf.set_xy(x + 4, y + 3.5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*purple)
        pdf.multi_cell(cw3 - 8, 4.4, T(title), align="L")
        pdf.set_xy(x + 4, pdf.get_y() + 1)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*grey)
        pdf.multi_cell(cw3 - 8, 3.9, T(desc), align="L")
    y += 24 + 5

    # ---------- How we solve it ----------
    y = heading("How we solve it", y)
    pdf.set_xy(L, y)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*grey)
    pdf.cell(22, 6, "Integrates with:")
    x = L + 23
    pdf.set_font("Helvetica", "B", 8)
    for crm in crms:
        w = pdf.get_string_width(T(crm)) + 7
        pdf.set_draw_color(*teal)
        pdf.set_line_width(0.35)
        pdf.set_text_color(*purple)
        _box(pdf, x, y + 0.5, w, 5.2, style="D", radius=2.6)
        pdf.set_xy(x, y + 0.5)
        pdf.cell(w, 5.2, T(crm), align="C")
        x += w + 2.5
    y += 10
    cw2 = (CW - gap) / 2
    for i, (title, desc) in enumerate(copy["outcomes"][:4]):
        col, row = i % 2, i // 2
        x = L + col * (cw2 + gap)
        yy = y + row * 17
        pdf.set_fill_color(*teal)
        pdf.ellipse(x, yy + 0.5, 7, 7, "F")
        pdf.set_xy(x, yy + 1.8)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(7, 4.4, str(i + 1), align="C")
        pdf.set_xy(x + 10, yy)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*ink)
        pdf.cell(cw2 - 10, 5, T(title))
        pdf.set_xy(x + 10, yy + 5.5)
        pdf.set_font("Helvetica", "", 8.2)
        pdf.set_text_color(*grey)
        pdf.multi_cell(cw2 - 12, 4, T(desc), align="L")
    y += 2 * 17 + 1

    # ---------- Switchover callout ----------
    pdf.set_fill_color(230, 247, 245)
    _box(pdf, L, y, CW, 19)
    pdf.set_fill_color(*teal)
    pdf.rect(L, y, 1.6, 19, "F")
    pdf.set_xy(L + 6, y + 3)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*purple)
    pdf.cell(CW - 10, 5, "The analogue switch-off is coming: January 2027")
    pdf.set_xy(L + 6, y + 8.5)
    pdf.set_font("Helvetica", "", 8.2)
    pdf.set_text_color(*grey)
    pdf.multi_cell(
        CW - 12, 4,
        "BT is retiring the traditional phone network. If you still rely on analogue or ISDN lines, moving now"
        " means you choose the timing, and you upgrade to a system that works with your software.",
        align="L",
    )
    y += 19 + 5

    # ---------- One partner + Why us (two columns) ----------
    y0 = y
    heading("One partner for your technology", y)
    yy = y + 8
    for i, item in enumerate(EVERYTHING_WE_DO):
        pdf.set_fill_color(*teal)
        pdf.ellipse(L, yy + i * 6 + 1.6, 2, 2, "F")
        pdf.set_xy(L + 4, yy + i * 6)
        pdf.set_font("Helvetica", "", 8.3)
        pdf.set_text_color(*ink)
        pdf.cell(80, 5, T(item))

    xw = L + CW / 2 + 4
    pdf.set_xy(xw, y0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*teal)
    pdf.cell(80, 4, "WHY SY COMMUNICATIONS")
    pdf.set_draw_color(*teal)
    pdf.line(xw, y0 + 5.2, xw + 10, y0 + 5.2)
    why = [
        ("Local to you", BRAND_HOME),
        ("One point of contact", "From first survey through installation and aftercare."),
        ("Built around your software", "We set up the integration around how your team works."),
        ("Clear, no-obligation quotes", "Straightforward pricing before you commit to anything."),
    ]
    yy = y0 + 8
    for title, desc in why:
        pdf.set_xy(xw, yy)
        pdf.set_font("Helvetica", "B", 8.3)
        pdf.set_text_color(*ink)
        pdf.cell(80, 4.2, T(title))
        pdf.set_xy(xw, yy + 4.2)
        pdf.set_font("Helvetica", "", 7.8)
        pdf.set_text_color(*grey)
        pdf.cell(80, 4, T(desc))
        yy += 9
    y = max(yy, y0 + 8 + 6 * 6) + 3

    # ---------- Next steps ----------
    if y > 250:  # Safety: never collide with the footer
        y = 250
    y = heading("Next steps", y)
    steps = [
        ("15-minute call", "A quick chat about your team, lines and software."),
        ("Free review", "We look at your current setup and contracts."),
        ("Tailored quote", "A clear, no-obligation proposal."),
    ]
    for i, (title, desc) in enumerate(steps):
        x = L + i * (cw3 + gap)
        pdf.set_fill_color(*light)
        _box(pdf, x, y, cw3, 16)
        pdf.set_xy(x + 4, y + 3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*purple)
        pdf.cell(cw3 - 8, 4.5, T(f"{i + 1}. {title}"))
        pdf.set_xy(x + 4, y + 8.3)
        pdf.set_font("Helvetica", "", 7.6)
        pdf.set_text_color(*grey)
        pdf.multi_cell(cw3 - 8, 3.6, T(desc), align="L")

    # ---------- Footer band ----------
    pdf.set_fill_color(*purple)
    pdf.rect(0, 272, W, 25, "F")
    pdf.set_fill_color(*teal)
    pdf.rect(0, 272, W, 1.2, "F")
    pdf.set_xy(L, 277)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(255, 255, 255)
    contact_name = sender.get("name") or "Talk to our team"
    pdf.cell(90, 5, T(contact_name + (f"  |  {sender['title']}" if sender.get("name") and sender.get("title") else "")))
    pdf.set_xy(L, 283)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(190, 184, 230)
    pdf.cell(
        CW, 5,
        T("  |  ".join(x for x in (sender.get("phone"), sender.get("email"), sender.get("website")) if x)),
    )
    pdf.set_xy(L, 288.5)
    pdf.set_font("Helvetica", "", 7.2)
    pdf.cell(CW, 4, T(sender.get("address", "")))

    out = pdf.output()
    return bytes(out) if not isinstance(out, str) else out.encode("latin-1", errors="replace")


class LeadDossierPDF(FPDF):

    def header(self):
        self.set_fill_color(30, 41, 59)  # Dark slate header bar
        self.rect(0, 0, 210, 14, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.set_xy(12, 3)
        self.cell(
            0,
            8,
            "SY COMMUNICATIONS | CONFIDENTIAL LEAD RECORD",
            ln=0,
        )
        self.ln(14)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            6,
            "Confidential lead record - Generated for internal sales review",
            0,
            0,
            "C",
        )


def create_pdf_dossier(
    lead: ScrapedLead,
    vertical_name: str,
    pitch_text: str,
    target_crms: List[str],
) -> bytes:
    pdf = LeadDossierPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    contact_name, contact_role = infer_contact_name_and_role(
        lead, vertical_name
    )

    # 1. PRIMARY CONTACT CARD
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, "PRIMARY CONTACT", ln=True)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_pdf_text(contact_name), ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(71, 85, 105)
    primary_email = pick_primary_email(lead, contact_name) or "Email TBD"
    primary_phone = (
        lead.phones_found[0] if lead.phones_found else "Phone TBD"
    )
    contact_sub = f"{contact_role} - {primary_email} - {primary_phone}"
    pdf.cell(0, 5, sanitize_pdf_text(contact_sub), ln=True)

    pdf.ln(3)

    # 2. FIRM CARD
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, "TARGET FIRM", ln=True)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, sanitize_pdf_text(lead.company_name[:55]), ln=True)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(71, 85, 105)
    addr_line = lead.registered_address or "Address not listed"
    site_line = lead.website_url or "Website not specified"
    pdf.cell(
        0,
        5,
        sanitize_pdf_text(
            f"{vertical_name} - {addr_line[:65]} - Company"
            f" #{lead.company_number or 'N/A'}"
        ),
        ln=True,
    )
    pdf.cell(0, 5, sanitize_pdf_text(f"Domain: {site_line}"), ln=True)

    if lead.site_meta_description:
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(
            190, 4, sanitize_pdf_text(f'"{lead.site_meta_description[:200]}"')
        )

    pdf.ln(2)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # 3. CORE INTEGRATION HOOK
    vert_cfg = VERTICAL_PRESETS.get(
        vertical_name, VERTICAL_PRESETS["Estate & Lettings Agents"]
    )
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, "SYSTEM INTEGRATION HOOK", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(2, 132, 199)  # Highlighted blue
    crms_headline = f"{vert_cfg['primary_hook']} (confirm which)"
    pdf.cell(0, 5, sanitize_pdf_text(crms_headline), ln=True)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    for bullet in vert_cfg["pitch_bullets"]:
        pdf.cell(0, 4.5, sanitize_pdf_text(f"- {bullet}"), ln=True)

    pdf.ln(3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # 4. TAILORED OUTREACH EMAIL DRAFT
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, "READY-TO-SEND OUTREACH EMAIL COPY", ln=True)

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(15, 23, 42)

    clean_pitch = sanitize_pdf_text(pitch_text)
    pdf.multi_cell(190, 4.2, clean_pitch, border=1, fill=True)

    output = pdf.output()
    if isinstance(output, str):
        return output.encode("latin-1", errors="replace")
    elif isinstance(output, bytearray):
        return bytes(output)
    return output


# ==========================================
# 3b. SENT LOG (remembers who's been emailed, across sessions)
# ==========================================


def _secret_value(key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(key, default) or default)
    except Exception:
        return default


class SentLog:
    """Stores {company_number: record} of firms that have been emailed.

    Permanent: a JSON file in a private GitHub repo (set GITHUB_TOKEN + GITHUB_REPO in Secrets).
    Fallback: a local file, which Streamlit Cloud wipes whenever the app restarts or redeploys.
    """

    def __init__(self, path_secret: str = "GITHUB_LOG_PATH", default_path: str = "sent_log.json",
                 local_name: str = ".sent_log.json", compact: bool = False) -> None:
        self.token = _secret_value("GITHUB_TOKEN")
        self.repo = _secret_value("GITHUB_REPO")  # e.g. "SouthWalesTelecoms/swcomms-saved-deals"
        self.branch = _secret_value("GITHUB_BRANCH", "main")
        # Everything this app saves sits in one folder of the data repo, so it never touches other apps' files
        prefix = _secret_value("GITHUB_PATH_PREFIX", "sales-hub/").strip().lstrip("/")
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        self.path = _secret_value(path_secret) or (prefix + default_path)
        self.compact = compact
        self.backend = "github" if (self.token and self.repo) else "local"
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        self.local_path = os.path.join(base_dir, local_name)
        self.last_error: Optional[str] = None

    # ---------- GitHub backend ----------
    def _url(self) -> str:
        return f"https://api.github.com/repos/{self.repo}/contents/{self.path}"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _gh_read(self) -> Tuple[Dict[str, Any], Optional[str]]:
        resp = requests.get(self._url(), headers=self._headers(), params={"ref": self.branch}, timeout=10)
        if resp.status_code == 404:
            return {}, None  # File doesn't exist yet; first write creates it
        if resp.status_code != 200:
            raise RuntimeError(self._describe(resp.status_code))
        payload = resp.json()
        if payload.get("encoding") == "none" or (not payload.get("content") and payload.get("size", 0) > 0):
            # Files over 1 MB come back without their content: fetch the raw file instead
            raw = requests.get(self._url(), headers={**self._headers(), "Accept": "application/vnd.github.raw+json"},
                               params={"ref": self.branch}, timeout=30)
            if raw.status_code != 200:
                raise RuntimeError(self._describe(raw.status_code))
            content = raw.content.decode("utf-8-sig").strip()
        else:
            content = base64.b64decode(payload.get("content", "") or b"").decode("utf-8-sig").strip()
        if not content or content in ("[]", "null"):
            return {}, payload.get("sha")  # Emptied by hand on GitHub: treat as a fresh start
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"{self.path} on GitHub isn't valid JSON. Replace its contents with {{}} to start fresh.")
        return (data if isinstance(data, dict) else {}), payload.get("sha")

    def _gh_write(self, data: Dict[str, Any], sha: Optional[str], message: str) -> int:
        body: Dict[str, Any] = {
            "message": message,
            "content": base64.b64encode((json.dumps(data, separators=(",", ":"), ensure_ascii=False) if self.compact
                                         else json.dumps(data, indent=2, sort_keys=True)).encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if sha:
            body["sha"] = sha
        resp = requests.put(self._url(), headers=self._headers(), json=body, timeout=30)
        return resp.status_code

    @staticmethod
    def _describe(code: int) -> str:
        return {
            401: "GitHub rejected the token (401). Check GITHUB_TOKEN in Secrets.",
            403: "GitHub token lacks permission (403). It needs Contents: Read and write on the repo.",
            404: "GitHub repo not found (404). Check GITHUB_REPO in Secrets.",
        }.get(code, f"GitHub returned an error ({code}).")

    # ---------- Local backend ----------
    def _local_read(self) -> Dict[str, Any]:
        try:
            with open(self.local_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _local_write(self, data: Dict[str, Any]) -> None:
        tmp = self.local_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.local_path)

    # ---------- Public API ----------
    def load(self) -> Dict[str, Any]:
        self.last_error = None
        try:
            return self._gh_read()[0] if self.backend == "github" else self._local_read()
        except Exception as exc:  # Never let the log break the app
            self.last_error = str(exc) if isinstance(exc, RuntimeError) else f"Couldn't load sent log ({exc.__class__.__name__})."
            return {}

    def apply(self, changes: Dict[str, Optional[Dict[str, Any]]], message: str) -> Dict[str, Any]:
        """Applies {company_number: record or None (= un-mark)} and returns the latest full log.
        Re-reads before writing, so two people using the app at once don't overwrite each other."""
        self.last_error = None

        def merge(data: Dict[str, Any]) -> Dict[str, Any]:
            for key, record in changes.items():
                if record is None:
                    data.pop(key, None)
                else:
                    data[key] = record
            return data

        if self.backend == "local":
            data = merge(self._local_read())
            self._local_write(data)
            return data

        for _attempt in range(3):
            data, sha = self._gh_read()
            data = merge(data)
            status = self._gh_write(data, sha, message)
            if status in (200, 201):
                return data
            if status not in (409, 422):  # 409/422 = someone else saved first; re-read and retry
                raise RuntimeError(self._describe(status))
        raise RuntimeError("GitHub was busy saving the sent log. Please try again.")


@st.cache_resource(show_spinner=False)
def _shard_cache() -> Dict[str, Any]:
    """Shared by every session on this server: {shard file name: (git sha, records)}. Only changed shards are re-downloaded."""
    return {"shards": {}, "listed_at": 0.0}


class ShardedStore:
    """The customer list, split across SHARDS small gzipped JSON files in one folder of the data repo.

    A list of ~30,000 customers is tens of MB as one file, so saving one call outcome would mean rewriting all of it.
    Split up, a click rewrites one ~100 KB file, and loading only fetches files that changed since this server last
    saw them. Same load() / apply() as SentLog, so the rest of the app doesn't care.
    """
    SHARDS = 64  # Never change once data is saved: it decides which file each customer lives in

    def __init__(self, dir_secret: str = "GITHUB_CRM_DIR", default_dir: str = "customers",
                 legacy: Optional["SentLog"] = None, local_dir: str = ".sales_hub_customers") -> None:
        self.token = _secret_value("GITHUB_TOKEN")
        self.repo = _secret_value("GITHUB_REPO")
        self.branch = _secret_value("GITHUB_BRANCH", "main")
        prefix = _secret_value("GITHUB_PATH_PREFIX", "sales-hub/").strip().lstrip("/")
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        self.dir = (_secret_value(dir_secret) or (prefix + default_dir)).strip("/")
        self.path = self.dir + "/"
        self.backend = "github" if (self.token and self.repo) else "local"
        self.legacy = legacy
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        self.local_dir = os.path.join(base_dir, local_dir)
        self.last_error: Optional[str] = None

    # ---------- shared helpers ----------
    @classmethod
    def shard_of(cls, rid: str) -> str:
        return f"s{int(hashlib.md5(str(rid).encode('utf-8')).hexdigest()[:8], 16) % cls.SHARDS:02d}.json.gz"

    @staticmethod
    def _pack(records: Dict[str, Any]) -> bytes:
        return gzip.compress(json.dumps(records, separators=(",", ":"), ensure_ascii=False).encode("utf-8"), 6)

    @staticmethod
    def _unpack(raw: bytes) -> Dict[str, Any]:
        if not raw:
            return {}
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass  # Someone saved it uncompressed by hand
        txt = raw.decode("utf-8-sig").strip()
        if not txt or txt in ("[]", "null"):
            return {}
        data = json.loads(txt)
        return data if isinstance(data, dict) else {}

    def _headers(self, raw: bool = False) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"}

    def _api(self, tail: str) -> str:
        return f"https://api.github.com/repos/{self.repo}/{tail}"

    # ---------- GitHub ----------
    def _list(self) -> Dict[str, str]:
        """{file name: sha} of the shard files on GitHub (one API call)."""
        resp = requests.get(self._api(f"contents/{self.dir}"), headers=self._headers(), params={"ref": self.branch},
                            timeout=15)
        if resp.status_code == 404:
            return {}
        if resp.status_code != 200:
            raise RuntimeError(SentLog._describe(resp.status_code))
        items = resp.json()
        return {i["name"]: i["sha"] for i in items if isinstance(i, dict) and i.get("type") == "file"
                and re.match(r"^s\d{2}\.json(\.gz)?$", i.get("name", ""))} if isinstance(items, list) else {}

    def _blob(self, sha: str) -> bytes:
        for attempt in range(3):
            try:
                resp = requests.get(self._api(f"git/blobs/{sha}"), headers=self._headers(raw=True), timeout=30)
            except requests.exceptions.RequestException:
                resp = None
            if resp is not None and resp.status_code == 200:
                return resp.content
            if resp is not None and resp.status_code in (401, 403, 404):
                break
            time.sleep(1 + attempt)
        raise RuntimeError(SentLog._describe(resp.status_code if resp is not None else 0)
                           if resp is not None else "Couldn't reach GitHub to load the customer list.")

    def _fetch(self, listing: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        cache = _shard_cache()["shards"]
        need = [n for n, sha in listing.items() if (cache.get(n) or (None,))[0] != sha]
        if need:
            with ThreadPoolExecutor(max_workers=min(8, len(need))) as pool:
                for name, raw in zip(need, pool.map(lambda n: self._blob(listing[n]), need)):
                    cache[name] = (listing[name], self._unpack(raw))
        for gone in [n for n in cache if n not in listing]:
            cache.pop(gone, None)
        return {n: cache[n][1] for n in listing}

    def _put_shard(self, name: str, changes: Dict[str, Optional[Dict[str, Any]]], message: str) -> Dict[str, Any]:
        cache = _shard_cache()["shards"]
        url = self._api(f"contents/{self.dir}/{name}")
        for _attempt in range(4):
            resp = requests.get(url, headers=self._headers(), params={"ref": self.branch}, timeout=15)
            if resp.status_code == 404:
                sha, current = None, {}
            elif resp.status_code == 200:
                sha = resp.json().get("sha")
                current = cache[name][1] if (cache.get(name) or (None,))[0] == sha else self._unpack(self._blob(sha))
            else:
                raise RuntimeError(SentLog._describe(resp.status_code))
            merged = dict(current)
            for k, v in changes.items():
                if v is None:
                    merged.pop(k, None)
                else:
                    merged[k] = v
            body: Dict[str, Any] = {"message": message, "branch": self.branch,
                                    "content": base64.b64encode(self._pack(merged)).decode("ascii")}
            if sha:
                body["sha"] = sha
            put = requests.put(url, headers=self._headers(), json=body, timeout=60)
            if put.status_code in (200, 201):
                new_sha = ((put.json() or {}).get("content") or {}).get("sha")
                if new_sha:
                    cache[name] = (new_sha, merged)
                return merged
            if put.status_code not in (409, 422):  # 409/422: someone saved this file first, so re-read and retry
                raise RuntimeError(SentLog._describe(put.status_code))
            time.sleep(0.6 + _attempt)
        raise RuntimeError("GitHub was busy saving. Please try again.")

    # ---------- local (no GitHub set up: wiped when the app restarts) ----------
    def _local_all(self) -> Dict[str, Dict[str, Any]]:
        out = {}
        if os.path.isdir(self.local_dir):
            for n in os.listdir(self.local_dir):
                if re.match(r"^s\d{2}\.json\.gz$", n):
                    with open(os.path.join(self.local_dir, n), "rb") as fh:
                        out[n] = self._unpack(fh.read())
        return out

    def _local_put(self, name: str, changes: Dict[str, Optional[Dict[str, Any]]]) -> Dict[str, Any]:
        os.makedirs(self.local_dir, exist_ok=True)
        p = os.path.join(self.local_dir, name)
        current = {}
        if os.path.exists(p):
            with open(p, "rb") as fh:
                current = self._unpack(fh.read())
        for k, v in changes.items():
            if v is None:
                current.pop(k, None)
            else:
                current[k] = v
        with open(p + ".tmp", "wb") as fh:
            fh.write(self._pack(current))
        os.replace(p + ".tmp", p)
        return current

    # ---------- public ----------
    def load(self) -> Dict[str, Any]:
        self.last_error = None
        try:
            shards = self._fetch(self._list()) if self.backend == "github" else self._local_all()
            data: Dict[str, Any] = {}
            for recs in shards.values():
                data.update(recs)
            if not shards and self.legacy is not None:  # First run after the upgrade: move the old single file over
                old = self.legacy.load()
                old = {k: v for k, v in old.items() if isinstance(v, dict)}
                if old:
                    self.apply(old, "Sales Hub: moved the customer list into the split store")
                    data = old
            return data
        except Exception as exc:
            self.last_error = str(exc) if isinstance(exc, RuntimeError) else \
                f"Couldn't load the customer list ({exc.__class__.__name__})."
            return {}

    def apply(self, changes: Dict[str, Optional[Dict[str, Any]]], message: str,
              progress: Optional[Any] = None) -> Dict[str, Any]:
        """Saves {id: record or None (= delete)}, touching only the files those ids live in. Returns the whole list."""
        self.last_error = None
        groups: Dict[str, Dict[str, Optional[Dict[str, Any]]]] = {}
        for k, v in changes.items():
            groups.setdefault(self.shard_of(k), {})[k] = v
        names = sorted(groups)
        for i, name in enumerate(names, start=1):
            if self.backend == "github":
                self._put_shard(name, groups[name], message if len(names) == 1 else f"{message} ({i}/{len(names)})")
            else:
                self._local_put(name, groups[name])
            if progress:
                progress(i, len(names))
        if self.backend == "github":
            cache = _shard_cache()["shards"]
            data: Dict[str, Any] = {}
            for _sha, recs in cache.values():
                data.update(recs)
            return data
        data = {}
        for recs in self._local_all().values():
            data.update(recs)
        return data


def now_uk() -> datetime:
    try:
        return datetime.now(ZoneInfo("Europe/London"))
    except Exception:
        return datetime.now()


def sent_label(record: Optional[Dict[str, Any]]) -> str:
    """'✓ 25 Sep' for the tables."""
    if not record:
        return ""
    try:
        return "✓ " + datetime.fromisoformat(record.get("sent_at", "")).strftime("%d %b").lstrip("0")
    except ValueError:
        return "✓ Sent"


# ------------------------------------------------------------------
# Batch export: a zip of ready-to-send Outlook drafts
# ------------------------------------------------------------------


def draft_filename_part(company_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", friendly_company_name(company_name)).strip("_") or "firm"


def build_lead_list_csv(items: List[Dict[str, Any]], log: Dict[str, Any]) -> bytes:
    """Spreadsheet of every selected firm, including those with no email (for phoning)."""
    rows = []
    for item in items:
        lead: ScrapedLead = item["lead"]
        cn = lead.company_number or ""
        contact, role = infer_contact_name_and_role(lead, item["vertical"])
        directors = [display_officer_name(o.name) for o in lead.officers if o.raw_role in DECISION_MAKER_ROLES]
        rec = log.get(cn)
        rows.append({
            "Status": (f"{rec.get('status') or 'Emailed'} {sent_label(rec)[2:]}" if rec
                       else "Ready to email" if item.get("to") else "No email"),
            "Firm": lead.company_name,
            "Trading name": getattr(lead, "trading_name", None) or "",
            "Company number": cn,
            "Sector": item["vertical"],
            "Contact": contact,
            "Contact role": role,
            "Email": item.get("to", ""),
            "Other emails": "; ".join(e for e in lead.emails_found if e != item.get("to")),
            "Phone": (lead.phones_found or [""])[0],
            "Other phones": "; ".join(lead.phones_found[1:]),
            "Directors": "; ".join(directors),
            "Website": lead.website_url or "",
            "Website match": (lead.website_confidence or "") if lead.website_url else "Not found",
            "Registered office": lead.registered_address or "",
            "Email subject": item.get("subject", "") if item.get("to") else "",
        })
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")  # utf-8-sig = opens cleanly in Excel


def build_drafts_zip(items: List[Dict[str, Any]], attach_overview: bool) -> Tuple[bytes, int, List[str]]:
    """items: queue items with lead/vertical/to/subject/body. Returns (zip_bytes, drafts_written, skipped_names)."""
    buf = io.BytesIO()
    written, skipped = 0, []
    summary = io.StringIO()
    summary.write("Firm,Company number,To,Contact,Subject,Website,Website match\n")
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in items:
            lead: ScrapedLead = item["lead"]
            if not item.get("to"):
                skipped.append(lead_display_name(lead))
                continue
            written += 1
            part = draft_filename_part(lead.company_name)
            attachments = None
            if attach_overview:
                sector_slug = re.sub(
                    r"[^A-Za-z0-9]+", "_",
                    SECTOR_COPY.get(item["vertical"], {}).get("sector_plural", "sector"),
                ).strip("_")
                attachments = [(
                    f"{BRAND_FILE}_{sector_slug}_overview_{part}.pdf",
                    create_sector_overview_pdf(lead, item["vertical"]),
                )]
            eml = build_eml_draft(item["to"], item["subject"], item["body"], attachments=attachments)
            zf.writestr(f"{written:02d}_{part}.eml", eml)
            contact, _ = infer_contact_name_and_role(lead, item["vertical"])
            row = [lead.company_name, lead.company_number or "", item["to"], contact,
                   item["subject"], lead.website_url or "", lead.website_confidence or "Not found"]
            summary.write(",".join('"' + str(v).replace('"', '""') + '"' for v in row) + "\n")
        zf.writestr("_summary.csv", summary.getvalue())
    return buf.getvalue(), written, skipped


# ==========================================
# 4. STREAMLIT APPLICATION
# ==========================================

# ==========================================
# ZOHO CRM: every enriched firm becomes a Zoho Lead (duplicate-checked), then Send via Zoho
# ==========================================
ZOHO_SEND_LIMIT = 100  # Zoho's Send Mail API allows 100 emails a day
ZOHO_SCOPE = ("ZohoCRM.modules.leads.ALL,ZohoCRM.modules.accounts.READ,ZohoCRM.modules.contacts.READ,"
              "ZohoCRM.modules.notes.CREATE,ZohoCRM.coql.READ,ZohoCRM.settings.fields.READ,ZohoCRM.org.READ,"
              "ZohoCRM.send_mail.leads.CREATE,ZohoCRM.Files.CREATE,ZohoCRM.settings.emails.READ")

class ZohoError(RuntimeError):
    pass


class ZohoCRM:
    """Minimal Zoho CRM v8 client using a Self Client refresh token (EU data centre by default)."""

    def __init__(self) -> None:
        self.client_id = _secret_value("ZOHO_CLIENT_ID")
        self.client_secret = _secret_value("ZOHO_CLIENT_SECRET")
        self.refresh_token = _secret_value("ZOHO_REFRESH_TOKEN")
        self.accounts_url = _secret_value("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.eu").rstrip("/")
        self.api_domain = _secret_value("ZOHO_API_DOMAIN", "https://www.zohoapis.eu").rstrip("/")
        self.crm_url = _secret_value("ZOHO_CRM_URL", "https://crm.zoho.eu").rstrip("/")
        self.configured = bool(self.client_id and self.client_secret and self.refresh_token)
        # Client ID + secret in Secrets but no refresh token yet: the app can do the one-off swap itself
        self.can_setup = bool(self.client_id and self.client_secret) and not self.refresh_token

    # ---------- one-off setup: swap a Self Client code for a refresh token ----------
    def exchange_code(self, code: str) -> Dict[str, str]:
        """Returns {'refresh_token': ...} or {'error': plain-English reason}."""
        try:
            resp = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                data={"grant_type": "authorization_code", "client_id": self.client_id,
                      "client_secret": self.client_secret, "code": code.strip()},
                timeout=15,
            )
            data = resp.json()
        except requests.exceptions.RequestException as exc:
            return {"error": f"Couldn't reach Zoho ({exc.__class__.__name__}). Try again in a moment."}
        except ValueError:
            return {"error": f"Zoho sent an unreadable reply (HTTP {resp.status_code}). Check the Self Client is on api-console.zoho.eu."}
        if data.get("refresh_token"):
            return {"refresh_token": data["refresh_token"]}
        if data.get("access_token"):
            return {"error": "Zoho gave a short-lived token but no refresh token. Generate a new code and try again."}
        err = str(data.get("error") or f"HTTP {resp.status_code}")
        hints = {
            "invalid_code": "The code has expired or was already used. Codes last only a few minutes and work once, so generate a fresh one and paste it straight in.",
            "invalid_client": "Zoho doesn't recognise ZOHO_CLIENT_ID. Copy it again from the Self Client's Client Secret tab. If the Self Client was made on api-console.zoho.com (not .eu), make a new one on api-console.zoho.eu.",
            "invalid_client_secret": "ZOHO_CLIENT_SECRET doesn't match the client ID. Copy it again from the Self Client's Client Secret tab (watch for stray spaces).",
        }
        return {"error": f"Zoho said: {err}. " + hints.get(err, "Generate a fresh code and try again. If it keeps failing, check the client ID and secret in Secrets.")}

    # ---------- auth ----------
    def _token(self, force: bool = False) -> str:
        cached = st.session_state.get("zoho_token")
        if cached and not force and cached[1] > time.time() + 60:
            return cached[0]
        try:
            resp = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                params={"refresh_token": self.refresh_token, "client_id": self.client_id,
                        "client_secret": self.client_secret, "grant_type": "refresh_token"},
                timeout=12,
            )
            data = resp.json()
        except requests.exceptions.RequestException as exc:
            raise ZohoError(f"Couldn't reach Zoho to sign in ({exc.__class__.__name__}).")
        except ValueError:
            raise ZohoError("Zoho sent an unreadable sign-in response.")
        if "access_token" not in data:
            err = data.get("error", "unknown error")
            hint = {
                "invalid_code": "The refresh token is invalid or was revoked. Generate a new one in api-console.zoho.eu.",
                "invalid_client": "ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET don't match. Check them in Secrets.",
            }.get(err, "Check the Zoho secrets and that the Self Client is in the EU data centre.")
            raise ZohoError(f"Zoho sign-in failed ({err}). {hint}")
        if data.get("api_domain"):
            self.api_domain = data["api_domain"].rstrip("/")
        st.session_state["zoho_token"] = (data["access_token"], time.time() + int(data.get("expires_in", 3600)))
        return data["access_token"]

    def _request(self, method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
        for attempt in (0, 1):
            headers = {"Authorization": f"Zoho-oauthtoken {self._token(force=attempt == 1)}"}
            try:
                resp = requests.request(method, f"{self.api_domain}{path}", headers=headers, timeout=20, **kwargs)
            except requests.exceptions.RequestException as exc:
                raise ZohoError(f"Couldn't reach Zoho CRM ({exc.__class__.__name__}).")
            if resp.status_code == 204:
                return None  # No records
            try:
                body = resp.json()
            except ValueError:
                body = {}
            code = str(body.get("code", ""))
            if resp.status_code == 401 and code in ("INVALID_TOKEN", "AUTHENTICATION_FAILURE") and attempt == 0:
                continue  # Token expired early: refresh once and retry
            if resp.status_code >= 400:
                row = (body.get("data") or [{}])[0] if isinstance(body.get("data"), list) else {}
                code = code or str(row.get("code", ""))
                msg = body.get("message") or row.get("message") or code or f"HTTP {resp.status_code}"
                if code == "OAUTH_SCOPE_MISMATCH":
                    msg = "The Zoho token is missing a permission. Regenerate it with the scopes listed in the setup notes."
                raise ZohoError(f"Zoho CRM error: {msg}")
            return body
        raise ZohoError("Zoho CRM rejected the sign-in.")

    # ---------- reads ----------
    def fields(self, module: str) -> Dict[str, Dict[str, Any]]:
        body = self._request("GET", "/crm/v8/settings/fields", params={"module": module}) or {}
        return {f["api_name"]: f for f in body.get("fields", [])}

    @staticmethod
    def picklist(fields: Dict[str, Dict[str, Any]], api_name: str) -> List[str]:
        values = (fields.get(api_name) or {}).get("pick_list_values") or []
        out = []
        for v in values:
            for k in ("display_value", "actual_value"):
                if v.get(k) and v[k] != "-None-":
                    out.append(v[k])
        return out

    def org_domain(self) -> Optional[str]:
        try:
            body = self._request("GET", "/crm/v8/org") or {}
            org = (body.get("org") or [{}])[0]
            return org.get("domain_name")
        except ZohoError:
            return None

    def coql(self, query: str) -> List[Dict[str, Any]]:
        body = self._request("POST", "/crm/v8/coql", json={"select_query": query})
        return (body or {}).get("data") or []

    def create_lead(self, fields: Dict[str, Any]) -> str:
        body = self._request("POST", "/crm/v8/Leads", json={"data": [fields], "trigger": ["workflow"]})
        return str(self._row_result(body).get("id", ""))

    # ---------- writes (phase 2): send, fill blanks, notes ----------
    @staticmethod
    def _row_result(body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        row = ((body or {}).get("data") or [{}])[0]
        if row.get("status") != "success":
            msg = row.get("message") or row.get("code") or "unknown error"
            raise ZohoError(f"Zoho CRM error: {msg}")
        return row.get("details") or {}

    def from_addresses(self) -> List[Dict[str, Any]]:
        body = self._request("GET", "/crm/v8/settings/emails/actions/from_addresses") or {}
        return [a for a in body.get("from_addresses", []) if a.get("email")]

    def upload_file(self, filename: str, data: bytes) -> str:
        body = self._request("POST", "/crm/v8/files", files={"file": (filename, data, "application/pdf")})
        return self._row_result(body)["id"]

    def send_mail(self, record_id: str, sender: Dict[str, Any], to_email: str, to_name: str,
                  subject: str, html: str, attachment_ids: Optional[List[str]] = None) -> str:
        mail: Dict[str, Any] = {
            "from": {"user_name": sender.get("user_name") or "", "email": sender["email"]},
            "to": [{"user_name": to_name or "", "email": to_email}],
            "subject": subject, "content": html, "mail_format": "html",
        }
        if sender.get("type") == "org_email":
            mail["org_email"] = True
        if attachment_ids:
            mail["attachments"] = [{"id": a} for a in attachment_ids]
        body = self._request("POST", f"/crm/v8/Leads/{record_id}/actions/send_mail", json={"data": [mail]})
        return self._row_result(body).get("message_id", "")

    def update_lead(self, record_id: str, fields: Dict[str, Any]) -> None:
        if fields:
            self._row_result(self._request("PUT", "/crm/v8/Leads", json={"data": [dict(fields, id=record_id)]}))

    def add_note(self, record_id: str, title: str, content: str) -> None:
        note = {"Note_Title": title, "Note_Content": content,
                "Parent_Id": {"module": {"api_name": "Leads"}, "id": record_id}}
        self._row_result(self._request("POST", f"/crm/v8/Leads/{record_id}/Notes", json={"data": [note]}))

    def record_tags(self, module: str, record_id: str) -> List[str]:
        body = self._request("GET", f"/crm/v8/{module}/{record_id}", params={"fields": "Tag"}) or {}
        rec = (body.get("data") or [{}])[0]
        return [str(t.get("name") if isinstance(t, dict) else t) for t in (rec.get("Tag") or [])]

    def record_url(self, record_id: str, module: str = "Leads") -> str:
        dom = st.session_state.get("zoho_org_domain")
        base = f"{self.crm_url}/crm/{dom}" if dom else f"{self.crm_url}/crm"
        return f"{base}/tab/{module}/{record_id}"

ZOHO = ZohoCRM()
# Firms already in Zoho with a tag containing these words are never pitched (e.g. "Not Interested")
BLOCKED_TAG_WORDS = ("not interested",)
ZOHO_STORE = SentLog("GITHUB_ZOHO_LEADS_PATH", "zoho_leads.json", ".zoho_leads.json")
UK_POSTCODE_RE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$", re.I)


def zoho_lead_source() -> str:
    return _secret_value("ZOHO_LEAD_SOURCE", "SW Telecoms")


def get_zoho_store() -> Dict[str, Any]:
    if "zoho_store_data" not in st.session_state:
        st.session_state["zoho_store_data"] = ZOHO_STORE.load()
    return st.session_state["zoho_store_data"]


def save_zoho_store(changes: Dict[str, Dict[str, Any]]) -> None:
    try:
        st.session_state["zoho_store_data"] = ZOHO_STORE.apply(changes, f"Prospect Engine: {len(changes)} firms to Zoho")
    except Exception:
        st.session_state.setdefault("zoho_store_data", {}).update(changes)


def load_zoho_meta() -> Optional[str]:
    """Lead fields (for picklist checks) and the org's URL name, once per session."""
    if "pe_lead_fields" in st.session_state:
        return None
    try:
        st.session_state["pe_lead_fields"] = ZOHO.fields("Leads")
    except ZohoError as exc:
        return str(exc)
    st.session_state["zoho_org_domain"] = ZOHO.org_domain()
    return None


def zoho_on() -> bool:
    return ZOHO.configured and "pe_lead_fields" in st.session_state


def lead_source_ok() -> bool:
    return zoho_lead_source() in ZOHO.picklist(st.session_state.get("pe_lead_fields") or {}, "Lead_Source")


def _q(v: str) -> str:
    return "'" + (v or "").replace("\\", "").replace("'", "\\'") + "'"


def _either(conds: List[str]) -> str:
    """COQL wants OR conditions nested in pairs: ((a or b) or c)."""
    out = conds[0]
    for c in conds[1:]:
        out = f"({out} or {c})"
    return out


def _name_variants(lead: ScrapedLead) -> List[str]:
    names = [lead.company_name, friendly_company_name(lead.company_name), getattr(lead, "trading_name", None) or ""]
    base = friendly_company_name(lead.company_name)
    names += [f"{base} Ltd", f"{base} Limited", base.upper(), lead.company_name.title()]
    return list(dict.fromkeys(n.strip() for n in names if n and n.strip()))[:8]


def find_in_zoho(lead: ScrapedLead, email: str, phone: str) -> Optional[Dict[str, Any]]:
    """An existing Lead, or an existing customer (Account / Contact email), for this firm."""
    names = ", ".join(_q(n) for n in _name_variants(lead))
    conds = [f"Company in ({names})"]
    if email:
        conds.append(f"Email = {_q(email)}")
    if phone:
        variants = list(dict.fromkeys([phone, phone.replace(" ", "")]))
        conds.append(f"Phone in ({', '.join(_q(p) for p in variants)})")
    rows = ZOHO.coql(f"select Company, Lead_Status from Leads where {_either(conds)} limit 0, 5")
    if rows:
        return {"status": "existing", "id": str(rows[0].get("id")), "zoho_status": rows[0].get("Lead_Status") or ""}
    rows = ZOHO.coql(f"select Account_Name from Accounts where Account_Name in ({names}) limit 0, 5")
    if rows:
        return {"status": "customer", "id": str(rows[0].get("id")), "name": rows[0].get("Account_Name") or ""}
    if email:
        rows = ZOHO.coql(f"select Email, Account_Name from Contacts where Email = {_q(email)} limit 0, 5")
        acc = (rows[0].get("Account_Name") or {}) if rows else {}
        if rows and isinstance(acc, dict) and acc.get("id"):
            return {"status": "customer", "id": str(acc["id"]), "name": acc.get("name") or ""}
    return None


def _split_address(addr: str) -> Dict[str, str]:
    parts = [p.strip() for p in (addr or "").split(",") if p.strip()]
    out: Dict[str, str] = {}
    if parts and UK_POSTCODE_RE.match(parts[-1]):
        out["Zip_Code"] = parts.pop().upper()
    county = re.compile(r"(shire|^(west|east|north|south|greater) |midlands|merseyside|cornwall|devon|kent|essex|"
                        r"surrey|norfolk|suffolk|cumbria|durham|tyne and wear|london|wales|scotland|county)", re.I)
    if len(parts) >= 3 and county.search(parts[-1]):
        out["State"] = parts.pop()
    if len(parts) >= 2:
        out["City"] = parts.pop()
    if parts:
        if len(parts) > 1 and re.fullmatch(r"[\dA-Za-z\-/]{1,6}", parts[0]) and any(ch.isdigit() for ch in parts[0]):
            parts = [f"{parts[0]} {parts[1]}"] + parts[2:]  # "14, Bridge Street" -> "14 Bridge Street"
        out["Street"] = ", ".join(parts)
    return out


def zoho_lead_fields(item: Dict[str, Any], cn: str) -> Dict[str, Any]:
    lead: ScrapedLead = item["lead"]
    lf = st.session_state.get("pe_lead_fields") or {}
    contact, role = infer_contact_name_and_role(lead, item["vertical"])
    person = (getattr(lead, "contact_name", None) or "").strip()
    if not person:
        officer = pick_decision_maker(lead.officers)
        person = display_officer_name(officer.name) if officer else ""
        role = officer.role if officer else ""
    fields: Dict[str, Any] = {"Company": lead_display_name(lead)}
    if person and len(person.split()) >= 2:
        fields["First_Name"], fields["Last_Name"] = person.split()[0], person.split()[-1]
        if role:
            fields["Designation"] = role
    else:
        fields["Last_Name"] = lead_display_name(lead)  # Zoho needs a Last Name
    email = (item.get("to") or (lead.emails_found[0] if lead.emails_found else "")).strip()
    if email:
        fields["Email"] = email
    if lead.phones_found:
        fields["Phone"] = lead.phones_found[0]
    if lead.website_url and lead.website_confidence in VERIFIED_WEBSITE:
        fields["Website"] = lead.website_url
    fields.update(_split_address(lead.registered_address or ""))
    industries = ZOHO.picklist(lf, "Industry")
    match = next((v for v in industries if v.lower() == (item.get("base_vertical") or item["vertical"]).lower()), None)
    if match:
        fields["Industry"] = match
    if item.get("lead_source") and item["lead_source"] in ZOHO.picklist(lf, "Lead_Source"):
        fields["Lead_Source"] = item["lead_source"]
    elif lead_source_ok():
        fields["Lead_Source"] = zoho_lead_source()
    statuses = ZOHO.picklist(lf, "Lead_Status")
    emailed = cn in get_sent_log()
    want = "Attempted to Contact" if emailed else "Not Contacted"
    if want in statuses:
        fields["Lead_Status"] = want
    directors = [display_officer_name(o.name) for o in lead.officers if o.raw_role in DECISION_MAKER_ROLES][:4]
    desc = [
        f"Found by Prospect Engine on {now_uk().strftime('%d %b %Y')} (source: {zoho_lead_source()}).",
        f"Legal name: {lead.company_name}" + (f" · Company number: {lead.company_number}" if lead.company_number else ""),
        f"Sector pitched: {item['vertical']}" + (f" · SIC: {', '.join(lead.sic_codes[:3])}" if lead.sic_codes else ""),
    ]
    if directors:
        desc.append("Directors: " + ", ".join(directors))
    if lead.website_url:
        desc.append(f"Website: {lead.website_url} ({lead.website_confidence or 'unverified'} match)")
    others = [e for e in lead.emails_found if e != email][:4]
    if others:
        desc.append("Other emails found: " + ", ".join(others))
    if len(lead.phones_found) > 1:
        desc.append("Other numbers: " + ", ".join(lead.phones_found[1:4]))
    if getattr(lead, "linkedin_url", None):
        desc.append(f"LinkedIn: {lead.linkedin_url}")
    if item.get("lead_source"):  # Quick add: the telemarketer's own data
        desc = [f"Added by {item.get('added_by') or 'a telemarketer'} with Prospect Engine Quick add on"
                f" {now_uk().strftime('%d %b %Y')} (source: {item['lead_source']}).",
                f"Sector pitched: {item['vertical']}"]
    else:
        desc.append("Details from Companies House, the firm's own website and Google Maps.")
    fields["Description"] = "\n".join(desc)
    return fields


def zoho_worthy(cn: str) -> bool:
    """Firms go into Zoho only once there's an email to use, unless 'Also add firms with no email' is on."""
    item = st.session_state.get("queue", {}).get(cn) or {}
    if st.session_state.get("zoho_no_email", False):
        return True
    return bool((item.get("to") or "").strip() or (item.get("lead") and item["lead"].emails_found))


def push_to_zoho_leads(cns: List[str]) -> Dict[str, List[str]]:
    """Adds each firm to Zoho as a Lead unless it's already there (as a lead or a customer)."""
    queue = st.session_state.get("queue", {})
    store = get_zoho_store()
    todo = [cn for cn in cns if cn in queue and cn not in store]
    summary: Dict[str, List[str]] = {"created": [], "existing": [], "customer": [], "not_interested": [], "error": []}
    if not todo:
        return summary
    stamp = now_uk().isoformat(timespec="seconds")
    who = get_sender().get("name", "")

    def _one(cn: str) -> Tuple[str, Dict[str, Any]]:
        item = queue[cn]
        lead: ScrapedLead = item["lead"]
        email = (item.get("to") or (lead.emails_found[0] if lead.emails_found else "")).strip()
        phone = lead.phones_found[0] if lead.phones_found else ""
        try:
            hit = find_in_zoho(lead, email, phone)
            if hit:
                try:  # Already in Zoho and tagged Not Interested: never pitch them
                    tags = ZOHO.record_tags("Accounts" if hit["status"] == "customer" else "Leads", hit["id"])
                    if any(w in t.lower() for t in tags for w in BLOCKED_TAG_WORDS):
                        hit = dict(hit, status="not_interested")
                except ZohoError:
                    pass
                return cn, dict(hit, at=stamp, by=who, firm=lead_display_name(lead))
            lid = ZOHO.create_lead(zoho_lead_fields(item, cn))
            rec = get_sent_log().get(cn)
            if rec:  # Already emailed from here (Outlook draft): put that on the lead's history
                ZOHO.add_note(lid, "Prospect Engine: pitch emailed",
                              f"Pitch emailed on {fmt_when(rec.get('sent_at', ''))} by {rec.get('sent_by') or 'the team'}"
                              f" to {rec.get('to') or 'unknown'}.\nSubject: {rec.get('subject', '')}")
            return cn, {"status": "created", "id": lid, "at": stamp, "by": who, "firm": lead_display_name(lead)}
        except ZohoError as exc:
            return cn, {"status": "error", "error": str(exc), "firm": lead_display_name(lead)}

    changes: Dict[str, Dict[str, Any]] = {}
    progress = st.progress(0.0, text="Checking Zoho for duplicates…")
    for n, cn_ in enumerate(todo, start=1):
        progress.progress(n / len(todo), text=f"Adding to Zoho {n} of {len(todo)} · {lead_display_name(queue[cn_]['lead'])}")
        cn, rec = _one(cn_)
        if rec["status"] == "error" and "permission" in rec["error"].lower():
            st.session_state["zoho_needs_scope"] = True  # Same for every firm, so stop and ask to reconnect
            summary["error"].append("permission")
            break
        summary[rec["status"]].append(rec.get("firm", cn) if rec["status"] != "error" else f"{rec['firm']}: {rec['error']}")
        if rec["status"] != "error":
            changes[cn] = rec
    progress.empty()
    if changes:
        save_zoho_store(changes)
    bump_queue_editor()
    return summary


def zoho_summary_text(s: Dict[str, List[str]]) -> Optional[str]:
    bits = []
    if s["created"]:
        bits.append(f"{len(s['created'])} added as new leads")
    if s["existing"]:
        bits.append(f"{len(s['existing'])} already in Zoho, so not duplicated")
    if s["customer"]:
        bits.append(f"{len(s['customer'])} already a customer: " + ", ".join(s["customer"][:3]))
    if s.get("not_interested"):
        bits.append(f"{len(s['not_interested'])} tagged Not Interested, so they won't be contacted: "
                    + ", ".join(s["not_interested"][:3]))
    return ("Zoho: " + " · ".join(bits) + ".") if bits else None


def zoho_label(cn: str) -> str:
    rec = get_zoho_store().get(cn)
    if not rec:
        return ""
    return {"created": "✓ New lead", "existing": "• Already a lead", "customer": "⚠ Customer",
            "not_interested": "⛔ Not interested"}.get(rec.get("status"), "")


def zoho_sent_today(log: Dict[str, Any]) -> int:
    today = now_uk().date().isoformat()
    return sum(1 for r in log.values() if r.get("via") == "zoho" and str(r.get("sent_at", "")).startswith(today)) \
        + sum(1 for r in log.values() if r.get("survey_kind") == "follow_up"
              and str(r.get("survey_sent_at", "")).startswith(today))


def zoho_senders() -> Tuple[List[Dict[str, Any]], Optional[str]]:
    if "zoho_from" not in st.session_state:
        try:
            st.session_state["zoho_from"] = ZOHO.from_addresses()
        except ZohoError as exc:
            return [], str(exc)
    return st.session_state["zoho_from"], None


SURVEY_APP = "Prospect Engine"


def survey_lead_id(key: str, rec: Dict[str, Any]) -> str:
    return str((get_zoho_store().get(key) or {}).get("id") or "")


# ---------------- Survey form (hosted on Zoho Forms) ----------------
SURVEY_TAG = _secret_value("SURVEY_TAG", "Survey sent")
SURVEY_DONE_TAG = _secret_value("SURVEY_DONE_TAG", "Survey completed")
SURVEY_DONE_FIELD = _secret_value("SURVEY_DONE_FIELD", "Survey_Completed")
SURVEY_KIND_PITCH = "Pitch email (with PDF)"
SURVEY_KIND_FORM = "Survey form (2-minute questionnaire)"
SURVEY_FILTERS = ["Not surveyed yet", "Survey sent, not completed", "Survey completed", "Everyone"]


def survey_form_url() -> str:
    return _secret_value("SURVEY_FORM_URL").strip()


SURVEY_SRC = "pe"


def survey_signed() -> bool:
    return bool(_secret_value("SURVEY_SIGNING_KEY"))


def survey_link(lead_id: str, company: str, contact: str, email: str, phone: str = "") -> str:
    """The form link with the lead's details filled in.
    Our own survey app (SURVEY_SIGNING_KEY set): signed, so the answers go straight onto this lead.
    Zoho Forms: 'field alias' prefill. Anything else (CRM webform, short link): the plain link."""
    base = survey_form_url()
    if not base:
        return ""
    key = _secret_value("SURVEY_SIGNING_KEY")
    if key and lead_id:
        q = {k: v for k, v in {"lid": lead_id, "c": company, "n": contact, "e": email, "p": phone,
                                "src": SURVEY_SRC}.items() if v}
        q["s"] = hmac.new(key.encode(), f"{lead_id}|{(email or '').strip().lower()}".encode(),
                          hashlib.sha256).hexdigest()[:20]
        return base + ("&" if "?" in base else "?") + urlencode(q)
    if not any(h in base for h in ("forms.zohopublic", "forms.zoho.")):
        return base  # CRM webform / short link: it can't prefill, so send the plain link
    q = {"ZohoLeadId": lead_id, "CompanyName": company, "ContactName": contact, "Email": email, "Phone": phone}
    return base + ("&" if "?" in base else "?") + urlencode({k: v for k, v in q.items() if v})


def survey_email(first: str, company: str, link: str, follow_up: bool, sector_plural: str = "",
                 email: str = "") -> Tuple[str, str]:
    """(subject, plain-text body). The branded HTML turns the 'form: link' line into a button."""
    hello = f"Hi {first}," if first and first not in ("Team", "there") else "Hello,"
    if follow_up:
        subject = f"A quick 2-minute form for {company}"
        intro = (f"I emailed recently about a phone system that works with the software {company} already uses, "
                 "so calls, contacts and call notes all sit in one place.")
    else:
        subject = f"Your phone system, {company}: a quick 2-minute form"
        who = sector_plural or "businesses"
        intro = (f"We help {who} like {company} move to modern cloud phones that work with the software they "
                 "already use, so calls, contacts and call notes all sit in one place.")
    body = "\n\n".join([
        hello,
        intro,
        "To put together an accurate, no-obligation quote, could you spare two minutes for this short form? "
        "It covers your sites, users, handsets and phone numbers, so we don't need to take up your time with a long call."
        + (f" Please use this email address ({email}) on the form, so your answers link straight to your enquiry."
           if email else ""),
        f"Fill in the 2-minute form: {link}",
        "Rather talk it through? Just reply with a good time to call.",
        build_signature(get_sender()),
        "P.S. Not the right time? Just reply \"no thanks\" and I won't chase.",
    ])
    return subject, body


def survey_status(tags: List[str], done_value: Any = None, rec: Optional[Dict[str, Any]] = None) -> str:
    low = [t.lower() for t in tags or []]
    if any(w in t for t in low for w in BLOCKED_SURVEY_WORDS):
        return "⛔ Not interested"
    if done_value in (True, "true", "Yes", "yes", "TRUE") or SURVEY_DONE_TAG.lower() in low:
        return "✅ Completed"
    if SURVEY_TAG.lower() in low or (rec or {}).get("survey_sent_at"):
        return "📨 Sent"
    return "—"


BLOCKED_SURVEY_WORDS = ("not interested",)


def zoho_survey_info(ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """{lead id: {'tags': [...], 'done': value}} for up to a few hundred leads (100 per call)."""
    out: Dict[str, Dict[str, Any]] = {}
    use_done = True
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        body = None
        if use_done and SURVEY_DONE_FIELD:
            try:
                body = ZOHO._request("GET", "/crm/v8/Leads",
                                     params={"ids": ",".join(chunk), "fields": f"Tag,{SURVEY_DONE_FIELD}"})
            except ZohoError:
                use_done = False  # The 'survey completed' field isn't in Zoho (yet): tags only
        if body is None:
            body = ZOHO._request("GET", "/crm/v8/Leads", params={"ids": ",".join(chunk), "fields": "Tag"})
        for r in (body or {}).get("data") or []:
            out[str(r.get("id"))] = {
                "tags": [str(t.get("name") if isinstance(t, dict) else t) for t in (r.get("Tag") or [])],
                "done": r.get(SURVEY_DONE_FIELD) if use_done else None}
    return out


def zoho_add_tag(record_id: str, tag: str) -> None:
    """Adds a tag to a lead (Zoho creates the tag the first time it's used)."""
    body = ZOHO._request("POST", f"/crm/v8/Leads/{record_id}/actions/add_tags",
                         json={"tags": [{"name": tag}], "over_write": False})
    row = ((body or {}).get("data") or [{}])[0]
    if row.get("status") not in ("success", None) and row.get("code") not in ("SUCCESS", None):
        raise ZohoError(f"Zoho CRM error: {row.get('message') or row.get('code') or 'tag not added'}")


def survey_sent_today(log: Dict[str, Any]) -> int:
    """Survey follow-ups sent today (first-contact surveys are already counted as normal sends)."""
    today = now_uk().date().isoformat()
    return sum(1 for r in log.values() if r.get("survey_kind") == "follow_up"
               and str(r.get("survey_sent_at", "")).startswith(today))


def send_surveys(targets: List[Dict[str, Any]], sender: Optional[Dict[str, Any]], follow_up: bool,
                 origin: str = "survey", new_status: Optional[str] = None) -> None:
    """Emails the survey form link from Zoho to each target, adds a note and the 'Survey sent' tag.
    target = {key, lead_id, company, contact, email, phone, sector_plural, record}"""
    done, problems = [], []
    changes: Dict[str, Dict[str, Any]] = {}
    log = get_sent_log()
    who = get_sender().get("name") or SURVEY_APP
    stamp = now_uk().strftime("%d %b %Y %H:%M")
    progress = st.progress(0.0, text="Sending survey forms through Zoho…")
    try:
        for n, t in enumerate(targets, start=1):
            name = t.get("company") or t.get("email") or "Lead"
            progress.progress(n / max(1, len(targets)), text=f"Sending {n} of {len(targets)} · {name}")
            to = (t.get("email") or "").strip()
            if not t.get("lead_id"):
                problems.append(f"{name}: not a Zoho lead, so no survey was sent")
                continue
            if not to or not sender:
                problems.append(f"{name}: no valid email address" if sender else f"{name}: no From address in Zoho")
                continue
            contact = t.get("contact") or ""
            first = contact.split()[0] if contact and contact not in ("Team", "there") else ""
            link = survey_link(t["lead_id"], t.get("company", ""), "" if contact in ("Team", "there") else contact,
                               to, t.get("phone", ""))
            subject, body = survey_email(first, t.get("company", ""), link, follow_up, t.get("sector_plural", ""),
                                          "" if survey_signed() else to)
            try:
                ZOHO.send_mail(t["lead_id"], sender, to, "" if contact in ("Team", "there") else contact,
                               subject, _email_body_html(body, subject), [])
            except ZohoError as exc:
                problems.append(f"{name}: not sent. {exc}")
                continue
            try:
                if new_status:
                    ZOHO.update_lead(t["lead_id"], {"Lead_Status": new_status})
                ZOHO.add_note(t["lead_id"], f"{SURVEY_APP}: survey form emailed",
                              f"Survey form {'follow-up ' if follow_up else ''}emailed by {who} via {SURVEY_APP} on {stamp}."
                              f"\nTo: {to}\nSubject: {subject}\nForm: {link}")
            except ZohoError as exc:
                problems.append(f"{name}: sent, but the note wasn't added. {exc}")
            try:
                zoho_add_tag(t["lead_id"], SURVEY_TAG)
            except ZohoError as exc:
                problems.append(f"{name}: sent, but the '{SURVEY_TAG}' tag wasn't added. {exc}")
            now_iso = now_uk().isoformat(timespec="seconds")
            rec = dict(log.get(t["key"]) or t.get("record") or {})
            rec.update(survey_sent_at=now_iso, survey_sent_by=who, survey_from=sender.get("email", ""),
                       survey_kind="follow_up" if follow_up else "first")
            if not follow_up:  # First contact: the survey IS the email, so log it like a send
                rec.update(via="zoho", status="Survey sent via Zoho", subject=subject, sent_at=now_iso, sent_by=who,
                           to=to, from_address=sender.get("email", ""))
            changes[t["key"]] = rec
            if len(changes) >= 5:  # Save as we go
                record_sent(dict(changes))
                changes.clear()
            done.append(name)
    finally:
        if changes:
            try:
                record_sent(dict(changes))
            except BaseException:
                save_log_quietly(SENT_LOG, dict(changes), f"{SURVEY_APP}: surveys saved after the page was interrupted")
                raise
            changes.clear()
    progress.empty()
    st.session_state.pop("survey_info", None)  # Re-read survey status next time
    st.session_state["zoho_push_result"] = {"done": done, "problems": problems, "origin": origin, "prepare": False}


SURVEY_SOURCE = _secret_value("SURVEY_LEAD_SOURCE", "Survey form")
SURVEY_LEAD_ID_FIELD = _secret_value("SURVEY_LEAD_ID_FIELD", "Survey_Lead_ID")


def survey_leftovers() -> List[Dict[str, Any]]:
    """The extra leads the webform leaves behind once its answers have been copied onto the original lead."""
    src = SURVEY_SOURCE.replace("'", "\\'")
    q = (f"select id, Company, Email, Created_Time from Leads where Lead_Source = '{src}' "
         f"and {SURVEY_LEAD_ID_FIELD} is not null order by Created_Time desc limit 0, 200")
    body = ZOHO._request("POST", "/crm/v8/coql", json={"select_query": q})
    return (body or {}).get("data") or []


def delete_zoho_leads(ids: List[str]) -> int:
    """Moves leads to Zoho's recycle bin (restorable there for 60 days). Returns how many went."""
    gone = 0
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        body = ZOHO._request("DELETE", "/crm/v8/Leads", params={"ids": ",".join(chunk)}) or {}
        gone += sum(1 for r in body.get("data") or [] if r.get("status") == "success")
    return gone


def render_survey_tidy() -> None:
    with st.expander("🧹  Tidy up leftover survey leads", expanded=False):
        st.caption(f"Each form submission creates a spare lead (Lead Source '{SURVEY_SOURCE}') once its answers are"
                   " copied onto the original lead. This finds those spares and moves them to Zoho's recycle bin."
                   " Forwarded forms that matched no lead are kept.")
        if st.session_state.get("survey_tidy_msg"):
            st.success(st.session_state.pop("survey_tidy_msg"))
        if st.button("Find leftover survey leads", key="sv_tidy_find"):
            try:
                st.session_state["survey_leftovers"] = survey_leftovers()
            except ZohoError as exc:
                st.session_state.pop("survey_leftovers", None)
                st.error(f"Couldn't search Zoho: {exc}. If the field name differs, set SURVEY_LEAD_ID_FIELD in Secrets"
                         f" to the Survey Lead ID field's API name (currently {SURVEY_LEAD_ID_FIELD}).")
        found = st.session_state.get("survey_leftovers")
        if found is None:
            return
        if not found:
            st.info("Nothing to tidy: no leftover survey leads.")
            return
        st.dataframe(pd.DataFrame([{"Company": r.get("Company") or "", "Email": r.get("Email") or "",
                                    "Submitted": str(r.get("Created_Time") or "")[:16].replace("T", " ")} for r in found]),
                     hide_index=True, **FULL_WIDTH)
        try:
            pop = st.popover(f"🗑  Move {len(found)} to the recycle bin", **FULL_WIDTH)
        except TypeError:
            pop = st.popover(f"🗑  Move {len(found)} to the recycle bin")
        with pop:
            st.markdown(f"Move **{len(found)}** spare survey leads to Zoho's recycle bin?")
            st.caption("The original leads keep the answers. These can be restored from the recycle bin for 60 days.")
            if st.button("Yes, tidy them up", type="primary", key="sv_tidy_go", **FULL_WIDTH):
                try:
                    n = delete_zoho_leads([str(r["id"]) for r in found if r.get("id")])
                    st.session_state["survey_tidy_msg"] = f"{n} leftover survey lead(s) moved to the recycle bin."
                except ZohoError as exc:
                    st.session_state["survey_tidy_msg"] = f"Stopped part way: {exc}"
                st.session_state.pop("survey_leftovers", None)
                st.rerun()


SURVEY_RESPONSES = SentLog("GITHUB_SURVEY_PATH", "survey_responses.json", ".survey_responses.json")


def survey_days_ago(rec: Dict[str, Any]) -> Optional[int]:
    try:
        sent = datetime.fromisoformat(str(rec.get("sent_at")))
        if sent.tzinfo is None:
            sent = sent.replace(tzinfo=now_uk().tzinfo)
        return max(0, (now_uk() - sent).days)
    except Exception:
        return None


def render_survey_page() -> None:
    """Survey follow-ups: leads this app has already emailed, sent the 2-minute form as a follow-up."""
    section_header("01", "Survey follow-ups",
                   "Send the 2-minute survey form to leads this app has already emailed")
    if not survey_form_url():
        st.info("Add the form link first: in this app's Streamlit Secrets add  SURVEY_FORM_URL = \"https://forms.zohopublic.eu/…\""
                "  (from Zoho Forms → Share → Public link), save, and reboot.")
        return
    if not ZOHO.configured:
        st.warning("Zoho isn't connected, so surveys can't be sent.")
        return
    show_zoho_push_result("survey")
    render_survey_tidy()
    log = get_sent_log()
    rows = []
    for key, r in log.items():
        if not r or not (r.get("to") or "").strip():
            continue
        lead_id = survey_lead_id(key, r)
        if not lead_id:
            continue
        rows.append((key, lead_id, r))
    if not rows:
        st.caption("No emailed Zoho leads in this app's sent log yet.")
        return
    c1, c2, c3 = st.columns([1, 1.4, 1.6])
    with c1:
        min_days = st.number_input("Emailed at least this many days ago", 0, 365, 3, key="sv_days")
    with c2:
        which = st.selectbox("Show", SURVEY_FILTERS, key="sv_filter")
    with c3:
        find = st.text_input("Search", key="sv_find", placeholder="Company, name or email")
    if "survey_info" not in st.session_state or st.button("↻  Re-check survey status in Zoho", key="sv_refresh"):
        with st.spinner("Checking tags in Zoho…"):
            try:
                st.session_state["survey_info"] = zoho_survey_info(sorted({lid for _, lid, _ in rows}))
            except ZohoError as exc:
                st.session_state["survey_info"] = {}
                st.warning(f"Couldn't read survey status from Zoho: {exc}")
    info = st.session_state.get("survey_info") or {}
    if "survey_responses" not in st.session_state or st.session_state.get("sv_refresh"):
        done_by: Dict[str, str] = {}
        for resp in SURVEY_RESPONSES.load().values():
            if isinstance(resp, dict):
                for lid in {str(resp.get("lead_id") or ""), str(resp.get("link_lead_id") or "")} - {""}:
                    done_by[lid] = max(done_by.get(lid, ""), str(resp.get("submitted_at") or ""))
        st.session_state["survey_responses"] = done_by
    responses = st.session_state.get("survey_responses") or {}
    table = []
    for key, lead_id, r in rows:
        days = survey_days_ago(r)
        if days is None or days < min_days:
            continue
        i_ = info.get(lead_id) or {}
        status = survey_status(i_.get("tags") or [], i_.get("done") or bool(responses.get(lead_id)), r)
        if status == "⛔ Not interested":
            continue
        if which == "Not surveyed yet" and status != "—":
            continue
        if which == "Survey sent, not completed" and status != "📨 Sent":
            continue
        if which == "Survey completed" and status != "✅ Completed":
            continue
        hay = " ".join(str(r.get(k, "")) for k in ("company_name", "contact", "to")).lower()
        if find and find.lower() not in hay:
            continue
        table.append({"key": key, "lead_id": lead_id, "Send": False, "Company": r.get("company_name") or "",
                      "Contact": r.get("contact") if r.get("contact") not in ("Team", "there") else "",
                      "Email": r.get("to") or "", "Emailed": str(r.get("sent_at", ""))[:10], "Days": days,
                      "Survey": status, "Sent on": str(r.get("survey_sent_at", ""))[:10]})
    table.sort(key=lambda x: -x["Days"])
    st.caption(f"{len(table)} lead(s) match. Tick the ones to send the survey to. Leads tagged Not Interested are always left out.")
    if not table:
        return
    pick_all = st.toggle("Tick all shown (not yet surveyed only)", key="sv_all")
    for row in table:
        row["Send"] = bool(pick_all and row["Survey"] == "—")
    df = pd.DataFrame(table)
    edited = st.data_editor(
        df, hide_index=True, key=f"sv_editor_{st.session_state.get('sent_log_ver', 0)}_{int(pick_all)}",
        column_order=["Send", "Company", "Contact", "Email", "Emailed", "Days", "Survey", "Sent on"],
        disabled=["Company", "Contact", "Email", "Emailed", "Days", "Survey", "Sent on"],
        column_config={"Send": st.column_config.CheckboxColumn("Send", width=60),
                       "Days": st.column_config.NumberColumn("Days ago", width=70),
                       "Survey": st.column_config.TextColumn("Survey", width=110)},
        height=min(38 + 35 * len(df), 460), **FULL_WIDTH)
    chosen = [table[i] for i, v in enumerate(list(edited["Send"])) if v]
    resend = sum(1 for c in chosen if c["Survey"] != "—")
    if resend:
        st.caption(f"⚠️ {resend} of the ticked leads have already had the survey; they'll get it again.")
    senders, err = zoho_senders()
    if err or not senders:
        st.error(err or "Zoho didn't return any address to send from.")
        return
    st.selectbox("Send from", list(range(len(senders))), key="sv_from",
                 format_func=lambda i: f"{senders[i].get('user_name') or ''} <{senders[i]['email']}>".strip()
                 + (" · org address" if senders[i].get("type") == "org_email" else ""))
    sent_today = zoho_sent_today(log)
    left = max(0, ZOHO_SEND_LIMIT - sent_today)
    if len(chosen) > left:
        st.warning(f"Zoho allows {ZOHO_SEND_LIMIT} emails a day and {sent_today} have gone today, so only the first {left} will be sent.")
        chosen = chosen[:left]
    label = f"📋  Send the survey to {len(chosen)} {'lead' if len(chosen) == 1 else 'leads'}"
    try:
        pop = st.popover(label, key=f"sv_pop_{st.session_state.get('sent_log_ver', 0)}", disabled=not chosen, **FULL_WIDTH)
    except TypeError:
        pop = st.popover(label, disabled=not chosen, **FULL_WIDTH)
    with pop:
        idx = st.session_state.get("sv_from", 0)
        frm = senders[idx] if isinstance(idx, int) and 0 <= idx < len(senders) else senders[0]
        st.markdown(f"Email the survey form to **{len(chosen)}** now from **{esc(frm['email'])}**?")
        st.caption(f"Each lead gets a note and the '{SURVEY_TAG}' tag in Zoho. This can't be undone.")
        if st.button("Yes, send the survey", type="primary", key="sv_confirm", **FULL_WIDTH):
            targets = []
            for c in chosen:
                r = log.get(c["key"]) or {}
                targets.append({"key": c["key"], "lead_id": c["lead_id"], "company": c["Company"],
                                "contact": r.get("contact") or "", "email": c["Email"], "phone": r.get("phone") or "",
                                "sector_plural": survey_sector_plural(r.get("vertical")), "record": r})
            send_surveys(targets, frm, follow_up=True, origin="survey")
            st.rerun()
    st.caption(f"Sent via Zoho today: {sent_today} of {ZOHO_SEND_LIMIT}.")


def survey_sector_plural(vertical: Optional[str]) -> str:
    try:
        return SECTOR_COPY.get(vertical or "", {}).get("sector_plural", "")
    except Exception:
        return ""


def send_via_zoho(cns: List[str], sender: Optional[Dict[str, Any]], origin: str = "panel",
                  survey: bool = False) -> None:
    """Makes sure each firm is a Zoho lead, then sends its pitch from Zoho, moves the status on and adds a note."""
    queue = st.session_state.get("queue", {})
    push_to_zoho_leads(cns)
    store = get_zoho_store()
    done, problems = [], []
    sent_changes: Dict[str, Dict[str, Any]] = {}
    who = get_sender().get("name") or "Prospect Engine"
    stamp = now_uk().strftime("%d %b %Y %H:%M")
    statuses = ZOHO.picklist(st.session_state.get("pe_lead_fields") or {}, "Lead_Status")
    if survey:  # The 2-minute survey form as the first email (no PDF)
        targets = []
        for cn in cns:
            item = queue.get(cn)
            if not item:
                continue
            lead_s: ScrapedLead = item["lead"]
            rec = store.get(cn) or {}
            nm = lead_display_name(lead_s)
            if rec.get("status") in ("not_interested", "customer"):
                problems.append(f"{nm}: {'tagged Not Interested' if rec.get('status') == 'not_interested' else 'already a customer'}"
                                " in Zoho, so no survey was sent")
                continue
            ensure_draft(item)
            to_s = (item.get("to") or "").strip()
            if not to_s or not clean_email(to_s):
                problems.append(f"{nm}: no valid email address")
                continue
            targets.append({"key": cn, "lead_id": rec.get("id"), "company": nm,
                            "contact": infer_contact_name_and_role(lead_s, item["vertical"])[0], "email": to_s,
                            "phone": (lead_s.phones_found or [""])[0],
                            "sector_plural": survey_sector_plural(item["vertical"]), "record": sent_record(item)})
        send_surveys(targets, sender, follow_up=False, origin=origin,
                     new_status="Attempted to Contact" if "Attempted to Contact" in statuses else None)
        st.session_state["zoho_push_result"]["problems"][:0] = problems
        return
    progress = st.progress(0.0, text="Sending through Zoho…")
    try:
        for n, cn in enumerate(cns, start=1):
            item = queue.get(cn)
            if not item:
                continue
            lead: ScrapedLead = item["lead"]
            name = lead_display_name(lead)
            progress.progress(n / len(cns), text=f"Sending {n} of {len(cns)} · {name}")
            rec = store.get(cn) or {}
            if rec.get("status") == "not_interested":
                problems.append(f"{name}: tagged Not Interested in Zoho, so it wasn't sent")
                continue
            if rec.get("status") == "customer":
                problems.append(f"{name}: already a customer in Zoho, so no new-business pitch was sent")
                continue
            if not rec.get("id"):
                problems.append(f"{name}: couldn't add it to Zoho, so it wasn't sent")
                continue
            ensure_draft(item)
            to = (item.get("to") or "").strip()
            if not to or not clean_email(to) or not sender:
                problems.append(f"{name}: no valid email address" if sender else f"{name}: no From address in Zoho")
                continue
            contact = infer_contact_name_and_role(lead, item["vertical"])[0]
            try:
                att = []
                if st.session_state["opt_attach"]:
                    pdf = create_sector_overview_pdf(lead, item["vertical"])
                    att = [ZOHO.upload_file(f"{BRAND_FILE}_overview_{draft_filename_part(lead.company_name)}.pdf", pdf)]
                ZOHO.send_mail(rec["id"], sender, to, "" if contact in ("Team", "there") else contact,
                               item["subject"], _email_body_html(item["body"], item["subject"]), att)
            except ZohoError as exc:
                problems.append(f"{name}: not sent. {exc}")
                continue
            try:
                if "Attempted to Contact" in statuses:
                    ZOHO.update_lead(rec["id"], {"Lead_Status": "Attempted to Contact"})
                ZOHO.add_note(rec["id"], "Prospect Engine: pitch emailed",
                              f"Emailed by {who} via Prospect Engine on {stamp}.\nTo: {to}\nSubject: {item['subject']}\n"
                              f"Pitch: {item['vertical']}" + (" (overview PDF attached)" if st.session_state["opt_attach"] else ""))
            except ZohoError as exc:
                problems.append(f"{name}: sent, but the lead wasn't updated. {exc}")
            sent_changes[cn] = dict(sent_record(item), via="zoho", status="Emailed via Zoho",
                                    from_address=sender.get("email", ""))
            if len(sent_changes) >= 5:  # Save as we go, so nothing is lost if the page is interrupted
                record_sent(dict(sent_changes))
                sent_changes.clear()
            done.append(name)
    finally:
        # Save whatever was sent even if the run is cut short (e.g. switching page mid-send)
        if sent_changes:
            try:
                record_sent(dict(sent_changes))
            except BaseException:  # Page stopping: save without touching the page, then let it stop
                save_log_quietly(SENT_LOG, dict(sent_changes), "Prospect Engine: sends saved after the page was interrupted")
                raise
            sent_changes.clear()
    progress.empty()
    if sent_changes:
        record_sent(sent_changes)
    st.session_state["zoho_push_result"] = {"done": done, "problems": problems, "origin": origin}


def show_zoho_push_result(origin: str) -> None:
    res = st.session_state.get("zoho_push_result")
    if not res or res.get("origin") != origin:
        return
    st.session_state.pop("zoho_push_result", None)
    if res["done"]:
        st.success(f"{len(res['done'])} sent via Zoho: " + ", ".join(res["done"][:6]) + ("…" if len(res["done"]) > 6 else ""))
    for p_ in res["problems"]:
        st.warning(p_)


def render_zoho_setup() -> None:
    render_html(
        '<div class="pe-panel"><div class="h">One-off Zoho setup</div>'
        '<div style="font-size:.84rem;line-height:1.55;color:var(--muted)">'
        "<b>1.</b> In <b>api-console.zoho.eu</b>, open your Self Client and go to <b>Generate Code</b>.<br>"
        "<b>2.</b> Paste the scope below, pick <b>10 minutes</b> and click <b>Create</b>.<br>"
        "<b>3.</b> Paste the code here and click Connect. Be quick: codes expire.</div></div>"
    )
    st.code(ZOHO_SCOPE, language=None)
    with st.form("zoho_setup", border=False):
        setup_code = st.text_input("Code from Zoho", type="password", placeholder="1000.xxxxxxxx…")
        setup_go = st.form_submit_button("Connect Zoho", type="primary", **FULL_WIDTH)
    if setup_go:
        if not setup_code.strip():
            st.warning("Paste the code from Zoho first.")
        else:
            with st.spinner("Asking Zoho for a permanent key…"):
                st.session_state["zoho_setup_result"] = ZOHO.exchange_code(setup_code)
    result = st.session_state.get("zoho_setup_result") or {}
    if result.get("error"):
        st.error(result["error"])
    elif result.get("refresh_token"):
        st.success("Connected. Last step:")
        st.code(f'ZOHO_REFRESH_TOKEN = "{result["refresh_token"]}"', language=None)
        st.caption("Copy that line into this app's Streamlit Secrets, save, then reboot. Don't share it in emails or chats.")


def render_leads_table(df: pd.DataFrame, key: str):
    """Selectable company table with tidy columns. Works on old and new Streamlit versions."""
    column_config = {
        "Company Name": st.column_config.TextColumn("Company Name", width=200),
        "Contacted": st.column_config.TextColumn("Contacted", width=78, help="Already emailed (from the sent log)"),
        "Company Number": st.column_config.TextColumn("Co. #", width=74),
        "Incorporated": st.column_config.DateColumn("Since", format="MMM YYYY", width=78),
        "Town": st.column_config.TextColumn("Town", width=95),
        "Companies House": st.column_config.LinkColumn(
            "Registry", display_text="View ↗", width=62,
            help="Opens the company's Companies House page in a new tab",
        ),
    }
    column_order = [c for c in column_config if c in df.columns]
    table_height = min(38 + 35 * len(df), 420)  # Grows with rows, scrolls after ~11
    common = dict(
        hide_index=True,
        selection_mode="multi-row",
        on_select="rerun",
        column_config=column_config,
        column_order=column_order,
        height=table_height,
        key=key,
    )
    try:
        return st.dataframe(df, width="stretch", **common)  # Streamlit 1.46+
    except Exception:
        return st.dataframe(df, use_container_width=True, **common)  # Older Streamlit


st.set_page_config(
    page_title=f"{APP_NAME} · Prospect Discovery & Dossiers",
    page_icon="🎯",
    layout="wide",
)
inject_css()

for _k, _v in {"stat_searches": 0, "stat_firms": 0, "stat_dossiers": 0}.items():
    st.session_state.setdefault(_k, 0)

hero_slot = st.empty()  # Filled at the end so the progress stepper reflects this run's actions
MAX_BATCH = 25
SENT_LOG = SentLog()
for _k, _v in {"opt_branded": True, "opt_attach": True, "opt_switch": True, "queue_editor_ver": 0, "sent_log_ver": 0}.items():
    st.session_state.setdefault(_k, _v)


def save_log_quietly(store: "SentLog", changes: Dict[str, Any], message: str) -> None:
    """Used when the page is stopping mid-send (e.g. someone switched page): Streamlit calls aren't allowed then,
    so save straight to GitHub and flag every session to reload the log on its next run."""
    import sys as _sys
    try:
        store.apply(changes, message)
    except Exception:
        return
    _sys._sy_log_epoch = getattr(_sys, "_sy_log_epoch", 0) + 1


def _log_epoch() -> int:
    import sys as _sys
    return getattr(_sys, "_sy_log_epoch", 0)


def get_sent_log() -> Dict[str, Any]:
    """Loaded once per session; refreshed after every change (and by the sidebar Refresh button)."""
    if "sent_log_data" not in st.session_state or st.session_state.get("sent_log_data_epoch") != _log_epoch():
        st.session_state["sent_log_data"] = SENT_LOG.load()
        st.session_state["sent_log_data_epoch"] = _log_epoch()
    return st.session_state["sent_log_data"]


def bump_queue_editor() -> None:
    st.session_state["queue_editor_ver"] = st.session_state.get("queue_editor_ver", 0) + 1


def record_sent(changes: Dict[str, Optional[Dict[str, Any]]]) -> None:
    """Saves sent ticks/unticks to the permanent log and refreshes every view of it."""
    local = dict(get_sent_log())
    try:
        n_on = sum(1 for v in changes.values() if v)
        latest = SENT_LOG.apply(changes, f"Prospect Engine: {n_on} marked sent, {len(changes) - n_on} unmarked")
        st.session_state["sent_log_data"] = latest
    except Exception as exc:
        for key, rec in changes.items():  # Keep this session correct even if saving failed
            if rec is None:
                local.pop(key, None)
            else:
                local[key] = rec
        st.session_state["sent_log_data"] = local
        st.session_state["sent_log_error"] = str(exc) if isinstance(exc, RuntimeError) else "Couldn't save the sent log."
    st.session_state["sent_log_ver"] = st.session_state.get("sent_log_ver", 0) + 1
    bump_queue_editor()


# ------------------------------------------------------------------
# CALL LIST (permanent, shared telemarketing database)
# ------------------------------------------------------------------
CALL_STORE = SentLog("GITHUB_CALLS_PATH", "call_list.json", ".call_list.json")

CALL_OPEN = ["New", "No answer", "Call back"]
CALL_DONE = ["Interested", "Not interested", "Wrong number", "Do not call"]
CALL_STATUSES = CALL_OPEN + CALL_DONE
CALL_STATUS_TONE = {"New": "accent", "No answer": "muted", "Call back": "warn", "Interested": "good",
                    "Not interested": "", "Wrong number": "bad", "Do not call": "bad"}
VERIFIED_WEBSITE = ("High", "Medium", "Manual")


def get_call_list() -> Dict[str, Any]:
    if "call_list_data" not in st.session_state:
        st.session_state["call_list_data"] = CALL_STORE.load()
    return st.session_state["call_list_data"]


def save_calls(changes: Dict[str, Optional[Dict[str, Any]]], message: str) -> None:
    """Writes call-list changes to the permanent store (re-reads first so colleagues' edits survive)."""
    local = dict(get_call_list())
    try:
        st.session_state["call_list_data"] = CALL_STORE.apply(changes, f"Prospect Engine calls: {message}")
    except Exception as exc:
        for key, rec in changes.items():
            if rec is None:
                local.pop(key, None)
            else:
                local[key] = rec
        st.session_state["call_list_data"] = local
        st.session_state["call_list_error"] = str(exc) if isinstance(exc, RuntimeError) else "Couldn't save the call list."
    st.session_state["call_ver"] = st.session_state.get("call_ver", 0) + 1


def call_record_from_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Only what a caller needs: who, which number, and the website if we've verified it."""
    lead: ScrapedLead = item["lead"]
    contact, role = infer_contact_name_and_role(lead, item["vertical"])
    website = lead.website_url if (lead.website_url and lead.website_confidence in VERIFIED_WEBSITE) else ""
    return {
        "company_number": lead.company_number or "",
        "firm": lead_display_name(lead),
        "legal_name": lead.company_name,
        "contact": contact,
        "role": role,
        "directors": [display_officer_name(o.name) for o in lead.officers if o.raw_role in DECISION_MAKER_ROLES][:3],
        "phone": (lead.phones_found or [""])[0],
        "other_phones": lead.phones_found[1:3],
        "website": website,
        "linkedin": getattr(lead, "linkedin_url", None) or "",
        "sector": item["vertical"],
        "address": lead.registered_address or "",
        "added_at": now_uk().isoformat(timespec="seconds"),
        "added_by": get_sender().get("name", ""),
        "status": "New",
        "notes": "",
        "callback": "",
        "attempts": 0,
        "last_called": "",
        "last_called_by": "",
        "history": [],
    }


def call_queue(calls: Dict[str, Any]) -> List[str]:
    """Order to work through: callbacks that are due, then new firms, then retries (least recent first)."""
    now = now_uk().replace(tzinfo=None)
    due, new, retry = [], [], []
    for cn, r in calls.items():
        status = r.get("status", "New")
        if status == "Call back":
            try:
                when = datetime.fromisoformat(r.get("callback") or "")
                when = when.replace(tzinfo=None)
            except ValueError:
                when = now
            if when <= now:
                due.append((when, cn))
        elif status == "New":
            new.append((r.get("added_at", ""), cn))
        elif status == "No answer":
            retry.append((r.get("last_called", ""), cn))
    return [c for _, c in sorted(due)] + [c for _, c in sorted(new)] + [c for _, c in sorted(retry)]


def fmt_when(iso: str, with_time: bool = True) -> str:
    try:
        d = datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    return d.strftime("%d %b %H:%M" if with_time else "%d %b").lstrip("0")


# ------------------------------------------------------------------
# CONFIRMED CONTACTS (found by a person, e.g. on LinkedIn; saved permanently)
# ------------------------------------------------------------------
CONTACTS_STORE = SentLog("GITHUB_CONTACTS_PATH", "contacts.json", ".contacts.json")


def get_contacts() -> Dict[str, Any]:
    if "contacts_data" not in st.session_state:
        st.session_state["contacts_data"] = CONTACTS_STORE.load()
    return st.session_state["contacts_data"]


def apply_contact(item: Dict[str, Any], rec: Dict[str, Any]) -> None:
    """Puts a confirmed contact onto a queued firm: greeting, role, LinkedIn and (if given) email."""
    lead: ScrapedLead = item["lead"]
    lead.contact_name = (rec.get("name") or "").strip() or None
    lead.contact_role = (rec.get("role") or "").strip() or None
    lead.linkedin_url = (rec.get("linkedin") or "").strip() or None
    email = clean_email(rec.get("email") or "") if rec.get("email") else None
    lead.contact_email = email
    if email:
        if email not in lead.emails_found:
            lead.emails_found = [email] + list(lead.emails_found)
        if item.get("to") != email:
            item["to"] = email
            item["to_ver"] = item.get("to_ver", 0) + 1
    item["sig"] = None  # Rebuild the draft with the new greeting


def save_contact(cn: str, name: str = "", role: str = "", linkedin: str = "", email: str = "") -> Optional[str]:
    """Saves a confirmed contact permanently and applies it. Returns an error message or None."""
    email = (email or "").strip()
    if email and not clean_email(email):
        return f"'{email}' doesn't look like a valid email address."
    current = dict(get_contacts().get(cn) or {})
    rec = {
        "name": (name or "").strip() or current.get("name", ""),
        "role": (role or "").strip() or current.get("role", ""),
        "linkedin": (linkedin or "").strip() or current.get("linkedin", ""),
        "email": clean_email(email) if email else current.get("email", ""),
        "updated_at": now_uk().isoformat(timespec="seconds"),
        "updated_by": get_sender().get("name", ""),
    }
    item = st.session_state.get("queue", {}).get(cn)
    if item:
        rec["firm"] = item["lead"].company_name
    try:
        st.session_state["contacts_data"] = CONTACTS_STORE.apply({cn: rec}, "contact updated")
    except Exception:
        st.session_state.setdefault("contacts_data", {})[cn] = rec
    if item:
        apply_contact(item, rec)
    bump_queue_editor()
    return None


def linkedin_people_url(lead: ScrapedLead) -> str:
    officer = pick_decision_maker(lead.officers)
    person = display_officer_name(officer.name) if officer else "director"
    return "https://www.linkedin.com/search/results/people/?keywords=" + quote(f"{person} {lead_display_name(lead)}")


def linkedin_company_url(lead: ScrapedLead) -> str:
    return "https://www.linkedin.com/search/results/companies/?keywords=" + quote(lead_display_name(lead))


def suggest_email(full_name: str, lead: ScrapedLead) -> Optional[str]:
    """If the firm's own website shows how staff emails are formed, apply that to a new name.
    e.g. site lists sarah.jones@firm.co.uk -> 'Mark Hughes' becomes mark.hughes@firm.co.uk. Unverified."""
    words = [re.sub(r"[^a-z]", "", w.lower()) for w in (full_name or "").split()]
    words = [w for w in words if w]
    if not words or not lead.website_url or lead.website_confidence not in ("High", "Medium", "Manual"):
        return None
    site = domain_of(lead.website_url) or ""
    own = [e for e in lead.emails_found if e.split("@", 1)[1] == site or e.split("@", 1)[1].endswith("." + site)]
    first, last = words[0], (words[-1] if len(words) > 1 else "")
    for e in own:
        local, dom = e.split("@", 1)
        if re.fullmatch(r"[a-z]+\.[a-z]+", local) and last:
            return f"{first}.{last}@{dom}"
    for e in own:
        local, dom = e.split("@", 1)
        if first_name_from_email(e) and re.fullmatch(r"[a-z]+", local):
            return f"{first}@{dom}"
    return None


def sent_record(item: Dict[str, Any]) -> Dict[str, Any]:
    lead: ScrapedLead = item["lead"]
    return {
        "company_name": lead.company_name,
        "to": item.get("to", ""),
        "contact": infer_contact_name_and_role(lead, item["vertical"])[0],
        "vertical": item["vertical"],
        "subject": item.get("subject", ""),
        "sent_at": now_uk().isoformat(timespec="seconds"),
        "sent_by": get_sender().get("name", ""),
        "status": "Emailed" if item.get("to") else "Handled",
    }


def add_to_queue(lead: ScrapedLead, vertical: str, cn: Optional[str] = None) -> None:
    queue = st.session_state.setdefault("queue", {})
    order = st.session_state.setdefault("queue_order", [])
    cn = cn or lead.company_number or lead.company_name
    contact, _ = infer_contact_name_and_role(lead, vertical)
    queue[cn] = {
        "lead": lead,
        "vertical": vertical,
        "include": True,
        "to": pick_primary_email(lead, contact) or "",
        "to_ver": queue.get(cn, {}).get("to_ver", 0) + 1,
        "subject": None,
        "body": None,
        "sig": None,
    }
    if cn not in order:
        order.append(cn)
    stored = get_contacts().get(cn)
    if stored:
        apply_contact(queue[cn], stored)
    bump_queue_editor()


def rescan_for_emails(cns: List[str]) -> Tuple[int, int, int]:
    """Looks at each firm's website again with the current email finder (no Companies House or Google lookups).
    Firms where an email turns up move to Ready to email, and new Zoho leads get the email too.
    Returns (looked at, emails found, Zoho leads updated)."""
    queue = st.session_state.get("queue", {})
    todo = [c for c in cns if c in queue and queue[c]["lead"].website_url]
    if not todo:
        return 0, 0, 0
    progress = st.progress(0.0, text="Looking again…")

    def _one(c: str) -> Tuple[str, Dict[str, Any]]:
        lead = queue[c]["lead"]
        return c, LeadEnricher(ch_api_key=ch_api_key).scrape_contact_channels(
            lead.website_url, names=[lead.company_name, lead.trading_name or ""])

    found: List[str] = []
    with ThreadPoolExecutor(max_workers=min(4, len(todo))) as pool:
        futures = [pool.submit(_one, c) for c in todo]
        for n, fut in enumerate(as_completed(futures), start=1):
            try:
                c, res = fut.result()
            except Exception:
                progress.progress(n / len(todo), text=f"Looked again at {n} of {len(todo)}")
                continue
            lead = queue[c]["lead"]
            emails, _dead = filter_deliverable(res.get("emails") or [])
            if emails:
                lead.emails_found = emails
                lead.other_emails = res.get("other_emails") or []
                lead.discovery_notes = list(lead.discovery_notes) + ["Looked again: " + (n_ or "email found on the site")
                                                                     for n_ in (res.get("notes") or [""])]
                if not lead.phones_found and res.get("phones"):
                    lead.phones_found = res["phones"]
                contact, _ = infer_contact_name_and_role(lead, queue[c]["vertical"])
                queue[c]["to"] = pick_primary_email(lead, contact) or ""
                queue[c]["to_ver"] = queue[c].get("to_ver", 0) + 1
                queue[c]["subject"] = queue[c]["body"] = queue[c]["sig"] = None
                found.append(c)
            progress.progress(n / len(todo), text=f"Looked again at {n} of {len(todo)} · {lead_display_name(lead)}")
    progress.empty()

    updated = 0
    already = set(get_zoho_store()) if found and zoho_on() else set()
    if found and zoho_on() and st.session_state.get("zoho_auto", True):  # Now they have an email, they belong in Zoho
        push_to_zoho_leads([c for c in found if c not in already])
    if found and zoho_on():  # Leads this app created had no email: add it, so Lead Revival and MY PA can use it too
        store = get_zoho_store()
        for c in [c for c in found if c in already]:
            rec = store.get(c) or {}
            if rec.get("status") == "created" and rec.get("id") and queue[c]["to"]:
                try:
                    ZOHO.update_lead(rec["id"], {"Email": queue[c]["to"]})
                    updated += 1
                except ZohoError:
                    pass
    bump_queue_editor()
    return len(todo), len(found), updated


def run_enrichment(
    rows: List[Dict[str, Any]],
    vertical: str,
    manual_websites: Optional[Dict[str, str]] = None,
) -> None:
    """Enriches firms 4 at a time with a progress bar and adds them to the review queue.
    rows need 'Company Number' and 'Company Name'. manual_websites: {company_number: url}."""
    manual_websites = manual_websites or {}
    progress = st.progress(0.0, text="Starting enrichment…")

    sra_data = sra_register() if vertical in SRA_SECTORS and _secret_value("SRA_API_KEY") else []

    def _enrich(row: Dict[str, Any]) -> ScrapedLead:
        enricher = LeadEnricher(ch_api_key=ch_api_key)
        enricher.sra_data = sra_data
        return enricher.enrich_selected_company(
            company_number=row["Company Number"],
            sector_name=vertical,
            manual_website=manual_websites.get(row["Company Number"]) or None,
        )

    results: Dict[str, ScrapedLead] = {}
    failures: List[str] = []
    with ThreadPoolExecutor(max_workers=min(4, len(rows))) as pool:
        futures = {pool.submit(_enrich, row): row for row in rows}
        for done, fut in enumerate(as_completed(futures), start=1):
            row = futures[fut]
            try:
                results[row["Company Number"]] = fut.result()
            except Exception:
                failures.append(friendly_company_name(row["Company Name"]))
            progress.progress(
                done / len(rows),
                text=f"Enriched {done} of {len(rows)} · {friendly_company_name(row['Company Name'])}",
            )
    progress.empty()

    first_cn = None
    for row in rows:  # Keep the table's order in the queue
        cn = row["Company Number"]
        if cn in results:
            add_to_queue(results[cn], vertical)
            first_cn = first_cn or cn
    if first_cn:
        st.session_state["current_cn"] = first_cn
        st.session_state["current_cn_select"] = first_cn
    st.session_state["stat_dossiers"] += len(results)
    if results and zoho_on() and st.session_state.get("zoho_auto", True):
        worthy = [c for c in results if zoho_worthy(c)]
        held = len(results) - len(worthy)
        summary = push_to_zoho_leads(worthy)
        if zoho_summary_text(summary) or held:
            st.info((zoho_summary_text(summary) or "Zoho: nothing new to add.")
                    + (f" {held} {'firm' if held == 1 else 'firms'} with no email kept out of Zoho;"
                       " they're under No email found, and go into Zoho if an email turns up." if held else ""))
        if "permission" in summary["error"]:
            st.warning("Zoho: the key in Secrets doesn't have all the permissions this app needs, so no firms were added."
                       " Open **Reconnect Zoho** in the sidebar to get this app its own key, then use **Add firms not yet in Zoho**"
                       " under Review & send.")
        else:
            for err in summary["error"]:
                st.warning("Zoho: couldn't add " + err)
    if failures:
        st.warning("Couldn't enrich: " + ", ".join(failures))
    if len(rows) > 1 and results:
        with_email = sum(1 for cn in results if results[cn].emails_found)
        st.success(
            f"{len(results)} firms enriched: {with_email} with an email address,"
            f" {len(results) - with_email} without. See Review & send below."
        )


def ensure_draft(item: Dict[str, Any]) -> None:
    """(Re)builds a firm's subject/body when first needed or when options/signature change."""
    sig = (item["vertical"], st.session_state["opt_attach"], st.session_state["opt_switch"],
           tuple(sorted(get_sender().items())),
           getattr(item["lead"], "contact_name", None), getattr(item["lead"], "contact_role", None))
    if item.get("sig") != sig or item.get("body") is None:
        item["subject"] = build_email_subject(item["lead"], item["vertical"])
        item["body"] = build_email_pitch(
            item["lead"], item["vertical"],
            include_attachment_line=st.session_state["opt_attach"],
            include_switchover=st.session_state["opt_switch"],
        )
        item["sig"] = sig



try:
    secret_ch_key = st.secrets.get("COMPANIES_HOUSE_KEY", "")
except Exception:
    secret_ch_key = ""


def columns(spec, **kwargs):
    """st.columns with bottom alignment where supported (Streamlit 1.36+)."""
    try:
        return st.columns(spec, vertical_alignment="bottom", **kwargs)
    except TypeError:
        return st.columns(spec, **kwargs)


QUICK_MODE = st.session_state.get("role") == "quick"
QUICK_SOURCE = _secret_value("QUICK_ADD_LEAD_SOURCE", "Vale")
QUICK_FROM = _secret_value("QUICK_ADD_FROM", "vh@sycomms.co.uk").strip().lower()  # Quick add logins always send as this


def register_vertical(base: str, crm: str) -> str:
    """A sector pitch that names the firm's own system, e.g. 'Dental Practices · Dentally'. Kept for the session."""
    key = f"{base} · {crm}"
    st.session_state.setdefault("custom_verticals", {})[key] = (base, crm)
    VERTICAL_PRESETS[key] = {**VERTICAL_PRESETS[base], "crms": [crm], "primary_hook": f"{crm} integration"}
    SECTOR_COPY[key] = SECTOR_COPY[base]
    return key


for _vk, (_vbase, _vcrm) in list(st.session_state.get("custom_verticals", {}).items()):
    if _vbase in VERTICAL_PRESETS:
        register_vertical(_vbase, _vcrm)

# ---------------- Sidebar ----------------
with st.sidebar:
    render_html(
        f'<div class="pe-brand"><div class="pe-logo">{icon("target", 22, 2.2)}</div>'
        f'<div><div class="n">{APP_NAME}</div><div class="s">{APP_TAGLINE}</div></div></div>'
    )
    # ---- Workspace switch (bookmarkable: ?view=calls) ----
    if QUICK_MODE:  # Telemarketer login: Quick add only
        st.session_state["view"] = "quick"
    else:
        if st.session_state.get("_goto_view"):  # A button elsewhere asked to switch page
            st.session_state["view"] = st.session_state["w_view"] = st.session_state.pop("_goto_view")
        if "view" not in st.session_state:
            st.session_state["view"] = st.query_params.get("view") if st.query_params.get("view") in (
                "customers", "caller", "callbacks", "pipeline", "local", "overview", "prospect", "activity") else "caller"
        _n_to_call = 0
        _views = {"caller": "📞  Caller", "callbacks": "🗓  Call-backs", "customers": "📇  Customers",
                  "pipeline": "💼  Pipeline", "overview": "📈  Overview", "local": "📍  Local hit list",
                  "prospect": "🎯  Prospecting", "activity": "✉️  Email activity"}
        if st.session_state["view"] not in _views:
            st.session_state["view"] = "caller"
        if st.session_state.get("w_view") not in _views:
            st.session_state["w_view"] = st.session_state["view"]
        st.session_state["view"] = st.radio(
            "Workspace", list(_views), key="w_view", label_visibility="collapsed", format_func=_views.get,
        )  # Labels stay fixed: a changing label would make Streamlit reset the switch
        if _n_to_call:
            render_html(f'<div style="font-size:.76rem;color:var(--muted);margin:-2px 0 6px 4px">'
                        f'{_n_to_call} {"firm" if _n_to_call == 1 else "firms"} waiting on the call list</div>')
        if st.query_params.get("view", "caller") != st.session_state["view"]:
            st.query_params["view"] = st.session_state["view"]
    if QUICK_MODE:  # Just what a telemarketer needs: Zoho sign-in, no settings
        ch_api_key = secret_ch_key
        zoho_err = load_zoho_meta() if ZOHO.configured else None
        st.session_state["zoho_auto"], st.session_state["zoho_no_email"] = True, False
        render_html(f'<div class="pe-status">Zoho CRM<span class="st {"ok" if zoho_on() and not zoho_err else "off"}">'
                    f'{"Connected" if zoho_on() and not zoho_err else "Not connected"}</span></div>')
        if zoho_err or not zoho_on():
            st.caption("⚠️ Zoho isn't connected, so leads can't be added or sent. Let Sam know.")
    else:
        render_html('<div class="pe-side-h">Connections</div>')
        if secret_ch_key:
            # Key stays server-side: never placed in a widget, so never sent to the browser.
            ch_api_key = secret_ch_key
        else:
            ch_api_key = st.text_input(
                "Companies House API key",
                type="password",
                help=(
                    "Not found in Secrets. Paste a key for this session, or add"
                    " COMPANIES_HOUSE_KEY to Streamlit Secrets."
                ),
            )
        ch_state = ('ok">Connected' if secret_ch_key else ('idle">Session key' if ch_api_key else 'off">No key'))
        render_html(
            f'<div class="pe-status">Companies House<span class="st {ch_state}</span></div>'
            '<div class="pe-status">Web discovery<span class="st ok">Ready</span></div>'
            '<div class="pe-status">PDF dossiers<span class="st ok">Ready</span></div>'
        )
        get_sent_log()
        if SENT_LOG.last_error or st.session_state.get("sent_log_error"):
            log_state = 'off">Error'
        elif SENT_LOG.backend == "github":
            log_state = 'ok">Saved to GitHub'
        else:
            log_state = 'idle">Temporary'
        render_html(f'<div class="pe-status">Sent log<span class="st {log_state}</span></div>')
        call_state = ('off">Error' if CALL_STORE.last_error else 'ok">Saved to GitHub' if CALL_STORE.backend == "github" else 'idle">Temporary')
        render_html(f'<div class="pe-status">Call list<span class="st {call_state}</span></div>')
        places_state = 'ok">Connected' if _secret_value("GOOGLE_PLACES_API_KEY") else 'idle">Not set up'
        render_html(f'<div class="pe-status">Google Maps lookup<span class="st {places_state}</span></div>')
        fca_state = 'ok">Connected' if _secret_value("FCA_API_KEY") and _secret_value("FCA_API_EMAIL") else 'idle">Add free key'
        sra_state = 'ok">Connected' if _secret_value("SRA_API_KEY") else 'idle">Add free key'
        render_html(
            '<div class="pe-status">OpenStreetMap<span class="st ok">Free · ready</span></div>'
            '<div class="pe-status">Email domain checks<span class="st ok">Free · ready</span></div>'
            '<div class="pe-status">Owners (Companies House)<span class="st ok">Free · ready</span></div>'
            f'<div class="pe-status">FCA register<span class="st {fca_state}</span></div>'
            f'<div class="pe-status">SRA register<span class="st {sra_state}</span></div>'
        )
        zoho_err = load_zoho_meta() if ZOHO.configured else None
        zoho_state = ('idle">Setup needed' if ZOHO.can_setup or (zoho_err and "invalid_code" in zoho_err)
                      else 'off">Error' if zoho_err else 'ok">Connected' if zoho_on() else 'idle">Not set up')
        render_html(f'<div class="pe-status">Zoho CRM<span class="st {zoho_state}</span></div>')
        needs_key = ZOHO.can_setup or st.session_state.get("zoho_needs_scope") or (
            zoho_err and ("invalid_code" in zoho_err or "permission" in zoho_err.lower()))
        if needs_key and not ZOHO.can_setup:
            st.caption("⚠️ The Zoho key in Secrets is from another app and is missing permissions. Get this app its own key below.")
        if ZOHO.client_id and ZOHO.client_secret:
            with st.expander("Connect Zoho" if needs_key else "Reconnect Zoho (new key)", expanded=bool(needs_key)):
                render_zoho_setup()
        if zoho_err and not needs_key:
            st.caption("⚠️ " + zoho_err)
        elif zoho_on():
            st.session_state["zoho_auto"] = st.toggle(
                "Add enriched firms to Zoho", value=st.session_state.get("zoho_auto", True), key="w_zoho_auto",
                help="Enriched firms with an email become Zoho Leads (checked for duplicates and existing customers first).")
            if st.session_state["zoho_auto"]:
                st.session_state["zoho_no_email"] = st.toggle(
                    "Also add firms with no email", value=st.session_state.get("zoho_no_email", False), key="w_zoho_no_email",
                    help="Off (recommended): firms without a findable email stay in this app's No email found list and"
                         " the call list, and only go into Zoho once an email turns up, which keeps Zoho free of leads"
                         " the other apps can't use. On: every enriched firm goes into Zoho, as before.")
            if not lead_source_ok():
                st.caption(f"⚠️ Add **{zoho_lead_source()}** as a Lead Source option in Zoho (Setup → Modules → Leads →"
                           " Lead Source). Until then, new leads are created without a Lead Source.")
        if SENT_LOG.last_error or st.session_state.get("sent_log_error"):
            st.caption("⚠️ " + (st.session_state.pop("sent_log_error", None) or SENT_LOG.last_error or ""))
        elif SENT_LOG.backend == "local":
            st.caption("Sent ticks reset when the app restarts. Add GITHUB_TOKEN & GITHUB_REPO to Secrets to keep them permanently.")
        if st.button("↻ Refresh shared data", **FULL_WIDTH, help="Pick up ticks made by colleagues since you opened the app."):
            st.session_state.pop("sent_log_data", None)
            st.session_state.pop("call_list_data", None)
            st.session_state.pop("contacts_data", None)
            for _k in ("zoho_store_data", "zoho_from", "pe_lead_fields"):
                st.session_state.pop(_k, None)
            st.session_state["call_ver"] = st.session_state.get("call_ver", 0) + 1
            st.session_state["sent_log_ver"] = st.session_state.get("sent_log_ver", 0) + 1
            bump_queue_editor()
            st.rerun()
    render_html('<div class="pe-side-h">This session</div>')
    sidebar_stats_slot = st.empty()
    render_html('<div class="pe-side-h">Your email signature</div>')
    with st.expander("Signature details", expanded=not st.session_state.get("sender_profile", {}).get("name")):
        def _secret(key: str, default: str) -> str:
            try:
                return str(st.secrets.get(key, default))
            except Exception:
                return default
        prof = st.session_state.setdefault("sender_profile", {
            "name": st.session_state.get("hub_user") or st.session_state.get("quick_user") or _secret("SENDER_NAME", ""),
            "title": _secret("SENDER_TITLE", SENDER_DEFAULTS["title"]),
            "phone": _secret("SENDER_PHONE", SENDER_DEFAULTS["phone"]),
            "email": _secret("SENDER_EMAIL", SENDER_DEFAULTS["email"]),
        })
        prof["name"] = st.text_input("Your name", value=prof.get("name", ""), placeholder="e.g. Sam",
                                     help=f"Leave blank to send as the company: \"Hi Mike, it's {SENDER_COMPANY} here.\"")
        if not get_sender().get("name"):
            st.caption(f"No name set: emails open \"It's {SENDER_COMPANY} here\" and are signed by the company.")
        prof["title"] = st.text_input("Job title", value=prof.get("title", ""))
        prof["phone"] = st.text_input("Direct phone", value=prof.get("phone", ""))
        prof["email"] = st.text_input("Your email", value=prof.get("email", ""))
        st.session_state["sender_profile"] = prof
    render_html('<div class="pe-side-h">Account</div>')
    if st.button("Log out", **FULL_WIDTH):
        st.session_state["password_correct"] = False
        for _k in ("role", "quick_user", "view"):
            st.session_state.pop(_k, None)
        st.rerun()

# ---------------- CALL LIST PAGE ----------------
CALL_CSS = """
<style>
.st-key-card-call-now, .st-key-card-call-list, .st-key-card-call-empty {
  background: linear-gradient(180deg, rgba(22, 31, 51, 0.85) 0%, rgba(17, 24, 39, 0.85) 100%);
  border: 1px solid var(--border) !important; border-radius: var(--radius); padding: 22px 22px 18px 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 40px -24px rgba(0,0,0,0.6); }
.st-key-card-call-now { border-color: rgba(253, 186, 116,.35) !important; }
.cl-kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 18px; }
@media (max-width: 1100px) { .cl-kpis { grid-template-columns: repeat(3, 1fr); } }
.cl-kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; border-top: 2px solid var(--c, var(--accent)); }
.cl-kpi .v { font-size: 1.45rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
.cl-kpi .l { font-size: 0.7rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: .07em; }
.cl-firm { font-size: 1.45rem; font-weight: 800; letter-spacing: -0.025em; color: var(--text); line-height: 1.2; }
.cl-legal { font-size: 0.78rem; color: var(--faint); margin-top: 2px; }
.cl-phone { display: flex; align-items: center; gap: 12px; margin: 14px 0 10px 0; padding: 14px 16px; border-radius: 14px;
  background: linear-gradient(135deg, rgba(253, 186, 116,.14), rgba(240, 100, 90,.10)); border: 1px solid rgba(253, 186, 116,.35); }
.cl-phone .ic { width: 40px; height: 40px; border-radius: 12px; background: var(--grad); color: #0A0E1A; display: grid; place-items: center; flex-shrink: 0; }
.cl-phone a { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.01em; color: var(--text) !important; text-decoration: none; }
.cl-phone .alt { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }
.cl-hist { margin-top: 6px; }
.cl-hist .row { display: flex; gap: 10px; font-size: 0.8rem; padding: 6px 0; border-top: 1px solid var(--border); color: var(--muted); }
.cl-hist .row b { color: var(--text); font-weight: 600; }
.cl-hist .row .when { color: var(--faint); white-space: nowrap; min-width: 88px; }
.cl-flash { margin-bottom: 12px; }
.st-key-card-call-now .stButton button { min-height: 44px; }
</style>
"""


def call_hero_html(to_call: int, due: int, interested: int) -> str:
    pills = [
        (str(to_call), "To call", "active"),
        (str(due), "Callbacks due", "done" if due == 0 else ""),
        (str(interested), "Interested", "done"),
    ]
    parts = [f'<div class="pe-step {cls}"><span class="num">{n}</span>{label}</div>' for n, label, cls in pills]
    return (
        '<div class="pe-hero"><div>'
        '<div class="pe-eyebrow"><span class="dot"></span>Shared call list · saved permanently</div>'
        '<div class="pe-title">Call list <span>&amp; dialler</span></div>'
        '<div class="pe-sub">Firms we couldn\'t email, ready to phone. Work top to bottom: every outcome is saved'
        ' for the whole team and shows as contacted in future searches.</div>'
        f'</div><div class="pe-stepper">{"<div class=pe-step-sep></div>".join(parts)}</div></div>'
    )


def log_call(cn: str, outcome: str, notes: str, callback_at: Optional[datetime]) -> None:
    calls = get_call_list()
    if cn not in calls:
        return
    caller = get_sender().get("name", "")
    r = dict(calls[cn])
    stamp = now_uk().isoformat(timespec="seconds")
    entry = {"at": stamp, "by": caller, "outcome": outcome, "note": (notes or "").strip()}
    r["history"] = list(r.get("history") or []) + [entry]
    r.update(status=outcome, notes=notes or "", attempts=int(r.get("attempts") or 0) + 1,
             last_called=stamp, last_called_by=caller,
             callback=callback_at.isoformat(timespec="minutes") if (outcome == "Call back" and callback_at) else "")
    save_calls({cn: r}, f"{r.get('firm', cn)} -> {outcome}")
    if outcome in CALL_DONE:  # Finished with: show as contacted in future prospecting searches
        record_sent({cn: {
            "company_name": r.get("legal_name", r.get("firm", "")), "to": "", "contact": r.get("contact", ""),
            "vertical": r.get("sector", ""), "subject": "", "sent_at": stamp, "sent_by": caller,
            "status": f"Called · {outcome}",
        }})
    st.session_state["call_current"] = None
    st.session_state["call_flash"] = f"{r.get('firm', 'Firm')} logged as {outcome}."


def render_call_page() -> None:
    st.markdown(CALL_CSS, unsafe_allow_html=True)
    calls = get_call_list()
    ver = st.session_state.get("call_ver", 0)
    order = call_queue(calls)
    caller = get_sender().get("name", "")
    today = now_uk().date().isoformat()
    status_counts = {s: sum(1 for r in calls.values() if r.get("status") == s) for s in CALL_STATUSES}
    due_now = sum(1 for cn in order if calls[cn].get("status") == "Call back")
    calls_today = sum(1 for r in calls.values() for h in (r.get("history") or []) if str(h.get("at", "")).startswith(today))

    render_html(
        '<div class="cl-kpis">'
        f'<div class="cl-kpi" style="--c:#FDBA74"><div class="l">To call now</div><div class="v">{len(order)}</div></div>'
        f'<div class="cl-kpi" style="--c:#FBBF24"><div class="l">Callbacks due</div><div class="v">{due_now}</div></div>'
        f'<div class="cl-kpi" style="--c:#F0645A"><div class="l">Calls today</div><div class="v">{calls_today}</div></div>'
        f'<div class="cl-kpi" style="--c:#34D399"><div class="l">Interested</div><div class="v">{status_counts["Interested"]}</div></div>'
        f'<div class="cl-kpi" style="--c:#5E6A82"><div class="l">On the list</div><div class="v">{len(calls)}</div></div>'
        "</div>"
    )
    if st.session_state.get("call_list_error"):
        st.error(st.session_state.pop("call_list_error"))

    if not calls:
        with st.container(key="card-call-empty"):
            render_html(
                f'<div class="pe-empty"><div style="color:var(--accent-2);display:inline-block;padding:18px;border-radius:20px;'
                f'background:rgba(253, 186, 116,.1);border:1px solid rgba(253, 186, 116,.3)">{icon("phone", 40, 1.6)}</div>'
                '<div class="t">The call list is empty</div>'
                '<div class="s">Firms we can phone but not email land here, saved for the whole team.</div>'
                "<ol><li>In Prospecting, enrich a batch of firms</li><li>Tick firms under <b>&nbsp;No email found</b></li>"
                "<li>Hit <b>&nbsp;Add to the call list</b></li></ol></div>"
            )
        return

    left, right = st.columns([1, 1.35], gap="large")

    # ===== Now calling =====
    with left:
        with st.container(key="card-call-now"):
            section_header("▶", "Now calling", f"{len(order)} in the queue · callbacks first, then new, then retries")
            if st.session_state.get("call_flash"):
                st.success(st.session_state.pop("call_flash"))
            if not caller:
                st.caption("💡 Add your name under **Your email signature** in the sidebar so calls are logged against you.")
            if not order:
                render_html('<div class="pe-hint">Queue clear. Every firm has an outcome or a callback booked for later.</div>')
            else:
                current = st.session_state.get("call_current")
                if current not in order:
                    current = order[0]
                pick = st.selectbox(
                    "Up next", order, index=order.index(current), key=f"call_pick_{ver}",
                    format_func=lambda c: f"{calls[c].get('firm', c)} · {calls[c].get('status', 'New')}"
                    + (f" · {fmt_when(calls[c].get('callback', ''))}" if calls[c].get("status") == "Call back" else ""),
                )
                st.session_state["call_current"] = pick
                r = calls[pick]
                cfg = VERTICAL_PRESETS.get(r.get("sector", ""), VERTICAL_PRESETS["Estate & Lettings Agents"])
                meta = [chip(r.get("status", "New"), CALL_STATUS_TONE.get(r.get("status", "New"), "")),
                        chip(r.get("sector", ""), "accent")]
                if r.get("attempts"):
                    meta.append(chip(f"{r['attempts']} previous call{'s' if r['attempts'] != 1 else ''}", "muted"))
                phone = r.get("phone", "")
                alt = " · ".join(r.get("other_phones") or [])
                site = r.get("website", "")
                directors = ", ".join(r.get("directors") or [])
                render_html(
                    f'<div class="cl-firm">{esc(r.get("firm", ""))}</div>'
                    f'<div class="cl-legal">{esc(r.get("legal_name", ""))} · #{esc(pick)}</div>'
                    f'<div class="pe-chips" style="margin-top:10px">{"".join(meta)}</div>'
                    f'<div class="cl-phone"><div class="ic">{icon("phone", 20, 2.2)}</div><div>'
                    f'<a href="tel:{esc(phone.replace(" ", ""))}">{esc(phone or "No number")}</a>'
                    + (f'<div class="alt">Also: {esc(alt)}</div>' if alt else "")
                    + "</div></div>"
                    '<div class="pe-panel"><div class="h">Ask for</div>'
                    f'<div class="pe-contact"><div class="pe-avatar">{esc(initials(r.get("contact", "?")))}</div>'
                    f'<div><div class="n">{esc(r.get("contact", ""))}</div><div class="r">{esc(r.get("role", ""))}'
                    + (f" · directors: {esc(directors)}" if directors else "")
                    + "</div></div></div>"
                    + (f'<div class="pe-row" style="margin-top:10px">{icon("globe", 15)}<a href="{esc(site)}" target="_blank">'
                       f'{esc(site.replace("https://", "").replace("http://", ""))}</a></div>' if site else "")
                    + (f'<div class="pe-row">{icon("pin", 15)}<span>{esc(r.get("address", ""))}</span></div>' if r.get("address") else "")
                    + "</div>"
                    f'<div class="pe-hook"><div class="h">Talking points</div><div class="t">{esc(cfg["primary_hook"])}</div>'
                    "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in cfg["pitch_bullets"][:3])
                    + "<li>BT's analogue lines switch off by January 2027, so now is the time to move</li></ul></div>"
                )
                li_q = f"{(r.get('directors') or [r.get('contact', '')])[0]} {r.get('firm', '')}"
                st.link_button("🔎  Find on LinkedIn", r.get("linkedin") or
                               "https://www.linkedin.com/search/results/people/?keywords=" + quote(li_q),
                               **FULL_WIDTH, help="Check who you're calling before you dial")
                hist = list(reversed(r.get("history") or []))[:3]
                if hist:
                    render_html(
                        '<div class="nl-lines-h" style="font-size:.7rem;font-weight:700;letter-spacing:.08em;'
                        'text-transform:uppercase;color:var(--faint);margin:10px 0 2px 0">Previous calls</div><div class="cl-hist">'
                        + "".join(
                            f'<div class="row"><span class="when">{esc(fmt_when(h.get("at", "")))}</span>'
                            f'<span><b>{esc(h.get("outcome", ""))}</b>{" · " + esc(h.get("by")) if h.get("by") else ""}'
                            f'{" · " + esc(h.get("note")) if h.get("note") else ""}</span></div>'
                            for h in hist)
                        + "</div>"
                    )
                notes = st.text_area("Call notes", value=r.get("notes", ""), key=f"call_note_{pick}_{ver}", height=90,
                                     placeholder="Who you spoke to, current provider, contract end date, number of users…")
                d1, d2 = st.columns(2)
                with d1:
                    cb_day = st.date_input("Call back on", value=now_uk().date() + timedelta(days=1),
                                           key=f"cb_day_{pick}_{ver}", format="DD/MM/YYYY")
                with d2:
                    slots = [dt_time(h, m) for h in range(8, 19) for m in (0, 30) if not (h == 18 and m == 30)]
                    cb_time = st.selectbox("at", slots, index=slots.index(dt_time(10, 0)), key=f"cb_time_{pick}_{ver}",
                                           format_func=lambda t: t.strftime("%H:%M"))
                outcome = None
                buttons = [
                    ("✅  Interested", "Interested", "primary", None),
                    ("📅  Call back", "Call back", "secondary", "Books the date & time above"),
                    ("📵  No answer", "No answer", "secondary", None),
                    ("✋  Not interested", "Not interested", "secondary", None),
                    ("⚠️  Wrong number", "Wrong number", "secondary", None),
                    ("🚫  Do not call", "Do not call", "secondary", "Never offered again. Use when someone asks not to be contacted."),
                ]
                for row_start in range(0, len(buttons), 2):
                    bcols = st.columns(2)
                    for bcol, (label, value, kind, tip) in zip(bcols, buttons[row_start:row_start + 2]):
                        with bcol:
                            if st.button(label, type=kind, key=f"o_{value.replace(' ', '_').lower()}_{pick}",
                                         help=tip, **FULL_WIDTH):
                                outcome = value
                if outcome:
                    log_call(pick, outcome, notes, datetime.combine(cb_day, cb_time) if outcome == "Call back" else None)
                    st.rerun()

    # ===== The whole list =====
    with right:
        with st.container(key="card-call-list"):
            section_header("≡", "The list", "Filter, tweak statuses or notes, then save. Shared with everyone using the app.")
            f1, f2, f3 = st.columns([1.3, 1.2, 1])
            with f1:
                show = st.multiselect("Status", CALL_STATUSES, default=CALL_OPEN, key="call_f_status")
            with f2:
                sectors = sorted({r.get("sector", "") for r in calls.values() if r.get("sector")})
                pick_sec = st.multiselect("Sector", sectors, default=[], key="call_f_sector", placeholder="All sectors")
            with f3:
                q = st.text_input("Search", key="call_f_q", placeholder="Firm, contact or phone").strip().lower()
            rows = []
            for cn, r in calls.items():
                if show and r.get("status", "New") not in show:
                    continue
                if pick_sec and r.get("sector") not in pick_sec:
                    continue
                hay = " ".join([r.get("firm", ""), r.get("contact", ""), r.get("phone", ""), r.get("legal_name", "")]).lower()
                if q and q not in hay:
                    continue
                rows.append({
                    "cn": cn, "Status": r.get("status", "New"), "Firm": r.get("firm", ""), "Contact": r.get("contact", ""),
                    "Phone": r.get("phone", ""), "Website": r.get("website", ""),
                    "Callback": fmt_when(r.get("callback", "")) if r.get("status") == "Call back" else "",
                    "Calls": int(r.get("attempts") or 0), "Last called": fmt_when(r.get("last_called", "")),
                    "Notes": r.get("notes", ""),
                })
            if not rows:
                st.caption("No firms match these filters.")
            else:
                df = pd.DataFrame(rows)
                kwargs = dict(
                    hide_index=True, num_rows="fixed", key=f"call_table_{ver}",
                    height=min(38 + 35 * len(df), 560),
                    column_order=["Status", "Firm", "Contact", "Phone", "Website", "Callback", "Calls", "Last called", "Notes"],
                    disabled=["Firm", "Contact", "Phone", "Website", "Callback", "Calls", "Last called"],
                    column_config={
                        "Status": st.column_config.SelectboxColumn("Status", options=CALL_STATUSES, required=True, width="small"),
                        "Firm": st.column_config.TextColumn("Firm", width="medium"),
                        "Contact": st.column_config.TextColumn("Contact", width="small"),
                        "Phone": st.column_config.TextColumn("Phone", width="small"),
                        "Website": st.column_config.LinkColumn("Website", width="small", display_text="Open ↗"),
                        "Callback": st.column_config.TextColumn("Callback", width="small"),
                        "Calls": st.column_config.NumberColumn("Calls", width="small"),
                        "Last called": st.column_config.TextColumn("Last called", width="small"),
                        "Notes": st.column_config.TextColumn("Notes (editable)", width="large"),
                    },
                )
                try:
                    edited = st.data_editor(df, width="stretch", **kwargs)
                except Exception:
                    edited = st.data_editor(df, use_container_width=True, **kwargs)
                changes: Dict[str, Dict[str, Any]] = {}
                for _, row in edited.iterrows():
                    orig = calls.get(row["cn"])
                    if not orig:
                        continue
                    if row["Status"] != orig.get("status", "New") or (row["Notes"] or "") != (orig.get("notes") or ""):
                        changes[row["cn"]] = {"status": row["Status"], "notes": row["Notes"] or ""}
                s1, s2 = st.columns([1.2, 1])
                with s1:
                    if st.button(f"💾  Save {len(changes)} change{'s' if len(changes) != 1 else ''}" if changes else "💾  No changes to save",
                                 type="primary", disabled=not changes, key="call_save", **FULL_WIDTH):
                        caller_now = get_sender().get("name", "")
                        stamp = now_uk().isoformat(timespec="seconds")
                        updates, handled = {}, {}
                        for cn, ch in changes.items():
                            r = dict(calls[cn])
                            if ch["status"] != r.get("status"):
                                r["history"] = list(r.get("history") or []) + [
                                    {"at": stamp, "by": caller_now, "outcome": f"Set to {ch['status']}", "note": ""}]
                                if ch["status"] in CALL_DONE:
                                    handled[cn] = {"company_name": r.get("legal_name", ""), "to": "", "contact": r.get("contact", ""),
                                                   "vertical": r.get("sector", ""), "subject": "", "sent_at": stamp,
                                                   "sent_by": caller_now, "status": f"Called · {ch['status']}"}
                            r.update(ch)
                            updates[cn] = r
                        save_calls(updates, f"{len(updates)} edited")
                        if handled:
                            record_sent(handled)
                        st.rerun()
                with s2:
                    export = pd.DataFrame([{
                        "Status": r.get("status", ""), "Firm": r.get("firm", ""), "Legal name": r.get("legal_name", ""),
                        "Company number": cn, "Contact": r.get("contact", ""), "Role": r.get("role", ""),
                        "Phone": r.get("phone", ""), "Other phones": "; ".join(r.get("other_phones") or []),
                        "Website": r.get("website", ""), "Sector": r.get("sector", ""), "Address": r.get("address", ""),
                        "Callback": r.get("callback", ""), "Calls": r.get("attempts", 0),
                        "Last called": r.get("last_called", ""), "Last called by": r.get("last_called_by", ""),
                        "Notes": r.get("notes", ""),
                    } for cn, r in calls.items()])
                    st.download_button("⬇  Export call list (.csv)", data=export.to_csv(index=False).encode("utf-8-sig"),
                                       file_name=f"{BRAND_FILE}_call_list_{now_uk().strftime('%Y-%m-%d')}.csv",
                                       mime="text/csv", key="call_export", **FULL_WIDTH)




# ==========================================
# ACTIVITY DASHBOARD (this app's emails and leads, read from its own saved log)
# ==========================================
ACT_CSS = """
<style>
.st-key-card-act-chart,.st-key-card-act-table,.st-key-card-act-empty{background:linear-gradient(180deg,rgba(22,31,51,.85) 0%,rgba(17,24,39,.85) 100%);border:1px solid var(--border)!important;border-radius:var(--radius);padding:22px 22px 18px;box-shadow:0 1px 0 rgba(255,255,255,.03) inset,0 20px 40px -24px rgba(0,0,0,.6);margin-bottom:18px}
.lo-kpis{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:14px;margin-bottom:18px}
@media (max-width:1000px){.lo-kpis{grid-template-columns:1fr}}
.lo-kpi{background:linear-gradient(180deg,rgba(22,31,51,.9) 0%,rgba(17,24,39,.9) 100%);border:1px solid var(--border);border-top:3px solid var(--c);border-radius:14px;padding:16px 18px 14px}
.lo-kpi .l{font-size:.95rem;font-weight:700;color:var(--text)}
.lo-kpi .row{display:flex;align-items:flex-end;gap:24px;margin-top:12px}
.lo-kpi .v{font-size:1.9rem;font-weight:800;letter-spacing:-.03em;color:var(--text);line-height:1}
.lo-kpi .v.big{font-size:2.3rem}
.lo-kpi .k{font-size:.72rem;color:var(--muted);margin-top:6px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.lo-kpi .foot{font-size:.78rem;color:var(--muted);margin-top:12px;padding-top:10px;border-top:1px solid var(--border)}
</style>
"""


def _act_when(value: Any) -> Optional[datetime]:
    try:
        d = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return None
    uk = ZoneInfo("Europe/London")
    return d.replace(tzinfo=uk) if d.tzinfo is None else d.astimezone(uk)


def _act_is_email(rec: Dict[str, Any]) -> bool:
    """A real email (sent from Zoho, or a draft ticked as sent). Not a call outcome or a 'handled, no email' tick."""
    if str(rec.get("status") or "").startswith("Called"):
        return False
    return bool(rec.get("to")) or rec.get("via") == "zoho"


def _act_how(rec: Dict[str, Any]) -> str:
    return "Sent from Zoho" if rec.get("via") == "zoho" else "Email draft / ticked"


def render_activity_page(title_html: str, colour: str, events: List[Dict[str, Any]],
                         tiles: List[Tuple[str, List[str], str]], email_acts: List[str]) -> None:
    """events: dicts with When, Activity, Firm, Contact, Email, Detail, By, How, Zoho.
    tiles: (label, activities counted, footnote)."""
    st.markdown(ACT_CSS, unsafe_allow_html=True)
    today = now_uk().date()
    df = pd.DataFrame(events, columns=["When", "Activity", "Firm", "Contact", "Email", "Detail", "By", "How", "Zoho"])
    if not df.empty:
        df = df.sort_values("When", ascending=False, na_position="last").reset_index(drop=True)
    days = df["When"].apply(lambda d: d.date() if d else None) if not df.empty else pd.Series(dtype=object)

    def n(acts: List[str], day=None) -> int:
        if df.empty:
            return 0
        m = df["Activity"].isin(acts)
        if day:
            m &= days == day
        return int(m.sum())

    week_start = today - timedelta(days=today.weekday())
    em_mask = df["Activity"].isin(email_acts) if not df.empty else pd.Series(dtype=bool)
    pills = [
        (n(email_acts, today), "Emails today", "active"),
        (int((em_mask & days.apply(lambda d: bool(d) and d >= week_start)).sum()) if not df.empty else 0, "This week", ""),
        (n(email_acts), "All time", ""),
    ]
    render_html(
        '<div class="pe-hero"><div>'
        '<div class="pe-eyebrow"><span class="dot"></span>Your activity · saved permanently</div>'
        f'<div class="pe-title">{title_html}</div>'
        '<div class="pe-sub">Every email and lead from this app, with a link straight to the record in Zoho.</div></div>'
        '<div class="pe-stepper">'
        + '<div class="pe-step-sep"></div>'.join(f'<div class="pe-step {c}"><span class="num">{v:,}</span>{esc(t)}</div>'
                                                 for v, t, c in pills)
        + "</div></div>",
        target=hero_slot,
    )
    render_html(
        f'<div class="lo-kpis" style="--n:{len(tiles)}">'
        + "".join(
            f'<div class="lo-kpi" style="--c:{colour}"><div class="l">{esc(label)}</div>'
            f'<div class="row"><div><div class="v big">{n(acts, today):,}</div><div class="k">Today</div></div>'
            f'<div><div class="v">{n(acts):,}</div><div class="k">Total</div></div></div>'
            f'<div class="foot">{esc(foot)}</div></div>'
            for label, acts, foot in tiles)
        + "</div>"
    )
    if df.empty:
        with st.container(key="card-act-empty"):
            render_html(
                '<div class="pe-empty"><div class="t">Nothing sent yet</div>'
                '<div class="s">Emails and new Zoho leads appear here as soon as you send them.</div></div>')
        return

    # ---- Emails per day (last 14 days) ----
    with st.container(key="card-act-chart"):
        section_header("01", "Emails per day", "Last 14 days. Hover a bar for the number.")
        start = today - timedelta(days=13)
        em = df[em_mask].copy()
        days = [d.date() for d in em["When"] if d is not None and pd.notna(d)] if len(em) else []
        counts = pd.Series([d for d in days if d and d >= start], dtype=object).value_counts()
        daily = pd.DataFrame({"Day": [start + timedelta(days=i) for i in range(14)]})
        daily["Emails"] = daily["Day"].map(counts).fillna(0).astype(int)
        daily["Label"] = pd.to_datetime(daily["Day"]).dt.strftime("%a %d")
        try:
            import altair as alt
            chart = (
                alt.Chart(daily).mark_bar(color=colour, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=26)
                .encode(
                    x=alt.X("Label:N", sort=list(daily["Label"]), title=None,
                            axis=alt.Axis(labelAngle=0, labelColor="#8C98B0", domainColor="#2A3550", ticks=False)),
                    y=alt.Y("Emails:Q", title=None,
                            axis=alt.Axis(labelColor="#8C98B0", gridColor="#1F2A40", domain=False, ticks=False, tickMinStep=1)),
                    tooltip=[alt.Tooltip("Label:N", title="Day"), alt.Tooltip("Emails:Q")],
                )
                .properties(height=220, background="transparent").configure_view(strokeWidth=0)
            )
            try:
                st.altair_chart(chart, width="stretch")
            except Exception:
                st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.bar_chart(daily.set_index("Label")["Emails"], color=colour)

    # ---- The table ----
    with st.container(key="card-act-table"):
        section_header("02", "All activity", "Newest first. Click Open to go to the record in Zoho.")
        f1, f2, f3 = st.columns([1, 1.3, 1.6])
        with f1:
            period = st.selectbox("Period", ["Today", "Last 7 days", "Last 30 days", "This month", "All time"],
                                  index=4, key="act_period")
        with f2:
            pick = st.multiselect("Activity", sorted(df["Activity"].unique()), default=[], placeholder="All activity",
                                  key="act_kinds")
        with f3:
            q = st.text_input("Search", placeholder="Firm, contact, email or subject", key="act_q").strip().lower()
        view = df.copy()
        vdays = days.copy()
        if period == "Today":
            keep = vdays == today
        elif period == "Last 7 days":
            keep = vdays.apply(lambda d: bool(d) and d >= today - timedelta(days=6))
        elif period == "Last 30 days":
            keep = vdays.apply(lambda d: bool(d) and d >= today - timedelta(days=29))
        elif period == "This month":
            keep = vdays.apply(lambda d: bool(d) and d.year == today.year and d.month == today.month)
        else:
            keep = pd.Series(True, index=view.index)
        view = view[keep]
        if pick:
            view = view[view["Activity"].isin(pick)]
        if q:
            hay = (view["Firm"].astype(str) + " " + view["Contact"].astype(str) + " " + view["Email"].astype(str)
                   + " " + view["Detail"].astype(str) + " " + view["By"].astype(str)).str.lower()
            view = view[hay.str.contains(q, regex=False)]
        st.caption(f"Showing {len(view):,} of {len(df):,}.")
        show = view.copy()
        show["When"] = show["When"].apply(
            lambda d: "" if not d else d.strftime("Today %H:%M") if d.date() == today
            else d.strftime("%a %d %b %H:%M") if d.year == today.year else d.strftime("%d %b %Y"))
        kwargs = dict(
            hide_index=True, height=min(38 + 35 * max(len(show), 1), 600),
            column_order=["When", "Activity", "Firm", "Contact", "Email", "Detail", "By", "How", "Zoho"],
            column_config={
                "When": st.column_config.TextColumn("When", width=128),
                "Activity": st.column_config.TextColumn("Activity", width=125),
                "Firm": st.column_config.TextColumn("Firm / customer", width="medium"),
                "Contact": st.column_config.TextColumn("Contact", width="small"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Detail": st.column_config.TextColumn("Subject / detail", width="large"),
                "By": st.column_config.TextColumn("By", width="small"),
                "How": st.column_config.TextColumn("How", width=150),
                "Zoho": st.column_config.LinkColumn("Zoho", width="small", display_text="Open ↗"),
            },
        )
        try:
            st.dataframe(show, width="stretch", **kwargs)
        except Exception:
            st.dataframe(show, use_container_width=True, **kwargs)
        export = view.copy()
        export["When"] = export["When"].apply(lambda d: d.strftime("%Y-%m-%d %H:%M") if d else "")
        d1, _ = st.columns([1, 3])
        with d1:
            st.download_button("⬇  Download these rows (.csv)", data=export.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"{APP_NAME.replace(' ', '_')}_activity_{today.isoformat()}.csv",
                               mime="text/csv", key="act_export", **FULL_WIDTH)
    if not st.session_state.get("zoho_org_domain"):
        st.caption("💡 Zoho links open in your default organisation. Connect Zoho in this session to make them exact.")


def build_pe_activity() -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    zs = get_zoho_store()
    for cn, r in zs.items():
        if isinstance(r, dict) and r.get("status") == "created":
            events.append({"When": _act_when(r.get("at")), "Activity": "Added to Zoho", "Firm": r.get("firm") or cn,
                           "Contact": "", "Email": "", "Detail": "New lead created", "By": r.get("by") or "",
                           "How": "Zoho", "Zoho": ZOHO.record_url(r["id"], "Leads") if r.get("id") else ""})
    for cn, r in get_sent_log().items():
        if not isinstance(r, dict):
            continue
        z = zs.get(cn) or {}
        link = ZOHO.record_url(z["id"], "Accounts" if z.get("status") == "customer" else "Leads") if z.get("id") else ""
        status = str(r.get("status") or "")
        if status.startswith("Called"):
            events.append({"When": _act_when(r.get("sent_at")), "Activity": "Call logged", "Firm": r.get("company_name") or cn,
                           "Contact": r.get("contact") or "", "Email": "", "Detail": status.replace("Called · ", "Outcome: "),
                           "By": r.get("sent_by") or "", "How": "Call list", "Zoho": link})
        elif _act_is_email(r):
            events.append({"When": _act_when(r.get("sent_at")), "Activity": "Emailed", "Firm": r.get("company_name") or cn,
                           "Contact": r.get("contact") or "", "Email": r.get("to") or "",
                           "Detail": r.get("subject") or r.get("vertical") or "", "By": r.get("sent_by") or "",
                           "How": _act_how(r), "Zoho": link})
    return events


if st.session_state.get("view") == "activity":
    render_activity_page(
        "Prospect Engine <span>activity</span>", "#3987e5", build_pe_activity(),
        [("New prospects added to Zoho", ["Added to Zoho"], "New leads only. Firms already in Zoho aren't counted."),
         ("New prospects emailed", ["Emailed"], "Pitch emails, sent from Zoho or ticked as emailed"),
         ("Calls logged", ["Call logged"], "Finished calls from the call list")],
        ["Emailed"],
    )
    render_html(
        '<div class="pe-stats">'
        f'<div class="pe-stat"><div class="v">{sum(1 for r in get_zoho_store().values() if r.get("status") == "created")}</div><div class="l">New leads</div></div>'
        f'<div class="pe-stat"><div class="v">{len(get_sent_log())}</div><div class="l">Handled</div></div>'
        f'<div class="pe-stat"><div class="v">{len(call_queue(get_call_list()))}</div><div class="l">To call</div></div>'
        "</div>",
        target=sidebar_stats_slot,
    )
    st.stop()

if st.session_state.get("view") == "survey" and not QUICK_MODE:
    render_survey_page()
    render_html(
        '<div class="pe-stats">'
        f'<div class="pe-stat"><div class="v">{sum(1 for r in get_sent_log().values() if r.get("survey_sent_at"))}</div><div class="l">Surveys sent</div></div>'
        f'<div class="pe-stat"><div class="v">{len(get_sent_log())}</div><div class="l">Handled</div></div>'
        f'<div class="pe-stat"><div class="v">{len(call_queue(get_call_list()))}</div><div class="l">To call</div></div>'
        "</div>",
        target=sidebar_stats_slot,
    )
    st.stop()

if st.session_state.get("view") == "calls":
    render_call_page()
    _calls = get_call_list()
    _order = call_queue(_calls)
    render_html(call_hero_html(len(_order), sum(1 for c in _order if _calls[c].get("status") == "Call back"),
                               sum(1 for r in _calls.values() if r.get("status") == "Interested")), target=hero_slot)
    render_html(
        '<div class="pe-stats">'
        f'<div class="pe-stat"><div class="v">{len(_calls)}</div><div class="l">On list</div></div>'
        f'<div class="pe-stat"><div class="v">{len(_order)}</div><div class="l">To call</div></div>'
        f'<div class="pe-stat"><div class="v">{len(get_sent_log())}</div><div class="l">Handled</div></div>'
        "</div>",
        target=sidebar_stats_slot,
    )
    st.stop()



# ---------------- QUICK ADD (telemarketers' own data) ----------------
QUICK_FREE_MAIL = {"gmail.com", "googlemail.com", "hotmail.com", "hotmail.co.uk", "outlook.com", "live.co.uk",
                   "live.com", "yahoo.com", "yahoo.co.uk", "btinternet.com", "btconnect.com", "icloud.com", "me.com",
                   "aol.com", "sky.com", "virginmedia.com", "talktalk.net"}
QUICK_AUTO, QUICK_OTHER = "Automatic", "Other (type it in)"
QUICK_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,24}$")
QUICK_COLUMNS = {  # CSV headings we recognise (any case)
    "sector": ("sector", "industry", "industry sector", "vertical", "type"),
    "name": ("name", "contact", "contact name", "full name", "first name"),
    "email": ("email", "email address", "e-mail"),
    "company": ("company", "company name", "business", "business name", "firm", "organisation", "organization"),
    "phone": ("phone", "telephone", "tel", "phone number", "mobile"),
    "crm": ("crm", "system", "software", "crm / system"),
}


def quick_hero_html() -> str:
    return (
        '<div class="pe-hero"><div>'
        '<div class="pe-eyebrow"><span class="dot"></span>Your own leads · logged in Zoho</div>'
        '<div class="pe-title">Quick <span>add &amp; send</span></div>'
        '<div class="pe-sub">Add a lead (or upload your list), and it goes into Zoho with a tailored email and'
        ' one-page PDF, ready to send from Zoho in one click. Opens and clicks are tracked.</div></div>'
        '<div class="pe-stepper"><div class="pe-step active"><span class="num">1</span>Add</div>'
        '<div class="pe-step-sep"></div><div class="pe-step"><span class="num">2</span>Check</div>'
        '<div class="pe-step-sep"></div><div class="pe-step"><span class="num">3</span>Send</div></div></div>'
    )


def _company_from_email(email: str) -> str:
    dom = email.split("@")[-1].lower() if "@" in email else ""
    if not dom or dom in QUICK_FREE_MAIL:
        return ""
    return " ".join(w.capitalize() for w in re.split(r"[-_]", dom.split(".")[0]) if w)


def match_sector(text: str) -> Optional[str]:
    """'dentist', 'Dental Practices' or 'solicitors' -> the sector pitch name."""
    t = (text or "").strip().lower()
    if not t:
        return None
    for k in VERTICAL_PRESETS:
        if " · " not in k and k.lower() == t:
            return k
    for k, rules in SECTOR_PLACE_RULES.items():
        if k in VERTICAL_PRESETS and (t in k.lower() or any(w in t for w in rules.get("words", ()) if len(w) >= 4)):
            return k
    return None


def quick_add(rows: List[Dict[str, str]], default_sector: Optional[str]) -> Tuple[List[str], List[str]]:
    """Adds each row to the review queue (and Zoho). Returns (keys added, problems)."""
    added, problems = [], []
    who = get_sender().get("name") or st.session_state.get("quick_user") or ""
    queue = st.session_state.setdefault("queue", {})
    for i, r in enumerate(rows, start=1):
        email = (r.get("email") or "").strip().lower()
        label = r.get("company") or email or f"Row {i}"
        if not QUICK_EMAIL_RE.match(email):
            problems.append(f"{label}: the email address doesn't look right")
            continue
        sector = match_sector(r.get("sector", "")) or default_sector
        if not sector:
            problems.append(f"{label}: no sector (pick a default sector for the list)")
            continue
        company = (r.get("company") or "").strip() or _company_from_email(email)
        if not company:
            problems.append(f"{label}: add the company name (it's a personal email address)")
            continue
        crm = (r.get("crm") or "").strip()
        vertical = register_vertical(sector, crm) if crm and crm.lower() not in ("automatic", "auto", "unknown") else sector
        cn = "qa:" + email
        lead = ScrapedLead(company_name=company, trading_name=company, emails_found=[email], contact_email=email,
                           contact_name=(r.get("name") or "").strip() or None, sector_guess=sector,
                           phones_found=[p for p in [normalise_uk_phone(r.get("phone") or "") or (r.get("phone") or "").strip()] if p])
        add_to_queue(lead, vertical, cn=cn)
        queue[cn].update({"base_vertical": sector, "lead_source": QUICK_SOURCE, "added_by": who})
        added.append(cn)
    if added:
        st.session_state["current_cn"] = st.session_state["current_cn_select"] = added[-1]
    if added and zoho_on():
        summary = push_to_zoho_leads(added)
        st.session_state["quick_zoho_msg"] = zoho_summary_text(summary)
        if summary["error"]:
            problems += ["Zoho: " + e for e in summary["error"][:5]]
    return added, problems


def render_quick_add() -> None:
    with st.container(key="card-left"):
        section_header("01", "Add your leads", "One at a time, or upload your list. Each goes into Zoho, checked"
                       " for duplicates and existing customers first.")
        if zoho_on() and QUICK_SOURCE not in ZOHO.picklist(st.session_state.get("pe_lead_fields") or {}, "Lead_Source"):
            st.caption(f"ℹ️ Add **{QUICK_SOURCE}** as a Lead Source option in Zoho (Setup → Modules → Leads → Lead"
                       " Source) to label these leads. Until then they use the usual Prospect Engine source.")
        tab1, tab2 = st.tabs(["➕  One lead", "📄  Upload a list (CSV)"])
        sectors = sorted([k for k in VERTICAL_PRESETS if " · " not in k], key=str.lower)
        v = st.session_state.get("qa_ver", 0)
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                sector = st.selectbox("Industry sector", sectors, index=None, placeholder="Pick a sector", key=f"qa_sector_{v}")
                name = st.text_input("Contact name", key=f"qa_name_{v}", placeholder="e.g. Sarah Jones")
                phone = st.text_input("Phone (optional)", key=f"qa_phone_{v}", placeholder="e.g. 01743 123456")
            with c2:
                email = st.text_input("Email", key=f"qa_email_{v}", placeholder="e.g. sarah@smithlaw.co.uk").strip()
                company = st.text_input("Company name", key=f"qa_company_{v}",
                                        placeholder=_company_from_email(email) or "e.g. Smith Law",
                                        help="Left blank, it's taken from the email address.")
                crm = ""
                if sector:
                    typical = VERTICAL_PRESETS[sector]["crms"]
                    pick = st.selectbox("Their CRM / system", [QUICK_AUTO] + typical + [QUICK_OTHER], key=f"qa_crm_{v}",
                                        format_func=lambda x: f"Automatic: {', '.join(typical[:3])}" if x == QUICK_AUTO else x,
                                        help="Automatic names the systems most firms in this sector use. If you know"
                                             " theirs, pick or type it and the email and PDF talk about that one.")
                    if pick == QUICK_OTHER:
                        crm = st.text_input("System name", key=f"qa_crm_other_{v}", placeholder="e.g. Practice Evolve").strip()
                    elif pick != QUICK_AUTO:
                        crm = pick
            if st.button("➕  Add this lead", type="primary", key="qa_add", **FULL_WIDTH,
                         disabled=not (sector and email)):
                added, problems = quick_add([{"sector": sector or "", "name": name, "email": email, "company": company,
                                              "phone": phone, "crm": crm}], sector)
                st.session_state["qa_msg"] = (added, problems)
                if added:
                    st.session_state["qa_ver"] = v + 1  # Fresh, empty form for the next lead
                st.rerun()
        with tab2:
            st.caption("A CSV with a row per lead. Headings it understands: Sector, Name, Email, Company, Phone, CRM."
                       " Only Email is required; rows without a sector use the default below.")
            tmpl = "Sector,Name,Email,Company,Phone,CRM\nDental Practices,Sarah Jones,sarah@example.co.uk,Example Dental,01743 123456,\n"
            st.download_button("⬇  Template (.csv)", data=tmpl.encode("utf-8"), file_name="quick_add_template.csv",
                               mime="text/csv")
            up = st.file_uploader("Your list", type=["csv"], key=f"qa_file_{v}")
            default_sector = st.selectbox("Default sector (for rows without one)", sectors, index=None,
                                          placeholder="Pick a sector", key=f"qa_default_{v}")
            rows: List[Dict[str, str]] = []
            if up is not None:
                try:
                    df = pd.read_csv(up, dtype=str, keep_default_na=False, encoding_errors="replace")
                except Exception as exc:
                    st.error(f"Couldn't read that file ({exc.__class__.__name__}). Save it from Excel as CSV and try again.")
                    df = pd.DataFrame()
                cols = {c: next((k for k, names in QUICK_COLUMNS.items() if c.strip().lower() in names), None) for c in df.columns}
                if not df.empty and "email" not in cols.values():
                    st.error("No Email column found. Name one column Email.")
                else:
                    for _, row in df.iterrows():
                        rec = {k: "" for k in QUICK_COLUMNS}
                        for c, k in cols.items():
                            if k and not rec[k]:
                                rec[k] = str(row[c]).strip()
                        if rec["email"]:
                            rows.append(rec)
                    st.caption(f"{len(rows):,} {'lead' if len(rows) == 1 else 'leads'} with an email in this file.")
            if st.button(f"➕  Add {len(rows):,} leads" if rows else "➕  Add the list", type="primary", key="qa_add_csv",
                         disabled=not rows, **FULL_WIDTH):
                added, problems = quick_add(rows, default_sector)
                st.session_state["qa_msg"] = (added, problems)
                if added:
                    st.session_state["qa_ver"] = v + 1
                st.rerun()
        msg = st.session_state.pop("qa_msg", None)
        if msg:
            added, problems = msg
            log_now = get_sent_log()
            again = [c for c in added if c in log_now]
            if added:
                st.success(f"Added {len(added)} {'lead' if len(added) == 1 else 'leads'}. Check the email below, then"
                           " send from Zoho." + (f" {st.session_state.pop('quick_zoho_msg', '') or ''}"))
            if again:
                st.warning(f"{len(again)} of these {'has' if len(again) == 1 else 'have'} already been emailed from this"
                           " app, so they're under Handled and won't be sent again.")
            for p_ in problems[:8]:
                st.caption("⚠️ " + p_)
        if not st.session_state.get("queue"):
            st.caption("Your leads appear below once added, with the email ready to check and send.")




# ==========================================================================================
# SALES HUB (South Wales Telecoms): the customer list is the CRM.
#   📇 Customers   upload / edit / enrich / download the list (it's the data source)
#   📞 Caller      one record at a time, one-click outcomes, next action dates, appointments
#   📍 Local       fill the diary: who else is near an appointment, from the list and Companies House
#   📈 Overview    management view: pipeline, calls, appointments, won deals and revenue
# ==========================================================================================
import uuid as _uuid

CRM_STORE = ShardedStore(legacy=SentLog("GITHUB_CRM_PATH", "customers.json", ".sales_hub_customers.json", compact=True))
PIPELINE = ["New", "No answer", "Call back", "Appointment", "Quoted", "Won", "Installed", "Lost", "Not interested",
            "Do not call", "Bad number"]
CLOSED = {"Won", "Installed", "Lost", "Not interested", "Do not call", "Bad number"}
STATUS_TONE = {"New": "accent", "No answer": "", "Call back": "warn", "Appointment": "good", "Quoted": "good",
               "Won": "good", "Installed": "good", "Lost": "muted", "Not interested": "muted", "Do not call": "risk",
               "Bad number": "risk"}
APPT_RESULTS = ["", "Sat – sold", "Sat – quoted / thinking", "Sat – not sold", "No show", "Cancelled"]
SOLD = {"Won", "Installed"}
CRM_FIELDS = [("company", "Company"), ("contact", "Contact name"), ("role", "Job title"), ("phone", "Phone"),
              ("mobile", "Mobile"), ("email", "Email"), ("website", "Website"), ("address", "Address"),
              ("town", "Town"), ("postcode", "Postcode"), ("sector", "Sector"), ("notes", "Notes")]
DEAL_TERMS = [12, 24, 36, 48, 60]
ALL_SECTORS = "All our sectors"
IMPORT_ALIASES: Dict[str, Tuple[str, ...]] = {
    "hub_id": ("hub id", "sales hub id", "record id", "crm id"),
    "company": ("company", "company name", "business", "business name", "organisation", "organization", "account",
                "account name", "customer", "customer name", "trading name", "firm"),
    "contact": ("contact", "contact name", "name", "full name", "decision maker", "owner", "main contact"),
    "first_name": ("first name", "forename", "firstname"),
    "last_name": ("last name", "surname", "lastname"),
    "role": ("title", "job title", "position", "role", "designation"),
    "phone": ("phone", "telephone", "tel", "phone number", "landline", "main number", "telephone number"),
    "mobile": ("mobile", "mobile number", "cell", "mobile phone"),
    "email": ("email", "email address", "e-mail", "e mail"),
    "website": ("website", "web", "url", "site", "web address", "domain"),
    "address": ("address", "address 1", "address line 1", "street", "address1", "street address"),
    "town": ("town", "city", "locality", "town/city"),
    "postcode": ("postcode", "post code", "zip", "postal code", "zip code"),
    "sector": ("sector", "industry", "category", "business type", "type of business"),
    "notes": ("notes", "comments", "note", "comment"),
    "status": ("status", "lead status", "stage", "pipeline stage"),
    "next_action": ("next action", "next action date", "call back", "callback", "callback date", "follow up",
                    "follow-up date", "next call"),
    "mrr": ("monthly value", "monthly", "mrr", "monthly recurring", "monthly (£)", "monthly value (£)"),
    "one_off": ("one-off", "one off", "one-off (£)", "upfront", "install", "one-off value (£)"),
    "term": ("term", "contract term", "term (months)", "months", "contract term (months)"),
    "won_at": ("won on", "won date", "date won"),
    "next_note": ("next action note", "next step"),
    "owner": ("owner", "account owner", "assigned to", "rep"),
    "company_number": ("company number", "company no", "companies house number", "crn"),
    "handsets": ("handsets", "number of handsets", "no of handsets", "handset count", "extensions"),
    "provider": ("current provider", "provider", "telecoms provider", "current supplier"),
    "contract_end": ("contract end", "contract end date", "contract ends", "contract expiry"),
    "next_time": ("next action time", "call back time", "callback time"),
}
# Columns our own download adds: ignored when that sheet comes back in (they're worked out live)
EXPORT_ONLY_COLS = {"last call", "last outcome", "calls", "next appointment", "total contract value (£)", "emailed",
                    "other emails", "source", "added", "credit band", "company status", "tps", "tps consent", "line type",
                    "region", "county", "sic", "sic description", "lease asset", "lease market", "lease rental (£)",
                    "rental frequency", "lease end", "lease supplier", "tags", "install date", "sold by", "staff",
                    "credit rating", "head office phone"}
IMPORT_LABELS = {"hub_id": "Hub ID (from a previous download)", "first_name": "First name", "last_name": "Last name",
                 "status": "Status", "next_action": "Next action date", "mrr": "Monthly value (£)",
                 "one_off": "One-off value (£)", "term": "Contract term (months)", "won_at": "Won on",
                 "next_note": "Next action note", "owner": "Owner", "company_number": "Company number",
                 "handsets": "Handsets", "provider": "Current provider", "contract_end": "Contract end",
                 "next_time": "Next action time",
                 **dict(CRM_FIELDS)}

SH_CSS = """
<style>
div[class*="st-key-card-sh"] { background: linear-gradient(180deg, rgba(22,31,51,.85) 0%, rgba(17,24,39,.85) 100%);
  border: 1px solid var(--border) !important; border-radius: var(--radius); padding: 22px 22px 18px 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,.03) inset, 0 20px 40px -24px rgba(0,0,0,.6); margin-bottom: 18px; }
.st-key-card-sh-now { border-color: rgba(240,100,90,.4) !important; }
.st-key-card-sh-now .stButton button { min-height: 46px; font-weight: 700; }
.sh-kpis { display: grid; grid-template-columns: repeat(var(--n, 4), minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
@media (max-width: 1100px) { .sh-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.sh-kpi { background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--c, var(--accent));
  border-radius: 12px; padding: 14px 16px; }
.sh-kpi .v { font-size: 1.6rem; font-weight: 800; letter-spacing: -.02em; color: var(--text); line-height: 1.1; }
.sh-kpi .l { font-size: .72rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: .06em; margin-top: 6px; }
.sh-kpi .f { font-size: .76rem; color: var(--faint); margin-top: 6px; }
.sh-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 4px 0; }
.sh-line { font-size: .86rem; color: var(--muted); margin: 3px 0; }
.sh-line b { color: var(--text); font-weight: 600; }
.sh-line a { color: var(--accent-2) !important; }
.sh-flash { background: rgba(52,211,153,.10); border: 1px solid rgba(52,211,153,.35); border-radius: 12px;
  padding: 10px 14px; color: var(--text); font-size: .9rem; margin-bottom: 12px; }
.sh-section { font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--faint);
  margin: 14px 0 6px 0; }
</style>
"""


# ---------------- Storage ----------------
def crm_get() -> Dict[str, Any]:
    ss = st.session_state
    # Re-checked every 45s (one cheap GitHub call; only files a colleague changed are downloaded again)
    stale = time.time() - ss.get("crm_loaded_at", 0) > 45
    if "crm_data" not in ss or ss.get("crm_data_epoch") != _log_epoch() or (stale and not ss.get("crm_hold")):
        fresh = CRM_STORE.load()
        if CRM_STORE.last_error:
            ss["crm_load_failed"] = True
            if ss.get("crm_data"):  # Keep what we had rather than showing an empty list
                ss["crm_loaded_at"] = time.time()
                ss["crm_error"] = CRM_STORE.last_error + " Showing the list as it was a moment ago."
                return ss["crm_data"]
        else:
            ss.pop("crm_load_failed", None)
        sig = (len(fresh), max((str(r.get("updated_at") or "") for r in fresh.values() if isinstance(r, dict)), default=""))
        if "crm_data" in ss and sig != ss.get("crm_sig"):
            ss["crm_ver"] = ss.get("crm_ver", 0) + 1  # A colleague changed something: redraw tables from the new list
        ss["crm_data"], ss["crm_sig"] = fresh, sig
        ss["crm_data_epoch"] = _log_epoch()
        ss["crm_loaded_at"] = time.time()
        if CRM_STORE.last_error:
            ss["crm_error"] = CRM_STORE.last_error
    return ss["crm_data"]


def crm_save(changes: Dict[str, Optional[Dict[str, Any]]], message: str, progress: Optional[Any] = None) -> None:
    """Saves records (None deletes). Re-reads first, so two people working at once don't overwrite each other."""
    ss = st.session_state
    stamp = now_uk().isoformat(timespec="seconds")
    for rec in changes.values():
        if rec is not None:
            rec["updated_at"] = stamp
    try:
        ss["crm_data"] = CRM_STORE.apply(changes, f"Sales Hub: {message}", progress=progress)
        ss["crm_loaded_at"] = time.time()
        ss["crm_sig"] = (len(ss["crm_data"]), max((str(r.get("updated_at") or "") for r in ss["crm_data"].values()
                                                   if isinstance(r, dict)), default=""))
    except Exception as exc:
        data = dict(ss.get("crm_data") or {})
        for k, v in changes.items():
            if v is None:
                data.pop(k, None)
            else:
                data[k] = v
        ss["crm_data"] = data
        ss["crm_error"] = (str(exc) if isinstance(exc, RuntimeError) else "Couldn't save to GitHub.") + \
            " Changes are kept for this session only."
    ss["crm_ver"] = ss.get("crm_ver", 0) + 1


def crm_user() -> str:
    return (get_sender().get("name") or st.session_state.get("sender_profile", {}).get("name") or "").strip()


def new_id() -> str:
    return "c" + _uuid.uuid4().hex[:10]


# ---------------- Small helpers ----------------
def _n(text: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def norm_company(name: str) -> str:
    words = [w for w in re.sub(r"[^\w ]", " ", (name or "").lower()).split()
             if w.upper() not in LEGAL_SUFFIX_WORDS and w not in ("the", "and")]
    return "".join(words)


def norm_phone(p: str) -> str:
    d = re.sub(r"\D", "", p or "")
    if d.startswith("44"):
        d = "0" + d[2:]
    return d if len(d) >= 10 else ""


def norm_pc(pc: str) -> str:
    return re.sub(r"\s", "", (pc or "").upper())


def pc_district(pc: str) -> str:
    """'CF10 1AA' -> 'CF10' (works for a district on its own too)."""
    m = re.match(r"^([A-Z]{1,2}\d[A-Z\d]?)", norm_pc(pc)[:-3] if len(norm_pc(pc)) >= 5 else norm_pc(pc))
    return m.group(1) if m else ""


def pc_area(pc: str) -> str:
    m = re.match(r"^([A-Z]{1,2})", norm_pc(pc))
    return m.group(1) if m else ""


def to_date(v: Any) -> Optional[date]:
    if not v:
        return None
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, datetime):
        return v.date()
    s_ = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s_[:10] if fmt.startswith("%Y") else s_, fmt).date()
        except ValueError:
            continue
    try:
        return pd.to_datetime(s_, dayfirst=True).date()
    except Exception:
        return None


def to_num(v: Any) -> float:
    try:
        return float(re.sub(r"[^\d.\-]", "", str(v))) if str(v).strip() not in ("", "nan", "None") else 0.0
    except ValueError:
        return 0.0


def money(v: float) -> str:
    if not v:
        return "£0"
    return f"£{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"£{v:,.2f}"


def next_working_day(d: date, n: int = 1) -> date:
    out = d
    while n > 0:
        out += timedelta(days=1)
        if out.weekday() < 5:
            n -= 1
    return out


def calls_of(rec: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [c for c in (rec.get("calls") or []) if isinstance(c, dict)]


def last_call(rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    cs = [c for c in calls_of(rec) if c.get("outcome") not in ("Note", "Edited")]
    return max(cs, key=lambda c: c.get("at", "")) if cs else None


def next_appt(rec: Dict[str, Any], from_dt: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    from_dt = from_dt or (now_uk() - timedelta(hours=2))
    ap = [a for a in (rec.get("appointments") or []) if isinstance(a, dict) and a.get("at") and not a.get("cancelled")]
    ap = [a for a in ap if (_when(a["at"]) or datetime.min.replace(tzinfo=UK_TZ)) >= from_dt]
    return min(ap, key=lambda a: a["at"]) if ap else None


UK_TZ = now_uk().tzinfo


def _when(iso: Any) -> Optional[datetime]:
    try:
        d = datetime.fromisoformat(str(iso))
        return d if d.tzinfo else d.replace(tzinfo=UK_TZ)
    except (TypeError, ValueError):
        return None


def rec_label(rec: Dict[str, Any]) -> str:
    return (rec.get("company") or rec.get("contact") or rec.get("email") or "Unnamed").strip()


def rec_vertical(rec: Dict[str, Any]) -> str:
    s_ = rec.get("sector") or ""
    if s_ in VERTICAL_PRESETS:
        return s_
    return match_sector(s_) or guess_sector(rec.get("company") or "", s_, rec.get("notes") or "")


def deal_values(rec: Dict[str, Any]) -> Tuple[float, float, int, float]:
    d = rec.get("deal") or {}
    mrr, one, term = to_num(d.get("mrr")), to_num(d.get("one_off")), int(to_num(d.get("term")) or 0)
    return mrr, one, term, mrr * term + one


# ---------------- Sector guessing and enrichment (as in Lead Revival) ----------------
SECTOR_KEYWORDS = {
    "Estate & Lettings Agents": ("estate agent", "estates", "lettings", "letting", "property", "properties", "homes", "real estate"),
    "Dental Practices": ("dental", "dentist", "orthodont", "smile", "teeth"),
    "Solicitors & Legal Practices": ("solicitor", "law", "legal", "lawyer", "conveyancing", "barrister"),
    "Accountants & Auditors": ("accountant", "accounting", "accountancy", "tax", "bookkeeping", "audit", "payroll"),
    "General Medical Clinics": ("clinic", "medical", "surgery", "health", "physio", "doctor", "gp "),
}
SECTOR_KEYWORDS = {**NEW_KEYWORDS, **SECTOR_KEYWORDS}
SIC_SECTOR_PREFIXES = {
    "683": "Estate & Lettings Agents", "8623": "Dental Practices", "691": "Solicitors & Legal Practices",
    "692": "Accountants & Auditors", "8621": "General Medical Clinics", "8622": "General Medical Clinics",
    "869": "General Medical Clinics",
}
SECTOR_FALSE_FRIENDS = ("health and safety", "health & safety", "health&safety", "health + safety", "tree surgery",
                        "tree surgeon", "law enforcement", "property maintenance", "fire safety")


def sector_from_sic(sic_codes: List[str]) -> Optional[str]:
    for code in sic_codes or []:
        for prefix, sector in SIC_SECTOR_PREFIXES.items():
            if str(code).startswith(prefix):
                return sector
        for sector, cfg in VERTICAL_PRESETS.items():
            if str(code) in (cfg.get("sic_codes") or []):
                return sector
    return None


def sector_from_place_types(types: List[str]) -> Optional[str]:
    tset = set(types or []) - {"health"}
    for sector, rules in SECTOR_PLACE_RULES.items():
        if tset & set(rules.get("types") or []):
            return sector
    return None


def guess_sector(company: str, industry: str = "", description: str = "") -> str:
    hay = f" {company} {industry} {description} ".lower()
    for phrase in SECTOR_FALSE_FRIENDS:
        hay = hay.replace(phrase, " ")
    for sector, words in SECTOR_KEYWORDS.items():
        if any(w in hay for w in words):
            return sector
    return "General Business"


def _name_similarity(a: str, b: str) -> float:
    ta, tb = set(distinctive_name_tokens(a)), set(distinctive_name_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def find_company_by_name(enricher: "LeadEnricher", company: str, town: str = "", postcode: str = "") -> Optional[Dict[str, Any]]:
    if not enricher.ch_api_key or not company:
        return None
    try:
        resp = requests.get(f"{enricher.base_url}/search/companies", headers=enricher.headers,
                            params={"q": company, "items_per_page": 10}, timeout=10)
        if resp.status_code != 200:
            return None
        items = resp.json().get("items", [])
    except (requests.exceptions.RequestException, ValueError):
        return None
    best, best_score = None, 0.0
    for it in items:
        if (it.get("company_status") or "").lower() != "active":
            continue
        score = _name_similarity(company, it.get("title", ""))
        snippet = (it.get("address_snippet") or "").lower()
        if postcode and postcode.replace(" ", "").lower() in snippet.replace(" ", ""):
            score += 0.3
        elif town and town.lower() in snippet:
            score += 0.15
        if score > best_score:
            best, best_score = it, score
    return best if best and best_score >= 0.75 else None


def enrich_record(rec: Dict[str, Any], ch_key: str) -> Tuple[Dict[str, Any], List[str]]:
    """Finds what's missing for one customer (Companies House, free registers, Google Maps, their website).
    Only fills blanks; never overwrites what's already on the record. Returns (field updates, notes)."""
    e = LeadEnricher(ch_api_key=ch_key)
    company = rec_label(rec)
    town, postcode = (rec.get("town") or "").strip(), (rec.get("postcode") or "").strip()
    vertical = rec_vertical(rec)
    notes: List[str] = []
    ch = None
    if rec.get("company_number"):
        ch = {"company_number": rec["company_number"], "title": company, "address_snippet": rec.get("address") or ""}
    elif ch_key:
        ch = find_company_by_name(e, company, town, postcode)
    company_number = ch.get("company_number") if ch else None
    officers = mark_owners(e.get_officers(company_number), psc_owner_names(ch_key, company_number)) \
        if company_number and ch_key else []
    sic_codes: List[str] = []
    reg_address = ch.get("address_snippet") if ch else None
    if company_number and ch_key:
        try:
            det = e.get_company_details(company_number)
            sic_codes = list(det.get("sic_codes") or [])
            addr = det.get("registered_office_address") or {}
            reg_address = ", ".join(x for x in (addr.get("premises"), addr.get("address_line_1"), addr.get("locality"),
                                                addr.get("postal_code")) if x) or reg_address
            town = town or (addr.get("locality") or "")
            postcode = postcode or (addr.get("postal_code") or "")
        except Exception:
            pass
    notes.append(f"Companies House: matched {ch.get('title')} (#{company_number})" if ch and company_number
                 else "Companies House: no confident match" if ch_key else "Companies House key not set")
    crm_site = (rec.get("website") or "").strip()
    crm_phone = (rec.get("phone") or rec.get("mobile") or "").strip()
    free, free_notes = (None, [])
    if not (crm_site and crm_phone):
        free, free_notes = free_intel(company, postcode, vertical)
    notes += free_notes
    have_site = bool(crm_site or (free and free.get("website")))
    have_phone = bool(crm_phone or (free and free.get("phone")))
    places = e.places_lookup(company, town or postcode, vertical) if not (have_site and have_phone) else None
    if places is None and getattr(e, "last_places_note", None):
        notes.append(e.last_places_note)
    trading = places["name"] if places and places.get("name") else None
    if crm_site:
        target, confidence = (crm_site if crm_site.startswith("http") else f"https://{crm_site}"), "From list"
    else:
        listed_site, listed_source = (places.get("website"), "Google Maps") if places and places.get("website") else (
            (free["website"], free["source"]) if free and free.get("website") else (None, "Google Maps"))
        d = e.auto_discover_website(company, location=town or postcode, company_number=company_number,
                                    postcode=postcode, places_website=listed_site, trading_name=trading,
                                    listing_source=listed_source)
        target, confidence = d.get("url"), d.get("confidence")
        notes += d.get("notes", [])
    site = e.scrape_contact_channels(target, names=[company, trading or ""]) if target else {
        "emails": [], "other_emails": [], "phones": [], "description": "", "resolved_url": None}
    found_emails, dead = filter_deliverable(list(dict.fromkeys(
        ([free["email"]] if free and free.get("email") else []) + list(site.get("emails") or []))))
    if dead:
        notes.append("Dropped (domain can't receive email): " + ", ".join(dead[:3]))
    phones: List[str] = []
    for raw in [free.get("phone") if free else None, places.get("phone") if places else None] + list(site.get("phones") or []):
        ph = normalise_uk_phone(raw or "")
        if ph and ph not in phones:
            phones.append(ph)
    upd: Dict[str, Any] = {}

    def fill(field: str, value: Any) -> None:
        if value and not str(rec.get(field) or "").strip():
            upd[field] = value

    if target and confidence in ("High", "Medium", "Manual", "From list"):
        fill("website", site.get("resolved_url") or target)
    elif target:
        notes.append(f"Possible website (not confident): {target}")
    if found_emails:
        lead_tmp = ScrapedLead(company_name=company, emails_found=found_emails, officers=officers,
                               contact_name=rec.get("contact") or None)
        fill("email", pick_primary_email(lead_tmp, rec.get("contact") or "") or found_emails[0])
        others = [x for x in found_emails if x != (upd.get("email") or rec.get("email"))]
        if others:
            upd["other_emails"] = list(dict.fromkeys((rec.get("other_emails") or []) + others))[:6]
    for ph in phones:
        if ph.startswith("07"):
            fill("mobile", ph)
        else:
            fill("phone", ph)
    officer = pick_decision_maker(officers)
    if officer:
        fill("contact", display_officer_name(officer.name))
        fill("role", format_role(officer.role) if officer.role else "")
    fill("company_number", company_number)
    fill("address", reg_address)
    fill("town", town)
    fill("postcode", postcode)
    if not rec.get("sector"):
        by = sector_from_sic(sic_codes) or sector_from_place_types(places.get("types", []) if places else []) or \
            guess_sector(company, "", " ".join(filter(None, [trading or "", site.get("description") or ""])))
        upd["sector"] = by
    if trading and _n(trading) != _n(company):
        fill("trading_name", trading)
    upd["enriched_at"] = now_uk().isoformat(timespec="seconds")
    upd["enrich_notes"] = notes[-8:]
    return upd, notes


def enrich_records(rids: List[str]) -> Tuple[int, List[str]]:
    data = crm_get()
    rids = [r for r in rids if r in data][:MAX_BATCH]
    if not rids:
        return 0, []
    progress = st.progress(0.0, text="Enriching…")
    results: Dict[str, Dict[str, Any]] = {}
    fails: List[str] = []
    key = ch_api_key if "ch_api_key" in globals() else secret_ch_key

    def _one(rid: str) -> Tuple[str, Dict[str, Any]]:
        return rid, enrich_record(dict(data[rid]), key)[0]

    with ThreadPoolExecutor(max_workers=min(4, len(rids))) as pool:
        futs = {pool.submit(_one, r): r for r in rids}
        for done_n, fut in enumerate(as_completed(futs), start=1):
            rid = futs[fut]
            try:
                results[rid] = fut.result()[1]
            except Exception:
                fails.append(rec_label(data[rid]))
            progress.progress(done_n / len(rids), text=f"Enriched {done_n} of {len(rids)} · {rec_label(data[rid])}")
    progress.empty()
    latest = crm_get()
    changes = {}
    for rid, upd in results.items():
        if rid in latest:
            changes[rid] = {**latest[rid], **upd}
    if changes:
        crm_save(changes, f"{len(changes)} enriched")
    return len(changes), fails


# ---------------- Import / export ----------------
def auto_map(columns: List[str]) -> Dict[str, Optional[str]]:
    low = {c: re.sub(r"\s+", " ", str(c).strip().lower()) for c in columns}
    out: Dict[str, Optional[str]] = {}
    used: Set[str] = set()
    for field, aliases in IMPORT_ALIASES.items():
        hit = next((c for c in columns if low[c] in aliases and c not in used), None)
        if not hit and field not in ("contact", "status", "term", "notes", "provider", "contract_end", "handsets"):
            hit = next((c for c in columns if c not in used and low[c] not in EXPORT_ONLY_COLS
                        and any(a in low[c] for a in aliases if len(a) >= 5)), None)
        out[field] = hit
        if hit:
            used.add(hit)
    return out


def match_status(v: Any) -> Optional[str]:
    t = _n(v)
    if not t:
        return None
    for s_ in PIPELINE:
        if _n(s_) == t:
            return s_
    for s_ in PIPELINE:
        if t in _n(s_) or _n(s_) in t:
            return s_
    if "appoint" in t or "meeting" in t:
        return "Appointment"
    if "callback" in t or "call back" in str(v).lower():
        return "Call back"
    return None


def crm_index(data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    idx: Dict[str, Dict[str, str]] = {"email": {}, "phone": {}, "co_pc": {}, "co": {}, "num": {}}
    for rid, r in data.items():
        if (r.get("email") or "").strip():
            idx["email"].setdefault(r["email"].strip().lower(), rid)
        for p in (r.get("phone"), r.get("mobile")):
            if norm_phone(p or ""):
                idx["phone"].setdefault(norm_phone(p), rid)
        co = norm_company(r.get("company") or "")
        if co:
            idx["co_pc"].setdefault(co + "|" + norm_pc(r.get("postcode") or ""), rid)
            idx["co"].setdefault(co, rid)
        if r.get("company_number"):
            idx["num"].setdefault(str(r["company_number"]).upper(), rid)
    return idx


def find_match(row: Dict[str, Any], data: Dict[str, Any], idx: Dict[str, Dict[str, str]]) -> Optional[str]:
    if row.get("hub_id") and row["hub_id"] in data:
        return row["hub_id"]
    if row.get("company_number") and str(row["company_number"]).upper() in idx["num"]:
        return idx["num"][str(row["company_number"]).upper()]
    if (row.get("email") or "").strip().lower() in idx["email"]:
        return idx["email"][row["email"].strip().lower()]
    for p in (row.get("phone"), row.get("mobile")):
        if norm_phone(p or "") in idx["phone"]:
            return idx["phone"][norm_phone(p)]
    co = norm_company(row.get("company") or "")
    if co and (co + "|" + norm_pc(row.get("postcode") or "")) in idx["co_pc"]:
        return idx["co_pc"][co + "|" + norm_pc(row.get("postcode") or "")]
    if co and not row.get("postcode") and co in idx["co"]:
        return idx["co"][co]
    return None


def import_rows(df: pd.DataFrame, mapping: Dict[str, Optional[str]], source: str, overwrite: bool,
                keep_extra: bool = True) -> Tuple[int, int, int]:
    data = dict(crm_get())
    idx = crm_index(data)
    mapped_cols = {c for c in mapping.values() if c}
    who, stamp = crm_user(), now_uk().isoformat(timespec="seconds")
    changes: Dict[str, Dict[str, Any]] = {}
    added = updated = skipped = 0
    for _, raw in df.iterrows():
        def val(field: str) -> str:
            col = mapping.get(field)
            if not col:
                return ""
            v = raw.get(col)
            return "" if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip().lower() == "nan" else str(v).strip()
        row = {f: val(f) for f in IMPORT_ALIASES}
        if not row["contact"] and (row["first_name"] or row["last_name"]):
            row["contact"] = " ".join(x for x in (row["first_name"], row["last_name"]) if x)
        if row["phone"]:
            row["phone"] = normalise_uk_phone(row["phone"]) or row["phone"]
        if row["mobile"]:
            row["mobile"] = normalise_uk_phone(row["mobile"]) or row["mobile"]
        if row["postcode"]:
            row["postcode"] = row["postcode"].upper()
        if not (row["company"] or row["email"] or row["phone"] or row["contact"]):
            skipped += 1
            continue
        extra = {}
        if keep_extra:
            for col in df.columns:
                if col in mapped_cols or str(col).strip().lower() in EXPORT_ONLY_COLS:
                    continue
                v = raw.get(col)
                if v is not None and not (isinstance(v, float) and pd.isna(v)) and str(v).strip():
                    extra[str(col)] = str(v).strip()
        rid = find_match(row, data, idx)
        rec = dict(data.get(rid) or {}) if rid else {"id": new_id(), "status": "New", "calls": [], "created_at": stamp,
                                                      "created_by": who, "source": source}
        for f, _lbl in CRM_FIELDS:
            v = row.get(f)
            if v and (overwrite or not str(rec.get(f) or "").strip()):
                rec[f] = v
        st_ = match_status(row.get("status"))
        if st_ and (overwrite or not rid):
            rec["status"] = st_
        nd = to_date(row.get("next_action"))
        if nd and (overwrite or not rec.get("next_action")):
            rec["next_action"] = nd.isoformat()
        for f in ("next_note", "owner", "company_number", "provider", "next_time"):
            if row.get(f) and (overwrite or not rec.get(f)):
                rec[f] = row[f]
        if row.get("handsets") and to_num(row["handsets"]) and (overwrite or not rec.get("handsets")):
            rec["handsets"] = int(to_num(row["handsets"]))
        ce_ = to_date(row.get("contract_end"))
        if ce_ and (overwrite or not rec.get("contract_end")):
            rec["contract_end"] = ce_.isoformat()
        if row.get("mrr") or row.get("one_off") or row.get("term") or row.get("won_at"):
            deal = dict(rec.get("deal") or {})
            for f in ("mrr", "one_off"):
                if row.get(f) and (overwrite or not deal.get(f)):
                    deal[f] = to_num(row[f])
            if row.get("term") and (overwrite or not deal.get("term")):
                deal["term"] = int(to_num(row["term"]))
            wd = to_date(row.get("won_at"))
            if wd and (overwrite or not deal.get("won_at")):
                deal["won_at"] = wd.isoformat()
            rec["deal"] = deal
        if extra:
            rec["extra"] = {**(rec.get("extra") or {}), **extra} if not overwrite else {**(rec.get("extra") or {}), **extra}
        rid = rid or rec["id"]
        rec["id"] = rid
        if rid in data:
            updated += 1
        else:
            added += 1
        data[rid] = rec
        changes[rid] = rec
        idx = crm_index(data) if (added + updated) % 200 == 0 else idx
        if rid not in idx["co"].values():
            co = norm_company(rec.get("company") or "")
            if co:
                idx["co_pc"].setdefault(co + "|" + norm_pc(rec.get("postcode") or ""), rid)
                idx["co"].setdefault(co, rid)
            if (rec.get("email") or "").strip():
                idx["email"].setdefault(rec["email"].strip().lower(), rid)
    if changes:
        crm_save(changes, f"import from {source}: {added} added, {updated} updated")
    return added, updated, skipped


def export_df(records: List[Dict[str, Any]]) -> pd.DataFrame:
    sent = get_sent_log()
    rows = []
    extra_cols: List[str] = []
    for r in records:
        for k in (r.get("extra") or {}):
            if k not in extra_cols:
                extra_cols.append(k)
    for r in records:
        lc = last_call(r)
        ap = next_appt(r)
        mrr, one, term, tcv = deal_values(r)
        row = {"Hub ID": r.get("id", ""), **{lbl: r.get(f, "") for f, lbl in CRM_FIELDS},
               "Status": r.get("status", ""), "Next action": r.get("next_action", ""),
               "Next action note": r.get("next_note", ""),
               "Last call": (lc or {}).get("at", "")[:16].replace("T", " "), "Last outcome": (lc or {}).get("outcome", ""),
               "Calls": len([c for c in calls_of(r) if c.get("outcome") not in ("Note", "Edited")]),
               "Next appointment": (ap or {}).get("at", "")[:16].replace("T", " "),
               "Monthly value (£)": mrr or "", "One-off value (£)": one or "", "Contract term (months)": term or "",
               "Total contract value (£)": tcv or "", "Won on": (r.get("deal") or {}).get("won_at", ""),
               "Emailed": "Yes" if f"crm:{r.get('id')}" in sent else "", "Owner": r.get("owner", ""),
               "Company number": r.get("company_number", ""), "Other emails": ", ".join(r.get("other_emails") or []),
               "Head office phone": r.get("ho_phone", ""), "Handsets": r.get("handsets", ""),
               "Current provider": r.get("provider", ""), "Contract end": r.get("contract_end", ""),
               "Staff": r.get("employees", ""), "Credit rating": r.get("credit_rating", ""),
               "Credit band": credit_band(r.get("credit_rating")), "Company status": r.get("company_status", ""),
               "TPS": "Yes" if r.get("tps") else "", "TPS consent": "Yes" if r.get("tps_ok") else "",
               "Line type": r.get("line_type", ""), "Region": r.get("region", ""), "County": r.get("county", ""),
               "SIC": r.get("sic", ""), "SIC description": r.get("sic_desc", ""),
               "Lease asset": r.get("lease_asset", ""), "Lease market": r.get("lease_market", ""),
               "Lease rental (£)": r.get("lease_rental", ""), "Rental frequency": r.get("lease_freq", ""),
               "Lease end": r.get("lease_end", ""), "Lease supplier": r.get("lease_supplier", ""),
               "Tags": ", ".join(r.get("tags") or []), "Next action time": r.get("next_time", ""),
               "Install date": (r.get("deal") or {}).get("install_date", ""),
               "Sold by": (r.get("deal") or {}).get("won_by", ""),
               "Source": r.get("source", ""), "Added": str(r.get("created_at", ""))[:10]}
        for k in extra_cols:
            row[k] = (r.get("extra") or {}).get(k, "")
        rows.append(row)
    return pd.DataFrame(rows)


def to_xlsx(df: pd.DataFrame, sheet: str = "Customers") -> Optional[bytes]:
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xw:
            df.to_excel(xw, index=False, sheet_name=sheet[:30])
            ws = xw.sheets[sheet[:30]]
            for i, col in enumerate(df.columns, start=1):
                width = min(45, max(10, len(str(col)) + 2, *(len(str(v)) + 2 for v in df[col].head(200))))
                ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = width
        return buf.getvalue()
    except Exception:
        return None


def read_upload(file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    name = (file.name or "").lower()
    try:
        if name.endswith((".xlsx", ".xlsm", ".xls")):
            return pd.read_excel(file, dtype=str), None
        raw = file.getvalue()
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=enc), None
            except UnicodeDecodeError:
                continue
        return None, "Couldn't read that file's text encoding."
    except Exception as exc:
        return None, f"Couldn't read that file ({exc.__class__.__name__}). Save it as .csv or .xlsx and try again."


# ---------------- Master data workbook (leasing list, "good credit" list, NOT Sold) ----------------
# The SW Comms master sheet has ~80 columns. These importers keep the ones that help pick who to call
# (staff numbers, credit, lease end and rental, phone system type, TPS flags) as proper fields you can filter on.
NOT_TRADING_RE = re.compile(r"dissol|liquidat|administ|receiver|winding|removed|closed|converted|gazette|creditors",
                            re.I)
CREDIT_BANDS = [("A", 71, 100, "Very low risk"), ("B", 51, 70, "Low risk"), ("C", 30, 50, "Moderate risk"),
                ("D", 21, 29, "High risk"), ("E", -999, 20, "Very high risk / not rated")]
EMP_BANDS = [("1-4", 1, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20-49", 20, 49), ("50-99", 50, 99), ("100+", 100, 10 ** 9)]
SMALL_WORDS = {"and", "of", "the", "for", "in", "on", "at", "to", "de"}
KEEP_UPPER = {"UK", "LLP", "PLC", "CIC", "NHS", "GP", "IT", "ICT", "TV", "PR", "HR", "UPVC"}


def tidy_name(text: Any) -> str:
    """'WESTON PARK CARE LIMITED' -> 'Weston Park Care Limited' (leaves mixed-case names alone)."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    t = re.sub(r"\bLTD\.?$", "Ltd", t) if not t.isupper() else t
    if not t or not t.isupper():
        return t
    out = []
    for i, w in enumerate(t.split(" ")):
        core = w.strip("().,&'")
        if core == "LTD":
            out.append("Ltd")
        elif core in KEEP_UPPER or (len(core) <= 3 and core.isalpha() and not any(c in "AEIOU" for c in core)):
            out.append(w)
        elif i and w.lower() in SMALL_WORDS:
            out.append(w.lower())
        else:
            out.append("-".join(re.sub(r"[A-Za-z]", lambda m: m.group(0).upper(), p.lower(), count=1)
                                for p in w.split("-")))
    return " ".join(out)


UK_COUNTIES = {
    "ABERDEENSHIRE", "ANGLESEY", "ISLE OF ANGLESEY", "ANGUS", "ARGYLL", "AVON", "AYRSHIRE", "BEDFORDSHIRE", "BERKSHIRE",
    "BLAENAU GWENT", "BUCKINGHAMSHIRE", "BUCKS", "CAERPHILLY", "CAMBRIDGESHIRE", "CAMBS", "CARMARTHENSHIRE",
    "CEREDIGION", "CHESHIRE", "CLEVELAND", "CLWYD", "CONWY", "CORNWALL", "COUNTY DURHAM", "CO DURHAM", "DURHAM",
    "CUMBRIA", "DENBIGHSHIRE", "DERBYSHIRE", "DEVON", "DORSET", "DUMFRIESSHIRE", "DYFED", "EAST SUSSEX",
    "EAST YORKSHIRE", "EAST RIDING OF YORKSHIRE", "ESSEX", "FIFE", "FLINTSHIRE", "GLAMORGAN", "MID GLAMORGAN",
    "SOUTH GLAMORGAN", "WEST GLAMORGAN", "VALE OF GLAMORGAN", "GLOUCESTERSHIRE", "GLOS", "GREATER LONDON",
    "GREATER MANCHESTER", "GWENT", "GWYNEDD", "HAMPSHIRE", "HANTS", "HEREFORDSHIRE", "HERTFORDSHIRE", "HERTS",
    "ISLE OF WIGHT", "KENT", "LANARKSHIRE", "LANCASHIRE", "LANCS", "LEICESTERSHIRE", "LEICS", "LINCOLNSHIRE", "LINCS",
    "LOTHIAN", "MERSEYSIDE", "MERTHYR TYDFIL", "MIDDLESEX", "MIDLOTHIAN", "MONMOUTHSHIRE", "NEATH PORT TALBOT",
    "NORFOLK", "NORTH YORKSHIRE", "NORTHAMPTONSHIRE", "NORTHANTS", "NORTHUMBERLAND", "NOTTINGHAMSHIRE", "NOTTS",
    "OXFORDSHIRE", "OXON", "PEMBROKESHIRE", "PERTHSHIRE", "POWYS", "RENFREWSHIRE", "RHONDDA CYNON TAF", "RUTLAND",
    "SHROPSHIRE", "SOMERSET", "SOUTH YORKSHIRE", "STAFFORDSHIRE", "STAFFS", "STIRLINGSHIRE", "SUFFOLK", "SURREY",
    "TORFAEN", "TYNE AND WEAR", "TYNE & WEAR", "WARWICKSHIRE", "WEST LOTHIAN", "WEST MIDLANDS", "WEST SUSSEX",
    "WEST YORKSHIRE", "WILTSHIRE", "WILTS", "WORCESTERSHIRE", "WORCS", "WREXHAM", "COUNTY ANTRIM", "CO ANTRIM",
    "COUNTY DOWN", "CO DOWN", "COUNTY TYRONE", "COUNTY ARMAGH", "COUNTY LONDONDERRY", "COUNTY FERMANAGH",
}


def _cell(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s_ = str(v).strip()
    return "" if s_.lower() in ("nan", "nat", "none", "unknown", "-1") else s_


def fix_sheet_phone(v: Any) -> str:
    """Excel drops the leading 0: '1743213007' -> '01743 213007'. Also '441915000000' and '1902855000.0'."""
    d = re.sub(r"\D", "", re.sub(r"\.0$", "", _cell(v)))
    if not d:
        return ""
    if d.startswith("44") and len(d) in (11, 12):
        d = "0" + d[2:]
    elif not d.startswith("0") and len(d) in (9, 10):
        d = "0" + d
    return normalise_uk_phone(d) or ""


def fix_company_number(v: Any) -> str:
    c = re.sub(r"\.0$", "", _cell(v)).upper().replace(" ", "")
    if not c or c in ("0", "-1"):
        return ""
    return c.zfill(8) if c.isdigit() else c


def credit_band(score: Any) -> str:
    try:
        n = int(float(score))
    except (TypeError, ValueError):
        return ""
    if n < 0:
        return ""
    return next((b for b, lo, hi, _ in CREDIT_BANDS if lo <= n <= hi), "")


def emp_band(n: Any) -> str:
    try:
        n = int(float(n))
    except (TypeError, ValueError):
        return "Unknown"
    return next((b for b, lo, hi in EMP_BANDS if lo <= n <= hi), "Unknown")


def _iso(v: Any) -> str:
    d = to_date(_cell(v)) if _cell(v) else None
    return d.isoformat() if d else ""


def _num(v: Any) -> Optional[float]:
    s_ = _cell(v)
    if not s_:
        return None
    try:
        return round(float(re.sub(r"[^\d.\-]", "", s_)), 2)
    except ValueError:
        return None


def _int(v: Any) -> Optional[int]:
    n = _num(v)
    return int(n) if n is not None else None


NOTE_DATE_RE = re.compile(r"[-–]\s*(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\s*$")


def note_to_call(note: str, by: str = "Old sheet") -> Optional[Dict[str, Any]]:
    """'Not in today, try Fri - 05.11' -> a call-history entry dated 5 Nov, so the old sheet's notes aren't lost."""
    note = (note or "").strip()
    if not note:
        return None
    m = NOTE_DATE_RE.search(note)
    when = now_uk()
    if m:
        dd, mm, yy = int(m.group(1)), int(m.group(2)), m.group(3)
        year = (2000 + int(yy) if len(yy) == 2 else int(yy)) if yy else now_uk().year
        try:
            when = datetime(year, mm, dd, 12, 0, tzinfo=UK_TZ)
            if not yy and when > now_uk() + timedelta(days=2):
                when = when.replace(year=year - 1)
        except ValueError:
            pass
    return {"at": when.isoformat(timespec="seconds"), "by": by, "outcome": "Old sheet note",
            "notes": NOTE_DATE_RE.sub("", note).strip(" -–") or note}


def detect_master_sheet(df: pd.DataFrame) -> Optional[str]:
    cols = {str(c).strip() for c in df.columns}
    if {"CompanyName", "CompanyRegistrationNumber", "TelephoneNumber"} <= cols:
        return "leasing"
    if {"NumberRecorded", "CallOutcome", "CompanyName"} <= cols:
        return "notsold"
    if {"CompanyName", "TelephoneNumber", "DirectorFirstName"} <= cols:
        return "shortlist"
    return None


MASTER_KIND_LABEL = {"leasing": "Leasing list (main data)", "shortlist": "Short list (tagged on the main data)",
                     "notsold": "Previously worked leads (with their old outcome)"}


def leasing_record(row: Dict[str, Any], source: str, stamp: str) -> Dict[str, Any]:
    g = lambda k: _cell(row.get(k))  # noqa: E731
    phone = fix_sheet_phone(row.get("TelephoneNumber"))
    ho = fix_sheet_phone(row.get("HeadOfficeTelephoneNumber"))
    a1, a2, a3, a4 = g("Address1"), g("Address2"), g("Address3"), g("Address4")
    if a3 and not a4 and a3.upper() in UK_COUNTIES:  # 'Street, Ipswich, Suffolk': the county sits in line 3
        a3, a4 = "", a3
    town = a3 or a2
    addr = ", ".join(x for x in (a1, a2 if a3 else "") if x)
    contact = " ".join(tidy_name(x) for x in (g("DirectorFirstName"), g("DirectorSecondName")) if x)
    status_txt = g("CompanyStatusDescription")
    active = str(row.get("Active")).strip().lower() in ("true", "1", "yes")
    credit = _int(row.get("CreditRating"))
    sic = re.sub(r"\.0$", "", g("SIC"))
    sic_desc = g("SICDescription").capitalize() if g("SICDescription") and g("SICDescription") != "UNCLASSIFIED" else ""
    company = tidy_name(g("CompanyName"))
    line = g("GROUP_LINE_TYPE")
    rec: Dict[str, Any] = {
        "company": company, "company_number": fix_company_number(row.get("CompanyRegistrationNumber")),
        "contact": contact, "role": g("JobTitle"), "phone": phone if not phone.startswith("07") else "",
        "mobile": phone if phone.startswith("07") else "", "ho_phone": ho if ho != phone else "",
        "website": g("WebsiteLink"), "address": tidy_name(addr), "town": tidy_name(town),
        "county": tidy_name(a4), "postcode": (g("AddressPostcode") or g("PostCode")).upper(),
        "region": g("PostcodeTerritoryArea"), "sic": sic, "sic_desc": sic_desc,
        "sector": sector_from_sic([sic]) or guess_sector(company, sic_desc),
        "company_status": status_txt, "trading_ok": bool(active and not NOT_TRADING_RE.search(status_txt)),
        "credit_rating": credit if credit is not None and credit >= 0 else None,
        "credit_limit": _num(row.get("CreditLimit")), "employees": _int(row.get("Employees")),
        "turnover": _num(row.get("Turnover")), "incorporated": _iso(row.get("IncorporationDate")),
        "tps": g("TPSNotification").upper() == "Y", "ho_ctps": g("HeadOfficeTradingCTPSFlag").upper() == "Y",
        "line_type": line if line not in ("Bad Numbers", "Wrong Details") else "",
        "lease_end": _iso(row.get("Contract End Date")), "lease_rental": _num(row.get("Next Rental Amount")),
        "lease_freq": g("Rental Frequency"), "lease_cost": _num(row.get("Original Equipment Cost")),
        "lease_term": _int(row.get("Original Term")), "lease_asset": tidy_name(g("Asset Type")),
        "lease_market": g("Market - UK View"), "lease_product": g("Commercial Product"),
        "lease_supplier": g("'Portfolio$'[Group Name]"),
        "tags": [], "source": source, "created_at": stamp,
    }
    if line in ("Bad Numbers", "Wrong Details"):
        rec["tags"].append("Bad number on sheet")
    if g("Unnamed: 39") == "1":
        rec["tags"].append("Ticked on old sheet")
    c = note_to_call(g("Unnamed: 80"))
    rec["calls"] = [c] if c else []
    return {k: v for k, v in rec.items() if v not in ("", None) or k in ("calls", "tags")}


NOTSOLD_STATUS = [("notinterested", "Not interested"), ("wrong phone", "Bad number"), ("disconnected", "Bad number"),
                  ("tps", "Do not call"), ("opt out", "Do not call"), ("callback", "Call back"),
                  ("answer phone", "No answer"), ("out of office", "No answer")]


def notsold_record(row: Dict[str, Any], source: str, stamp: str) -> Optional[Dict[str, Any]]:
    g = lambda k: _cell(row.get(k))  # noqa: E731
    if g("LRSDisposition") in ("Fake Lead",) or not (g("CompanyName") or g("NumberRecorded")):
        return None
    phone = fix_sheet_phone(row.get("NumberRecorded")) or fix_sheet_phone(row.get("LatestNumber"))
    outcome = g("CallOutcome")
    status = next((s_ for k, s_ in NOTSOLD_STATUS if k in outcome.lower()), "New")
    tags = [t for t in (("Old outcome: " + outcome[:40]) if outcome else "",
                        ("Old lead: " + g("LRSDisposition")) if g("LRSDisposition") not in ("", "Completed Survey") else "",
                        "Was booked, not sold" if outcome.lower().startswith("booked") else "") if t]
    calls = []
    when = to_date(g("CallDateTime")[:10]) if g("CallDateTime") else None
    if outcome and when:
        calls.append({"at": datetime.combine(when, dt_time(12, 0), tzinfo=UK_TZ).isoformat(timespec="seconds"),
                      "by": "Old sheet", "outcome": "Old sheet: " + outcome, "notes": g("CampaignGenerated")})
    c = note_to_call(g("Unnamed: 23"))
    if c:
        calls.append(c)
    rec = {"company": tidy_name(g("CompanyName")),
           "company_number": fix_company_number(row.get("SoldReg") or row.get("LeadReg")),
           "phone": phone if not phone.startswith("07") else "", "mobile": phone if phone.startswith("07") else "",
           "postcode": g("PostCode").upper(), "credit_rating": _int(row.get("CreditRating")),
           "incorporated": _iso(row.get("IncorporationDate")), "campaign": g("CampaignGenerated"),
           "status": status, "next_action": now_uk().date().isoformat() if status == "Call back" else "",
           "tags": tags, "calls": calls, "source": source, "created_at": stamp}
    rec["sector"] = guess_sector(rec["company"])
    return {k: v for k, v in rec.items() if v not in ("", None) or k in ("calls", "tags")}


def merge_into(existing: Dict[str, Any], new: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
    """Adds an imported row to a record that's already on the list. Call history and tags are always kept and added to;
    status, next action and deals are never touched by an import."""
    out = dict(existing)
    for k, v in new.items():
        if k in ("calls", "tags", "id", "status", "next_action", "created_at", "source", "deal", "appointments"):
            continue
        if v not in ("", None) and (overwrite or existing.get(k) in ("", None)):
            out[k] = v
    out["tags"] = list(dict.fromkeys(list(existing.get("tags") or []) + list(new.get("tags") or [])))
    seen = {(c.get("at"), c.get("notes")) for c in calls_of(existing)}
    out["calls"] = calls_of(existing) + [c for c in new.get("calls") or [] if (c.get("at"), c.get("notes")) not in seen]
    return out


def import_master(frames: List[Tuple[str, pd.DataFrame, str]], skip_closed: bool, overwrite: bool,
                  progress: Optional[Any] = None) -> Dict[str, int]:
    """frames: [(kind, dataframe, source label)]. The leasing list goes first so the others can match onto it."""
    data = dict(crm_get())
    idx = crm_index(data)
    stamp = now_uk().isoformat(timespec="seconds")
    who = crm_user()
    stats = {"added": 0, "updated": 0, "skipped_closed": 0, "skipped": 0, "tagged": 0}
    changes: Dict[str, Dict[str, Any]] = {}
    added_ids: Set[str] = set()
    order = {"leasing": 0, "notsold": 1, "shortlist": 2}
    for kind, df, source in sorted(frames, key=lambda f: order.get(f[0], 9)):
        df = df.where(pd.notna(df), None)
        for row in df.to_dict("records"):
            if kind == "shortlist":  # A hand-picked subset of the main list: tag the matching record
                key = {"company": tidy_name(_cell(row.get("CompanyName"))),
                       "postcode": _cell(row.get("AddressPostcode")).upper(),
                       "phone": fix_sheet_phone(row.get("TelephoneNumber"))}
                rid = find_match(key, data, idx)
                if not rid:
                    stats["skipped"] += 1
                    continue
                rec = dict(data[rid])
                tag = source.split(":")[-1].strip() or "Short list"
                if tag not in (rec.get("tags") or []):
                    rec["tags"] = list(rec.get("tags") or []) + [tag]
                    data[rid] = changes[rid] = rec
                    stats["tagged"] += 1
                continue
            new = leasing_record(row, source, stamp) if kind == "leasing" else notsold_record(row, source, stamp)
            if not new:
                stats["skipped"] += 1
                continue
            if kind == "leasing" and skip_closed and not new.get("trading_ok"):
                stats["skipped_closed"] += 1
                continue
            rid = find_match(new, data, idx)
            if rid:
                rec = merge_into(data[rid], new, overwrite)
                if rid not in added_ids:
                    stats["updated"] += rid not in changes
            else:
                rid = new_id()
                rec = {"id": rid, "status": "New", "created_by": who, **new}
                added_ids.add(rid)
                stats["added"] += 1
                for f_, key in (("num", str(rec.get("company_number") or "").upper()),
                                ("email", (rec.get("email") or "").lower())):
                    if key:
                        idx[f_].setdefault(key, rid)
                for p in (rec.get("phone"), rec.get("mobile")):
                    if norm_phone(p or ""):
                        idx["phone"].setdefault(norm_phone(p), rid)
                co = norm_company(rec.get("company") or "")
                if co:
                    idx["co_pc"].setdefault(co + "|" + norm_pc(rec.get("postcode") or ""), rid)
                    idx["co"].setdefault(co, rid)
            rec["id"] = rid
            data[rid] = changes[rid] = rec
    if changes:
        crm_save(changes, f"master data import: {stats['added']} added, {stats['updated']} updated", progress=progress)
    return stats


@st.cache_data(show_spinner=False, max_entries=2)
def read_workbook(raw: bytes) -> Dict[str, pd.DataFrame]:
    try:
        sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, dtype=str)
    except Exception:
        return {}
    return {str(n): d.dropna(how="all") for n, d in sheets.items()}


def render_master_import(fname: str, sheets: Dict[str, pd.DataFrame], master: Dict[str, Optional[str]]) -> None:
    st.success("This looks like the SW Comms master data. Each tab is read with its own column matching, so staff"
               " numbers, credit, lease end, rental, phone line type and TPS flags all become filters.")
    picks = []
    for name, df in sheets.items():
        kind = master.get(name)
        if not kind:
            st.caption(f"⏭ {esc(name)}: not recognised, skipped ({len(df):,} rows).")
            continue
        on = st.checkbox(f"**{name}** · {len(df):,} rows · {MASTER_KIND_LABEL[kind]}", value=True, key=f"mi_{name}")
        if on:
            picks.append((kind, df, f"Master data: {name}"))
    c1, c2 = st.columns([1.3, 1])
    skip_closed = c1.toggle("Leave out dissolved / liquidated / closed companies", value=True, key="mi_skip")
    overwrite = c2.radio("When a firm is already on the list", ["Only fill in blanks (safe)", "Update with the sheet's values"],
                         key="mi_mode") == "Update with the sheet's values"
    st.caption("Calls, statuses, call-backs, appointments and deals already logged are never changed by an import."
               " Notes typed on the old sheet are added to each firm's call history.")
    total = sum(len(d) for _, d, _ in picks)
    if st.button(f"⬆️ Import {total:,} rows", type="primary", disabled=not picks, key="mi_go"):
        bar = st.progress(0.0, text="Matching rows…")
        st.session_state["crm_hold"] = True
        try:
            stats = import_master(picks, skip_closed, overwrite,
                                  progress=lambda i, n: bar.progress(i / n, text=f"Saving… {i} of {n} files"))
        finally:
            st.session_state.pop("crm_hold", None)
        bar.empty()
        st.session_state["sh_flash"] = (
            f"⬆️ Imported {esc(fname)}: <b>{stats['added']:,}</b> added, <b>{stats['updated']:,}</b> updated"
            + (f", {stats['tagged']:,} tagged from the short list" if stats["tagged"] else "")
            + (f", {stats['skipped_closed']:,} closed companies left out" if stats["skipped_closed"] else "")
            + (f", {stats['skipped']:,} rows skipped (empty, fake or unmatched)" if stats["skipped"] else "") + ".")
        st.session_state["sh_up_ver"] = st.session_state.get("sh_up_ver", 0) + 1
        st.rerun()


# ---------------- Calls, outcomes, deals ----------------
def log_outcome(rid: str, outcome: str, notes: str = "", next_action: Optional[date] = None,
                status: Optional[str] = None, appt: Optional[Dict[str, Any]] = None,
                deal: Optional[Dict[str, Any]] = None, clear_next: bool = False, next_time: str = "",
                fields: Optional[Dict[str, Any]] = None) -> None:
    data = crm_get()
    if rid not in data:
        return
    rec = dict(data[rid])
    who, stamp = crm_user() or "Unknown", now_uk().isoformat(timespec="seconds")
    rec["calls"] = calls_of(rec) + [{"at": stamp, "by": who, "outcome": outcome, "notes": notes.strip()}]
    if status:
        rec["status"] = status
    if next_action:
        rec["next_action"] = next_action.isoformat()
        rec["next_time"] = next_time or ""
    elif clear_next:
        rec["next_action"] = rec["next_time"] = ""
    if fields:
        rec.update({k: v for k, v in fields.items() if v not in (None, "")})
    if appt:
        rec["appointments"] = (rec.get("appointments") or []) + [dict(appt, booked_by=who, booked_at=stamp)]
    if deal:
        rec["deal"] = dict(rec.get("deal") or {}, **deal)
        rec["deal"]["won_by"] = deal.get("won_by") or rec["deal"].get("won_by") or who
    if not rec.get("owner"):
        rec["owner"] = who
    crm_save({rid: rec}, f"{outcome}: {rec_label(rec)}")


def caller_queue(data: Dict[str, Any], seg: Optional[Dict[str, Any]] = None, include_future: bool = False,
                 me: str = "") -> List[str]:
    """Who to ring next: call-backs that are due (timed ones from 10 minutes before), then people never called,
    then the rest. Closed records and booked-in appointments are left out."""
    now = now_uk()
    today = now.date()
    seg = seg or SEG_DEFAULT
    out = []
    for rid, r in data.items():
        if not isinstance(r, dict):
            continue
        st_ = r.get("status") or "New"
        if seg.get("status"):
            if st_ not in seg["status"]:
                continue
        elif st_ in CLOSED:
            continue
        if not (r.get("phone") or r.get("mobile") or r.get("ho_phone")):
            continue
        if not seg_match(r, seg, today, me):
            continue
        nd = to_date(r.get("next_action"))
        due = due_now(r, now)
        if nd and not due and not include_future:
            continue
        if st_ == "Appointment" and next_appt(r) and not due:
            continue  # Booked in: nothing to call about until after the meeting
        lc = last_call(r)
        bucket = 0 if due else (1 if not lc or lc.get("by") == "Old sheet" else 2)
        out.append(((bucket, nd or today, r.get("next_time") or "", (lc or {}).get("at", ""),
                     (r.get("town") or "").lower(), rec_label(r).lower()), rid))
    return [rid for _, rid in sorted(out)]


def to_queue_for_email(rid: str) -> None:
    """Hands the customer to Prospecting's Review & send, where the pitch, PDF and Zoho sending already live."""
    r = crm_get().get(rid)
    if not r:
        return
    vertical = rec_vertical(r)
    if vertical not in VERTICAL_PRESETS:
        vertical = "General Business" if "General Business" in VERTICAL_PRESETS else sorted(VERTICAL_PRESETS)[0]
    emails = [e_ for e_ in [r.get("email")] + list(r.get("other_emails") or []) if e_]
    lead = ScrapedLead(company_name=rec_label(r), trading_name=r.get("trading_name") or None,
                       company_number=r.get("company_number") or None, emails_found=emails,
                       contact_email=r.get("email") or None, contact_name=r.get("contact") or None,
                       contact_role=r.get("role") or None, sector_guess=vertical,
                       phones_found=[p for p in (r.get("phone"), r.get("mobile")) if p],
                       website_url=r.get("website") or None, website_confidence="Manual" if r.get("website") else None,
                       registered_address=", ".join(x for x in (r.get("address"), r.get("town"), r.get("postcode")) if x) or None)
    cn = f"crm:{rid}"
    add_to_queue(lead, vertical, cn=cn)
    st.session_state["queue"][cn].update({"lead_source": zoho_lead_source(), "base_vertical": vertical})
    st.session_state["current_cn"] = st.session_state["current_cn_select"] = cn
    goto_view("prospect")


# ---------------- Shared bits of UI ----------------
def sh_hero(title_html: str, sub: str, pills: List[Tuple[str, str, str]], eyebrow: str) -> None:
    def _short(n: str) -> str:  # The pill circle fits ~3 characters: 22744 -> 23k
        try:
            v = int(str(n).replace(",", ""))
        except ValueError:
            return str(n)
        return str(v) if v < 1000 else (f"{v / 1000:.1f}k" if v < 9950 else f"{round(v / 1000)}k")
    parts = [f'<div class="pe-step {cls}"><span class="num">{esc(_short(n))}</span>{esc(lbl)}</div>' for n, lbl, cls in pills]
    render_html('<div class="pe-hero"><div>'
                f'<div class="pe-eyebrow"><span class="dot"></span>{esc(eyebrow)}</div>'
                f'<div class="pe-title">{title_html}</div><div class="pe-sub">{esc(sub)}</div>'
                + (f'</div><div class="pe-stepper">{"<div class=pe-step-sep></div>".join(parts)}</div></div>' if parts
                   else "</div></div>"),
                target=hero_slot)


def kpis(items: List[Tuple[str, str, str, str]], n: int = 4) -> None:
    """items: (value, label, footnote, colour)."""
    render_html(f'<div class="sh-kpis" style="--n:{n}">' + "".join(
        f'<div class="sh-kpi" style="--c:{c or "var(--accent)"}"><div class="v">{esc(v)}</div>'
        f'<div class="l">{esc(lbl)}</div>' + (f'<div class="f">{esc(f)}</div>' if f else "") + "</div>"
        for v, lbl, f, c in items) + "</div>")


def flash(key: str = "sh_flash") -> None:
    msg = st.session_state.pop(key, None)
    if msg:
        render_html(f'<div class="sh-flash">{msg}</div>')


def show_crm_error() -> None:
    if st.session_state.get("crm_error"):
        st.warning("⚠️ " + st.session_state.pop("crm_error"))
    if CRM_STORE.backend == "local":
        st.caption("⚠️ Not saving to GitHub yet: add GITHUB_TOKEN and GITHUB_REPO to Secrets, or the list resets when the"
                   " app restarts.")


def name_gate() -> bool:
    if crm_user():
        return True
    with st.container(key="card-sh-name"):
        section_header("👋", "Who's using the Hub?", "Your name goes on every call, appointment and deal you log.")
        nm = st.text_input("Your name", key="sh_name_in", placeholder="e.g. Sarah")
        if st.button("Continue", type="primary", disabled=not nm.strip()):
            prof = st.session_state.setdefault("sender_profile", {})
            prof["name"] = nm.strip()
            st.session_state["sender_profile"] = prof
            st.rerun()
    return False


def record_card_html(r: Dict[str, Any]) -> str:
    st_ = r.get("status") or "New"
    meta = [chip(st_, STATUS_TONE.get(st_, ""))]
    if r.get("sector"):
        meta.append(chip(r["sector"], "muted"))
    if r.get("town") or r.get("postcode"):
        meta.append(chip(" ".join(x for x in (r.get("town"), r.get("postcode")) if x), "muted"))
    nd = to_date(r.get("next_action"))
    if nd:
        meta.append(chip(("Due " if nd <= now_uk().date() else "Next ") + nd.strftime("%a %d %b"),
                         "warn" if nd <= now_uk().date() else ""))
    ap = next_appt(r)
    if ap:
        meta.append(chip("📅 " + (_when(ap["at"]) or now_uk()).strftime("%a %d %b %H:%M"), "good"))
    mrr, one, term, tcv = deal_values(r)
    if (r.get("status") in SOLD) and (mrr or one):
        meta.append(chip(f"{money(mrr)}/mo · {term or '?'} mths", "good"))
    meta += facts_chips(r)
    lines = []
    who = " · ".join(x for x in (r.get("contact"), r.get("role")) if x)
    if who:
        lines.append(f'<div class="sh-line">👤 <b>{esc(who)}</b></div>')
    if r.get("email"):
        lines.append(f'<div class="sh-line">✉️ <a href="mailto:{esc(r["email"])}">{esc(r["email"])}</a></div>')
    if r.get("website"):
        site = r["website"] if r["website"].startswith("http") else "https://" + r["website"]
        lines.append(f'<div class="sh-line">🌐 <a href="{esc(site)}" target="_blank">{esc(domain_of(site) or site)}</a></div>')
    addr = ", ".join(x for x in (r.get("address"), r.get("town"), r.get("postcode")) if x)
    if addr:
        maps = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(addr)
        lines.append(f'<div class="sh-line">📍 <a href="{esc(maps)}" target="_blank">{esc(addr)}</a></div>')
    lines.append(lease_html(r) + company_facts_html(r))
    legal = r.get("trading_name") and r.get("company") and r["trading_name"] != r["company"]
    return (f'<div class="cl-firm">{esc(r.get("trading_name") or rec_label(r))}</div>'
            + (f'<div class="cl-legal">{esc(r["company"])}</div>' if legal else "")
            + f'<div class="sh-meta">{"".join(meta)}</div>' + "".join(lines))


def phone_html(r: Dict[str, Any]) -> str:
    nums = list(dict.fromkeys(p for p in (r.get("phone"), r.get("mobile"), r.get("ho_phone")) if p))
    if not nums:
        return '<div class="cl-phone"><div><div class="alt">No phone number yet: enrich it or add one.</div></div></div>'
    first, rest = nums[0], nums[1:]
    tel = lambda p: re.sub(r"[^\d+]", "", p)  # noqa: E731
    return (f'<div class="cl-phone"><div class="ic">{icon("phone", 20, 2.2)}</div><div>'
            f'<a href="tel:{tel(first)}">{esc(first)}</a>'
            + "".join(f'<div class="alt">or <a style="font-size:.95rem" href="tel:{tel(p)}">{esc(p)}</a>'
                      + (' <span style="color:var(--faint)">(head office)</span>' if p == r.get("ho_phone") else "")
                      + '</div>' for p in rest)
            + "</div></div>")


def history_html(r: Dict[str, Any], n: int = 6) -> str:
    cs = sorted(calls_of(r), key=lambda c: c.get("at", ""), reverse=True)[:n]
    if not cs:
        return '<div class="sh-line">No calls logged yet.</div>'
    return '<div class="cl-hist">' + "".join(
        f'<div class="row"><span class="when">{esc((_when(c.get("at")) or now_uk()).strftime("%d %b %H:%M"))}</span>'
        f'<span><b>{esc(c.get("outcome"))}</b>' + (f' · {esc(c.get("notes"))}' if c.get("notes") else "")
        + f' <span style="color:var(--faint)">· {esc(c.get("by") or "")}</span></span></div>' for c in cs) + "</div>"


def deal_inputs(prefix: str, rec: Dict[str, Any]) -> Dict[str, Any]:
    d = rec.get("deal") or {}
    c1, c2, c3 = st.columns(3)
    mrr = c1.number_input("Monthly value (£)", min_value=0.0, step=5.0, value=float(to_num(d.get("mrr"))),
                          key=f"{prefix}_mrr")
    one = c2.number_input("One-off value (£)", min_value=0.0, step=50.0, value=float(to_num(d.get("one_off"))),
                          key=f"{prefix}_one")
    t0 = int(to_num(d.get("term")) or 36)
    term = c3.selectbox("Contract term (months)", DEAL_TERMS + ([t0] if t0 not in DEAL_TERMS else []),
                        index=(DEAL_TERMS + ([t0] if t0 not in DEAL_TERMS else [])).index(t0), key=f"{prefix}_term")
    c4, c5, c6 = st.columns(3)
    won = c4.date_input("Sold on", value=to_date(d.get("won_at")) or now_uk().date(), format="DD/MM/YYYY",
                        key=f"{prefix}_won")
    inst = c5.date_input("Install date", value=to_date(d.get("install_date")), format="DD/MM/YYYY", key=f"{prefix}_inst")
    rep = rep_picker(c6, "Sold by", key=f"{prefix}_rep", value=d.get("won_by") or "")
    st.caption(f"Total contract value: **{money(mrr * term + one)}** ({money(mrr)} × {term} months + {money(one)}).")
    return {"mrr": mrr, "one_off": one, "term": int(term), "won_at": won.isoformat(),
            "install_date": inst.isoformat() if inst else "", "won_by": rep}


def goto_view(view: str) -> None:
    """Switches page on the next run (the sidebar switch picks it up before it's drawn)."""
    st.session_state["_goto_view"] = view
    st.query_params["view"] = view


def open_in_caller(rid: str) -> None:
    st.session_state["caller_rid"] = rid
    goto_view("caller")


# ---------------- 📇 Customers ----------------
def render_record_editor(rid: str) -> None:
    data = crm_get()
    r = data.get(rid)
    if not r:
        return
    ver = st.session_state.get("crm_ver", 0)
    with st.container(key="card-sh-record"):
        render_html(record_card_html(r))
        a1, a2, a3, a4 = st.columns(4)
        if a1.button("📞 Call now", key=f"ed_call_{rid}", **FULL_WIDTH):
            open_in_caller(rid)
            st.rerun()
        if a2.button("✨ Enrich", key=f"ed_enrich_{rid}", **FULL_WIDTH,
                     help="Finds missing website, email, phone, decision maker and sector. Never overwrites."):
            n, fails = enrich_records([rid])
            st.session_state["sh_flash"] = (f"✨ Enriched {esc(rec_label(r))}." if n else
                                            "Couldn't enrich: " + esc(", ".join(fails)))
            st.rerun()
        if a3.button("✉️ Email (Zoho)", key=f"ed_mail_{rid}", disabled=not r.get("email"), **FULL_WIDTH,
                     help="Opens the pitch and overview PDF in Prospecting's Review & send, ready to send via Zoho."):
            to_queue_for_email(rid)
            st.rerun()
        try:
            pop = a4.popover("🗑 Delete", **FULL_WIDTH)
        except TypeError:
            pop = a4.popover("🗑 Delete")
        with pop:
            st.caption("Removes this customer and their call history. This can't be undone.")
            if st.button("Yes, delete", key=f"ed_del_{rid}", type="primary"):
                crm_save({rid: None}, f"deleted {rec_label(r)}")
                st.session_state.pop("cust_rid", None)
                st.rerun()
        if r.get("enrich_notes"):
            with st.expander("What enrichment found"):
                for n_ in r["enrich_notes"]:
                    st.caption("• " + str(n_))
        with st.form(f"ed_form_{rid}_{ver}", border=False):
            render_html('<div class="sh-section">Details</div>')
            vals = {}
            cols = st.columns(2)
            for i, (f, lbl) in enumerate(CRM_FIELDS):
                if f in ("notes",):
                    continue
                if f == "sector":
                    opts = [""] + sorted(VERTICAL_PRESETS)
                    cur = r.get("sector") or ""
                    vals[f] = cols[i % 2].selectbox(lbl, opts + ([cur] if cur not in opts else []),
                                                    index=(opts + ([cur] if cur not in opts else [])).index(cur))
                else:
                    vals[f] = cols[i % 2].text_input(lbl, value=r.get(f) or "")
            vals["notes"] = st.text_area("Notes", value=r.get("notes") or "", height=90)
            render_html('<div class="sh-section">Phone system</div>')
            q1, q2, q3, q4 = st.columns(4)
            hs = q1.number_input("Handsets", min_value=0, step=1, value=int(to_num(r.get("handsets")) or 0))
            prov = q2.text_input("Current provider", value=r.get("provider") or "")
            ce = q3.date_input("Their contract ends", value=to_date(r.get("contract_end")), format="DD/MM/YYYY")
            ho = q4.text_input("Head office phone", value=r.get("ho_phone") or "")
            t1_, t2_ = st.columns([3, 1])
            tags_in = t1_.text_input("Tags (comma separated)", value=", ".join(r.get("tags") or []),
                                     placeholder="e.g. Hot, Ring after Christmas")
            tps_ok = t2_.checkbox("OK to call (TPS consent)", value=bool(r.get("tps_ok")), disabled=not r.get("tps"))
            render_html('<div class="sh-section">Pipeline</div>')
            p1, p2, p3 = st.columns(3)
            status = p1.selectbox("Status", PIPELINE, index=PIPELINE.index(r.get("status") or "New")
                                  if (r.get("status") or "New") in PIPELINE else 0)
            nd = p2.date_input("Next action date", value=to_date(r.get("next_action")), format="DD/MM/YYYY")
            owner = p3.text_input("Owner", value=r.get("owner") or "")
            next_note = st.text_input("Next action note", value=r.get("next_note") or "",
                                      placeholder="e.g. Send quote for 6 handsets")
            render_html('<div class="sh-section">Deal (when sold)</div>')
            deal = deal_inputs(f"ed_deal_{rid}_{ver}", r)
            facts = [(lbl, r.get(k)) for k, lbl in (
                ("company_status", "Company status"), ("credit_rating", "Credit score"), ("credit_limit", "Credit limit (£)"),
                ("employees", "Staff"), ("turnover", "Turnover (£)"), ("sic_desc", "Business activity"), ("sic", "SIC"),
                ("incorporated", "Incorporated"), ("region", "Region"), ("county", "County"), ("line_type", "Phone lines"),
                ("lease_asset", "Leased asset"), ("lease_market", "Lease market"), ("lease_product", "Lease product"),
                ("lease_rental", "Lease rental (£)"), ("lease_freq", "Rental frequency"), ("lease_cost", "Equipment cost (£)"),
                ("lease_term", "Lease term (months)"), ("lease_end", "Lease end"), ("lease_supplier", "Lease via"),
                ("campaign", "Old campaign"), ("reg_address", "Registered office"), ("officers", "Officers"),
                ("former_contact", "Previous contact"), ("ch_checked_at", "Checked at Companies House"),
                ("source", "Came from")) if r.get(k) not in (None, "", [])]
            if facts:
                with st.expander(f"Company & lease data ({len(facts)})"):
                    fc = st.columns(2)
                    for i_, (lbl, v) in enumerate(facts):
                        fc[i_ % 2].markdown(f"**{esc(lbl)}:** {esc(', '.join(v) if isinstance(v, list) else v)}")
            if r.get("extra"):
                with st.expander(f"Other columns from the upload ({len(r['extra'])})"):
                    for k, v in r["extra"].items():
                        st.markdown(f"**{esc(k)}:** {esc(v)}")
            saved = st.form_submit_button("💾 Save changes", type="primary")
        if saved:
            new = {**r, **{k: (v.strip() if isinstance(v, str) else v) for k, v in vals.items()}, "status": status,
                   "next_action": nd.isoformat() if nd else "", "owner": owner.strip(), "next_note": next_note.strip(),
                   "handsets": int(hs) or "", "provider": prov.strip(), "contract_end": ce.isoformat() if ce else "",
                   "ho_phone": normalise_uk_phone(ho) or ho.strip(), "tps_ok": bool(tps_ok),
                   "tags": [t.strip() for t in tags_in.split(",") if t.strip()]}
            if not nd:
                new["next_time"] = ""
            if status == "Installed" and not (r.get("deal") or {}).get("installed_at"):
                deal["installed_at"] = deal.get("install_date") or now_uk().date().isoformat()
            if status in SOLD or deal["mrr"] or deal["one_off"]:
                new["deal"] = dict(r.get("deal") or {}, **deal)
            if status != (r.get("status") or "New"):
                new["calls"] = calls_of(r) + [{"at": now_uk().isoformat(timespec="seconds"), "by": crm_user(),
                                                "outcome": "Status changed", "notes": f"{r.get('status') or 'New'} → {status}"}]
            crm_save({rid: new}, f"edited {rec_label(new)}")
            st.session_state["sh_flash"] = f"💾 Saved {esc(rec_label(new))}."
            st.rerun()
        render_html('<div class="sh-section">Call history</div>' + history_html(r, 12))


def add_customer_form() -> None:
    with st.expander("➕ Add a customer by hand"):
        with st.form("sh_add", border=False):
            c = st.columns(2)
            v = {f: c[i % 2].text_input(lbl) for i, (f, lbl) in enumerate(CRM_FIELDS) if f not in ("notes", "sector")}
            v["sector"] = st.selectbox("Sector", [""] + sorted(VERTICAL_PRESETS))
            v["notes"] = st.text_area("Notes", height=70)
            go = st.form_submit_button("Add customer", type="primary")
        if go:
            if not (v["company"].strip() or v["contact"].strip()):
                st.warning("Add at least a company or contact name.")
                return
            data = crm_get()
            m = find_match(v, data, crm_index(data))
            if m:
                st.warning(f"That looks like {rec_label(data[m])}, already on the list.")
                st.session_state["cust_rid"] = m
                return
            rid = new_id()
            rec = {"id": rid, **{k: (x.strip() if isinstance(x, str) else x) for k, x in v.items()}, "status": "New",
                   "calls": [], "created_at": now_uk().isoformat(timespec="seconds"), "created_by": crm_user(),
                   "source": "Added by hand", "owner": crm_user()}
            if rec.get("phone"):
                rec["phone"] = normalise_uk_phone(rec["phone"]) or rec["phone"]
            crm_save({rid: rec}, f"added {rec_label(rec)}")
            st.session_state["cust_rid"] = rid
            st.session_state["sh_flash"] = f"➕ Added {esc(rec_label(rec))}."
            st.rerun()


def render_import_box() -> None:
    if st.session_state.get("crm_load_failed"):
        st.error("The customer list didn't load from GitHub, so uploads are paused (importing now could create"
                 " duplicates). Reload the page in a minute.")
        return
    with st.expander("⬆️ Upload a customer list (CSV or Excel)", expanded=not crm_get()):
        st.caption("Your sheet becomes the customer list. Any headings work: we match the usual ones (Company, Contact,"
                   " Phone, Email, Postcode…) and keep every other column too. Re-upload a sheet you downloaded from"
                   " here to update records: they're matched by Hub ID, then email, phone, or company + postcode.")
        up = st.file_uploader("Customer list", type=["csv", "xlsx", "xls"], key=f"sh_up_{st.session_state.get('sh_up_ver', 0)}",
                              label_visibility="collapsed")
        if not up:
            return
        if (up.name or "").lower().endswith((".xlsx", ".xlsm", ".xls")):
            with st.spinner("Reading the workbook (big sheets take up to a minute)…"):
                sheets = read_workbook(up.getvalue())
            master = {n: detect_master_sheet(d) for n, d in sheets.items()}
            if any(master.values()):
                render_master_import(up.name, sheets, master)
                return
        df, err = read_upload(up)
        if err or df is None:
            st.error(err or "Couldn't read that file.")
            return
        df = df.dropna(how="all")
        df.columns = [str(c).strip() for c in df.columns]
        st.caption(f"**{len(df):,} rows** · {len(df.columns)} columns found in {esc(up.name)}.")
        auto = auto_map(list(df.columns))
        opts = ["—"] + list(df.columns)
        mapping: Dict[str, Optional[str]] = {}
        with st.container(border=True):
            st.markdown("**Match your columns** (we've guessed; change any that are wrong)")
            mc = st.columns(3)
            for i, f in enumerate(IMPORT_ALIASES):
                cur = auto.get(f)
                pick = mc[i % 3].selectbox(IMPORT_LABELS.get(f, f), opts, index=opts.index(cur) if cur in opts else 0,
                                           key=f"map_{f}_{up.name}")
                mapping[f] = None if pick == "—" else pick
        if not any(mapping.get(f) for f in ("company", "contact", "email", "phone")):
            st.warning("Match at least one of Company, Contact, Email or Phone.")
            return
        st.dataframe(df.head(8), hide_index=True, **FULL_WIDTH)
        u1, u2 = st.columns([1.6, 1])
        overwrite = u1.radio("When a customer is already on the list",
                             ["Only fill in blanks (safe)", "Update with the sheet's values"], key="sh_up_mode",
                             horizontal=True) == "Update with the sheet's values"
        if u2.button(f"⬆️ Import {len(df):,} rows", type="primary", **FULL_WIDTH):
            with st.spinner("Importing…"):
                a, u, s_ = import_rows(df, mapping, f"Upload: {up.name}", overwrite)
            st.session_state["sh_flash"] = f"⬆️ Imported {esc(up.name)}: {a:,} added, {u:,} updated" + \
                (f", {s_:,} empty rows skipped." if s_ else ".")
            st.session_state["sh_up_ver"] = st.session_state.get("sh_up_ver", 0) + 1
            st.rerun()


def render_customers_page() -> None:
    data = crm_get()
    recs = [r for r in data.values() if isinstance(r, dict)]
    today = now_uk().date()
    due = sum(1 for r in recs if (to_date(r.get("next_action")) or date.max) <= today and (r.get("status") or "New") not in CLOSED)
    won = [r for r in recs if r.get("status") in SOLD]
    sh_hero('Customer <span>list</span>', "Your customers and prospects in one place: upload your sheet, enrich it,"
            " work it, and download it any time.",
            [(f"{len(recs):,}", "On the list", "active"), (f"{due:,}", "Due a call", ""), (f"{len(won):,}", "Sold", "done")],
            "Stand-alone CRM · saved for the whole team")
    flash()
    show_crm_error()
    render_import_box()
    add_customer_form()
    if not recs:
        st.info("Upload your customer list above to get started.")
        return
    with st.container(key="card-sh-list"):
        section_header("01", "Customers", "Search and filter, tick rows for bulk actions, or tick one to open it.")
        seg = render_segment_filters("cu", defaults={"tps": TPS_OPTS[1]})
        only_due = st.toggle("Only due a call", key="cu_due")
        now_ = now_uk()
        me = crm_user()
        view = [r for r in recs if seg_match(r, seg, today, me) and (not only_due or (
            due_now(r, now_) and (r.get("status") or "New") not in CLOSED))]
        view.sort(key=lambda r: (to_date(r.get("next_action")) or date.max, rec_label(r).lower()))
        sent = get_sent_log()
        df = pd.DataFrame([{
            "id": r["id"], "Company": rec_label(r), "Contact": r.get("contact") or "",
            "Phone": r.get("phone") or r.get("mobile") or r.get("ho_phone") or "",
            "Email": r.get("email") or "", "Town": r.get("town") or "", "Postcode": r.get("postcode") or "",
            "Status": r.get("status") or "New", "Next action": to_date(r.get("next_action")),
            "Last call": ((_when((last_call(r) or {}).get("at")) or None)),
            "Staff": r.get("employees"), "Handsets": int(to_num(r.get("handsets")) or 0) or None,
            "Credit": credit_band(r.get("credit_rating")), "Lease/contract end": end_date_of(r),
            "Equipment": r.get("lease_asset") or "", "TPS": "⛔" if is_tps(r) else "",
            "Emailed": "✓" if f"crm:{r['id']}" in sent else "", "Sector": r.get("sector") or "",
        } for r in view], columns=["id", "Company", "Contact", "Phone", "Email", "Town", "Postcode", "Status",
                                   "Next action", "Last call", "Staff", "Handsets", "Credit", "Lease/contract end",
                                   "Equipment", "TPS", "Emailed", "Sector"])
        if not df.empty:
            df["Last call"] = pd.to_datetime(df["Last call"], errors="coerce", utc=True).dt.tz_convert("Europe/London").dt.tz_localize(None)
        st.caption(f"Showing {len(view):,} of {len(recs):,}.")
        common = dict(hide_index=True, selection_mode="multi-row", on_select="rerun",
                      column_order=["Company", "Contact", "Phone", "Town", "Postcode", "Status", "Next action",
                                    "Staff", "Handsets", "Credit", "Lease/contract end", "Equipment", "TPS", "Last call",
                                    "Email", "Emailed", "Sector"],
                      column_config={"Next action": st.column_config.DateColumn("Next action", format="ddd D MMM"),
                                     "Lease/contract end": st.column_config.DateColumn("Lease/contract end", format="MMM YYYY"),
                                     "Staff": st.column_config.NumberColumn("Staff", width=60),
                                     "Handsets": st.column_config.NumberColumn("Handsets", width=70),
                                     "Credit": st.column_config.TextColumn("Credit", width=50),
                                     "TPS": st.column_config.TextColumn("TPS", width=40),
                                     "Last call": st.column_config.DatetimeColumn("Last call", format="D MMM HH:mm"),
                                     "Emailed": st.column_config.TextColumn("✉️", width=40)},
                      height=min(38 + 35 * max(len(df), 1), 480), key=f"cu_tbl_{st.session_state.get('crm_ver', 0)}")
        try:
            ev = st.dataframe(df, width="stretch", **common)
        except TypeError:
            ev = st.dataframe(df, use_container_width=True, **common)
        sel_rows = [i for i in (ev.selection.rows if ev else []) if i < len(view)]
        sel = [view[i]["id"] for i in sel_rows]
        b1, b5, b2, b3, b4 = st.columns(5)
        ch_targets = (sel or [r["id"] for r in view])[:CH_BATCH]
        if b5.button(f"🏛 Check {len(ch_targets)} at Companies House", disabled=not view, **FULL_WIDTH,
                     help=f"Free: checks each firm is still trading and updates its address, officers and sector."
                          f" Uses the ones you've ticked, or the first {CH_BATCH} shown. Records checked in the last"
                          f" 30 days are skipped."):
            n, closed, fails = ch_cleanse(ch_targets)
            st.session_state["sh_flash"] = (f"🏛 Checked {n} at Companies House" + (f": {closed} no longer trading"
                                            " (marked, and left out of the Caller)" if closed else ": all still trading")
                                            + "." + (f" {fails} not found." if fails else ""))
            st.rerun()
        if b1.button(f"✨ Enrich {len(sel) or ''} selected".replace("  ", " "), disabled=not sel, **FULL_WIDTH,
                     help=f"Up to {MAX_BATCH} at a time. Fills blanks only."):
            n, fails = enrich_records(sel)
            st.session_state["sh_flash"] = f"✨ Enriched {n} customer(s)." + (
                " Couldn't enrich: " + esc(", ".join(fails[:5])) if fails else "")
            st.rerun()
        with b2:
            try:
                pop = st.popover("🏷 Set status", disabled=not sel, **FULL_WIDTH)
            except TypeError:
                pop = st.popover("🏷 Set status", disabled=not sel)
            with pop:
                new_st = st.selectbox("New status", PIPELINE, key="cu_bulk_st")
                if st.button(f"Apply to {len(sel)}", key="cu_bulk_go", type="primary"):
                    latest = crm_get()
                    crm_save({rid: {**latest[rid], "status": new_st} for rid in sel if rid in latest},
                             f"{len(sel)} set to {new_st}")
                    st.rerun()
        if b3.button("📞 Call selected", disabled=not sel, **FULL_WIDTH):
            st.session_state["caller_focus"] = sel
            open_in_caller(sel[0])
            st.rerun()
        stamp = now_uk().strftime("%Y-%m-%d")
        dl_sig = (len(view), st.session_state.get("crm_ver", 0), seg_summary(seg))
        if st.session_state.get("cu_dl_sig") != dl_sig:
            if b4.button(f"⬇️ Prepare download ({len(view):,})", **FULL_WIDTH,
                         help="Builds an Excel file of what's shown. Big lists take a few seconds."):
                with st.spinner("Building the spreadsheet…"):
                    exp = export_df(view)
                    xl = to_xlsx(exp) if len(view) <= 40000 else None
                    st.session_state["cu_dl"] = (xl, "xlsx") if xl else (exp.to_csv(index=False).encode("utf-8-sig"), "csv")
                    st.session_state["cu_dl_sig"] = dl_sig
                st.rerun()
        else:
            blob, ext = st.session_state["cu_dl"]
            b4.download_button(f"⬇️ Download ({ext.upper()})", blob, file_name=f"{BRAND_FILE}_customers_{stamp}.{ext}",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if ext == "xlsx"
                               else "text/csv", **FULL_WIDTH)
        st.caption("The download is what's shown (filters applied), with every original column. Edit it in Excel and"
                   " upload it again to update the list.")
    if len(sel) == 1:
        st.session_state["cust_rid"] = sel[0]
    rid = st.session_state.get("cust_rid")
    if rid and rid in data and (len(sel) <= 1):
        render_record_editor(rid)


# ---------------- 📞 Caller ----------------
def render_caller_page() -> None:
    ss = st.session_state
    data = crm_get()
    today = now_uk().date()
    if not name_gate():
        return
    with st.expander("🎛 Who to call: " + seg_summary(seg_from_state("ca")) +
                     (f" · group: {ss['ca_group']}" if ss.get("ca_group") else ""), expanded=False):
        seg = render_segment_filters("ca", show_status=False)
        fut = st.toggle("Include call-backs that aren't due yet", key="ca_future")
    focus = [r for r in (ss.get("caller_focus") or []) if r in data]
    order = focus or caller_queue(data, seg, fut, crm_user())
    now_ = now_uk()
    due_n = sum(1 for rid in order if due_now(data[rid], now_))
    calls_today = sum(1 for r in data.values() if isinstance(r, dict) for c in calls_of(r)
                      if str(c.get("at", "")).startswith(today.isoformat()) and c.get("by") == crm_user()
                      and c.get("outcome") not in ("Note", "Edited", "Status changed"))
    appts_today = sum(1 for r in data.values() if isinstance(r, dict) for a in (r.get("appointments") or [])
                      if str(a.get("booked_at", "")).startswith(today.isoformat()) and a.get("booked_by") == crm_user())
    sh_hero('Caller <span>&amp; diary</span>', "One customer at a time. Ring, pick the outcome, and the next one is"
            " ready. Every call is saved for the team.",
            [(str(len(order)), "To call", "active"), (str(due_n), "Due today", ""), (str(calls_today), "Your calls today", "done"),
             (str(appts_today), "Booked today", "done")], f"Calling as {crm_user()}")
    flash()
    show_crm_error()
    later = sorted((r.get("next_time"), r) for r in data.values() if isinstance(r, dict) and r.get("next_time")
                   and to_date(r.get("next_action")) == today and not due_now(r, now_)
                   and (r.get("status") or "New") not in CLOSED)
    if later:
        t_, r_ = later[0]
        st.caption(f"⏰ Next timed call-back: **{t_}** {esc(rec_label(r_))}"
                   + (f" (+{len(later) - 1} more later today)" if len(later) > 1 else "")
                   + ". It joins the top of the list 10 minutes before.")
    if focus:
        st.info(f"Calling the {len(focus)} customer(s) you picked.")
        if st.button("Back to the full call list", key="ca_unfocus"):
            ss.pop("caller_focus", None)
            st.rerun()
    if ss.get("sh_local_prompt"):
        area_, rid_ = ss["sh_local_prompt"]
        if st.button(f"📍 Fill the diary near {area_}: see who else is nearby", type="primary", key="ca_local"):
            ss["local_area"] = area_
            ss.pop("sh_local_prompt", None)
            goto_view("local")
            st.rerun()
    rid = ss.get("caller_rid")
    if rid not in data or (rid not in order and not ss.get("caller_pin")):
        rid = order[0] if order else None
    ss.pop("caller_pin", None)
    if not rid:
        with st.container(key="card-sh-empty"):
            section_header("🎉", "Nothing to call right now",
                           "Everyone due has been called. Change 'Who to call', or upload more customers.")
        return
    ss["caller_rid"] = rid
    r = data[rid]
    pos = order.index(rid) + 1 if rid in order else 0
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        with st.container(key="card-sh-now"):
            section_header("▶", "Now calling", f"{pos} of {len(order)}" if pos else "Opened from the list")
            render_html(record_card_html(r) + phone_html(r))
            if r.get("next_note"):
                render_html(f'<div class="sh-line">📝 Next action: <b>{esc(r["next_note"])}</b></div>')
            if r.get("notes"):
                render_html(f'<div class="sh-line">🗒 {esc(r["notes"])}</div>')
            if r.get("extra"):
                with st.expander("More from the customer sheet"):
                    for k, v in list(r["extra"].items())[:30]:
                        st.markdown(f"**{esc(k)}:** {esc(v)}")
            if is_tps(r):
                st.warning("⛔ This number is on the TPS/CTPS register. Don't make an unsolicited sales call to it"
                           " unless they've agreed to hear from you. Tick 'OK to call' in the details below if they have.")
            notes = st.text_area("Notes from this call", key=f"ca_notes_{rid}", height=80,
                                 placeholder="Who you spoke to, what they said…")
            with st.expander("📝 What you found out: handsets, provider, contract end, contact",
                             expanded=not (r.get("handsets") or r.get("provider"))):
                k1, k2, k3 = st.columns(3)
                hs = k1.number_input("Handsets", min_value=0, step=1, value=int(to_num(r.get("handsets")) or 0),
                                     key=f"ca_hs_{rid}")
                prov = k2.text_input("Current provider", value=r.get("provider") or "", key=f"ca_prov_{rid}",
                                     placeholder="e.g. BT, Daisy")
                ce = k3.date_input("Their contract ends", value=to_date(r.get("contract_end")), format="DD/MM/YYYY",
                                   key=f"ca_ce_{rid}")
                k4, k5, k6 = st.columns(3)
                dm = k4.text_input("Decision maker", value=r.get("contact") or "", key=f"ca_dm_{rid}")
                em = k5.text_input("Email", value=r.get("email") or "", key=f"ca_emv_{rid}")
                ok_call = k6.checkbox("TPS: OK to call", value=bool(r.get("tps_ok")), key=f"ca_tpsok_{rid}",
                                      disabled=not r.get("tps"))
                if st.button("💾 Save details", key=f"ca_det_{rid}"):
                    latest = crm_get().get(rid) or r
                    upd = {**latest, "handsets": int(hs) or "", "provider": prov.strip(),
                           "contract_end": ce.isoformat() if ce else "", "contact": dm.strip() or latest.get("contact", ""),
                           "email": em.strip() or latest.get("email", ""), "tps_ok": bool(ok_call)}
                    crm_save({rid: upd}, f"details for {rec_label(r)}")
                    ss["sh_flash"] = f"💾 Saved details for {esc(rec_label(r))}."
                    ss["caller_pin"] = True
                    st.rerun()
            learned = {"handsets": int(hs) or None, "provider": prov.strip() or None,
                       "contract_end": ce.isoformat() if ce else None}
            render_html('<div class="sh-section">One click: outcome & next action</div>')
            nwd = next_working_day(today)
            o1, o2, o3 = st.columns(3)
            if o1.button("📵 No answer", key=f"ca_na_{rid}", **FULL_WIDTH, help=f"Try again {nwd.strftime('%a %d %b')}"):
                log_outcome(rid, "No answer", notes, fields=learned, next_action=nwd, status="No answer" if r.get("status") in (None, "", "New", "No answer") else None)
                ss["sh_flash"] = f"📵 No answer from {esc(rec_label(r))}: back on the list {nwd.strftime('%a %d %b')}."
                ss["caller_rid"] = None
                st.rerun()
            if o2.button("🔁 Tomorrow", key=f"ca_cb1_{rid}", **FULL_WIDTH, help=f"Call back {nwd.strftime('%a %d %b')}"):
                log_outcome(rid, "Call back", notes, next_action=nwd, status="Call back", fields=learned)
                ss["sh_flash"] = f"🔁 Call back {esc(rec_label(r))} on {nwd.strftime('%a %d %b')}."
                ss["caller_rid"] = None
                st.rerun()
            nxt_week = today + timedelta(days=(7 - today.weekday()) or 7)
            if o3.button("🔁 Next week", key=f"ca_cb7_{rid}", **FULL_WIDTH, help=f"Call back {nxt_week.strftime('%a %d %b')}"):
                log_outcome(rid, "Call back", notes, next_action=nxt_week, status="Call back", fields=learned)
                ss["sh_flash"] = f"🔁 Call back {esc(rec_label(r))} on {nxt_week.strftime('%a %d %b')}."
                ss["caller_rid"] = None
                st.rerun()
            d1, d0, d2 = st.columns([1, 0.7, 1.1])
            cb_date = d1.date_input("Call back on", value=next_working_day(today, 2), min_value=today,
                                    format="DD/MM/YYYY", key=f"ca_cbd_{rid}")
            cb_time = d0.selectbox("At", TIME_SLOTS, key=f"ca_cbt_{rid}", format_func=lambda t: t or "Any time")
            if d2.button("🔁 Call back then", key=f"ca_cbx_{rid}", **FULL_WIDTH):
                log_outcome(rid, "Call back", notes, next_action=cb_date, status="Call back", next_time=cb_time,
                            fields=learned)
                ss["sh_flash"] = f"🔁 Call back {esc(rec_label(r))} on {cb_date.strftime('%a %d %b')}" + \
                    (f" at {cb_time}." if cb_time else ".")
                ss["caller_rid"] = None
                st.rerun()
            render_html('<div class="sh-section">Appointment booked</div>')
            ap1, ap2, ap3 = st.columns([1, 0.8, 1])
            ap_date = ap1.date_input("Date", value=next_working_day(today, 2), min_value=today, format="DD/MM/YYYY",
                                     key=f"ca_apd_{rid}")
            ap_time = ap2.time_input("Time", value=dt_time(10, 0), step=900, key=f"ca_apt_{rid}")
            ap_kind = ap3.selectbox("Type", ["On site visit", "Phone call", "Video call", "At our office"], key=f"ca_apk_{rid}")
            aw1, aw2 = st.columns(2)
            ap_with = aw1.text_input("Meeting with", value=r.get("contact") or "", key=f"ca_apw_{rid}")
            ap_rep = rep_picker(aw2, "Sales rep going", key=f"ca_aprep_{rid}")
            if st.button("📅 Appointment booked", key=f"ca_ap_{rid}", type="primary", **FULL_WIDTH):
                at = datetime.combine(ap_date, ap_time).replace(tzinfo=UK_TZ).isoformat(timespec="minutes")
                log_outcome(rid, "Appointment booked", notes, next_action=ap_date, status="Appointment", fields=learned,
                            appt={"at": at, "kind": ap_kind, "with": ap_with.strip(), "notes": notes.strip(),
                                  "rep": ap_rep})
                area_ = pc_district(r.get("postcode") or "") or (r.get("town") or "")
                ss["sh_flash"] = (f"📅 Booked: {esc(rec_label(r))}, {ap_date.strftime('%a %d %b')} at"
                                  f" {ap_time.strftime('%H:%M')} ({esc(ap_kind.lower())}).")
                if area_:
                    ss["sh_local_prompt"] = (area_, rid)
                ss["caller_rid"] = None
                st.rerun()
            render_html('<div class="sh-section">Other outcomes</div>')
            y1, y2 = st.columns(2)
            if y1.button("📆 In contract: call before it ends", key=f"ca_inc_{rid}", **FULL_WIDTH,
                         disabled=not ce, help="Fill in 'Their contract ends' above first. We'll call back 3 months before."):
                back = max(next_working_day(today, 5), ce - timedelta(days=90))
                log_outcome(rid, "In contract", notes, next_action=back, status="Call back", fields=learned)
                ss["sh_flash"] = (f"📆 {esc(rec_label(r))} is in contract until {ce.strftime('%b %Y')}: back on the"
                                  f" list {back.strftime('%a %d %b %Y')}.")
                ss["caller_rid"] = None
                st.rerun()
            if y2.button("☎️ Wrong / dead number", key=f"ca_bad_{rid}", **FULL_WIDTH,
                         help="Takes it off the call list. Find a new number with Enrich on the Customers page."):
                log_outcome(rid, "Wrong number", notes, status="Bad number", clear_next=True, fields=learned)
                ss["sh_flash"] = f"☎️ {esc(rec_label(r))} marked as a bad number."
                ss["caller_rid"] = None
                st.rerun()
            x1, x2, x3, x4 = st.columns([1.25, 1, 1, 0.75])
            if x1.button("👎 Not interested", key=f"ca_ni_{rid}", **FULL_WIDTH):
                log_outcome(rid, "Not interested", notes, status="Not interested", clear_next=True, fields=learned)
                ss["sh_flash"] = f"👎 {esc(rec_label(r))} marked not interested."
                ss["caller_rid"] = None
                st.rerun()
            if x2.button("🚫 Do not call", key=f"ca_dnc_{rid}", **FULL_WIDTH, help="Wrong number, or asked not to be called"):
                log_outcome(rid, "Do not call", notes, status="Do not call", clear_next=True, fields=learned)
                ss["sh_flash"] = f"🚫 {esc(rec_label(r))} won't be called again."
                ss["caller_rid"] = None
                st.rerun()
            if x3.button("✉️ Email info", key=f"ca_em_{rid}", disabled=not r.get("email"), **FULL_WIDTH,
                         help="Logs the call, then opens the pitch email and PDF ready to send via Zoho"):
                log_outcome(rid, "Asked for info", notes, next_action=next_working_day(today, 3), status="Call back",
                            fields=learned)
                to_queue_for_email(rid)
                st.rerun()
            if x4.button("⏭ Skip", key=f"ca_skip_{rid}", **FULL_WIDTH, help="Move on without logging anything"):
                nxt = order[(order.index(rid) + 1) % len(order)] if rid in order and len(order) > 1 else None
                ss["caller_rid"] = nxt
                ss["caller_pin"] = True
                st.rerun()
            with st.expander("💷 Sold on the phone"):
                deal = deal_inputs(f"ca_deal_{rid}", r)
                if st.button("💷 Save as sold", key=f"ca_won_{rid}", type="primary"):
                    log_outcome(rid, "Won", notes, status="Won", deal=deal, clear_next=True, fields=learned)
                    ss["sh_flash"] = f"💷 Won: {esc(rec_label(r))}, {money(deal['mrr'])}/month over {deal['term']} months" + \
                        (f" + {money(deal['one_off'])} one-off." if deal["one_off"] else ".")
                    ss["caller_rid"] = None
                    st.rerun()
    with right:
        with st.container(key="card-sh-side"):
            section_header("≡", "History", "Everything logged for this customer")
            render_html(history_html(r, 10))
            ap = next_appt(r)
            if ap:
                render_html(f'<div class="sh-line" style="margin-top:10px">📅 Next appointment: <b>'
                            f'{esc((_when(ap["at"]) or now_uk()).strftime("%a %d %b, %H:%M"))}</b> · {esc(ap.get("kind") or "")}</div>')
            if st.button("✏️ Edit this customer", key=f"ca_edit_{rid}", **FULL_WIDTH):
                ss["cust_rid"] = rid
                goto_view("customers")
                st.rerun()
        with st.container(key="card-sh-next"):
            section_header("→", "Coming up", "The next few on your list")
            nxt = [x for x in order if x != rid][:6]
            for x in nxt:
                rx = data[x]
                nd = to_date(rx.get("next_action"))
                lbl = f"{rec_label(rx)}  ·  {rx.get('town') or rx.get('postcode') or ''}" + (
                    f"  ·  due {nd.strftime('%d %b')}" if nd else "") + (f" {rx['next_time']}" if rx.get("next_time") else "")
                if st.button(lbl, key=f"ca_jump_{x}", **FULL_WIDTH):
                    ss["caller_rid"] = x
                    ss["caller_pin"] = True
                    st.rerun()
            if not nxt:
                st.caption("That's the last one.")


# ---------------- 📍 Local hit list ----------------
def area_match(r: Dict[str, Any], area: str) -> bool:
    a = area.strip()
    if not a:
        return False
    au = a.upper().replace(" ", "")
    pc = norm_pc(r.get("postcode") or "")
    if re.match(r"^[A-Z]{1,2}\d[A-Z\d]?$", au):  # District, e.g. CF10
        return pc_district(pc) == au
    if re.match(r"^[A-Z]{1,2}$", au):  # Area, e.g. CF
        return pc_area(pc) == au
    return a.lower() in (r.get("town") or "").lower() or a.lower() in (r.get("address") or "").lower()


def render_local_page() -> None:
    ss = st.session_state
    data = crm_get()
    today = now_uk().date()
    sh_hero('Local <span>hit list</span>', "Booked an appointment? Fill the diary around it: who else on your list is"
            " nearby, plus new local firms from Companies House.", [], "Plan the day around the visit")
    flash()
    show_crm_error()
    with st.container(key="card-sh-area"):
        section_header("01", "Area", "A postcode district (CF10), postcode area (CF) or a town name.")
        a1, a2 = st.columns([1.3, 1])
        area = a1.text_input("Area", key="local_area", placeholder="e.g. CF10, NP20 or Bridgend").strip()
        recent_days = a2.selectbox("Leave out anyone called in the last", [0, 3, 7, 14], index=2, key="local_recent",
                                   format_func=lambda d: "Show everyone" if d == 0 else f"{d} days")
        if not area:
            st.caption("Type an area, or book an appointment in the Caller and press 'Fill the diary'.")
            return
        near = []
        appts = []
        for r in data.values():
            if not isinstance(r, dict) or not area_match(r, area):
                continue
            ap = next_appt(r)
            if ap:
                appts.append((ap, r))
            if (r.get("status") or "New") in CLOSED:
                continue
            lc = last_call(r)
            if recent_days and lc and (_when(lc.get("at")) or datetime.min.replace(tzinfo=UK_TZ)) > now_uk() - timedelta(days=recent_days):
                continue
            near.append(r)
        if appts:
            render_html('<div class="sh-section">Appointments in this area</div>' + "".join(
                f'<div class="sh-line">📅 <b>{esc((_when(ap["at"]) or now_uk()).strftime("%a %d %b %H:%M"))}</b> · '
                f'{esc(rec_label(r))} · {esc(r.get("postcode") or r.get("town") or "")}</div>'
                for ap, r in sorted(appts, key=lambda x: x[0]["at"])))
    with st.container(key="card-sh-near"):
        section_header("02", "On your list nearby", f"{len(near)} customer(s) in {area} worth a call. Tick and call.")
        if near:
            order = {"New": 0, "Call back": 1, "No answer": 2, "Quoted": 3, "Appointment": 4}
            near.sort(key=lambda r: (order.get(r.get("status") or "New", 5), norm_pc(r.get("postcode") or ""), rec_label(r)))
            df = pd.DataFrame([{"id": r["id"], "Company": rec_label(r), "Contact": r.get("contact") or "",
                                "Phone": r.get("phone") or r.get("mobile") or "", "Postcode": r.get("postcode") or "",
                                "Town": r.get("town") or "", "Status": r.get("status") or "New",
                                "Last call": (last_call(r) or {}).get("at", "")[:10]} for r in near])
            common = dict(hide_index=True, selection_mode="multi-row", on_select="rerun",
                          column_order=["Company", "Contact", "Phone", "Postcode", "Town", "Status", "Last call"],
                          height=min(38 + 35 * len(df), 420), key=f"lo_near_{area}_{ss.get('crm_ver', 0)}")
            try:
                ev = st.dataframe(df, width="stretch", **common)
            except TypeError:
                ev = st.dataframe(df, use_container_width=True, **common)
            picked = [near[i]["id"] for i in (ev.selection.rows if ev else []) if i < len(near)]
            if st.button(f"📞 Call {len(picked) if picked else 'all ' + str(len(near))} now", type="primary",
                         key="lo_call", **FULL_WIDTH):
                ss["caller_focus"] = picked or [r["id"] for r in near]
                open_in_caller(ss["caller_focus"][0])
                st.rerun()
        else:
            st.caption("Nobody else on your list in this area yet: find new local firms below.")
    with st.container(key="card-sh-new"):
        section_header("03", "New local firms", "Live from Companies House. Add the ones you like to the list, then call.")
        n1, n2, n3 = st.columns([1.2, 1.4, 0.8])
        town_guess = next((r.get("town") for r in data.values() if isinstance(r, dict) and r.get("town") and area_match(r, area)), "")
        where = n1.text_input("Town or postcode for the search", value=town_guess or area, key=f"lo_where_{area}")
        sector = n2.selectbox("Sector", [ALL_SECTORS] + sorted(VERTICAL_PRESETS), key="lo_sector",
                              help="'All our sectors' searches every sector we have a pitch for at once.")
        limit = n3.selectbox("Results", [25, 50, 100], key="lo_limit")
        if st.button("🔎 Find local firms", key="lo_find", **FULL_WIDTH):
            key = ch_api_key if "ch_api_key" in globals() else secret_ch_key
            if not key:
                st.error("Companies House key missing: add COMPANIES_HOUSE_KEY to Secrets.")
            else:
                with st.spinner("Searching Companies House…"):
                    codes = (sorted({c for v in VERTICAL_PRESETS.values() for c in v.get("sic_codes") or []})
                             if sector == ALL_SECTORS else VERTICAL_PRESETS[sector]["sic_codes"])
                    res, err = LeadEnricher(ch_api_key=key).browse_vertical(
                        sic_codes=codes, location_keyword=where, limit=limit)
                if err:
                    st.error(err)
                ss["lo_results"] = res or []
                ss["lo_results_for"] = (where, sector)
        res = ss.get("lo_results") or []
        if res:
            idx = crm_index(data)
            fresh = [x for x in res if str(x.get("Company Number", "")).upper() not in idx["num"]
                     and norm_company(x.get("Company Name", "")) not in idx["co"]]
            st.caption(f"{len(res)} found for {esc(ss.get('lo_results_for', ('', ''))[1])} in"
                       f" {esc(ss.get('lo_results_for', ('', ''))[0])} · {len(res) - len(fresh)} already on your list.")
            if fresh:
                df = pd.DataFrame([{"Company": friendly_company_name(x["Company Name"]), "Where": x.get("Town / Postcode", ""),
                                    "Since": x.get("Incorporated", ""), "Number": x.get("Company Number", "")} for x in fresh])
                common = dict(hide_index=True, selection_mode="multi-row", on_select="rerun",
                              height=min(38 + 35 * len(df), 420), key=f"lo_new_{len(res)}_{ss.get('crm_ver', 0)}")
                try:
                    ev2 = st.dataframe(df, width="stretch", **common)
                except TypeError:
                    ev2 = st.dataframe(df, use_container_width=True, **common)
                chosen = [fresh[i] for i in (ev2.selection.rows if ev2 else []) if i < len(fresh)]
                c1, c2 = st.columns(2)
                enrich_too = c2.toggle("Enrich them straight away (finds phone, email, website)", value=True, key="lo_enrich")
                if c1.button(f"➕ Add {len(chosen) or 'the'} {'selected' if chosen else 'ticked'} to the list", type="primary",
                             disabled=not chosen, key="lo_add", **FULL_WIDTH):
                    stamp = now_uk().isoformat(timespec="seconds")
                    changes = {}
                    for x in chosen[:MAX_BATCH]:
                        rid = new_id()
                        loc = x.get("Town / Postcode", "")
                        town = loc.split(",")[0].strip() if "," in loc else ""
                        pc = loc.split(",")[-1].strip() if "," in loc else loc
                        changes[rid] = {"id": rid, "company": x["Company Name"], "company_number": x.get("Company Number"),
                                        "town": town, "postcode": pc if UK_POSTCODE_RE.match(pc or "") else "",
                                        "sector": "" if sector == ALL_SECTORS else sector, "status": "New",
                                        "calls": [], "created_at": stamp,
                                        "created_by": crm_user(), "source": f"Local search: {where}", "owner": crm_user()}
                    crm_save(changes, f"{len(changes)} added from local search")
                    msg = f"➕ Added {len(changes)} local firm(s) to the list."
                    if enrich_too:
                        n, fails = enrich_records(list(changes))
                        msg += f" Enriched {n}."
                    ss["sh_flash"] = msg
                    ss["lo_results"] = []
                    st.rerun()
                st.caption("Tick firms, then add them. Enriched firms with a phone number join the Caller straight away.")
            else:
                st.caption("Everything found is already on your list. Try another sector.")


# ---------------- 📈 Overview (management) ----------------
def render_overview_page() -> None:
    data = crm_get()
    recs = [r for r in data.values() if isinstance(r, dict)]
    now = now_uk()
    today = now.date()
    sh_hero('Management <span>overview</span>', "Pipeline, calls, appointments, deals and revenue, live from the list.",
            [], f"Updated {now.strftime('%a %d %b, %H:%M')}")
    show_crm_error()
    if not recs:
        st.info("Nothing to report yet: upload your customer list on the Customers page.")
        return
    period = st.radio("Period", ["Today", "This week", "This month", "Last 30 days", "This year", "All time"], index=2,
                      horizontal=True, key="ov_period", label_visibility="collapsed")
    start = {"Today": today, "This week": today - timedelta(days=today.weekday()), "This month": today.replace(day=1),
             "Last 30 days": today - timedelta(days=29), "This year": today.replace(month=1, day=1),
             "All time": date(2000, 1, 1)}[period]
    in_p = lambda iso: bool(iso) and (to_date(str(iso)[:10]) or date.min) >= start  # noqa: E731
    render_funnel(recs, start, period)

    calls = [dict(c, rid=r["id"], company=rec_label(r)) for r in recs for c in calls_of(r)
             if c.get("outcome") not in ("Note", "Edited", "Status changed") and c.get("by") != "Old sheet"]
    calls_p = [c for c in calls if in_p(c.get("at"))]
    appts = [dict(a, rid=r["id"], company=rec_label(r), town=r.get("town") or "", postcode=r.get("postcode") or "")
             for r in recs for a in (r.get("appointments") or []) if isinstance(a, dict)]
    booked_p = [a for a in appts if in_p(a.get("booked_at"))]
    won = [r for r in recs if r.get("status") in SOLD]
    won_p = [r for r in won if in_p((r.get("deal") or {}).get("won_at"))]
    mrr_p = sum(deal_values(r)[0] for r in won_p)
    one_p = sum(deal_values(r)[1] for r in won_p)
    tcv_p = sum(deal_values(r)[3] for r in won_p)
    live = []
    for r in won:
        d = r.get("deal") or {}
        wd, term = to_date(d.get("won_at")), int(to_num(d.get("term")) or 0)
        end = (pd.Timestamp(wd) + pd.DateOffset(months=term)).date() if wd and term else None
        if not end or end >= today:
            live.append((r, end))
    ongoing = sum(deal_values(r)[0] for r, _ in live)
    open_pipe = [r for r in recs if (r.get("status") or "New") not in CLOSED]
    upcoming = [a for a in appts if not a.get("cancelled") and (_when(a.get("at")) or datetime.min.replace(tzinfo=UK_TZ)) >= now - timedelta(hours=2)]
    conv = (len(won_p) / len(booked_p) * 100) if booked_p else None

    kpis([(f"{len(calls_p):,}", "Calls", period.lower(), "#60A5FA"),
          (f"{len(booked_p):,}", "Appointments booked", f"{len(upcoming)} coming up", "#34D399"),
          (f"{len(won_p):,}", "Deals won", (f"{conv:.0f}% of appointments" if conv is not None else period.lower()), "#F0645A"),
          (money(mrr_p), "New monthly revenue", f"{money(tcv_p)} total contract value", "#FBBF24")], 4)
    kpis([(money(ongoing), "Ongoing monthly revenue", f"{len(live)} live contract(s)", "#FBBF24"),
          (money(ongoing * 12), "Annual run rate", "ongoing × 12", "#FBBF24"),
          (money(one_p), "One-off value", period.lower(), "#A78BFA"),
          (f"{len(open_pipe):,}", "Open pipeline", f"{len(recs):,} on the list", "#60A5FA")], 4)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(key="card-sh-ch1"):
            section_header("01", "Calls per day", "Last 14 days, by person")
            days = [today - timedelta(days=i) for i in range(13, -1, -1)]
            people = sorted({c.get("by") or "Unknown" for c in calls}) or ["Unknown"]
            grid = []
            for d in days:
                for p in people:
                    grid.append({"Day": d.strftime("%a %d"), "Person": p,
                                 "Calls": sum(1 for c in calls if str(c.get("at", ""))[:10] == d.isoformat()
                                              and (c.get("by") or "Unknown") == p)})
            try:
                import altair as alt
                ch = (alt.Chart(pd.DataFrame(grid)).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                      .encode(x=alt.X("Day:N", sort=[d.strftime("%a %d") for d in days], title=None,
                                      axis=alt.Axis(labelAngle=0, labelColor="#8C98B0")),
                              y=alt.Y("Calls:Q", title=None, axis=alt.Axis(labelColor="#8C98B0", gridColor="#1F2A40", tickMinStep=1)),
                              color=alt.Color("Person:N", legend=alt.Legend(orient="top", title=None, labelColor="#E7EAF3")),
                              tooltip=["Day", "Person", "Calls"])
                      .properties(height=230, background="transparent").configure_view(strokeWidth=0))
                st.altair_chart(ch, **FULL_WIDTH)
            except Exception:
                st.bar_chart(pd.DataFrame(grid).pivot(index="Day", columns="Person", values="Calls"))
    with c2:
        with st.container(key="card-sh-ch2"):
            section_header("02", "New monthly revenue won", "Last 12 months, by the month won")
            months = [(pd.Timestamp(today.replace(day=1)) - pd.DateOffset(months=i)).date() for i in range(11, -1, -1)]
            rows = []
            for m in months:
                rs = [r for r in won if (to_date((r.get("deal") or {}).get("won_at")) or date.min).strftime("%Y-%m") == m.strftime("%Y-%m")]
                rows.append({"Month": m.strftime("%b %y"), "Monthly revenue": sum(deal_values(r)[0] for r in rs),
                             "Deals": len(rs)})
            try:
                import altair as alt
                ch2 = (alt.Chart(pd.DataFrame(rows)).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#F0645A")
                       .encode(x=alt.X("Month:N", sort=[m.strftime("%b %y") for m in months], title=None,
                                       axis=alt.Axis(labelAngle=0, labelColor="#8C98B0")),
                               y=alt.Y("Monthly revenue:Q", title=None, axis=alt.Axis(labelColor="#8C98B0", gridColor="#1F2A40", format="~s")),
                               tooltip=["Month", alt.Tooltip("Monthly revenue:Q", format=",.0f"), "Deals"])
                       .properties(height=230, background="transparent").configure_view(strokeWidth=0))
                st.altair_chart(ch2, **FULL_WIDTH)
            except Exception:
                st.bar_chart(pd.DataFrame(rows).set_index("Month")["Monthly revenue"])

    with st.container(key="card-sh-pipe"):
        section_header("03", "Pipeline", "Where every customer on the list sits now")
        counts = {s_: sum(1 for r in recs if (r.get("status") or "New") == s_) for s_ in PIPELINE}
        kpis([(f"{counts[s_]:,}", s_, "", "") for s_ in PIPELINE], 5)

    with st.container(key="card-sh-team"):
        section_header("04", "Team", f"Who did what · {period.lower()}")
        people = sorted({c.get("by") for c in calls_p if c.get("by")} | {a.get("booked_by") for a in booked_p if a.get("booked_by")}
                        | {(r.get("deal") or {}).get("won_by") for r in won_p if (r.get("deal") or {}).get("won_by")})
        team = []
        for p in people:
            wp = [r for r in won_p if (r.get("deal") or {}).get("won_by") == p]
            team.append({"Person": p, "Calls": sum(1 for c in calls_p if c.get("by") == p),
                         "Appointments": sum(1 for a in booked_p if a.get("booked_by") == p),
                         "Deals won": len(wp), "New monthly (£)": round(sum(deal_values(r)[0] for r in wp), 2),
                         "One-off (£)": round(sum(deal_values(r)[1] for r in wp), 2),
                         "Contract value (£)": round(sum(deal_values(r)[3] for r in wp), 2)})
        if team:
            st.dataframe(pd.DataFrame(team), hide_index=True, **FULL_WIDTH,
                         column_config={k: st.column_config.NumberColumn(k, format="£%.0f")
                                        for k in ("New monthly (£)", "One-off (£)", "Contract value (£)")})
        else:
            st.caption("No activity in this period yet.")

    t1, t2 = st.columns(2)
    with t1:
        with st.container(key="card-sh-appts"):
            section_header("05", "Upcoming appointments", "Next 14 days")
            ups = sorted([a for a in upcoming if (_when(a["at"]) or now) <= now + timedelta(days=14)], key=lambda a: a["at"])
            if ups:
                st.dataframe(pd.DataFrame([{"When": (_when(a["at"]) or now).strftime("%a %d %b %H:%M"), "Company": a["company"],
                                            "Where": " ".join(x for x in (a["town"], a["postcode"]) if x),
                                            "Type": a.get("kind") or "", "With": a.get("with") or "",
                                            "Booked by": a.get("booked_by") or ""} for a in ups]), hide_index=True, **FULL_WIDTH)
            else:
                st.caption("No appointments in the next 14 days.")
    with t2:
        with st.container(key="card-sh-overdue"):
            section_header("06", "Overdue follow-ups", "Next action date has passed")
            od = sorted([r for r in open_pipe if (to_date(r.get("next_action")) or date.max) < today],
                        key=lambda r: to_date(r.get("next_action")))
            if od:
                st.dataframe(pd.DataFrame([{"Due": to_date(r["next_action"]).strftime("%d %b"), "Company": rec_label(r),
                                            "Status": r.get("status") or "New", "Owner": r.get("owner") or "",
                                            "Note": r.get("next_note") or ""} for r in od[:200]]), hide_index=True, **FULL_WIDTH)
            else:
                st.caption("Nothing overdue. 👏")

    with st.container(key="card-sh-deals"):
        section_header("07", "Won deals & renewals", "Every won deal, with its contract end date")
        if won:
            rows = []
            for r in sorted(won, key=lambda r: (r.get("deal") or {}).get("won_at", ""), reverse=True):
                mrr, one, term, tcv = deal_values(r)
                wd = to_date((r.get("deal") or {}).get("won_at"))
                end = (pd.Timestamp(wd) + pd.DateOffset(months=term)).date() if wd and term else None
                rows.append({"Company": rec_label(r), "Won on": wd.strftime("%d %b %Y") if wd else "",
                             "Monthly (£)": mrr, "One-off (£)": one, "Term (months)": term, "Contract value (£)": tcv,
                             "Ends": end.strftime("%b %Y") if end else "", "Renewal due": "⚠️ within 6 months"
                             if end and today <= end <= today + timedelta(days=183) else ("Ended" if end and end < today else ""),
                             "Won by": (r.get("deal") or {}).get("won_by") or r.get("owner") or ""})
            ddf = pd.DataFrame(rows)
            st.dataframe(ddf, hide_index=True, **FULL_WIDTH,
                         column_config={k: st.column_config.NumberColumn(k, format="£%.2f")
                                        for k in ("Monthly (£)", "One-off (£)", "Contract value (£)")})
            xl = to_xlsx(ddf, "Won deals")
            if xl:
                st.download_button("⬇️ Download won deals (Excel)", xl, file_name=f"{BRAND_FILE}_won_deals_{today}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.caption("No deals won yet. Use 💷 Deal won in the Caller, or set a customer to Won on the Customers page.")
        acts = pd.DataFrame([{"When": str(c.get("at", ""))[:16].replace("T", " "), "Company": c["company"],
                              "Outcome": c.get("outcome"), "Notes": c.get("notes") or "", "By": c.get("by") or ""}
                             for c in sorted(calls, key=lambda c: c.get("at", ""), reverse=True)])
        if not acts.empty:
            xl2 = to_xlsx(acts, "Call log")
            if xl2:
                st.download_button("⬇️ Download the full call log (Excel)", xl2, file_name=f"{BRAND_FILE}_call_log_{today}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def add_queue_to_crm(cns: List[str]) -> Tuple[int, int]:
    """Prospecting → the customer list: adds enriched firms that aren't on it yet. Returns (added, already there)."""
    queue_ = st.session_state.get("queue", {})
    data = dict(crm_get())
    idx = crm_index(data)
    changes, there = {}, 0
    stamp = now_uk().isoformat(timespec="seconds")
    for cn in cns:
        item = queue_.get(cn)
        if not item or str(cn).startswith("crm:"):
            continue
        lead: ScrapedLead = item["lead"]
        contact, role = infer_contact_name_and_role(lead, item["vertical"])
        addr = lead.registered_address or ""
        m = UK_POSTCODE_RE.search(addr.split(",")[-1].strip()) if addr else None
        row = {"company": lead.company_name, "company_number": lead.company_number, "email": item.get("to") or "",
               "phone": (lead.phones_found or [""])[0], "postcode": addr.split(",")[-1].strip() if m else ""}
        if find_match(row, data, idx):
            there += 1
            continue
        rid = new_id()
        rec = {"id": rid, "company": lead.company_name, "trading_name": lead.trading_name or "",
               "company_number": lead.company_number or "", "contact": "" if contact in ("Team", "there") else contact,
               "role": role or "", "email": item.get("to") or "", "phone": (lead.phones_found or [""])[0],
               "mobile": next((p for p in lead.phones_found[1:] if p.startswith("07")), ""), "website": lead.website_url or "",
               "address": ", ".join(addr.split(",")[:-2]) if addr.count(",") >= 2 else addr,
               "town": addr.split(",")[-2].strip() if addr.count(",") >= 1 else "", "postcode": row["postcode"],
               "sector": item.get("base_vertical") or item["vertical"], "status": "New", "calls": [],
               "created_at": stamp, "created_by": crm_user(), "source": "Prospecting", "owner": crm_user(),
               "other_emails": [e_ for e_ in lead.emails_found if e_ != item.get("to")][:5]}
        data[rid] = rec
        changes[rid] = rec
        idx = crm_index(data)
    if changes:
        crm_save(changes, f"{len(changes)} added from Prospecting")
    return len(changes), there


# ==========================================================================================
# GROUPS: find a slice of the list in a few clicks (area, staff, credit, lease end…) and save it to reuse
# ==========================================================================================
GROUP_STORE = SentLog("GITHUB_GROUPS_PATH", "groups.json", ".sales_hub_groups.json")
LEASE_BANDS = ["Ended 12+ months ago", "Ended in the last 12 months", "Ends in the next 6 months",
               "Ends in 6-12 months", "Ends in 12+ months", "No end date"]
TPS_OPTS = ["Leave out TPS / CTPS numbers", "Include them", "Only TPS / CTPS"]
OWNER_OPTS = ["Anyone", "Mine", "Unassigned"]
SEG_DEFAULT: Dict[str, Any] = {
    "q": "", "status": [], "areas": [], "district": "", "regions": [], "sectors": [], "emp": [], "credit": [],
    "lease": [], "markets": [], "assets": [], "lines": [], "tags": [], "sources": [], "handsets_min": 0,
    "tps": TPS_OPTS[0], "trading_only": True, "owner": OWNER_OPTS[0], "gaps": False,
}


def end_date_of(r: Dict[str, Any]) -> Optional[date]:
    """Their phone contract end if the caller has found it out, otherwise the lease end from the data."""
    return to_date(r.get("contract_end")) or to_date(r.get("lease_end"))


def lease_band(r: Dict[str, Any], today: date) -> str:
    d = end_date_of(r)
    if not d:
        return LEASE_BANDS[5]
    days = (d - today).days
    if days < -365:
        return LEASE_BANDS[0]
    if days < 0:
        return LEASE_BANDS[1]
    if days <= 183:
        return LEASE_BANDS[2]
    if days <= 365:
        return LEASE_BANDS[3]
    return LEASE_BANDS[4]


def is_tps(r: Dict[str, Any]) -> bool:
    return bool(r.get("tps")) and not r.get("tps_ok")


@st.cache_data(show_spinner=False, max_entries=4)
def _seg_options(sig: Tuple[Any, ...], _data: Dict[str, Any]) -> Dict[str, List[Tuple[str, int]]]:
    """Every value in the list for each filter, with how many records have it (cached until the list changes)."""
    from collections import Counter
    c: Dict[str, Counter] = {k: Counter() for k in ("areas", "regions", "sectors", "markets", "assets", "lines",
                                                     "tags", "sources")}
    for r in _data.values():
        if not isinstance(r, dict):
            continue
        a = pc_area(r.get("postcode") or "")
        if a:
            c["areas"][a] += 1
        for k, f in (("regions", "region"), ("sectors", "sector"), ("markets", "lease_market"),
                     ("assets", "lease_asset"), ("lines", "line_type"), ("sources", "source")):
            if r.get(f):
                c[k][str(r[f])] += 1
        for t in r.get("tags") or []:
            c["tags"][t] += 1
    return {k: sorted(v.items(), key=lambda kv: (-kv[1], kv[0])) for k, v in c.items()}


def seg_options() -> Dict[str, List[Tuple[str, int]]]:
    data = crm_get()
    return _seg_options((st.session_state.get("crm_sig"), len(data), st.session_state.get("crm_ver", 0)), data)


def seg_match(r: Dict[str, Any], seg: Dict[str, Any], today: date, me: str = "") -> bool:
    st_ = r.get("status") or "New"
    if seg.get("status") and st_ not in seg["status"]:
        return False
    if seg.get("trading_only") and r.get("trading_ok") is False:
        return False
    tps = seg.get("tps") or TPS_OPTS[0]
    if tps == TPS_OPTS[0] and is_tps(r):
        return False
    if tps == TPS_OPTS[2] and not is_tps(r):
        return False
    if seg.get("areas") and pc_area(r.get("postcode") or "") not in seg["areas"]:
        return False
    if seg.get("district"):
        parts = [p.strip() for p in re.split(r"[,;]", seg["district"]) if p.strip()]
        if parts and not any(area_match(r, p) or norm_pc(r.get("postcode") or "").startswith(p.upper().replace(" ", ""))
                             for p in parts):
            return False
    for k, f in (("regions", "region"), ("sectors", "sector"), ("markets", "lease_market"), ("assets", "lease_asset"),
                 ("lines", "line_type"), ("sources", "source")):
        if seg.get(k) and str(r.get(f) or "") not in seg[k]:
            return False
    if seg.get("tags") and not set(seg["tags"]) & set(r.get("tags") or []):
        return False
    if seg.get("emp") and emp_band(r.get("employees")) not in seg["emp"]:
        return False
    if seg.get("credit") and (credit_band(r.get("credit_rating")) or "Not rated") not in seg["credit"]:
        return False
    if seg.get("lease") and lease_band(r, today) not in seg["lease"]:
        return False
    if seg.get("handsets_min") and int(to_num(r.get("handsets")) or 0) < int(seg["handsets_min"]):
        return False
    own = seg.get("owner") or "Anyone"
    if own == "Mine" and (r.get("owner") or "") != me:
        return False
    if own == "Unassigned" and r.get("owner"):
        return False
    if seg.get("gaps") and (r.get("email") and (r.get("phone") or r.get("mobile"))):
        return False
    q = (seg.get("q") or "").strip().lower()
    if q:
        hay = " ".join(str(r.get(k) or "") for k in ("company", "trading_name", "contact", "phone", "mobile", "ho_phone",
                                                     "email", "town", "postcode", "notes", "sector", "company_number",
                                                     "provider", "lease_supplier")).lower()
        if q not in hay and _n(q) not in _n(hay):
            return False
    return True


def _seg_key(prefix: str, k: str) -> str:
    return f"{prefix}_seg_{k}"


def seg_from_state(prefix: str) -> Dict[str, Any]:
    ss = st.session_state
    return {k: ss.get(_seg_key(prefix, k), v) for k, v in SEG_DEFAULT.items()}


def _load_group(prefix: str) -> None:
    ss = st.session_state
    name = ss.get(f"{prefix}_group")
    groups = GROUP_STORE.load() if name else {}
    seg = dict(SEG_DEFAULT, **((groups.get(name) or {}).get("seg") or {})) if name else dict(SEG_DEFAULT)
    for k, v in seg.items():
        ss[_seg_key(prefix, k)] = v


def seg_summary(seg: Dict[str, Any]) -> str:
    bits = []
    for k, lbl in (("areas", ""), ("regions", ""), ("emp", "staff "), ("credit", "credit "), ("lease", ""),
                   ("markets", ""), ("assets", ""), ("lines", ""), ("sectors", ""), ("tags", ""), ("status", "")):
        if seg.get(k):
            bits.append(lbl + ", ".join(seg[k][:4]) + ("…" if len(seg[k]) > 4 else ""))
    if seg.get("district"):
        bits.append(seg["district"])
    if seg.get("handsets_min"):
        bits.append(f"{seg['handsets_min']}+ handsets")
    if seg.get("q"):
        bits.append(f'"{seg["q"]}"')
    return " · ".join(bits) or "Everyone"


def render_segment_filters(prefix: str, show_status: bool = True, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The filter panel used on Customers and the Caller. Returns the chosen filters."""
    ss = st.session_state
    for k, v in dict(SEG_DEFAULT, **(defaults or {})).items():
        ss.setdefault(_seg_key(prefix, k), v)
    opts = seg_options()
    fmt = lambda pairs: {k: f"{k}  ({n:,})" for k, n in pairs}  # noqa: E731
    groups = GROUP_STORE.load()
    names = sorted(groups)
    g1, g2, g3 = st.columns([1.3, 1.6, 1.3])
    g1.selectbox("Saved group", [""] + names, key=f"{prefix}_group", on_change=_load_group, args=(prefix,),
                 format_func=lambda n: n or "— Everyone (no group) —",
                 help="Pick a saved group to load its filters. Save the current filters as a group below.")
    g2.text_input("Search", key=_seg_key(prefix, "q"), placeholder="Company, contact, phone, postcode, supplier…")
    am = fmt(opts["areas"])
    g3.multiselect("Postcode area", [a for a, _ in opts["areas"]], key=_seg_key(prefix, "areas"),
                   format_func=lambda a: am.get(a, a), placeholder="e.g. CF, NP, SA")
    h1, h2, h3, h4 = st.columns(4)
    h1.multiselect("Staff", [b for b, _, _ in EMP_BANDS] + ["Unknown"], key=_seg_key(prefix, "emp"), placeholder="Any size")
    h2.multiselect("Lease / contract end", LEASE_BANDS, key=_seg_key(prefix, "lease"), placeholder="Any")
    h3.multiselect("Credit", [b for b, *_ in CREDIT_BANDS] + ["Not rated"], key=_seg_key(prefix, "credit"),
                   format_func=lambda b: next((f"{b} · {d}" for x, _, _, d in CREDIT_BANDS if x == b), b), placeholder="Any")
    if show_status:
        h4.multiselect("Status", PIPELINE, key=_seg_key(prefix, "status"), placeholder="Any")
    else:
        h4.selectbox("Whose", OWNER_OPTS, key=_seg_key(prefix, "owner"))
    with st.expander("More filters: region, town, sector, equipment, phone line, tags…"):
        m1, m2, m3 = st.columns(3)
        rm = fmt(opts["regions"])
        m1.multiselect("Region", [a for a, _ in opts["regions"]], key=_seg_key(prefix, "regions"),
                       format_func=lambda a: rm.get(a, a), placeholder="Any")
        m2.text_input("Districts or towns", key=_seg_key(prefix, "district"), placeholder="e.g. CF10, CF11, Newport")
        sm = fmt(opts["sectors"])
        m3.multiselect("Sector", [a for a, _ in opts["sectors"]], key=_seg_key(prefix, "sectors"),
                       format_func=lambda a: sm.get(a, a), placeholder="Any")
        n1, n2, n3 = st.columns(3)
        mm = fmt(opts["markets"])
        n1.multiselect("Leased equipment type", [a for a, _ in opts["markets"]], key=_seg_key(prefix, "markets"),
                       format_func=lambda a: mm.get(a, a), placeholder="Any", help="From the leasing data, e.g. Telecoms")
        asm = fmt(opts["assets"][:60])
        n2.multiselect("Leased asset", [a for a, _ in opts["assets"][:60]], key=_seg_key(prefix, "assets"),
                       format_func=lambda a: asm.get(a, a), placeholder="Any", help="e.g. Office Telecoms, Copier")
        lm = fmt(opts["lines"])
        n3.multiselect("Phone line type", [a for a, _ in opts["lines"]], key=_seg_key(prefix, "lines"),
                       format_func=lambda a: lm.get(a, a), placeholder="Any",
                       help="ISDN and analogue lines are switched off in the 2027 digital switchover")
        o1, o2, o3 = st.columns(3)
        tm = fmt(opts["tags"])
        o1.multiselect("Tags", [a for a, _ in opts["tags"]], key=_seg_key(prefix, "tags"),
                       format_func=lambda a: tm.get(a, a), placeholder="Any")
        srm = fmt(opts["sources"])
        o2.multiselect("Came from", [a for a, _ in opts["sources"]], key=_seg_key(prefix, "sources"),
                       format_func=lambda a: srm.get(a, a), placeholder="Any list")
        o3.number_input("At least this many handsets", min_value=0, step=1, key=_seg_key(prefix, "handsets_min"),
                        help="Only counts records where a handset number has been filled in")
        p1, p2, p3, p4 = st.columns(4)
        p1.selectbox("TPS / CTPS", TPS_OPTS, key=_seg_key(prefix, "tps"),
                     help="Numbers registered with TPS/CTPS shouldn't get unsolicited sales calls")
        if show_status:
            p2.selectbox("Whose", OWNER_OPTS, key=_seg_key(prefix, "owner"))
        p3.toggle("Trading companies only", key=_seg_key(prefix, "trading_only"),
                  help="Hides firms marked dissolved, in liquidation or administration")
        p4.toggle("Missing email or phone", key=_seg_key(prefix, "gaps"))
    seg = seg_from_state(prefix)
    with st.popover("💾 Save these filters as a group"):
        nm = st.text_input("Group name", key=f"{prefix}_gname", placeholder="e.g. Cardiff 10-49 staff, lease ended")
        st.caption(seg_summary(seg))
        if st.button("Save group", key=f"{prefix}_gsave", type="primary", disabled=not nm.strip()):
            try:
                GROUP_STORE.apply({nm.strip(): {"seg": seg, "by": crm_user(), "at": now_uk().isoformat(timespec="seconds")}},
                                  f"Sales Hub: saved group {nm.strip()}")
                ss["sh_flash"] = f"💾 Saved the group <b>{esc(nm.strip())}</b>. Pick it from Saved group any time."
            except Exception as exc:
                ss["sh_flash"] = f"⚠️ Couldn't save the group: {esc(str(exc))}"
            st.rerun()
        cur = ss.get(f"{prefix}_group")
        if cur and st.button(f"🗑 Delete '{cur}'", key=f"{prefix}_gdel"):
            try:
                GROUP_STORE.apply({cur: None}, f"Sales Hub: deleted group {cur}")
            except Exception:
                pass
            ss[f"{prefix}_group"] = ""
            st.rerun()
    return seg


# ---------------- Extra detail on a record (from the master data + what the caller learns) ----------------
def facts_chips(r: Dict[str, Any]) -> List[str]:
    today = now_uk().date()
    out = []
    if is_tps(r):
        out.append(chip("⛔ TPS registered", "bad"))
    if r.get("trading_ok") is False:
        out.append(chip("⚠️ " + (r.get("company_status") or "Not trading"), "bad"))
    if r.get("employees"):
        out.append(chip(f"👥 {int(r['employees'])} staff", ""))
    if r.get("handsets"):
        out.append(chip(f"☎️ {int(to_num(r['handsets']))} handsets", "good"))
    b = credit_band(r.get("credit_rating"))
    if b:
        out.append(chip(f"Credit {b} ({int(r['credit_rating'])})", "good" if b in "AB" else ("warn" if b == "C" else "risk")))
    if r.get("line_type"):
        out.append(chip(f"Lines: {r['line_type']}", "warn" if r["line_type"] in ("ISDN", "Analogue") else ""))
    d = end_date_of(r)
    if d:
        lbl = "Contract" if r.get("contract_end") else "Lease"
        out.append(chip(f"{lbl} {'ended' if d < today else 'ends'} {d.strftime('%b %Y')}", "warn" if d < today + timedelta(days=183) else ""))
    if r.get("provider"):
        out.append(chip(f"With {r['provider']}", "muted"))
    for t in (r.get("tags") or [])[:4]:
        out.append(chip("🏷 " + t, "accent"))
    return out


def lease_html(r: Dict[str, Any]) -> str:
    if not any(r.get(k) for k in ("lease_asset", "lease_rental", "lease_end", "lease_supplier")):
        return ""
    bits = []
    if r.get("lease_asset") or r.get("lease_market"):
        bits.append(" / ".join(x for x in (r.get("lease_asset"), r.get("lease_market")) if x))
    if r.get("lease_rental"):
        bits.append(f"{money(r['lease_rental'])} {(r.get('lease_freq') or '').lower()}".strip())
    if r.get("lease_term"):
        bits.append(f"{r['lease_term']}-month term")
    if r.get("lease_end"):
        bits.append("end " + to_date(r["lease_end"]).strftime("%d %b %Y"))
    if r.get("lease_supplier"):
        bits.append("via " + r["lease_supplier"])
    return f'<div class="sh-line">📄 Lease: <b>{esc(" · ".join(bits))}</b></div>'


def company_facts_html(r: Dict[str, Any]) -> str:
    bits = []
    if r.get("sic_desc"):
        bits.append(r["sic_desc"])
    if r.get("turnover"):
        bits.append(f"turnover {money(r['turnover'])}")
    if r.get("incorporated"):
        bits.append("since " + str(r["incorporated"])[:4])
    if r.get("company_number"):
        bits.append(f"#{r['company_number']}")
    return f'<div class="sh-line" style="color:var(--faint)">🏢 {esc(" · ".join(bits))}</div>' if bits else ""


TIME_SLOTS = [""] + [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]


def due_now(r: Dict[str, Any], now: datetime) -> bool:
    """Due a call: next action date has come, and if a time was given, it's within 10 minutes of it."""
    nd = to_date(r.get("next_action"))
    if not nd or nd > now.date():
        return False
    if nd < now.date() or not r.get("next_time"):
        return True
    try:
        hh, mm = (int(x) for x in str(r["next_time"]).split(":")[:2])
    except ValueError:
        return True
    return now + timedelta(minutes=10) >= now.replace(hour=hh, minute=mm, second=0, microsecond=0)


# ---------------- Sales reps ----------------
def rep_names() -> List[str]:
    names: List[str] = []
    try:
        raw = st.secrets.get("SALES_REPS") or []
        names += [x.strip() for x in (raw.split(",") if isinstance(raw, str) else list(raw)) if str(x).strip()]
        names += [str(k) for k in dict(st.secrets.get("HUB_USERS") or {})]
    except Exception:
        pass
    for r in crm_get().values():
        if not isinstance(r, dict):
            continue
        for a in r.get("appointments") or []:
            if isinstance(a, dict) and a.get("rep"):
                names.append(a["rep"])
        if (r.get("deal") or {}).get("won_by"):
            names.append(r["deal"]["won_by"])
    return sorted(dict.fromkeys(n for n in names if n), key=str.lower)


def rep_picker(container, label: str, key: str, value: str = "") -> str:
    opts = [""] + rep_names()
    if value and value not in opts:
        opts.append(value)
    try:
        pick = container.selectbox(label, opts, index=opts.index(value) if value in opts else 0, key=key,
                                   accept_new_options=True, format_func=lambda n: n or "— pick or type a name —")
    except TypeError:
        pick = container.text_input(label, value=value, key=key)
    return (pick or "").strip()


def appts_of(rec: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [a for a in (rec.get("appointments") or []) if isinstance(a, dict) and a.get("at")]


def last_appt(rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ap = appts_of(rec)
    return max(ap, key=lambda a: a["at"]) if ap else None


def is_sat(a: Dict[str, Any]) -> bool:
    return str(a.get("result") or "").startswith("Sat")


# ---------------- 🗓 Call-backs (the telesales day) ----------------
def render_callbacks_page() -> None:
    ss = st.session_state
    data = crm_get()
    now = now_uk()
    today = now.date()
    if not name_gate():
        return
    mine_only = ss.get("cb_mine", False)
    me = crm_user()
    open_recs = [r for r in data.values() if isinstance(r, dict) and (r.get("status") or "New") not in CLOSED
                 and to_date(r.get("next_action")) and (not mine_only or (r.get("owner") or "") == me)]
    week_end = today + timedelta(days=6 - today.weekday() + 7 if today.weekday() >= 5 else 6 - today.weekday())
    groups = [("🔴 Overdue", [r for r in open_recs if to_date(r["next_action"]) < today], "risk"),
              ("🟠 Today", [r for r in open_recs if to_date(r["next_action"]) == today], "warn"),
              ("🟡 Tomorrow", [r for r in open_recs if to_date(r["next_action"]) == next_working_day(today)], ""),
              ("🗓 Rest of this week", [r for r in open_recs if next_working_day(today) < to_date(r["next_action"]) <= week_end], "muted")]
    appts_today = sorted(((a, r) for r in data.values() if isinstance(r, dict) for a in appts_of(r)
                          if not a.get("cancelled") and str(a["at"])[:10] == today.isoformat()), key=lambda x: x[0]["at"])
    sh_hero('Call-backs <span>&amp; today</span>', "Everyone you promised to ring, in order. Click a name to open it in"
            " the Caller.", [(str(len(groups[0][1])), "Overdue", "active"), (str(len(groups[1][1])), "Today", ""),
                             (str(len(groups[2][1])), "Tomorrow", ""), (str(len(appts_today)), "Appointments today", "done")],
            f"{now.strftime('%A %d %B')} · {me}")
    flash()
    show_crm_error()
    st.toggle("Only my call-backs", key="cb_mine")
    if appts_today:
        with st.container(key="card-sh-cbap"):
            section_header("📅", "Appointments today", "Booked visits and calls")
            st.dataframe(pd.DataFrame([{"Time": (_when(a["at"]) or now).strftime("%H:%M"), "Company": rec_label(r),
                                        "Where": " ".join(x for x in (r.get("town"), r.get("postcode")) if x),
                                        "Type": a.get("kind") or "", "With": a.get("with") or "",
                                        "Rep": a.get("rep") or "", "Booked by": a.get("booked_by") or ""}
                                       for a, r in appts_today]), hide_index=True, **FULL_WIDTH)
    for gi, (title, recs, tone) in enumerate(groups):
        recs = sorted(recs, key=lambda r: (r["next_action"], r.get("next_time") or "99", rec_label(r).lower()))
        with st.container(key=f"card-sh-cb{gi}"):
            section_header(title.split(" ")[0], " ".join(title.split(" ")[1:]), f"{len(recs)} to call")
            if not recs:
                st.caption("Nothing here. 👏" if gi < 2 else "Nothing booked yet.")
                continue
            df = pd.DataFrame([{"When": to_date(r["next_action"]).strftime("%a %d %b") + (f" {r['next_time']}" if r.get("next_time") else ""),
                                "Company": rec_label(r), "Phone": r.get("phone") or r.get("mobile") or r.get("ho_phone") or "",
                                "Contact": r.get("contact") or "", "Status": r.get("status") or "",
                                "Last note": ((last_call(r) or {}).get("notes") or r.get("next_note") or "")[:80],
                                "Owner": r.get("owner") or ""} for r in recs[:300]])
            try:
                ev = st.dataframe(df, hide_index=True, width="stretch", selection_mode="single-row", on_select="rerun",
                                  key=f"cb_tbl_{gi}_{ss.get('crm_ver', 0)}", height=min(38 + 35 * len(df), 420))
            except TypeError:
                ev = st.dataframe(df, hide_index=True, use_container_width=True, selection_mode="single-row",
                                  on_select="rerun", key=f"cb_tbl_{gi}_{ss.get('crm_ver', 0)}")
            rows = ev.selection.rows if ev else []
            c1, c2 = st.columns([1, 2])
            if rows:
                pick = recs[rows[0]]
                if c1.button(f"📞 Call {rec_label(pick)}", key=f"cb_go_{gi}", type="primary", **FULL_WIDTH):
                    ss["caller_rid"], ss["caller_pin"] = pick["id"], True
                    goto_view("caller")
                    st.rerun()
            if c2.button(f"📞 Work through all {len(recs)} in the Caller", key=f"cb_all_{gi}", **FULL_WIDTH):
                ss["caller_focus"] = [r["id"] for r in recs]
                open_in_caller(recs[0]["id"])
                st.rerun()


# ---------------- 💼 Pipeline (appointments → sat → sold → installed) ----------------
def apply_appt_result(rec: Dict[str, Any], appt_at: str, result: str, deal: Dict[str, Any], who: str) -> Dict[str, Any]:
    rec = dict(rec)
    today = now_uk().date()
    stamp = now_uk().isoformat(timespec="seconds")
    aps = []
    for a in appts_of(rec):
        if a["at"] == appt_at:
            a = dict(a, result=result, result_at=stamp, result_by=who, cancelled=result == "Cancelled")
        aps.append(a)
    rec["appointments"] = aps
    a = next((x for x in aps if x["at"] == appt_at), {})
    note = f"{result}" + (f" (rep {a.get('rep')})" if a.get("rep") else "")
    if result == "Sat – sold":
        rec["status"] = "Won"
        rec["deal"] = dict(rec.get("deal") or {}, **{k: v for k, v in deal.items() if v not in (None, "")})
        rec["deal"].setdefault("won_at", str(a.get("at", ""))[:10] or today.isoformat())
        rec["deal"]["won_by"] = rec["deal"].get("won_by") or a.get("rep") or who
        rec["deal"]["booked_by"] = a.get("booked_by") or ""
        rec["next_action"] = rec["next_time"] = ""
    elif result == "Sat – quoted / thinking":
        rec["status"] = "Quoted"
        rec["next_action"], rec["next_time"] = next_working_day(today, 3).isoformat(), ""
    elif result == "Sat – not sold":
        rec["status"] = "Lost"
        rec["next_action"] = rec["next_time"] = ""
    elif result in ("No show", "Cancelled"):
        rec["status"] = "Call back"
        rec["next_action"], rec["next_time"] = today.isoformat(), ""
        note += ": call to rebook"
    rec["calls"] = calls_of(rec) + [{"at": stamp, "by": who, "outcome": "Appointment: " + result, "notes": note}]
    return rec


def render_pipeline_page() -> None:
    ss = st.session_state
    data = crm_get()
    now = now_uk()
    today = now.date()
    if not name_gate():
        return
    recs = [r for r in data.values() if isinstance(r, dict)]
    pending = sorted(((a, r) for r in recs for a in appts_of(r) if not a.get("result") and not a.get("cancelled")
                      and (_when(a["at"]) or now) <= now + timedelta(hours=1)), key=lambda x: x[0]["at"])
    upcoming = [(a, r) for r in recs for a in appts_of(r) if not a.get("result") and not a.get("cancelled")
                and (_when(a["at"]) or now) > now + timedelta(hours=1)]
    awaiting = [r for r in recs if r.get("status") == "Won"]
    sh_hero('Sales <span>pipeline</span>', "Booked → sat → sold → installed. Record how each appointment went and keep"
            " deal values up to date: the Overview reports from here.",
            [(str(len(upcoming)), "Booked ahead", ""), (str(len(pending)), "Need an outcome", "active"),
             (str(len(awaiting)), "Sold, awaiting install", ""),
             (str(sum(1 for r in recs if r.get("status") == "Installed")), "Installed", "done")], f"Updating as {crm_user()}")
    flash()
    show_crm_error()

    with st.container(key="card-sh-pl1"):
        section_header("01", "How did the appointment go?",
                       "Appointments that have happened but have no result yet. Pick a result, add the deal for sales,"
                       " then save.")
        if not pending:
            st.caption("All appointments have a result. 👏")
        else:
            df = pd.DataFrame([{"_rid": r["id"], "_at": a["at"],
                                "When": (_when(a["at"]) or now).strftime("%a %d %b %H:%M"), "Company": rec_label(r),
                                "Booked by": a.get("booked_by") or "", "Rep": a.get("rep") or "", "Result": "",
                                "Monthly £": float(to_num((r.get("deal") or {}).get("mrr"))) or None,
                                "One-off £": float(to_num((r.get("deal") or {}).get("one_off"))) or None,
                                "Term (months)": int(to_num((r.get("deal") or {}).get("term")) or 0) or None,
                                "Install date": to_date((r.get("deal") or {}).get("install_date"))}
                               for a, r in pending])
            ed = st.data_editor(df, hide_index=True, key=f"pl_ed1_{ss.get('crm_ver', 0)}", **FULL_WIDTH,
                                column_order=["When", "Company", "Booked by", "Rep", "Result", "Monthly £", "One-off £",
                                              "Term (months)", "Install date"],
                                disabled=["When", "Company", "Booked by"],
                                column_config={"Result": st.column_config.SelectboxColumn("Result", options=APPT_RESULTS,
                                                                                          width="medium"),
                                               "Rep": st.column_config.SelectboxColumn("Rep", options=[""] + rep_names()),
                                               "Monthly £": st.column_config.NumberColumn("Monthly £", min_value=0, format="£%.2f"),
                                               "One-off £": st.column_config.NumberColumn("One-off £", min_value=0, format="£%.2f"),
                                               "Term (months)": st.column_config.SelectboxColumn("Term (months)", options=DEAL_TERMS),
                                               "Install date": st.column_config.DateColumn("Install date", format="DD/MM/YYYY")})
            done = ed[ed["Result"].fillna("") != ""]
            if st.button(f"💾 Save {len(done)} result(s)", type="primary", disabled=done.empty, key="pl_save1"):
                latest = crm_get()
                changes = {}
                for _, row in done.iterrows():
                    rid = row["_rid"]
                    rec = changes.get(rid) or latest.get(rid)
                    if not rec:
                        continue
                    nv = lambda c: None if c not in row or pd.isna(row[c]) or row[c] == "" else row[c]  # noqa: E731
                    if nv("Rep"):
                        rec = dict(rec, appointments=[dict(a, rep=nv("Rep")) if a["at"] == row["_at"] else a
                                                      for a in appts_of(rec)])
                    deal = {"mrr": float(nv("Monthly £") or 0), "one_off": float(nv("One-off £") or 0),
                            "term": int(nv("Term (months)") or 36),
                            "install_date": nv("Install date").isoformat() if nv("Install date") else "",
                            "won_by": nv("Rep") or ""}
                    changes[rid] = apply_appt_result(rec, row["_at"], row["Result"], deal, crm_user())
                if changes:
                    crm_save(changes, f"{len(changes)} appointment result(s)")
                    ss["sh_flash"] = f"💾 Saved {len(changes)} appointment result(s)."
                st.rerun()

    with st.container(key="card-sh-pl2"):
        section_header("02", "Deals", "Quoted, sold and installed. Edit any cell (values, rep, install date, stage),"
                       " then save. Set the stage to Installed once it's in.")
        f1, f2 = st.columns([2, 1])
        stages = f1.multiselect("Show", ["Quoted", "Won", "Installed", "Lost"], default=["Quoted", "Won", "Installed"],
                                key="pl_stages", format_func=lambda s_: {"Won": "Sold (awaiting install)"}.get(s_, s_))
        since = f2.date_input("Sold / updated since", value=today - timedelta(days=365), format="DD/MM/YYYY", key="pl_since")
        rows = [r for r in recs if r.get("status") in stages and
                (to_date((r.get("deal") or {}).get("won_at")) or to_date(str(r.get("updated_at") or "")[:10]) or today) >= since]
        rows.sort(key=lambda r: (["Quoted", "Won", "Installed", "Lost"].index(r["status"]),
                                 str((r.get("deal") or {}).get("won_at") or "")), reverse=False)
        if not rows:
            st.caption("No deals in this view yet.")
        else:
            def _row(r: Dict[str, Any]) -> Dict[str, Any]:
                d = r.get("deal") or {}
                la = last_appt(r) or {}
                mrr, one, term, tcv = deal_values(r)
                return {"_rid": r["id"], "Company": rec_label(r), "Stage": r["status"],
                        "Booked by": d.get("booked_by") or la.get("booked_by") or "",
                        "Rep": d.get("won_by") or la.get("rep") or "", "Sold on": to_date(d.get("won_at")),
                        "Monthly £": mrr or None, "One-off £": one or None, "Term (months)": term or None,
                        "Contract value £": tcv or None, "Install date": to_date(d.get("install_date")),
                        "Handsets": int(to_num(r.get("handsets")) or 0) or None, "Deal notes": d.get("notes") or ""}
            df2 = pd.DataFrame([_row(r) for r in rows])
            ed2 = st.data_editor(df2, hide_index=True, key=f"pl_ed2_{ss.get('crm_ver', 0)}", **FULL_WIDTH,
                                 column_order=[c for c in df2.columns if not c.startswith("_")],
                                 disabled=["Company", "Contract value £"],
                                 column_config={
                                     "Stage": st.column_config.SelectboxColumn("Stage", options=["Quoted", "Won", "Installed", "Lost"]),
                                     "Rep": st.column_config.SelectboxColumn("Rep", options=[""] + rep_names()),
                                     "Booked by": st.column_config.TextColumn("Booked by"),
                                     "Sold on": st.column_config.DateColumn("Sold on", format="DD/MM/YYYY"),
                                     "Install date": st.column_config.DateColumn("Install date", format="DD/MM/YYYY"),
                                     "Monthly £": st.column_config.NumberColumn("Monthly £", min_value=0, format="£%.2f"),
                                     "One-off £": st.column_config.NumberColumn("One-off £", min_value=0, format="£%.2f"),
                                     "Contract value £": st.column_config.NumberColumn("Contract value £", format="£%.0f"),
                                     "Term (months)": st.column_config.SelectboxColumn("Term (months)", options=DEAL_TERMS),
                                     "Handsets": st.column_config.NumberColumn("Handsets", min_value=0, step=1)})
            tot = ed2.fillna({"Monthly £": 0, "One-off £": 0, "Term (months)": 0})
            st.caption(f"In this view: **{money(float(tot['Monthly £'].sum()))}/month**, "
                       f"**{money(float((tot['Monthly £'] * tot['Term (months)']).sum() + tot['One-off £'].sum()))}** total contract value.")
            if st.button("💾 Save deal changes", type="primary", key="pl_save2"):
                latest = crm_get()
                changes = {}
                stamp = now_uk().isoformat(timespec="seconds")
                cols = ["Stage", "Booked by", "Rep", "Sold on", "Monthly £", "One-off £", "Term (months)", "Install date",
                        "Handsets", "Deal notes"]
                for (_, new), (_, old) in zip(ed2.iterrows(), df2.iterrows()):
                    same = all((pd.isna(new[c]) and pd.isna(old[c])) or new[c] == old[c] for c in cols)
                    if same or new["_rid"] not in latest:
                        continue
                    rec = dict(latest[new["_rid"]])
                    d = dict(rec.get("deal") or {})
                    nv = lambda c: None if pd.isna(new[c]) else new[c]  # noqa: E731
                    d.update({"mrr": float(nv("Monthly £") or 0), "one_off": float(nv("One-off £") or 0),
                              "term": int(nv("Term (months)") or 0), "won_by": nv("Rep") or "",
                              "booked_by": nv("Booked by") or "", "notes": nv("Deal notes") or "",
                              "won_at": nv("Sold on").isoformat() if nv("Sold on") else d.get("won_at", ""),
                              "install_date": nv("Install date").isoformat() if nv("Install date") else ""})
                    if new["Stage"] == "Installed" and not d.get("installed_at"):
                        d["installed_at"] = d.get("install_date") or today.isoformat()
                    if new["Stage"] in ("Won", "Installed") and not d.get("won_at"):
                        d["won_at"] = today.isoformat()
                    if new["Stage"] != rec.get("status"):
                        rec["calls"] = calls_of(rec) + [{"at": stamp, "by": crm_user(), "outcome": "Status changed",
                                                         "notes": f"{rec.get('status')} → {new['Stage']}"}]
                    rec["status"], rec["deal"] = new["Stage"], d
                    if nv("Handsets"):
                        rec["handsets"] = int(nv("Handsets"))
                    changes[rec["id"]] = rec
                if changes:
                    crm_save(changes, f"{len(changes)} deal(s) updated")
                    ss["sh_flash"] = f"💾 Updated {len(changes)} deal(s)."
                st.rerun()

    with st.container(key="card-sh-pl3"):
        section_header("03", "Booked ahead", "Appointments still to happen")
        ups = sorted(upcoming, key=lambda x: x[0]["at"])
        if not ups:
            st.caption("Nothing booked ahead.")
        else:
            st.dataframe(pd.DataFrame([{"When": (_when(a["at"]) or now).strftime("%a %d %b %H:%M"), "Company": rec_label(r),
                                        "Where": " ".join(x for x in (r.get("town"), r.get("postcode")) if x),
                                        "Type": a.get("kind") or "", "With": a.get("with") or "", "Rep": a.get("rep") or "",
                                        "Booked by": a.get("booked_by") or "",
                                        "Handsets": int(to_num(r.get("handsets")) or 0) or None} for a, r in ups]),
                         hide_index=True, **FULL_WIDTH)


# ---------------- 📈 Funnel numbers for the Overview ----------------
def funnel_stats(recs: List[Dict[str, Any]], start: date) -> Dict[str, Any]:
    """Booked (by the date it was booked), sat (by appointment date), sold (by sold date), installed (by install date)."""
    in_p = lambda iso: bool(iso) and (to_date(str(iso)[:10]) or date.min) >= start  # noqa: E731
    booked, sat, sold, installed, awaiting = [], [], [], [], []
    for r in recs:
        for a in appts_of(r):
            if in_p(a.get("booked_at")):
                booked.append((a, r))
            if is_sat(a) and in_p(a.get("at")):
                sat.append((a, r))
        d = r.get("deal") or {}
        if r.get("status") in SOLD and in_p(d.get("won_at")):
            sold.append(r)
        if r.get("status") == "Installed" and in_p(d.get("installed_at") or d.get("install_date") or d.get("won_at")):
            installed.append(r)
        if r.get("status") == "Won":
            awaiting.append(r)
    val = lambda rs: sum(deal_values(r)[3] for r in rs)  # noqa: E731
    return {"booked": booked, "sat": sat, "sold": sold, "installed": installed, "awaiting": awaiting,
            "sold_tcv": val(sold), "sold_mrr": sum(deal_values(r)[0] for r in sold), "installed_tcv": val(installed),
            "awaiting_tcv": val(awaiting), "awaiting_mrr": sum(deal_values(r)[0] for r in awaiting)}


def render_funnel(recs: List[Dict[str, Any]], start: date, period: str) -> None:
    f = funnel_stats(recs, start)
    nb, ns, nsold = len(f["booked"]), len(f["sat"]), len(f["sold"])
    sit = f"{ns / nb * 100:.0f}% sit rate" if nb else period.lower()
    close = f"{nsold / ns * 100:.0f}% of sits" if ns else period.lower()
    with st.container(key="card-sh-funnel"):
        section_header("£", "Sales funnel", f"Booked → sat → sold → installed · {period.lower()}")
        kpis([(f"{nb:,}", "Booked", "appointments made", "#60A5FA"), (f"{ns:,}", "Sat", sit, "#34D399"),
              (f"{nsold:,}", "Sold", close, "#F0645A"), (money(f["sold_tcv"]), "Sold value", f"{money(f['sold_mrr'])}/month new", "#FBBF24")], 4)
        kpis([(f"{len(f['awaiting']):,}", "Awaiting install", f"{money(f['awaiting_mrr'])}/month", "#A78BFA"),
              (money(f["awaiting_tcv"]), "Value to be installed", "sold, not yet in", "#A78BFA"),
              (f"{len(f['installed']):,}", "Installed", period.lower(), "#34D399"),
              (money(f["installed_tcv"]), "Installed value", period.lower(), "#34D399")], 4)
        try:
            import altair as alt
            fd = pd.DataFrame([{"Stage": s_, "Count": n, "o": i} for i, (s_, n) in enumerate(
                [("Booked", nb), ("Sat", ns), ("Sold", nsold), ("Installed", len(f["installed"]))])])
            ch = (alt.Chart(fd).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#F0645A")
                  .encode(y=alt.Y("Stage:N", sort=["Booked", "Sat", "Sold", "Installed"], title=None,
                                  axis=alt.Axis(labelColor="#E7EAF3")),
                          x=alt.X("Count:Q", title=None, axis=alt.Axis(labelColor="#8C98B0", gridColor="#1F2A40", tickMinStep=1)),
                          tooltip=["Stage", "Count"])
                  .properties(height=150, background="transparent").configure_view(strokeWidth=0))
            st.altair_chart(ch, **FULL_WIDTH)
        except Exception:
            pass
        t1, t2 = st.columns(2)
        tele: Dict[str, Dict[str, Any]] = {}
        for a, r in f["booked"]:
            tele.setdefault(a.get("booked_by") or "Unknown", {"Booked": 0, "Sat": 0, "Sold": 0, "Sold value £": 0.0})["Booked"] += 1
        for a, r in f["sat"]:
            tele.setdefault(a.get("booked_by") or "Unknown", {"Booked": 0, "Sat": 0, "Sold": 0, "Sold value £": 0.0})["Sat"] += 1
        for r in f["sold"]:
            p = (r.get("deal") or {}).get("booked_by") or (last_appt(r) or {}).get("booked_by")
            if p:
                t = tele.setdefault(p, {"Booked": 0, "Sat": 0, "Sold": 0, "Sold value £": 0.0})
                t["Sold"] += 1
                t["Sold value £"] += deal_values(r)[3]
        reps: Dict[str, Dict[str, Any]] = {}
        for a, r in f["sat"]:
            reps.setdefault(a.get("rep") or "Unassigned", {"Sat": 0, "Sold": 0, "Monthly £": 0.0, "Contract value £": 0.0})["Sat"] += 1
        for r in f["sold"]:
            p = (r.get("deal") or {}).get("won_by") or "Unassigned"
            t = reps.setdefault(p, {"Sat": 0, "Sold": 0, "Monthly £": 0.0, "Contract value £": 0.0})
            t["Sold"] += 1
            t["Monthly £"] += deal_values(r)[0]
            t["Contract value £"] += deal_values(r)[3]
        money_cfg = lambda cols: {c: st.column_config.NumberColumn(c, format="£%.0f") for c in cols}  # noqa: E731
        with t1:
            st.markdown("**Telesales**: who booked what")
            if tele:
                st.dataframe(pd.DataFrame([{"Telesales": k, **v, "Sit rate": f"{v['Sat'] / v['Booked'] * 100:.0f}%" if v["Booked"] else ""}
                                           for k, v in sorted(tele.items())]), hide_index=True, **FULL_WIDTH,
                             column_config=money_cfg(["Sold value £"]))
            else:
                st.caption("No appointments booked in this period.")
        with t2:
            st.markdown("**Sales reps**: sits and sales")
            if reps:
                st.dataframe(pd.DataFrame([{"Rep": k, **v, "Close rate": f"{v['Sold'] / v['Sat'] * 100:.0f}%" if v["Sat"] else ""}
                                           for k, v in sorted(reps.items())]), hide_index=True, **FULL_WIDTH,
                             column_config=money_cfg(["Monthly £", "Contract value £"]))
            else:
                st.caption("No sits or sales in this period.")


# ---------------- 🏛 Companies House check (free, light: 2 calls per firm) ----------------
CH_BATCH = 100


def ch_check_one(rec: Dict[str, Any], key: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Returns (field updates, note). Uses the company number; looks one up by name only if it's missing."""
    e = LeadEnricher(ch_api_key=key)
    num = rec.get("company_number")
    if not num:
        hit = find_company_by_name(e, rec_label(rec), rec.get("town") or "", rec.get("postcode") or "")
        num = (hit or {}).get("company_number")
        if not num:
            return None, "no match"
    det = e.get_company_details(num)
    if not det:
        return None, "not found"
    upd: Dict[str, Any] = {"company_number": num, "ch_checked_at": now_uk().isoformat(timespec="seconds")}
    status = str(det.get("company_status") or "")
    upd["company_status"] = status.replace("-", " ").capitalize() + (
        f" ({det['company_status_detail'].replace('-', ' ')})" if det.get("company_status_detail") else "")
    upd["trading_ok"] = status == "active" and not det.get("company_status_detail")
    addr = det.get("registered_office_address") or {}
    reg = ", ".join(x for x in (addr.get("premises"), addr.get("address_line_1"), addr.get("address_line_2"),
                                addr.get("locality"), addr.get("postal_code")) if x)
    if reg:
        upd["reg_address"] = reg
    if not rec.get("postcode") and addr.get("postal_code"):
        upd["postcode"] = addr["postal_code"].upper()
    if not rec.get("town") and addr.get("locality"):
        upd["town"] = addr["locality"]
    if not rec.get("address") and addr.get("address_line_1"):
        upd["address"] = ", ".join(x for x in (addr.get("premises"), addr.get("address_line_1")) if x)
    if det.get("sic_codes"):
        upd["sic"] = ", ".join(det["sic_codes"])
        if not rec.get("sector") or rec.get("sector") == "General Business":
            upd["sector"] = sector_from_sic(det["sic_codes"]) or rec.get("sector") or "General Business"
    if det.get("date_of_creation"):
        upd["incorporated"] = det["date_of_creation"]
    if det.get("company_name") and _n(det["company_name"]) != _n(rec.get("company") or ""):
        upd["company"] = tidy_name(det["company_name"])
        upd["former_name"] = rec.get("company") or ""
    officers = e.get_officers(num)
    if officers:
        names = [display_officer_name(o.name) for o in officers]
        if not rec.get("contact") or not any(_n(rec["contact"]).startswith(_n(nm)[:6]) or _n(nm).startswith(_n(rec["contact"])[:6])
                                             for nm in names):
            dm = pick_decision_maker(officers)
            if dm:
                upd["contact"], upd["role"] = display_officer_name(dm.name), format_role(dm.role) if dm.role else "Director"
                if rec.get("contact"):
                    upd["former_contact"] = rec["contact"]
        upd["officers"] = names[:6]
    tags = list(rec.get("tags") or [])
    if not upd["trading_ok"] and "Closed at Companies House" not in tags:
        upd["tags"] = tags + ["Closed at Companies House"]
    return upd, ("closed" if not upd["trading_ok"] else "ok")


def ch_cleanse(rids: List[str]) -> Tuple[int, int, int]:
    key = ch_api_key if "ch_api_key" in globals() else secret_ch_key
    if not key:
        st.session_state["crm_error"] = "Add COMPANIES_HOUSE_KEY to Secrets to check records at Companies House."
        return 0, 0, 0
    data = crm_get()
    cutoff = (now_uk() - timedelta(days=30)).isoformat()
    todo = [r for r in rids if r in data and str(data[r].get("ch_checked_at") or "") < cutoff][:CH_BATCH]
    if not todo:
        return 0, 0, 0
    bar = st.progress(0.0, text="Checking Companies House…")
    results: Dict[str, Dict[str, Any]] = {}
    closed = fails = 0
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(ch_check_one, dict(data[r]), key): r for r in todo}
        for n_, fut in enumerate(as_completed(futs), start=1):
            rid = futs[fut]
            try:
                upd, note = fut.result()
            except Exception:
                upd, note = None, "error"
            if upd:
                results[rid] = upd
                closed += note == "closed"
            else:
                fails += 1
                results[rid] = {"ch_checked_at": now_uk().isoformat(timespec="seconds")}
            bar.progress(n_ / len(todo), text=f"Checked {n_} of {len(todo)} · {rec_label(data[rid])}")
    bar.empty()
    latest = crm_get()
    changes = {rid: {**latest[rid], **upd} for rid, upd in results.items() if rid in latest}
    if changes:
        crm_save(changes, f"Companies House check: {len(changes)}")
    return len(todo) - fails, closed, fails


def dispatch_sales_hub_views() -> None:
    view = st.session_state.get("view")
    pages = {"customers": render_customers_page, "caller": render_caller_page, "callbacks": render_callbacks_page,
             "pipeline": render_pipeline_page, "local": render_local_page, "overview": render_overview_page}
    if view not in pages:
        return
    render_html(SH_CSS + CALL_CSS)
    pages[view]()
    data = crm_get()
    today = now_uk().date()
    due = sum(1 for r in data.values() if isinstance(r, dict) and (r.get("status") or "New") not in CLOSED
              and (to_date(r.get("next_action")) or date.max) <= today)
    render_html('<div class="pe-stats">'
                f'<div class="pe-stat"><div class="v">{len(data):,}</div><div class="l">Customers</div></div>'
                f'<div class="pe-stat"><div class="v">{due:,}</div><div class="l">Due a call</div></div>'
                f'<div class="pe-stat"><div class="v">{sum(1 for r in data.values() if isinstance(r, dict) and r.get("status") in SOLD):,}</div><div class="l">Sold</div></div>'
                "</div>", target=sidebar_stats_slot)
    st.stop()


dispatch_sales_hub_views()  # Customers / Caller / Local / Overview stop here; Prospecting carries on below

col_left, col_right = st.columns([1.08, 0.92], gap="large")

# ---------------- Left: Target & Select ----------------
if st.session_state.get("view") == "quick":
    with col_left:
        render_quick_add()
else:
    with col_left:
        with st.container(key="card-left"):
            section_header("01", "Target market", "Pick a sector and territory to pull live firms from Companies House.")

            selected_vertical_name = st.selectbox(
                "Industry vertical",
                options=sorted(VERTICAL_PRESETS.keys()),
                index=sorted(VERTICAL_PRESETS.keys()).index("Estate & Lettings Agents"),
                help="16 sectors, each with its own Companies House codes, systems, pitch and overview PDF.",
            )
            vertical_config = VERTICAL_PRESETS[selected_vertical_name]
            render_html(
                '<div class="pe-vertical"><div style="flex:1">'
                '<div class="lbl">Systems we integrate with</div><div class="pe-chips">'
                + "".join(chip(c, "accent") for c in vertical_config["crms"])
                + '</div></div><div><div class="lbl">SIC</div><div class="pe-chips">'
                + "".join(chip(c) for c in vertical_config["sic_codes"])
                + "</div></div></div>"
            )

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                location_input = st.text_input(
                    "Town, city or county",
                    placeholder="e.g. Walsall or West Midlands",
                )
            with f_col2:
                keyword_filter = st.text_input(
                    "Name keyword (optional)",
                    placeholder=f"e.g. {vertical_config['search_hint']}",
                )

            r_col1, r_col2 = columns([1, 2.2])
            with r_col1:
                result_limit = st.selectbox("Results", [25, 50, 100], index=0)
            with r_col2:
                browse_btn = st.button(
                    "Find companies", type="primary", **FULL_WIDTH
                )
            target_row = None

            if browse_btn:
                if not ch_api_key:
                    st.error("Please supply your Companies House API key in the sidebar.")
                else:
                    with st.spinner("Querying the Companies House register…"):
                        enricher = LeadEnricher(ch_api_key=ch_api_key)
                        leads_list, search_error = enricher.browse_vertical(
                            sic_codes=vertical_config["sic_codes"],
                            location_keyword=location_input,
                            company_name_includes=keyword_filter,
                            limit=result_limit,
                        )
                    st.session_state["discovered_leads"] = leads_list
                    st.session_state["active_vertical_name"] = selected_vertical_name
                    st.session_state["search_location"] = location_input.strip()
                    st.session_state["selected_lead_row"] = None
                    # New search = new table widget, so no stale row selection carries over.
                    st.session_state["search_version"] = st.session_state.get("search_version", 0) + 1
                    if not search_error:
                        st.session_state["stat_searches"] += 1
                        st.session_state["stat_firms"] += len(leads_list)
                    if search_error:
                        st.error(search_error)
                    elif not leads_list:
                        st.warning(
                            "No active companies matched. Try a broader location"
                            " (e.g. county instead of town) or remove the name keyword."
                        )

        if st.session_state.get("discovered_leads"):
            with st.container(key="card-select"):
                leads_data = st.session_state["discovered_leads"]
                where = st.session_state.get("search_location") or "the UK"
                log_now = get_sent_log()
                already = sum(1 for r in leads_data if r.get("Company Number") in log_now)
                section_header(
                    "02", "Select firms",
                    f"{len(leads_data)} active {'firm' if len(leads_data) == 1 else 'firms'} in {where}"
                    f" · {st.session_state.get('active_vertical_name', '')}"
                    + (f" · {already} already contacted" if already else ""),
                )

                df = pd.DataFrame(leads_data)
                df["Contacted"] = [sent_label(log_now.get(cn)) for cn in df["Company Number"]]
                if "Town / Postcode" in df.columns:
                    df["Town"] = df["Town / Postcode"].astype(str).str.split(",").str[0]
                if "Incorporated" in df.columns:
                    df["Incorporated"] = pd.to_datetime(df["Incorporated"], errors="coerce")

                table_event = render_leads_table(
                    df, key=f"leads_table_{st.session_state.get('search_version', 0)}"
                )
                selected_rows = [i for i in (table_event.selection.rows if table_event else []) if i < len(leads_data)]
                selected = [leads_data[i] for i in selected_rows]
                st.session_state["selected_rows_data"] = selected

                batch_to_run: List[Dict[str, Any]] = []
                website_override = ""
                if not selected:
                    render_html(
                        f'<div class="pe-hint">{icon("pointer", 16)}'
                        "Tick one firm, or several to build a batch. Or enrich every result in one go.</div>"
                    )
                    n_all = min(len(leads_data), MAX_BATCH)
                    fresh = [r for r in leads_data if r["Company Number"] not in log_now and r["Company Number"] not in st.session_state.get("queue", {})]
                    if st.button(
                        f"⚡ Enrich all {min(len(fresh), MAX_BATCH)} new results"
                        + (f" (skips {len(leads_data) - len(fresh)} already contacted or queued)" if len(fresh) < len(leads_data) else ""),
                        type="primary", disabled=not fresh, **FULL_WIDTH,
                        help=f"Finds contacts for every firm in the list (up to {MAX_BATCH} at a time), then sorts them into Ready to email / No email below.",
                    ):
                        batch_to_run = fresh[:MAX_BATCH]
                    if len(fresh) > MAX_BATCH:
                        st.caption(f"The first {MAX_BATCH} will be enriched. Run it again for the next {MAX_BATCH}.")
                else:
                    n_sel = len(selected)
                    names = ", ".join(esc(friendly_company_name(r["Company Name"])) for r in selected[:3])
                    more = f" + {n_sel - 3} more" if n_sel > 3 else ""
                    contacted_sel = [r for r in selected if r["Company Number"] in log_now]
                    meta = (f'#{esc(selected[0]["Company Number"])} · {esc(selected[0]["Town / Postcode"])}'
                            if n_sel == 1 else f"{names}{more}")
                    render_html(
                        f'<div class="pe-selected"><div><div class="n">'
                        f'{esc(selected[0]["Company Name"]) if n_sel == 1 else f"{n_sel} firms selected"}</div>'
                        f'<div class="m">{meta}</div></div>'
                        f'{chip(f"{n_sel} selected", "accent")}</div>'
                    )
                    if contacted_sel:
                        st.caption(
                            f"⚠️ {len(contacted_sel)} of these already contacted: "
                            + ", ".join(friendly_company_name(r["Company Name"]) for r in contacted_sel[:4])
                            + ("…" if len(contacted_sel) > 4 else "")
                        )
                    if n_sel > MAX_BATCH:
                        st.warning(f"Batches are capped at {MAX_BATCH} firms. Only the first {MAX_BATCH} will be enriched.")

                    if n_sel == 1:
                        e_col1, e_col2 = columns([1.6, 1])
                        with e_col1:
                            website_override = st.text_input(
                                "Website (optional)", placeholder="Leave blank to auto-discover",
                            )
                        with e_col2:
                            if st.button("Enrich & build dossier", type="primary", **FULL_WIDTH):
                                batch_to_run = selected[:1]
                    else:
                        if st.button(f"Enrich {min(n_sel, MAX_BATCH)} firms & add to review", type="primary", **FULL_WIDTH):
                            batch_to_run = selected[:MAX_BATCH]

                if batch_to_run:
                    vertical_now = st.session_state.get("active_vertical_name", "Estate & Lettings Agents")
                    run_enrichment(
                        batch_to_run, vertical_now,
                        manual_websites={batch_to_run[0]["Company Number"]: website_override} if website_override else None,
                    )


# ---------------- Right: Dossier ----------------
queue: Dict[str, Dict[str, Any]] = st.session_state.setdefault("queue", {})
queue_order: List[str] = [cn for cn in st.session_state.setdefault("queue_order", []) if cn in queue]

with col_right:
    with st.container(key="card-right"):
        if not queue:
            render_html(
                f'<div class="pe-empty"><div style="color:var(--accent);display:inline-block;'
                f'padding:18px;border-radius:20px;background:var(--accent-soft);border:1px solid rgba(240, 100, 90,.3)">'
                f'{icon("target", 40, 1.6)}</div>'
                '<div class="t">Your dossier will appear here</div>'
                '<div class="s">Every enriched firm gets a contact card, verified channels,'
                ' a sector integration pitch and a one-page PDF.</div>'
                "<ol><li>Choose a sector &amp; territory</li><li>Tick one or more firms</li>"
                "<li>Hit <b>&nbsp;Enrich</b></li></ol></div>"
            )
        else:
            log_now = get_sent_log()
            if st.session_state.get("current_cn") not in queue:
                st.session_state["current_cn"] = queue_order[0]
            if len(queue_order) > 1:
                if st.session_state.get("current_cn_select") not in queue:
                    st.session_state["current_cn_select"] = st.session_state["current_cn"]
                st.selectbox(
                    f"Viewing firm ({len(queue_order)} in queue)",
                    options=queue_order,
                    key="current_cn_select",
                    format_func=lambda c: ("✓ " if c in log_now else "") + lead_display_name(queue[c]["lead"]),
                )
                st.session_state["current_cn"] = st.session_state["current_cn_select"]
            cn = st.session_state["current_cn"]
            item = queue[cn]
            lead: ScrapedLead = item["lead"]
            current_vert_name = item["vertical"]
            vert_cfg = VERTICAL_PRESETS[current_vert_name]
            contact_name, contact_role = infer_contact_name_and_role(lead, current_vert_name)
            primary_email = pick_primary_email(lead, contact_name)
            is_sent = cn in log_now

            section_header("02" if st.session_state.get("view") == "quick" else "03", "Lead dossier",
                           "Review, tailor the pitch and send.")

            # Firm header
            quick_lead = bool(item.get("lead_source"))  # Added by hand: no company number or website to show
            meta = ([] if quick_lead else [chip(f"#{lead.company_number or 'N/A'}")]) + [chip(current_vert_name, "accent")]
            meta += [chip(f"SIC {c}", "muted") for c in lead.sic_codes[:2]]
            if quick_lead:
                meta.append(chip(f"Added by {item.get('added_by') or 'Quick add'}", "muted"))
            else:
                meta.append(confidence_chip(lead.website_confidence if lead.website_url else None))
            if is_sent:
                meta.append(chip(f"Sent {sent_label(log_now[cn])[2:]}", "good"))
            zrec = get_zoho_store().get(cn) or {}
            if zrec:
                meta.append(chip({"created": "In Zoho: new lead", "existing": "In Zoho: existing lead",
                                  "customer": "Existing customer!"}.get(zrec.get("status"), "In Zoho"),
                                 "risk" if zrec.get("status") == "customer" else "accent"))
            blurb = (
                f'<div class="blurb">“{esc(lead.site_meta_description[:220])}'
                f'{"…" if len(lead.site_meta_description) > 220 else ""}”</div>'
                if lead.site_meta_description else ""
            )
            render_html(
                f'<div class="pe-firm"><div><div class="name">{esc(lead.company_name)}</div>'
                f'<div class="meta">{"".join(meta)}</div>{blurb}</div></div>'
            )
            if zrec.get("id"):
                st.link_button("Open in Zoho ↗", ZOHO.record_url(zrec["id"], "Accounts" if zrec.get("status") == "customer" else "Leads"))
            if zrec.get("status") == "customer":
                st.error(f"This firm is already a customer in Zoho ({zrec.get('name') or 'Accounts'}). Use Customer Growth for them,"
                         " not a new-business pitch.")

            if not lead.website_url and getattr(lead, "contact_email", None):
                pass  # A person has confirmed the contact, so the missing website no longer matters
            elif not lead.website_url:
                st.warning(
                    "Couldn't confidently find this firm's website. Tick just this firm on the left,"
                    " paste its website and re-run to pull contacts."
                )
            elif lead.website_confidence == "Low":
                st.warning(
                    "Weak website match. Check it's the right firm before sending, or tick just this"
                    " firm on the left, paste the correct website and re-run."
                )

            reg = register_link(current_vert_name, lead.company_name)
            if reg:
                st.link_button(f"🔎 Check on the {reg[0]} ↗", reg[1],
                               help="Official register: confirms the firm and often lists its website, phone and manager.")

            tab1, tab2 = st.tabs(["Overview", "Pitch & send"])

            with tab1:
                # Contact + channels
                email_rows = "".join(
                    f'<div class="pe-row">{icon("mail", 15)}<a class="trunc" title="{esc(e)}" href="mailto:{esc(e)}">{esc(e)}</a>'
                    + ('<span class="tag" title="Used in the email &amp; PDF">★ Primary</span>' if e == primary_email else "")
                    + "</div>"
                    for e in lead.emails_found[:5]
                ) or '<div class="pe-none">No emails found</div>'
                phone_rows = "".join(
                    f'<div class="pe-row">{icon("phone", 15)}'
                    f'<a href="tel:{esc(p.replace(" ", ""))}">{esc(p)}</a>'
                    + ('<span class="tag">Main</span>' if i == 0 else "")
                    + "</div>"
                    for i, p in enumerate(lead.phones_found[:4])
                ) or '<div class="pe-none">No phone numbers found</div>'
                site_row = (
                    f'<div class="pe-row">{icon("globe", 15)}<a href="{esc(lead.website_url)}" target="_blank">'
                    f'{esc(lead.website_url.replace("https://", "").replace("http://", ""))}</a></div>'
                    if lead.website_url else ""
                )
                addr_row = (
                    f'<div class="pe-row">{icon("pin", 15)}<span>{esc(lead.registered_address)}</span>'
                    '<span class="tag">Reg. office</span></div>'
                    if lead.registered_address else ""
                )
                li_row = (
                    f'<div class="pe-row"><span class="li-mini">in</span><a class="trunc" href="{esc(lead.linkedin_url)}" target="_blank">'
                    'LinkedIn profile</a></div>' if getattr(lead, "linkedin_url", None) else ""
                )
                render_html(
                    '<div class="pe-panel"><div class="h">Decision-maker</div>'
                    f'<div class="pe-contact"><div class="pe-avatar">{esc(initials(contact_name))}</div>'
                    f'<div><div class="n">{esc(contact_name)}</div><div class="r">{esc(contact_role)}</div></div></div>'
                    f'<div style="margin-top:12px">{site_row}{addr_row}{li_row}</div></div>'
                    '<div class="pe-panel"><div class="h">Channels</div><div class="pe-cols">'
                    f'<div>{email_rows}</div><div>{phone_rows}</div></div></div>'
                )

                # ---- LinkedIn: a person looks, then brings the right contact back ----
                with st.container(key="card-linkedin"):
                    have = bool(getattr(lead, "contact_name", None))
                    render_html(
                        '<div class="li-head"><span class="li-badge">in</span><div><div class="t">'
                        + ("Contact confirmed" if have else "Find the right person on LinkedIn")
                        + '</div><div class="s">'
                        + (f"{esc(lead.contact_name)}{' · ' + esc(lead.contact_role) if lead.contact_role else ''}"
                           f"{' · updated by ' + esc(get_contacts().get(cn, {}).get('updated_by')) if get_contacts().get(cn, {}).get('updated_by') else ''}"
                           if have else "Search in your own LinkedIn, then paste who you find below. The email and PDF update instantly.")
                        + "</div></div></div>"
                    )
                    lk1, lk2 = st.columns(2)
                    with lk1:
                        st.link_button("🔎  Find people on LinkedIn", linkedin_people_url(lead), **FULL_WIDTH,
                                       help="Opens LinkedIn in a new tab, searching for the director at this firm")
                    with lk2:
                        st.link_button("🏢  Company page", linkedin_company_url(lead), **FULL_WIDTH)
                    with st.form(key=f"li_form_{cn}", border=False):
                        a1, a2 = st.columns(2)
                        with a1:
                            f_name = st.text_input("Contact name", value=getattr(lead, "contact_name", None) or "",
                                                   placeholder="e.g. Sarah Jones")
                        with a2:
                            f_role = st.text_input("Job title", value=getattr(lead, "contact_role", None) or "",
                                                   placeholder="e.g. Practice Manager")
                        a3, a4 = st.columns(2)
                        with a3:
                            f_li = st.text_input("LinkedIn profile link", value=getattr(lead, "linkedin_url", None) or "",
                                                 placeholder="https://www.linkedin.com/in/…")
                        with a4:
                            hint = suggest_email(getattr(lead, "contact_name", None) or "", lead)
                            f_email = st.text_input("Business email (if known)", value=getattr(lead, "contact_email", None) or "",
                                                    placeholder=f"Likely: {hint}" if hint else "name@firm.co.uk")
                        saved = st.form_submit_button("Save contact", type="primary", **FULL_WIDTH)
                    if hint and not getattr(lead, "contact_email", None):
                        st.caption(f"💡 Their website uses addresses like this, so **{hint}** is likely, but unverified."
                                   " Only use it if you're comfortable it's right.")
                    elif getattr(lead, "contact_name", None) is None:
                        st.caption("Tip: type the name and save first. If their website shows how emails are formed,"
                                   " a likely address will be suggested.")
                    if saved:
                        err = save_contact(cn, f_name, f_role, f_li, f_email)
                        if err:
                            st.error(err)
                        else:
                            st.session_state["li_flash"] = "Contact saved" + (
                                ". This firm is now in Ready to email." if f_email.strip() else ".")
                            st.rerun()
                    if st.session_state.get("li_flash"):
                        st.success(st.session_state.pop("li_flash"))

                # Officers + integration hook
                officer_rows = "".join(
                    f'<div class="pe-officer"><span><span class="who">{esc(display_officer_name(o.name))}</span>'
                    f' <span style="color:var(--muted)">· {esc(o.role)}</span></span>'
                    f'<span class="since">since {esc((o.appointed_on or "N/A")[:4])}</span></div>'
                    for o in lead.officers[:6]
                ) or '<div class="pe-none">No active officers returned</div>'
                hook_items = "".join(f"<li>{esc(b)}</li>" for b in vert_cfg["pitch_bullets"])
                render_html(
                    f'<div class="pe-hook"><div class="h">Integration hook</div>'
                    f'<div class="t">{esc(vert_cfg["primary_hook"])}</div><ul>{hook_items}</ul></div>'
                    f'<div class="pe-panel"><div class="h">Registered officers ({len(lead.officers)})</div>{officer_rows}</div>'
                )

                if lead.website_reasons or lead.discovery_notes or lead.other_emails or lead.pages_checked:
                    with st.expander("How this was found"):
                        if lead.website_reasons:
                            st.markdown("**Website match:** " + "; ".join(lead.website_reasons))
                        for note in lead.discovery_notes:
                            st.markdown(f"- {note}")
                        if lead.other_emails:
                            st.markdown(
                                "**Third-party emails ignored** (agencies, regulators, portals): "
                                + ", ".join(f"`{e}`" for e in lead.other_emails)
                            )
                        if lead.pages_checked:
                            st.markdown("**Pages checked:** " + " · ".join(lead.pages_checked))

            with tab2:
                o1, o2 = st.columns(2)
                with o1:
                    st.session_state["opt_attach"] = st.toggle(
                        "Attach sector overview", value=st.session_state["opt_attach"], key="w_opt_attach",
                        help="Adds a line to the email and attaches the branded PDF to drafts.")
                with o2:
                    st.session_state["opt_switch"] = st.toggle(
                        "Mention Jan 2027 switch-off", value=st.session_state["opt_switch"], key="w_opt_switch")
                st.session_state["opt_branded"] = st.toggle(
                    "Branded email design", value=st.session_state["opt_branded"], key="w_opt_branded",
                    help="On: SY Communications header, feature tiles, switch-off callout and a demo button."
                         " Off: a plain, personal-looking email. Applies to drafts and Zoho sends.")
                attach_overview = st.session_state["opt_attach"]

                ensure_draft(item)
                # Push this firm's saved draft into the editor when switching firms or after a rebuild
                widget_sig = (cn, item["sig"], item.get("to_ver", 0))
                if st.session_state.get("email_widget_sig") != widget_sig:
                    st.session_state["email_to"] = item["to"]
                    st.session_state["email_subject"] = item["subject"]
                    st.session_state["email_body"] = item["body"]
                    st.session_state["email_widget_sig"] = widget_sig

                email_to = st.text_input("To", key="email_to", placeholder="name@firm.co.uk")
                email_subject = st.text_input("Subject", key="email_subject")
                edited_pitch = st.text_area("Email body", key="email_body", height=380)
                if email_to != item["to"]:
                    bump_queue_editor()  # Keep the review table in step with the To box
                item.update(to=email_to, subject=email_subject, body=edited_pitch)
                if lead.emails_found and len(lead.emails_found) > 1:
                    st.caption("Other addresses found: " + ", ".join(e for e in lead.emails_found if e != email_to))
                with st.expander("👀  Preview the email as they'll see it"):
                    components.html(_email_body_html(edited_pitch, email_subject), height=820, scrolling=True)

                mailto_url = build_mailto(email_to, email_subject, edited_pitch)
                friendly = draft_filename_part(lead.company_name)
                sector_slug = re.sub(r"[^A-Za-z0-9]+", "_", SECTOR_COPY.get(current_vert_name, {}).get("sector_plural", "sector")).strip("_")

                overview_name = f"{BRAND_FILE}_{sector_slug}_overview_{friendly}.pdf"
                overview_bytes = create_sector_overview_pdf(lead, current_vert_name) if attach_overview else None
                eml_bytes = build_eml_draft(
                    email_to, email_subject, edited_pitch,
                    attachments=[(overview_name, overview_bytes)] if overview_bytes else None,
                )
                st.download_button(
                    label=("📎  Email draft with PDF attached" if attach_overview else "📎  Email draft (.eml)"),
                    data=eml_bytes,
                    file_name=f"Email_to_{friendly}.eml",
                    mime="message/rfc822",
                    type="primary",
                    help="Downloads a ready-to-send draft. Click the downloaded file to open it in Outlook with the PDF attached.",
                    **FULL_WIDTH,
                )
                st.caption(
                    "Click the downloaded file to open it in Outlook as a new draft with the PDF attached,"
                    " then check it and hit Send. (Apple Mail: open it, then Message → Send Again.)"
                )
                b1, b2, b3 = st.columns(3)
                with b1:
                    st.link_button("✉️ Email only", mailto_url, **FULL_WIDTH,
                                   help="Opens your email app with the text filled in (no attachment). Handy for Gmail.")
                with b2:
                    if overview_bytes:
                        st.download_button(
                            label="⬇ Overview PDF",
                            data=overview_bytes,
                            file_name=overview_name,
                            mime="application/pdf",
                            **FULL_WIDTH,
                        )
                with b3:
                    st.download_button(
                        label="⬇ Lead dossier",
                        data=bytes(create_pdf_dossier(
                            lead=lead,
                            vertical_name=current_vert_name,
                            pitch_text=edited_pitch,
                            target_crms=vert_cfg["crms"],
                        )),
                        file_name=f"dossier_{friendly.lower()}.pdf",
                        mime="application/pdf",
                        **FULL_WIDTH,
                    )

                # Send this one firm through Zoho (adds it as a lead first if needed)
                if zoho_on() and not is_sent and zrec.get("status") != "customer":
                    try:
                        zpop = st.popover("🚀  Send this email via Zoho", key=f"zs1_{cn}_{st.session_state.get('sent_log_ver', 0)}",
                                          disabled=not email_to, **FULL_WIDTH)
                    except TypeError:
                        zpop = st.popover("🚀  Send this email via Zoho", disabled=not email_to, **FULL_WIDTH)
                    with zpop:
                        senders_, s_err_ = zoho_senders()
                        if s_err_:
                            st.caption(s_err_)
                        elif senders_:
                            idx_ = st.session_state.get("zs_from", 0)
                            frm_ = senders_[idx_] if 0 <= idx_ < len(senders_) else senders_[0]
                            st.markdown(f"Send to **{esc(email_to)}** from **{esc(frm_['email'])}**?")
                            st.caption("Logged on the Zoho lead with a note, and the status moves to Attempted to Contact.")
                            if st.button("Yes, send it now", type="primary", key=f"zs1_go_{cn}", **FULL_WIDTH):
                                send_via_zoho([cn], frm_, origin="dossier")
                                st.rerun()
                show_zoho_push_result("dossier")

                # Sent tick: saved to the permanent log, so it's there next time anyone opens the app
                sent_now = st.checkbox(
                    "✅  Handled: tick once this email has gone",
                    value=is_sent,
                    key=f"sent_chk_{cn}_{st.session_state.get('sent_log_ver', 0)}",
                    help="Saved permanently, and shows as Contacted in future searches.",
                )
                if sent_now != is_sent:
                    record_sent({cn: sent_record(item) if sent_now else None})
                    st.rerun()
                if is_sent:
                    rec = log_now[cn]
                    who = f" by {rec['sent_by']}" if rec.get("sent_by") else ""
                    st.caption(f"Marked sent{who} on {sent_label(rec)[2:]} to {rec.get('to') or 'unknown address'}.")

                tips = []
                if len(mailto_url) > 1900:
                    tips.append("This email is long, so the 'Email only' button may cut it short in some apps. The draft file isn't affected.")
                if not email_to:
                    tips.append("No email address found. Add one in the To box first.")
                for tip in tips:
                    st.caption("💡 " + tip)

                if st.toggle("Show copy-ready email", value=False, key="opt_copy"):
                    st.caption("Use the copy icon at the top-right of each box.")
                    st.code(email_subject, language=None)
                    st.code(edited_pitch, language=None)


# ---------------- Review queue (full width) ----------------
def _data_editor(df: pd.DataFrame, **kwargs):
    try:
        return st.data_editor(df, width="stretch", **kwargs)
    except Exception:
        return st.data_editor(df, use_container_width=True, **kwargs)


def _website_label(lead: ScrapedLead) -> str:
    return (lead.website_confidence or "Not found") if lead.website_url else "Not found"


def _mark_handled_popover(ids: List[str], label_noun: str, key: str) -> None:
    pop_kwargs = dict(disabled=not ids, **FULL_WIDTH)
    label = f"✅  Mark {len(ids)} as handled"
    try:  # A fresh key after each save closes the pop-up
        pop = st.popover(label, key=f"{key}_{st.session_state.get('sent_log_ver', 0)}", **pop_kwargs)
    except TypeError:
        pop = st.popover(label, **pop_kwargs)
    with pop:
        st.markdown(f"Mark **{len(ids)} selected {label_noun}** as handled?")
        st.caption("They'll show as contacted in future searches. You can untick any of them afterwards.")
        if st.button("Yes, mark as handled", type="primary", key=f"{key}_confirm", **FULL_WIDTH):
            record_sent({c: sent_record(queue[c]) for c in ids})
            st.rerun()


def _apply_editor(edited: pd.DataFrame, log_now: Dict[str, Any]) -> None:
    """Writes table edits back to the queue (selection, email, website, handled tick)."""
    sent_changes: Dict[str, Optional[Dict[str, Any]]] = {}
    moved = False
    for _, row in edited.iterrows():
        c = row["cn"]
        if c not in queue:
            continue
        if "Select" in row:
            queue[c]["include"] = bool(row["Select"])
        if "Contact" in row:
            shown = infer_contact_name_and_role(queue[c]["lead"], queue[c]["vertical"])[0]
            new_name = str(row["Contact"] or "").strip()
            if new_name and new_name != shown:
                save_contact(c, name=new_name)
                moved = True
        if "Email" in row:
            new_to = str(row["Email"] or "").strip()
            if new_to != queue[c]["to"]:
                if bool(new_to) != bool(queue[c]["to"]):
                    moved = True  # Firm changes group: redraw straight away
                if new_to:
                    err = save_contact(c, email=new_to)  # Saved permanently, like LinkedIn finds
                    if err:
                        st.session_state["table_error"] = err
                        moved = True
                        continue
                moved = moved or (bool(new_to) != bool(queue[c]["to"]))
                queue[c]["to"] = new_to
                queue[c]["to_ver"] = queue[c].get("to_ver", 0) + 1
        if "Website" in row:
            queue[c]["website_input"] = str(row["Website"] or "").strip()
        if bool(row["Handled"]) != (c in log_now):
            sent_changes[c] = sent_record(queue[c]) if row["Handled"] else None
    if sent_changes:
        record_sent(sent_changes)
        st.rerun()
    if moved:  # An email was added/removed, so the firm changes group
        bump_queue_editor()
        st.rerun()



def render_zoho_send_panel(ready_sel: List[str], log_now: Dict[str, Any]) -> None:
    with st.container(key="card-zoho-send"):
        render_html(
            '<div style="display:flex;align-items:center;gap:10px;margin:6px 0 2px 0">'
            f'<span style="font-weight:700;color:var(--text)">🚀 Send via Zoho</span>{chip("Logged on each lead", "accent")}</div>'
            '<div style="font-size:.8rem;color:var(--muted);margin-bottom:6px">Sends each pitch from Zoho with its PDF,'
            " logs it on the firm's Zoho lead, adds a note and sets the status to Attempted to Contact.</div>")
        show_zoho_push_result("panel")
        store = get_zoho_store()
        missing = [c for c in st.session_state.get("queue_order", []) if c in st.session_state.get("queue", {})
                   and c not in store and zoho_worthy(c)]
        if missing and st.button(f"➕  Add {len(missing)} firm(s) not yet in Zoho", key="zoho_add_missing"):
            s_ = push_to_zoho_leads(missing)
            st.session_state["zoho_add_msg"] = (
                "Zoho needs a new key first: open Connect Zoho in the sidebar." if "permission" in s_["error"]
                else zoho_summary_text(s_) or ("Couldn't add: " + "; ".join(s_["error"][:3]) if s_["error"] else "Nothing new to add."))
            st.rerun()
        if st.session_state.get("zoho_add_msg"):
            st.info(st.session_state.pop("zoho_add_msg"))
        senders, err = zoho_senders()
        if err:
            if "permission" in err.lower() or "scope" in err.lower():
                st.info("Sending needs the full Zoho permissions: open Connect Zoho in the sidebar and connect again.")
            else:
                st.error(err)
            return
        if not senders:
            st.warning("Zoho didn't return any address to send from.")
            return
        fixed = None
        if QUICK_MODE:  # Telemarketer login: one fixed From address, no choice
            fixed = next((dict(a, user_name=a.get("user_name") or get_sender().get("name") or "")
                          for a in senders if (a.get("email") or "").strip().lower() == QUICK_FROM), None)
            if not fixed:
                st.error(f"Zoho won't send from {QUICK_FROM} yet, so nothing can be sent. Sam needs to add it in Zoho CRM:"
                         " Setup → Channels → Email → Organization Emails → Add, then click the link in the"
                         " verification email that arrives in that inbox.")
                return
            st.caption(f"✉️ Sending from **{esc(fixed['email'])}**"
                       + (f" as {esc(fixed['user_name'])}" if fixed.get("user_name") else ""))
        else:
            st.selectbox("Send from", list(range(len(senders))), key="zs_from",
                         format_func=lambda i: f"{senders[i].get('user_name') or ''} <{senders[i]['email']}>".strip()
                         + (" · org address" if senders[i].get("type") == "org_email" else ""))
        kinds = [SURVEY_KIND_PITCH, SURVEY_KIND_FORM]
        st.radio("Email to send", kinds, key="zs_kind", horizontal=True,
                 help="The survey is a short form (sites, users, handsets, numbers) that fills in the lead in Zoho.")
        survey = st.session_state.get("zs_kind") == SURVEY_KIND_FORM
        if survey and not survey_form_url():
            st.warning("The survey form link isn't set up yet: add SURVEY_FORM_URL to this app's Secrets.")
            return
        ids = [c for c in ready_sel if (store.get(c) or {}).get("status") != "customer"]
        customers = len(ready_sel) - len(ids)
        if customers:
            st.caption(f"⚠️ {customers} selected firm(s) are already customers in Zoho, so they're left out.")
        sent_today = zoho_sent_today(log_now)
        left = max(0, ZOHO_SEND_LIMIT - sent_today)
        if len(ids) > left:
            st.warning(f"Zoho allows {ZOHO_SEND_LIMIT} emails a day and {sent_today} have gone today, so only the first {left} will be sent.")
            ids = ids[:left]
        label = (f"📋  Send the survey to {len(ids)} via Zoho" if survey
                 else f"🚀  Send {len(ids)} {'email' if len(ids) == 1 else 'emails'} via Zoho")
        try:
            pop = st.popover(label, key=f"zs_pop_{st.session_state.get('sent_log_ver', 0)}", disabled=not ids, **FULL_WIDTH)
        except TypeError:
            pop = st.popover(label, disabled=not ids, **FULL_WIDTH)
        with pop:
            idx = st.session_state.get("zs_from", 0)
            frm = fixed or (senders[idx] if 0 <= idx < len(senders) else senders[0])
            st.markdown(f"Send **{len(ids)} {'survey forms' if survey else 'emails'}** now from **{esc(frm['email'])}**?")
            st.caption("This can't be undone. Each is logged on its Zoho lead"
                       + (f" and tagged '{SURVEY_TAG}'." if survey else "."))
            if st.button("Yes, send them now", type="primary", key="zs_confirm", **FULL_WIDTH):
                send_via_zoho(ids, frm, survey=survey)
                st.rerun()
        st.caption(f"Sent via Zoho today: {sent_today} of {ZOHO_SEND_LIMIT}.")


def _group_title(emoji: str, title: str, count: int, tone: str) -> None:
    render_html(
        f'<div style="display:flex;align-items:center;gap:10px;margin:18px 0 8px 0">'
        f'<span style="font-size:1.05rem">{emoji}</span>'
        f'<span style="font-weight:700;color:var(--text)">{esc(title)}</span>{chip(str(count), tone)}</div>'
    )


if queue:
    with st.container(key="card-queue"):
        log_now = get_sent_log()
        for c in queue_order:
            ensure_draft(queue[c])
        _zs = get_zoho_store()
        not_interested = [c for c in queue_order if (_zs.get(c) or {}).get("status") == "not_interested"]
        ready_all = [c for c in queue_order if c not in log_now and queue[c]["to"] and c not in not_interested]
        noemail_all = [c for c in queue_order if c not in log_now and not queue[c]["to"] and c not in not_interested]
        handled_all = [c for c in queue_order if c in log_now]
        ver = st.session_state.get("queue_editor_ver", 0)
        stamp = now_uk().strftime("%Y-%m-%d_%H%M")

        section_header(
            "03" if st.session_state.get("view") == "quick" else "04", "Review & send",
            f"{len(queue_order)} enriched · {len(ready_all)} ready to email · {len(noemail_all)} no email found"
            f" · {len(handled_all)} handled",
        )
        _not_listed = [c for c in queue_order if not str(c).startswith("crm:")]
        if _not_listed:
            _a1, _a2 = st.columns([1.4, 2])
            if _a1.button(f"📇 Add {len(_not_listed)} to the customer list", key="pe_to_crm", **FULL_WIDTH,
                          help="Puts these enriched firms on the Customers list (skipping any already there), so they"
                               " show in the Caller and Overview."):
                _added, _there = add_queue_to_crm(_not_listed)
                st.session_state["pe_crm_msg"] = (f"📇 Added {_added} to the customer list"
                                                  + (f" ({_there} were already there)." if _there else "."))
                st.rerun()
            if st.session_state.get("pe_crm_msg"):
                _a2.success(st.session_state.pop("pe_crm_msg"))
        if not_interested:
            st.caption("⛔ Left out, tagged Not Interested in Zoho: "
                       + ", ".join(lead_display_name(queue[c]["lead"]) for c in not_interested[:6])
                       + ("…" if len(not_interested) > 6 else ""))

        # ===== 1. Ready to email =====
        _group_title("✉️", "Ready to email", len(ready_all), "good")
        if not ready_all:
            st.caption("No firms with an email address yet. Check the No email found list below.")
        else:
            st.caption("These firms have an email address. Untick any you don't want, fix addresses inline, then export.")
            rdf = pd.DataFrame([{
                "cn": c,
                "Select": bool(queue[c]["include"]),
                "Handled": False,
                "Firm": lead_display_name(queue[c]["lead"]),
                "Contact": infer_contact_name_and_role(queue[c]["lead"], queue[c]["vertical"])[0],
                "Email": queue[c]["to"],
                "Phone": (queue[c]["lead"].phones_found or [""])[0],
                "LinkedIn": getattr(queue[c]["lead"], "linkedin_url", None) or linkedin_people_url(queue[c]["lead"]),
                "Website match": _website_label(queue[c]["lead"]),
                "Zoho": zoho_label(c),
            } for c in ready_all])
            edited = _data_editor(
                rdf, hide_index=True, num_rows="fixed", key=f"q_ready_{ver}",
                height=min(38 + 35 * len(rdf), 390),
                column_order=["Select", "Handled", "Firm", "Contact", "Email", "LinkedIn", "Phone", "Website match", "Zoho"],
                disabled=["Firm", "Phone", "LinkedIn", "Website match", "Zoho"],
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", width="small"),
                    "Handled": st.column_config.CheckboxColumn("Handled ✓", width="small", help="Tick once emailed. Saved permanently."),
                    "Firm": st.column_config.TextColumn("Firm", width="medium"),
                    "Contact": st.column_config.TextColumn("Contact ✎", width="small", help="Type the right first name or full name. Saved permanently."),
                    "Email": st.column_config.TextColumn("Email ✎", width="medium", help="Clear it to move the firm to No email found"),
                    "LinkedIn": st.column_config.LinkColumn("LinkedIn", width="small", display_text="Find ↗"),
                    "Phone": st.column_config.TextColumn("Phone", width="small"),
                    "Website match": st.column_config.TextColumn("Website", width="small"),
                },
            )
            _apply_editor(edited, log_now)
            ready_sel = [c for c in ready_all if queue[c]["include"]]
            r1, r2 = st.columns([1.4, 1])
            with r1:
                if ready_sel:
                    zip_bytes, n_written, _ = build_drafts_zip([queue[c] for c in ready_sel], st.session_state["opt_attach"])
                    st.download_button(
                        f"📦  Download {n_written} email {'draft' if n_written == 1 else 'drafts'} (.zip)",
                        data=zip_bytes,
                        file_name=f"{BRAND_FILE}_drafts_{stamp}.zip",
                        mime="application/zip", type="primary",
                        help="One ready-to-send Outlook draft per selected firm, each with its PDF attached.",
                        **FULL_WIDTH,
                    )
                else:
                    st.button("📦  Select firms to export", disabled=True, **FULL_WIDTH)
            with r2:
                _mark_handled_popover(ready_sel, "firms", "pop_ready")
            if zoho_on():
                render_zoho_send_panel(ready_sel, log_now)

        # ===== 2. No email found =====
        _group_title("📞", "No email found", len(noemail_all), "warn")
        if not noemail_all:
            st.caption("Every enriched firm has an email address.")
        else:
            st.caption(
                "Click **Find ↗** to look the firm up on LinkedIn, then type the right contact and business email"
                " straight into the row: the firm moves up to Ready to email with a personalised draft. Or send them"
                " to the shared call list, or paste their real website and hit Retry."
            )
            if st.session_state.get("table_error"):
                st.error(st.session_state.pop("table_error"))
            calls_now = get_call_list()
            ndf = pd.DataFrame([{
                "cn": c,
                "Select": bool(queue[c]["include"]),
                "Handled": False,
                "Firm": lead_display_name(queue[c]["lead"]),
                "Contact": infer_contact_name_and_role(queue[c]["lead"], queue[c]["vertical"])[0],
                "Phone": (queue[c]["lead"].phones_found or [""])[0],
                "LinkedIn": getattr(queue[c]["lead"], "linkedin_url", None) or linkedin_people_url(queue[c]["lead"]),
                "Email": "",
                "Website": queue[c].get("website_input") or (queue[c]["lead"].website_url or ""),
                "Zoho": zoho_label(c),
                "Why": ("📞 In call list" if c in calls_now else "No website" if not queue[c]["lead"].website_url
                        else "No email on site"),
            } for c in noemail_all])
            edited = _data_editor(
                ndf, hide_index=True, num_rows="fixed", key=f"q_noemail_{ver}",
                height=min(38 + 35 * len(ndf), 390),
                column_order=["Select", "Handled", "Firm", "Zoho", "LinkedIn", "Contact", "Email", "Phone", "Website", "Why"],
                disabled=["Firm", "Phone", "LinkedIn", "Why", "Zoho"],
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", width="small"),
                    "Handled": st.column_config.CheckboxColumn("Handled ✓", width="small", help="Tick once called or dealt with."),
                    "Firm": st.column_config.TextColumn("Firm", width="medium"),
                    "LinkedIn": st.column_config.LinkColumn("LinkedIn", width="small", display_text="Find ↗",
                                                            help="Opens a LinkedIn search for this firm's director in a new tab"),
                    "Contact": st.column_config.TextColumn("Contact ✎", width="small", help="Type the name you found. Saved permanently."),
                    "Phone": st.column_config.TextColumn("Phone", width="small"),
                    "Email": st.column_config.TextColumn("Add email ✎", width="medium", help="Type an address to move this firm to Ready to email"),
                    "Website": st.column_config.TextColumn("Website (editable)", width="medium", help="Paste the right website, then Retry"),
                    "Why": st.column_config.TextColumn("Why", width="small"),
                },
            )
            _apply_editor(edited, log_now)
            noemail_sel = [c for c in noemail_all if queue[c]["include"]]
            retry_ids = [
                c for c in noemail_sel
                if queue[c].get("website_input") and domain_of(queue[c]["website_input"]) != domain_of(queue[c]["lead"].website_url or "")
            ]
            to_call = [c for c in noemail_sel if c not in calls_now and queue[c]["lead"].phones_found]
            no_phone = [c for c in noemail_sel if c not in calls_now and not queue[c]["lead"].phones_found]
            if st.button(
                f"📞  Add {len(to_call)} to the call list" if to_call else "📞  Nothing new to add to the call list",
                type="primary", disabled=not to_call, key="add_to_calls", **FULL_WIDTH,
                help="Saves the selected firms (contact, phone and verified website) to the shared call list page.",
            ):
                save_calls({c: call_record_from_item(queue[c]) for c in to_call}, f"{len(to_call)} added")
                for c in to_call:
                    queue[c]["include"] = False
                bump_queue_editor()
                st.session_state["calls_flash"] = f"{len(to_call)} firms added to the call list."
                st.rerun()
            if st.session_state.get("calls_flash"):
                st.success(st.session_state.pop("calls_flash") + " Open **Call list** in the sidebar to start calling.")
            if no_phone:
                st.caption(f"💡 {len(no_phone)} selected {'firm has' if len(no_phone) == 1 else 'firms have'} no phone number,"
                           " so can't go on the call list. Paste their website and hit Retry to look again.")
            look_ids = [c for c in noemail_sel if c not in retry_ids and queue[c]["lead"].website_url]
            if st.button(f"🔎  Look again for emails on {len(look_ids)} {'website' if len(look_ids) == 1 else 'websites'}",
                         disabled=not look_ids, key="look_again", **FULL_WIDTH,
                         help="Checks the selected firms' websites again with the improved email finder (contact,"
                              " privacy and terms pages, and emails on a different domain that match the firm's name)."
                              " No Companies House or Google lookups, so it's quick and free."):
                n_look, n_found, n_zoho = rescan_for_emails(look_ids)
                st.session_state["calls_flash_look"] = (
                    f"Looked again at {n_look} websites: found an email for {n_found}"
                    + (f" (now under Ready to email{f'; added to {n_zoho} Zoho leads' if n_zoho else ''})." if n_found else ".")
                )
                st.rerun()
            if st.session_state.get("calls_flash_look"):
                st.success(st.session_state.pop("calls_flash_look"))
            n1, n2, n3 = st.columns(3)
            with n1:
                if st.button(f"🔁  Retry {len(retry_ids)} with new website", disabled=not retry_ids, **FULL_WIDTH,
                             help="Re-scrapes the selected firms whose website you've changed."):
                    run_enrichment(
                        [{"Company Number": c, "Company Name": queue[c]["lead"].company_name} for c in retry_ids],
                        queue[retry_ids[0]]["vertical"],
                        manual_websites={c: queue[c]["website_input"] for c in retry_ids},
                    )
                    st.rerun()
            with n2:
                st.download_button(
                    f"📋  Call list: {len(noemail_sel)} (.csv)",
                    data=build_lead_list_csv([queue[c] for c in noemail_sel], log_now),
                    file_name=f"{BRAND_FILE}_call_list_{stamp}.csv",
                    mime="text/csv", disabled=not noemail_sel,
                    help="Selected firms with phone numbers, directors and websites. Opens in Excel.",
                    **FULL_WIDTH,
                )
            with n3:
                _mark_handled_popover(noemail_sel, "firms", "pop_noemail")

        # ===== 3. Handled =====
        if handled_all:
            with st.expander(f"✓ Handled ({len(handled_all)})"):
                hdf = pd.DataFrame([{
                    "cn": c,
                    "Handled": True,
                    "Status": f"{log_now[c].get('status') or 'Emailed'} {sent_label(log_now[c])[2:]}",
                    "Firm": lead_display_name(queue[c]["lead"]),
                    "Sent to": log_now[c].get("to") or "",
                    "By": log_now[c].get("sent_by") or "",
                } for c in handled_all])
                edited = _data_editor(
                    hdf, hide_index=True, num_rows="fixed", key=f"q_handled_{ver}",
                    column_order=["Handled", "Status", "Firm", "Sent to", "By"],
                    disabled=["Status", "Firm", "Sent to", "By"],
                    column_config={"Handled": st.column_config.CheckboxColumn("Handled ✓", width="small", help="Untick to move it back")},
                )
                _apply_editor(edited, log_now)

        # ===== Footer =====
        st.write("")
        f1, f2, _ = st.columns([1.3, 0.8, 1.4])
        with f1:
            st.download_button(
                f"📋  Full lead list: {len(queue_order)} firms (.csv)",
                data=build_lead_list_csv([queue[c] for c in queue_order], log_now),
                file_name=f"{BRAND_FILE}_lead_list_{stamp}.csv",
                mime="text/csv", **FULL_WIDTH,
            )
        with f2:
            if st.button("Clear queue", **FULL_WIDTH, help="Empty the review queue (handled ticks are kept)."):
                st.session_state["queue"] = {}
                st.session_state["queue_order"] = []
                bump_queue_editor()
                st.rerun()


# ---------------- Late-rendered pieces (reflect this run's state) ----------------
if queue:
    active_step = 4
elif st.session_state.get("selected_rows_data"):
    active_step = 3
elif st.session_state.get("discovered_leads"):
    active_step = 2
else:
    active_step = 1
render_html(quick_hero_html() if st.session_state.get("view") == "quick" else hero_html(active_step), target=hero_slot)
render_html(
    '<div class="pe-stats">'
    f'<div class="pe-stat"><div class="v">{st.session_state["stat_firms"]}</div><div class="l">Firms</div></div>'
    f'<div class="pe-stat"><div class="v">{len(queue)}</div><div class="l">Enriched</div></div>'
    f'<div class="pe-stat"><div class="v">{len(get_sent_log())}</div><div class="l">Handled</div></div>'
    "</div>",
    target=sidebar_stats_slot,
)
