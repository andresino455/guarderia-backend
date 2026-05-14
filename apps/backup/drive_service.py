import os
import io
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS_FILE,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)

def get_or_create_folder(service):
    """Obtiene o crea la carpeta de backups en Drive."""
    folder_name = settings.GOOGLE_DRIVE_FOLDER_NAME

    query = (
        f"name='{folder_name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    # Crear la carpeta si no existe
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]

def subir_backup(contenido_bytes, nombre_archivo):
    """Sube el backup a Google Drive y retorna el file_id y link."""
    service = get_drive_service()
    folder_id = get_or_create_folder(service)

    file_metadata = {
        "name": nombre_archivo,
        "parents": [folder_id],
    }
    media = MediaIoBaseUpload(
        io.BytesIO(contenido_bytes),
        mimetype="application/octet-stream",
        resumable=True,
    )
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink, name, createdTime, size",
    ).execute()

    return file

def listar_backups():
    """Lista todos los backups en la carpeta de Drive."""
    service = get_drive_service()
    folder_id = get_or_create_folder(service)

    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, createdTime, size, webViewLink)",
        orderBy="createdTime desc",
    ).execute()

    return results.get("files", [])

def descargar_backup(file_id):
    """Descarga un backup de Drive y retorna los bytes."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer.read()

def eliminar_backup(file_id):
    """Elimina un backup de Drive."""
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()