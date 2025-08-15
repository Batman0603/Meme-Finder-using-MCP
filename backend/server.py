# server.py
import os
import sys
import traceback
import logging

from mcp.server.fastmcp import FastMCP

# ---------- logging ----------
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("meme-finder")

# ---------- optional API key (load from env) ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    logger.info("GEMINI_API_KEY loaded from environment")

# ---------- try to import helpers (fail gracefully) ----------
try:
    import reddit_client
except Exception:
    reddit_client = None
    logger.exception("Failed to import reddit_client")

try:
    import local_client
except Exception:
    local_client = None
    logger.exception("Failed to import local_client")

# ---------- create MCP instance ----------
mcp = FastMCP(name="Meme Finder")

# ---------- minimal health tool (ensures list-tools works) ----------
@mcp.tool()
def ping() -> dict:
    """Simple health check."""
    return {"ok": True, "message": "pong"}

# ---------- actual tools (wrapped safely) ----------
@mcp.tool()
def search_memes(keyword: str, platform: str = "reddit", limit: int = 8):
    platform = (platform or "reddit").lower()
    try:
        if platform == "reddit":
            if not reddit_client:
                return {"error": "reddit_client not available"}
            return reddit_client.search_reddit_memes(keyword, limit)
        if platform == "local":
            if not local_client:
                return {"error": "local_client not available"}
            return local_client.search_local_memes(keyword, limit)
        return {"error": "platform not supported. use 'reddit' or 'local'"}
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception("search_memes failed")
        return {"error": str(e), "traceback": tb}

@mcp.tool()
def trending_memes(platform: str = "reddit", limit: int = 8):
    platform = (platform or "reddit").lower()
    try:
        if platform == "reddit":
            if not reddit_client:
                return {"error": "reddit_client not available"}
            return reddit_client.trending_reddit_memes(limit)
        if platform == "local":
            if not local_client:
                return {"error": "local_client not available"}
            return local_client.list_local_memes(limit)
        return {"error": "platform not supported. use 'reddit' or 'local'"}
    except Exception:
        tb = traceback.format_exc()
        logger.exception("trending_memes failed")
        return {"error": "internal", "traceback": tb}

@mcp.tool()
def random_meme(platform: str = "reddit"):
    platform = (platform or "reddit").lower()
    try:
        if platform == "reddit":
            if not reddit_client:
                return {"error": "reddit_client not available"}
            return reddit_client.random_reddit_meme()
        if platform == "local":
            if not local_client:
                return {"error": "local_client not available"}
            return local_client.random_local_meme()
        return {"error": "platform not supported. use 'reddit' or 'local'"}
    except Exception:
        tb = traceback.format_exc()
        logger.exception("random_meme failed")
        return {"error": "internal", "traceback": tb}

@mcp.resource("meme://{source}/{meme_id}")
def get_meme(source: str, meme_id: str):
    try:
        source = (source or "").lower()
        if source == "reddit":
            if not reddit_client:
                return {"error": "reddit_client not available"}
            return reddit_client.get_reddit_meme_by_id(meme_id)
        if source == "local":
            if not local_client:
                return {"error": "local_client not available"}
            return local_client.get_local_meme_by_filename(meme_id)
        return {"error": "unknown source"}
    except Exception:
        tb = traceback.format_exc()
        logger.exception("get_meme failed")
        return {"error": "internal", "traceback": tb}

# ---------- run server (stdio) ----------
if __name__ == "__main__":
    try:
        logger.info("Starting MCP server (transport=stdio)...")
        mcp.run(transport="stdio")
    except Exception:
        logger.exception("mcp.run failed")
        # Exit non-zero so Cline knows the process failed
        sys.exit(1)
