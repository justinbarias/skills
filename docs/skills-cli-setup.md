# Install with the skills CLI

The open [skills CLI](https://github.com/vercel-labs/skills) reads `skills/*/SKILL.md` from a GitHub repo and installs into whichever agents it detects on your machine (Claude Code, Cursor, Codex, Copilot, Cline, Windsurf, and others).

```bash
npx skills add justinbarias/skills                 # everything
npx skills add justinbarias/skills --list          # see what is in the pack
npx skills add justinbarias/skills --skill codex-litellm-setup
npx skills add justinbarias/skills --skill agent-harness
```

Per-skill installs copy the whole skill directory, including `scripts/` and `references/`, so bundled helpers work after install. Re-run the same command to update.
