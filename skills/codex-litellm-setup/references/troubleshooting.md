# Troubleshooting Codex + LiteLLM

Read this when a step in SKILL.md fails. Each entry: symptom, cause, fix.

## Sync script

**`environment variable LITE_LLM_KEY is not set`**
The shell running the script has not loaded the export. `source ~/.zshrc` (or the rc file used), or prefix the command: `LITE_LLM_KEY=... python3 sync_codex_models.py --force`. Check the name matches `env_key` in config.toml exactly.

**`model catalog sync requires an HTTPS provider base_url`**
The provider `base_url` is `http://`. The sync script refuses to send a bearer token in clear text. Options: use the HTTPS hostname for the gateway; or keep the LAN URL in config.toml and sync from a second config: `sync_codex_models.py --config /path/to/https-config.toml`.

**`gateway model request failed: ... 401`**
Key rejected. Confirm the key works: `curl -s -H "Authorization: Bearer $LITE_LLM_KEY" https://gateway/v1/models | head -c 300`. LiteLLM virtual keys can be scoped to models; a key with no model access returns an empty `data` list rather than 401.

**`gateway returned no models compatible with the bundled Codex catalog`**
Every gateway id was skipped. Codex only renders models it has metadata for, and the script takes that metadata from `codex debug models --bundled` by matching the last path segment of the gateway id against a bundled slug. List both sides:

```bash
codex debug models --bundled | python3 -c 'import json,sys; print([m["slug"] for m in json.load(sys.stdin)["models"]])'
curl -s -H "Authorization: Bearer $LITE_LLM_KEY" https://gateway/v1/models | python3 -c 'import json,sys; print([m["id"] for m in json.load(sys.stdin)["data"]])'
```

Fix on the LiteLLM side: add a `model_name` alias that equals a bundled slug (for example `gpt-5.4`) pointing at the upstream deployment. Codex will then send `gpt-5.4` and LiteLLM routes it.

**`cannot load bundled Codex model catalog`**
Old Codex without `codex debug models --bundled`. Upgrade: `npm i -g @openai/codex@latest` or `brew upgrade codex`.

**`Codex model catalog is fresh`** when you expected a refresh
Freshness guard (6 h default). Add `--force` or lower `--max-age-seconds`.

## Config

**Picker still shows OpenAI models, or is empty**
`model_catalog_json` must be an absolute path and the file must exist. `codex debug models` shows what Codex actually loaded. Also confirm `model_provider = "litellm"` is at the top level of config.toml (before any `[table]`); TOML assigns top-level keys after a table header to that table.

**`unknown model` or `model not found` on `codex exec -m`**
The slug must be the gateway id exactly as in models.json (including any `provider/` prefix). `model =` in config.toml, if set, must also be a gateway id.

**Merge script refuses: `existing config is not valid TOML`**
Fix the syntax first (`python3 -c 'import tomllib;tomllib.load(open("$HOME/.codex/config.toml","rb"))'` prints the line). The script will not merge into a file it cannot parse.

## Requests

**400 from the gateway on every turn, mentions `parallel_tool_calls`**
The catalog opted a model into Responses-Lite. The bundled sync script forces `use_responses_lite = false`; regenerate with `--force` if models.json was hand-edited.

**Works with `wire_api = "chat"` but not `"responses"`**
LiteLLM version predates full `/v1/responses` support, or the upstream model lacks it. Set `--wire-api chat` when applying config; you lose some Codex features (reasoning summaries, some tool streaming).

**Works in the terminal, not in the Codex desktop app**
GUI apps do not read shell rc files. Set the variable via `launchctl setenv LITE_LLM_KEY ...` (macOS) or a `~/.config/environment.d/` file (Linux), then restart the app.

**Sync works, chat 401s**
Codex sends the value of the env var named by `env_key`; the sync script reads the same name, so a mismatch is unlikely unless config was edited after sync. Re-run `apply_codex_config.py --dry-run` and compare.
