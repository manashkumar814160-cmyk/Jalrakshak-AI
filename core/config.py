from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
SAMPLE_WEATHER = DATA_DIR / "sample_weather_hyderabad.json"
DB_PATH = Path(os.getenv("JALRAKSHAK_DB", str(DATA_DIR / "jalrakshak.sqlite3")))
OFFLINE = os.getenv("JALRAKSHAK_OFFLINE", "0").strip() == "1"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
DISCLAIMER = ("This is an estimate based on weather data and standard crop parameters. "
              "Check the soil in the field before irrigating and follow local agricultural advice.")
