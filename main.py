# AutomacaoSelic/main.py

import logging
import traceback
from datetime import datetime
import config
import google_drive_manager as gdm
from selic_processor import buscar_e_calcular_selic
from excel_updater import atualizar_todas_planilhas
from email_notifier import enviar_email_de_erro
from logger_config import setup_logging
from update_checker import houve_atualizacao_selic
from excel_recalculator import recalcular_e_salvar_pasta


def run():
    logging.info("=========================================================")
    logging.info("=== INICIANDO AUTOMAÇÃO DE ATUALIZAÇÃO DE PLANILHAS ===")
    logging.info("=========================================================")

    df_selic_calculada = buscar_e_calcular_selic()

    if df_selic_calculada is None:
        raise Exception("Busca de dados da Selic falhou.")

    if not houve_atualizacao_selic(df_selic_calculada.copy()):
        logging.info(
            "Execução interrompida, pois não há novos dados. Próxima tentativa agendada."
        )
        return

    drive_service = gdm.get_drive_service(config.PATH_CREDENTIALS)

    if not drive_service:
        raise Exception("Falha na autenticação com Google Drive.")

    nome_pasta_timestamp = datetime.now().strftime("%Y.%m.%d_%H%M%S")
    path_backup_puro_dia = config.PATH_LOCAL_BACKUP_PURO / nome_pasta_timestamp
    path_atualizadas_dia = (
        config.PATH_LOCAL_PLANILHAS_ATUALIZADAS / nome_pasta_timestamp
    )
    path_backup_puro_dia.mkdir(parents=True, exist_ok=True)
    path_atualizadas_dia.mkdir(parents=True, exist_ok=True)
    logging.info(f"Pasta de backup puro criada em: '{path_backup_puro_dia}'")
    logging.info(
        f"Pasta para planilhas atualizadas criada em: '{path_atualizadas_dia}'"
    )

    arquivos_no_drive = gdm.list_files(
        drive_service, config.FOLDER_ID_ORIGINAL, config.SHARED_DRIVE_ID
    )

    if not arquivos_no_drive:
        logging.warning(
            "Nenhum arquivo encontrado na pasta de origem do Drive. finalizando"
        )
        return

    logging.info(
        f"Baixando {len(arquivos_no_drive)} arquivos para as duas pastas de destino..."
    )

    for arquivo in arquivos_no_drive:
        gdm.download_file(
            drive_service, arquivo["id"], path_backup_puro_dia / arquivo["name"]
        )
        gdm.download_file(
            drive_service, arquivo["id"], path_atualizadas_dia / arquivo["name"]
        )
    logging.info("Download de todos os arquivos concluído.")

    logging.info("Iniciando a atualização das planilhas de destino...")
    atualizar_todas_planilhas(
        pasta_alvo=path_atualizadas_dia,
        df_selic=df_selic_calculada,
        nome_aba=config.NOME_ABA_SELIC,
    )

    recalcular_e_salvar_pasta(path_atualizadas_dia)

    logging.info("=== EXECUÇÃO CONCLUÍDA COM SUCESSO ===")
    logging.info(f"Backup puro salvo em: '{path_backup_puro_dia}'")
    logging.info(f"Planilhas atualizadas salvas em: '{path_atualizadas_dia}'")


if __name__ == "__main__":
    setup_logging()

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
