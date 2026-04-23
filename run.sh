#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
./.venv/bin/python -m pip install --upgrade pip setuptools wheel >/dev/null
./.venv/bin/python -m pip install -r requirements.txt >/dev/null
exec ./.venv/bin/python -m streamlit run app.py --server.headless true --server.port "${LEADOPS_PORT:-8501}"
