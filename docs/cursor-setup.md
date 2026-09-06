# Using this pack with Cursor

Cursor loads two kinds of project context:

| Layer | Path | Role |
|---|---|---|
| Rules | `.cursor/rules/*.mdc` | Short, always-on or glob-scoped policies |
| Skills | `.cursor/skills/<name>/SKILL.md` | Full workflows, read when the description matches |
| User skills | `~/.cursor/skills/` | Same, available in every workspace |

Put these skills under `.cursor/skills/`. Do not paste skill bodies into rules; a rule may point at a skill, nothing more.

## Install

Fastest:

```bash
npx skills add justinbarias/skills          # detects Cursor, writes .cursor/skills/
```

Manual, from a clone:

```bash
git clone https://github.com/justinbarias/skills.git /tmp/jb-skills
mkdir -p .cursor/skills
rsync -a /tmp/jb-skills/skills/ .cursor/skills/          # project
rsync -a /tmp/jb-skills/skills/ ~/.cursor/skills/        # or global
```

## Optional pointer rule

`.cursor/rules/skills.mdc`:

```markdown
---
description: Use project skills for setup and harness work
alwaysApply: true
---
Before configuring Codex against a gateway, or editing AGENTS.md / agent guidance, read the matching skill under .cursor/skills/.
```

## Update

Re-run the sync. `.cursor/skills/` is the copy Cursor reads; the clone is upstream only.
