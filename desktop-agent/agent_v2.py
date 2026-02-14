"""
PharmaRec Desktop Agent v1.0
Watches a local folder for sales files and uploads them to the backend.
Features:
- File watcher for CSV/Excel files
- Offline cache with SQLite
- Auto-retry mechanism
- Windows auto-start support
- Comprehensive logging
"""
import os
import sqlite3
import requests
import time
import logging
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


# Configuration
BACKEND_URL = os.getenv("PHARMAREC_BACKEND_URL", "http://127.0.0.1:8000")
UPLOAD_ENDPOINT = f"{BACKEND_URL}/api/sales/upload"
WATCH_FOLDERS = os.getenv("PHARMAREC_WATCH_FOLDERS", "C:/MedivisionExports").split(",")
AGENT_DB = "pharmarec_agent_cache.db"
LOG_FILE = "pharmarec_agent.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PharmarecAgent")


class AgentDatabase:
    """Manage local cache database."""

    def __init__(self, db_path=AGENT_DB):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                uploaded BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt TIMESTAMP,
                error_message TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_file(self, file_path):
        """Add file to upload queue."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pending_files(file_path) VALUES(?)",
                (file_path,)
            )
            conn.commit()
            conn.close()
            logger.info(f"📝 Added to queue: {file_path}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ File already in queue: {file_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Error adding file to queue: {e}")
            return False

    def get_pending_files(self):
        """Get all pending files."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, file_path FROM pending_files WHERE uploaded=0 ORDER BY created_at"
        )
        files = cursor.fetchall()
        conn.close()
        return files

    def mark_uploaded(self, file_id):
        """Mark file as successfully uploaded."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pending_files SET uploaded=1 WHERE id=?",
            (file_id,)
        )
        conn.commit()
        conn.close()

    def mark_error(self, file_id, error_message):
        """Mark file with error."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pending_files SET last_attempt=CURRENT_TIMESTAMP, error_message=? WHERE id=?",
            (error_message, file_id)
        )
        conn.commit()
        conn.close()


class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events."""

    def __init__(self, db):
        self.db = db
        self.supported_extensions = {".csv", ".xlsx", ".xls"}

    def on_created(self, event):
        """Handle file creation."""
        if event.is_dir:
            return

        file_ext = Path(event.src_path).suffix.lower()
        if file_ext in self.supported_extensions:
            logger.info(f"📂 Detected new file: {event.src_path}")
            self.db.add_file(event.src_path)

    def on_modified(self, event):
        """Handle file modification."""
        if event.is_dir:
            return

        file_ext = Path(event.src_path).suffix.lower()
        if file_ext in self.supported_extensions:
            time.sleep(1)
            logger.info(f"✏️ File modified: {event.src_path}")
            if not self._is_pending(event.src_path):
                self.db.add_file(event.src_path)

    def _is_pending(self, file_path):
        """Check if file is already pending."""
        pending = self.db.get_pending_files()
        return any(f[1] == file_path for f in pending)


class UploadManager:
    """Manage file uploads to backend."""

    def __init__(self, db):
        self.db = db

    def upload_file(self, file_path, file_id):
        """Upload single file to backend."""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ File not found: {file_path}")
                self.db.mark_error(file_id, "File not found")
                return False

            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    UPLOAD_ENDPOINT,
                    files=files,
                    timeout=30
                )

            if response.status_code == 200:
                logger.info(f"✅ Successfully uploaded: {file_path}")
                self.db.mark_uploaded(file_id)
                return True
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.warning(f"⚠️ Upload failed: {error_msg}")
                self.db.mark_error(file_id, error_msg)
                return False

        except requests.exceptions.ConnectionError:
            logger.warning("📡 Backend is offline, will retry later...")
            self.db.mark_error(file_id, "Connection error")
            return False
        except requests.exceptions.Timeout:
            logger.warning("⏱️ Upload timeout...")
            self.db.mark_error(file_id, "Timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Upload error: {str(e)}")
            self.db.mark_error(file_id, f"Error: {str(e)}")
            return False

    def process_queue(self):
        """Process all pending files."""
        pending_files = self.db.get_pending_files()

        if not pending_files:
            return

        logger.info(f"📤 Processing {len(pending_files)} pending files...")

        for file_id, file_path in pending_files:
            self.upload_file(file_path, file_id)
            time.sleep(1)


class PharmarecAgent:
    """Main agent application."""

    def __init__(self):
        self.db = AgentDatabase()
        self.upload_manager = UploadManager(self.db)
        self.observer = Observer()
        self.running = False

    def start(self):
        """Start the agent."""
        logger.info("🚀 Starting PharmaRec Desktop Agent...")
        logger.info(f"📂 Watching folders: {WATCH_FOLDERS}")
        logger.info(f"📡 Backend URL: {BACKEND_URL}")

        handler = FileWatcherHandler(self.db)
        for folder in WATCH_FOLDERS:
            folder = folder.strip()
            if os.path.exists(folder):
                self.observer.schedule(handler, folder, recursive=True)
                logger.info(f"👁️ Watching: {folder}")
            else:
                logger.warning(f"⚠️ Folder does not exist: {folder}")

        self.observer.start()
        self.running = True

        logger.info("✅ Agent started successfully")

    def upload_loop(self):
        """Main upload loop."""
        while self.running:
            try:
                self.upload_manager.process_queue()
                time.sleep(30)
            except KeyboardInterrupt:
                logger.info("⏹️ Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"❌ Upload loop error: {e}")
                time.sleep(30)

    def stop(self):
        """Stop the agent."""
        logger.info("⏹️ Stopping agent...")
        self.running = False
        self.observer.stop()
        self.observer.join()
        logger.info("❌ Agent stopped")

    def run(self):
        """Run the agent."""
        self.start()
        try:
            self.upload_loop()
        finally:
            self.stop()


def add_to_startup():
    """Add agent to Windows startup registry."""
    try:
        import winreg
        exe_path = sys.executable
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key,
            "PharmarecAgent",
            0,
            winreg.REG_SZ,
            f'"{exe_path}" "{os.path.abspath(__file__)}"'
        )
        key.Close()
        logger.info("✅ Added to Windows startup")
    except Exception as e:
        logger.warning(f"⚠️ Could not add to startup: {e}")


if __name__ == "__main__":
    logger.info(f"PharmaRec Agent v1.0 started at {datetime.now()}")

    if "--add-startup" in sys.argv:
        add_to_startup()

    agent = PharmarecAgent()
    agent.run()
