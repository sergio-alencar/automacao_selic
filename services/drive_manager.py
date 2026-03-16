import logging
from pathlib import Path
from typing import Any, List, Dict, Optional
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
from config.constants import DriveConfig


def get_drive_service(credentials_path: Path) -> Any:
    creds = Credentials.from_service_account_file(credentials_path, scopes=DriveConfig.SCOPES)
    return build("drive", "v3", credentials=creds)


def list_excel_files(
    service: Any, parent_folder_id: str, shared_drive_id: str
) -> List[Dict[str, str]]:
    try:
        all_files: List[Dict[str, str]] = []
        page_token: Optional[str] = None

        query: str = (
            f"'{parent_folder_id}' in parents and "
            f"(mimeType='{DriveConfig.MIME_XLSX}' or mimeType='{DriveConfig.MIME_XLSM}')"
        )

        while True:
            results = (
                service.files()
                .list(
                    q=query,
                    corpora="drive",
                    driveId=shared_drive_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="nextPageToken, files(id, name)",
                    pageSize=DriveConfig.PAGE_SIZE,
                    pageToken=page_token,
                )
                .execute()
            )

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


def download_file(service: Any, file_id: str, local_path: Path) -> bool:
    try:
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

        with open(local_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done: bool = False

            while not done:
                status, done = downloader.next_chunk()

        logging.info(f"File '{local_path.name}' downloaded successfully.")
        return True

    except Exception as e:
        logging.error(f"Failed to download file ID {file_id}: {e}")
        return False
