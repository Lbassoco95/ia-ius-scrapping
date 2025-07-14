#!/usr/bin/env python3
"""
Script de producción para scraping de tesis de la SCJN
- Múltiples términos de búsqueda
- Descarga de PDFs
- Subida a Google Drive
- Monitoreo en tiempo real
"""

import logging
import sys
import os
import time
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.selenium_scraper import SeleniumSCJNScraper
from src.database.models import create_tables, get_session, Tesis, ScrapingSession
from src.storage.google_drive import GoogleDriveManager

class ProductionScraper:
    """Scraper de producción con múltiples búsquedas"""
    
    def __init__(self):
        self.scraper = SeleniumSCJNScraper()
        self.gdrive = GoogleDriveManager()
        self.session_id = f"prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Términos de búsqueda específicos para tesis
        self.search_terms = [
            "amparo",
            "derechos humanos", 
            "constitucional",
            "penal",
            "civil",
            "laboral",
            "administrativo",
            "fiscal",
            "mercantil",
            "familia",
            "agrario",
            "ambiental"
        ]
        
        # Crear directorios necesarios
        os.makedirs("data/pdfs", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
    def start_production(self):
        """Iniciar proceso de producción"""
        logger = logging.getLogger(__name__)
        
        logger.info("🚀 === INICIANDO SCRAPING DE PRODUCCIÓN ===")
        logger.info(f"📅 Sesión: {self.session_id}")
        logger.info(f"🔍 Términos de búsqueda: {len(self.search_terms)}")
        
        # Crear base de datos
        try:
            create_tables()
            logger.info("✅ Base de datos inicializada")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            return False
        
        # Registrar sesión
        self.register_session()
        
        # Configurar scraper
        if not self.scraper.setup_driver():
            logger.error("❌ No se pudo configurar el driver")
            return False
        
        total_found = 0
        total_downloaded = 0
        total_uploaded = 0
        
        try:
            # Navegar a la página
            if not self.scraper.navigate_to_search_page():
                logger.error("❌ No se pudo navegar a la página")
                return False
            
            # Procesar cada término de búsqueda
            for i, term in enumerate(self.search_terms, 1):
                logger.info(f"\n📋 [{i}/{len(self.search_terms)}] Procesando: '{term}'")
                
                # Realizar búsqueda
                if not self.scraper.search_for_tesis(term):
                    logger.warning(f"⚠️ No se pudo buscar: {term}")
                    continue
                
                # Extraer resultados
                results = self.scraper.extract_search_results()
                logger.info(f"📊 Encontrados {len(results)} resultados para '{term}'")
                
                if not results:
                    logger.warning(f"⚠️ No se encontraron resultados para: {term}")
                    continue
                
                # Procesar cada resultado
                for j, result in enumerate(results, 1):
                    logger.info(f"  📄 [{j}/{len(results)}] Procesando: {result.get('titulo', 'Sin título')[:50]}...")
                    
                    try:
                        # Verificar si ya existe en la base de datos
                        session = get_session()
                        existing = session.query(Tesis).filter_by(scjn_id=result.get('scjn_id')).first()
                        
                        if existing:
                            logger.info(f"    ⏭️ Ya existe en BD: {result.get('scjn_id')}")
                            session.close()
                            continue
                        
                        # Obtener detalles completos
                        detail_url = result.get('url')
                        if detail_url:
                            details = self.scraper.get_tesis_detail(detail_url)
                            if details:
                                result.update(details)
                        
                        # Guardar en base de datos
                        tesis = Tesis(
                            scjn_id=result.get('scjn_id'),
                            titulo=result.get('titulo'),
                            url=result.get('url'),
                            rubro=result.get('rubro'),
                            texto=result.get('texto'),
                            precedente=result.get('precedente'),
                            metadata_json=result.get('metadata'),
                            procesado=True
                        )
                        
                        session.add(tesis)
                        session.commit()
                        session.close()
                        
                        total_found += 1
                        logger.info(f"    ✅ Guardado en BD: {result.get('scjn_id')}")
                        
                        # Descargar PDF si está disponible
                        if result.get('pdf_url'):
                            url = result.get('url')
                            scjn_id = result.get('scjn_id')
                            if url and scjn_id:
                                pdf_path = self.scraper.download_pdf(url, scjn_id)
                                if pdf_path:
                                    total_downloaded += 1
                                    logger.info(f"    📥 PDF descargado: {pdf_path}")
                                    
                                    # Subir a Google Drive
                                    try:
                                        gdrive_result = self.gdrive.upload_pdf(pdf_path, scjn_id)
                                        if gdrive_result:
                                            total_uploaded += 1
                                            logger.info(f"    ☁️ Subido a Google Drive: {gdrive_result}")
                                            
                                            # Actualizar enlace en BD
                                            session = get_session()
                                            tesis = session.query(Tesis).filter_by(scjn_id=scjn_id).first()
                                            if tesis:
                                                tesis.google_drive_link = gdrive_result
                                                session.commit()
                                            session.close()
                                    except Exception as e:
                                        logger.warning(f"    ⚠️ Error subiendo a Google Drive: {e}")
                        
                    except Exception as e:
                        logger.error(f"    ❌ Error procesando resultado: {e}")
                        continue
                
                # Pausa entre búsquedas
                time.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Error en proceso de producción: {e}")
        finally:
            self.scraper.close_driver()
            self.finalize_session(total_found, total_downloaded, total_uploaded)
        
        logger.info(f"\n🎉 === PRODUCCIÓN COMPLETADA ===")
        logger.info(f"📊 Total encontradas: {total_found}")
        logger.info(f"📥 Total descargadas: {total_downloaded}")
        logger.info(f"☁️ Total subidas: {total_uploaded}")
        
        return True
    
    def register_session(self):
        """Registrar sesión de scraping"""
        try:
            session = get_session()
            scraping_session = ScrapingSession(
                session_id=self.session_id,
                fase='production',
                estado='running'
            )
            session.add(scraping_session)
            session.commit()
            session.close()
            
            logging.getLogger(__name__).info(f"📝 Sesión registrada: {self.session_id}")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"❌ Error registrando sesión: {e}")
    
    def finalize_session(self, total_found, total_downloaded, total_uploaded):
        """Finalizar sesión de scraping"""
        try:
            session = get_session()
            scraping_session = session.query(ScrapingSession).filter_by(session_id=self.session_id).first()
            if scraping_session:
                scraping_session.fecha_fin = datetime.now()
                scraping_session.archivos_descargados = total_downloaded
                scraping_session.estado = 'completed'
                session.commit()
            session.close()
            
            logging.getLogger(__name__).info(f"📝 Sesión finalizada: {self.session_id}")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"❌ Error finalizando sesión: {e}")

def main():
    """Función principal"""
    scraper = ProductionScraper()
    success = scraper.start_production()
    
    if success:
        print("\n🎉 ¡Producción completada exitosamente!")
        print("📊 Revisa los logs en 'logs/production_scraping.log'")
        print("📁 Los PDFs se guardan en 'data/pdfs/'")
        print("🗄️ Los datos se almacenan en 'data/scjn_database.db'")
    else:
        print("\n❌ Error en la producción")
        print("📋 Revisa los logs para más detalles")

if __name__ == "__main__":
    main() 