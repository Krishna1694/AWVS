import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from backend.scanner import default_payloads, analyze_response


def scan_access_control(base_url, payloads):
    results = []
    for path in payloads:
        url = base_url.rstrip("/") + path
        try:
            r = requests.get(url, timeout=5)
            if r.status_code in [200, 403]:  # 200 = accessible, 403 = interesting too
                results.append((url, "Potential Exposure"))
            else:
                results.append((url, "No Issue Detected"))
        except Exception as e:
            results.append((url, f"Error: {e}"))
    return results

def scan_insecure_design(base_url, payloads):
    results = []

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    for path in payloads:
        url = base_url + path
        try:
            r = requests.get(url, timeout=5)
            if r.status_code in [200, 302]:
                if any(x in r.text.lower() for x in ["admin", "delete", "edit", "account", "user info", "profile"]):
                    results.append((url, "Potential Insecure Design"))
                else:
                    results.append((url, "Accessible Endpoint"))
            else:
                results.append((url, "No Issue Detected"))
        except Exception as e:
            results.append((url, f"Error: {e}"))

    return results

def scan_misconfiguration(base_url, payloads):
    results = []

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    for path in payloads:
        url = base_url + path
        try:
            r = requests.get(url, timeout=5)
            status = r.status_code
            content = r.text.lower()

            if status in [200, 403]:
                if any(x in content for x in ["index of /", "php version", "mysql", "debug", "fatal error", "exception", "traceback"]):
                    results.append((url, "Potential Misconfiguration"))
                else:
                    results.append((url, "Accessible Endpoint"))
            else:
                results.append((url, "No Issue Detected"))
        except Exception as e:
            results.append((url, f"Error: {e}"))

    return results

def scan_auth_bypass(forms, payloads):
    results = []
    for form in forms:
        url = form.get("action")
        method = form.get("method", "get").lower()
        inputs = form.get("inputs", [])

        username_fields = [i for i in inputs if "user" in i.lower() or "email" in i.lower()]
        password_fields = [i for i in inputs if "pass" in i.lower()]

        if not username_fields or not password_fields:
            continue  # Skip non-login forms

        for user_payload in payloads:
            for pass_payload in payloads:
                data = {f: user_payload for f in username_fields}
                data.update({f: pass_payload for f in password_fields})

                try:
                    if method == "post":
                        r = requests.post(url, data=data, timeout=5)
                    else:
                        r = requests.get(url, params=data, timeout=5)
                    
                    if "logout" in r.text.lower() or "dashboard" in r.text.lower() or r.status_code == 302:
                        result = "Potential Auth Bypass"
                    else:
                        result = "No Issue Detected"

                    results.append((url, method.upper(), data, result))
                    if result == "Potential Auth Bypass":
                        break
                except Exception as e:
                    results.append((url, method.upper(), data, f"Error: {e}"))

    return results

def scan_ssrf_from_file(file_path, payloads):
    results = []
    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)

        for param in query:
            for payload in payloads:
                new_query = query.copy()
                new_query[param] = [payload]
                encoded_query = urlencode(new_query, doseq=True)
                new_url = urlunparse(parsed_url._replace(query=encoded_query))
                try:
                    response = requests.get(new_url, timeout=5)
                    if response.status_code in [200, 302, 403]:
                        results.append((new_url, param, payload, "Potential SSRF"))
                    else:
                        results.append((new_url, param, payload, "No Issue Detected"))
                except Exception as e:
                    results.append((new_url, param, payload, f"Error: {e}"))

    return results


def inject_get_params_from_file(file_path, category="SQLi", log=None):
    results = []

    try:
        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        if log: 
            log(f"[!] Error reading file: {e}")
        return []

    if log: 
        log(f"[*] Loaded {len(urls)} URLs from {file_path}")

    for url in urls:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if not params:
            continue

        for param in params:
            for payload in default_payloads[category]:
                test_params = params.copy()
                test_params[param] = [payload]

                new_query = urlencode(test_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))

                try:
                    resp = requests.get(test_url, timeout=5)
                    result = analyze_response(category, resp.text)
                    results.append((test_url, param, payload, result))
                    if log: 
                        log(f"[{category}] {param} → {payload} → {result}")

                    if result == "Potential Vulnerability":
                        break  # ✅ Stop testing more payloads on this param
                except Exception as e:
                    error_msg = f"Error: {e}"
                    results.append((test_url, param, payload, error_msg))
                    if log: 
                        log(f"[!] {test_url} → {error_msg}")
    return results

def inject_form_payloads(forms, category="SQLi", log=None):
    if log:
        log(f"[*] Testing {len(forms)} forms for {category}...\n")

    results = []

    for form in forms:
        url = form.get("action")
        method = form.get("method", "GET").upper()
        inputs = form.get("inputs", [])
        origin = form.get("url")

        if not url:
            continue 
        full_url = urljoin(origin, url)

        for payload in default_payloads[category]:
            data = {field: payload for field in inputs}

            try:
                if method == "POST":
                    response = requests.post(full_url, data=data, timeout=5)
                else:
                    response = requests.get(full_url, params=data, timeout=5)

                result = analyze_response(category, response.text)
                results.append((full_url, method, data, result))

                if log:
                    log(f"[{category}] {method} → {full_url}")
                    log(f"    Payload: {data}")
                    log(f"    Result : {result}\n")

                if result == "Potential Vulnerability":
                    break  # ✅ Stop testing more payloads on this form
            except Exception as e:
                err = f"Error: {e}"
                results.append((full_url, method, data, err))
                if log:
                    log(f"[!] Failed: {full_url} → {err}\n")
    return results