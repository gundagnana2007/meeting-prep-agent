"""A pastel, interactive meeting-prep assistant backed by Hindsight memory."""

from __future__ import annotations

import hashlib
import os
import re
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
        value = source.get(field) if isinstance(source, dict) else getattr(source, field, None)
        if value:
            return str(value)
    return str(source)


def source_date(source: object) -> str | None:
    for field in ("occurred_start", "occurred_end", "mentioned_at"):
        value = source.get(field) if isinstance(source, dict) else getattr(source, field, None)
        if value:
            match = re.search(r"\d{4}-\d{2}-\d{2}", str(value))
            if match:
                return match.group(0)
    match = re.search(r"Meeting date:\s*(\d{4}-\d{2}-\d{2})", source_text(source), re.IGNORECASE)
    return match.group(1) if match else None


def contact_tag(contact: str) -> str:
    normalized = " ".join(contact.casefold().split())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"meeting-contact-{digest}"


def source_items(answer: object) -> list[object]:
    based_on = getattr(answer, "based_on", None)
    if based_on is None:
        return []
    if isinstance(based_on, list):
        return based_on
    if isinstance(based_on, dict):
        memories = based_on.get("memories")
    else:
        memories = getattr(based_on, "memories", None)
    if memories is not None:
        return list(memories)
    return [based_on]


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
    st.info(
        "New meeting records are tagged to their contact, and briefings filter by that tag. "
        "Re-save older notes once to add the contact tag."
    )

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
        previous_commitments = st.text_area(
            "What happened to promises from earlier meetings?",
            height=90,
            placeholder=(
                "Rollout plan: sent on Oct 1; the customer confirmed they received it.\n"
                "Write 'not discussed' if nobody checked the status."
            ),
            help="Record an update only when someone confirmed it in this meeting. Leaving it blank means the status is unknown.",
        )
        new_commitments = st.text_area(
            "New promises and follow-ups",
            height=90,
            placeholder=(
                "I will send the deployment checklist by Oct 5.\n"
                "The customer will confirm the rollout date."
            ),
            help="Include who owns each action and its due date when known.",
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
                f"Meeting record\n"
                f"Contact name exactly as entered: {contact.strip()}\n"
                f"Contact matching key: {' '.join(contact.casefold().split())}\n"
                f"Meeting date: {meeting_date.isoformat()}\n"
                f"Conversation notes: {notes.strip()}\n"
                f"Confirmed updates to earlier commitments: {previous_commitments.strip() or 'Not discussed or not recorded.'}\n"
                f"New commitments and follow-ups (open when recorded unless stated otherwise): "
                f"{new_commitments.strip() or 'None recorded.'}"
            )
            try:
                with st.spinner("Saving this conversation to Hindsight…"):
                    connect(base_url, api_key).retain(
                        bank_id=bank_id.strip(),
                        content=content,
                        context=f"Meeting notes with {contact.strip()} on {meeting_date.isoformat()}",
                        tags=[contact_tag(contact)],
                    )
                st.success(
                    f"Saved the {meeting_date.isoformat()} meeting with {contact.strip()}. "
                    "Its commitment updates will be available in the next briefing."
                )
                st.session_state["last_saved_contact"] = contact.strip()
            except Exception as error:
                st.error(f"Could not save the notes: {error}")

with prepare_tab:
    st.subheader("Get your context before the conversation")
    st.markdown(
        '<p class="soft-note">Use the same person or organization name. Each new meeting can update what was promised, completed, or left open.</p>',
        unsafe_allow_html=True,
    )

    with st.expander("Try the two-meeting memory loop", expanded=False):
        st.markdown(
            """
            **1. Save the first meeting** for `Northstar Foods` on `2026-09-27`.

            - Notes: They are worried setup may interrupt their busy season and prefer a phased rollout.
            - New promises: I will send a rollout plan by 2026-10-02.

            **2. Prepare before the next meeting.** Use `Northstar Foods` and ask:  
            `What did I promise, and has any later note confirmed it was completed?`

            With only the first meeting saved, the briefing should say the completion status is not recorded.

            **3. Save the follow-up meeting** for `Northstar Foods` on `2026-10-02`.

            - Notes: The customer confirmed receiving the rollout plan and prefers a two-week rollout.
            - Earlier promises: Rollout plan — sent on 2026-10-01; customer confirmed receipt.
            - New promises: I will send the deployment checklist by 2026-10-05.

            **4. Prepare again** for `Northstar Foods`. The new memory should change the briefing: the rollout plan is confirmed complete, while the checklist is a new open follow-up. Expand **Memory timeline and sources** to inspect the evidence.

            **5. Check contact matching.** Save a note for a different company with a different preference, then prepare for `Northstar Foods` again. Check the answer and its source memories for cross-contact details. Also try a new name such as `Maple Labs`; the assistant should say it found no relevant notes.

            This check can reveal a retrieval mistake. Contact-name instructions help the model focus, but they are not a substitute for separate access-controlled banks in a multi-customer production system.
            """
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
                f"Prepare a time-ordered meeting briefing using only memories clearly about "
                f"this exact person or organization: {prep_contact.strip()} (matching key: {' '.join(prep_contact.casefold().split())}). "
                f"Focus on: {focus_text}. Ignore memories about every other contact or topic. "
                "Compare matching meeting records by date. Treat items in 'New commitments and follow-ups' "
                "as open at the time of that meeting unless the note explicitly says otherwise. "
                "Track them across later meetings: mark an older item completed only when a later note "
                "explicitly confirms completion; mark it still open only when a note says it remains pending; "
                "otherwise say its later status is not recorded. "
                "For every status, include the meeting date and the supporting detail. "
                "Describe how the customer's concerns or preferences changed over time, and distinguish "
                "current statements from older ones. Do not treat silence as completion or assume an old "
                "concern is still current. Do not invent dates, outcomes, reasons, promises, or decisions. "
                "If no clearly matching memory exists, say no relevant notes were found. "
                "Separate confirmed facts from suggestions, list decisions and open follow-ups, and mark "
                "missing information as not recorded."
            )
            try:
                with st.spinner("Finding the right conversation memories…"):
                    answer = connect(base_url, api_key).reflect(
                        bank_id=bank_id.strip(),
                        query=query,
                        tags=[contact_tag(prep_contact)],
                        tags_match="all_strict",
                        include_facts=True,
                    )
                st.markdown("### Your briefing")
                st.markdown(
                    '<div class="soft-note">Compare the dates and source memories. A promise is complete only when a later note explicitly confirms it.</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(getattr(answer, "text", str(answer)))

                sources = source_items(answer)
                if sources:
                    with st.expander("🧭  Memory timeline and sources"):
                        ordered_sources = sorted(
                            sources,
                            key=lambda item: (source_date(item) is None, source_date(item) or ""),
                        )
                        for source in ordered_sources:
                            meeting_date_label = source_date(source) or "Date not included"
                            st.markdown(f"**Meeting: {meeting_date_label}**")
                            st.markdown(source_text(source))
                else:
                    st.info("Hindsight did not return source memories with this briefing.")
            except Exception as error:
                st.error(f"Could not prepare the briefing: {error}")

st.divider()
st.caption(
    "Hindsight remembers what you save. The LLM organizes it into a briefing. "
    "It does not send messages, schedule meetings, or know details you haven’t recorded."
)
