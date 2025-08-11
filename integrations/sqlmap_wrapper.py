"""Minimal sqlmap CLI wrapper. Requires sqlmap to be installed and in PATH."""
import shutil
import subprocess
import json
import tempfile
import os

def run_sqlmap(url, param):
    if not shutil.which('sqlmap'):
        raise RuntimeError('sqlmap not installed or not in PATH')
    args = ['sqlmap', '-u', url, '--batch', '--level=1', '--risk=1', '--output-dir', tempfile.gettempdir()]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        # crude check: look for 'is vulnerable' phrase
        if 'is vulnerable' in out.lower() or 'payload' in out.lower():
            return True
        return False
    except subprocess.TimeoutExpired:
        raise RuntimeError('sqlmap timed out')
