#!/usr/bin/env python3
"""
Script de automatización de Google Drive para VM
Sube PDFs automáticamente durante el scraping
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Cargar variables de entorno desde .env (directorio actual y del script)
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path.cwd() / ".env")
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Depuración: imprimir el valor de la variable antes de configurar el logger
print(f"[DEBUG] GOOGLE_DRIVE_ENABLED={os.getenv('GOOGLE_DRIVE_ENABLED')}")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gdrive_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def upload_pdf_to_drive(pdf_path: str, tesis_id: str):
    """Subir PDF a Google Drive"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        # Configuración
        service_account_path = "credentials/service_account.json"
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
        
        if not os.path.exists(service_account_path):
            logger.error("Archivo de cuenta de servicio no encontrado")
            return None
        
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF no encontrado: {pdf_path}")
            return None
        
        # Crear credenciales
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Construir servicio
        service = build('drive', 'v3', credentials=credentials)
        
        # Preparar archivo
        filename = f"tesis_{tesis_id}_{os.path.basename(pdf_path)}"
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }
        
        # Subir archivo
        media = MediaFileUpload(pdf_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        
        logger.info(f"✅ PDF subido: {filename} (ID: {file_id})")
        logger.info(f"   Enlace: {web_link}")
        
        return file_id
        
    except Exception as e:
        logger.error(f"❌ Error subiendo PDF: {e}")
        return None

def main():
    """Función principal"""
    logger.info("🚀 Iniciando automatización de Google Drive")
    
    # Depuración: mostrar el valor de la variable
    logger.info(f"GOOGLE_DRIVE_ENABLED={os.getenv('GOOGLE_DRIVE_ENABLED')}")
    
    # Verificar configuración
    if not os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true":
        logger.error("Google Drive no está habilitado")
        return False
    
    if not os.getenv("GOOGLE_DRIVE_FOLDER_ID"):
        logger.warning("GOOGLE_DRIVE_FOLDER_ID no configurado")
    
    logger.info("✅ Automatización configurada correctamente")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 