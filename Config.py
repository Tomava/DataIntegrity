import os
from dotenv import load_dotenv

load_dotenv()
GOTIFY_URL = os.getenv("GOTIFY_URL")
GOTIFY_TOKEN = os.getenv("GOTIFY_TOKEN")

DATA_DIR = "data"
LOG_DIR = os.path.join(DATA_DIR, "log")
DATA_DIR = os.path.join(DATA_DIR, "data")
ERROR_DIR = os.path.join(DATA_DIR, "errors")
LATEST_FILE = os.path.join(LOG_DIR, "latest.log")
FINISHED_FILE = os.path.join(DATA_DIR, "finished.txt")
DATABASE_FILE = os.path.join(DATA_DIR, "db.json")
DATABASE_BACKUP_FILE = os.path.join(DATA_DIR, "db_backup.json")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)

# How often to save the handled files in seconds
SAVE_FREQUENCY_SECONDS = int(os.getenv("SAVE_FREQUENCY_SECONDS", "300"))
DAYS_BETWEEN_RUNS = int(os.getenv("DAYS_BETWEEN_RUNS", "14"))
