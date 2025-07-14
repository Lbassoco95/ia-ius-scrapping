#!/usr/bin/env python3
"""
Script para crear una carpeta en Google Drive y obtener su ID
"""

import sys
import os
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.storage.google_drive import GoogleDriveManager
from src.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_gdrive_folder():
    """Crear carpeta en Google Drive y mostrar su ID"""
    
    logger.info("🚀 Creando carpeta en Google Drive...")
    
    # Configurar variables de entorno
    os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
    os.environ['GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH'] = 'credentials/service_account.json'
    
    try:
        # Crear instancia de Google Drive Manager
        drive_manager = GoogleDriveManager()
        
        # Crear carpeta
        folder_name = "Tesis SCJN - Scraping"
        folder_id = drive_manager.create_folder(folder_name)
        
        if folder_id:
            logger.info("✅ Carpeta creada exitosamente")
            logger.info(f"📁 Nombre: {folder_name}")
            logger.info(f"🆔 ID: {folder_id}")
            logger.info("="*50)
            logger.info("📋 CONFIGURACIÓN PARA USAR:")
            logger.info(f"export GOOGLE_DRIVE_FOLDER_ID=\"{folder_id}\"")
            logger.info("="*50)
            
            return folder_id
        else:
            logger.error("❌ Error creando carpeta")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

def list_available_folders():
    """Listar carpetas disponibles en Google Drive"""
    
    logger.info("📋 Listando carpetas disponibles...")
    
    try:
        drive_manager = GoogleDriveManager()
        
        # Listar archivos (incluyendo carpetas)
        files = drive_manager.list_files()
        
        folders = [f for f in files if f.get('mimeType') == 'application/vnd.google-apps.folder']
        
        if folders:
            logger.info(f"✅ Encontradas {len(folders)} carpetas:")
            for folder in folders:
                logger.info(f"   📁 {folder['name']} (ID: {folder['id']})")
        else:
            logger.info("❌ No se encontraron carpetas")
            
        return folders
        
    except Exception as e:
        logger.error(f"❌ Error listando carpetas: {e}")
        return []

def main():
    """Función principal"""
    logger.info("🔍 GESTOR DE CARPETAS DE GOOGLE DRIVE")
    logger.info("="*50)
    
    # Listar carpetas existentes
    existing_folders = list_available_folders()
    
    if existing_folders:
        logger.info("\n💡 Puedes usar una carpeta existente o crear una nueva")
    
    # Crear nueva carpeta
    new_folder_id = create_gdrive_folder()
    
    if new_folder_id:
        logger.info("🎉 ¡Carpeta creada exitosamente!")
        logger.info("Ahora puedes usar este ID en la configuración del scraping")

if __name__ == "__main__":
    main() 