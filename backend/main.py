from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ai_logic import generate_script_json
from processor import process_video_job
from render_engine import stitch_video

import uuid
import os
import traceback

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# ENV URLS
# =========================
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# =========================
# FASTAPI INIT
# =========================
app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "https://lumiaflims.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# TEMP STORAGE
# =========================
TEMP_DIR = "temp"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

# =========================
# JOB STORAGE
# =========================
jobs = {}

# =========================
# START VIDEO GENERATION
# =========================
@app.post("/generate-video")
async def start_video_generation(
    background_tasks: BackgroundTasks,
    topic: str = Form(...),
    ratio: str = Form("16:9"),
    duration: int = Form(...),
    user_id: str = Form(...)
):
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "status": "processing",
        "progress": 10
    }

    print(f"🚀 Job {job_id} started for: {topic}")

    background_tasks.add_task(
        run_full_pipeline,
        topic,
        job_id,
        user_id,
        ratio,
        duration
    )

    return {
        "job_id": job_id
    }

# =========================
# FULL PIPELINE
# =========================
async def run_full_pipeline(
    topic,
    job_id,
    user_id,
    ratio,
    duration
):
    try:
        user_folder = os.path.join(TEMP_DIR, user_id)

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # =========================
        # 1. SCRIPT GENERATION
        # =========================
        script = generate_script_json(topic, duration)

        jobs[job_id]["progress"] = 30

        print(f"📝 Script generated for {job_id}")

        # =========================
        # 2. ASSET PROCESSING
        # =========================
        orientation = (
            "portrait"
            if ratio == "9:16"
            else "landscape"
        )

        assets = await process_video_job(
            script,
            job_id,
            user_folder,
            duration,
            orientation
        )

        jobs[job_id]["progress"] = 70

        print(f"🎙️ Assets downloaded for {job_id}")

        # =========================
        # 3. FINAL RENDER
        # =========================
        final_video_path = stitch_video(
            assets,
            job_id,
            user_folder,
            ratio
        )

        # =========================
        # FINAL VIDEO URL
        # =========================
        video_url = (
            f"{BACKEND_URL}/temp/"
            f"{user_id}/"
            f"{os.path.basename(final_video_path)}"
        )

        jobs[job_id] = {
            "status": "completed",
            "url": video_url,
            "progress": 100
        }

        print(f"✅ Job {job_id} completed!")

    except Exception as e:
        print(f"❌ ERROR IN PIPELINE ({job_id}):")
        traceback.print_exc()

        jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }

# =========================
# JOB STATUS
# =========================
@app.get("/job-status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(
        job_id,
        {"status": "not_found"}
    )

# =========================
# USER VIDEO GALLERY
# =========================
@app.get("/user-videos/{user_id}")
async def get_user_gallery(user_id: str):

    user_folder = os.path.join(
        TEMP_DIR,
        user_id
    )

    if not os.path.exists(user_folder):
        return {"videos": []}

    videos = []

    for file in os.listdir(user_folder):

        if file.endswith("_final.mp4"):

            videos.append({
                "name": file,
                "url": (
                    f"{BACKEND_URL}/temp/"
                    f"{user_id}/{file}"
                )
            })

    return {"videos": videos}

# =========================
# DELETE VIDEO
# =========================
@app.delete("/delete-video/{user_id}/{file_name}")
async def delete_video(
    user_id: str,
    file_name: str
):
    file_path = os.path.join(
        TEMP_DIR,
        user_id,
        file_name
    )

    if os.path.exists(file_path):

        try:
            os.remove(file_path)

            return {
                "status": "deleted"
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }

    return {
        "status": "not_found"
    }