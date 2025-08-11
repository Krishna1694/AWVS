# Advanced Web Vulnerability Scanner 
This is a minimal, educational vulnerability scanner with a Tkinter UI.
**Important:** Only run scans against targets you own or have explicit permission to test.

## What it includes
- Lightweight crawling and passive checks
- Non-destructive heuristic checks for a subset of OWASP Top 10 (injection heuristics, header checks, XSS reflections)
- Optional integrations:
  - sqlmap (CLI) wrapper for SQL injection confirmation
  - ZAP (via zap-cli) wrapper for deeper scans (optional)

## Install
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
For sqlmap: install from your package manager or from https://github.com/sqlmapproject/sqlmap
For ZAP: install ZAP and zap-cli (https://github.com/Grunny/zap-cli).

## Run
```bash
python3 app.py
```

## Safety
- Default mode is non-destructive. Deep scans (sqlmap/ZAP/SSRF active tests) require explicit toggles in the UI.
- Always have written authorization for any scans you perform.
