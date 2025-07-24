# AutomacaoSelic/find_ids.py

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/drive"]
PATH_CREDENTIALS = "credentials.json"


def get_drive_service():
    creds = Credentials.from_service_account_file(PATH_CREDENTIALS, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def find_ids(service, shared_drive_name, folder_path):
    try:
        drives = service.drives().list(q=f"name='{shared_drive_name}'").execute()
        if not drives["drives"]:
            print(f"ERRO: Drive compartilhado '{shared_drive_name}' não encontrado.")
            return None, None
        shared_drive_id = drives["drives"][0]["id"]
        print(
            f"Encontrado drive compartilhado '{shared_drive_name}' com ID: {shared_drive_id}"
        )

        current_id = shared_drive_id
        path_parts = [part for part in folder_path.split("/") if part]

        for part in path_parts:
            query = f"'{current_id}' in parents and name='{part}' and mimeType='application/vnd.google-apps.folder'"
            results = (
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
            items = results.get("files", [])
            if not items:
                print(f"ERRO: Pasta '{part}' não encontrada.")
                return shared_drive_id, None
            current_id = items[0]["id"]
            print(f"    → Encontrada subpasta '{part}' com ID: {current_id}")

        return shared_drive_id, current_id

    except Exception as error:
        print(f"Ocorreu um erro: {error}")
        return None, None


if __name__ == "__main__":
    service = get_drive_service()
    print("\n--- Buscador de IDs de pastas do Google Drive ---")
    drive_name_input = input(
        "1. Digite o nome EXATO do seu Drive Compartilhado (Ex: Contabil) e pressione Enter: "
    )
    folder_path_input = input(
        f"2. Digite o caminho das subpastas DENTRO de '{drive_name_input}' (Ex: CLIENTES/RCT/...) e pressione Enter: "
    )

    drive_id, folder_id = find_ids(service, drive_name_input, folder_path_input)

    if folder_id:
        print("\n================================================")
        print("IDs encontrados com sucesso! Copie-os para o seu arquivo config.py")
        print(f"FOLDER_ID_ORIGINAL = '{folder_id}'")
        print("==================================================")
