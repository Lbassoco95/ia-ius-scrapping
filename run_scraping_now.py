#!/usr/bin/env python3
"""
Script para ejecutar el scraping manualmente ahora
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/manual_scraping.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal"""
    
    logger.info("🚀 EJECUTANDO SCRAPING MANUAL")
    logger.info(f"⏰ Hora de ejecución: {datetime.now()}")
    
    try:
        # Configurar entorno
        os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
        os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
        os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
        
        # Importar módulos
        from src.scraper.main import ScrapingOrchestrator
        
        # Inicializar orquestador
        orchestrator = ScrapingOrchestrator()
        
        logger.info("✅ Orquestador inicializado")
        
        # Ejecutar scraping completo
        logger.info("🔍 Iniciando scraping de tesis...")
        orchestrator.run_full_scraping(max_documents=30)  # Limitar a 30 tesis
        
        logger.info("✅ Scraping manual completado exitosamente")
        
        # Mostrar resumen
        from src.database.models import Tesis, get_session
        session = get_session()
        total_tesis = session.query(Tesis).count()
        tesis_con_pdf = session.query(Tesis).filter(Tesis.google_drive_link.isnot(None)).count()
        session.close()
        
        logger.info(f"📊 Resumen: {total_tesis} tesis total, {tesis_con_pdf} con PDF en Google Drive")
        
    except Exception as e:
        logger.error(f"❌ Error en scraping manual: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Scraping manual completado exitosamente")
    else:
        print("❌ Error en scraping manual") 