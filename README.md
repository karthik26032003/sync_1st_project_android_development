# MyCards AI proxy

A tiny FastAPI server that holds the Anthropic API key and answers questions
about card transactions using Claude. The Android app calls this; the key
never ships to the phone.

Managed with **uv**. Dependencies live in `pyproject.toml`.

## Setup (one time)

```bash
# from this folder: mycards-ai-proxy/
uv sync                     # creates/updates .venv and installs deps from pyproject.toml

# add your key (if not already done)
copy .env.example .env      # Windows   (macOS/Linux: cp .env.example .env)
# then open .env and paste your real ANTHROPIC_API_KEY
```

## Run

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- `--host 0.0.0.0` is important: it lets the Android emulator reach the server.
- Health check: open http://localhost:8000/health → `{"status":"ok"}`.

## How the app reaches it

The Android emulator talks to your computer via the special address
**`10.0.2.2`** (that's "localhost of the host machine" from inside the emulator).
So the app is configured to call `http://10.0.2.2:8000/`.

## Model

Uses `claude-haiku-4-5` (fast + low cost) — plenty for transaction Q&A.
Change the model in `main.py` if you want a more capable one.

## Test without the app (optional)

```bash
uv run python -c "import urllib.request, json; print(urllib.request.urlopen(urllib.request.Request('http://localhost:8000/chat', data=json.dumps({'question':'How much on dining?','transactions':[{'merchant':'Starbucks','category':'Dining','amount':6.75,'date':'2026-07-14'}]}).encode(), headers={'Content-Type':'application/json'})).read().decode())"
```
