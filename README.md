# Meeting Prep Agent

A beginner-friendly web app that stores dated meeting records in Hindsight and uses Hindsight Reflect to prepare a briefing before a later meeting. It tracks what was promised, what a later conversation confirmed, and what remains unknown.

The interface uses a warm, matte palette with animated pastel accents. It has separate tabs for saving meeting notes and preparing for the next conversation.

## Repository contents

- `app.py` — Streamlit interface and Hindsight integration.
- `requirements.txt` — Python dependencies.

Article, social post, and video materials are kept separately from this code repository.

## How the pieces work

- **Streamlit** displays the form and briefing in a browser.
- **Hindsight `retain`** saves each dated meeting record, including explicit updates to earlier commitments and new follow-ups.
- **Hindsight `retain`** tags each record with a stable, contact-specific identifier. **Hindsight `reflect`** applies a strict tag filter, then compares that contact's dated memories and prepares a briefing with dates, changes, and open questions.
- The briefing marks a commitment complete only when a later note explicitly confirms it. The interface shows the memories used so you can check the evidence.
- The first version does not read calendars, send email, or schedule meetings.

## Requirements

- Python 3.10 or newer
- A Hindsight Cloud account, API key, and existing memory bank

## Run it on Windows PowerShell

1. Open PowerShell in this project folder.
2. Create and activate a virtual environment, then install the dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

4. In the browser, enter your Hindsight API key and bank ID in the sidebar. The app does not save these values in the project files.
5. Save one or more meeting notes. Use the same person or organization name consistently.
6. Enter that name under **Prepare for the next meeting** and click **Prepare my briefing**.

Hindsight Cloud setup instructions are in the [Getting Started guide](https://docs.hindsight.vectorize.io/getting-started/). The API URL defaults to `https://api.hindsight.vectorize.io`; change it in the sidebar if you use another Hindsight instance.

## Try the two-meeting memory loop

Use **Northstar Foods** for both records. Save a meeting dated `2026-09-27` with these notes:

> They are worried setup may interrupt their busy season and prefer a phased rollout.

Under **New promises and follow-ups**, enter:

> I will send a rollout plan by 2026-10-02.

Prepare a briefing for **Northstar Foods** and ask: `What did I promise, and has a later note confirmed it was completed?` With only the first meeting stored, the status should be **not recorded**.

Now save a second meeting dated `2026-10-02`:

- Notes: The customer confirmed receiving the rollout plan and prefers a two-week rollout.
- Earlier promises: `Rollout plan — sent on 2026-10-01; customer confirmed receipt.`
- New promises: `I will send the deployment checklist by 2026-10-05.`

Prepare again with the same question. The briefing should now show the rollout plan as confirmed complete and the checklist as a new follow-up. Expand **Memory timeline and sources** to review the supporting notes in date order. Hindsight retrieval is probabilistic, so verify that the source memories and briefing match the records you entered.

## Contact matching and data handling

Each new record includes the contact name and a normalized matching key, and Hindsight stores it under a stable hashed contact tag. Briefings use Hindsight's strict tag matching, which filters the retrieved memory scope as well as naming the contact in the prompt. It is retrieval scoping, not user authorization: anyone who can use this app and its memory bank can request a briefing for a contact. For a multi-user production service, derive the allowed tag from the authenticated user's permissions and enforce access at the server.

Records saved before contact tags were added are untagged and will not appear in strict scoped briefings. Re-save older meeting notes through the app to add their contact tags.

## Keep in mind

Use fictional or approved data while developing. Meeting notes can contain sensitive information. For a real team deployment, configure appropriate access controls and decide what information should be stored. Verify the briefing before relying on it; the app is a preparation aid, not a source of truth.
