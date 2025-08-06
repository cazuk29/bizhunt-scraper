import requests
import re
from bs4 import BeautifulSoup

SERP_API_KEY = "c6c98f0d23a0600601f8c7e761e24c2acc3a99fc26488b26cb0c81de3774270b"  # Replace this with your real key

def is_uk_address(address):
    if not address:
        return False
    address = address.lower()

    non_uk_terms = ["united states", "usa", "france", "germany", "canada", "australia"]
    if any(term in address for term in non_uk_terms):
        return False

    if "united kingdom" in address or " uk" in address or ",uk" in address:
        return True

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
        "hl": "en",                   # Force English
        "gl": "gb",                   # Force UK country code
        "google_domain": "google.co.uk",  # UK-specific domain
        "api_key": SERP_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for result in data.get("local_results", []):
        title = result.get("title")
        phone = result.get("phone", "N/A")
        address = result.get("address", "N/A")
        website = result.get("website", None)

        if not is_uk_address(address):
            continue

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

    listings = soup.find_all("div", class_="container__09f24__mpR8_")

    for listing in listings:
        name_tag = listing.find("a", class_="css-19v1rkv")
        if not name_tag:
            continue

        name = name_tag.text.strip()
        address_tag = listing.find("span", class_="raw__09f24__T4Ezm")
        address = address_tag.text.strip() if address_tag else "N/A"

        if not is_uk_address(address):
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
