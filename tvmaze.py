import re
import requests

BASE_URL = "https://api.tvmaze.com"


def _strip_html(text):
    """Remove HTML tags from a string."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text)


def _parse_show(show_data):
    """Parse raw TVmaze show data into a clean dict."""
    network_name = None
    if show_data.get("network"):
        network_name = show_data["network"].get("name")
    elif show_data.get("webChannel"):
        network_name = show_data["webChannel"].get("name")

    image_url = None
    if show_data.get("image"):
        image_url = show_data["image"].get("medium")

    rating = None
    if show_data.get("rating"):
        rating = show_data["rating"].get("average")

    return {
        "id": show_data["id"],
        "name": show_data.get("name", ""),
        "genres": show_data.get("genres", []),
        "rating": rating,
        "network": network_name,
        "summary": _strip_html(show_data.get("summary", "")),
        "image": image_url,
        "premiered": show_data.get("premiered"),
        "status": show_data.get("status"),
        "type": show_data.get("type"),
    }


def search_shows(query):
    """Search TVmaze for shows matching query string."""
    resp = requests.get(f"{BASE_URL}/search/shows", params={"q": query}, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    return [_parse_show(item["show"]) for item in results]


def get_show(show_id):
    """Fetch a single show by its TVmaze ID."""
    resp = requests.get(f"{BASE_URL}/shows/{show_id}", timeout=10)
    resp.raise_for_status()
    return _parse_show(resp.json())


def get_shows_by_page(page=0):
    """Bulk-fetch shows from TVmaze (250 per page)."""
    resp = requests.get(f"{BASE_URL}/shows", params={"page": page}, timeout=10)
    resp.raise_for_status()
    return [_parse_show(show) for show in resp.json()]
