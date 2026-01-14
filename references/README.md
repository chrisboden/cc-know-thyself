# Claude Code Documentation References

This directory contains mirrored documentation from the official Claude Code docs at [code.claude.com/docs](https://code.claude.com/docs).

## Source

- **Official docs**: https://code.claude.com/docs
- **Changelog**: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- **Manifest**: See `docs_manifest.json` for file hashes and last-updated timestamps

## Updating

Documentation is fetched using the skill's fetch script:

```bash
# From anywhere
python .claude/skills/cc-docs/scripts/fetch.py

# Options
python scripts/fetch.py --validate      # Only check SKILL.md refs vs files
python scripts/fetch.py --update-skill  # Add new files to SKILL.md
```

The script:
- Discovers pages from the official sitemap
- Fetches markdown versions of each page
- Tracks content hashes to detect changes
- Includes the changelog from the Claude Code GitHub repo
- Validates SKILL.md references against fetched files
- Can auto-append new files to an "Uncategorized" section

## Key Files for Debugging

| Issue Type | Start Here |
|------------|------------|
| General errors | `troubleshooting.md` |
| Permission/access | `settings.md`, `iam.md` |
| Hooks | `hooks.md`, `hooks-guide.md` |
| MCP servers | `mcp.md` |
| Sandbox/files | `sandboxing.md` |
| Costs/limits | `costs.md`, `monitoring-usage.md` |

## Related Skills

- **cc-agent-sdk**: For Claude Agent SDK API reference (Python/TypeScript)
- **cc-docs** (this skill): For Claude Code CLI behavior and configuration
