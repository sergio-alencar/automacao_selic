import logging
import pandas as pd
from pathlib import Path
from typing import List, Optional
from config import settings
from config.constants import SelicCols

EXCEL_EXTENSION_PATTERN: str = "*.xls*"
HEADER_SKIP_ROWS: int = 2
TARGET_COLUMNS: str = "B:C"
COMPARISON_DECIMALS: int = 6


def _get_latest_backup_folder(base_path: Path) -> Optional[Path]:
    if not base_path.exists():
        return None

    backup_folders: List[Path] = sorted(
        [p for p in base_path.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return backup_folders[0] if backup_folders else None


def _get_reference_excel_file(folder_path: Path) -> Optional[Path]:
    return next(folder_path.glob(EXCEL_EXTENSION_PATTERN), None)


def _load_old_selic_data(file_path: Path) -> pd.DataFrame:
    old_selic_df: pd.DataFrame = pd.read_excel(
        file_path,
        sheet_name=settings.SELIC_SHEET_NAME,
        skiprows=HEADER_SKIP_ROWS,
        usecols=TARGET_COLUMNS,
    )

    old_selic_df.columns = [SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]
    old_selic_df[SelicCols.MONTH_YEAR] = pd.to_datetime(old_selic_df[SelicCols.MONTH_YEAR])

    return old_selic_df


def _has_data_changed(new_df: pd.DataFrame, old_df: pd.DataFrame) -> bool:
    new_compare = new_df.copy()
    new_compare.columns = [SelicCols.MONTH_YEAR, SelicCols.ACCUMULATED]

    is_identical = new_compare.round(COMPARISON_DECIMALS).equals(old_df.round(COMPARISON_DECIMALS))

    if is_identical:
        logging.warning("CHECK: No updates found in the Selic data.")
        return False

    logging.info("CHECK: New Selic data found. The update will proceed.")
    return True


def has_selic_updated(new_selic_df: pd.DataFrame) -> bool:
    try:
        latest_backup_path = _get_latest_backup_folder(settings.LOCAL_BACKUP_PATH)

        if not latest_backup_path:
            logging.info("No previous backup foind. Proceeding with the first execution.")
            return True

        logging.info(f"Checking for updates against the latest backup: {latest_backup_path.name}")

        first_old_file = _get_reference_excel_file(latest_backup_path)

        if not first_old_file:
            logging.warning("Latest backup folder is empty. Assuming an update is required.")
            return True

        olf_selic_df = _load_old_selic_data(first_old_file)

        return _has_data_changed(new_selic_df, olf_selic_df)

    except Exception as e:
        logging.error(f"Error checking for updates: {e}. Proceeding with update for safety.")
        return True
