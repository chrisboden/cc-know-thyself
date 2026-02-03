# OpenRouter integration

> Configure Claude Code to route requests through OpenRouter for provider failover, cost controls, and model routing.

## Why use OpenRouter

OpenRouter provides a reliability and management layer between Claude Code and model providers:

* **Provider failover** - Automatically routes requests across providers if one is down or rate-limited
* **Budget controls** - Centralized spend limits and credit allocation across teams
* **Usage visibility** - Usage analytics and per-user/project tracking

## How it works

OpenRouter exposes an Anthropic Messages API-compatible endpoint. Configure Claude Code to send requests to OpenRouter by setting the base URL and API token. No local proxy is required.

## Configuration

### Shell profile (global)

Set these in your shell profile (for example, `~/.zshrc`):

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""  # Important: must be explicitly empty
```

### Project settings file (scoped)

Use a project-level settings file at `.claude/settings.local.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "<your-openrouter-api-key>",
    "ANTHROPIC_API_KEY": ""
  }
}
```

> **Note:** Do not put these in a project `.env` file. The native Claude Code installer does not read standard `.env` files.

### Model overrides (OpenRouter model IDs)

You can override Claude Code defaults to target specific OpenRouter model IDs. Example using Anthropic-hosted models:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "sk-or-v1-...",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "anthropic/claude-haiku-4.5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "anthropic/claude-sonnet-4.5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "anthropic/claude-opus-4.5"
  }
}
```

> **Note:** You can use other OpenRouter model IDs, as long as they are compatible with the Anthropic Messages API and support tool use.

## Verify

Within Claude Code, run `/status`:

```text
Auth token: ANTHROPIC_AUTH_TOKEN
Anthropic base URL: https://openrouter.ai/api
```

## Troubleshooting

* **Auth errors**: Ensure `ANTHROPIC_API_KEY` is set to an empty string (`""`). If it is unset, Claude Code may fall back to Anthropic defaults.
* **Requests still go to Anthropic**: Confirm `ANTHROPIC_BASE_URL` is set to `https://openrouter.ai/api` and your OpenRouter API key is in `ANTHROPIC_AUTH_TOKEN`.

## Source

* https://openrouter.ai/docs/guides/claude-code-integration
