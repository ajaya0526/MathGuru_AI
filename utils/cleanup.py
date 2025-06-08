import os
import time

def clean_old_audio(folder="static/audio", max_age_sec=3600):
    now = time.time()

    # ✅ Ensure the folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)
        return  # Nothing to clean yet

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path) and path.endswith(".mp3"):
            if now - os.path.getmtime(path) > max_age_sec:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"[CLEANUP ERROR] {e}")
