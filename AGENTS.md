# AGENTS.md

This repository is a skills pack. There is no application code; the deliverables are `skills/*/SKILL.md` files, their bundled `scripts/` and `references/`, and the manifests that expose them to each agent.

## Layout

- `skills/<name>/` — one skill per directory. `SKILL.md` frontmatter `name` must equal the directory name.
- `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `plugin.json` — manifests. All carry the same plugin name and version.
- `docs/` — per-agent install guides. Keep them in step with the README install section.
- `scripts/` — validators run by CI.

## Working here

- Edit skills in place; do not fork a skill into agent-specific copies. One `SKILL.md` serves every agent.
- After any edit run `node scripts/validate-skills.js` and `node scripts/validate-versions.js`.
- Bundled scripts must run with no third-party dependencies (Python 3.11+ standard library, POSIX shell).
- A version bump touches all five manifests in one commit.
