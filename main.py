# AutomacaoSelic/main.py

import logging
import traceback
import config
from datetime import datetime
import google_drive_manager as gdm
from selic_processor import buscar_e_calcular_selic
from excel_updater import atualizar_todas_planilhas
from email_notifier import enviar_email_de_erro


def run():
    logging.info("=========================================================")
    logging.info("=== INICIANDO EXECUÇÃO DA AUTOMAÇÃO GOOGLE DRIVE API ===")
    logging.info("=========================================================")

    drive_service = gdm.get_drive_service(config.PATH_CREDENTIALS)
    if not drive_service:
        raise Exception("Falha na autenticação com Google Drive.")

    if config.MODO_DESENVOLVIMENTO:
        logging.info("--- EXECUTANDO EM MODO DE DESENVOLVIMENTO ---")
        id_pasta_origem = config.FOLDER_ID_ORIGINAL_DEV

    else:
        logging.info("--- EXECUTANDO EM MODO DE PRODUÇÃO ---")
        id_pasta_origem = config.FOLDER_ID_ORIGINAL_PROD

    nome_pasta_backup = datetime.now().strftime("%Y.%m.%d_%H%M%S")
    path_backup_dia_local = config.PATH_LOCAL_BACKUP_BASE / nome_pasta_backup
    path_backup_dia_local.mkdir(parents=True, exist_ok=True)
    logging.info(f"Pasta de backup local criada em '{path_backup_dia_local}'.")

    arquivos_no_drive = gdm.list_files(
        drive_service, id_pasta_origem, config.SHARED_DRIVE_ID
    )
    if not arquivos_no_drive:
        logging.warning("Nenhum arquivo encontrado. Finalizando...")
        return

    logging.info(f"Baixando {len(arquivos_no_drive)} arquivos...")
    for arquivo in arquivos_no_drive:
        caminho_local_destino = path_backup_dia_local / arquivo["name"]
        gdm.download_file(drive_service, arquivo["id"], caminho_local_destino)
    logging.info("Download de todos os arquivos concluído.")

    df_selic_calculada = buscar_e_calcular_selic()
    if df_selic_calculada is None:
        raise Exception("Busca de dados da Selic falhou.")

    atualizar_todas_planilhas(
        pasta_alvo=path_backup_dia_local,
        df_selic=df_selic_calculada,
        nome_aba=config.NOME_ABA_SELIC,
    )

    logging.info("=== EXECUÇÃO CONCLUÍDA COM SUCESSO ===")
    logging.info(f"As planilhas modificadas estão na pasta: '{path_backup_dia_local}'")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.PATH_ARQUIVO_LOG, mode="a"),
            logging.StreamHandler(),
        ],
    )

    try:
        run()

    except Exception as e:
        logging.error("!!!!!! UMA FALHA CRÍTICA OCORREU !!!!!!")
        logging.error(traceback.format_exc())

        assunto = "ALERTA: Falha na execução do robô atualizador de planilhas Selic"
        corpo = (
            "Ocorreu um erro crítico durante a execução do script de atualização da Selic.\n\n"
            "Por favor, verifique o arquivo de log para mais detalhes.\n\n"
            "==================== MENSAGEM DE ERRO ====================\n"
            f"{traceback.format_exc()}"
        )
        enviar_email_de_erro(
            assunto, corpo, config.EMAIL_DESTINATARIO_ALERTA, config.EMAIL_CONFIG
        )
        logging.error("===================================================")
