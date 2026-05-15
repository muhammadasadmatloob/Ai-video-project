from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from ai_logic import generate_script_json
from processor import process_video_job
from render_engine import stitch_video
from cleanup import delete_old_folders

import uuid
import os
import traceback

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://lumiaflims.vercel.app")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
TEMP_DIR = "temp"

# Run cleanup automatically when the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🧹 Running startup cleanup...")
    delete_old_folders(target_dir=TEMP_DIR, age_hours=24)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "https://lumiaflims.vercel.app",
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

jobs = {}

@app.post("/generate-video")
async def start_video_generation(
    background_tasks: BackgroundTasks,
    topic: str = Form(...),
    ratio: str = Form("16:9"),
    duration: int = Form(...),
    user_id: str = Form(...)
):
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"status": "processing", "progress": 10}
    print(f"🚀 Job {job_id} started for user {user_id}")

    background_tasks.add_task(
        run_full_pipeline, topic, job_id, user_id, ratio, duration
    )
    return {"job_id": job_id}

async def run_full_pipeline(topic, job_id, user_id, ratio, duration):
    try:
        user_folder = os.path.join(TEMP_DIR, user_id)
        os.makedirs(user_folder, exist_ok=True)

        script = generate_script_json(topic, duration)
        jobs[job_id]["progress"] = 30

        orientation = "portrait" if ratio == "9:16" else "landscape"

        assets = await process_video_job(
            script,
            job_id,
            user_folder,
            duration,
            orientation
        )
        jobs[job_id]["progress"] = 70

        final_video_path = stitch_video(assets, job_id, user_folder, ratio)

        video_url = f"{BACKEND_URL}/temp/{user_id}/{os.path.basename(final_video_path)}"

        jobs[job_id] = {
            "status": "completed",
            "url": video_url,
            "progress": 100
        }
        print(f"✅ Job {job_id} completed successfully")

    except Exception as e:
        print("❌ PIPELINE ERROR:\n", traceback.format_exc())
        jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.get("/job-status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/user-videos/{user_id}")
async def get_user_gallery(user_id: str):
    folder = os.path.join(TEMP_DIR, user_id)
    if not os.path.exists(folder):
        return {"videos": []}

    videos = [
        {
            "name": f,
            "url": f"{BACKEND_URL}/temp/{user_id}/{f}"
        }
        for f in os.listdir(folder)
        if f.endswith("_final.mp4")
    ]
    return {"videos": videos}

@app.delete("/delete-video/{user_id}/{file_name}")
async def delete_video(user_id: str, file_name: str):
    path = os.path.join(TEMP_DIR, user_id, file_name)
    if os.path.exists(path):
        os.remove(path)
        return {"status": "deleted"}
    return {"status": "not_found"}