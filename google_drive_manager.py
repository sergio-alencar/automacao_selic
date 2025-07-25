# AutomacaoSelic/google_drive_manager.py

import logging
import io
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service(path_credentials):
    creds = Credentials.from_service_account_file(path_credentials, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def list_files(service, parent_folder_id, shared_drive_id):
    try:
        all_files = []
        page_token = None
        query = f"'{parent_folder_id}' in parents and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/vnd.ms-excel.sheet.macroEnabled.12')"

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
                    pageSize=1000,
                    pageToken=page_token,
                )
                .execute()
            )

            items = results.get("files", [])
            all_files.extend(items)

            page_token = results.get("nextPageToken", None)
            if page_token is None:
                break

        logging.info(
            f"Encontrados {len(all_files)} arquivos na pasta de origem do Google Drive."
        )
        return all_files

    except Exception as e:
        logging.error(
            f"Falha ao listar arquivos da pasta de origem do Google Drive: {e}"
        )
        return []


def download_file(service, file_id, local_path):
    try:
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        with open(local_path, "wb") as f:
            f.write(fh.getvalue())
        logging.info(f"Arquivo '{local_path.name}' baixado com sucesso.")
        return True

    except Exception as e:
        logging.error(f"Falha ao baixar o arquivo ID {file_id}: {e}")
        return False
