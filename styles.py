"""Look and feel for the app: one CSS block plus a few fixed HTML snippets.

Everything in this file is fixed text written by us. No submitted code, filename,
or tool output is ever put into these HTML strings, so they are safe to render
with unsafe_allow_html=True.
"""

APP_NAME = "AI Code Reviewer"

CSS = """
<style>
.block-container { max-width: 1240px; padding-top: 2.2rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: #0F1424;
    border-right: 1px solid rgba(139, 92, 246, 0.18);
}
.brand { display: flex; align-items: center; gap: 12px; margin: 6px 0 22px 0; }
.brand-logo {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #8B5CF6, #22D3EE);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 22px; font-weight: 700;
}
.brand-name { font-size: 1.15rem; font-weight: 800; color: #F1F4FB; line-height: 1.1; }
.brand-sub { font-size: 0.68rem; letter-spacing: 0.08em; color: #8F9BB8; margin-top: 3px; }
.side-card {
    background: linear-gradient(160deg, #1A1F3A, #151B2E);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 14px; padding: 14px 16px; margin-bottom: 22px;
}
.side-card b { color: #F1F4FB; }
.side-card p { color: #A9B4CE; font-size: 0.85rem; margin: 6px 0 0 0; line-height: 1.5; }
.side-label {
    font-size: 0.68rem; letter-spacing: 0.14em; font-weight: 700;
    color: #8F9BB8; margin: 8px 0 10px 0;
}
.cap { color: #D5DCEE; font-size: 0.9rem; margin: 7px 0; }
.dot-on, .dot-off {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 9px;
}
.dot-on { background: #34D399; }
.dot-off { border: 1.5px solid #8F9BB8; }
.cap-planned { color: #A9B4CE; }

/* ---------- Hero ---------- */
.eyebrow {
    color: #22D3EE; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.2em; margin-bottom: 6px;
}
.hero-title {
    font-size: 3.1rem; font-weight: 800; line-height: 1.08; color: #F5F7FF; margin: 0 0 14px 0;
}
.grad {
    background: linear-gradient(90deg, #A78BFA, #22D3EE);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
}
.hero-sub { color: #B4BEDA; font-size: 1.05rem; max-width: 760px; line-height: 1.6; margin-bottom: 16px; }
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 26px 0; }
.pill {
    background: #151B2E; border: 1px solid rgba(34, 211, 238, 0.35);
    color: #9AE6F5; border-radius: 999px; padding: 4px 13px; font-size: 0.82rem;
}

/* ---------- Section headings ---------- */
.sec { margin: 8px 0 14px 0; }
.sec-title { font-size: 1.25rem; font-weight: 700; color: #F1F4FB; }
.sec-num { color: #22D3EE; font-family: Consolas, monospace; margin-right: 8px; }
.sec-sub { color: #A9B4CE; font-size: 0.92rem; margin-top: 3px; }

/* ---------- Module cards ---------- */
.mod {
    background: #131929; border: 1px solid rgba(139, 92, 246, 0.28);
    border-radius: 14px; padding: 16px 18px; margin-bottom: 14px;
}
.mod-title { color: #F1F4FB; font-weight: 700; font-size: 1.02rem; margin-bottom: 6px; }
.mod-desc { color: #B4BEDA; font-size: 0.88rem; line-height: 1.55; margin-bottom: 10px; }
.badge-live {
    display: inline-block; color: #34D399; background: rgba(52, 211, 153, 0.10);
    border: 1px solid rgba(52, 211, 153, 0.45); border-radius: 8px;
    padding: 2px 10px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.1em;
}

/* ---------- Empty state and footer ---------- */
.empty {
    background: linear-gradient(160deg, #141B30, #161430);
    border: 1px solid rgba(34, 211, 238, 0.25); border-radius: 14px; padding: 20px 24px;
}
.empty b { color: #F1F4FB; font-size: 1.05rem; }
.empty p { color: #B4BEDA; margin: 8px 0 0 0; line-height: 1.6; }
.foot {
    border-top: 1px solid rgba(139, 92, 246, 0.22); margin-top: 40px; padding-top: 14px;
    color: #8F9BB8; font-size: 0.82rem; line-height: 1.7;
}
.foot b { color: #A78BFA; letter-spacing: 0.08em; }

/* ---------- Streamlit widgets ---------- */
[data-testid="stTextArea"] textarea {
    font-family: "Cascadia Code", Consolas, monospace; font-size: 0.93rem;
    border: 1px solid rgba(139, 92, 246, 0.45); border-radius: 12px; background: #0D1220;
}
[data-testid="stTextArea"] textarea::placeholder { color: #6F7C9C; opacity: 1; }
[data-testid="stFileUploader"] section { border-radius: 12px; border: 1px dashed rgba(139, 92, 246, 0.5); }
[data-testid="stMetric"] {
    background: #151B2E; border: 1px solid rgba(34, 211, 238, 0.30);
    border-radius: 12px; padding: 14px 16px;
}
[data-testid="stMetricValue"] { color: #22D3EE; }
[data-testid="stExpander"] { border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 10px; }
[data-testid="stButton"] { width: 100%; }
.stButton button, [data-testid="stButton"] button {
    width: 100%; border-radius: 10px; font-weight: 600; min-height: 2.7rem;
}
button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #7C3AED, #6366F1); border: none; color: #fff;
}
button[data-baseweb="tab"] { font-weight: 600; }
</style>
"""

SIDEBAR_HTML = f"""
<div class="brand">
  <div class="brand-logo">&#9670;</div>
  <div>
    <div class="brand-name">{APP_NAME}</div>
    <div class="brand-sub">PYTHON LEARNING ASSISTANT</div>
  </div>
</div>
<div class="side-card">
  <b>&#10022; Built for learning</b>
  <p>Understand your Python code, catch mistakes, and learn what to fix and why.</p>
</div>
<div class="side-label">CURRENT CAPABILITIES</div>
<div class="cap"><span class="dot-on"></span>Code input</div>
<div class="cap"><span class="dot-on"></span>.py file upload</div>
<div class="cap"><span class="dot-on"></span>Syntax validation</div>
<div class="cap"><span class="dot-on"></span>Ruff quality review</div>
<div class="cap"><span class="dot-on"></span>Radon complexity</div>
<div class="side-label" style="margin-top:22px;">PLANNED</div>
<div class="cap cap-planned"><span class="dot-off"></span>Code overview</div>
<div class="cap cap-planned"><span class="dot-off"></span>Evaluation on labelled examples</div>
"""

HERO_HTML = """
<div class="eyebrow">YOUR PYTHON WORKSPACE</div>
<div class="hero-title">Write code.<br><span class="grad">Understand more.</span></div>
<div class="hero-sub">
  Paste or upload Python code and get syntax errors, code-quality findings and
  complexity scores, each explained in plain language with a suggested next step.
</div>
<div class="pill-row">
  <span class="pill">&#10022; Beginner-friendly</span>
  <span class="pill">Never runs your code</span>
  <span class="pill">Syntax + Ruff + Radon</span>
</div>
"""

MODULE_CARDS_HTML = """
<div class="mod">
  <div class="mod-title">Syntax validation</div>
  <div class="mod-desc">Checks whether Python can parse your code. Reports the line number and
  explains common mistakes in plain language.</div>
  <span class="badge-live">AVAILABLE NOW</span>
</div>
<div class="mod">
  <div class="mod-title">Ruff code quality</div>
  <div class="mod-desc">Finds unused imports, undefined names and style issues, and keeps likely
  errors apart from style advice.</div>
  <span class="badge-live">AVAILABLE NOW</span>
</div>
<div class="mod">
  <div class="mod-title">Radon complexity</div>
  <div class="mod-desc">Scores how many paths each function has. A high score is a hint to take a
  second look, not a verdict.</div>
  <span class="badge-live">AVAILABLE NOW</span>
</div>
"""

EMPTY_STATE_HTML = """
<div class="empty">
  <b>&#9670; Workspace ready</b>
  <p>Add Python code above and click Review code. Your results will appear here.
  Your code is analysed as text and is never run.</p>
</div>
"""

FOOTER_HTML = f"""
<div class="foot">
  <b>{APP_NAME.upper()}</b> &middot; Python code review and learning assistant &middot; Data Science Capstone<br>
  Analysis is static. Submitted code is never executed, and static analysis cannot find every bug.
</div>
"""


def section_html(number: str, title: str, subtitle: str) -> str:
    """Section heading. Call it only with fixed text written in this project."""
    return (
        '<div class="sec">'
        f'<div class="sec-title"><span class="sec-num">{number} /</span>{title}</div>'
        f'<div class="sec-sub">{subtitle}</div>'
        "</div>"
    )