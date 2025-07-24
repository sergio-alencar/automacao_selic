# AutomacaoSelic/config.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODO_DESENVOLVIMENTO = True

NOME_ABA_SELIC = "SELIC ACUMULADA"
PATH_CREDENTIALS = BASE_DIR / "credentials.json"
PATH_ARQUIVO_LOG = BASE_DIR / "execution_log.log"

SHARED_DRIVE_ID = "0AGj3IQTkqQIAUk9PVA"
FOLDER_ID_ORIGINAL_PROD = "13kYv27L8wEO4koNFy9fBd2e9wBPY-aVk"
FOLDER_ID_BACKUP_BASE_PROD = Path(
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\Backups_Desenvolvimento"
)

FOLDER_ID_ORIGINAL_DEV = FOLDER_ID_ORIGINAL_PROD
FOLDER_ID_BACKUP_BASE_DEV = FOLDER_ID_BACKUP_BASE_PROD

PATH_LOCAL_BACKUP_BASE = Path(
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\Backups_Desenvolvimento"
)

EMAIL_CONFIG = {
    "servidor_smtp": "smtp.gmail.com",
    "porta": 587,
    "usuario": "sergio.alencar@msladvocacia.com.br",
    "senha": "eyhx sxlh dvdq bjan",
}
EMAIL_DESTINATARIO_ALERTA = "sergio.alencar@msladvocacia.com.br"
