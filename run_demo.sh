#!/usr/bin/env bash
# Start the local Streamlit demo on port 8765.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt
exec streamlit run app.py --server.port 8765
