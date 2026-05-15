import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

def fallback_video():
    return "https://cdn.pixabay.com/vimeo/458072826/space-26368.mp4"

def best(video_dict):
    return (
        video_dict.get("large", {}).get("url") or
        video_dict.get("medium", {}).get("url") or
        video_dict.get("small", {}).get("url")
    )

async def fetch_stock_video(keyword, orientation="landscape", used=None):
    used = used or set()
    url = (
        f"https://pixabay.com/api/videos/"
        f"?key={PIXABAY_KEY}&q={keyword}&per_page=10&safesearch=true"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url)
            data = r.json()

        hits = data.get("hits", [])
        if not hits:
            return fallback_video()

        for h in hits:
            v = best(h.get("videos", {}))
            if v and v not in used:
                return v

        return best(hits[0].get("videos", {})) or fallback_video()

    except Exception:
        return fallback_video()