import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
APP_VERSION = "5.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'cosmos.db'}")
SECRET = os.getenv("COSMOS_SECRET", "change-this-secret-in-production")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 20 * 1024 * 1024))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 900))
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
