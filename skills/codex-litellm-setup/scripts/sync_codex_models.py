#!/usr/bin/env python3
"""Build a Codex model catalog from LiteLLM model IDs."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


class CatalogError(RuntimeError):
    """Raised when a source cannot produce a safe Codex model catalog."""


@dataclass(frozen=True)
class ProviderSettings:
    provider_id: str
    name: str
    base_url: str
    env_key: str


def load_provider_settings(config_path: Path) -> ProviderSettings:
    """Load the active provider without reading the credential itself."""
    try:
        with config_path.open("rb") as config_file:
            config = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise CatalogError(f"cannot read Codex config: {error}") from error

    provider_id = config.get("model_provider")
    providers = config.get("model_providers")
    if not isinstance(provider_id, str) or not isinstance(providers, dict):
        raise CatalogError("Codex config does not define an active model provider")
    provider = providers.get(provider_id)
    if not isinstance(provider, dict):
        raise CatalogError(f"Codex config does not define provider {provider_id!r}")

    name = provider.get("name")
    base_url = provider.get("base_url")
    env_key = provider.get("env_key")
    if not all(isinstance(value, str) and value for value in (name, base_url, env_key)):
        raise CatalogError(
            f"provider {provider_id!r} must define name, base_url, and env_key"
        )
    return ProviderSettings(provider_id, name, base_url, env_key)


def models_endpoint(base_url: str) -> str:
    """Return the provider's models endpoint and require encrypted transport."""
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise CatalogError("model catalog sync requires an HTTPS provider base_url")
    path = f'{parsed.path.rstrip("/")}/models'
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def is_catalog_fresh(
    catalog_path: Path,
    *,
    max_age_seconds: int,
    now: float | None = None,
) -> bool:
    """Return whether a last-known-good catalog is still within its TTL."""
    if max_age_seconds <= 0 or not catalog_path.is_file():
        return False
    current_time = time.time() if now is None else now
    return current_time - catalog_path.stat().st_mtime <= max_age_seconds


def _curl_config_value(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise CatalogError("curl configuration values cannot contain a newline")
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_curl_request(
    url: str,
    bearer_token: str,
    *,
    timeout_seconds: int,
) -> tuple[list[str], str]:
    """Build a curl request that keeps the credential out of argv."""
    if timeout_seconds <= 0:
        raise CatalogError("curl timeout must be greater than zero")
    escaped_url = _curl_config_value(url)
    escaped_header = _curl_config_value(f"Authorization: Bearer {bearer_token}")
    stdin_config = "\n".join(
        [
            "silent",
            "show-error",
            "fail",
            f'max-time = "{timeout_seconds}"',
            f'url = "{escaped_url}"',
            f'header = "{escaped_header}"',
            'header = "Accept: application/json"',
            "",
        ]
    )
    return ["curl", "--config", "-"], stdin_config


def fetch_gateway_payload(url: str, bearer_token: str) -> Any:
    command, stdin_config = build_curl_request(
        url,
        bearer_token,
        timeout_seconds=15,
    )
    try:
        result = subprocess.run(
            command,
            input=stdin_config,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise CatalogError(f"cannot run curl: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or f"curl exited with status {result.returncode}"
        raise CatalogError(f"gateway model request failed: {detail[:500]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise CatalogError("gateway models response is not valid JSON") from error


def load_bundled_catalog() -> Any:
    """Load the catalog shipped with the currently installed Codex binary."""
    try:
        result = subprocess.run(
            ["codex", "debug", "models", "--bundled"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise CatalogError(f"cannot run Codex: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or f"Codex exited with status {result.returncode}"
        raise CatalogError(f"cannot load bundled Codex model catalog: {detail[:500]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise CatalogError("bundled Codex model catalog is not valid JSON") from error


def sync_catalog(
    config_path: Path,
    destination: Path,
    *,
    max_age_seconds: int,
    force: bool,
) -> tuple[int, list[str], bool]:
    """Synchronize the catalog and return count, skipped IDs, and cache status."""
    if not force and is_catalog_fresh(
        destination,
        max_age_seconds=max_age_seconds,
    ):
        return 0, [], True

    settings = load_provider_settings(config_path)
    bearer_token = os.environ.get(settings.env_key)
    if not bearer_token:
        raise CatalogError(f"environment variable {settings.env_key} is not set")

    gateway_payload = fetch_gateway_payload(
        models_endpoint(settings.base_url),
        bearer_token,
    )
    gateway_model_ids = extract_gateway_model_ids(gateway_payload)
    catalog, skipped = build_catalog(
        gateway_model_ids,
        load_bundled_catalog(),
        provider_name=settings.name,
    )
    write_catalog_atomic(destination, catalog)
    return len(catalog["models"]), skipped, False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(
        description="Synchronize Codex's model picker with the active inference gateway."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=codex_home / "config.toml",
        help="Codex config path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=codex_home / "models.json",
        help="Generated Codex model catalog path",
    )
    parser.add_argument(
        "--max-age-seconds",
        type=int,
        default=6 * 60 * 60,
        help="Skip refresh while the existing catalog is newer than this value",
    )
    parser.add_argument("--force", action="store_true", help="Ignore the freshness guard")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        count, skipped, was_fresh = sync_catalog(
            args.config,
            args.output,
            max_age_seconds=args.max_age_seconds,
            force=args.force,
        )
    except CatalogError as error:
        print(f"Codex model catalog sync failed: {error}", file=sys.stderr)
        return 1

    if not args.quiet:
        if was_fresh:
            print(f"Codex model catalog is fresh: {args.output}")
        else:
            print(f"Synced {count} models to {args.output}")
            if skipped:
                print(f"Skipped unsupported gateway models: {', '.join(skipped)}")
    return 0


def extract_gateway_model_ids(payload: Any) -> list[str]:
    """Return unique, non-empty model IDs from an OpenAI-compatible response."""
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise CatalogError("gateway models response must contain a data array")

    model_ids: list[str] = []
    seen: set[str] = set()
    for entry in payload["data"]:
        if not isinstance(entry, dict):
            continue
        model_id = entry.get("id")
        if not isinstance(model_id, str):
            continue
        model_id = model_id.strip()
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        model_ids.append(model_id)
    return model_ids


def build_catalog(
    gateway_model_ids: list[str],
    bundled_catalog: Any,
    *,
    provider_name: str,
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Map gateway IDs onto Codex's bundled metadata and return skipped IDs."""
    if not isinstance(bundled_catalog, dict) or not isinstance(
        bundled_catalog.get("models"), list
    ):
        raise CatalogError("bundled Codex catalog must contain a models array")

    templates: dict[str, dict[str, Any]] = {}
    for model in bundled_catalog["models"]:
        if isinstance(model, dict) and isinstance(model.get("slug"), str):
            templates[model["slug"]] = model

    built: list[tuple[int, int, dict[str, Any]]] = []
    skipped: list[str] = []
    for gateway_index, gateway_id in enumerate(gateway_model_ids):
        canonical_slug = gateway_id.rsplit("/", 1)[-1]
        template = templates.get(gateway_id) or templates.get(canonical_slug)
        if template is None:
            skipped.append(gateway_id)
            continue

        model = copy.deepcopy(template)
        model["slug"] = gateway_id
        model["display_name"] = f'{template["display_name"]} ({provider_name})'
        model["visibility"] = "list"
        model["supported_in_api"] = True
        model["additional_speed_tiers"] = []
        model["service_tiers"] = []
        model["availability_nux"] = None
        model["upgrade"] = None
        # The Responses-Lite endpoint rejects requests that carry
        # parallel_tool_calls=true when routed through an OpenAI-compatible
        # proxy, so the generated catalog never opts a model into lite mode.
        model["use_responses_lite"] = False
        priority = model.get("priority")
        built.append((priority if isinstance(priority, int) else 10_000, gateway_index, model))

    if not built:
        raise CatalogError("gateway returned no models compatible with the bundled Codex catalog")

    built.sort(key=lambda item: (item[0], item[1]))
    return {"models": [item[2] for item in built]}, skipped


def write_catalog_atomic(destination: Path, catalog: Any) -> None:
    """Replace the catalog only after complete JSON has reached disk."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(catalog, temp_file, indent=2, ensure_ascii=True)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, destination)
    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
