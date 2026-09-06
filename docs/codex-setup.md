# Using this pack with Codex

The repo is a Codex plugin. `.codex-plugin/plugin.json` points `skills` at `./skills/`, and `.agents/plugins/marketplace.json` declares the repo root as the plugin source, so Codex reads the same `SKILL.md` files Claude Code does.

## Install

```bash
codex plugin marketplace add justinbarias/skills
codex plugin add justinbarias-skills@justinbarias
```

Requires Codex CLI 0.122 or later. From a local clone:

```bash
codex plugin marketplace add /path/to/skills
codex plugin add justinbarias-skills@justinbarias
```

Start a new Codex session after installing.

## Direct install without the plugin system

Copy a skill directory into `~/.codex/skills/`:

```bash
cp -r skills/codex-litellm-setup ~/.codex/skills/
```

## Invoke

Type `@codex-litellm-setup` or `@agent-harness` in chat, or describe the task and let Codex pick. `skills/agent-harness/agents/openai.yaml` supplies the display name and default prompt Codex shows for that skill.

## Note on codex-litellm-setup

That skill edits `~/.codex/config.toml`. Running it *from inside* Codex against the same `CODEX_HOME` is fine (the merge script backs up first), but the new provider only takes effect in the next session.
