import requests
import re
import os
from bs4 import BeautifulSoup

SERP_API_KEY = os.getenv("SERP_API_KEY")

def is_uk_address(address):
    if not address:
        return False

    address = address.lower()

    # Disqualify common non-UK countries
    non_uk_terms = ["united states", "usa", "france", "germany", "canada", "australia"]
    for term in non_uk_terms:
        if term in address:
            return False

    # Confirm if UK-related keywords or postcode present
    if "united kingdom" in address or " uk" in address or ",uk" in address:
        return True

    # UK postcode regex
    postcode_pattern = r"\b([A-Z]{1,2}[0-9R][0-9A-Z]?)\s?[0-9][ABD-HJLNP-UW-Z]{2}\b"
    return re.search(postcode_pattern, address.upper()) is not None


def scrape_google_maps(keyword, location):
    location = f"{location}, United Kingdom"
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps",
        "q": keyword,
        "location": location,
        "type": "search",
        "hl": "en",
        "gl": "gb",
        "google_domain": "google.co.uk",
        "api_key": SERP_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    print("📦 SerpAPI raw data:", data)  # For debugging

    results = []

    for result in data.get("local_results", []):
        title = result.get("title")
        phone = result.get("phone", "N/A")
        address = result.get("address", "N/A")
        website = result.get("website", None)

        if not is_uk_address(address):
            continue

        # Attempt email scrape
        email = "N/A"
        if website:
            try:
                page = requests.get(website, timeout=5)
                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page.text)
                email = emails[0] if emails else "N/A"
            except:
                pass

        results.append({
            "Source": "Google Maps",
            "Business Name": title,
            "Phone": phone,
            "Address": address,
            "Email": email,
            "Website": website if website else "N/A"
        })

    return results


def scrape_yelp(keyword, location):
    headers = {"User-Agent": "Mozilla/5.0"}
    location = f"{location}, United Kingdom"
    url = f"https://www.yelp.co.uk/search?find_desc={keyword}&find_loc={location.replace(' ', '+')}"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    listings = soup.select("li[class*=border-color--default__]")

    for listing in listings:
        name_tag = listing.find("a", href=True)
        address_tag = listing.find("span", class_="css-e81eai")

        name = name_tag.text.strip() if name_tag else None
        address = address_tag.text.strip() if address_tag else "N/A"

        if not name or not is_uk_address(address):
            continue

        results.append({
            "Source": "Yelp",
            "Business Name": name,
            "Phone": "N/A",
            "Address": address,
            "Email": "N/A",
            "Website": "N/A"
        })

    return results
