import subprocess
import os
import imageio_ffmpeg

# ✅ FIX: Grabs the portable FFmpeg binary installed via pip
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

def build_drawtext_filter(subs):
    if not subs:
        return ""
    filters = []
    for s in subs:
        filters.append(
            f"drawtext=text='{s['word']}':"
            f"enable='between(t,{s['start']},{s['end']})':"
            f"fontcolor=white:fontsize=48:"
            f"x=(w-text_w)/2:y=h*0.8:borderw=4:bordercolor=black"
        )
    return ",".join(filters)

def stitch_video(assets, job_id, user_folder, ratio):
    output = os.path.join(user_folder, f"{job_id}_final.mp4")
    w, h = (720, 1280) if ratio == "9:16" else (1280, 720)

    scene_files = []

    for i, a in enumerate(assets):
        out = os.path.join(user_folder, f"scene_{i}.mp4")
        vf = build_drawtext_filter(a["subtitles"])
        
        # Base filter handles resizing and cropping
        filter_complex = f"[0:v]fps=30,scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[v0]"
        
        # Only add subtitle mapping if subtitles exist
        if vf:
            filter_complex += f";[v0]{vf}[v]"
        else:
            filter_complex += ";[v0]copy[v]"

        cmd = [
            FFMPEG_PATH, "-y",
            "-stream_loop", "-1",
            "-i", a["video"],
            "-i", a["audio"],
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            out
        ]

        subprocess.run(cmd, check=True)
        scene_files.append(out)

    concat_file = os.path.join(user_folder, "concat.txt")
    with open(concat_file, "w") as f:
        for s in scene_files:
            f.write(f"file '{os.path.abspath(s)}'\n")

    final_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output
    ]

    subprocess.run(final_cmd, check=True)
    return output