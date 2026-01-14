# cc-docs

A Claude Code skill that provides indexed documentation for debugging and reference.

## What is this?

This is a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) - a directory of instruction files and resources that Claude can access to help with specific tasks.

**cc-docs** mirrors the official Claude Code documentation from [code.claude.com/docs](https://code.claude.com/docs) for offline/fast access and provides a structured index for quick lookups.

## Use Cases

- Debugging Claude Code or Claude Agent SDK projects
- Looking up CLI flags, settings, hooks, or MCP configuration
- Understanding Claude Code behavior and permissions
- Checking the changelog for breaking changes

## Installation

Copy this directory into your project's `.claude/skills/` folder:

```
your-project/
└── .claude/
    └── skills/
        └── cc-docs/
            ├── SKILL.md
            ├── scripts/
            │   └── fetch.py
            └── references/
                ├── troubleshooting.md
                ├── settings.md
                └── ...
```

Or clone directly:

```bash
git clone https://github.com/chrisboden/cc-docs.git .claude/skills/cc-docs
```

## Updating Documentation

The docs are fetched from official sources using the included script:

```bash
# Fetch latest docs
python3 scripts/fetch.py

# Validate SKILL.md references match fetched files
python3 scripts/fetch.py --validate

# Auto-add new files to SKILL.md
python3 scripts/fetch.py --update-skill
```

## Structure

```
cc-docs/
├── README.md           # This file
├── SKILL.md            # Skill manifest and index (read by Claude)
├── scripts/
│   └── fetch.py        # Documentation fetcher
└── references/
    ├── README.md       # References directory info
    ├── docs_manifest.json  # File hashes and timestamps
    ├── troubleshooting.md
    ├── settings.md
    ├── hooks.md
    └── ...             # ~50 documentation files
```

## Related Skills

- **[cc-agent-sdk](https://github.com/anthropics/claude-code)** - For Claude Agent SDK API reference (Python/TypeScript)

## License

Documentation content is sourced from [Anthropic's Claude Code docs](https://code.claude.com/docs) and [Claude Code repository](https://github.com/anthropics/claude-code).
