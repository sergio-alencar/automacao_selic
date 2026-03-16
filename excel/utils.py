from pathlib import Path
from typing import List
from config.constants import FileExtensions


def get_excel_files(target_folder: Path) -> List[Path]:
    files: List[Path] = []

    for ext in FileExtensions.EXCEL:
        files.extend(target_folder.glob(ext))

    return files
