---
name: codex-litellm-setup
description: Configure the OpenAI Codex CLI to route through a LiteLLM gateway (or any OpenAI-compatible proxy) instead of OpenAI directly. Merges the litellm model provider into ~/.codex/config.toml without clobbering existing settings, installs the API-key env var into the user's shell rc, and generates ~/.codex/models.json from the gateway's /v1/models list so the Codex model picker shows the gateway's models. Use this whenever the user mentions Codex together with LiteLLM, a gateway, a proxy, model_provider, model_catalog_json, models.json, "point codex at my gateway", "codex model picker is empty", or wants to run Codex against self-hosted / local models. Also use it to re-sync the model catalog after the gateway's model list changes.
---

# Codex + LiteLLM gateway setup

Codex normally talks to OpenAI. Pointing it at a LiteLLM gateway needs three things to agree with each other:

1. `config.toml` names a provider whose `base_url` is the gateway and whose `env_key` is the env var holding the key.
2. That env var is exported in the user's shell, so Codex can read it.
3. `models.json` (the catalog Codex's picker reads) lists the gateway's model ids, built on Codex's own bundled metadata so reasoning levels and limits are right.

If any one is missing, the symptoms are confusing (empty picker, 401s, "unknown model"). Do all three, in order, then verify.

All scripts honour `CODEX_HOME` (default `~/.codex`). Use a scratch `CODEX_HOME` when you must not touch the real config.

## Inputs to gather first

Ask only for what you cannot infer. Defaults in brackets.

| Input | Default | Notes |
|---|---|---|
| Gateway base URL | ask | Must end in `/v1`. HTTPS strongly preferred: the sync script refuses HTTP. |
| Env var name | `LITE_LLM_KEY` | Must match between config `env_key` and the shell export. |
| Key value | ask | Never put it in argv or in your own output. Let the user paste it into the installer's hidden prompt, or read it from a file they name. |
| Default model | none | A gateway model id. Leave unset to keep whatever `model =` already exists. |
| Reasoning effort / context window / compact limit | `medium` / `1000000` / `450000` | Override only if the user asks. |

## Steps

### 1. Preflight

```bash
codex --version                 # needs `codex debug models --bundled` (present in 0.15x+)
python3 --version               # 3.11+ for tomllib
curl --version | head -1
ls -la "${CODEX_HOME:-$HOME/.codex}/config.toml" 2>/dev/null
```

If `config.toml` exists, read it. Existing content (projects, MCP servers, plugins, personality) is preserved by the merge script; only the managed keys and `[model_providers.<id>]` are replaced. Mention anything that will change, notably an existing `model_auto_compact_token_limit` or `model =` line.

### 2. Merge the provider into config.toml

Dry-run first, show the user the result, then write. The script backs up the old file as `config.toml.backup-<timestamp>` and validates the merged TOML before writing.

```bash
SKILL=<directory containing this SKILL.md>   # wherever the skill is installed
python3 $SKILL/scripts/apply_codex_config.py --base-url https://gateway.example.com/v1 --dry-run
python3 $SKILL/scripts/apply_codex_config.py --base-url https://gateway.example.com/v1
```

Flags: `--env-key`, `--provider-name`, `--model`, `--reasoning-effort`, `--context-window`, `--auto-compact-token-limit`, `--wire-api {responses,chat}`, `--codex-home`.

What the managed block sets and why:

```toml
model_provider = "litellm"                     # activates the provider table below
model_catalog_json = "/abs/path/.codex/models.json"  # absolute; TOML does not expand ~
model_reasoning_effort = "medium"
model_context_window = 1000000                 # gateway models can exceed Codex's bundled defaults
model_auto_compact_token_limit = 450000
approvals_reviewer = "user"

[model_providers.litellm]
name = "LiteLLM Gateway"
base_url = "https://gateway.example.com/v1"
env_key = "LITE_LLM_KEY"      # Codex reads this env var and sends it as the Bearer token
wire_api = "responses"        # LiteLLM serves /v1/responses; Codex works best on it
```

### 3. Export the key in the shell

```bash
bash $SKILL/scripts/install_env_var.sh --var LITE_LLM_KEY            # prompts, input hidden
bash $SKILL/scripts/install_env_var.sh --var LITE_LLM_KEY --key-file ~/.secrets/litellm.key
```

Picks the rc file from `$SHELL` (`~/.zshrc`, `~/.bash_profile` on macOS, `~/.bashrc` on Linux, fish `config.fish`). Override with `--rc`. Replaces an existing export line rather than appending a duplicate. In Claude Code the user can run it interactively with the `!` prefix so the key never enters the transcript.

The current session will not see the new variable. Either `source` the rc file or export it inline for the next step.

### 4. Generate the model catalog

Install the sync script somewhere durable, then run it forced once.

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/bin"
cp $SKILL/scripts/sync_codex_models.py "${CODEX_HOME:-$HOME/.codex}/bin/"
python3 "${CODEX_HOME:-$HOME/.codex}/bin/sync_codex_models.py" --force
```

Expected output: `Synced N models to .../models.json`, possibly followed by `Skipped unsupported gateway models: ...`. Skipped ids are gateway models with no matching slug in Codex's bundled catalog (for example `claude-*`, `ollama/*`). Codex cannot render them in the picker without metadata; that is expected, not an error. Tell the user which were skipped.

The script only maps a gateway id when its last path segment matches a bundled slug (`openai/gpt-5.4` matches `gpt-5.4`). If everything is skipped, the gateway's model names do not match Codex's slugs; see the troubleshooting reference.

Freshness guard: without `--force` the script is a no-op while `models.json` is under 6 hours old, so it is safe to call from a shell rc or a cron/launchd job:

```bash
# ~/.zshrc, keeps the picker current without slowing shell startup noticeably
python3 ~/.codex/bin/sync_codex_models.py --quiet 2>/dev/null &
```

### 5. Verify

```bash
codex debug models | python3 -c 'import json,sys; [print(m["slug"]) for m in json.load(sys.stdin)["models"]]'
codex exec -m <gateway-model-id> "Reply with exactly: ok"
```

The first command should list gateway ids with the provider name in their display names. The second proves auth, `wire_api`, and routing end-to-end. If it fails, read `references/troubleshooting.md`.

## Guardrails

- Never write the key into `config.toml`, a script argument, or your own messages. The env var is the only place it lives.
- Never overwrite `config.toml` by hand with a template; users accumulate MCP servers, trusted projects and plugin settings there. Use the merge script or edit surgically.
- Do not run the sync or `codex exec` against the real `~/.codex` when the user says not to touch their live setup; use `CODEX_HOME=/some/scratch/dir`.
- Report outcomes plainly: how many models synced, which were skipped, where the backup is.
