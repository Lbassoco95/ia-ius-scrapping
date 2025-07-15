#!/usr/bin/env python3
"""
SCRAPER DE PRODUCCIÓN - SCJN
Sistema completo con descarga de PDFs y subida a Google Drive
"""

import sys
import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Agregar src al path
sys.path.insert(0, 'src')

def setup_logging():
    """Configurar logging para producción"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/production_scraper_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Función principal del scraper de producción"""
    logger = setup_logging()
    
    logger.info("🚀 INICIANDO SCRAPER DE PRODUCCIÓN")
    logger.info("=" * 60)
    
    try:
        # Importar módulos necesarios
        from src.scraper.main import ScrapingOrchestrator
        from src.database.models import create_tables, get_session, Tesis
        from src.config import Config
        
        # Verificar configuración
        logger.info("📋 Verificando configuración...")
        
        # Crear directorios necesarios
        Path("data/pdfs").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("credentials").mkdir(exist_ok=True)
        
        # Verificar Google Drive
        if Config.GOOGLE_DRIVE_ENABLED:
            logger.info("✅ Google Drive habilitado")
            if not Config.GOOGLE_DRIVE_FOLDER_ID:
                logger.warning("⚠️ GOOGLE_DRIVE_FOLDER_ID no configurado")
        else:
            logger.info("ℹ️ Google Drive deshabilitado")
        
        # Crear tablas de base de datos
        logger.info("🗄️ Configurando base de datos...")
        create_tables()
        
        # Verificar estado de la base de datos
        session = get_session()
        total_tesis = session.query(Tesis).count()
        logger.info(f"📊 Tesis en base de datos: {total_tesis}")
        
        # Inicializar orquestador
        logger.info("🤖 Inicializando orquestador de scraping...")
        orchestrator = ScrapingOrchestrator()
        
        # Configurar parámetros de producción
        max_documents = 50  # Documentos por sesión
        max_hours = 2       # Máximo 2 horas por sesión
        
        logger.info(f"⚙️ Configuración de producción:")
        logger.info(f"   - Máximo documentos por sesión: {max_documents}")
        logger.info(f"   - Tiempo máximo por sesión: {max_hours} horas")
        logger.info(f"   - Descarga de PDFs: HABILITADA")
        logger.info(f"   - Subida a Google Drive: {'HABILITADA' if Config.GOOGLE_DRIVE_ENABLED else 'DESHABILITADA'}")
        
        # Ejecutar scraping completo
        logger.info("🔄 Iniciando proceso de scraping...")
        start_time = time.time()
        
        orchestrator.run_full_scraping(max_documents=max_documents)
        
        # Mostrar resumen final
        end_time = time.time()
        duration = end_time - start_time
        duration_hours = duration / 3600
        
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DE PRODUCCIÓN")
        logger.info("=" * 60)
        logger.info(f"⏱️ Tiempo total de ejecución: {duration_hours:.2f} horas")
        
        # Verificar resultados
        session = get_session()
        tesis_con_pdf = session.query(Tesis).filter(Tesis.google_drive_id.isnot(None)).count()
        total_tesis_final = session.query(Tesis).count()
        
        logger.info(f"📄 Total tesis en BD: {total_tesis_final}")
        logger.info(f"📁 Tesis con PDF en Drive: {tesis_con_pdf}")
        logger.info(f"📈 Nuevas tesis agregadas: {total_tesis_final - total_tesis}")
        
        if Config.GOOGLE_DRIVE_ENABLED:
            logger.info(f"☁️ PDFs subidos a Google Drive: {tesis_con_pdf}")
        
        logger.info("✅ SCRAPER DE PRODUCCIÓN COMPLETADO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en scraper de producción: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
