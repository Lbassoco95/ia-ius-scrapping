#!/usr/bin/env python3
"""
Scraper Selenium para la página de tesis y jurisprudencia de SCJN
- Navegación automática
- Extracción de resultados
- Manejo de detalles de tesis
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SeleniumSCJNScraper:
    """Scraper para la página de SCJN usando Selenium"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://sjf2.scjn.gob.mx"
        self.search_url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        
    def setup_driver(self) -> bool:
        """Configurar el driver de Firefox como alternativa"""
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import logging

            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")  # Ejecutar sin interfaz
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")

            # Usar GeckoDriverManager para obtener la ruta correcta
            service = FirefoxService(GeckoDriverManager().install())

            # Crear driver
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.wait = WebDriverWait(self.driver, 10)

            logger.info("✅ Driver configurado correctamente (usando Firefox)")
            return True

        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    def close_driver(self):
        """Cerrar el driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Driver cerrado")
            except Exception as e:
                logger.error(f"❌ Error cerrando driver: {e}")
    
    def navigate_to_search_page(self) -> bool:
        """Navegar a la página de búsqueda"""
        try:
            logger.info(f"🌐 Navegando a: {self.search_url}")
            self.driver.get(self.search_url)
            
            # Esperar a que cargue la página
            time.sleep(5)
            
            # Verificar que estamos en la página correcta
            page_title = self.driver.title.lower()
            if "tesis" in page_title or "búsqueda" in page_title:
                logger.info("✅ Página de búsqueda cargada")
                return True
            else:
                logger.error(f"❌ No se pudo cargar la página de búsqueda. Título: {self.driver.title}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error navegando a página de búsqueda: {e}")
            return False
    
    def search_for_tesis(self, search_term: str) -> bool:
        """Realizar búsqueda de tesis"""
        try:
            logger.info(f"🔍 Buscando: {search_term}")
            
            # 1. Seleccionar épocas (necesario para que aparezcan resultados)
            logger.info("📅 Seleccionando épocas...")
            try:
                # Buscar enlaces de épocas
                epoca_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Época')]")
                if epoca_links:
                    # Hacer click en la primera época disponible
                    epoca_links[0].click()
                    time.sleep(2)
                    logger.info("✅ Época seleccionada")
                else:
                    logger.warning("⚠️ No se encontraron enlaces de épocas")
            except Exception as e:
                logger.warning(f"⚠️ Error seleccionando épocas: {e}")
            
            # 2. Buscar campo de búsqueda
            search_selectors = [
                "input[type='text']",
                "input[placeholder*='Escriba el tema']",
                "input.form-control.sjf-input-search"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        # Verificar que el elemento sea visible y editable
                        if elem.is_displayed() and elem.is_enabled():
                            search_input = elem
                            break
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                logger.error("❌ No se encontró campo de búsqueda")
                return False
            
            # 3. Limpiar y escribir término de búsqueda
            search_input.clear()
            search_input.send_keys(search_term)
            time.sleep(2)
            
            # 4. Buscar botón de búsqueda
            search_button_selectors = [
                "button.btn.sjf-button-search",
                "button[class*='btn']",
                "button:contains('Buscar')",
                "button:contains('Ver todo')"
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            button_text = elem.text.strip()
                            if "Buscar" in button_text or "Ver todo" in button_text:
                                search_button = elem
                                break
                    if search_button:
                        break
                except:
                    continue
            
            if search_button:
                search_button.click()
                logger.info("🔍 Botón de búsqueda clickeado")
            else:
                # Intentar con Enter
                search_input.send_keys("\n")
                logger.info("🔍 Búsqueda enviada con Enter")
            
            # 5. Esperar resultados y verificar navegación
            logger.info("⏳ Esperando resultados...")
            time.sleep(10)  # Más tiempo para que carguen los resultados
            
            # Verificar si la URL cambió a la página de resultados
            current_url = self.driver.current_url
            if "listado-resultado-tesis" in current_url:
                logger.info("✅ Navegación a página de resultados exitosa")
            else:
                logger.warning(f"⚠️ URL actual: {current_url}")
            
            # 6. Verificar que hay resultados
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, ".list-group-item")
            if result_elements:
                logger.info(f"✅ Encontrados {len(result_elements)} elementos de resultado")
            else:
                logger.warning("⚠️ No se encontraron elementos de resultado")
            
            logger.info("✅ Búsqueda realizada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return False
    
    def extract_search_results(self) -> List[Dict]:
        """Extraer resultados de búsqueda"""
        results = []
        
        try:
            logger.info("📋 Extrayendo resultados...")
            
            # Selectores para resultados - basados en el análisis real
            result_selectors = [
                ".list-group-item",  # Encontrado en el análisis
                ".item",
                "[class*='item']",
                ".result",
                "[class*='result']",
                "tr",
                ".row",
                ".col",
                ".card",
                ".panel"
            ]
            
            result_elements = []
            for selector in result_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Filtrar solo los elementos que contengan al menos un enlace a /detalle/tesis/
                        for elem in elements:
                            try:
                                links = elem.find_elements(By.TAG_NAME, "a")
                                if any('/detalle/tesis/' in (link.get_attribute('href') or '') for link in links):
                                    result_elements.append(elem)
                            except:
                                continue
                        if result_elements:
                            logger.info(f"✅ Encontrados {len(result_elements)} elementos con enlace a detalle de tesis con selector '{selector}'")
                            break
                except:
                    continue
            
            if not result_elements:
                logger.warning("⚠️ No se encontraron resultados")
                return results
            
            logger.info(f"📊 Encontrados {len(result_elements)} resultados")
            
            for element in result_elements:
                try:
                    result = self.extract_result_data(element)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"❌ Error extrayendo resultado: {e}")
                    continue
            
            logger.info(f"✅ Extraídos {len(results)} resultados válidos")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo resultados: {e}")
            return results
    
    def extract_result_data(self, element) -> Optional[Dict]:
        """Extraer datos de un resultado individual"""
        try:
            logger.info("🔍 Iniciando extracción de datos de elemento...")
            
            # Extraer ID de la tesis
            id_selectors = [
                ".list-item-text.fw-bold",
                ".list-item-text",
                "[class*='list-item-text']",
                "a[class*='fw-bold']"
            ]
            
            scjn_id = ""
            for selector in id_selectors:
                try:
                    id_elem = element.find_element(By.CSS_SELECTOR, selector)
                    id_text = id_elem.text.strip()
                    logger.info(f"  ID selector '{selector}': '{id_text}'")
                    # Extraer número del texto "1. Registro digital: 2030542"
                    import re
                    numbers = re.findall(r'\d{6,}', id_text)
                    if numbers:
                        scjn_id = numbers[0]
                        logger.info(f"  ✅ ID extraído: {scjn_id}")
                        break
                except Exception as e:
                    logger.info(f"  ❌ Error con selector ID '{selector}': {e}")
                    continue
            
            # Extraer título
            title_selectors = [
                ".tesis-rubro-completo",
                ".block-with-text.text-decoration-none.font-weight-bold",
                "[class*='tesis-rubro']",
                "a[class*='tesis-rubro']"
            ]
            
            titulo = ""
            url = ""
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    titulo = title_elem.text.strip()
                    url = title_elem.get_attribute("href")
                    logger.info(f"  Título selector '{selector}': '{titulo[:50]}...'")
                    logger.info(f"  URL: {url}")
                    if titulo and url:
                        logger.info(f"  ✅ Título extraído: {titulo[:50]}...")
                        break
                except Exception as e:
                    logger.info(f"  ❌ Error con selector título '{selector}': {e}")
                    continue
            
            # Extraer metadatos
            metadata_selectors = [
                ".list-item-text2",
                "[class*='list-item-text2']"
            ]
            
            metadata = {}
            for selector in metadata_selectors:
                try:
                    meta_elem = element.find_element(By.CSS_SELECTOR, selector)
                    metadata_text = meta_elem.text.strip()
                    logger.info(f"  Metadatos selector '{selector}': '{metadata_text[:50]}...'")
                    if metadata_text:
                        # Parsear metadatos: "SCJN;11a. Época;Semanario Judicial de la Federación;P./J. 5/2025 (11a.) ;J; Publicación: viernes 13 de junio de 2025 10:19 h"
                        parts = metadata_text.split(';')
                        if len(parts) >= 4:
                            metadata['organo'] = parts[0].strip()
                            metadata['epoca'] = parts[1].strip()
                            metadata['publicacion'] = parts[2].strip()
                            metadata['numero'] = parts[3].strip()
                            if len(parts) > 4:
                                metadata['tipo'] = parts[4].strip()
                            if len(parts) > 5:
                                metadata['fecha_publicacion'] = parts[5].strip()
                            logger.info(f"  ✅ Metadatos extraídos: {metadata}")
                        break
                except Exception as e:
                    logger.info(f"  ❌ Error con selector metadatos '{selector}': {e}")
                    continue
            
            # Si no encontramos datos válidos, intentar extraer del texto completo
            if not scjn_id or not titulo:
                logger.info("  🔍 Intentando extracción del texto completo...")
                full_text = element.text.strip()
                if full_text:
                    logger.info(f"  Texto completo: {full_text[:100]}...")
                    # Extraer ID del texto completo
                    import re
                    numbers = re.findall(r'\d{6,}', full_text)
                    if numbers and not scjn_id:
                        scjn_id = numbers[0]
                        logger.info(f"  ✅ ID extraído del texto completo: {scjn_id}")
                    
                    # Extraer título (buscar texto en mayúsculas que parezca un título)
                    lines = full_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if (len(line) > 20 and 
                            line.isupper() and 
                            not line.startswith('Registro') and
                            not line.startswith('SCJN') and
                            not line.startswith('Publicación')):
                            titulo = line
                            logger.info(f"  ✅ Título extraído del texto completo: {titulo[:50]}...")
                            break
            
            # Verificar que tenemos datos mínimos
            if not scjn_id and not titulo:
                logger.warning("  ❌ No se encontraron datos mínimos (ID o título)")
                return None
            
            # Si no tenemos URL, construirla con el ID
            if not url and scjn_id:
                url = f"https://sjf2.scjn.gob.mx/detalle/tesis/{scjn_id}"
                logger.info(f"  🔗 URL construida: {url}")
            
            result = {
                'scjn_id': scjn_id,
                'titulo': titulo,
                'url': url,
                'metadata': metadata
            }
            
            logger.info(f"  ✅ Resultado final: ID={scjn_id}, Título={titulo[:30]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de resultado: {e}")
            return None
    
    def get_tesis_detail(self, url: str) -> Optional[Dict]:
        """Obtener detalles completos de una tesis"""
        try:
            if not url:
                return None
            
            logger.info(f"📄 Obteniendo detalles: {url}")
            
            # Navegar a la página de detalles
            self.driver.get(url)
            time.sleep(3)
            
            # Extraer contenido
            detail_data = {}
            
            # Título
            title_selectors = ["h1", ".titulo", ".tesis-title", "#titulo"]
            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data['titulo'] = title_elem.text.strip()
                    break
                except:
                    continue
            
            # Rubro
            rubro_selectors = [".rubro", ".rubro-tesis", ".categoria"]
            for selector in rubro_selectors:
                try:
                    rubro_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data['rubro'] = rubro_elem.text.strip()
                    break
                except:
                    continue
            
            # Texto de la tesis
            texto_selectors = [".texto", ".contenido", ".tesis-text", "#contenido"]
            for selector in texto_selectors:
                try:
                    texto_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data['texto'] = texto_elem.text.strip()
                    break
                except:
                    continue
            
            # Precedente
            precedente_selectors = [".precedente", ".precedent", ".antecedente"]
            for selector in precedente_selectors:
                try:
                    precedente_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data['precedente'] = precedente_elem.text.strip()
                    break
                except:
                    continue
            
            # URL del PDF
            pdf_selectors = ["a[href*='.pdf']", ".pdf-link", "#pdf-download"]
            for selector in pdf_selectors:
                try:
                    pdf_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data['pdf_url'] = pdf_elem.get_attribute("href")
                    break
                except:
                    continue
            
            # HTML completo para análisis posterior
            detail_data['html_content'] = self.driver.page_source
            
            logger.info("✅ Detalles extraídos correctamente")
            return detail_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo detalles: {e}")
            return None
    
    def download_pdf(self, tesis_url: str, scjn_id: str) -> Optional[str]:
        """Descargar PDF de la página de detalle usando Selenium y asociarlo a la tesis (cada descarga en nueva sesión)"""
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import StaleElementReferenceException
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        import os
        import glob

        PDF_DIR = os.path.abspath("data/pdfs")
        max_retries = 3
        for attempt in range(max_retries):
            chrome_options = Options()
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            # chrome_options.add_argument("--headless")  # Puedes activar headless si todo funciona
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_prefs = {
                "download.default_directory": PDF_DIR,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", chrome_prefs)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            pdf_path = None
            try:
                # Limpiar PDFs temporales antes de descargar
                for f in glob.glob(os.path.join(PDF_DIR, '*.pdf')):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
                driver.get(tesis_url)
                time.sleep(8)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                download_button = None
                # 1. Esperar botón por aria-label, title, íconos
                selectors = [
                    "button[aria-label*='Descargar']", "button[title*='Descargar']",
                    ".fa-download", ".icon-download"
                ]
                for selector in selectors:
                    try:
                        download_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if download_button:
                            break
                    except Exception:
                        continue
                # 2. Buscar enlaces <a> con texto o href
                if not download_button:
                    try:
                        links = driver.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute("href")
                            text = link.text.strip().lower()
                            if (href and href.lower().endswith('.pdf')) or ('pdf' in text) or ('descargar' in text):
                                download_button = link
                                break
                    except Exception:
                        pass
                # 3. Buscar botones con texto específico
                if not download_button:
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            text = button.text.strip().lower()
                            if 'descargar' in text or 'pdf' in text or 'download' in text:
                                download_button = button
                                break
                    except Exception:
                        pass
                # 4. Buscar por clase CSS específica
                if not download_button:
                    try:
                        download_button = driver.find_element(By.CSS_SELECTOR, ".btn-download, .download-btn, .pdf-download")
                    except Exception:
                        pass
                if download_button:
                    try:
                        # Hacer scroll hacia el botón
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                        time.sleep(2)
                        # Intentar click directo
                        download_button.click()
                        time.sleep(5)
                        # Verificar si se descargó el archivo
                        pdf_files = glob.glob(os.path.join(PDF_DIR, '*.pdf'))
                        if pdf_files:
                            # Tomar el archivo más reciente
                            pdf_path = max(pdf_files, key=os.path.getctime)
                            # Renombrar con el ID de la tesis
                            new_name = os.path.join(PDF_DIR, f"tesis_{scjn_id}.pdf")
                            if os.path.exists(new_name):
                                os.remove(new_name)
                            os.rename(pdf_path, new_name)
                            pdf_path = new_name
                            logger.info(f"✅ PDF descargado: {pdf_path}")
                            break
                        else:
                            logger.warning(f"⚠️ No se detectó descarga en intento {attempt + 1}")
                    except Exception as e:
                        logger.error(f"❌ Error haciendo click en botón de descarga: {e}")
                else:
                    logger.warning(f"⚠️ No se encontró botón de descarga en intento {attempt + 1}")
            except Exception as e:
                logger.error(f"❌ Error en intento {attempt + 1}: {e}")
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass
            if pdf_path:
                break
        if not pdf_path:
            logger.error(f"❌ No se pudo descargar PDF después de {max_retries} intentos")
        return pdf_path

    def test_connection(self) -> bool:
        """Probar conexión con la página SCJN"""
        try:
            logger.info("🔗 Probando conexión con SCJN...")
            
            if not self.setup_driver():
                return False
            
            if not self.navigate_to_search_page():
                return False
            
            # Verificar que la página cargó correctamente
            page_title = self.driver.title
            logger.info(f"📄 Título de la página: {page_title}")
            
            # Verificar elementos básicos
            if "scjn" in page_title.lower() or "suprema" in page_title.lower():
                logger.info("✅ Conexión exitosa con SCJN")
                return True
            else:
                logger.warning("⚠️ Página cargada pero no parece ser SCJN")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False
        finally:
            self.close_driver() 