#!/usr/bin/env bash
# Add (or replace) an `export VAR="..."` line in the user's shell rc file.
#
# The secret is never accepted on argv (visible in `ps` and shell history).
# Provide it via --key-file, or the script prompts silently on the terminal.
#
# usage: install_env_var.sh [--var LITE_LLM_KEY] [--rc ~/.zshrc] [--key-file PATH] [--dry-run]
set -euo pipefail

VAR="LITE_LLM_KEY"
RC=""
KEY_FILE=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --var) VAR="$2"; shift 2 ;;
    --rc) RC="$2"; shift 2 ;;
    --key-file) KEY_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ ! "$VAR" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "error: invalid variable name: $VAR" >&2; exit 2
fi

# Pick the rc file for the login shell when not given.
if [[ -z "$RC" ]]; then
  case "$(basename "${SHELL:-/bin/zsh}")" in
    zsh)  RC="$HOME/.zshrc" ;;
    bash) if [[ "$(uname)" == "Darwin" ]]; then RC="$HOME/.bash_profile"; else RC="$HOME/.bashrc"; fi ;;
    fish) RC="$HOME/.config/fish/config.fish" ;;
    *)    RC="$HOME/.profile" ;;
  esac
fi

# Obtain the secret.
if [[ -n "$KEY_FILE" ]]; then
  KEY="$(tr -d '\r\n' < "$KEY_FILE")"
elif [[ -t 0 ]]; then
  read -rs -p "Paste value for $VAR (input hidden): " KEY; echo
else
  KEY="$(tr -d '\r\n')"   # piped stdin
fi
if [[ -z "$KEY" ]]; then echo "error: empty value" >&2; exit 2; fi
if [[ "$KEY" == *$'\n'* || "$KEY" == *'"'* || "$KEY" == *'$'* || "$KEY" == *'`'* ]]; then
  echo "error: value contains characters unsafe for a double-quoted export" >&2; exit 2
fi

if [[ "$RC" == *config.fish ]]; then
  LINE="set -gx $VAR \"$KEY\""
  PATTERN="^set -gx $VAR "
else
  LINE="export $VAR=\"$KEY\""
  PATTERN="^export $VAR="
fi
MARK="# added by codex-litellm-setup"

if [[ $DRY_RUN -eq 1 ]]; then
  if [[ -f "$RC" ]] && grep -qE "$PATTERN" "$RC"; then
    echo "would replace existing $VAR line in $RC"
  else
    echo "would append $VAR to $RC"
  fi
  exit 0
fi

mkdir -p "$(dirname "$RC")"
touch "$RC"
TMP="$(mktemp "${RC}.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

if grep -qE "$PATTERN" "$RC"; then
  # Replace in place; awk avoids sed delimiter/escaping issues with the key.
  awk -v pat="$PATTERN" -v line="$LINE" '$0 ~ pat { print line; next } { print }' "$RC" > "$TMP"
  ACTION="replaced"
else
  cp "$RC" "$TMP"
  printf '\n%s\n%s\n' "$MARK" "$LINE" >> "$TMP"
  ACTION="appended"
fi
chmod --reference="$RC" "$TMP" 2>/dev/null || chmod 600 "$TMP"
mv "$TMP" "$RC"
trap - EXIT

echo "$ACTION $VAR in $RC"
echo "reload with:  source \"$RC\"   (or open a new terminal)"
