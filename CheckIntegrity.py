from enum import Enum
import os
import json
import hashlib
import datetime
import sys
import Notify

LOG_DIR = "log"
DATA_DIR = "data"
ERROR_DIR = "errors"
LATEST_FILE = os.path.join(LOG_DIR, "latest.log")
DATABASE_FILE = os.path.join(DATA_DIR, "db.json")
DATABASE_BACKUP_FILE = os.path.join(DATA_DIR, "db_backup.json")
# How often to save the handled files in seconds
SAVE_FREQUENCY = 300
DAYS_BETWEEN_RUNS = 14


class Level(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3


def create_data_object(file_hash, modification_time):
    return {"hash": file_hash, "mod_time": modification_time}


class Checker:
    def __init__(self) -> None:
        self.database = self.get_database()
        # This allows to continue from unfinished run
        self.handled_files = self.get_checked_files()
        self.error_file = os.path.join(ERROR_DIR, f"{datetime.datetime.now()}.log")
        self.last_save_time = datetime.datetime.now()
        self.log_file = os.path.join(LOG_DIR, f"{datetime.datetime.now()}.log")
        self.log_message(
            Level.INFO, f"Started with {len(self.handled_files)} files already checked"
        )

    def log_message(self, level: Level, message):
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(
                f"{int(datetime.datetime.now().timestamp())}: {level.name}: {message}\n"
            )

    def get_database(self):
        # If database backup exists, the last save was not successful
        if os.path.isfile(DATABASE_BACKUP_FILE):
            self.log_message(Level.ERROR, "Database was corrupted!")
            with open(DATABASE_BACKUP_FILE, "r", encoding="utf-8") as file:
                db = json.load(file)
            with open(DATABASE_FILE, "w", encoding="utf-8") as file:
                json.dump(db, file)
            os.remove(DATABASE_BACKUP_FILE)
            return db
        if not os.path.isfile(DATABASE_FILE):
            with open(DATABASE_FILE, "w", encoding="utf-8") as file:
                json.dump({}, file)
        with open(DATABASE_FILE, "r", encoding="utf-8") as file:
            db = json.load(file)
        return db

    def get_checked_files(self):
        if not os.path.isfile(LATEST_FILE):
            return set()
        with open(LATEST_FILE, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines()]
        return set(lines)

    def add_to_errors(self, data_object, file_path, file_hash, modification_time):
        self.log_message(Level.ERROR, f"Corruption on {file_path}")
        new_object = create_data_object(file_hash, modification_time)
        with open(self.error_file, "a", encoding="utf-8") as file:
            file.write(f"{file_path}: OLD: {data_object} != NEW: {new_object}\n")
        Notify.send("Corruption", file_path)

    def check_integrity(self, file_path, file_hash, modification_time):
        data_object = self.database.get(file_path)
        # Not in database
        if data_object is None:
            return False
        # File hash matches
        if data_object.get("hash") == file_hash:
            return True
        # File hash doesn't match but modification time does (means it's corrupted)
        if data_object.get("mod_time") == modification_time:
            self.add_to_errors(data_object, file_path, file_hash, modification_time)
            return False
        # File changed but not corrupted
        return False

    def hash_file_sha256(self, file_path):
        with open(file_path, "rb", buffering=0) as f:
            return hashlib.file_digest(f, "sha256").hexdigest()

    def save_progress(self):
        with open(LATEST_FILE, "w", encoding="utf-8") as file:
            for path in self.handled_files:
                file.write(f"{path}\n")
        with open(DATABASE_BACKUP_FILE, "w", encoding="utf-8") as file:
            json.dump(self.database, file)
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.database, file)
        os.remove(DATABASE_BACKUP_FILE)
        self.last_save_time = datetime.datetime.now()
        self.log_message(Level.INFO, "Saved progress")

    def handle_file(self, file_path):
        if file_path in self.handled_files:
            return
        file_hash = self.hash_file_sha256(file_path)
        modification_time = os.path.getmtime(file_path)
        is_unchanged = self.check_integrity(file_path, file_hash, modification_time)
        if not is_unchanged:
            self.database[file_path] = create_data_object(file_hash, modification_time)
        self.handled_files.add(file_path)
        if (
            datetime.datetime.now() - self.last_save_time
        ).total_seconds() > SAVE_FREQUENCY:
            self.save_progress()

    def check_dir(self, dir_path):
        try:
            for item in os.listdir(dir_path):
                full_path = os.path.join(dir_path, item)
                if os.path.isdir(full_path):
                    self.check_dir(full_path)
                else:
                    self.handle_file(full_path)
        except PermissionError:
            self.log_message(Level.ERROR, f"Error trying to access {dir_path}")

    def remove_non_existing(self):
        new_db = {}
        for file_path, data_object in self.database.items():
            if file_path in self.handled_files:
                new_db[file_path] = data_object
        # Backup old database in case the program is stopped while writing the new one
        with open(DATABASE_BACKUP_FILE, "w", encoding="utf-8") as file:
            json.dump(self.database, file)
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(new_db, file)
        os.remove(DATABASE_BACKUP_FILE)

    def clean_up(self):
        if os.path.isfile(LATEST_FILE):
            self.log_message(Level.INFO, f"Removing {LATEST_FILE}")
            os.remove(LATEST_FILE)
        self.log_message(Level.INFO, "Removing non-existing")
        self.remove_non_existing()


def check_enough_time_between(days_between):
    """
    Check if there is no unfinished run (latest.log doesn't exist) and that enough time has passed since last run. 
    """
    if os.path.exists(LATEST_FILE):
        print(f"A previous run was unfinished as {LATEST_FILE} exists. Continuing.")
        return True
    print(f"No run was unfinished as file {LATEST_FILE} doesn't exist.")

    # Get the creation time of the most recently created file in the log dir
    latest_file = max([f for f in os.listdir(LOG_DIR)], key=lambda f: os.path.getctime(os.path.join(LOG_DIR, f)))
    latest_file_path = os.path.join(LOG_DIR, latest_file)
    creation_time = os.path.getctime(latest_file_path)

    # Check if the file was created less than days_between days ago
    time_delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)
    if time_delta > days_between:
        print(f"There were more than {days_between} days since last run. Starting a new one.")
        return True
    print(f"There was a run {days_between} days ago. Not running now.")
    return False


def main():
    if len(sys.argv) < 2:
        print("No root dir given!")
        return
    root_dir = sys.argv[1]
    if not check_enough_time_between(DAYS_BETWEEN_RUNS):
        print(f"Not running on {datetime.datetime.now()}")
        return
    print(f"Starting on {datetime.datetime.now()}")
    checker = Checker()
    checker.check_dir(root_dir)
    checker.clean_up()


if __name__ == "__main__":
    main()
