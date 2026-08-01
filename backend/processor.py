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

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 200 and len(r.content) > 5000:
                with open(path, "wb") as f:
                    f.write(r.content)
                return
    except Exception as e:
        print(f"Primary video download failed ({e}), using reliable fallback...")

    # Fallback to guaranteed valid video stream
    fallback_url = fallback_video()
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            r = await client.get(fallback_url)
            with open(path, "wb") as f:
                f.write(r.content)
    except Exception as e:
        print(f"Fallback download error: {e}")


def build_timed_subtitles(words, actual_duration):
    if not words:
        return []

    cleaned_words = [w.strip() for w in words if w.strip()]
    if not cleaned_words:
        return []

    # Chunk into 4-6 word sentence fragments for natural sentence-level captions
    chunks = []
    curr = []
    curr_len = 0

    for w in cleaned_words:
        # Push chunk when exceeding 5 words or 30 chars for readable sentence fragments
        if len(curr) >= 5 or (curr_len + len(w)) > 28:
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
        end_time = round(t + chunk_dur, 3)
        if i == len(chunks) - 1:
            end_time = round(actual_duration, 3)

        formatted_word = c.upper()
        # If over 26 chars, add newline at first space for two-line centering
        if len(formatted_word) > 26 and " " in formatted_word:
            mid = len(formatted_word) // 2
            # Find closest space to middle for balanced line split
            left = formatted_word.rfind(" ", 0, mid)
            right = formatted_word.find(" ", mid)
            split_pos = left if (left != -1 and (right == -1 or mid - left <= right - mid)) else right
            if split_pos != -1:
                formatted_word = formatted_word[:split_pos] + "\n" + formatted_word[split_pos+1:]

        out.append({
            "word": formatted_word,
            "start": round(t, 3),
            "end": end_time
        })
        t = end_time

    return out


def trim_audio_silence(raw_audio):
    try:
        from render_engine import FFMPEG_PATH
        trimmed = raw_audio.replace(".mp3", "_trimmed.mp3")
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", raw_audio,
            "-af", "silenceremove=stop_periods=-1:stop_duration=0.05:stop_threshold=-38dB,apad=pad_dur=0.5",
            trimmed
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(trimmed):
            os.replace(trimmed, raw_audio)
    except Exception as e:
        print(f"Silence trim notice: {e}")


async def process_video_job(script_data, job_id, user_folder, duration, orientation, voice="guy"):

    scenes = script_data.get("scenes", [])
    full_script = script_data.get("full_script", "")
    if not full_script and scenes:
        full_script = " ".join([s.get("narration", "") for s in scenes])

    # 1. Generate master continuous narration audio
    master_audio = os.path.join(user_folder, f"{job_id}_master.mp3")
    print(f"Generating continuous master TTS audio ({voice})...")
    await generate_voice(full_script, master_audio, voice)
    master_dur = get_audio_duration(master_audio)

    # 2. Build full timed subtitles for master narration
    words = full_script.split()
    master_subtitles = build_timed_subtitles(words, master_dur)

    # 3. Calculate scene duration allocations based on narration character weight
    total_chars = sum(len(s.get("narration", "")) for s in scenes) or 1
    
    used = set()
    scene_assets = []
    
    for i, s in enumerate(scenes):
        s_narration = s.get("narration", "")
        weight = len(s_narration) / total_chars if total_chars > 0 else (1.0 / len(scenes))
        scene_dur = round(weight * master_dur, 2)
        if scene_dur <= 0.5:
            scene_dur = 2.0

        v_url = await fetch_stock_video(s.get("keywords", "cinematic"), orientation, used)
        used.add(v_url)

        video_path = os.path.join(user_folder, f"{job_id}_s{i}.mp4")
        await download_file(v_url, video_path)

        scene_assets.append({
            "video": video_path,
            "duration": scene_dur,
            "caption": s.get("caption", "")
        })

    return {
        "master_audio": master_audio,
        "master_duration": master_dur,
        "subtitles": master_subtitles,
        "scenes": scene_assets
    }


