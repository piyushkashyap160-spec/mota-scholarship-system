import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
SAMPLE_DOCS_DIR = os.path.join(BASE_DIR, "sample_docs")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'mota_scholarship.db')}")

SECRET_KEY = os.getenv("SECRET_KEY", "mota-sih-st-fellowship-jwt-secret-key-26239-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
