# AutomacaoSelic/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

MODO_DESENVOLVIMENTO = os.getenv("MODO_DESENVOLVIMENTO", "True").lower() in (
    "true",
    "1",
    "t",
)

NOME_ABA_SELIC = os.getenv("NOME_ABA_SELIC", "SELIC_ACUMULADA")
SHARED_DRIVE_ID = os.getenv("SHARED_DRIVE_ID")
FOLDER_ID_ORIGINAL = os.getenv("FOLDER_ID_ORIGINAL")

PATH_CREDENTIALS = BASE_DIR / "credentials.json"
PATH_ARQUIVO_LOG = BASE_DIR / "execution_log.log"
PATH_LOCAL_TEMP = BASE_DIR / "temp_files"

path_str = os.getenv("PATH_LOCAL_BACKUP_BASE")
PATH_LOCAL_BACKUP_BASE = Path(path_str) if path_str else None

EMAIL_CONFIG = {
    "servidor_smtp": os.getenv("EMAIL_HOST"),
    "porta": int(os.getenv("EMAIL_PORT", 587)),
    "usuario": os.getenv("EMAIL_USER"),
    "senha": os.getenv("EMAIL_PASSWORD"),
}
