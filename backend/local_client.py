# local_client.py
# Simple local-folder loader: place images into memes_local/ to use them as a 'local' source.

import os
import base64
import random
from typing import List, Dict
from datetime import datetime

HERE = os.path.dirname(__file__)
MEME_DIR = os.path.join(HERE, "memes_local")
ALLOWED = (".jpg", ".jpeg", ".png", ".gif", ".webp")

os.makedirs(MEME_DIR, exist_ok=True)


def _list_files():
    items = []
    for fn in os.listdir(MEME_DIR):
        ext = os.path.splitext(fn)[1].lower()
        if ext in ALLOWED:
            path = os.path.join(MEME_DIR, fn)
            mtime = os.path.getmtime(path)
            items.append({
                "id": fn,
                "filename": fn,
                "path": path,
                "mtime": mtime,
                "mtime_iso": datetime.utcfromtimestamp(mtime).isoformat() + "Z",
            })
    # newest first
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items


def list_local_memes(limit: int = 8) -> List[Dict]:
    files = _list_files()
    return [{"id": f["id"], "title": f["filename"], "source": "local", "mtime": f["mtime_iso"]} for f in files[:limit]]


def search_local_memes(keyword: str, limit: int = 8) -> List[Dict]:
    files = _list_files()
    keyword = (keyword or "").lower()
    filtered = [f for f in files if keyword in f["filename"].lower()]
    return [{"id": f["id"], "title": f["filename"], "source": "local", "mtime": f["mtime_iso"]} for f in filtered[:limit]]


def random_local_meme() -> Dict:
    files = _list_files()
    if not files:
        return {"error": "no local memes found. drop images into memes_local/"}
    f = random.choice(files)
    return {"id": f["id"], "title": f["filename"], "source": "local", "mtime": f["mtime_iso"]}


def get_local_meme_by_filename(filename: str) -> Dict:
    # Returns base64 data URI (small convenience; for large images prefer streaming or hosting)
    path = os.path.join(MEME_DIR, filename)
    if not os.path.exists(path):
        return {"error": "file not found"}
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"
    with open(path, "rb") as f:
        b = f.read()
    b64 = base64.b64encode(b).decode('ascii')
    return {"id": filename, "title": filename, "source": "local", "image_base64": f"data:{mime};base64,{b64}"}