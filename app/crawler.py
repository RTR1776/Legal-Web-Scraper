import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin

def crawl_site(start_url: str, max_depth: int = 2):
    visited = set()
    queue = deque([(start_url, 0)])
    docs = []

    while queue:
        url, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Capture page content if needed
            docs.append({
                "url": url,
                "content": soup.get_text("\n", strip=True)
            })

            # Enqueue new links
            for link in soup.find_all("a", href=True):
                new_link = urljoin(url, link["href"])
                if new_link not in visited:
                    queue.append((new_link, depth + 1))
        except Exception:
            pass

    return docs

def run_deep_crawler():
    start_urls = [
        "https://labor.mo.gov/pubs-and-forms",
        "https://revisor.mo.gov/main/OneChapter.aspx?chapter=287",
        "https://www.dol.ks.gov/workers-compensation/overview",
        "https://kslegislature.gov/li/b2025_26/statute/044_000_0000_chapter/044_005_0000_article/"
    ]
    all_docs = []
    for url in start_urls:
        all_docs.extend(crawl_site(url, max_depth=3))
    return all_docs