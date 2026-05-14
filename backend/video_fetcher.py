import httpx
import os
from dotenv import load_dotenv

load_dotenv()
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY")

def get_best_video(video_obj):
    if "large" in video_obj:
        return video_obj["large"]["url"]
    if "medium" in video_obj:
        return video_obj["medium"]["url"]
    if "small" in video_obj:
        return video_obj["small"]["url"]
    return None

async def fetch_stock_video(keyword, orientation="landscape", used_urls=None):
    if used_urls is None:
        used_urls = set()

    query = keyword.replace(",", " ")
    url = (
        f"https://pixabay.com/api/videos/"
        f"?key={PIXABAY_KEY}"
        f"&q={query}"
        f"&per_page=15"
        f"&safesearch=true"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            data = response.json()

            hits = data.get("hits", [])
            if not hits:
                return fallback_video()

            filtered = []
            for vid in hits:
                w = vid.get("videos", {}).get("medium", {}).get("width", 0)
                h = vid.get("videos", {}).get("medium", {}).get("height", 0)

                if orientation == "portrait" and h > w:
                    filtered.append(vid)
                elif orientation == "landscape" and w >= h:
                    filtered.append(vid)

            candidates = filtered if filtered else hits
            candidates.sort(
                key=lambda v: v.get("videos", {}).get("medium", {}).get("width", 0),
                reverse=True
            )

            # Look for the best video that hasn't been used yet
            for cand in candidates:
                best_url = get_best_video(cand["videos"])
                if best_url and best_url not in used_urls:
                    return best_url

            # Fallback if all top results are already used
            if candidates:
                return get_best_video(candidates[0]["videos"])
            
            return fallback_video()

    except Exception as e:
        print("Pixabay fetch error:", e)
        return fallback_video()

def fallback_video():
    return "https://cdn.pixabay.com/vimeo/458072826/space-26368.mp4"