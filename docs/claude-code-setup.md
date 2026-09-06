# Using this pack with Claude Code

## Marketplace install

```text
/plugin marketplace add justinbarias/skills
/plugin install justinbarias-skills@justinbarias
```

The first command registers `.claude-plugin/marketplace.json` as a marketplace named `justinbarias`; the second installs the `justinbarias-skills` plugin, which exposes every directory under `skills/`.

SSH errors during `marketplace add`? Use the HTTPS URL: `/plugin marketplace add https://github.com/justinbarias/skills.git`.

## Local clone, no install

```bash
git clone https://github.com/justinbarias/skills.git
claude --plugin-dir /path/to/skills
```

## Copy a single skill

Skills are plain directories. Copying `skills/codex-litellm-setup/` into `~/.claude/skills/` (user) or `.claude/skills/` (project) also works, and is how `npx skills add` installs.

## Invoke

Claude reads each skill's description and triggers it when the task matches. Force one with `/codex-litellm-setup` or `/agent-harness`.
