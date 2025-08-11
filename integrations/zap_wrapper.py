"""Minimal ZAP wrapper. Assumes ZAP is running and accessible via API.
This wrapper uses zap-cli if available as a simple approach.
"""
import shutil
import subprocess
import json
import tempfile
import os

def run_zap_scan(target, write_callback=print):
    write_callback('ZAP wrapper: checking zap-cli...')
    if not shutil.which('zap-cli'):
        write_callback('zap-cli not installed; skipping ZAP scan')
        return {'findings':[]}
    # simple sequence: quick-scan via zap-cli
    try:
        subprocess.run(['zap-cli','status'], check=True, capture_output=True)
    except Exception as e:
        write_callback('zap-cli cannot reach ZAP daemon: ' + str(e))
        return {'findings':[]}
    try:
        write_callback('ZAP: starting quick-scan (this may take a while)...')
        subprocess.run(['zap-cli','quick-scan', target], check=True)
        # export alerts
        out = subprocess.run(['zap-cli','alerts','-l','0'], capture_output=True, text=True)
        raw = out.stdout
        # crude parsing: each line -> finding
        findings = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            findings.append({'severity':'Medium','title':'ZAP Alert','detail':line})
        return {'findings':findings}
    except Exception as e:
        write_callback('ZAP scan error: ' + str(e))
        return {'findings':[]}
