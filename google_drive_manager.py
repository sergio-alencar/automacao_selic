# AutomacaoSelic/google_drive_manager.py

import logging
import io
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service(path_credentials):
    try:
        creds = Credentials.from_service_account_file(path_credentials, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        logging.info("Autenticação com a API do Google Drive bem-sucedida.")
        return service

    except Exception as e:
        logging.error(f"Falha na autenticação com a API do Google Drive: {e}")
        return None


def create_folder(service, name, parent_id):
    try:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = (
            service.files()
            .create(body=file_metadata, fields="id", supportsAllDrives=True)
            .execute()
        )
        logging.info(f"Pasta de backup '{name}' criada com sucesso.")
        return folder.get("id")

    except Exception as e:
        logging.error(f"Falha ao criar pasta de backup '{name}': {e}")
        return None


def list_files(service, folder_id):
    try:
        query = f"'{folder_id}' in parents and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/vnd.ms-excel.sheet.macroEnabled.12')"
        results = (
            service.files()
            .list(
                q=query,
                corpora="drive",
                driveId=folder_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="files(id, name)",
            )
            .execute()
        )
        items = results.get("files", [])
        logging.info(f"Encontrados {len(items)} arquivos na pasta de origem.")
        return items

    except Exception as e:
        logging.error(f"Falha ao listar arquivos da pasta de origem: {e}")
        return []


def download_file(service, file_id, local_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        with open(local_path, "wb") as f:
            f.write(fh.getvalue())
        return True

    except Exception as e:
        logging.error(f"Falha ao baixar o arquivo ID {file_id}: {e}")
        return False


def update_file(service, file_id, local_path, mime_type):
    try:
        media = MediaFileUpload(local_path, mimetype=mime_type)
        service.files().update(
            fileId=file_id, media_body=media, supportsAllDrives=True
        ).execute()
        return True

    except Exception as e:
        logging.error(f"Falha ao fazer upload do arquivo ID {file_id}: {e}")
        return False


def copy_file(service, source_file_id, name, destination_folder_id):
    try:
        file_metadata = {"name": name, "parents": [destination_folder_id]}
        copied_file = (
            service.files()
            .copy(
                fileId=source_file_id,
                body=file_metadata,
                supportsAllDrives=True,
                fields="id",
            )
            .execute()
        )
        return copied_file.get("id")

    except Exception as e:
        logging.error(f"Falha ao copiar o arquivo ID {source_file_id}: {e}")
        return None
