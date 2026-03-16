from urllib import response

from click import Option
import pandas as pd
import requests
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.constants import APIConfig, DateFormats


def _fetch_batch(start_str: str, end_str) -> Optional[List[Dict[str, Any]]]:
    params: Dict[str, str] = {
        "formato": "json",
        "dataInicial": start_str,
        "dataFinal": end_str,
    }

    try:
        response: requests.Response = requests.get(
            APIConfig.SELIC_SGS_URL,
            params=params,
            headers=APIConfig.HEADERS,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"FAILED to fetch batch {start_str}-{end_str}: {e}")
        return None


def fetch_raw_selic_data() -> Optional[pd.DataFrame]:
    logging.info("Starting daily Selic data fetch in batches...")

    start_date: pd.Timestamp = pd.to_datetime(APIConfig.START_DATE)
    end_date: datetime = datetime.now()
    date_periods: pd.DatetimeIndex = pd.date_range(
        start=start_date,
        end=end_date,
        freq=APIConfig.BATCH_FREQ,
    )

    all_dataframes: List[pd.DataFrame] = []

    for i, period_start in enumerate(date_periods):
        if i + 1 < len(date_periods):
            period_end: pd.Timestamp = date_periods[i + 1] - pd.Timedelta(days=1)
        else:
            period_end = pd.Timestamp(end_date)

        start_str: str = period_start.strftime(DateFormats.API_AND_PANDAS)
        end_str: str = period_end.strftime(DateFormats.API_AND_PANDAS)

        logging.info(f"Fetching data batch: {start_str} to {end_str}...")

        batch_data: Optional[List[Dict[str, Any]]] = _fetch_batch(start_str, end_str)

        if batch_data is None:
            return None

        if batch_data:
            all_dataframes.append(pd.DataFrame(batch_data))

    if not all_dataframes:
        logging.error("No data was downloaded from the API.")
        return None

    return pd.concat(all_dataframes, ignore_index=True)
