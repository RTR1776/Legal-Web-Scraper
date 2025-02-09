import requests
from bs4 import BeautifulSoup
import uuid

def scrape_missouri_forms():
    url = "https://labor.mo.gov/workers-compensation/forms"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    docs = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.endswith(".pdf"):
            title = link.get_text(strip=True)
            docs.append({
                "jurisdiction": "Missouri",
                "document_type": "Form",
                "title": title,
                "metadata": {},
                "content": f"PDF content placeholder from {href}",
                "source_url": href,
            })
    return docs

def scrape_kansas_decisions():
    url = "https://dol.ks.gov/workers-compensation/appeals"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    docs = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "decision" in href:
            title = link.get_text(strip=True)
            docs.append({
                "jurisdiction": "Kansas",
                "document_type": "Decision",
                "title": title,
                "metadata": {},
                "content": f"Decision content placeholder from {href}",
                "source_url": href,
            })
    return docs

def run_scraper():
    all_docs = []
    try:
        mo_forms = scrape_missouri_forms()
        all_docs.extend(mo_forms)
    except Exception as e:
        print("Error scraping Missouri forms:", e)
    try:
        ks_decisions = scrape_kansas_decisions()
        all_docs.extend(ks_decisions)
    except Exception as e:
        print("Error scraping Kansas decisions:", e)
    for doc in all_docs:
        doc["id"] = str(uuid.uuid4())
    return all_docs