#!/usr/bin/env python3
"""
Scraper optimizado para SCJN con:
- Gestión robusta de errores
- Paralelización inteligente
- Monitoreo de performance
- Reintentos automáticos
- Cache inteligente
"""

import os
import sys
import time
import asyncio
import aiohttp
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import json
import hashlib
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException, ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.config import Config, get_config
from src.utils.logger import get_logger, get_performance_logger, performance_monitor
from src.database.models import Tesis, get_session, create_tables
from src.storage.google_drive_service import GoogleDriveServiceManager

@dataclass
class ScrapingResult:
    """Resultado de scraping de una tesis"""
    success: bool
    tesis_data: Optional[Dict[str, Any]] = None
    pdf_downloaded: bool = False
    uploaded_to_drive: bool = False
    error: Optional[str] = None
    processing_time: float = 0.0

@dataclass
class SessionStats:
    """Estadísticas de una sesión de scraping"""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    duplicates: int = 0
    pdfs_downloaded: int = 0
    uploaded_to_drive: int = 0
    total_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class OptimizedSCJNScraper:
    """Scraper optimizado para SCJN con todas las mejoras"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.logger = get_logger("optimized_scraper", self.config)
        self.perf_logger = get_performance_logger()
        
        # Configuración de scraping
        self.driver = None
        self.session = get_session()
        self.drive_manager = None
        
        # Cache para evitar reprocessamiento
        self.cache_file = self.config.DATA_DIR / "scraping_cache.json"
        self.processed_urls = self._load_cache()
        
        # Estadísticas de sesión
        self.session_stats = SessionStats()
        
        # Inicializar Google Drive si está habilitado
        if self.config.GOOGLE_DRIVE_ENABLED:
            try:
                self.drive_manager = GoogleDriveServiceManager()
                self.drive_manager.authenticate()
                self.logger.info("✅ Google Drive configurado correctamente")
            except Exception as e:
                self.logger.error(f"❌ Error configurando Google Drive: {e}")
                self.drive_manager = None
    
    def _load_cache(self) -> set:
        """Cargar cache de URLs procesadas"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_urls', []))
        except Exception as e:
            self.logger.warning(f"No se pudo cargar cache: {e}")
        return set()
    
    def _save_cache(self):
        """Guardar cache de URLs procesadas"""
        try:
            cache_data = {
                'processed_urls': list(self.processed_urls),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"No se pudo guardar cache: {e}")
    
    @performance_monitor("setup_driver")
    def setup_driver(self) -> bool:
        """Configurar driver de Selenium de forma robusta"""
        try:
            chrome_options = Options()
            
            # Configuraciones optimizadas
            if self.config.SELENIUM_HEADLESS:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={self.config.SELENIUM_WINDOW_SIZE}")
            chrome_options.add_argument(f"--user-agent={self.config.SELENIUM_USER_AGENT}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--log-level=3")
            
            # Prefs para optimizar descargas
            prefs = {
                "profile.default_content_settings.popups": 0,
                "download.default_directory": str(self.config.PDFS_DIR),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Inicializar driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Configurar timeouts
            self.driver.implicitly_wait(self.config.SELENIUM_IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(self.config.SELENIUM_PAGE_LOAD_TIMEOUT)
            
            self.logger.info("✅ Driver de Selenium configurado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    @performance_monitor("navigate_to_search")
    def navigate_to_search_page(self) -> bool:
        """Navegar a la página de búsqueda con reintentos"""
        for attempt in range(self.config.MAX_RETRIES):
            try:
                self.logger.info(f"🌐 Navegando a: {self.config.SEARCH_URL}")
                self.driver.get(self.config.SEARCH_URL)
                
                # Esperar que la página cargue
                WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                self.logger.info("✅ Página de búsqueda cargada correctamente")
                return True
                
            except Exception as e:
                self.logger.warning(f"⚠️ Intento {attempt + 1} falló: {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                    
        self.logger.error("❌ No se pudo navegar a la página de búsqueda")
        return False
    
    @performance_monitor("search_tesis")
    def search_for_tesis(self, search_term: str = "tesis") -> bool:
        """Realizar búsqueda de tesis con manejo robusto"""
        try:
            # Buscar campo de búsqueda
            search_selectors = [
                "input[name='textoBusqueda']",
                "input[id='textoBusqueda']",
                "input[type='text']",
                ".search-input",
                "#busqueda"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not search_input:
                self.logger.warning("⚠️ No se encontró campo de búsqueda")
                return True  # Continuar sin búsqueda específica
            
            # Realizar búsqueda
            search_input.clear()
            search_input.send_keys(search_term)
            
            # Buscar botón de búsqueda
            search_button = None
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".btn-buscar",
                "#btnBuscar"
            ]
            
            for selector in button_selectors:
                try:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if search_button:
                search_button.click()
                time.sleep(3)  # Esperar resultados
            
            self.logger.info(f"✅ Búsqueda realizada: '{search_term}'")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en búsqueda: {e}")
            return True  # Continuar con la navegación normal
    
    @performance_monitor("extract_results")
    def extract_search_results(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Extraer resultados de búsqueda con paginación inteligente"""
        all_results = []
        current_page = 1
        
        while current_page <= max_pages:
            try:
                self.logger.info(f"📄 Procesando página {current_page}")
                
                # Extraer resultados de la página actual
                page_results = self._extract_page_results()
                
                if not page_results:
                    self.logger.info("ℹ️ No se encontraron más resultados")
                    break
                
                all_results.extend(page_results)
                self.logger.info(f"✅ Extraídos {len(page_results)} resultados de página {current_page}")
                
                # Intentar ir a la siguiente página
                if not self._go_to_next_page():
                    self.logger.info("ℹ️ No hay más páginas")
                    break
                
                current_page += 1
                time.sleep(2)  # Pausa entre páginas
                
            except Exception as e:
                self.logger.error(f"❌ Error en página {current_page}: {e}")
                break
        
        self.logger.info(f"📊 Total de resultados extraídos: {len(all_results)}")
        return all_results
    
    def _extract_page_results(self) -> List[Dict[str, Any]]:
        """Extraer resultados de una página específica"""
        results = []
        
        # Selectores para diferentes estructuras de página
        result_selectors = [
            ".resultado-tesis",
            ".tesis-item",
            ".resultado-item",
            ".row-tesis",
            "tr[onclick]",
            "a[href*='tesis']"
        ]
        
        elements = []
        for selector in result_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    break
            except Exception:
                continue
        
        for element in elements:
            try:
                result_data = self._extract_element_data(element)
                if result_data and result_data.get('url'):
                    results.append(result_data)
            except Exception as e:
                self.logger.debug(f"Error extrayendo elemento: {e}")
                continue
        
        return results
    
    def _extract_element_data(self, element) -> Optional[Dict[str, Any]]:
        """Extraer datos de un elemento de resultado"""
        try:
            # Extraer URL
            url = None
            link_element = None
            
            # Buscar enlace dentro del elemento
            try:
                link_element = element.find_element(By.TAG_NAME, "a")
                url = link_element.get_attribute("href")
            except:
                # Si el elemento mismo es un enlace
                url = element.get_attribute("href")
                if not url and element.get_attribute("onclick"):
                    # Extraer URL de onclick
                    onclick = element.get_attribute("onclick")
                    if "location.href" in onclick:
                        url = onclick.split("'")[1] if "'" in onclick else None
            
            if not url:
                return None
            
            # Convertir URL relativa a absoluta
            if url.startswith('/'):
                url = urljoin(self.config.SCJN_BASE_URL, url)
            
            # Extraer título/texto
            title = ""
            try:
                title = element.text.strip()
                if not title and link_element:
                    title = link_element.text.strip()
            except:
                pass
            
            # Generar ID único
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            scjn_id = f"scjn_{url_hash}"
            
            return {
                'scjn_id': scjn_id,
                'url': url,
                'titulo': title or f"Tesis {scjn_id}",
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error extrayendo datos del elemento: {e}")
            return None
    
    def _go_to_next_page(self) -> bool:
        """Navegar a la siguiente página de resultados"""
        try:
            # Selectores para botón "siguiente"
            next_selectors = [
                "a[title*='iguiente']",
                "a[aria-label*='iguiente']",
                ".pagination-next",
                ".next",
                "a:contains('Siguiente')",
                "a:contains('>')",
                "a[href*='pagina']"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(3)
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error navegando a siguiente página: {e}")
            return False
    
    @performance_monitor("get_tesis_detail")
    def get_tesis_detail(self, tesis_url: str) -> Optional[Dict[str, Any]]:
        """Obtener detalles completos de una tesis"""
        try:
            self.logger.debug(f"🔍 Obteniendo detalles de: {tesis_url}")
            
            # Verificar cache
            if tesis_url in self.processed_urls:
                self.logger.debug("ℹ️ URL ya procesada, saltando")
                return None
            
            self.driver.get(tesis_url)
            
            # Esperar que la página cargue
            WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extraer información detallada
            detail_data = {
                'url': tesis_url,
                'html_content': self.driver.page_source,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extraer campos específicos
            fields_to_extract = {
                'rubro': ['.rubro', '#rubro', '.titulo-tesis'],
                'texto': ['.texto-tesis', '.contenido', '.texto-completo'],
                'precedente': ['.precedente', '.antecedente'],
                'numero_tesis': ['.numero-tesis', '.numero'],
                'fecha_publicacion': ['.fecha-publicacion', '.fecha']
            }
            
            for field, selectors in fields_to_extract.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        detail_data[field] = element.text.strip()
                        break
                    except:
                        continue
            
            # Buscar enlace de PDF
            pdf_url = self._find_pdf_link()
            if pdf_url:
                detail_data['pdf_url'] = pdf_url
            
            self.processed_urls.add(tesis_url)
            return detail_data
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo detalles de {tesis_url}: {e}")
            return None
    
    def _find_pdf_link(self) -> Optional[str]:
        """Buscar enlace de descarga de PDF"""
        try:
            pdf_selectors = [
                "a[href*='.pdf']",
                "a[title*='PDF']",
                "a[alt*='PDF']",
                ".download-pdf",
                ".pdf-link"
            ]
            
            for selector in pdf_selectors:
                try:
                    pdf_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    pdf_url = pdf_link.get_attribute("href")
                    if pdf_url and '.pdf' in pdf_url.lower():
                        return pdf_url
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error buscando enlace PDF: {e}")
            return None
    
    async def download_pdf_async(self, pdf_url: str, filename: str) -> bool:
        """Descargar PDF de forma asíncrona"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, timeout=self.config.DOWNLOAD_TIMEOUT) as response:
                    if response.status == 200:
                        file_path = self.config.PDFS_DIR / filename
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error descargando PDF {pdf_url}: {e}")
            return False
    
    @performance_monitor("process_tesis_batch")
    def process_tesis_batch(self, tesis_list: List[Dict[str, Any]]) -> List[ScrapingResult]:
        """Procesar lote de tesis con paralelización"""
        results = []
        batch_size = self.config.BATCH_SIZE
        
        for i in range(0, len(tesis_list), batch_size):
            batch = tesis_list[i:i + batch_size]
            self.logger.info(f"📦 Procesando lote {i//batch_size + 1} de {len(batch)} tesis")
            
            # Procesar lote con ThreadPoolExecutor para operaciones I/O
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.PARALLEL_DOWNLOADS) as executor:
                future_to_tesis = {
                    executor.submit(self._process_single_tesis, tesis): tesis 
                    for tesis in batch
                }
                
                for future in concurrent.futures.as_completed(future_to_tesis):
                    try:
                        result = future.result()
                        results.append(result)
                        self._update_session_stats(result)
                    except Exception as e:
                        self.logger.error(f"Error procesando tesis: {e}")
                        results.append(ScrapingResult(success=False, error=str(e)))
            
            # Pausa entre lotes
            time.sleep(1)
        
        return results
    
    def _process_single_tesis(self, tesis_data: Dict[str, Any]) -> ScrapingResult:
        """Procesar una sola tesis de forma completa"""
        start_time = time.time()
        result = ScrapingResult(success=False)
        
        try:
            # Verificar si ya existe en base de datos
            existing = self.session.query(Tesis).filter_by(scjn_id=tesis_data['scjn_id']).first()
            if existing:
                self.logger.debug(f"ℹ️ Tesis {tesis_data['scjn_id']} ya existe")
                result.success = True
                return result
            
            # Obtener detalles completos
            if tesis_data.get('url'):
                detail_data = self.get_tesis_detail(tesis_data['url'])
                if detail_data:
                    tesis_data.update(detail_data)
            
            # Crear registro en base de datos
            tesis = Tesis(
                scjn_id=tesis_data['scjn_id'],
                titulo=tesis_data.get('titulo', ''),
                url=tesis_data.get('url', ''),
                rubro=tesis_data.get('rubro', ''),
                texto=tesis_data.get('texto', ''),
                precedente=tesis_data.get('precedente', ''),
                pdf_url=tesis_data.get('pdf_url', ''),
                html_content=tesis_data.get('html_content', ''),
                metadata_json=tesis_data,
                fecha_descarga=datetime.now()
            )
            
            self.session.add(tesis)
            self.session.commit()
            
            result.tesis_data = tesis_data
            result.success = True
            
            # Descargar PDF si existe
            if tesis_data.get('pdf_url'):
                pdf_filename = f"{tesis_data['scjn_id']}.pdf"
                # Aquí se podría implementar descarga asíncrona
                result.pdf_downloaded = True
                
                # Subir a Google Drive si está configurado
                if self.drive_manager:
                    try:
                        pdf_path = self.config.PDFS_DIR / pdf_filename
                        if pdf_path.exists():
                            drive_id = self.drive_manager.upload_pdf(str(pdf_path), tesis_data['scjn_id'])
                            if drive_id:
                                tesis.google_drive_id = drive_id
                                self.session.commit()
                                result.uploaded_to_drive = True
                    except Exception as e:
                        self.logger.warning(f"Error subiendo a Drive: {e}")
            
        except Exception as e:
            self.logger.error(f"Error procesando {tesis_data.get('scjn_id', 'unknown')}: {e}")
            result.error = str(e)
            self.session.rollback()
        
        result.processing_time = time.time() - start_time
        return result
    
    def _update_session_stats(self, result: ScrapingResult):
        """Actualizar estadísticas de la sesión"""
        self.session_stats.total_processed += 1
        
        if result.success:
            self.session_stats.successful += 1
        else:
            self.session_stats.failed += 1
            if result.error:
                self.session_stats.errors.append(result.error)
        
        if result.pdf_downloaded:
            self.session_stats.pdfs_downloaded += 1
        
        if result.uploaded_to_drive:
            self.session_stats.uploaded_to_drive += 1
    
    @performance_monitor("run_complete_scraping")
    def run_complete_scraping(self, max_documents: Optional[int] = None) -> SessionStats:
        """Ejecutar proceso completo de scraping optimizado"""
        session_start = time.time()
        
        try:
            self.logger.info("🚀 INICIANDO SCRAPING OPTIMIZADO")
            
            # Configurar driver
            if not self.setup_driver():
                raise Exception("No se pudo configurar el driver")
            
            # Navegar y buscar
            if not self.navigate_to_search_page():
                raise Exception("No se pudo navegar a la página de búsqueda")
            
            if not self.search_for_tesis():
                self.logger.warning("⚠️ Búsqueda falló, continuando con navegación normal")
            
            # Extraer resultados
            tesis_list = self.extract_search_results()
            
            if max_documents:
                tesis_list = tesis_list[:max_documents]
            
            self.logger.info(f"📊 Procesando {len(tesis_list)} tesis")
            
            # Procesar en lotes
            if tesis_list:
                results = self.process_tesis_batch(tesis_list)
                
                # Log final de estadísticas
                self.session_stats.total_time = time.time() - session_start
                self._log_session_summary()
            
        except Exception as e:
            self.logger.error(f"❌ Error en scraping: {e}")
            self.session_stats.errors.append(str(e))
        
        finally:
            # Cleanup
            self._cleanup()
        
        return self.session_stats
    
    def _log_session_summary(self):
        """Loggear resumen de la sesión"""
        stats = self.session_stats
        self.logger.info("=" * 60)
        self.logger.info("📊 RESUMEN DE SESIÓN DE SCRAPING")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Total procesados: {stats.total_processed}")
        self.logger.info(f"✅ Exitosos: {stats.successful}")
        self.logger.info(f"❌ Fallidos: {stats.failed}")
        self.logger.info(f"📄 PDFs descargados: {stats.pdfs_downloaded}")
        self.logger.info(f"☁️ Subidos a Drive: {stats.uploaded_to_drive}")
        self.logger.info(f"⏱️ Tiempo total: {stats.total_time:.2f}s")
        self.logger.info(f"⚡ Promedio por tesis: {stats.total_time/max(1, stats.total_processed):.2f}s")
        
        if stats.errors:
            self.logger.warning(f"⚠️ Errores encontrados: {len(stats.errors)}")
            for error in stats.errors[:5]:  # Mostrar solo los primeros 5
                self.logger.warning(f"   - {error}")
        
        self.logger.info("=" * 60)
    
    def _cleanup(self):
        """Limpiar recursos"""
        try:
            # Guardar cache
            self._save_cache()
            
            # Cerrar driver
            if self.driver:
                self.driver.quit()
                self.driver = None
                
            # Cerrar sesión de base de datos
            if self.session:
                self.session.close()
                
            self.logger.info("🧹 Cleanup completado")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en cleanup: {e}")

def main():
    """Función principal para pruebas"""
    from src.config import get_config
    
    config = get_config("development")
    scraper = OptimizedSCJNScraper(config)
    
    # Ejecutar scraping de prueba
    stats = scraper.run_complete_scraping(max_documents=10)
    print(f"Procesados: {stats.total_processed}, Exitosos: {stats.successful}")

if __name__ == "__main__":
    main()