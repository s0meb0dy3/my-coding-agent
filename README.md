# NEXA

A from-scratch coding agent, following the learning guide in
[tau/dev-notes/learning-guide.md](../tau/dev-notes/learning-guide.md).

Mirrors Tau's three-layer split:

```text
nexa_coding → nexa_agent → nexa_ai
```

- `nexa_ai` — provider layer (how we talk to models).
- `nexa_agent` — the portable brain (messages, tools, loop, harness). Pure:
  no CLI, no Textual/Rich, no local config paths.
- `nexa_coding` — the coding app (CLI, file/shell tools, sessions, UI).

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```
