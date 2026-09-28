# Meeting Prep Agent

A beginner-friendly meeting assistant that saves your notes in Hindsight, searches the public web for company hiring posts and company facts, and uses Hindsight Reflect to prepare a sourced plan before a later meeting.

The interface pairs a conversational briefing screen with simple meeting-note capture. A contact-specific chat keeps each preparation conversation separate. The full meeting plan organizes recalled information into what happened, how to approach the meeting, key points to remember, promises, and questions to confirm. Users can search current hiring posts and company stats, rate a briefing after a meeting, and chart human-rated performance over time.

## Repository contents

- `app.py` — Streamlit chat interface, meeting-note capture, and Hindsight integration.
- `requirements.txt` — Python dependencies.

Article, social post, and video materials are kept separately from this code repository.

## How the pieces work

- **Streamlit** displays the form and briefing in a browser.
- **Hindsight `retain`** saves the user's dated meeting note as written, with a contact tag for later recall.
- **Hindsight `retain`** tags each record with a stable, contact-specific identifier. **Hindsight `reflect`** applies a strict tag filter, then compares that contact's dated memories and prepares a briefing with dates, changes, and open questions.
- The meeting plan only marks a commitment complete when a later note explicitly confirms it. It separates recalled facts from suggestions and unknowns. The interface shows the retrieved source memories and date coverage so you can inspect the evidence.
- If Hindsight returns no readable source memories, the app withholds the generated briefing and explains how to check the contact, bank, and older untagged notes.
- Company research uses web metasearch to find current hiring posts and company facts/statistics. Each result shows its source link and snippet; users can inspect the source and explicitly save the dated result set to Hindsight as unverified public background. Search snippets can be incomplete or stale, so verify important claims at the linked source.
- After a sourced briefing, users can save a 1–5 usefulness rating, meeting outcome, and correction. Hindsight retains the written review so later briefings can use it as guidance. A small local SQLite ledger stores only the contact tag, review date, and numeric score for a dependable chart; its file is excluded from Git.
- Web search is provided by the `ddgs` package and needs an internet connection. Search-provider availability and result quality can vary.
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
5. Choose **Save meeting notes** and save one or more dated records. Use the same person or organization name consistently.
6. Choose **Prepare for a meeting**, enter that name, and ask a natural-language question in the chat input.
7. After reviewing a sourced briefing, open **How did this briefing hold up?** to save a rating and what happened. Use **Performance graph** to chart the local ratings and their recent average for the contact.
8. Use **Research a company** to search for the company's current jobs and stats. Verify the source pages, then choose whether to save the dated results to the same contact's memory.

Hindsight Cloud setup instructions are in the [Getting Started guide](https://docs.hindsight.vectorize.io/getting-started/). The API URL defaults to `https://api.hindsight.vectorize.io`; change it in the sidebar if you use another Hindsight instance.

## Try the two-meeting memory loop

Use **Northstar Foods** for both records. Save a meeting dated `2026-09-27` with this note:

> They are worried setup may interrupt their busy season and prefer a phased rollout.

Add this promise in the same note:

> I will send a rollout plan by 2026-10-02.

Prepare a briefing for **Northstar Foods** and ask: `What did I promise, and has a later note confirmed it was completed?` With only the first meeting stored, the status should be **not recorded**.

Now save a second meeting dated `2026-10-02`:

- Note: The customer confirmed receiving the rollout plan and prefers a two-week rollout. I will send the deployment checklist by 2026-10-05.

Prepare again with the same question. The briefing should now show the rollout plan as confirmed complete and the checklist as a new follow-up. Expand **Memory timeline and sources** to review the supporting notes in date order. Hindsight retrieval is probabilistic, so verify that the source memories and briefing match the records you entered.

## Contact matching and data handling

Each new record includes the contact name and a normalized matching key, and Hindsight stores it under a stable hashed contact tag. Briefings use Hindsight's strict tag matching, which filters the retrieved memory scope as well as naming the contact in the prompt. It is retrieval scoping, not user authorization: anyone who can use this app and its memory bank can request a briefing for a contact. For a multi-user production service, derive the allowed tag from the authenticated user's permissions and enforce access at the server.

Records saved before contact tags were added are untagged and will not appear in strict scoped briefings. Re-save older meeting notes through the app to add their contact tags.

## Keep in mind

Use fictional or approved data while developing. Meeting notes can contain sensitive information. For a real team deployment, configure appropriate access controls and decide what information should be stored. Verify the briefing before relying on it; the app is a preparation aid, not a source of truth.
