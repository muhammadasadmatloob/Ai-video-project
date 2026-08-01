import subprocess
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Target specific local FFmpeg setups or default to system PATH for Render
possible_paths = [
    os.path.join(BASE_DIR, "ffmpeg", "bin", "ffmpeg.exe"),
    os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe"),
    os.path.join(BASE_DIR, "ffmpeg", "ffmpeg"),
    "ffmpeg"
]

FFMPEG_PATH = "ffmpeg"
for path in possible_paths:
    if os.path.isfile(path) or shutil.which(path):
        FFMPEG_PATH = path
        break
else:
    try:
        import imageio_ffmpeg
        FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass

FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
FONT_CONFIG = f"fontfile='{FONT_PATH.replace(os.sep, '/')}':" if os.path.exists(FONT_PATH) else ""

SUBTITLE_STYLES = {
    "viral_yellow": {
        "fontcolor": "yellow",
        "fontsize": 48,
        "borderw": 6,
        "bordercolor": "black",
        "box": 0,
        "y": "h*0.75"
    },
    "dark_box": {
        "fontcolor": "white",
        "fontsize": 44,
        "borderw": 0,
        "bordercolor": "black",
        "box": 1,
        "boxcolor": "black@0.65",
        "boxborderw": 12,
        "y": "h*0.75"
    },
    "neon_cyber": {
        "fontcolor": "#00FFFF",
        "fontsize": 46,
        "borderw": 4,
        "bordercolor": "black",
        "box": 0,
        "y": "h*0.75"
    },
    "minimal_clean": {
        "fontcolor": "white",
        "fontsize": 44,
        "borderw": 4,
        "bordercolor": "black",
        "box": 0,
        "y": "h*0.78"
    }
}

def escape_ffmpeg_text(text):
    if not text:
        return ""
    return (
        text.replace("\\", "")
        .replace("'", "")
        .replace('"', "")
        .replace(":", "")
        .replace("%", "\\%")
    )

def build_drawtext_filter(subs, style_key="viral_yellow", caption="", ratio="16:9"):
    style = SUBTITLE_STYLES.get(style_key, SUBTITLE_STYLES["viral_yellow"])
    filters = []

    # Font size for max 3-word caption chunks — readable but stays on screen
    base_fontsize = 32 if ratio == "9:16" else 38

    if not subs:
        return ""


    for s in subs:
        word = escape_ffmpeg_text(s["word"])
        if not word:
            continue

        base = (
            f"drawtext="
            f"{FONT_CONFIG}"
            f"text='{word}':"
            f"enable='between(t,{s['start']},{s['end']})':"
            f"fontcolor={style['fontcolor']}:"
            f"fontsize={base_fontsize}:"
            f"line_spacing=8:"
            f"x=(w-text_w)/2:"
            f"y={style['y']}"
        )

        if style.get("borderw", 0) > 0:
            base += f":borderw={style['borderw']}:bordercolor={style['bordercolor']}"

        if style.get("box", 0) == 1:
            base += f":box=1:boxcolor={style['boxcolor']}:boxborderw={style['boxborderw']}"

        filters.append(base)

    return ",".join(filters)


def stitch_video(assets, job_id, user_folder, ratio, subtitle_style="viral_yellow", bgm="cinematic", topic="Video", target_duration=None):
    safe_topic = "".join([c if (c.isalnum() or c in " -_") else "" for c in topic]).strip().replace(" ", "_")
    if not safe_topic:
        safe_topic = "Video"
    safe_topic = safe_topic[:35]
    output = os.path.join(user_folder, f"{safe_topic}_{job_id}_final.mp4")

    if ratio == "9:16":
        w, h = 480, 854
    else:
        w, h = 854, 480

    # Support legacy asset list or new master continuous structure
    if isinstance(assets, dict):
        master_audio = assets.get("master_audio")
        subtitles = assets.get("subtitles", [])
        scenes = assets.get("scenes", [])
    else:
        scenes = assets
        master_audio = assets[0]["audio"] if assets else None
        subtitles = assets[0]["subtitles"] if assets else []

    scene_files = []

    for i, a in enumerate(scenes):
        out = os.path.join(user_folder, f"scene_{i}.mp4")
        dur = a.get("duration", 4.0)

        # Base filter chain: High FPS, Scale, Crop, Color Grade (Contrast & Saturation) + subtle fade transitions
        base_filter = (
            f"[0:v]"
            f"fps=30,"
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            f"eq=contrast=1.08:saturation=1.2:brightness=0.01,"
            f"fade=in:st=0:d=0.25"
        )

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-threads", "1",
            "-stream_loop", "-1",
            "-i", a["video"],
            "-t", str(dur),
            "-filter_complex", base_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-an",
            out
        ]

        print(f"Rendering Scene {i} (Duration: {dur}s)...")
        subprocess.run(cmd, check=True)
        scene_files.append(out)

    concat_file = os.path.join(user_folder, "concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for s in scene_files:
            safe_path = os.path.abspath(s).replace('\\', '/')
            f.write(f"file '{safe_path}'\n")

    video_concat_temp = os.path.join(user_folder, f"{job_id}_vconcat.mp4")

    concat_cmd = [
        FFMPEG_PATH,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        video_concat_temp
    ]

    print("Merging Video Scenes...")
    subprocess.run(concat_cmd, check=True)

    # Build master subtitle filter chain
    sub_filter = build_drawtext_filter(subtitles, subtitle_style, "", ratio)

    # Audio & Subtitle Mixdown Command
    bgm_file = os.path.join(BASE_DIR, "assets", "bgm", f"{bgm}.mp3")
    has_bgm = bgm != "none" and os.path.exists(bgm_file)

    inputs = ["-i", video_concat_temp, "-i", master_audio]
    if has_bgm:
        inputs.extend(["-stream_loop", "-1", "-i", bgm_file])

    if has_bgm:
        audio_filter = "[1:a]volume=1.0[v_aud];[2:a]volume=0.14[bgm_aud];[v_aud][bgm_aud]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    else:
        audio_filter = "[1:a]volume=1.0[aout]"

    if sub_filter:
        full_filter_complex = f"[0:v]{sub_filter}[vout]; {audio_filter}"
        v_map = "[vout]"
    else:
        full_filter_complex = audio_filter
        v_map = "0:v"

    final_cmd = [
        FFMPEG_PATH,
        "-y",
        *inputs,
        "-filter_complex", full_filter_complex,
        "-map", v_map,
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        output
    ]

    print("Executing Final Pro Mashup Audio & Dynamic Subtitle Mixdown...")
    subprocess.run(final_cmd, check=True)

    # Clean up intermediate files
    for a in scenes:
        try:
            if os.path.exists(a["video"]):
                os.remove(a["video"])
        except Exception:
            pass

    for sf in scene_files:
        try:
            if os.path.exists(sf):
                os.remove(sf)
        except Exception:
            pass

    for tmp in [video_concat_temp, concat_file, master_audio]:
        try:
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    print(f"Final YouTube Pro Mashup video created: {output}")
    return output


