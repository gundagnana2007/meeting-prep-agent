# Meeting Prep Agent

A beginner-friendly web app that stores meeting notes in Hindsight and uses Hindsight Reflect to prepare a briefing before a later meeting. The briefing can include previous concerns, decisions, promises, and follow-ups.

The interface uses a warm, matte palette with animated pastel accents. It has separate tabs for saving meeting notes and preparing for the next conversation.

## Repository contents

- `app.py` — Streamlit interface and Hindsight integration.
- `requirements.txt` — Python dependencies.

Article, social post, and video materials are kept separately from this code repository.

## How the pieces work

- **Streamlit** displays the form and briefing in a browser.
- **Hindsight `retain`** saves each meeting's notes in your memory bank.
- **Hindsight `reflect`** retrieves relevant memories and uses its configured LLM to write a briefing.
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

## Try this fictional example

Save these notes for **Northstar Foods**:

> They are concerned setup may interrupt their busy season. I promised to send a rollout plan by Friday. They prefer a short product demo.

Then save a second meeting:

> They liked the demo. They want setup finished before June. I agreed to send the rollout plan by Friday.

Ask the app to prepare you for a meeting with **Northstar Foods**, focusing on promises, concerns, and follow-ups. It should use the notes stored in Hindsight to build the briefing. Results depend on the notes retained and Hindsight's retrieval.

## Keep in mind

Use fictional or approved data while developing. Meeting notes can contain sensitive information. For a real team deployment, configure appropriate access controls and decide what information should be stored. Verify the briefing before relying on it; the app is a preparation aid, not a source of truth.
