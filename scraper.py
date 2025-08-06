import requests
import re
import os
from bs4 import BeautifulSoup

SERP_API_KEY = os.getenv("SERP_API_KEY", "c6c98f0d23a0600601f8c7e761e24c2acc3a99fc26488b26cb0c81de3774270b")


def extract_email(text):
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text):
    if not text:
        return None
    match = re.search(r"(\+44\s?7\d{3}|\(?07\d{3}\)?)\s?\d{3}\s?\d{3}", text)
    return match.group(0) if match else None


def scrape_directory_listing(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")

        return {
            "name": soup.title.string.strip() if soup.title else "",
            "phone": extract_phone(text),
            "email": extract_email(text),
            "address": None,  # Optional: can improve later
            "website": url,
            "source": "Yell"
        }
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return None


def scrape_google_search(keyword, county):
    print(f"🔍 Searching Google: {keyword} in {county}")
    params = {
        "engine": "google",
        "q": f"{keyword} in {county} site:yell.com",
        "api_key": SERP_API_KEY,
        "num": 20,
        "hl": "en",
        "gl": "gb"
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print("📦 Raw search data:", data)

    results = []
    for result in data.get("organic_results", []):
        link = result.get("link")
        if not link or "yell.com" not in link:
            continue

        listing = scrape_directory_listing(link)
        if listing:
            results.append(listing)

    print(f"✅ Collected {len(results)} businesses from Yell")
    return results
