# my-coding-agent

A from-scratch mini coding agent, following the learning guide in
[tau/dev-notes/learning-guide.md](../tau/dev-notes/learning-guide.md).

Mirrors Tau's three-layer split:

```text
mini_coding → mini_agent → mini_ai
```

- `mini_ai` — provider layer (how we talk to models).
- `mini_agent` — the portable brain (messages, tools, loop, harness). Pure:
  no CLI, no Textual/Rich, no local config paths.
- `mini_coding` — the coding app (CLI, file/shell tools, sessions, UI).

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```
