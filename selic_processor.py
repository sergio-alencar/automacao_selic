# AutomacaoSelic/selic_processor.py

import pandas as pd
import requests
import logging
from datetime import datetime


def buscar_e_calcular_selic():
    logging.info("Iniciando busca da Selic diária (SGS 11) em lotes...")

    start_date = pd.to_datetime("1995-01-01")
    end_date = datetime.now()
    date_periods = pd.date_range(start=start_date, end=end_date, freq="9YS-JAN")
    all_dataframes = []

    for i, period_start in enumerate(date_periods):
        if i + 1 < len(date_periods):
            period_end = date_periods[i + 1] - pd.Timedelta(days=1)
        else:
            period_end = end_date
        data_inicial_str = period_start.strftime("%d/%m/%Y")
        data_final_str = period_end.strftime("%d/%m/%Y")
        url_api = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={data_inicial_str}&dataFinal={data_final_str}"
        logging.info(
            f"Buscando lote de dados: {data_inicial_str} a {data_final_str}..."
        )
        try:
            headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
            response = requests.get(url_api, headers=headers)
            response.raise_for_status()
            dados_lote = response.json()
            if dados_lote:
                all_dataframes.append(pd.DataFrame(dados_lote))
        except requests.exceptions.RequestException as e:
            logging.error(
                f"FALHA ao buscar o lote {data_inicial_str}-{data_final_str}: {e}"
            )
            return None

    if not all_dataframes:
        logging.error("Nenhum dado foi baixado da API.")
        return None

    df_diario = pd.concat(all_dataframes, ignore_index=True)

    logging.info("Calculando a taxa mensal real via juros compostos...")

    df_diario["valor"] = pd.to_numeric(df_diario["valor"])
    df_diario["data"] = pd.to_datetime(df_diario["data"], format="%d/%m/%Y")
    df_diario["fator_diario"] = 1 + (df_diario["valor"] / 100)

    df_fatores_mensais = (
        df_diario.groupby(pd.Grouper(key="data", freq="ME"))["fator_diario"]
        .prod()
        .reset_index()
    )
    df_fatores_mensais["selic_real_do_mes"] = (
        df_fatores_mensais["fator_diario"] - 1
    ) * 100
    df_fatores_mensais["selic_real_do_mes"] = df_fatores_mensais[
        "selic_real_do_mes"
    ].round(2)

    df_mensal = df_fatores_mensais.rename(columns={"data": "data"})[
        ["data", "selic_real_do_mes"]
    ]

    logging.info("Aplicando a regra de negócio Sicalc (mês anterior = 1%)...")
    hoje = datetime.now()
    primeiro_dia_mes_atual = hoje.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    df_historico = df_mensal[df_mensal["data"] < primeiro_dia_mes_atual].copy()
    df_historico.sort_values(by="data", ascending=False, inplace=True)
    df_historico["selic_para_soma"] = df_historico["selic_real_do_mes"].shift(1)
    df_historico.iloc[0, df_historico.columns.get_loc("selic_para_soma")] = 1.0
    df_historico["Selic Acumulada"] = df_historico["selic_para_soma"].cumsum()

    linha_mes_atual = pd.DataFrame(
        [{"data": primeiro_dia_mes_atual, "Selic Acumulada": 0.00}]
    )

    df_final = pd.concat([linha_mes_atual, df_historico], ignore_index=True)
    df_final.rename(columns={"data": "Mês/Ano"}, inplace=True)

    logging.info("Cálculo final (padrão Receita Federal) concluído com sucesso.")
    return df_final[["Mês/Ano", "Selic Acumulada"]]
