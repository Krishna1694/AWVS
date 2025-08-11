"""Injection testing utilities with smarter SQLi, CMDi, HTMLi detection for GET & POST."""
import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, ParseResult, urljoin
from .crawler import extract_forms

def _replace_param_in_url(url, param, payload):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs[param] = [payload]
    new_q = urlencode(qs, doseq=True)
    newp = ParseResult(parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_q, parsed.fragment)
    return urlunparse(newp)

def _similar(a, b, tolerance=0.8):  # relaxed from 0.9 to catch more blind SQLi
    if not a or not b:
        return False
    shorter, longer = sorted([a, b], key=len)
    return len(shorter) / len(longer) >= tolerance

def test_params_with_payloads(url, payloads, write_callback=print, stop_flag=lambda: False):
    findings = []
    try:
        r = requests.get(url, timeout=8)
    except Exception as e:
        write_callback('request failed: ' + str(e))
        return findings

    parsed = urlparse(url)
    params = []
    if parsed.query:
        params = list(parse_qs(parsed.query).keys())

    # --- GET PARAM TESTING ---
    for p in params:
        if stop_flag():
            break

        # --- SQL Injection detection ---
        try:
            base_resp = requests.get(url, timeout=8).text
            true_payload = _replace_param_in_url(url, p, "' AND '1'='1")
            false_payload = _replace_param_in_url(url, p, "' AND '1'='2")
            t1 = requests.get(true_payload, timeout=8).text
            t2 = requests.get(false_payload, timeout=8).text
            if _similar(base_resp, t1) and not _similar(base_resp, t2):
                findings.append({'severity':'High','title':'Possible Boolean-based SQL Injection','detail':f'Boolean test difference detected at {url}','type':'sqli','param':p,'owasp':'A03: Injection'})
                write_callback('Boolean-based SQLi possible on ' + url)
            # Time-based
            slow_payload = _replace_param_in_url(url, p, "' OR SLEEP(5)-- ")
            start = time.time()
            _ = requests.get(slow_payload, timeout=10)
            if time.time() - start > 4:
                findings.append({'severity':'High','title':'Possible Time-based SQL Injection','detail':f'Slow response on time-based payload at {url}','type':'sqli','param':p,'owasp':'A03: Injection'})
                write_callback('Time-based SQLi possible on ' + url)
        except Exception as e:
            write_callback('SQLi check error: ' + str(e))

        # --- CMD Injection detection ---
        for cmd_payload in ["; echo cmd_injection_test", "&& echo cmd_injection_test", "| echo cmd_injection_test"]:
            test_url = _replace_param_in_url(url, p, cmd_payload)
            try:
                tr = requests.get(test_url, timeout=8, allow_redirects=True)
                if "cmd_injection_test" in tr.text:
                    findings.append({'severity':'High','title':'Possible Command Injection','detail':f'Command output reflected at {test_url}','type':'cmdi','param':p,'owasp':'A03: Injection'})
                    write_callback('Possible Command Injection on ' + test_url)
                    break
            except Exception as e:
                write_callback('CMDi test failed: ' + str(e))

        # --- HTML Injection detection ---
        html_payload = "<b>html_test</b>"
        test_url = _replace_param_in_url(url, p, html_payload)
        try:
            tr = requests.get(test_url, timeout=8)
            if "<b>html_test</b>" in tr.text and "&lt;b&gt;html_test&lt;/b&gt;" not in tr.text:
                findings.append({'severity':'Medium','title':'Possible HTML Injection','detail':f'Unescaped HTML reflected at {test_url}','type':'htmli','param':p,'owasp':'A03: Injection'})
                write_callback('Possible HTML Injection on ' + test_url)
        except Exception as e:
            write_callback('HTMLi test failed: ' + str(e))

        # --- Existing payload-based checks (XSS, SQLi error-based) ---
        for payload in payloads:
            test_url = _replace_param_in_url(url, p, payload)
            try:
                tr = requests.get(test_url, timeout=8, allow_redirects=True)
                body = tr.text.lower()
                if '<script' in payload and '<script' in body:
                    findings.append({'severity':'High','title':'Reflected XSS','detail':f'Payload reflected in {test_url}','type':'xss','param':p,'owasp':'A03: Injection'})
                    write_callback('Potential reflected XSS found on ' + test_url)
                if "sql" in payload and ("error in your sql" in body or "mysql" in body or "syntax" in body):
                    findings.append({'severity':'High','title':'Potential SQL Injection','detail':f'SQLi-like response for {test_url}','type':'sqli','param':p,'owasp':'A03: Injection'})
                    write_callback('Potential SQLi detected on ' + test_url)
            except Exception as e:
                write_callback('param test failed: ' + str(e))

    # --- FORM TESTING ---
    forms = extract_forms(url, r.text) if 'r' in locals() else []
    for form in forms:
        if stop_flag():
            break
        action = form.get('action')
        action = urljoin(url, action)  # normalize relative URLs
        method = form.get('method','get').lower()
        inputs = form.get('inputs',{})

        for field in inputs.keys():  # test each field individually
            base_data = {k: v for k, v in inputs.items()}

            # --- SQL Injection detection for forms ---
            try:
                base_resp = requests.post(action, data=base_data, timeout=8).text if method == 'post' else requests.get(action, params=base_data, timeout=8).text
                true_data = {**base_data, field: "' AND '1'='1"}
                false_data = {**base_data, field: "' AND '1'='2"}
                t1 = requests.post(action, data=true_data, timeout=8).text if method == 'post' else requests.get(action, params=true_data, timeout=8).text
                t2 = requests.post(action, data=false_data, timeout=8).text if method == 'post' else requests.get(action, params=false_data, timeout=8).text
                if _similar(base_resp, t1) and not _similar(base_resp, t2):
                    findings.append({'severity':'High','title':'Possible Boolean-based SQL Injection','detail':f'Boolean test difference detected at {action}','type':'sqli','param':field,'owasp':'A03: Injection'})
                    write_callback('Boolean-based SQLi possible on form field ' + field)
                # Time-based
                slow_data = {**base_data, field: "' OR SLEEP(5)-- "}
                start = time.time()
                if method == 'post':
                    requests.post(action, data=slow_data, timeout=10)
                else:
                    requests.get(action, params=slow_data, timeout=10)
                if time.time() - start > 4:
                    findings.append({'severity':'High','title':'Possible Time-based SQL Injection','detail':f'Slow response on time-based payload at {action}','type':'sqli','param':field,'owasp':'A03: Injection'})
                    write_callback('Time-based SQLi possible on form field ' + field)
            except Exception as e:
                write_callback('Form SQLi check error: ' + str(e))

            # --- XSS detection ---
            for payload in payloads:
                test_data = {**base_data, field: payload}
                try:
                    fr = requests.post(action, data=test_data, timeout=8) if method == 'post' else requests.get(action, params=test_data, timeout=8)
                    body = fr.text.lower()
                    if '<script' in payload and '<script' in body:
                        findings.append({'severity':'High','title':'Reflected XSS (form)','detail':f'Payload reflected in form field "{field}" at {action}','type':'xss','param':field,'owasp':'A03: Injection'})
                        write_callback(f'Potential XSS in form field {field} at ' + action)
                except Exception as e:
                    write_callback('Form XSS test failed: ' + str(e))

    return findings
