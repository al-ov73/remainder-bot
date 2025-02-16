from tinydb import TinyDB, Query
import os
import pytz
from dotenv import load_dotenv

load_dotenv()

db = TinyDB('db.json')
API_TOKEN = os.getenv("API_TOKEN")
timezone = pytz.timezone("Etc/GMT-4")

remainder_types = {
    "Ежедневно": "dayly",
    "Еженедельно": "weekly",
    "Ежемесячно": "monthly",
}
