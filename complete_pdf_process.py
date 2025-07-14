#!/usr/bin/env python3
"""
Script para completar el proceso de la tesis 2030758
- Actualizar ID en la base de datos
- Subir PDF a Google Drive
- Generar enlace web
"""

import sys
import os
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.models import get_session, Tesis
from src.storage.google_drive import GoogleDriveManager
from src.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_tesis_process():
    """Completar el proceso de la tesis 2030758"""
    
    logger.info("🔄 Completando proceso de tesis 2030758...")
    
    # 1. Verificar que el PDF existe
    pdf_path = "data/pdfs/tesis_2030758.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF no encontrado: {pdf_path}")
        return False
    
    logger.info(f"✅ PDF encontrado: {pdf_path}")
    logger.info(f"📏 Tamaño: {os.path.getsize(pdf_path)} bytes")
    
    # 2. Buscar la tesis en la base de datos
    session = get_session()
    try:
        # Buscar por ID incorrecto primero
        tesis = session.query(Tesis).filter_by(scjn_id="tesis_1").first()
        
        if not tesis:
            logger.error("❌ Tesis no encontrada en la base de datos")
            return False
        
        logger.info(f"✅ Tesis encontrada: {tesis.titulo}")
        
        # 3. Actualizar con el ID correcto
        tesis.scjn_id = "2030758"
        tesis.pdf_url = "https://sjf2.scjn.gob.mx/detalle/tesis/2030758"
        
        logger.info("✅ ID actualizado en la base de datos")
        
        # 4. Subir PDF a Google Drive
        logger.info("📤 Subiendo PDF a Google Drive...")
        drive_manager = GoogleDriveManager()
        
        try:
            result = drive_manager.upload_file(pdf_path, "tesis_2030758.pdf")
            if result:
                file_id, web_link = result
                tesis.google_drive_id = file_id
                tesis.google_drive_link = web_link
                
                logger.info(f"✅ PDF subido a Google Drive")
                logger.info(f"🔗 Enlace: {web_link}")
                logger.info(f"🆔 File ID: {file_id}")
            else:
                logger.error("❌ Error subiendo PDF a Google Drive")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error con Google Drive: {e}")
            return False
        
        # 5. Guardar cambios en la base de datos
        session.commit()
        logger.info("✅ Cambios guardados en la base de datos")
        
        # 6. Verificar resultado final
        session.refresh(tesis)
        logger.info("📊 ESTADO FINAL DE LA TESIS:")
        logger.info(f"   ID: {tesis.scjn_id}")
        logger.info(f"   Título: {tesis.titulo}")
        logger.info(f"   PDF URL: {tesis.pdf_url}")
        logger.info(f"   Google Drive ID: {tesis.google_drive_id}")
        logger.info(f"   Google Drive Link: {tesis.google_drive_link}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando tesis: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_google_drive_config():
    """Verificar configuración de Google Drive"""
    logger.info("🔍 Verificando configuración de Google Drive...")
    
    if not Config.GOOGLE_DRIVE_ENABLED:
        logger.error("❌ Google Drive no está habilitado en la configuración")
        return False
    
    if not Config.GOOGLE_DRIVE_FOLDER_ID:
        logger.error("❌ No hay folder ID configurado para Google Drive")
        return False
    
    logger.info("✅ Configuración de Google Drive válida")
    return True

def main():
    """Función principal"""
    logger.info("🚀 INICIANDO COMPLETADO DE PROCESO DE TESIS")
    logger.info("="*50)
    
    # Verificar configuración
    if not verify_google_drive_config():
        logger.error("❌ Configuración de Google Drive inválida")
        return
    
    # Completar proceso
    success = complete_tesis_process()
    
    if success:
        logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("✅ PDF descargado y subido a Google Drive")
        logger.info("✅ Base de datos actualizada")
        logger.info("✅ Enlace web generado")
    else:
        logger.error("❌ ERROR EN EL PROCESO")

if __name__ == "__main__":
    main() 