import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from config.constants import APIConfig, DateFormats

PARAM_FORMAT_KEY: str = "formato"
PARAM_FORMAT_VAL: str = "json"
PARAM_START_DATE: str = "dataInicial"
PARAM_END_DATE: str = "dataFinal"


def _generate_date_batches(start_date: datetime, end_date: datetime) -> List[Tuple[str, str]]:
    date_periods: pd.DatetimeIndex = pd.date_range(
        start=start_date,
        end=end_date,
        freq=APIConfig.BATCH_FREQ,
    )

    batches: List[Tuple[str, str]] = []

    for i, period_start in enumerate(date_periods):
        if i + 1 < len(date_periods):
            period_end: pd.Timestamp = date_periods[i + 1] - pd.Timedelta(days=1)
        else:
            period_end = pd.Timestamp(end_date)

        start_str: str = period_start.strftime(DateFormats.API)
        end_str: str = period_end.strftime(DateFormats.API)
        batches.append((start_str, end_str))

    return batches


def _fetch_batch(start_str: str, end_str: str) -> Optional[List[Dict[str, Any]]]:
    params: Dict[str, str] = {
        PARAM_FORMAT_KEY: PARAM_FORMAT_VAL,
        PARAM_START_DATE: start_str,
        PARAM_END_DATE: end_str,
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

    start_date: datetime = pd.to_datetime(APIConfig.START_DATE).to_pydatetime()
    end_date: datetime = datetime.now()

    batches: List[Tuple[str, str]] = _generate_date_batches(start_date, end_date)
    all_dataframes: List[pd.DataFrame] = []

    for start_str, end_str in batches:
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
