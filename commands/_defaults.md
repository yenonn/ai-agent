# Command Defaults

This file documents the default settings used across all command files in this directory.

## Default Model Configuration

**Default Model**: `claude-sonnet-4-5`

All command files (unless explicitly overridden) should include this frontmatter:

```yaml
---
model: claude-sonnet-4-5
---
```

## How to Use

When creating new command files in `tools/` or `workflows/` directories:

1. Start with the YAML frontmatter specifying the model
2. Follow with your command content
3. If you need a different model for specific use cases, override with:
   - `claude-opus-4-0` for complex reasoning tasks
   - `claude-haiku-4-0` for fast, simple tasks

## Template Structure

```markdown
---
model: claude-sonnet-4-5
---

# Command Name

Brief description of what this command does.

## Context

Background information...

## Requirements

$ARGUMENTS

## Instructions

Detailed instructions...
```

## Notes

- The model setting in each file's frontmatter takes precedence
- No global configuration file is currently supported by Claude Code
- Keep this file updated if you change your default model preference

