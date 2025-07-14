#!/usr/bin/env python3
"""
Script de producción para ejecución automática
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
        logging.FileHandler("logs/production.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal de producción"""
    
    logger.info("🚀 Iniciando scraping automático")
    
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
        orchestrator.run_full_scraping(max_documents=50)  # Limitar a 50 tesis para prueba
        
        logger.info("✅ Scraping completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en producción: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Scraping automático completado exitosamente")
    else:
        print("❌ Error en scraping automático")
