import time, requests, sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UPLOAD_URL = "http://127.0.0.1:8000/sales/upload"
WATCH_FOLDER = "C:/MedivisionExports"

conn = sqlite3.connect("agent_cache.db")

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".csv"):
            print("Detected:", event.src_path)
            conn.execute("INSERT INTO pending_files(path) VALUES(?)", (event.src_path,))
            conn.commit()

def upload_loop():
    while True:
        rows = conn.execute("SELECT id, path FROM pending_files WHERE uploaded=0").fetchall()
        for rid, path in rows:
            try:
                files = {"file": open(path, "rb")}
                requests.post(UPLOAD_URL, files=files, timeout=5)
                conn.execute("UPDATE pending_files SET uploaded=1 WHERE id=?", (rid,))
                conn.commit()
                print("Uploaded:", path)
            except:
                print("Offline, retry later...")
        time.sleep(30)

observer = Observer()
observer.schedule(Handler(), WATCH_FOLDER, recursive=False)
observer.start()

print("Pharmarec Agent Running...")
upload_loop()
import winreg
import sys

def add_to_startup():
    exe_path = sys.executable  # Path of your EXE when packaged
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "PharmarecAgent", 0, winreg.REG_SZ, exe_path)
    key.Close()
