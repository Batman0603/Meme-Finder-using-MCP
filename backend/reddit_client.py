# reddit_client.py
# Small, robust helpers that query Reddit's public JSON endpoints for r/memes.

import requests
import random
from typing import List, Dict

USER_AGENT = "MemeFinder/1.0 (by: yourname)"
REDDIT_BASE = "https://www.reddit.com"
HEADERS = {"User-Agent": USER_AGENT}

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def _post_to_meme_dict(d: Dict) -> Dict:
    """Normalize reddit post data to a small dict."""
    url = d.get("url_overridden_by_dest") or d.get("url") or d.get("thumbnail")
    is_image = isinstance(url, str) and url.lower().endswith(IMAGE_EXTS)
    return {
        "id": d.get("id"),
        "title": d.get("title"),
        "author": d.get("author"),
        "url": url,
        "permalink": f"{REDDIT_BASE}{d.get('permalink')}",
        "is_video": d.get("is_video", False),
        "is_image": is_image,
        "subreddit": d.get("subreddit"),
        "created_utc": d.get("created_utc"),
    }


def _json_get(url: str, params=None, timeout: int = 8):
    """Wrap requests.get with simple checks."""
    try:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Return empty structure on failure - MCP tools should gracefully handle these
        return {"error": str(e)}


def search_reddit_memes(keyword: str, limit: int = 8) -> List[Dict]:
    params = {"q": keyword, "restrict_sr": 1, "sort": "relevance", "limit": limit}
    url = f"{REDDIT_BASE}/r/memes/search.json"
    data = _json_get(url, params=params)
    if data.get("error"):
        return [{"error": data["error"]}]
    posts = data.get("data", {}).get("children", [])
    return [_post_to_meme_dict(p.get("data", {})) for p in posts]


def trending_reddit_memes(limit: int = 8, t: str = "day") -> List[Dict]:
    params = {"limit": limit, "t": t}
    url = f"{REDDIT_BASE}/r/memes/top.json"
    data = _json_get(url, params=params)
    if data.get("error"):
        return [{"error": data["error"]}]
    posts = data.get("data", {}).get("children", [])
    return [_post_to_meme_dict(p.get("data", {})) for p in posts]


def random_reddit_meme():
    # get a larger sample and pick randomly
    posts = trending_reddit_memes(limit=50)
    posts = [p for p in posts if isinstance(p, dict) and not p.get("error")]
    if not posts:
        return {"error": "no memes found"}
    return random.choice(posts)


def get_reddit_meme_by_id(post_id: str) -> Dict:
    # reddit comments endpoint returns the thread JSON for a post id
    url = f"{REDDIT_BASE}/comments/{post_id}.json"
    data = _json_get(url, params={"raw_json": 1})
    if data.get("error"):
        return {"error": data["error"]}
    try:
        post = data[0].get("data", {}).get("children", [])[0].get("data", {})
        return _post_to_meme_dict(post)
    except Exception as e:
        return {"error": f"could not parse reddit response: {e}"}