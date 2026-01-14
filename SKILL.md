---
name: cc-docs
description: Provides an indexed manifest of Claude Code CLI documentation for fast lookup and task guidance.
---

# Claude Code Docs (Index)

## Purpose

Provide a compact, searchable index of Claude Code CLI documentation so the right reference can be loaded quickly and only when needed.

## When to Use

Use this skill whenever a request involves:
- Claude Code CLI usage, configuration, or operational guidance
- Debugging issues with Claude Code or Claude Agent SDK projects
- Understanding Claude Code behavior, permissions, hooks, or settings

For SDK-specific API questions (Python/TypeScript), also load the `cc-agent-sdk` skill.

## Debugging Starting Point

When troubleshooting issues, start here:

1. **General errors / unexpected behavior**: `references/troubleshooting.md`
2. **Permission denied / tool blocked**: `references/settings.md`, `references/iam.md`
3. **Hooks not firing / hook errors**: `references/hooks.md`, `references/hooks-guide.md`
4. **MCP server issues**: `references/mcp.md`
5. **Sandbox / file access issues**: `references/sandboxing.md`
6. **Session / state problems**: `references/checkpointing.md`, `references/memory.md`
7. **Cost / rate limit issues**: `references/costs.md`, `references/monitoring-usage.md`

Common debugging pattern:
- Check `troubleshooting.md` first for known issues
- Check `settings.md` for configuration problems
- Check `changelog.md` for recent breaking changes

## How to Use

Select the smallest set of reference files that answer the question.
Start with the debugging section above for issues, or orientation docs for broad questions.
Use `references/docs_manifest.json` for a machine-readable map when the topic is unclear.

## References Index

### Orientation and Core Concepts

- `references/overview.md` - high-level product overview
- `references/quickstart.md` - quick start workflow
- `references/setup.md` - environment setup steps
- `references/changelog.md` - release notes and version changes
- `references/docs_manifest.json` - machine-readable manifest of all docs

### CLI Usage and Commands

- `references/cli-reference.md` - CLI flags, options, and syntax
- `references/slash-commands.md` - slash command usage
- `references/interactive-mode.md` - interactive mode behavior
- `references/headless.md` - non-interactive/headless usage
- `references/common-workflows.md` - common task flows

### Configuration and Behavior

- `references/settings.md` - configuration options and defaults
- `references/model-config.md` - model selection and config
- `references/terminal-config.md` - terminal-specific configuration
- `references/statusline.md` - statusline configuration
- `references/output-styles.md` - response/output style controls
- `references/memory.md` - memory features and management
- `references/sandboxing.md` - sandbox behavior and constraints
- `references/checkpointing.md` - checkpointing details

### Skills, Hooks, and Extensions

- `references/skills.md` - skills concepts and usage
- `references/hooks.md` - hooks configuration and lifecycle
- `references/hooks-guide.md` - hooks best practices and examples

### Plugins

- `references/plugins.md` - plugin fundamentals
- `references/plugins-reference.md` - plugin API/reference details
- `references/discover-plugins.md` - discovery guidance
- `references/plugin-marketplaces.md` - marketplace and distribution info

### Interfaces and Editors

- `references/vs-code.md` - VS Code integration
- `references/jetbrains.md` - JetBrains IDE integration
- `references/desktop.md` - desktop app usage
- `references/chrome.md` - Chrome/extension usage
- `references/claude-code-on-the-web.md` - web usage
- `references/devcontainer.md` - devcontainer setup

### Integrations and Automation

- `references/github-actions.md` - GitHub Actions integration
- `references/gitlab-ci-cd.md` - GitLab CI/CD integration
- `references/slack.md` - Slack integration
- `references/third-party-integrations.md` - other integrations
- `references/mcp.md` - MCP integration and usage
- `references/sub-agents.md` - sub-agent orchestration

### Providers and Gateways

- `references/amazon-bedrock.md` - Bedrock configuration
- `references/google-vertex-ai.md` - Vertex AI configuration
- `references/microsoft-foundry.md` - Microsoft Foundry configuration
- `references/llm-gateway.md` - LLM gateway setup and routing

### Security, Compliance, and Networking

- `references/security.md` - security guidance
- `references/iam.md` - IAM and access control
- `references/legal-and-compliance.md` - legal/compliance notes
- `references/data-usage.md` - data handling and retention
- `references/network-config.md` - network configuration

### Monitoring, Costs, and Analytics

- `references/monitoring-usage.md` - usage monitoring
- `references/analytics.md` - analytics features
- `references/costs.md` - cost and billing guidance

### Troubleshooting

- `references/troubleshooting.md` - troubleshooting steps and common fixes

## Maintenance

To update documentation from official sources:

```bash
python3 scripts/fetch.py              # Fetch docs and validate
python3 scripts/fetch.py --validate   # Only validate SKILL.md refs
python3 scripts/fetch.py --update-skill  # Add new files to SKILL.md
```

See `references/README.md` for details.