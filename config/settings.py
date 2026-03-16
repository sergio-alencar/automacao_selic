import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent

IS_DEVELOPMENT: bool = os.getenv("DEV_MODE", "True").lower() in (
    "true",
    "1",
    "t",
)

SELIC_SHEET_NAME: str = os.getenv("SELIC_SHEET_NAME", "SELIC_ACUMULADA")
SHARED_DRIVE_ID: str = os.getenv("SHARED_DRIVE_ID", "")
ORIGINAL_FOLDER_ID: str = os.getenv("ORIGINAL_FOLDER_ID", "")
ALERT_EMAIL_RECIPIENT: str = os.getenv("ALERT_EMAIL_RECIPIENT", "")

CREDENTIALS_PATH: Path = BASE_DIR / "credentials.json"
LOG_FILE_PATH: Path = BASE_DIR / "execution_log.log"

LOCAL_BACKUP_PATH: Path = Path(os.getenv("PATH_LOCAL_BACKUP_BASE", "backups"))
LOCAL_UPDATED_SHEETS_PATH: Path = Path(os.getenv("PATH_LOCAL_UPDATED_SHEETS", "updated_sheets"))

EMAIL_CONFIG: Dict[str, Any] = {
    "smtp_server": os.getenv("EMAIL_HOST", ""),
    "port": int(os.getenv("EMAIL_PORT", 587)),
    "user": os.getenv("EMAIL_USER", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),
}
