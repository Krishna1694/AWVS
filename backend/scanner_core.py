"""Core scanning logic with lightweight OWASP Top 10 checks + grouping support."""
import requests
from .crawler import simple_crawl, extract_forms
from .injector import test_params_with_payloads
from integrations.sqlmap_wrapper import run_sqlmap
from integrations.zap_wrapper import run_zap_scan

DEFAULT_PAYLOADS = ["' OR '1'='1", "<script>alert(1)</script>", "../../etc/passwd", "../"]

OWASP_MAP = {
    "xss": "A03: Injection",
    "sqli": "A03: Injection",
    "misconfig": "A05: Security Misconfiguration",
    "auth": "A07: Identification and Authentication Failures",
    "crypto": "A02: Cryptographic Failures",
    "ssrf": "A10: Server-Side Request Forgery",
    "cmdi": "A03: Injection",
    "htmli": "A03: Injection"
}

class ScannerCore:
    def __init__(self):
        self.findings = []

    def run_scan(self, config, write_callback=print, stop_flag=lambda: False):
        target = config.get('target')
        depth = config.get('depth', 0)
        zap_on = config.get('zap', False)
        write = write_callback or print

        write(f"Starting lightweight scan on {target} (depth={depth})")
        urls = [target]
        if depth > 0:
            write('Crawling...')
            try:
                crawled = simple_crawl(target, max_depth=depth, write_callback=write, stop_flag=stop_flag)
                urls = list(dict.fromkeys(urls + crawled))
                write(f'Found {len(urls)} URLs')
            except Exception as e:
                write('Crawl failed: ' + str(e))

        try:
            r = requests.get(target, timeout=10, allow_redirects=True)
            self.check_headers(target, r, write)
        except Exception as e:
            write('Passive check failed: ' + str(e))

        for u in urls:
            if stop_flag():
                write('Stop flag detected, aborting scans.')
                break
            write(f'Testing {u}')
            findings = test_params_with_payloads(u, DEFAULT_PAYLOADS, write_callback=write, stop_flag=stop_flag)
            for fnd in findings:
                fnd['owasp'] = OWASP_MAP.get(fnd.get('type'), 'Unmapped')
                if 'url' not in fnd:
                    fnd['url'] = u
                self.findings.append(fnd)
                if fnd.get('type') == 'sqli':
                    try:
                        ok = run_sqlmap(u, fnd.get('param'))
                        if ok:
                            fnd['confirmed'] = True
                            write('sqlmap confirmed SQLi on ' + u)
                    except Exception as e:
                        write('sqlmap wrapper error: ' + str(e))

        if zap_on:
            write('Starting ZAP deep scan (this may be slow)...')
            try:
                zap_results = run_zap_scan(target, write_callback=write)
                for f in zap_results.get('findings', []):
                    f['owasp'] = OWASP_MAP.get(f.get('type'), 'Unmapped')
                    if 'url' not in f:
                        f['url'] = target
                self.findings.extend(zap_results.get('findings', []))
            except Exception as e:
                write('ZAP scan failed: ' + str(e))

        # Merge duplicates (same OWASP, title, severity, url)
        unique = []
        seen = set()
        for f in self.findings:
            key = (f.get('owasp'), f.get('title'), f.get('severity'), f.get('url'))
            if key not in seen:
                seen.add(key)
                unique.append(f)
        self.findings = unique

        results = {
            'target': target,
            'findings': self.findings
        }
        return results

    def check_headers(self, target, response, write):
        headers = response.headers
        if 'strict-transport-security' not in headers:
            self.findings.append({'severity':'Medium','title':'Missing HSTS','detail':'Strict-Transport-Security header is not present','type':'misconfig','owasp':'A05: Security Misconfiguration','url':target})
            write('Missing HSTS header detected')
        if 'x-frame-options' not in headers:
            self.findings.append({'severity':'Low','title':'Missing X-Frame-Options','detail':'Potential clickjacking','type':'misconfig','owasp':'A05: Security Misconfiguration','url':target})
            write('Missing X-Frame-Options detected')
