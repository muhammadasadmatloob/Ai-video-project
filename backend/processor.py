import httpx, os, asyncio
from voice_generator import generate_voice
from video_fetcher import fetch_stock_video

async def download_file(url, path):
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)

def build_timed_subtitles(words, scene_duration=6):
    if not words:
        return []

    safe_duration = scene_duration - 0.2
    word_duration = safe_duration / len(words)
    timeline = []
    t = 0

    for i, w in enumerate(words):
        start = t
        end = t + word_duration
        if i == len(words) - 1:
            end = scene_duration

        timeline.append({
            "word": w,
            "start": round(start, 2),
            "end": round(end, 2)
        })
        t += word_duration

    return timeline

async def process_video_job(script_data, job_id, user_folder, duration, orientation):
    scenes = script_data['scenes']
    used_videos = set()

    # 1. Fetch URLs sequentially to entirely prevent duplicates
    for scene in scenes:
        v_url = await fetch_stock_video(scene['keywords'], orientation, used_videos)
        scene['final_v_url'] = v_url
        if v_url:
            used_videos.add(v_url)

    # 2. Process audio and download videos concurrently
    async def process_single_scene(i, scene):
        audio_p = os.path.join(user_folder, f"{job_id}_s{i}.mp3")
        video_p = os.path.join(user_folder, f"{job_id}_s{i}.mp4")

        await generate_voice(scene['narration'], audio_p)
        await download_file(scene['final_v_url'], video_p)

        words = scene.get("subtitle_words", [])

        return {
            "video": video_p,
            "audio": audio_p,
            "caption": scene["caption"],
            "subtitles": build_timed_subtitles(words, scene_duration=6)
        }

    tasks = [process_single_scene(i, s) for i, s in enumerate(scenes)]
    return await asyncio.gather(*tasks)