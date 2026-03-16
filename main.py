import logging
import traceback
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Optional

from config import settings
from config.logger import setup_logging
from services import bcb_api, drive_manager, email_notifier
from core import calculator, update_validator
from excel import updater, recalculator


def run() -> None:
    logging.info("=" * 60)
    logging.info("=== STARTING SPREADSHEET UPDATE AUTOMATION ===")
    logging.info("=" * 60)

    raw_selic_data: Optional[pd.DataFrame] = bcb_api.fetch_raw_selic_data()

    if raw_selic_data is None:
        raise Exception("Selic data fetch failed.")

    calculated_selic_df: pd.DataFrame = calculator.calculate_accumulated_selic(
        raw_selic_data
    )

    if not update_validator.has_selic_updated(calculated_selic_df.copy()):
        logging.info(
            "Execution stopped as there is no new data. Scheduled for next attempt."
        )
        return

    drive_service: Any = drive_manager.get_drive_service(
        settings.CREDENTIALS_PATH
    )

    if not drive_service:
        raise Exception("Failed to authenticate with Google Drive.")

    timestamp_folder: str = datetime.now().strftime("%Y.%m.%d_%H%M%S")
    pure_backup_path: Path = settings.LOCAL_BACKUP_PATH / timestamp_folder
    updated_sheets_path: Path = (
        settings.LOCAL_UPDATED_SHEETS_PATH / timestamp_folder
    )

    pure_backup_path.mkdir(parents=True, exist_ok=True)
    updated_sheets_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Pure backup folder created at: '{pure_backup_path}'")
    logging.info(f"Updated sheets folder created at: '{updated_sheets_path}'")

    drive_files: List[Dict[str, str]] = drive_manager.list_excel_files(
        service=drive_service,
        parent_folder_id=settings.ORIGINAL_FOLDER_ID,
        shared_drive_id=settings.SHARED_DRIVE_ID,
    )

    if not drive_files:
        logging.warning("No files found in the source Drive folder. Finishing.")
        return

    logging.info(
        f"Downloading {len(drive_files)} files to destination folders..."
    )

    for file_info in drive_files:
        drive_manager.download_file(
            service=drive_service,
            file_id=file_info["id"],
            local_path=pure_backup_path / file_info["name"],
        )
        drive_manager.download_file(
            service=drive_service,
            file_id=file_info["id"],
            local_path=updated_sheets_path / file_info["name"],
        )

    logging.info("All files downloaded successfully.")

    logging.info("Starting destination spreadsheets update...")

    updater.update_all_worksheets(
        target_folder=updated_sheets_path,
        selic_df=calculated_selic_df,
        sheet_name=settings.SELIC_SHEET_NAME,
    )

    recalculator.recalculate_and_save_folder(updated_sheets_path)

    logging.info("=== EXECUTION COMPLETED SUCCESSFULLY ===")
    logging.info(f"Pure backup saved at: '{pure_backup_path}'")
    logging.info(f"Updated sheets saved at: '{updated_sheets_path}'")


if __name__ == "__main__":
    setup_logging()

    try:
        run()

    except Exception as e:
        logging.error("!!!!!! A CRITICAL FAILURE OCCURRED !!!!!!")
        logging.error(traceback.format_exc())

        subject: str = (
            "ALERT: Failure in Selic spreadsheet updater robot execution"
        )
        body: str = (
            "A critical error occurred during the Selic update script execution.\n\n"
            "Please check the log file for more details.\n\n"
            "==================== ERROR MESSAGE ====================\n"
            f"{traceback.format_exc()}"
        )

        email_notifier.send_alert_email(
            subject=subject,
            body=body,
            recipient=settings.ALERT_EMAIL_RECIPIENT,
            config=settings.EMAIL_CONFIG,
        )

        logging.error("=" * 50)
