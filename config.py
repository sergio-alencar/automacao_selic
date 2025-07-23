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
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\CONTROLES PADRONIZADOS - Atualizado"
)
PATH_DEV_BACKUP_BASE = Path(
    r"C:\Users\Administrator\Desktop\BACKUP - COMPENSACAO\Backups_Desenvolvimento"
)
