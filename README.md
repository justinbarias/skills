# skills

Agent skills by Justin Barias, packaged so one repo installs into Claude Code, Codex, Cursor, Antigravity, and anything the [skills CLI](https://github.com/vercel-labs/skills) supports. Layout follows [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills): every skill lives in `skills/<name>/SKILL.md`, and the plugin manifests at the repo root point every agent at that same directory.

## Skills

| Skill | What it does |
|---|---|
| [`codex-litellm-setup`](skills/codex-litellm-setup/SKILL.md) | Point the Codex CLI at a LiteLLM gateway: merge the provider into `config.toml` without clobbering existing settings, install the API-key env var into the shell rc, and generate `models.json` from the gateway's `/v1/models` so the model picker shows gateway models. Ships the merge, env-var, and catalog-sync scripts. |
| [`agent-harness`](skills/agent-harness/SKILL.md) | Bootstrap or maintain a repository's agent harness: concise `AGENTS.md`, architecture and knowledge maps, execution plans, and drift checks. |

## Install

<details open>
<summary><b>skills CLI (any agent, one command)</b></summary>

```bash
npx skills add justinbarias/skills                        # install every skill
npx skills add justinbarias/skills --list                 # browse first
npx skills add justinbarias/skills --skill codex-litellm-setup
```

Installs into 70+ agents (Claude Code, Cursor, Codex, Copilot, Cline, and more). See [docs/skills-cli-setup.md](docs/skills-cli-setup.md).

</details>

<details>
<summary><b>Claude Code</b></summary>

```text
/plugin marketplace add justinbarias/skills
/plugin install justinbarias-skills@justinbarias
```

Or run from a local clone without installing: `claude --plugin-dir /path/to/skills`. See [docs/claude-code-setup.md](docs/claude-code-setup.md).

</details>

<details>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add justinbarias/skills
codex plugin add justinbarias-skills@justinbarias
```

Then invoke with `@codex-litellm-setup` or `@agent-harness` in chat. See [docs/codex-setup.md](docs/codex-setup.md).

</details>

<details>
<summary><b>Cursor</b></summary>

Sync `skills/*` into `.cursor/skills/` (project) or `~/.cursor/skills/` (global). Keep `.cursor/rules/*.mdc` for short policies only. See [docs/cursor-setup.md](docs/cursor-setup.md).

</details>

<details>
<summary><b>Antigravity CLI</b></summary>

```bash
agy plugin install https://github.com/justinbarias/skills.git
```

See [docs/antigravity-setup.md](docs/antigravity-setup.md).

</details>

## How skills work

A skill is a directory with a `SKILL.md`. Its YAML frontmatter carries `name` and `description`; agents load only the description into context and read the body when the description matches the task. Larger material sits beside it in `references/` (loaded on demand) and `scripts/` (executed, never loaded). One file format serves every agent listed above.

## Project structure

```text
skills/
├── skills/                      # the skills; one directory per skill
│   ├── codex-litellm-setup/
│   │   ├── SKILL.md
│   │   ├── scripts/             # apply_codex_config.py, install_env_var.sh, sync_codex_models.py
│   │   └── references/          # troubleshooting.md
│   └── agent-harness/
│       ├── SKILL.md
│       ├── references/          # bootstrap.md, maintain.md
│       └── agents/openai.yaml   # Codex display metadata
├── .claude-plugin/              # Claude Code plugin + marketplace manifests
├── .codex-plugin/plugin.json    # Codex plugin manifest
├── .agents/plugins/marketplace.json  # Codex marketplace entry
├── plugin.json                  # generic manifest (skills CLI, Antigravity)
├── docs/                        # per-agent setup guides
└── scripts/                     # validate-skills.js, validate-versions.js (run in CI)
```

## Validate

```bash
node scripts/validate-skills.js     # frontmatter, naming, dead links
node scripts/validate-versions.js   # all manifests carry the same version
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bump the version in every manifest together (the CI check enforces it).

## License

Apache-2.0. See [LICENSE](LICENSE).
