#!/usr/bin/env python3
"""Merge LiteLLM gateway settings into an existing Codex config.toml.

The script never clobbers unrelated config (projects, MCP servers, plugins).
It replaces only the managed top-level keys and the [model_providers.<id>]
table, backs up the previous file, validates the result with tomllib before
writing, and supports --dry-run so the merged config can be reviewed first.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import time
import tomllib
from pathlib import Path

MANAGED_KEYS = (
    "model_provider",
    "model_catalog_json",
    "model_reasoning_effort",
    "model_context_window",
    "model_auto_compact_token_limit",
    "approvals_reviewer",
)
BEGIN_MARK = "# --- managed by codex-litellm-setup (begin) ---"
END_MARK = "# --- managed by codex-litellm-setup (end) ---"
TABLE_RE = re.compile(r"^\s*\[")


def toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def key_re(keys: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(r"^\s*(" + "|".join(re.escape(k) for k in keys) + r")\s*=")


def split_preamble(lines: list[str]) -> tuple[list[str], list[str]]:
    """Return (top-level lines, everything from the first [table] on)."""
    for index, line in enumerate(lines):
        if TABLE_RE.match(line):
            return lines[:index], lines[index:]
    return lines, []


def strip_managed_block(lines: list[str]) -> list[str]:
    out: list[str] = []
    inside = False
    for line in lines:
        if line.strip() == BEGIN_MARK:
            inside = True
            continue
        if line.strip() == END_MARK:
            inside = False
            continue
        if not inside:
            out.append(line)
    return out


def strip_table(lines: list[str], table_prefix: str) -> list[str]:
    """Drop [table_prefix] and any [table_prefix.sub] tables."""
    out: list[str] = []
    skipping = False
    header_re = re.compile(r"^\s*\[\s*([^\]]+?)\s*\]")
    for line in lines:
        match = header_re.match(line)
        if match:
            name = match.group(1).strip()
            skipping = name == table_prefix or name.startswith(table_prefix + ".")
        if not skipping:
            out.append(line)
    return out


def render(
    existing: str,
    *,
    provider_id: str,
    provider_name: str,
    base_url: str,
    env_key: str,
    wire_api: str,
    catalog_path: str,
    reasoning_effort: str,
    context_window: int,
    auto_compact_token_limit: int,
    model: str | None,
) -> str:
    lines = existing.splitlines()
    lines = strip_managed_block(lines)
    preamble, rest = split_preamble(lines)

    managed = set(MANAGED_KEYS)
    if model is not None:
        managed.add("model")
    drop = key_re(tuple(managed))
    preamble = [line for line in preamble if not drop.match(line)]
    rest = strip_table(rest, f"model_providers.{provider_id}")

    managed_lines = [
        BEGIN_MARK,
        f"model_provider = {toml_str(provider_id)}",
        f"model_catalog_json = {toml_str(catalog_path)}",
        f"model_reasoning_effort = {toml_str(reasoning_effort)}",
        f"model_context_window = {context_window}",
        f"model_auto_compact_token_limit = {auto_compact_token_limit}",
        'approvals_reviewer = "user"',
    ]
    if model is not None:
        managed_lines.insert(1, f"model = {toml_str(model)}")
    managed_lines.append(END_MARK)

    provider_lines = [
        "",
        f"[model_providers.{provider_id}]",
        f"name = {toml_str(provider_name)}",
        f"base_url = {toml_str(base_url)}",
        f"env_key = {toml_str(env_key)}  # Codex sends this env var as the Bearer token",
        f"wire_api = {toml_str(wire_api)}",
    ]

    # Trim leading blank lines from the preserved preamble so the file stays tidy.
    while preamble and not preamble[0].strip():
        preamble.pop(0)
    while rest and not rest[-1].strip():
        rest.pop()

    body = managed_lines + ([""] if preamble else []) + preamble
    if rest:
        body += [""] + rest
    body += provider_lines
    return "\n".join(body).rstrip("\n") + "\n"


def validate(text: str, *, provider_id: str, catalog_path: str, env_key: str) -> None:
    data = tomllib.loads(text)  # raises TOMLDecodeError on bad output
    problems = []
    if data.get("model_provider") != provider_id:
        problems.append("model_provider mismatch")
    if data.get("model_catalog_json") != catalog_path:
        problems.append("model_catalog_json mismatch")
    provider = data.get("model_providers", {}).get(provider_id)
    if not isinstance(provider, dict):
        problems.append(f"[model_providers.{provider_id}] missing")
    elif provider.get("env_key") != env_key:
        problems.append("provider env_key mismatch")
    if problems:
        raise ValueError("; ".join(problems))


def write_with_backup(path: Path, text: str, *, backup: bool) -> Path | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None
    mode = 0o600
    if path.exists():
        mode = path.stat().st_mode & 0o777
        if backup:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            backup_path = path.with_name(f"{path.name}.backup-{stamp}")
            backup_path.write_bytes(path.read_bytes())
            os.chmod(backup_path, mode)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    os.chmod(tmp_path, mode)
    os.replace(tmp_path, path)
    return backup_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--codex-home", type=Path, default=codex_home,
                   help="Codex home (default: $CODEX_HOME or ~/.codex)")
    p.add_argument("--base-url", required=True,
                   help="LiteLLM OpenAI-compatible base URL, e.g. https://gateway.example.com/v1")
    p.add_argument("--env-key", default="LITE_LLM_KEY",
                   help="Env var Codex reads for the Bearer token (default: LITE_LLM_KEY)")
    p.add_argument("--provider-id", default="litellm")
    p.add_argument("--provider-name", default="LiteLLM Gateway")
    p.add_argument("--wire-api", default="responses", choices=["responses", "chat"])
    p.add_argument("--catalog-path", type=Path, default=None,
                   help="models.json path (default: <codex-home>/models.json)")
    p.add_argument("--reasoning-effort", default="medium")
    p.add_argument("--context-window", type=int, default=1_000_000)
    p.add_argument("--auto-compact-token-limit", type=int, default=450_000)
    p.add_argument("--model", default=None,
                   help="Optional default model slug (a gateway model id). Leaves existing 'model' untouched when omitted.")
    p.add_argument("--dry-run", action="store_true", help="Print merged config, write nothing")
    p.add_argument("--no-backup", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    codex_home: Path = args.codex_home.expanduser().resolve()
    config_path = codex_home / "config.toml"
    catalog_path = (args.catalog_path or codex_home / "models.json").expanduser().resolve()

    if not args.base_url.rstrip("/").endswith("/v1"):
        print(f"warning: base_url {args.base_url!r} does not end in /v1; LiteLLM usually expects it",
              file=sys.stderr)
    if not args.base_url.startswith("https://"):
        print("warning: base_url is not HTTPS. Codex will work, but sync_codex_models.py refuses "
              "non-HTTPS URLs; run the sync against an HTTPS URL.", file=sys.stderr)

    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    if existing:
        try:
            tomllib.loads(existing)
        except tomllib.TOMLDecodeError as error:
            print(f"error: existing config is not valid TOML, refusing to merge: {error}",
                  file=sys.stderr)
            return 2

    merged = render(
        existing,
        provider_id=args.provider_id,
        provider_name=args.provider_name,
        base_url=args.base_url,
        env_key=args.env_key,
        wire_api=args.wire_api,
        catalog_path=str(catalog_path),
        reasoning_effort=args.reasoning_effort,
        context_window=args.context_window,
        auto_compact_token_limit=args.auto_compact_token_limit,
        model=args.model,
    )
    try:
        validate(merged, provider_id=args.provider_id, catalog_path=str(catalog_path),
                 env_key=args.env_key)
    except (tomllib.TOMLDecodeError, ValueError) as error:
        print(f"error: merged config failed validation, nothing written: {error}", file=sys.stderr)
        return 2

    if args.dry_run:
        sys.stdout.write(merged)
        return 0

    backup = write_with_backup(config_path, merged, backup=not args.no_backup)
    print(f"wrote {config_path}")
    if backup:
        print(f"backup {backup}")
    print(f"catalog path {catalog_path} (run sync_codex_models.py --force to generate it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
