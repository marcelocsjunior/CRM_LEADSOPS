Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot
if (-not (Test-Path .venv)) {
    py -m venv .venv
}
$VenvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $VenvPython -m pip install --upgrade pip setuptools wheel | Out-Null
& $VenvPython -m pip install -r requirements.txt | Out-Null
& $VenvPython -m streamlit run app.py --server.headless true --server.port 8501
