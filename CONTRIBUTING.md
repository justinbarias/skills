# Contributing

## Add a skill

1. Create `skills/<kebab-name>/SKILL.md` with frontmatter `name` (must equal the directory name) and `description` (under 1024 characters, and it must say *when* to use the skill, not only what it does).
2. Put long material in `references/` and executable helpers in `scripts/`. Keep `SKILL.md` under about 500 lines.
3. Link references from `SKILL.md` with relative paths; the validator fails on dead links.
4. Add a row to the table in `README.md`.
5. Run `node scripts/validate-skills.js`.

## Release

Bump `version` in all five manifests (`plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`). `node scripts/validate-versions.js` fails if they disagree.
