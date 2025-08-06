import requests
import re
import os

SERP_API_KEY = os.getenv("SERP_API_KEY", "c6c98f0d23a0600601f8c7e761e24c2acc3a99fc26488b26cb0c81de3774270b")


def extract_email(text):
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def get_serpapi_location(county):
    """Gets a matching UK location string from SerpAPI's /locations.json."""
    try:
        response = requests.get(
            "https://serpapi.com/locations.json",
            params={"q": f"{county}, United Kingdom"}
        )
        locations = response.json()
        if locations:
            print(f"📍 Matched location: {locations[0]['canonical_name']}")
            return locations[0]['canonical_name']
    except Exception as e:
        print(f"❌ Error fetching location: {e}")
    return f"{county}, United Kingdom"  # fallback


def scrape_google_maps(keyword, county):
    location = get_serpapi_location(county)
    print(f"🔍 Google Maps Search: {keyword} in {location}")

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

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print("📦 SerpAPI raw data:", data)

    results = []
    local_results = data.get("local_results", [])

    for biz in local_results:
        result = {
            "name": biz.get("title"),
            "address": biz.get("address"),
            "phone": biz.get("phone"),
            "website": biz.get("website"),
            "email": extract_email(biz.get("website")),
            "source": "Google Maps"
        }
        results.append(result)

    print(f"✅ Returning {len(results)} Google results")
    return results


def scrape_yelp(keyword, county):
    location = get_serpapi_location(county)
    print(f"🔍 Yelp Search: {keyword} in {location}")

    params = {
        "engine": "yelp",
        "q": keyword,
        "location": location,
        "api_key": SERP_API_KEY
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print("📦 Yelp raw data:", data)

    results = []
    for biz in data.get("businesses", []):
        result = {
            "name": biz.get("name"),
            "address": biz.get("address"),
            "phone": biz.get("phone"),
            "website": biz.get("website"),
            "email": extract_email(biz.get("website")),
            "source": "Yelp"
        }
        results.append(result)

    print(f"✅ Returning {len(results)} Yelp results")
    return results
