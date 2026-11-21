"""Shared design system and presentation helpers for the AuthMark interface."""

from __future__ import annotations

from html import escape

import streamlit as st

# Inline line icons (24x24, stroke based) so no external icon font is needed.
_ICON_PATHS = {
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="m11 12 9-9"/><path d="m16 7 3 3"/><path d="m14 9 2 2"/>',
    "file-sign": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h4"/><path d="M14 3v5h5"/><path d="M19 8v3"/><path d="M8 12h6"/><path d="M8 16h3"/><path d="m13 20 1-3 6-6a1.4 1.4 0 0 1 2 2l-6 6z"/>',
    "shield-check": '<path d="M12 3 5 6v5c0 4.4 2.9 8.2 7 10 4.1-1.8 7-5.6 7-10V6z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "text": '<path d="M5 6V4h14v2"/><path d="M12 4v16"/><path d="M9 20h6"/>',
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "file": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6"/><path d="M9 17h4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
    "x": '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6"/><path d="m15 9-6 6"/>',
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
}


def icon(name: str, size: int = 22) -> str:
    """Return an inline SVG icon that inherits the surrounding text colour."""
    return (
        f'<svg class="am-icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{_ICON_PATHS[name]}</svg>'
    )


def _mask(name: str) -> str:
    """Build a CSS data-URI mask for a sidebar navigation icon."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{_ICON_PATHS[name]}</svg>"
    )
    encoded = svg.replace("<", "%3C").replace(">", "%3E").replace('"', "'").replace("#", "%23")
    return f'url("data:image/svg+xml,{encoded}")'


_NAV_ICONS = ["home", "key", "file-sign", "shield-check", "text"]


def _nav_icon_css() -> str:
    rules = []
    for index, name in enumerate(_NAV_ICONS, start=1):
        mask = _mask(name)
        for selector in (
            f'[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type({index}) p::before',
            f'[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type({index}) > label p::before',
        ):
            rules.append(f"{selector} {{ -webkit-mask-image: {mask}; mask-image: {mask}; }}")
    return "\n".join(rules)


_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --am-bg: #0b0f12;
  --am-panel: #11171b;
  --am-panel-2: #161d22;
  --am-border: #27323a;
  --am-border-soft: #1d262c;
  --am-text: #e6edf2;
  --am-muted: #a3b0ba;
  --am-accent: #22d3ee;
  --am-accent-deep: #0e3b43;
  --am-good: #34d399;
  --am-bad: #f87171;
  --am-radius: 14px;
}

html, body, .stApp, .stApp :is(p, h1, h2, h3, h4, label, li, a, button, input, textarea, div) {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
/* Keep Streamlit's own icon font for built-in icons (password eye, upload arrow, ...) */
[data-testid="stIconMaterial"], .material-symbols-rounded {
  font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
}
.stApp { background: var(--am-bg); }

/* Layout */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display: none; }
.block-container { max-width: 1320px; padding-top: 3.2rem; padding-bottom: 4rem; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: #0d1216;
  border-right: 1px solid var(--am-border-soft);
  min-width: 290px; max-width: 290px;
}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { display: none; }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarUserContent"] { padding-top: 1.6rem; }
.am-brand { font-size: 2rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; margin: .2rem 0 .35rem; }
.am-brand span { color: var(--am-accent); }
.am-tagline { color: var(--am-muted); font-size: .85rem; margin-bottom: 1.8rem; }

[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: .72rem .9rem; border-radius: 12px; width: 100%; cursor: pointer;
  border: 1px solid transparent; transition: background .15s, border-color .15s;
}
/* Hide the radio dot in both the current and the older Streamlit markup */
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child,
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] label p {
  display: flex; align-items: center; gap: .85rem; font-weight: 600; font-size: .98rem;
  color: #c4cfd7; margin: 0;
}
[data-testid="stSidebar"] [role="radiogroup"] label p::before {
  content: ""; width: 22px; height: 22px; flex: none; background: currentColor;
  -webkit-mask-size: contain; mask-size: contain; -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
  -webkit-mask-position: center; mask-position: center;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #131b21; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, #0f3a40, #0e2f35); border-color: #15525a;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: #fff; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p::before { background: var(--am-accent); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:focus-visible) { outline: 2px solid rgba(34,211,238,.35); outline-offset: 1px; }
.am-side-foot {
  display: flex; align-items: center; gap: .6rem; color: var(--am-muted); font-size: .82rem;
  padding-top: 1.2rem; margin-top: 1.4rem; border-top: 1px solid var(--am-border);
}

/* Page header */
.am-eyebrow { color: var(--am-accent); font-size: .78rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
.stApp h1.am-title { color: var(--am-text); font-size: 3rem; font-weight: 700; letter-spacing: -.025em; line-height: 1.12; margin: .35rem 0 .6rem; padding: 0; }
.stApp h1.am-title .am-accent { color: var(--am-accent); }
.am-subtitle { color: #cbd5dc; font-size: 1.08rem; max-width: 780px; margin: 0 0 2rem; line-height: 1.55; }

/* Section headings */
.am-bar-heading { display: flex; align-items: center; gap: .8rem; margin: 2.2rem 0 .5rem; }
.am-bar-heading::before { content: ""; width: 4px; height: 1.7rem; background: var(--am-accent); border-radius: 2px; }
.am-bar-heading h2 { font-size: 1.65rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -.01em; }
.am-body { color: #cbd5dc; max-width: 780px; line-height: 1.65; }
.am-section { display: flex; align-items: center; gap: .7rem; margin: 2.2rem 0 1rem; color: var(--am-accent); }
.am-section h3 { color: var(--am-text); font-size: 1.35rem; font-weight: 700; margin: 0; padding: 0; }
.am-section.plain { color: var(--am-text); }

/* Cards */
.am-card {
  display: flex; gap: 1.1rem; align-items: flex-start; min-height: 150px;
  border: 1px solid var(--am-border); border-radius: var(--am-radius); padding: 1.3rem 1.4rem;
  background: linear-gradient(180deg, var(--am-panel-2), var(--am-panel));
}
.am-card-icon {
  flex: none; width: 54px; height: 54px; border-radius: 12px; display: grid; place-items: center;
  background: #1a2730; color: var(--am-accent);
}
.am-card h3 { font-size: 1.2rem; font-weight: 700; margin: .1rem 0 .5rem; padding: 0; }
.am-card p { color: var(--am-muted); margin: 0; line-height: 1.55; font-size: .97rem; }
.am-card code, .am-chip code { font-family: 'JetBrains Mono', monospace; background: #222c33; padding: .1rem .4rem; border-radius: 6px; color: #dbe5eb; font-size: .85em; }

/* Workflow */
.am-flow {
  display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; border: 1px solid var(--am-border);
  border-radius: var(--am-radius); padding: 1.2rem 1.2rem; background: var(--am-panel);
}
.am-chip {
  font-family: 'JetBrains Mono', monospace; font-size: .76rem; background: #1a2229; color: #dbe5eb;
  padding: .65rem .7rem; text-align: center; border-radius: 10px; line-height: 1.35;
}
.am-flow .am-arrow { color: #7d8b95; display: grid; place-items: center; }
.am-flow .am-arrow svg { width: 16px; height: 16px; }
@media (min-width: 1100px) { .am-flow { flex-wrap: nowrap; } .am-flow.spread { justify-content: space-between; } }
.am-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }

/* Notes and results */
.am-note {
  display: flex; gap: 1rem; align-items: flex-start; margin: 1.4rem 0; padding: 1.15rem 1.4rem; line-height: 1.6;
  border: 1px solid #14606b; border-radius: var(--am-radius); color: #dbe9ee;
  background: linear-gradient(90deg, rgba(34,211,238,.13), rgba(34,211,238,.04));
}
.am-note .am-icon { flex: none; color: var(--am-accent); margin-top: .1rem; }
.am-result {
  display: flex; gap: 1.1rem; align-items: center; margin: 1.2rem 0; padding: 1.3rem 1.5rem;
  border-radius: var(--am-radius); border: 1px solid;
}
.am-result.good { border-color: #1b6b52; background: linear-gradient(90deg, rgba(52,211,153,.16), rgba(52,211,153,.04)); color: var(--am-good); }
.am-result.bad { border-color: #7f2d2d; background: linear-gradient(90deg, rgba(248,113,113,.16), rgba(248,113,113,.04)); color: var(--am-bad); }
.am-result h3 { margin: 0 0 .15rem; font-size: 1.3rem; padding: 0; color: inherit; }
.am-result p { margin: 0; color: #cbd5dc; }
.am-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin: 0 0 1.6rem; }
.am-fact { border: 1px solid var(--am-border); border-radius: var(--am-radius); padding: .95rem 1.1rem; background: var(--am-panel); }
.am-fact b { display: block; font-size: 1.02rem; }
.am-fact span { color: var(--am-muted); font-size: .88rem; }

/* Streamlit widgets */
[data-testid="stForm"] {
  border: 1px solid var(--am-border); border-radius: var(--am-radius); padding: 1.6rem 1.6rem 1.4rem;
  background: linear-gradient(180deg, var(--am-panel-2), var(--am-panel));
}
[data-testid="stWidgetLabel"] p { font-weight: 600; color: #dbe5eb; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] {
  background: #0c1114 !important; border-radius: 10px !important; border-color: var(--am-border) !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within { border-color: var(--am-accent) !important; }
[data-testid="stFileUploaderDropzone"] {
  background: #0c1114; border: 1.5px dashed #34414a; border-radius: 12px;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--am-accent); }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 10px; font-weight: 600; padding: .6rem 1.3rem; border: 1px solid var(--am-border);
  background: var(--am-panel-2); color: var(--am-text); transition: border-color .15s, background .15s;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--am-accent); color: #fff; }
button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: var(--am-accent) !important; color: #04242a !important; border-color: var(--am-accent) !important;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover { background: #67e3f5 !important; }
button:focus-visible { outline: 2px solid var(--am-accent); outline-offset: 2px; }
[data-testid="stAlert"] { border-radius: var(--am-radius); }
[data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--am-border); }
[data-baseweb="tab"] { font-weight: 600; }
[data-baseweb="tab-highlight"] { background: var(--am-accent) !important; }

@media (max-width: 760px) {
  .stApp h1.am-title { font-size: 2.2rem; }
  .am-card { flex-direction: column; }
}
"""


def apply_styles() -> None:
    """Inject the shared AuthMark design system into the current page."""
    st.markdown(f"<style>{_BASE_CSS}\n{_nav_icon_css()}</style>", unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render the AuthMark wordmark and tagline at the top of the sidebar."""
    st.markdown(
        '<div class="am-brand">Auth<span>Mark</span></div>'
        '<div class="am-tagline">Authenticity. Integrity. Assurance.</div>',
        unsafe_allow_html=True,
    )


def sidebar_footer() -> None:
    """Render the cryptographic suite summary at the bottom of the sidebar."""
    st.markdown(
        f'<div class="am-side-foot">{icon("lock", 18)}<span>RSA-3072 · RSA-PSS · SHA-256</span></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, accent: str | None = None) -> None:
    """Render the shared eyebrow, title (with accented final word), and subtitle."""
    accent_word = accent or title.rsplit(" ", 1)[-1]
    plain = title[: len(title) - len(accent_word)].rstrip()
    st.markdown(
        '<div class="am-eyebrow">AuthMark Digital Trust System</div>'
        f'<h1 class="am-title">{escape(plain)} <span class="am-accent">{escape(accent_word)}</span></h1>'
        f'<p class="am-subtitle">{escape(subtitle)}</p>',
        unsafe_allow_html=True,
    )


def bar_heading(text: str) -> None:
    """Render a large heading with an accent bar."""
    st.markdown(f'<div class="am-bar-heading"><h2>{escape(text)}</h2></div>', unsafe_allow_html=True)


def body_text(text: str) -> None:
    """Render a muted-contrast body paragraph."""
    st.markdown(f'<p class="am-body">{escape(text)}</p>', unsafe_allow_html=True)


def section_heading(text: str, icon_name: str | None = None) -> None:
    """Render a section heading, optionally prefixed by an accent icon."""
    icon_html = icon(icon_name, 24) if icon_name else ""
    plain = "" if icon_name else " plain"
    st.markdown(
        f'<div class="am-section{plain}">{icon_html}<h3>{escape(text)}</h3></div>',
        unsafe_allow_html=True,
    )


def feature_grid(cards: list[tuple[str, str, str]]) -> None:
    """Render equal-height icon cards from (icon, title, trusted description HTML) tuples."""
    items = "".join(
        f'<div class="am-card"><div class="am-card-icon">{icon(icon_name, 28)}</div>'
        f"<div><h3>{escape(title)}</h3><p>{description_html}</p></div></div>"
        for icon_name, title, description_html in cards
    )
    st.markdown(f'<div class="am-grid">{items}</div>', unsafe_allow_html=True)


def workflow(steps: list[str], spread: bool = False) -> None:
    """Render a left-to-right process strip from trusted step labels.

    Set ``spread`` to distribute the steps across the full width of a narrow container.
    """
    arrow = f'<span class="am-arrow">{icon("arrow", 20)}</span>'
    chips = arrow.join(f'<span class="am-chip">{step}</span>' for step in steps)
    extra = " spread" if spread else ""
    st.markdown(f'<div class="am-flow{extra}">{chips}</div>', unsafe_allow_html=True)


def fact_row(facts: list[tuple[str, str]]) -> None:
    """Render a row of short title/detail facts."""
    items = "".join(
        f'<div class="am-fact"><b>{escape(title)}</b><span>{escape(detail)}</span></div>'
        for title, detail in facts
    )
    st.markdown(f'<div class="am-facts">{items}</div>', unsafe_allow_html=True)


def security_note(text: str) -> None:
    """Render a concise security information callout."""
    st.markdown(
        f'<div class="am-note">{icon("info", 26)}<div>{escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


def result_banner(valid: bool, title: str, detail: str) -> None:
    """Render a prominent valid/invalid verification outcome."""
    kind, icon_name = ("good", "check") if valid else ("bad", "x")
    st.markdown(
        f'<div class="am-result {kind}" role="status">{icon(icon_name, 34)}'
        f"<div><h3>{escape(title)}</h3><p>{escape(detail)}</p></div></div>",
        unsafe_allow_html=True,
    )
