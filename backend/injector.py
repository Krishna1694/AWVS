import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from backend.scanner import default_payloads, analyze_response

def inject_get_params_from_file(file_path, category="SQLi", log=None):
    seen = set()
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

        dedup_key = (parsed.path, tuple(sorted(params.keys())))
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

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
                        break
                except Exception as e:
                    error_msg = f"Error: {e}"
                    results.append((test_url, param, payload, error_msg))
                    if log: 
                        log(f"[!] {test_url} → {error_msg}")

    return results


def inject_form_payloads(forms, category="SQLi", log=None):
    if log:
        log(f"[*] Testing {len(forms)} forms for {category}...\n")

    seen = set()
    results = []

    for form in forms:
        url = form.get("action")
        method = form.get("method", "GET").upper()
        inputs = form.get("inputs", [])
        origin = form.get("url")

        for payload in default_payloads[category]:
            data = {field: payload for field in inputs}
            full_url = urljoin(origin, url) if url else origin

            dedup_key = (full_url, method, tuple(sorted(data.items())))
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

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
                    break
            except Exception as e:
                err = f"Error: {e}"
                results.append((full_url, method, data, err))
                if log:
                    log(f"[!] Failed: {full_url} → {err}\n")

    return results
