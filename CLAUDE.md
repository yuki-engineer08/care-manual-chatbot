# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This project is in its initial scaffolding stage. The codebase currently consists of:
- `src/chat.py` — empty, intended as the entry point for a chatbot built on the Anthropic API
- `requirements.txt` — declares `anthropic` and `python-dotenv` as dependencies
- `.env` — local environment file (gitignored) expected to hold API keys (e.g. `ANTHROPIC_API_KEY`)

There is no build, lint, or test tooling configured yet. As this project grows, update this file with real commands (install, run, test) and architectural notes once they exist — avoid documenting structure that isn't there yet.

## Setup

```
pip install -r requirements.txt
```

API credentials should be loaded via `python-dotenv` from a local `.env` file, which must never be committed.
