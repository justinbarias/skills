# Using this pack with Antigravity CLI (agy)

Antigravity installs this repo as a native plugin using the root `plugin.json` and the `skills/` directory.

## Install

From GitHub:

```bash
agy plugin install https://github.com/justinbarias/skills.git
```

From a local clone:

```bash
git clone https://github.com/justinbarias/skills.git
agy plugin install ./skills
```

The plugin lands under `~/.gemini/config/plugins/justinbarias-skills/` on current releases (older releases used `~/.gemini/antigravity-cli/plugins/`).

## Verify

```bash
agy plugin list
agy plugin validate ./skills
```

## Invoke

Reference a skill by name in chat (`codex-litellm-setup`, `agent-harness`) or describe the task. This pack ships no legacy `commands/*.toml`, so there are no slash-command wrappers to convert; the namespaced skills are the interface.
