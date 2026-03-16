import logging
import os
import pandas as pd
from pathlib import Path
from typing import List, Optional
from config import settings
from config.constants import SelicCols


def has_selic_updated(new_selic_df: pd.DataFrame) -> bool:
    try:
        backup_folders: List[Path] = sorted(
            [p for p in settings.LOCAL_BACKUP_PATH.iterdir() if p.is_dir()],
            key=os.path.getmtime,
            reverse=True,
        )

        if not backup_folders:
            logging.info("No previous backup found. Proceeding with the first execution.")
            return True

        latest_backup_path: Path = backup_folders[0]
        logging.info(f"Checking for updates against the latest backup: {latest_backup_path.name}")

        first_old_file: Optional[Path] = next(latest_backup_path.glob("*.xls*"), None)

        if not first_old_file:
            logging.warning("Latest backup folder is empty. Assuming an update is required.")
            return True

        old_selic_df: pd.DataFrame = pd.read_excel(
            first_old_file,
            sheet_name=settings.SELIC_SHEET_NAME,
            skiprows=2,
            usecols="B:C",
        )
        old_selic_df.columns = [SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]
        new_selic_df.columns = [SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]

        old_selic_df[SelicCols.MONTH_YEAR] = pd.to_datetime(old_selic_df[SelicCols.MONTH_YEAR])

        if new_selic_df.round(6).equals(old_selic_df.round(6)):
            logging.warning("CHECK: No updates found in the Selic data.")
            return False

        logging.info("CHECK: New Selic data found. The update will proceed.")
        return True

    except Exception as e:
        logging.error(f"Error checking for updates: {e}. Proceeding with update for safety.")
        return True
