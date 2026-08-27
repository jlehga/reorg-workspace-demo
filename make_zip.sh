#!/usr/bin/env bash
# Build a reviewer zip of the Reorg Workspace prototype (no clone required).
# Excludes: .venv, __pycache__, .git, _local, assets (proprietary photos),
#           dist, .pytest_cache, and other local junk.
set -euo pipefail
cd "$(dirname "$0")"

OUT_DIR="dist"
OUT_ZIP="${OUT_DIR}/reorg-execution-system.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$OUT_DIR"
rm -f "$OUT_ZIP"

# Prefer git-tracked files so we never ship ignored/local material.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files -z | while IFS= read -r -d '' f; do
    case "$f" in
      assets/*|_local/*|dist/*) continue ;;
    esac
    mkdir -p "$STAGE/$(dirname "$f")"
    cp "$f" "$STAGE/$f"
  done
else
  rsync -a \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '_local' \
    --exclude 'assets' \
    --exclude 'dist' \
    --exclude '.env' \
    --exclude '.env.*' \
    --exclude '.streamlit/secrets.toml' \
    ./ "$STAGE/"
fi

# Drop any caches that slipped in
find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true

(
  cd "$STAGE"
  zip -qr "$OLDPWD/$OUT_ZIP" .
)

echo "Wrote $OUT_ZIP ($(du -h "$OUT_ZIP" | awk '{print $1}'))"
