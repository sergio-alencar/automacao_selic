from typing import Any, Tuple, Optional, List, Dict
from googleapiclient.discovery import build  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore
from config import settings
from config.constants import DriveConfig


def get_drive_service() -> Any:
    creds = Credentials.from_service_account_file(
        settings.CREDENTIALS_PATH, scopes=DriveConfig.SCOPES_FULL
    )
    return build("drive", "v3", credentials=creds)


def _get_shared_drive_id(service: Any, shared_drive_name: str) -> Optional[str]:
    drives: Dict[str, Any] = service.drives().list(q=f"name='{shared_drive_name}'").execute()

    if not drives.get("drives"):
        print(f"ERROR: Shared drive '{shared_drive_name}' not found.")
        return None

    drive_id: str = drives["drives"][0]["id"]
    print(f"Found shared drive '{shared_drive_name}' with ID: {drive_id}")
    return drive_id


def _traverse_folder_path(service: Any, shared_drive_id: str, folder_path: str) -> Optional[str]:
    current_id: str = shared_drive_id
    path_parts: List[str] = [part for part in folder_path.split("/") if part]

    for part in path_parts:
        query: str = (
            f"'{current_id}' in parents and name='{part}' and "
            f"mimeType='{DriveConfig.MIME_FOLDER}'"
        )

        results: Dict[str, Any] = (
            service.files()
            .list(
                q=query,
                corpora="drive",
                driveId=shared_drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="files(id, name)",
            )
            .execute()
        )

        items: List[Dict[str, str]] = results.get("files", [])

        if not items:
            print(f"ERROR: Folder '{part}' not found.")
            return None

        current_id = items[0]["id"]
        print(f"    → Found subfolder '{part}' with ID: {current_id}")

    return current_id


def find_folder_ids(
    service: Any, shared_drive_name: str, folder_path: str
) -> Tuple[Optional[str], Optional[str]]:
    try:
        shared_drive_id = _get_shared_drive_id(service, shared_drive_name)
        if not shared_drive_id:
            return None, None

        target_folder_id = _traverse_folder_path(service, shared_drive_id, folder_path)

        return shared_drive_id, target_folder_id

    except Exception as error:
        print(f"An error occurred while communicating with Google Drive API: {error}")
        return None, None


if __name__ == "__main__":
    service: Any = get_drive_service()
    print("\n--- Google Drive Folder ID Finder ---")

    drive_name_input: str = input(
        "1. Enter the EXACT name of your Shared Drive (e.g., Accounting) and press Enter: "
    )
    folder_path_input: str = input(
        f"2. Enter the subfolder path INSIDE '{drive_name_input}' (e.g., CLIENTS/RCT/...) and press Enter: "
    )

    drive_id, folder_id = find_folder_ids(service, drive_name_input, folder_path_input)

    if drive_id and folder_id:
        print("\n" + ("=" * 55))
        print(" SUCCESS! Copy the IDs below to your .env file:")
        print("=" * 55)
        print(f'SHARED_DRIVE_ID="{drive_id}"')
        print(f'ORIGINAL_FOLDER_ID="{folder_id}"')
        print(("=" * 55) + "\n")
