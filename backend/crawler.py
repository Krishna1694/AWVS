import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque

def get_all_links(base_url, log=None):
    visited = set()
    internal_links = set()
    queue = deque([base_url])

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            if log: 
                log(f"[Crawl] Visiting: {url}")
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup.find_all("a", href=True):
                href = tag.get("href")
                if href.startswith("mailto:") or href.startswith("javascript:"):
                    continue
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                if base_url in full_url and parsed.scheme.startswith("http"):
                    normalized = parsed.scheme + "://" + parsed.netloc + parsed.path
                    if normalized not in internal_links:
                        internal_links.add(normalized)
                        queue.append(full_url)
                        if log: 
                            log(f"[✔] Added: {normalized}")

        except Exception as e:
            if log: 
                log(f"[!] Error visiting {url} → {e}")

    return internal_links


def extract_forms_from_url(url, log=None):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        forms = []

        for form in soup.find_all("form"):
            action = form.get("action")
            method = form.get("method", "get")
            inputs = [i.get("name") for i in form.find_all("input") if i.get("name")]

            forms.append({
                "url": url,
                "action": action,
                "method": method,
                "inputs": inputs
            })

        return forms
    except Exception as e:
        if log: 
            log(f"[!] Error extracting forms from {url} → {e}")
        return []
