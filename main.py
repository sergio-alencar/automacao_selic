import logging
import traceback
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

from config import settings
from config.constants import SystemDefaults
from config.logger import setup_logging
from core import calculator, update_validator
from excel import updater, recalculator
from excel.utils import get_excel_files
from services import bcb_api, drive_manager, email_notifier


def _get_validated_selic_data() -> Optional[pd.DataFrame]:
    raw_selic_data: Optional[pd.DataFrame] = bcb_api.fetch_raw_selic_data()

    if raw_selic_data is None:
        raise Exception("Selic data fetch failed.")

    calculated_selic_df: pd.DataFrame = calculator.calculate_accumulated_selic(raw_selic_data)

    if not update_validator.has_selic_updated(calculated_selic_df.copy()):
        logging.info("Execution stopped as there is no new data. Scheduled for next attempt.")
        return None

    return calculated_selic_df


def _setup_destination_folders() -> Tuple[Path, Path]:
    timestamp_folder: str = datetime.now().strftime("%Y.%m.%d_%H%M%S")
    pure_backup_path: Path = settings.LOCAL_BACKUP_PATH / timestamp_folder
    updated_sheets_path: Path = settings.LOCAL_UPDATED_SHEETS_PATH / timestamp_folder

    pure_backup_path.mkdir(parents=True, exist_ok=True)
    updated_sheets_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Pure backup folder created at: '{pure_backup_path}'")
    logging.info(f"Updated sheets folder created at: '{updated_sheets_path}'")

    return pure_backup_path, updated_sheets_path


def _download_target_files(
    drive_service: Any,
    pure_backup_path: Path,
    updated_sheets_path: Path,
) -> bool:
    drive_files: List[Dict[str, str]] = drive_manager.list_excel_files(
        service=drive_service,
        parent_folder_id=settings.ORIGINAL_FOLDER_ID,
        shared_drive_id=settings.SHARED_DRIVE_ID,
    )

    if not drive_files:
        logging.warning("No files found in the source Drive folder. Finishing.")
        return False

    logging.info(f"Downloading {len(drive_files)} files to destination folders...")

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
    return True


def _handle_critical_error(exception_traceback: str) -> None:
    logging.error("!!! A CRITICAL FAILURE OCCURRED !!!")
    logging.error(exception_traceback)

    subject: str = "ALERTA: Falha na execução da automação Selic"
    body: str = (
        "Um erro crítico ocorreu durante a execução do script de atualização da Selic.\n\n"
        "Verifique o arquivo de log em anexo para mais detalhes.\n\n"
        "==================== MENSAGEM DE ERRO ====================\n"
        f"{exception_traceback}"
    )

    for handler in logging.getLogger().handlers:
        handler.flush()

    email_notifier.send_alert_email(
        subject=subject,
        body=body,
        recipient=settings.ALERT_EMAIL_RECIPIENT,
        config=settings.EMAIL_SETTINGS,
        attachment_path=settings.LOG_FILE_PATH,
    )
    logging.error("=" * 50)


def run() -> None:
    logging.info("=" * 60)
    logging.info("=== STARTING SPREADSHEET UPDATE AUTOMATION ===")
    logging.info("=" * 60)

    calculated_selic_df = _get_validated_selic_data()
    if calculated_selic_df is None:
        return

    drive_service: Any = drive_manager.get_drive_service(settings.CREDENTIALS_PATH)
    if not drive_service:
        raise Exception("Failed to authenticate with Google Drive.")

    pure_backup_path, updated_sheets_path = _setup_destination_folders()

    files_downloaded = _download_target_files(drive_service, pure_backup_path, updated_sheets_path)
    if not files_downloaded:
        return

    target_files = get_excel_files(updated_sheets_path)
    if settings.IS_DEVELOPMENT:
        max_files = SystemDefaults.DEV_MAX_FILES
        logging.warning(
            f"DEV_MODE ACTIVE: Limiting processing to first {max_files} files for speed."
        )
        target_files = target_files[:max_files]

    logging.info("Starting destination spreadsheets update...")

    updater.update_all_worksheets(
        target_files=target_files,
        selic_df=calculated_selic_df,
        sheet_name=settings.SELIC_SHEET_NAME,
    )

    recalculator.recalculate_and_save_files(target_files)

    logging.info("=== EXECUTION COMPLETED SUCCESSFULLY ===")
    logging.info(f"Pure backup saved at: '{pure_backup_path}'")
    logging.info(f"Updated sheets saved at: '{updated_sheets_path}'")


if __name__ == "__main__":
    setup_logging()

    try:
        run()
    except Exception as e:
        _handle_critical_error(traceback.format_exc())
