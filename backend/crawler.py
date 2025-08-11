"""Simple crawler utilities"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def extract_forms(url, resp_text):
    soup = BeautifulSoup(resp_text, 'html.parser')
    forms = []
    for form in soup.find_all('form'):
        action = form.get('action') or url
        action = urljoin(url, action)  # <-- normalize to absolute URL
        method = (form.get('method') or 'get').lower()
        inputs = {}
        for inp in form.find_all(['input','textarea','select']):
            name = inp.get('name')
            if not name:
                continue
            val = inp.get('value') or ''
            inputs[name] = val
        forms.append({'action': action, 'method': method, 'inputs': inputs})
    return forms

def simple_crawl(start_url, max_depth=1, write_callback=print, stop_flag=lambda: False):
    visited = set()
    to_visit = [(start_url,0)]
    base = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(start_url))
    results = []
    while to_visit:
        url, depth = to_visit.pop(0)
        if stop_flag():
            break
        if url in visited or depth>max_depth:
            continue
        try:
            r = requests.get(url, timeout=8)
            visited.add(url)
            results.append(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                link = urljoin(base, a['href'])
                if urlparse(link).netloc == urlparse(start_url).netloc and link not in visited:
                    to_visit.append((link, depth+1))
        except Exception as e:
            write_callback(f'crawl error on {url}: {e}')
        time.sleep(0.1)
    return results
