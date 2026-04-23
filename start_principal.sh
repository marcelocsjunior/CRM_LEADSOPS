#!/usr/bin/env bash
set -euo pipefail
cd "/home/biotech/Documentos/LeadOps_TI"
nohup ./.venv/bin/streamlit run app.py --server.headless true --server.port 8501 \
  > "/home/biotech/Documentos/LeadOps_TI/streamlit.out" 2>&1 &
echo $! > "/home/biotech/Documentos/LeadOps_TI/streamlit.pid"
sleep 5
echo "PID: $(cat /home/biotech/Documentos/LeadOps_TI/streamlit.pid)"
tail -n 40 "/home/biotech/Documentos/LeadOps_TI/streamlit.out"
