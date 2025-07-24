# AutomacaoSelic/config.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODO_DESENVOLVIMENTO = True

NOME_ABA_SELIC = "SELIC ACUMULADA"

PATH_CREDENTIALS = BASE_DIR / "credentials.json"
PATH_ARQUIVO_LOG = BASE_DIR / "execution_log.log"
PATH_LOCAL_TEMP = BASE_DIR / "temp_files"

DRIVE_ID_ORIGINAL_PROD = "13kYv27L8wEO4koNFy9fBd2e9wBPY-aVk"
DRIVE_ID_ORIGINAL_DEV = DRIVE_ID_ORIGINAL_PROD

PATH_LOCAL_BACKUP_BASE_PROD = Path(
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\Backups_Desenvolvimento"
)
PATH_LOCAL_BACKUP_BASE_DEV = PATH_LOCAL_BACKUP_BASE_PROD

EMAIL_CONFIG = {
    "servidor_smtp": "smtp.gmail.com",
    "porta": 587,
    "usuario": "sergio.alencar@msladvocacia.com.br",
    "senha": "eyhx sxlh dvdq bjan",
}
EMAIL_DESTINATARIO_ALERTA = "sergio.alencar@msladvocacia.com.br"
