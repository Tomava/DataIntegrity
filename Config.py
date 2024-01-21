import os
from dotenv import load_dotenv

load_dotenv()
PUSHOVER_API_KEY = os.getenv("PUSHOVER_API_KEY")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")

ROOT_DATA_DIR = "data"
LOG_DIR = os.path.join(ROOT_DATA_DIR, "log")
DATA_DIR = os.path.join(ROOT_DATA_DIR, "data")
ERROR_DIR = os.path.join(ROOT_DATA_DIR, "errors")
LATEST_FILE = os.path.join(LOG_DIR, "latest.log")
FINISHED_FILE = os.path.join(DATA_DIR, "finished.txt")
DATABASE_FILE = os.path.join(DATA_DIR, "db.json")
DATABASE_BACKUP_FILE = os.path.join(DATA_DIR, "db_backup.json")
# How often to save the handled files in seconds
SAVE_FREQUENCY = 300
# Default value
DAYS_BETWEEN_RUNS = 14