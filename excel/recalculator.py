import logging
import xlwings as xw  # type: ignore
from pathlib import Path
from typing import List, Any, Tuple
from excel.utils import get_excel_files

EXCEL_APP_VISIBLE: bool = False


def _process_single_workbook(
    app: Any,
    file_path: Path,
    current_index: int,
    total_files: int,
) -> None:
    try:
        logging.info(f"Processing file {current_index}/{total_files}: {file_path.name}")
        wb = app.books.open(file_path)
        wb.save()
        wb.close()

    except Exception as e:
        logging.error(f"Failed to recalculate file '{file_path.name}': {e}")


def recalculate_and_save_files(target_files: List[Path]) -> None:
    logging.info("--- STARTING FINAL STAGE: FORMULA RECALCULATION ---")

    total_files: int = len(target_files)

    if total_files == 0:
        logging.warning("No Excel files provided for recalculation.")
        return

    logging.info(f"Found {total_files} files to force recalculation.")

    with xw.App(visible=EXCEL_APP_VISIBLE) as app:
        for index, file_path in enumerate(target_files, 1):
            _process_single_workbook(
                app=app,
                file_path=file_path,
                current_index=index,
                total_files=total_files,
            )

    logging.info("--- FORMULA RECALCULATION STAGE COMPLETED ---")
