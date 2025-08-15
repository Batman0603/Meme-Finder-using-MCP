import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_client import trending_reddit_memes, search_reddit_memes

print("=== Trending Memes ===")
memes = trending_reddit_memes(limit=5)
for m in memes:
    print(m["title"], "->", m["url"])


search=input("Enter keyword to search :  ")
print(f"\n=== Search Memes: '{search}' ===")
search_results = search_reddit_memes(search, limit=5)
for m in search_results:
    print(m["title"], "->", m["url"])
