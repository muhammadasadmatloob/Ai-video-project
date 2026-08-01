import httpx
import os
import asyncio
import subprocess
from voice_generator import generate_voice
from video_fetcher import fetch_stock_video, fallback_video

def get_audio_duration(audio_path):
    try:
        from render_engine import FFMPEG_PATH
        ffprobe_bin = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe.exe")
        if not os.path.exists(ffprobe_bin):
            ffprobe_bin = "ffprobe"
        
        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8').strip()
        return float(out)
    except Exception as e:
        print(f"Error probing audio duration ({e}). Defaulting to estimated duration.")
        return 5.0

async def download_file(url, path):
    if not url:
        url = fallback_video()

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)

def build_timed_subtitles(words, actual_duration):
    if not words:
        return []

    cleaned_words = [w.strip() for w in words if w.strip()]
    if not cleaned_words:
        return []

    # Chunk into 1-2 word punchy cards to prevent text overflow
    chunks = []
    curr = []
    curr_len = 0

    for w in cleaned_words:
        # If adding w exceeds 2 words or 14 chars, push current chunk
        if len(curr) >= 2 or (curr_len + len(w)) > 12:
            if curr:
                chunks.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        chunks.append(" ".join(curr))

    total_chars = sum(len(c) for c in chunks)
    if total_chars == 0:
        total_chars = 1

    t = 0.0
    out = []
    for i, c in enumerate(chunks):
        chunk_len = len(c)
        chunk_dur = (chunk_len / total_chars) * actual_duration
        end_time = round(t + chunk_dur, 2)
        if i == len(chunks) - 1:
            end_time = round(actual_duration, 2)

        formatted_word = c.upper()
        # If still over 14 chars, add newline between words for multiline centering
        if len(formatted_word) > 14 and " " in formatted_word:
            formatted_word = formatted_word.replace(" ", "\n", 1)

        out.append({
            "word": formatted_word,
            "start": round(t, 2),
            "end": end_time
        })
        t = end_time

    return out

async def process_video_job(script_data, job_id, user_folder, duration, orientation, voice="guy"):

    scenes = script_data.get("scenes", [])
    used = set()

    for s in scenes:
        s["final_v_url"] = await fetch_stock_video(
            s["keywords"],
            orientation,
            used
        )
        used.add(s["final_v_url"])

    async def process_scene(i, scene):
        audio = os.path.join(user_folder, f"{job_id}_s{i}.mp3")
        video = os.path.join(user_folder, f"{job_id}_s{i}.mp4")

        await asyncio.gather(
            generate_voice(scene["narration"], audio, voice),
            download_file(scene["final_v_url"], video)
        )

        audio_dur = get_audio_duration(audio)
        subtitles = build_timed_subtitles(scene.get("subtitle_words", []), audio_dur)

        return {
            "video": video,
            "audio": audio,
            "duration": audio_dur,
            "caption": scene.get("caption", ""),
            "subtitles": subtitles
        }

    return await asyncio.gather(*[
        process_scene(i, s) for i, s in enumerate(scenes)
    ])