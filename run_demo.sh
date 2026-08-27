#!/usr/bin/env bash
# Start the local Streamlit demo. Prefers 8765; if busy, tries 8766-8799.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

pick_port() {
  local p
  for p in $(seq 8765 8799); do
    # Free if nothing accepts a TCP connection on this port.
    if ! (echo >/dev/tcp/127.0.0.1/"$p") >/dev/null 2>&1; then
      echo "$p"
      return 0
    fi
  done
  echo "No free port in 8765-8799" >&2
  exit 1
}

PORT="$(pick_port)"
echo "Local URL: http://127.0.0.1:${PORT}"
exec streamlit run app.py --server.port "$PORT" --browser.gatherUsageStats false
