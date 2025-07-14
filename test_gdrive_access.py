#!/usr/bin/env python3
"""
Script para probar acceso a Google Drive y listar unidades compartidas
"""

import sys
import os
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.storage.google_drive import GoogleDriveManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gdrive_access():
    """Probar acceso a Google Drive"""
    
    logger.info("🔍 Probando acceso a Google Drive...")
    
    # Configurar variables de entorno
    os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
    os.environ['GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH'] = 'credentials/service_account.json'
    
    try:
        # Crear instancia
        drive_manager = GoogleDriveManager()
        
        # Autenticar
        drive_manager.authenticate()
        
        if not drive_manager.service:
            logger.error("❌ No se pudo autenticar con Google Drive")
            return False
        
        logger.info("✅ Autenticación exitosa")
        
        # Listar unidades compartidas
        logger.info("📋 Listando unidades compartidas...")
        
        try:
            # Buscar unidades compartidas
            shared_drives = drive_manager.service.drives().list().execute()
            
            if shared_drives.get('drives'):
                logger.info(f"✅ Encontradas {len(shared_drives['drives'])} unidades compartidas:")
                for drive in shared_drives['drives']:
                    logger.info(f"   📁 {drive['name']} (ID: {drive['id']})")
                    logger.info(f"      Capacidad: {drive.get('capabilities', {}).get('canAddChildren', 'N/A')}")
            else:
                logger.info("❌ No se encontraron unidades compartidas")
                logger.info("💡 Necesitas crear una unidad compartida y dar acceso a la cuenta de servicio")
                
        except Exception as e:
            logger.error(f"❌ Error listando unidades compartidas: {e}")
        
        # Listar archivos en la raíz
        logger.info("📋 Listando archivos en la raíz...")
        
        try:
            files = drive_manager.service.files().list(
                pageSize=10,
                fields="files(id, name, mimeType)"
            ).execute()
            
            if files.get('files'):
                logger.info(f"✅ Encontrados {len(files['files'])} archivos/carpetas:")
                for file in files['files']:
                    file_type = "📁 Carpeta" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄 Archivo"
                    logger.info(f"   {file_type} {file['name']} (ID: {file['id']})")
            else:
                logger.info("❌ No se encontraron archivos")
                
        except Exception as e:
            logger.error(f"❌ Error listando archivos: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        return False

def main():
    """Función principal"""
    success = test_gdrive_access()
    
    if success:
        logger.info("🎉 Prueba de acceso completada")
    else:
        logger.error("❌ Error en la prueba de acceso")

if __name__ == "__main__":
    main() 