import subprocess, os

FFMPEG_PATH = "ffmpeg"

def build_drawtext_filter(subs):
    filters = []
    for s in subs:
        word = s["word"].replace("'", "").replace(":", "")
        start = s["start"]
        end = s["end"]

        filters.append(
            f"drawtext=text='{word}':"
            f"enable='between(t,{start},{end})':"
            f"fontcolor=white:"
            f"fontsize=48:"
            f"font='Arial':"
            f"x=(w-text_w)/2:"
            f"y=h-(h*0.20):"
            f"borderw=4:"
            f"bordercolor=black@0.9"
        )
    return ",".join(filters)

def stitch_video(assets, job_id, user_folder, ratio):
    output_path = os.path.join(user_folder, f"{job_id}_final.mp4")
    w, h = (720, 1280) if ratio == "9:16" else (1280, 720)
    scene_files = []

    for i, asset in enumerate(assets):
        out_p = os.path.join(user_folder, f"scene_{i}.mp4")
        v = asset["video"].replace("\\", "/")
        a = asset["audio"].replace("\\", "/")

        subtitle_filter = build_drawtext_filter(asset["subtitles"])

        cmd = [
            FFMPEG_PATH, "-y",
            "-stream_loop", "-1",
            "-i", v,
            "-i", a,

            "-filter_complex",
            (
                f"[0:v]fps=30,scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},setsar=1[v0];"
                f"[v0]{subtitle_filter}[v]"
            ),

            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-c:a", "aac",           # 🔥 ENCODES TO BROWSER COMPATIBLE AUDIO
            "-b:a", "192k",          # 🔥 HIGH QUALITY AUDIO BITRATE
            "-preset", "ultrafast",   
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-shortest",
            out_p
        ]

        subprocess.run(cmd, check=True)
        scene_files.append(out_p)

    concat_file = os.path.join(user_folder, "concat.txt")
    with open(concat_file, "w") as f:
        for s in scene_files:
            f.write(f"file '{os.path.basename(s)}'\n")

    final_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file.replace("\\", "/"),
        "-c:v", "libx264",
        "-c:a", "aac",               # 🔥 ENSURE FINAL OUTPUT REMAINS AAC
        "-pix_fmt", "yuv420p",
        output_path.replace("\\", "/")
    ]

    subprocess.run(final_cmd, check=True)
    return output_path