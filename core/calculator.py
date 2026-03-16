import pandas as pd
import logging
from datetime import datetime
from config.constants import SelicCols, DateFormats


def calculate_accumulated_selic(raw_df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Calculating real monthly rate via compound interest...")

    raw_df[SelicCols.RAW_VALUE] = pd.to_numeric(raw_df[SelicCols.RAW_VALUE])
    raw_df[SelicCols.RAW_DATE] = pd.to_datetime(
        raw_df[SelicCols.RAW_DATE], format=DateFormats.API_AND_PANDAS
    )
    raw_df[SelicCols.DAILY_FACTOR] = 1 + (raw_df[SelicCols.RAW_VALUE] / 100)

    monthly_factors: pd.DataFrame = (
        raw_df.groupby(pd.Grouper(key=SelicCols.RAW_DATE, freq="MS"))[SelicCols.DAILY_FACTOR]
        .prod()
        .reset_index()
    )
    monthly_factors[SelicCols.REAL_MONTHLY] = (
        (monthly_factors[SelicCols.DAILY_FACTOR] - 1) * 100
    ).round(2)

    monthly_df: pd.DataFrame = monthly_factors[[SelicCols.RAW_DATE, SelicCols.REAL_MONTHLY]]

    logging.info("Applying business rule (previous month = 1%)...")
    today: datetime = datetime.now()
    first_day_current_month: datetime = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    historical_df: pd.DataFrame = monthly_df[
        monthly_df[SelicCols.RAW_DATE] < first_day_current_month
    ].copy()
    historical_df.sort_values(by=SelicCols.RAW_DATE, ascending=False, inplace=True)
    historical_df[SelicCols.FOR_SUM] = historical_df[SelicCols.REAL_MONTHLY].shift(1)

    historical_df.iloc[0, historical_df.columns.get_loc(SelicCols.FOR_SUM)] = 1.0
    historical_df[SelicCols.ACCUMULATED] = historical_df[SelicCols.FOR_SUM].cumsum()

    current_month_row: pd.DataFrame = pd.DataFrame(
        [
            {
                SelicCols.RAW_DATE: first_day_current_month,
                SelicCols.ACCUMULATED: 0.00,
            }
        ]
    )
    final_df: pd.DataFrame = pd.concat([current_month_row, historical_df], ignore_index=True)

    final_df[SelicCols.ACCUMULATED] = final_df[SelicCols.ACCUMULATED] / 100
    final_df.rename(columns={SelicCols.RAW_DATE: SelicCols.MONTH_YEAR}, inplace=True)

    logging.info("Final calculation completed successfully.")
    return final_df[[SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]]
