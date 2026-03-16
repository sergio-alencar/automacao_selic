import logging
import xlwings as xw  # type: ignore
from pathlib import Path
from typing import List


def recalculate_and_save_folder(target_folder: Path) -> None:
    logging.info("--- STARTING FINAL STAGE: FORMULA RECALCULATION ---")

    with xw.App(visible=False) as app:
        files: List[Path] = list(target_folder.glob("*.xlsx")) + list(target_folder.glob("*.xlsm"))
        logging.info(f"Found {len(files)} files to force recalculation.")

        for i, file_path in enumerate(files, 1):
            try:
                logging.info(f"Processing file {i}/{len(files)}: {file_path.name}")
                wb = app.books.open(file_path)
                wb.save()
                wb.close()
            except Exception as e:
                logging.error(f"Failed to recalculate file '{file_path.name}': {e}")
                continue

    logging.info("--- FORMULA RECALCULATION STAGE COMPLETED ---")
