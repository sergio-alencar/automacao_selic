class SelicCols:
    RAW_VALUE: str = "valor"
    RAW_DATE: str = "data"
    DAILY_FACTOR: str = "daily_factor"
    REAL_MONTHLY: str = "real_monthly_selic"
    FOR_SUM: str = "selic_for_sum"
    ACCUMULATED: str = "Selic Acumulada"
    MONTH_YEAR: str = "Mês/Ano"


class ExcelFormats:
    DATE: str = "dd/mm/yyyy"
    NUMBER: str = "0.00"


class APIConfig:
    SELIC_SGS_URL: str = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    START_DATE: str = "1995-01-01"
    BATCH_FREQ: str = "9YS-JAN"
    HEADERS: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }


class DateFormats:
    API_AND_PANDAS: str = "%d/%m/%Y"


class DriveConfig:
    SCOPES: list[str] = ["https://www.googleapis.com/auth/drive.readonly"]
    SCOPES_FULL: list[str] = ["https://www.googleapis.com/auth/drive"]
    PAGE_SIZE: int = 1000
    MIME_XLSX: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    MIME_XLSM: str = "application/vnd.ms-excel.sheet.macroEnabled.12"
    MIME_FOLDER: str = "application/vnd.google-apps.folder"
