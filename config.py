# AutomacaoSelic/config.py

from pathlib import Path

MODO_DESENVOLVIMENTO = True

NOME_ABA_SELIC = "SELIC ACUMULADA"

PATH_PROD_ORIGINAL = Path(
    r"G:\Drives compartilhados\Contabil\CLIENTES\RCT\EM COMPENSACAO\0-CONTROLES DE COMPENSACOES\CONTROLES PADRONIZADOS"
)
PATH_PROD_BACKUP_BASE = Path(
    r"G:\Drives compartilhados\Contabil\CLIENTES\RCT\EM COMPENSACAO\0-CONTROLES DE COMPENSACOES\BACK UP"
)

PATH_DEV_ORIGINAL = Path(
    r"G:\Drives compartilhados\Contabil\CLIENTES\RCT\EM COMPENSACAO\0-CONTROLES DE COMPENSACOES\CONTROLES PADRONIZADOS"
)
PATH_DEV_BACKUP_BASE = Path(
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\Backups_Desenvolvimento"
)

EMAIL_CONFIG = {
    "servidor_smtp": "smtp.gmail.com",
    "porta": 587,
    "usuario": "sergio.alencar@msladvocacia.com.br",
    "senha": "eyhx sxlh dvdq bjan",
}

EMAIL_DESTINATARIO_ALERTA = "sergio.alencar@msladvocacia.com.br"

PATH_ARQUIVO_LOG = Path(r"C:\Scripts\AutomacaoSelic\execution_log.log")
