import pandas as pd
import logging
from pathlib import Path
from typing import List
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from config.constants import ExcelFormats


def update_all_worksheets(target_folder: Path, selic_df: pd.DataFrame, sheet_name: str) -> None:
    logging.info(f"Looking for spreadsheets in: '{target_folder}'")

    files: List[Path] = list(target_folder.glob("*.xlsx")) + list(target_folder.glob("*.xlsm"))

    if not files:
        logging.warning("No .xlsx or .xlsm files found in the folder.")
        return

    logging.info(f"Found {len(files)} files. Starting update...")

    for file_path in files:
        try:
            keep_vba: bool = file_path.suffix.lower() == ".xlsm"
            book = load_workbook(file_path, keep_vba=keep_vba)
            logging.info(f"Processing '{file_path.name}'...")

            if sheet_name in book.sheetnames:
                book.remove(book[sheet_name])

            new_sheet = book.create_sheet(sheet_name)
            rows = dataframe_to_rows(selic_df, index=False, header=True)

            for r_idx, row in enumerate(rows, 1):
                for c_idx, value in enumerate(row, 1):
                    new_sheet.cell(row=r_idx + 2, column=c_idx + 1, value=value)

            for row_idx in range(4, new_sheet.max_row + 1):
                new_sheet.cell(row=row_idx, column=2).number_format = ExcelFormats.DATE
                new_sheet.cell(row=row_idx, column=3).number_format = ExcelFormats.NUMBER

            book.save(file_path)
            logging.info(f"File '{file_path.name}' updated successfully.")

        except Exception as e:
            logging.error(f"FAILED to process the file '{file_path.name}': {e}")
