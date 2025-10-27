import os
from dotenv import load_dotenv

# Config file where i put variables from env
load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
EMAIL = os.getenv("EMAIL")
PASS = os.getenv("PASS")
API_URL = os.getenv("API_URL")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
