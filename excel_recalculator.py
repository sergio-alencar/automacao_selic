# AutomacaoSelic/excel_recalculator.py

import logging
import xlwings as xw
from pathlib import Path


def recalcular_e_salvar_pasta(pasta_alvo: Path):
    logging.info("--- INICIANDO ETAPA FINAL: RECALCULAÇÃO DE FÓRMULAS ---")

    with xw.App(visible=False) as app:
        arquivos = list(pasta_alvo.glob("*.xlsx")) + list(pasta_alvo.glob("*.xlsm"))

        logging.info(
            f"Encontrados {len(arquivos)} arquivos para forçar a recalculação."
        )

        for i, arquivo in enumerate(arquivos, 1):
            try:
                logging.info(f"Processando arquivo {i}/{len(arquivos)}: {arquivo.name}")

                wb = app.books.open(arquivo)
                wb.save()
                wb.close()

            except Exception as e:
                logging.error(f"Falha ao recalcular o arquivo '{arquivo.name}': {e}")
                continue

    logging.info("--- ETAPA DE RECALCULAÇÃO DE FÓRMULAS CONCLUÍDA ---")
