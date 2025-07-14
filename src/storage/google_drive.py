import os
import logging
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from src.config import Config

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Gestor para operaciones con Google Drive"""
    
    # Scope para acceso a archivos
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        
    def authenticate(self):
        """Autenticar con Google Drive API usando cuenta de servicio"""
        try:
            # Usar cuenta de servicio si está configurada
            if hasattr(Config, 'GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH') and Config.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH:
                service_account_path = Config.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH
                if os.path.exists(service_account_path):
                    from google.oauth2 import service_account
                    self.creds = service_account.Credentials.from_service_account_file(
                        service_account_path, scopes=self.SCOPES)
                    logger.info("Autenticación con cuenta de servicio exitosa")
                else:
                    logger.error(f"Archivo de cuenta de servicio no encontrado: {service_account_path}")
                    raise FileNotFoundError(f"Archivo de cuenta de servicio no encontrado: {service_account_path}")
            else:
                # Fallback a autenticación de usuario (código original)
                token_path = 'credentials/token.json'
                
                if os.path.exists(token_path):
                    self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                
                # Si no hay credenciales válidas, solicitar autorización
                if not self.creds or not self.creds.valid:
                    if self.creds and self.creds.expired and self.creds.refresh_token:
                        self.creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            Config.GOOGLE_DRIVE_CREDENTIALS_PATH, self.SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    
                    # Guardar credenciales para la próxima ejecución
                    os.makedirs('credentials', exist_ok=True)
                    with open(token_path, 'w') as token:
                        token.write(self.creds.to_json())
            
            # Construir servicio
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("✅ Autenticación con Google Drive exitosa")
            
        except Exception as e:
            logger.error(f"❌ Error en autenticación con Google Drive: {e}")
            raise
    
    def upload_file(self, file_path: str, filename: str = None, parent_id: str = None) -> Optional[tuple]:
        """Subir archivo a Google Drive y devolver (id, enlace web)"""
        try:
            if not self.service:
                self.authenticate()
            if not filename:
                filename = os.path.basename(file_path)
            file_metadata = {
                'name': filename
            }
            # Usar parent_id si se especifica, sino usar el folder_id por defecto
            if parent_id:
                file_metadata['parents'] = [parent_id]
                logger.info(f"Subiendo archivo a carpeta destino (parent_id): {parent_id}")
            elif self.folder_id:
                file_metadata['parents'] = [self.folder_id]
                logger.info(f"Subiendo archivo a carpeta raíz de unidad compartida (folder_id): {self.folder_id}")
            else:
                logger.error("No se especificó carpeta destino para el archivo.")
                return None
            media = MediaFileUpload(file_path, resumable=True)
            extra_args = {}
            # Soporte para unidades compartidas SOLO supportsAllDrives en create
            if self.folder_id and self.folder_id.startswith('0AA'):
                extra_args['supportsAllDrives'] = True
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink',
                **extra_args
            ).execute()
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            logger.info(f"Archivo subido exitosamente: {filename} (ID: {file_id})")
            logger.info(f"Enlace de acceso: {web_link}")
            return (file_id, web_link)
        except HttpError as e:
            logger.error(f"Error HTTP subiendo archivo {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error subiendo archivo {file_path}: {e}")
            return None
    
    def upload_pdf(self, pdf_path: str, tesis_id: str) -> Optional[str]:
        """Subir PDF específico de tesis"""
        try:
            if not os.path.exists(pdf_path):
                logger.warning(f"Archivo PDF no encontrado: {pdf_path}")
                return None
            
            # Crear nombre descriptivo
            filename = f"tesis_{tesis_id}_{os.path.basename(pdf_path)}"
            
            return self.upload_file(pdf_path, filename)
            
        except Exception as e:
            logger.error(f"Error subiendo PDF {pdf_path}: {e}")
            return None
    
    def list_files(self, query: str = None) -> List[dict]:
        """Listar archivos en la carpeta"""
        try:
            if not self.service:
                self.authenticate()
            
            # Construir query
            if not query:
                query = f"'{self.folder_id}' in parents"
            
            extra_args = {}
            # Soporte para unidades compartidas: supportsAllDrives y driveId en list
            if self.folder_id and self.folder_id.startswith('0AA'):
                extra_args['supportsAllDrives'] = True
                extra_args['driveId'] = self.folder_id
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, createdTime, size)",
                **extra_args
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Encontrados {len(files)} archivos")
            
            return files
            
        except Exception as e:
            logger.error(f"Error listando archivos: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo de Google Drive"""
        try:
            if not self.service:
                self.authenticate()
            
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Archivo eliminado: {file_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_id}: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Optional[dict]:
        """Obtener información de un archivo"""
        try:
            if not self.service:
                self.authenticate()
            
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, createdTime, modifiedTime, size, webViewLink"
            ).execute()
            
            return file
            
        except Exception as e:
            logger.error(f"Error obteniendo información del archivo {file_id}: {e}")
            return None
    
    def create_folder(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """Crear carpeta en Google Drive (soporta unidades compartidas)"""
        try:
            if not self.service:
                self.authenticate()
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            extra_args = {}
            # Soporte para unidades compartidas SOLO supportsAllDrives en create
            if self.folder_id and self.folder_id.startswith('0AA'):
                extra_args['supportsAllDrives'] = True
            file = self.service.files().create(
                body=file_metadata,
                fields='id',
                **extra_args
            ).execute()
            folder_id = file.get('id')
            logger.info(f"✅ Carpeta creada: {folder_name} (ID: {folder_id})")
            return folder_id
        except Exception as e:
            logger.error(f"❌ Error creando carpeta {folder_name}: {e}")
            return None
    
    def search_files(self, query: str) -> List[dict]:
        """Buscar archivos por nombre o contenido"""
        try:
            if not self.service:
                self.authenticate()
            
            # Buscar en la carpeta específica
            search_query = f"'{self.folder_id}' in parents and (name contains '{query}' or fullText contains '{query}')"
            
            results = self.service.files().list(
                q=search_query,
                pageSize=50,
                fields="nextPageToken, files(id, name, createdTime, size, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Búsqueda '{query}' encontró {len(files)} archivos")
            
            return files
            
        except Exception as e:
            logger.error(f"Error buscando archivos: {e}")
            return [] 