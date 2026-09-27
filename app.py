"""A pastel, interactive meeting-prep assistant backed by Hindsight memory."""

from __future__ import annotations

import os
from datetime import date

import streamlit as st
from hindsight_client import Hindsight


DEFAULT_BASE_URL = "https://api.hindsight.vectorize.io"


@st.cache_resource
def connect(base_url: str, api_key: str) -> Hindsight:
    """Keep one client alive across Streamlit reruns; don't close it per action."""
    return Hindsight(base_url=base_url.strip().rstrip("/"), api_key=api_key.strip())


def source_text(source: object) -> str:
    for field in ("text", "content"):
        value = getattr(source, field, None)
        if value:
            return str(value)
    return str(source)


def credentials_error(api_key: str, bank_id: str) -> str | None:
    if not api_key.strip() or not bank_id.strip():
        return "Add your Hindsight API key and memory bank ID in the sidebar first."
    if not api_key.strip().startswith("hsk_"):
        return (
            "This does not look like a Hindsight Cloud API key. It should start with "
            "hsk_. Put the full key in the API key field, not the API URL or bank ID."
        )
    return None


st.set_page_config(page_title="Meeting Prep Agent", page_icon="🪷", layout="wide")

st.markdown(
    """
    <style>
    @keyframes pastelDrift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    @keyframes riseIn {
      from { opacity: 0; transform: translateY(18px); }
      to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg, #f7f0e5 0%, #f4ebdc 48%, #f1edf5 100%);
      color: #51433a;
    }
    [data-testid="stHeader"] { background: rgba(247,240,229,.78); }
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1120px; }
    .hero {
      position: relative; overflow: hidden; padding: 2.1rem 2.2rem; border-radius: 28px; margin: 0 0 1.5rem 0;
      background: linear-gradient(115deg, #e8d5bb, #f5e5b7, #e4dbef, #ead8ce, #e8d5bb);
      background-size: 280% 280%; animation: pastelDrift 16s ease infinite, riseIn .75s ease both;
      border: 1px solid rgba(255,255,255,.72); box-shadow: 0 16px 38px rgba(105,78,55,.11);
    }
    .hero::before {
      content: ""; position: absolute; inset: -55%; pointer-events: none;
      background: radial-gradient(circle at 28% 38%, rgba(255,248,217,.58), transparent 27%),
                  radial-gradient(circle at 72% 56%, rgba(204,185,231,.36), transparent 30%),
                  radial-gradient(circle at 52% 12%, rgba(214,177,151,.30), transparent 28%);
      background-size: 170% 170%; animation: pastelDrift 13s ease-in-out infinite alternate;
    }
    .hero > * { position: relative; z-index: 1; }
    .hero-kicker { color: #735f69; font-size: .78rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .hero h1 { color: #554139; font-size: clamp(2.1rem, 4vw, 3.35rem); line-height: 1.06; margin: .55rem 0 .65rem 0; }
    .hero p { color: #67564c; font-size: 1.05rem; max-width: 700px; margin: 0; }
    [data-testid="stAppViewContainer"] .stMarkdown, [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] p { color: #55483f; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #eee3d2, #e8ddcf); }
    section[data-testid="stSidebar"] * { color: #55483f; }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .5rem; }
    [data-testid="stTabs"] button[role="tab"] {
      border-radius: 999px; padding: .65rem 1.15rem; background: #eee4d5;
      border: 1px solid rgba(133,105,82,.15); color: #625247;
    }
    [data-testid="stTabs"] button[aria-selected="true"] { background: #d9cbea; color: #51415d; }
    [data-testid="stForm"] {
      background: rgba(255,251,243,.88); padding: 1.2rem 1.35rem 1rem 1.35rem;
      border: 1px solid rgba(148,117,92,.17); border-radius: 22px;
      box-shadow: 0 14px 34px rgba(105,78,55,.09); animation: riseIn .55s ease both;
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input {
      border-radius: 13px; border-color: #dfd0bd; background: #fffdf8; color: #51433a;
    }
    div.stButton > button, [data-testid="stFormSubmitButton"] button {
      border: 0; border-radius: 999px; padding: .58rem 1.2rem;
      color: #51415d; font-weight: 700; background: linear-gradient(100deg, #ddcfee, #f2dfaa, #ead3bf);
      box-shadow: 0 7px 18px rgba(145, 113, 135, .16); transition: transform .18s ease, box-shadow .18s ease;
    }
    div.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
      transform: translateY(-2px); box-shadow: 0 10px 24px rgba(145,113,135,.24);
    }
    .soft-note { color: #79695d; font-size: .9rem; padding: .3rem .15rem; }
    [data-testid="stAlert"] { border-radius: 15px; }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }
    </style>
    <section class="hero">
      <div class="hero-kicker">Your conversations, remembered</div>
      <h1>Walk into every meeting prepared.</h1>
      <p>Save what was discussed. Before the next conversation, get the promises, concerns, and open questions back in view.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🌿 Connect your memory")
    base_url = st.text_input(
        "Hindsight API URL",
        value=os.getenv("HINDSIGHT_BASE_URL", DEFAULT_BASE_URL),
    )
    api_key = st.text_input(
        "Hindsight API key",
        value=os.getenv("HINDSIGHT_API_KEY", ""),
        type="password",
        help="Used only to connect this app to Hindsight. Never share it or commit it.",
    )
    bank_id = st.text_input(
        "Memory bank ID",
        value=os.getenv("HINDSIGHT_BANK_ID", ""),
        help="Choose the Hindsight bank where these meeting notes should live.",
    )
    st.caption("Your API key stays masked in this field. The app does not write it to a file.")

save_tab, prepare_tab = st.tabs(["📝  Add meeting notes", "✨  Prepare for a meeting"])

with save_tab:
    st.subheader("Capture the details while they’re fresh")
    st.markdown(
        '<p class="soft-note">Add the other person’s concerns, decisions, promises, and anything to follow up on.</p>',
        unsafe_allow_html=True,
    )
    with st.form("meeting_notes_form", clear_on_submit=False):
        contact = st.text_input("Person or organization", placeholder="Northstar Foods")
        meeting_date = st.date_input("Meeting date", value=date.today())
        notes = st.text_area(
            "Meeting notes",
            height=190,
            placeholder=(
                "They are concerned setup may interrupt their busy season.\n"
                "I promised to send a rollout plan by Friday.\n"
                "They prefer a short product demo."
            ),
        )
        save_clicked = st.form_submit_button("Save these notes to memory", type="primary")

    if save_clicked:
        config_problem = credentials_error(api_key, bank_id)
        if config_problem:
            st.error(config_problem)
        elif not contact.strip() or not notes.strip():
            st.warning("Add the person or organization and some meeting notes first.")
        else:
            content = (
                f"Meeting with: {contact.strip()}\n"
                f"Meeting date: {meeting_date.isoformat()}\n"
                f"Notes: {notes.strip()}"
            )
            try:
                with st.spinner("Saving this conversation to Hindsight…"):
                    connect(base_url, api_key).retain(
                        bank_id=bank_id.strip(),
                        content=content,
                        context=f"Meeting notes with {contact.strip()} on {meeting_date.isoformat()}",
                    )
                st.success(f"Saved notes about {contact.strip()} to your memory bank.")
                st.session_state["last_saved_contact"] = contact.strip()
            except Exception as error:
                st.error(f"Could not save the notes: {error}")

with prepare_tab:
    st.subheader("Get your context before the conversation")
    st.markdown(
        '<p class="soft-note">Use the same person or organization name that you used when saving notes.</p>',
        unsafe_allow_html=True,
    )
    with st.form("prep_form"):
        prep_contact = st.text_input(
            "Who are you meeting?",
            value=st.session_state.get("last_saved_contact", ""),
            placeholder="Northstar Foods",
        )
        focus = st.selectbox(
            "What should the briefing focus on?",
            ["Everything important", "Promises and follow-ups", "Their concerns", "Decisions and next steps"],
        )
        custom_focus = st.text_input(
            "Add a specific question (optional)",
            placeholder="Did I send the rollout plan?",
        )
        prep_clicked = st.form_submit_button("Build my briefing", type="primary")

    if prep_clicked:
        config_problem = credentials_error(api_key, bank_id)
        if config_problem:
            st.error(config_problem)
        elif not prep_contact.strip():
            st.warning("Enter the person or organization you are meeting.")
        else:
            focus_text = custom_focus.strip() or focus
            query = (
                f"Prepare a meeting briefing only from saved meeting memories clearly about "
                f"this exact person or organization: {prep_contact.strip()}. Focus on: {focus_text}. "
                "Ignore memories about any other person, company, project, incident, or topic. "
                "Do not infer or invent dates, outcomes, reasons, promises, concerns, or decisions. "
                "Only state a detail as confirmed if it is explicitly present in a matching meeting memory. "
                "If there is no clearly matching meeting memory, say that no relevant notes were found. "
                "Separate confirmed notes from suggestions. List promises, their concerns, decisions, "
                "and open follow-ups. If a detail is absent, mark it not recorded."
            )
            try:
                with st.spinner("Finding the right conversation memories…"):
                    answer = connect(base_url, api_key).reflect(bank_id=bank_id.strip(), query=query)
                st.markdown("### Your briefing")
                st.markdown(
                    '<div class="soft-note">Generated from memories associated with the selected contact. Review details before relying on them.</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(getattr(answer, "text", str(answer)))

                sources = getattr(answer, "based_on", None)
                if sources:
                    with st.expander("🔎  See the memories used"):
                        for source in sources:
                            st.markdown(f"- {source_text(source)}")
                else:
                    st.info("Hindsight did not return source memories with this briefing.")
            except Exception as error:
                st.error(f"Could not prepare the briefing: {error}")

st.divider()
st.caption(
    "Hindsight remembers what you save. The LLM organizes it into a briefing. "
    "It does not send messages, schedule meetings, or know details you haven’t recorded."
)
