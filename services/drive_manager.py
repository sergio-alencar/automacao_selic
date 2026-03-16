import logging
from pathlib import Path
from typing import Any, List, Dict, Optional, Final
from googleapiclient.discovery import build  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore
from googleapiclient.http import MediaIoBaseDownload  # type: ignore
from config.constants import DriveConfig

API_SERVICE_NAME: Final[str] = "drive"
API_VERSION: Final[str] = "v3"
DRIVE_CORPORA: Final[str] = "drive"
API_FIELDS_TO_RETURN: Final[str] = "nextPageToken, files(id, name)"
FILE_WRITE_MODE: Final[str] = "wb"


def get_drive_service(credentials_path: Path) -> Any:
    creds = Credentials.from_service_account_file(credentials_path, scopes=DriveConfig.SCOPES)
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def _build_excel_query(parent_folder_id: str) -> str:
    return (
        f"'{parent_folder_id}' in parents and "
        f"(mimeType='{DriveConfig.MIME_XLSX}' or mimeType='{DriveConfig.MIME_XLSM}')"
    )


def _fetch_files_page(
    service: Any, query: str, shared_drive_id: str, page_token: Optional[str]
) -> Dict[str, Any]:
    return (
        service.files()
        .list(
            q=query,
            corpora=DRIVE_CORPORA,
            driveId=shared_drive_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields=API_FIELDS_TO_RETURN,
            pageSize=DriveConfig.PAGE_SIZE,
            pageToken=page_token,
        )
        .execute()
    )


def list_excel_files(
    service: Any,
    parent_folder_id: str,
    shared_drive_id: str,
) -> List[Dict[str, str]]:
    try:
        all_files: List[Dict[str, str]] = []
        page_token: Optional[str] = None
        query: str = _build_excel_query(parent_folder_id)

        while True:
            results = _fetch_files_page(service, query, shared_drive_id, page_token)

            items: List[Dict[str, str]] = results.get("files", [])
            all_files.extend(items)

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        logging.info(f"Found {len(all_files)} files in the Google Drive source folder.")
        return all_files

    except Exception as e:
        logging.error(f"Failed to list files from Google Drive: {e}")
        return []


def download_file(
    service: Any,
    file_id: str,
    local_path: Path,
) -> bool:
    try:
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

        with open(local_path, FILE_WRITE_MODE) as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done: bool = False

            while not done:
                _, done = downloader.next_chunk()

        logging.info(f"File '{local_path.name}' downloaded successfully.")
        return True

    except Exception as e:
        logging.error(f"Failed to download file ID {file_id}: {e}")
        return False
