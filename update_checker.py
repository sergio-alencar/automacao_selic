# AutomacaoSelic/update_checker.py

import logging
import os
import pandas as pd
import config


def houve_atualizacao_selic(df_selic_novo):
    try:
        pastas_backup = sorted(
            [p for p in config.PATH_LOCAL_BACKUP_PURO.iterdir() if p.is_dir()],
            key=os.path.getmtime,
            reverse=True,
        )

        if not pastas_backup:
            logging.info(
                "Nenhum backup anterior encontrado. Prosseguindo com a primeira execução."
            )
            return True

        path_ultimo_backup = pastas_backup[0]
        logging.info(
            f"Verificando atualizações em relação ao último backup: {path_ultimo_backup.name}"
        )

        primeiro_arquivo_antigo = next(path_ultimo_backup.glob("*.xls*"), None)

        if not primeiro_arquivo_antigo:
            logging.warning(
                "Última pasta de backup está vazia. Considerando que há atualização."
            )
            return True

        df_selic_antigo = pd.read_excel(
            primeiro_arquivo_antigo,
            sheet_name=config.NOME_ABA_SELIC,
            skiprows=2,
            usecols="B:C",
        )
        df_selic_antigo.columns = ["Mês/Ano", "Selic Acumulada"]
        df_selic_novo.columns = ["Mês/Ano", "Selic Acumulada"]

        df_selic_antigo["Mês/Ano"] = pd.to_datetime(df_selic_antigo["Mês/Ano"])

        if df_selic_novo.round(6).equals(df_selic_antigo.round(6)):
            logging.warning(
                "VERIFICAÇÃO: Nenhuma atualização nos dados da Selic foi encontrada."
            )
            return False

        else:
            logging.info(
                "VERIFICAÇÃO: Novos dados da Selic encontrados. A atualização irá continuar."
            )
            return True

    except Exception as e:
        logging.error(
            f"Erro ao verificar atualizações: {e}. Prosseguindo com a atualização por segurança."
        )
        return True
