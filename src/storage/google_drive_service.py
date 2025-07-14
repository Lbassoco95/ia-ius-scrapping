import os
import logging
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pathlib import Path

from src.config import Config

logger = logging.getLogger(__name__)

class GoogleDriveServiceManager:
    """Gestor de Google Drive usando cuenta de servicio para automatización completa"""
    
    # Scope para acceso a archivos
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.service = None
        self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        self.service_account_path = Config.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH
        
    def authenticate(self):
        """Autenticar con Google Drive API usando cuenta de servicio"""
        try:
            if not os.path.exists(self.service_account_path):
                raise FileNotFoundError(f"Archivo de cuenta de servicio no encontrado: {self.service_account_path}")
            
            # Crear credenciales desde archivo de cuenta de servicio
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path, 
                scopes=self.SCOPES
            )
            
            # Construir servicio
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Autenticación con Google Drive (cuenta de servicio) exitosa")
            
        except Exception as e:
            logger.error(f"Error en autenticación con Google Drive: {e}")
            raise
    
    def upload_file(self, file_path: str, filename: str = None) -> Optional[str]:
        """Subir archivo a Google Drive"""
        try:
            if not self.service:
                self.authenticate()
            
            if not os.path.exists(file_path):
                logger.warning(f"Archivo no encontrado: {file_path}")
                return None
            
            if not filename:
                filename = os.path.basename(file_path)
            
            # Metadatos del archivo
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Crear objeto de media
            media = MediaFileUpload(file_path, resumable=True)
            
            # Subir archivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            file_name = file.get('name')
            web_link = file.get('webViewLink')
            
            logger.info(f"Archivo subido exitosamente: {file_name} (ID: {file_id})")
            logger.info(f"Enlace de acceso: {web_link}")
            
            return file_id
            
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
    
    def upload_batch(self, file_paths: List[str], prefix: str = "") -> List[Optional[str]]:
        """Subir múltiples archivos en lote"""
        results = []
        
        for file_path in file_paths:
            try:
                if prefix:
                    filename = f"{prefix}_{os.path.basename(file_path)}"
                else:
                    filename = None
                
                file_id = self.upload_file(file_path, filename)
                results.append(file_id)
                
            except Exception as e:
                logger.error(f"Error en lote subiendo {file_path}: {e}")
                results.append(None)
        
        successful_uploads = len([r for r in results if r is not None])
        logger.info(f"Lote completado: {successful_uploads}/{len(file_paths)} archivos subidos exitosamente")
        
        return results
    
    def list_files(self, query: str = None) -> List[dict]:
        """Listar archivos en la carpeta"""
        try:
            if not self.service:
                self.authenticate()
            
            # Construir query
            if not query:
                if self.folder_id:
                    query = f"'{self.folder_id}' in parents"
                else:
                    query = "trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, createdTime, size, webViewLink)"
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
        """Crear carpeta en Google Drive"""
        try:
            if not self.service:
                self.authenticate()
            
            if not parent_id:
                parent_id = self.folder_id
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id] if parent_id else []
            }
            
            file = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()
            
            folder_id = file.get('id')
            folder_name = file.get('name')
            logger.info(f"Carpeta creada: {folder_name} (ID: {folder_id})")
            
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creando carpeta {folder_name}: {e}")
            return None
    
    def search_files(self, query: str) -> List[dict]:
        """Buscar archivos por nombre o contenido"""
        try:
            if not self.service:
                self.authenticate()
            
            # Buscar en la carpeta específica si está configurada
            if self.folder_id:
                search_query = f"'{self.folder_id}' in parents and (name contains '{query}' or fullText contains '{query}')"
            else:
                search_query = f"name contains '{query}' or fullText contains '{query}'"
            
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
    
    def check_quota(self) -> Optional[dict]:
        """Verificar cuota de Google Drive"""
        try:
            if not self.service:
                self.authenticate()
            
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get('storageQuota', {})
            
            return {
                'limit': quota.get('limit'),
                'usage': quota.get('usage'),
                'usage_in_drive': quota.get('usageInDrive'),
                'usage_in_drive_trash': quota.get('usageInDriveTrash')
            }
            
        except Exception as e:
            logger.error(f"Error verificando cuota: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Probar conexión con Google Drive"""
        try:
            if not self.service:
                self.authenticate()
            
            # Intentar listar archivos para probar conexión
            self.service.files().list(pageSize=1).execute()
            logger.info("✅ Conexión con Google Drive exitosa")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión con Google Drive: {e}")
            return False 