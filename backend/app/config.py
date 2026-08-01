import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    OLLAMA_URL: str = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:3b"
    )

    MAX_PROFILE_ROWS: int = int(
        os.getenv("MAX_PROFILE_ROWS", "200000")
    )

    STORAGE_DIR: Path = BASE_DIR / os.getenv(
        "STORAGE_DIR",
        "storage"
    )

    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    REPORTS_DIR: Path = STORAGE_DIR / "reports"

    FRONTEND_ORIGIN: str = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    )

    def ensure_dirs(self):
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()