import pandas as pd
import logging
from datetime import datetime
from config.constants import SelicCols, DateFormats

PERCENTAGE_DIVISOR: float = 100.0
PREVIOUS_MONTH_FIXED_RATE: float = 1.0
CURRENT_MONTH_START_RATE: float = 0.00


def _calculate_monthly_real_rate(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df[SelicCols.RAW_VALUE] = pd.to_numeric(df[SelicCols.RAW_VALUE])
    df[SelicCols.RAW_DATE] = pd.to_datetime(df[SelicCols.RAW_DATE], format=DateFormats.PANDAS)
    df[SelicCols.DAILY_FACTOR] = 1 + (df[SelicCols.RAW_VALUE] / PERCENTAGE_DIVISOR)

    monthly_factors: pd.DataFrame = (
        df.groupby(pd.Grouper(key=SelicCols.RAW_DATE, freq="MS"))[SelicCols.DAILY_FACTOR]
        .prod()
        .reset_index()
    )

    monthly_factors[SelicCols.REAL_MONTHLY] = (
        (monthly_factors[SelicCols.DAILY_FACTOR] - 1) * PERCENTAGE_DIVISOR
    ).round(2)

    return monthly_factors[[SelicCols.RAW_DATE, SelicCols.REAL_MONTHLY]]


def _apply_accumulation_rules(monthly_df: pd.DataFrame) -> pd.DataFrame:
    today: datetime = datetime.now()
    first_day_current_month: datetime = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    historical_df: pd.DataFrame = monthly_df[
        monthly_df[SelicCols.RAW_DATE] < first_day_current_month
    ].copy()

    historical_df.sort_values(by=SelicCols.RAW_DATE, ascending=False, inplace=True)
    historical_df[SelicCols.FOR_SUM] = historical_df[SelicCols.REAL_MONTHLY].shift(1)

    if not historical_df.empty:
        first_row_index = historical_df.index[0]
        historical_df.loc[first_row_index, SelicCols.FOR_SUM] = PREVIOUS_MONTH_FIXED_RATE

    historical_df[SelicCols.ACCUMULATED] = historical_df[SelicCols.FOR_SUM].cumsum()

    current_month_row: pd.DataFrame = pd.DataFrame(
        [
            {
                SelicCols.RAW_DATE: first_day_current_month,
                SelicCols.ACCUMULATED: CURRENT_MONTH_START_RATE,
            }
        ]
    )

    return pd.concat([current_month_row, historical_df], ignore_index=True)


def _format_for_export(final_df: pd.DataFrame) -> pd.DataFrame:
    df = final_df.copy()
    df[SelicCols.ACCUMULATED] = df[SelicCols.ACCUMULATED] / PERCENTAGE_DIVISOR
    df.rename(columns={SelicCols.RAW_DATE: SelicCols.MONTH_YEAR}, inplace=True)

    return df[[SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]]


def calculate_accumulated_selic(raw_df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Calculating real monthly rate via compound interest...")
    monthly_df = _calculate_monthly_real_rate(raw_df)

    logging.info("Applying business rule (previous month = 1%)...")
    accumulated_df = _apply_accumulation_rules(monthly_df)

    final_df = _format_for_export(accumulated_df)

    logging.info("Final calculation completed successfully.")
    return final_df
