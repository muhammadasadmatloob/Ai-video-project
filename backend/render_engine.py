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

    # Dynamic font size based on aspect ratio to guarantee text fits within margins
    base_fontsize = 34 if ratio == "9:16" else 42

    # Optional top topic badge
    if caption:
        safe_caption = escape_ffmpeg_text(caption)
        filters.append(
            f"drawtext="
            f"{FONT_CONFIG}"
            f"text='🔥 {safe_caption.upper()}':"
            f"fontcolor=yellow:"
            f"fontsize=20:"
            f"x=(w-text_w)/2:"
            f"y=h*0.06:"
            f"box=1:boxcolor=black@0.5:boxborderw=6"
        )

    if not subs:
        return ",".join(filters) if filters else ""

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


def stitch_video(assets, job_id, user_folder, ratio, subtitle_style="viral_yellow", bgm="cinematic", topic="Video"):
    safe_topic = "".join([c if (c.isalnum() or c in " -_") else "" for c in topic]).strip().replace(" ", "_")
    if not safe_topic:
        safe_topic = "Video"
    safe_topic = safe_topic[:35]
    output = os.path.join(user_folder, f"{safe_topic}_{job_id}_final.mp4")


    if ratio == "9:16":
        w, h = 480, 854
    else:
        w, h = 854, 480

    scene_files = []

    for i, a in enumerate(assets):
        out = os.path.join(user_folder, f"scene_{i}.mp4")
        vf = build_drawtext_filter(a["subtitles"], subtitle_style, a.get("caption", ""), ratio)


        # Base filter chain: High FPS, Scale, Crop, Color Grade (Contrast & Saturation)
        base_filter = (
            f"[0:v]"
            f"fps=30,"
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            f"eq=contrast=1.08:saturation=1.2:brightness=0.01"
        )

        if vf:
            filter_complex = f"{base_filter}[v0];[v0]{vf}[v]"
        else:
            filter_complex = f"{base_filter}[v]"

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-threads", "1",
            "-stream_loop", "-1",
            "-i", a["video"],
            "-i", a["audio"],
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-shortest",
            out
        ]

        print(f"Rendering Scene {i}...")
        subprocess.run(cmd, check=True)
        scene_files.append(out)

    concat_file = os.path.join(user_folder, "concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for s in scene_files:
            safe_path = os.path.abspath(s).replace('\\', '/')
            f.write(f"file '{safe_path}'\n")

    merged_temp = os.path.join(user_folder, f"{job_id}_merged.mp4")

    concat_cmd = [
        FFMPEG_PATH,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        merged_temp
    ]

    print("Merging Scenes...")
    subprocess.run(concat_cmd, check=True)

    # Check if Background Music is requested and available
    bgm_file = os.path.join(BASE_DIR, "assets", "bgm", f"{bgm}.mp3")
    if bgm != "none" and os.path.exists(bgm_file):
        print(f"Mixing Background Music: {bgm}...")
        bgm_cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", merged_temp,
            "-stream_loop", "-1",
            "-i", bgm_file,
            "-filter_complex", "[0:a]volume=1.0[v_aud];[1:a]volume=0.14[bgm_aud];[v_aud][bgm_aud]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            output
        ]
        subprocess.run(bgm_cmd, check=True)
        if os.path.exists(merged_temp):
            os.remove(merged_temp)
    else:
        if os.path.exists(output):
            os.remove(output)
        os.rename(merged_temp, output)

    print(f"Final YouTube-level video created: {output}")
    return output