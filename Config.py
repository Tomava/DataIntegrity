import os
from dotenv import load_dotenv

load_dotenv()
PUSHOVER_API_KEY = os.getenv("PUSHOVER_API_KEY")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
