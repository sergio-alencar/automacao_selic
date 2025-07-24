# AutomacaoSelic/find_ids.py

from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/drive"]
PATH_CREDENTIALS = "credentials.json"


def get_drive_service():
    creds = Credentials.from_service_account_file(PATH_CREDENTIALS, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service


def find_id_path(service, path):
    current_id = "root"
    path_parts = [part for part in path.split("/") if part]

    try:
        drive_name = path_parts[0]
        drives = service.drives().list(q=f"name='{drive_name}'").execute()
        if not drives["drives"]:
            print(f"ERRO: Drive compartilhado '{drive_name}' não encontrado.")
            return None
        current_id = drives["drives"][0]["id"]
        print(f"Encontrado drive compartilhado '{drive_name}' com ID: {current_id}")

        for part in path_parts[1:]:
            query = f"'{current_id}' in parents and name='{part}' and mimeType='application/vnd.google-apps.folder'"
            results = (
                service.files()
                .list(
                    q=query,
                    corpora="drive",
                    driveId=current_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="files(id, name)",
                )
                .execute()
            )
            items = results.get("files", [])
            if not items:
                print(
                    f"ERRO: Pasta '{part}' não encontrada dentro de '{'/'.join(path_parts[:path_parts.index(part)])}'"
                )
                return None
            current_id = items[0]["id"]
            print(f"    → Encontrada subpasta '{part}' com ID: {current_id}")

        return current_id

    except HttpError as error:
        print(f"Ocorreu um erro: {error}")
        return None


if __name__ == "__main__":
    service = get_drive_service()
    print("--- Buscador de IDs de pastas do Google Drive ---")
    print("Copie o caminho completo da pasta a partir do nome do drive compartilhado.")
    print(
        "Exemplo: Contabil/CLIENTES/RCT/EM COMPENSACAO/0-CONTROLES DE COMPENSACOES/CONTROLES PADRONIZADOS"
    )
    path_input = input("Cole o caminho da pasta aqui e pressione Enter: ")

    folder_id = find_id_path(service, path_input)

    if folder_id:
        print("\n================================================")
        print(f"O ID final da pasta é: {folder_id}")
        print("Copie esse ID para o seu arquivo config.py.")
        print("==================================================")
