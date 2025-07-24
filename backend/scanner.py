import requests

# Basic payloads for each category (you can later load from files or user input)
default_payloads = {
    "SQLi": ["' OR '1'='1", "' AND 1=2--", "' OR 1=1--", "' UNION SELECT NULL--"],
    "XSS": ["<script>alert(1)</script>", "\" onmouseover=\"alert(1)", "'><svg onload=alert(1)>"],
    "CMD": ["; whoami", "&& whoami", "| whoami", "`whoami`", "$(whoami)"],
    "HTML": [ "<b>Test</b>", "<i>Italic</i>", "<img src=x onerror=alert(1)>"]
}

def scan_for_vulnerabilities(url, selected_payloads):
    results = {}

    for category, payloads in selected_payloads.items():
        if not payloads:
            continue

        results[category] = []
        for payload in payloads:
            try:
                test_url = f"{url}?input={payload}"
                response = requests.get(test_url, timeout=5)
                result = analyze_response(category, response.text)
                results[category].append((payload, result))
            except Exception as e:
                results[category].append((payload, f"Error: {e}"))

    return results

def analyze_response(category, response_text):
    """
    Very basic vulnerability indicator logic.
    """
    if category == "SQLi":
        indicators = ["SQL", "syntax", "mysql", "error"]
    elif category == "XSS":
        indicators = ["<script>", "alert", "onerror"]
    elif category == "CMD":
        indicators = ["uid=", "root", "bin/bash"]
    elif category == "HTML":
        indicators = ["<b>", "<i>", "<img"]

    for indicator in indicators:
        if indicator.lower() in response_text.lower():
            return "Potential Vulnerability"
    return "No Issue Detected"
