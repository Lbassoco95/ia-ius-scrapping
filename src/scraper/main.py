#!/usr/bin/env python3
"""
Script principal para ejecutar el scraping de tesis de la SCJN
"""

import sys
import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.scraper.selenium_scraper import SeleniumSCJNScraper
from src.storage.google_drive import GoogleDriveManager
from src.analysis.ai_analyzer import AIAnalyzer
from src.database.models import create_tables, get_session, Tesis
from src.config import Config
from organize_and_upload_tesis import TesisOrganizer
import time

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrapingOrchestrator:
    """Orquestador principal del proceso de scraping"""
    
    def __init__(self):
        self.scraper = SeleniumSCJNScraper()
        self.drive_manager = GoogleDriveManager()
        self.ai_analyzer = AIAnalyzer()
        
    def run_full_scraping(self, max_documents: Optional[int] = None):
        """Ejecutar proceso completo de scraping con límite de 3 horas"""
        try:
            logger.info("=== INICIANDO PROCESO DE SCRAPING ===")
            create_tables()
            logger.info("Creando base de datos...")
            
            # Configurar driver Selenium
            if not self.scraper.setup_driver():
                logger.error("❌ No se pudo configurar el driver de Selenium")
                return
                
            try:
                # Navegar a la página de búsqueda
                if not self.scraper.navigate_to_search_page():
                    logger.error("❌ No se pudo navegar a la página de búsqueda")
                    return
                
                # Realizar búsqueda (puedes ajustar el término de búsqueda)
                search_term = "tesis"  # Búsqueda general
                if not self.scraper.search_for_tesis(search_term):
                    logger.warning("⚠️ No se pudo realizar la búsqueda, continuando...")
                
                # Extraer resultados
                tesis_list = self.scraper.extract_search_results()
                if not tesis_list:
                    logger.warning("No se encontraron tesis para procesar")
                    return
                
                logger.info(f"Se encontraron {len(tesis_list)} tesis")
                
                # Limitar documentos si se especifica
                if max_documents:
                    tesis_list = tesis_list[:max_documents]
                    logger.info(f"Limitando a {max_documents} documentos")
                
                start_time = time.time()
                max_seconds = 3 * 3600  # 3 horas
                processed_count = 0
                pdfs_subidos = 0
                enlaces_generados = 0
                errores_count = 0
                organizer = TesisOrganizer()
                
                for tesis_data in tesis_list:
                    # Limitar a 3 horas
                    if time.time() - start_time > max_seconds:
                        logger.info("⏰ Tiempo máximo de ejecución alcanzado (3 horas)")
                        break
                    
                    try:
                        # Obtener detalles completos de la tesis
                        if tesis_data.get('url'):
                            detail_data = self.scraper.get_tesis_detail(tesis_data['url'])
                            if detail_data:
                                tesis_data.update(detail_data)
                        
                        # Descargar PDF si hay enlace
                        pdf_local_path = None
                        google_drive_id = None
                        google_drive_link = None
                        
                        if tesis_data.get('pdf_url'):
                            pdf_local_path = self.scraper.download_pdf(tesis_data['url'], tesis_data['scjn_id'])
                            if pdf_local_path:
                                logger.info(f"PDF descargado correctamente: {pdf_local_path}")
                                # Subir a Google Drive con organización
                                result = organizer.upload_tesis_with_organization(tesis_data, pdf_local_path)
                                if result:
                                    google_drive_id, google_drive_link = result
                                    logger.info(f"PDF subido a Google Drive: {google_drive_link}")
                                else:
                                    logger.warning(f"No se pudo subir el PDF a Google Drive para tesis {tesis_data.get('scjn_id')}")
                            else:
                                logger.warning(f"No se pudo descargar el PDF para tesis {tesis_data.get('scjn_id')}")
                        else:
                            logger.info(f"Tesis {tesis_data.get('scjn_id')} no tiene enlace a PDF")
                        
                        # Guardar en base de datos
                        self.save_tesis_to_database(tesis_data, google_drive_id, google_drive_link)
                        processed_count += 1
                        
                        if google_drive_id:
                            pdfs_subidos += 1
                            enlaces_generados += 1
                        
                        if processed_count % 10 == 0:
                            self.mostrar_resumen_periodico(
                                processed_count, len(tesis_list), 
                                pdfs_subidos, enlaces_generados, errores_count
                            )
                        
                        logger.info(f"Tesis procesada {processed_count}/{len(tesis_list)}")
                        
                    except Exception as e:
                        errores_count += 1
                        logger.error(f"Error procesando tesis {tesis_data.get('scjn_id', 'unknown')}: {e}")
                        continue
                
                self.mostrar_resumen_final(
                    processed_count, len(tesis_list), 
                    pdfs_subidos, enlaces_generados, errores_count
                )
                
            finally:
                # Cerrar driver
                self.scraper.close_driver()
                
        except Exception as e:
            logger.error(f"Error en ejecución principal: {e}")
            raise
    
    def mostrar_resumen_periodico(self, procesadas, total, pdfs_subidos, enlaces_generados, errores):
        """Mostrar resumen periódico del progreso"""
        porcentaje = (procesadas / total) * 100 if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 RESUMEN PERIÓDICO")
        logger.info("=" * 60)
        logger.info(f"📈 Progreso: {procesadas}/{total} tesis ({porcentaje:.1f}%)")
        logger.info(f"📄 PDFs subidos a Google Drive: {pdfs_subidos}")
        logger.info(f"🔗 Enlaces web generados: {enlaces_generados}")
        logger.info(f"❌ Errores encontrados: {errores}")
        logger.info(f"⏱️  Tiempo estimado restante: {self.estimar_tiempo_restante(procesadas, total)}")
        logger.info("=" * 60)
    
    def mostrar_resumen_final(self, procesadas, total, pdfs_subidos, enlaces_generados, errores):
        """Mostrar resumen final del proceso"""
        logger.info("=" * 60)
        logger.info("🎉 RESUMEN FINAL DEL SCRAPING")
        logger.info("=" * 60)
        logger.info(f"✅ Total tesis procesadas: {procesadas}/{total}")
        logger.info(f"📄 PDFs subidos a Google Drive: {pdfs_subidos}")
        logger.info(f"🔗 Enlaces web generados: {enlaces_generados}")
        logger.info(f"❌ Errores totales: {errores}")
        logger.info(f"📊 Tasa de éxito: {((procesadas - errores) / procesadas * 100):.1f}%" if procesadas > 0 else "0%")
        logger.info("=" * 60)
    
    def estimar_tiempo_restante(self, procesadas, total):
        """Estimar tiempo restante basado en progreso actual"""
        if procesadas == 0:
            return "Calculando..."
        
        # Estimación simple: 30 segundos por tesis
        tiempo_por_tesis = 30  # segundos
        tesis_restantes = total - procesadas
        tiempo_restante = tesis_restantes * tiempo_por_tesis
        
        if tiempo_restante < 60:
            return f"{tiempo_restante:.0f} segundos"
        elif tiempo_restante < 3600:
            return f"{tiempo_restante/60:.1f} minutos"
        else:
            return f"{tiempo_restante/3600:.1f} horas"
    
    def process_single_tesis_organized(self, tesis_data: Dict, organizer: TesisOrganizer):
        """Procesar una tesis individual usando organización automática"""
        try:
            session = get_session()
            existing_tesis = session.query(Tesis).filter(Tesis.scjn_id == tesis_data['scjn_id']).first()
            if existing_tesis:
                logger.info(f"Tesis {tesis_data['scjn_id']} ya existe en la base de datos")
                session.close()
                return False, False
            
            pdf_local_path = None
            google_drive_id = None
            google_drive_link = None
            
            if tesis_data.get('pdf_url'):
                pdf_filename = f"tesis_{tesis_data['scjn_id']}.pdf"
                pdf_local_path = self.scraper.download_pdf(tesis_data['pdf_url'], pdf_filename)
                if pdf_local_path:
                    # Usar lógica de organización
                    result = organizer.upload_tesis_with_organization(tesis_data, pdf_local_path)
                    if result:
                        google_drive_id, google_drive_link = result
                        logger.info(f"🔗 PDF subido: {google_drive_link}")
            
            # Guardar en base de datos
            self.save_tesis_to_database(tesis_data, google_drive_id, google_drive_link)
            session.close()
            return True, google_drive_id is not None
            
        except Exception as e:
            logger.error(f"Error procesando tesis {tesis_data.get('scjn_id', 'unknown')}: {e}")
            raise
    
    def save_tesis_to_database(self, tesis_data: Dict, google_drive_id: Optional[str] = None, google_drive_link: Optional[str] = None):
        """Guardar tesis en la base de datos"""
        try:
            session = get_session()
            
            # Crear objeto Tesis
            tesis = Tesis(
                scjn_id=tesis_data['scjn_id'],
                titulo=tesis_data['titulo'],
                url=tesis_data['url'],
                rubro=tesis_data.get('rubro', ''),
                texto=tesis_data.get('texto', ''),
                precedente=tesis_data.get('precedente', ''),
                pdf_url=tesis_data.get('pdf_url'),
                google_drive_id=google_drive_id,
                google_drive_link=google_drive_link,
                metadata_json=tesis_data.get('metadata', {})
            )
            
            session.add(tesis)
            session.commit()
            session.close()
            
            logger.info(f"Tesis guardada en base de datos: {tesis_data['scjn_id']}")
            
        except Exception as e:
            logger.error(f"Error guardando tesis en base de datos: {e}")
            raise
    
    def run_incremental_scraping(self):
        """Ejecutar scraping incremental (solo documentos nuevos)"""
        try:
            logger.info("=== INICIANDO SCRAPING INCREMENTAL ===")
            
            # Obtener última fecha de scraping
            session = get_session()
            last_tesis = session.query(Tesis).order_by(Tesis.fecha_creacion.desc()).first()
            session.close()
            
            if last_tesis:
                logger.info(f"Última tesis procesada: {last_tesis.fecha_creacion}")
            
            # Ejecutar scraping con filtros de fecha si es necesario
            self.run_full_scraping(max_documents=50)  # Procesar menos documentos en modo incremental
            
        except Exception as e:
            logger.error(f"Error en scraping incremental: {e}")
            raise

def main():
    """Función principal"""
    try:
        # Validar configuración
        Config.validate()
        
        # Crear orquestador
        orchestrator = ScrapingOrchestrator()
        
        # Verificar argumentos de línea de comandos
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "incremental":
                orchestrator.run_incremental_scraping()
            elif command == "full":
                max_docs = int(sys.argv[2]) if len(sys.argv) > 2 else None
                orchestrator.run_full_scraping(max_docs)
            else:
                print("Uso: python main.py [incremental|full] [max_documents]")
                print("  incremental: Solo documentos nuevos")
                print("  full: Todos los documentos (opcional: número máximo)")
        else:
            # Modo por defecto: scraping completo
            orchestrator.run_full_scraping()
            
    except Exception as e:
        logger.error(f"Error en ejecución principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        orchestrator = ScrapingOrchestrator()
        
        # Ejecutar scraping con límite de documentos
        max_docs = Config.MAX_FILES_PER_SESSION
        orchestrator.run_full_scraping(max_docs)
        
    except Exception as e:
        logger.error(f"Error en ejecución principal: {e}")
        sys.exit(1) 