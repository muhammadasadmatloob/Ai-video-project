import subprocess
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Target specific local FFmpeg setups or default to system PATH for Render
possible_paths = [
    os.path.join(BASE_DIR, "ffmpeg", "bin", "ffmpeg.exe"), # Explicit local bin path
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

def build_drawtext_filter(subs):
    if not subs:
        return ""

    filters = []
    for s in subs:
        word = (
            s["word"]
            .replace("'", "")
            .replace('"', "")
            .replace(":", "")
            .replace("\\", "")
        )

        filters.append(
            f"drawtext="
            f"{FONT_CONFIG}"
            f"text='{word}':"
            f"enable='between(t,{s['start']},{s['end']})':"
            f"fontcolor=white:"
            f"fontsize=48:"
            f"x=(w-text_w)/2:"
            f"y=h*0.8:"
            f"borderw=4:"
            f"bordercolor=black"
        )

    return ",".join(filters)

def stitch_video(assets, job_id, user_folder, ratio):
    output = os.path.join(user_folder, f"{job_id}_final.mp4")

    if ratio == "9:16":
        w, h = 720, 1280
    else:
        w, h = 1280, 720

    scene_files = []

    for i, a in enumerate(assets):
        out = os.path.join(user_folder, f"scene_{i}.mp4")
        vf = build_drawtext_filter(a["subtitles"])

        base_filter = (
            f"[0:v]"
            f"fps=30,"
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}"
        )

        if vf:
            filter_complex = f"{base_filter}[v0];[v0]{vf}[v]"
        else:
            filter_complex = f"{base_filter}[v]"

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-stream_loop", "-1",
            "-i", a["video"],
            "-i", a["audio"],
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-shortest",
            out
        ]

        print(f"🎬 Running FFmpeg Command for Scene {i}")
        subprocess.run(cmd, check=True)
        scene_files.append(out)

    concat_file = os.path.join(user_folder, "concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for s in scene_files:
            # Ensure FFmpeg doesn't break on Windows backslashes
            safe_path = os.path.abspath(s).replace('\\', '/')
            f.write(f"file '{safe_path}'\n")

    final_cmd = [
        FFMPEG_PATH,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output
    ]

    print("🎞️ Merging Final Video...")
    subprocess.run(final_cmd, check=True)
    print(f"✅ Final video created: {output}")

    return output