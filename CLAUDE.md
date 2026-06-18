# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

A care-facility staff chatbot built on the Anthropic API, with both a CLI and a web interface.

- `src/bot.py` — shared core: `MODEL` (`claude-haiku-4-5`), `SYSTEM_PROMPT` (care-practice assistant persona), and `ask(messages)` which calls the Anthropic Messages API. Both the CLI and the web API import from here so the persona/model stay in one place.
- `src/chat.py` — CLI entry point. Keeps conversation history in memory for the session and reconfigures stdin/stdout to UTF-8 (Windows consoles default to a non-UTF-8 codepage, which corrupts Japanese input/output otherwise).
- `src/api.py` — FastAPI app exposing `POST /api/chat` (`{"messages": [{"role", "content"}, ...]}` → `{"reply": "..."}`) and serving `static/` (the frontend) at `/`. Conversation history is stateless on the server — the frontend resends the full message list on every request.
- `static/index.html` — single-file vanilla JS/HTML/CSS chat UI; no build step.
- `.env` (gitignored) — holds `ANTHROPIC_API_KEY`, loaded via `python-dotenv`.

There is no lint or test tooling configured yet.

## Setup

```
pip install -r requirements.txt
```

## Running

CLI:
```
python src/chat.py
```

Web (serves the chat UI and API on http://127.0.0.1:8000):
```
cd src
uvicorn api:app --reload
```
