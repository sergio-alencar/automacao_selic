import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from config.constants import SystemDefaults

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent

IS_DEVELOPMENT: bool = os.getenv("DEV_MODE", "True").lower() in ("true", "1", "t")

SELIC_SHEET_NAME: str = os.getenv("SELIC_SHEET_NAME", SystemDefaults.SELIC_SHEET)
SHARED_DRIVE_ID: str = os.getenv("SHARED_DRIVE_ID", "")
ORIGINAL_FOLDER_ID: str = os.getenv("ORIGINAL_FOLDER_ID", "")
ALERT_EMAIL_RECIPIENT: str = os.getenv("ALERT_EMAIL_RECIPIENT", "")

CREDENTIALS_PATH: Path = BASE_DIR / SystemDefaults.CREDENTIALS_FILE
LOG_FILE_PATH: Path = BASE_DIR / SystemDefaults.LOG_FILE

LOCAL_BACKUP_PATH: Path = Path(os.getenv("PATH_LOCAL_BACKUP_BASE", SystemDefaults.BACKUP_DIR))
LOCAL_UPDATED_SHEETS_PATH: Path = Path(
    os.getenv("PATH_LOCAL_UPDATED_SHEETS", SystemDefaults.UPDATED_DIR)
)


@dataclass(frozen=True)
class EmailConfig:
    smtp_server: str
    port: int
    user: str
    password: str


EMAIL_SETTINGS = EmailConfig(
    smtp_server=os.getenv("EMAIL_HOST", ""),
    port=int(os.getenv("EMAIL_PORT", SystemDefaults.SMTP_PORT)),
    user=os.getenv("EMAIL_USER", ""),
    password=os.getenv("EMAIL_PASSWORD", ""),
)
