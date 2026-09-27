# Meeting Prep Agent

A small Streamlit app that helps you prepare for a meeting by recalling what you recorded after previous conversations. It uses Hindsight as persistent memory and Hindsight Reflect to turn relevant memories into a briefing.

## What it does

1. Save meeting notes with the contact name and meeting date.
2. Before a later meeting, enter the same contact name and choose a briefing focus.
3. Hindsight retrieves relevant memories and its LLM organizes them into a briefing.
4. Expand **See the memories used** to inspect the context behind the answer.

The interface uses a warm, matte palette with animated pastel accents. The app does not read calendars, send email, schedule meetings, or update a CRM.

## How memory works

- `app.py` sends notes to Hindsight with `retain`.
- When preparing, the app calls Hindsight `reflect` with the contact and requested focus.
- The model is instructed to separate recorded facts from suggestions and to say when information is missing.
- Check the source memories and verify important details before relying on the briefing. Prompt instructions cannot guarantee perfect retrieval or replace access controls.

## Requirements

- Python 3.10 or newer
- A Hindsight Cloud account
- A Hindsight API key and memory bank ID

## Run on Windows

Open PowerShell in the repository folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep the PowerShell window open while using the app. Streamlit prints a local URL, normally `http://localhost:8501`.

## Connect Hindsight

1. In [Hindsight Cloud](https://ui.hindsight.vectorize.io/), create or choose a memory bank.
2. Create an active API key from the organization’s **API Keys** page. Copy the full key when shown; it starts with `hsk_` and is only displayed once.
3. In the app’s sidebar, enter the key, the memory bank ID, and the API URL (`https://api.hindsight.vectorize.io`).

Never commit an API key or paste one into an issue or chat. The app keeps the key in a masked input field and does not write it to project files.

## Try it with sample notes

Under **Add meeting notes**, enter `Northstar Foods` and a note such as:

> They are concerned setup may interrupt their busy season. I promised to send a rollout plan by Friday. They prefer a short product demo.

Then open **Prepare for a meeting**, use the same contact name, and choose **Promises and follow-ups**. Review the briefing and expand the source-memory panel.

## Project files

- `app.py` — Streamlit interface and Hindsight integration.
- `requirements.txt` — Python dependencies.
- `.gitignore` — excludes the local virtual environment and secrets files.
