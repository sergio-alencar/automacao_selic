# AutomacaoSelic/main.py

import logging
import config
from backup_manager import criar_backup
from selic_processor import buscar_e_calcular_selic
from excel_updater import atualizar_todas_planilhas


def run():
    path_origem = None
    path_backup_base = None

    if config.MODO_DESENVOLVIMENTO:
        logging.info("--- EXECUTANDO EM MODO DE DESENVOLVIMENTO ---")
        path_origem = config.PATH_DEV_ORIGINAL
        path_backup_base = config.PATH_DEV_BACKUP_BASE

    else:
        logging.info("--- EXECUTANDO EM MODO DE PRODUÇÃO ---")
        path_origem = config.PATH_PROD_ORIGINAL
        path_backup_base = config.PATH_PROD_BACKUP_BASE

    path_da_copia_de_trabalho = criar_backup(path_origem, path_backup_base)

    if path_da_copia_de_trabalho:
        df_selic_calculada = buscar_e_calcular_selic()

        if df_selic_calculada is not None:
            atualizar_todas_planilhas(
                pasta_alvo=path_da_copia_de_trabalho,
                df_selic=df_selic_calculada,
                nome_aba=config.NOME_ABA_SELIC,
            )
            logging.info(
                f"As planilhas modificadas estão na pasta: '{path_da_copia_de_trabalho}'"
            )

        else:
            logging.error(
                "Processo interrompido porque a busca de dados da Selic falhou."
            )

    else:
        logging.error(
            "Processo abortado devido a falha na criação da cópia de trabalho."
        )

    logging.info("--- PROCESSO FINALIZADO ---")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    run()
