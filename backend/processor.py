import httpx, os, asyncio
from voice_generator import generate_voice
from video_fetcher import fetch_stock_video, fallback_video


async def download_file(url, path):
    if not url:
        url = fallback_video()

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)


def build_timed_subtitles(words, scene_duration=6):
    if not words:
        return []

    word_time = scene_duration / max(len(words), 1)
    t = 0
    out = []

    for i, w in enumerate(words):
        out.append({
            "word": w,
            "start": round(t, 2),
            "end": round(t + word_time, 2)
        })
        t += word_time

    return out


async def process_video_job(script_data, job_id, user_folder, duration, orientation):
    scenes = script_data["scenes"]
    used = set()

    for s in scenes:
        s["final_v_url"] = await fetch_stock_video(
            s["keywords"],
            orientation,
            used
        )
        used.add(s["final_v_url"])

    async def process(i, scene):
        audio = os.path.join(user_folder, f"{job_id}_s{i}.mp3")
        video = os.path.join(user_folder, f"{job_id}_s{i}.mp4")

        await generate_voice(scene["narration"], audio)
        await download_file(scene["final_v_url"], video)

        return {
            "video": video,
            "audio": audio,
            "caption": scene["caption"],
            "subtitles": build_timed_subtitles(scene.get("subtitle_words", []))
        }

    return await asyncio.gather(*[
        process(i, s) for i, s in enumerate(scenes)
    ])