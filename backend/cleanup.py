import os
import time
import shutil

def delete_old_folders(target_dir="temp", age_hours=24):
    now = time.time()
    for folder in os.listdir(target_dir):
        folder_path = os.path.join(target_dir, folder)
        if os.path.isdir(folder_path):
            # If the folder is older than 24 hours, delete it
            if os.stat(folder_path).st_mtime < now - (age_hours * 3600):
                shutil.rmtree(folder_path)
                print(f"🗑️ Cleaned up expired data: {folder}")

# You can run this function at the start of main.py