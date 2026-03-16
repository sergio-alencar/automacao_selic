from typing import Dict, List, Final, Tuple


class SelicCols:
    RAW_VALUE: Final[str] = "valor"
    RAW_DATE: Final[str] = "data"
    DAILY_FACTOR: Final[str] = "daily_factor"
    REAL_MONTHLY: Final[str] = "real_monthly_selic"
    FOR_SUM: Final[str] = "selic_for_sum"
    ACCUMULATED: Final[str] = "Selic Acumulada"
    MONTH_YEAR: Final[str] = "Mês/Ano"


class ExcelFormats:
    DATE: Final[str] = "dd/mm/yyyy"
    NUMBER: Final[str] = "0.00"


class APIConfig:
    SELIC_SGS_URL: Final[str] = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    START_DATE: Final[str] = "1995-01-01"
    BATCH_FREQ: Final[str] = "9YS-JAN"
    HEADERS: Final[Dict[str, str]] = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }


class DateFormats:
    API: Final[str] = "%d/%m/%Y"
    PANDAS: Final[str] = "%d/%m/%Y"


class DriveConfig:
    SCOPES: Final[List[str]] = ["https://www.googleapis.com/auth/drive.readonly"]
    SCOPES_FULL: Final[List[str]] = ["https://www.googleapis.com/auth/drive"]
    PAGE_SIZE: Final[int] = 1000
    MIME_XLSX: Final[str] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    MIME_XLSM: Final[str] = "application/vnd.ms-excel.sheet.macroEnabled.12"
    MIME_FOLDER: Final[str] = "application/vnd.google-apps.folder"


class LogConfig:
    FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(message)s"
    FILE_MODE: Final[str] = "w"
    ENCODING: Final[str] = "utf-8"


class SystemDefaults:
    CREDENTIALS_FILE: Final[str] = "credentials.json"
    LOG_FILE: Final[str] = "execution_log.log"
    BACKUP_DIR: Final[str] = "backups"
    UPDATED_DIR: Final[str] = "updated_sheets"
    SELIC_SHEET: Final[str] = "SELIC_ACUMULADA"
    SMTP_PORT: Final[int] = 587
    DEV_MAX_FILES: Final[int] = 3


class FileExtensions:
    EXCEL: Final[tuple[str, ...]] = ("*.xlsx", "*.xlsm")
