# AutomacaoSelic/backup_manager.py

import shutil
import logging
from datetime import datetime
from pathlib import Path


def criar_backup(path_origem: Path, path_backup_base: Path):
    if not path_origem.is_dir():
        logging.error(
            f"ERRO DE BACKUP: A pasta de origem '{path_origem}' não foi encontrada."
        )
        return None

    try:
        path_backup_base.mkdir(parents=True, exist_ok=True)
        data_hora_hoje = datetime.now().strftime("%Y.%m.%d_%H%M%S")
        destino_final = path_backup_base / data_hora_hoje

        logging.info(f"Criando cópia de trabalho segura em: '{destino_final}'")
        shutil.copytree(path_origem, destino_final)
        logging.info("Cópia de trabalho criada com sucesso.")
        return destino_final

    except Exception as e:
        logging.error(f"ERRO INESPERADO DURANTE O BACKUP: {e}")
        return None
