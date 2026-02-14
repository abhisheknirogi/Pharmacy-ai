import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

class MedivisionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.csv', '.xlsx')):
            print(f"📦 New report detected: {event.src_path}")
            self.upload_to_backend(event.src_path)

    def upload_to_backend(self, path):
        url = "http://localhost:8000/api/sales/upload"
        files = {'file': open(path, 'rb')}
        try:
            r = requests.post(url, files=files)
            print(f"🚀 Upload status: {r.status_code}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

# Start watching the 'data/sales' folder
observer = Observer()
observer.schedule(MedivisionHandler(), path='./data/sales', recursive=False)
observer.start()