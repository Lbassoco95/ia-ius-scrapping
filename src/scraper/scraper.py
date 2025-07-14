import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os
from typing import List, Dict, Optional
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.config import Config

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

class SCJNScraper:
    """Scraper para la página de tesis de la SCJN"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = Config.SCJN_BASE_URL
        self.search_url = Config.SEARCH_URL
        
    def get_search_page(self, page=1, filters=None):
        """Obtener página de búsqueda con filtros"""
        try:
            params = {
                'page': page,
                'size': 20
            }
            
            if filters:
                params.update(filters)
            
            response = self.session.get(self.search_url, params=params, timeout=Config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo página de búsqueda: {e}")
            return None
    
    def parse_search_results(self, html_content: str) -> List[Dict]:
        """Parsear resultados de búsqueda"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        try:
            # Buscar elementos de tesis (ajustar selectores según la estructura real)
            tesis_elements = soup.find_all('div', class_='tesis-item') or \
                           soup.find_all('tr', class_='tesis-row') or \
                           soup.find_all('div', class_='resultado-busqueda')
            
            for element in tesis_elements:
                tesis_data = self.extract_tesis_data(element)
                if tesis_data:
                    results.append(tesis_data)
                    
        except Exception as e:
            logger.error(f"Error parseando resultados: {e}")
            
        return results
    
    def extract_tesis_data(self, element) -> Optional[Dict]:
        """Extraer datos de un elemento de tesis"""
        try:
            # Extraer ID de la tesis
            link_element = element.find('a', href=True)
            if not link_element:
                return None
                
            href = link_element['href']
            scjn_id = self.extract_id_from_url(href)
            
            # Extraer título
            titulo = element.find('h3') or element.find('h4') or element.find('strong')
            titulo_text = titulo.get_text(strip=True) if titulo else "Sin título"
            
            # Extraer metadatos básicos
            metadata = self.extract_metadata(element)
            
            return {
                'scjn_id': scjn_id,
                'titulo': titulo_text,
                'url': urljoin(self.base_url, href),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de tesis: {e}")
            return None
    
    def extract_id_from_url(self, url: str) -> str:
        """Extraer ID de tesis de la URL"""
        try:
            # Buscar patrones como /detalle/tesis/2030758
            if '/detalle/tesis/' in url:
                return url.split('/detalle/tesis/')[-1].split('/')[0]
            elif '/tesis/' in url:
                return url.split('/tesis/')[-1].split('/')[0]
            else:
                # Extraer números de la URL
                import re
                numbers = re.findall(r'\d+', url)
                return numbers[-1] if numbers else url
        except:
            return url
    
    def extract_metadata(self, element) -> Dict:
        """Extraer metadatos de un elemento"""
        metadata = {}
        
        try:
            # Buscar diferentes tipos de metadatos
            metadata_selectors = [
                '.materia', '.epoca', '.sala', '.registro',
                '.fecha', '.tipo', '.numero'
            ]
            
            for selector in metadata_selectors:
                meta_element = element.select_one(selector)
                if meta_element:
                    key = selector.replace('.', '')
                    metadata[key] = meta_element.get_text(strip=True)
                    
        except Exception as e:
            logger.error(f"Error extrayendo metadatos: {e}")
            
        return metadata
    
    def get_tesis_detail(self, tesis_url: str) -> Optional[Dict]:
        """Obtener detalles completos de una tesis"""
        try:
            response = self.session.get(tesis_url, timeout=Config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información detallada
            detail_data = {
                'url': tesis_url,
                'html_content': response.text
            }
            
            # Extraer campos específicos
            fields = ['rubro', 'texto', 'precedente', 'materia', 'epoca', 'sala']
            
            for field in fields:
                element = soup.find('div', class_=field) or \
                         soup.find('span', class_=field) or \
                         soup.find('p', class_=field)
                if element:
                    detail_data[field] = element.get_text(strip=True)
            
            # Buscar enlace de PDF
            pdf_link = soup.find('a', href=lambda x: x and x.endswith('.pdf')) or \
                      soup.find('a', text=lambda x: x and 'PDF' in x.upper())
            
            if pdf_link:
                detail_data['pdf_url'] = urljoin(self.base_url, pdf_link['href'])
            
            return detail_data
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo detalles de tesis {tesis_url}: {e}")
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
                # 3. Buscar por XPath (por texto visible)
                if not download_button:
                    try:
                        download_button = driver.find_element(By.XPATH, "//*[contains(text(),'Descargar') or contains(text(),'PDF')]")
                    except Exception:
                        pass
                # 4. Fallback: buscar cualquier botón visible
                if not download_button:
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if btn.is_displayed() and ('descargar' in btn.text.lower() or 'pdf' in btn.text.lower()):
                                download_button = btn
                                break
                    except Exception:
                        pass
                if not download_button:
                    logger.warning(f"No se encontró botón/enlace de descarga en {tesis_url}")
                    driver.quit()
                    continue
                try:
                    ActionChains(driver).move_to_element(download_button).click().perform()
                except StaleElementReferenceException:
                    logger.warning(f"StaleElementReferenceException al hacer click, reintentando ({attempt+1}/{max_retries}) en {tesis_url}")
                    driver.quit()
                    continue
                except Exception:
                    try:
                        download_button.click()
                    except StaleElementReferenceException:
                        logger.warning(f"StaleElementReferenceException al hacer click directo, reintentando ({attempt+1}/{max_retries}) en {tesis_url}")
                        driver.quit()
                        continue
                    except Exception:
                        logger.warning(f"No se pudo hacer click en el botón/enlace de descarga en {tesis_url}")
                        driver.quit()
                        continue
                time.sleep(18)
                # Buscar PDF descargado
                pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
                if pdf_files:
                    pdf_files_full = [os.path.join(PDF_DIR, f) for f in pdf_files]
                    latest_pdf = max(pdf_files_full, key=os.path.getctime)
                    pdf_filename = f"tesis_{scjn_id}.pdf"
                    pdf_path = os.path.join(PDF_DIR, pdf_filename)
                    if os.path.basename(latest_pdf) != pdf_filename:
                        os.rename(latest_pdf, pdf_path)
                    else:
                        pdf_path = latest_pdf
                else:
                    logger.warning(f"No se descargó ningún PDF para {tesis_url}")
                driver.quit()
                if pdf_path and os.path.exists(pdf_path):
                    return pdf_path
            except Exception as e:
                logger.error(f"Error robusto descargando PDF en {tesis_url}: {e}")
                driver.quit()
                continue
        return None
    
    def scrape_recent_tesis(self, max_documents: int = None) -> List[Dict]:
        """Scraper de tesis recientes de la SCJN siguiendo el flujo correcto y robusto"""
        try:
            if max_documents is None:
                max_documents = Config.MAX_DOCUMENTS_PER_RUN
            logger.info(f"Iniciando scraping de hasta {max_documents} documentos")
            # 1. Obtener listado de URLs de detalle de tesis
            urls = self.get_tesis_detail_urls(max_documents)
            logger.info(f"🔗 Encontradas {len(urls)} URLs de detalle de tesis")
            tesis_list = []
            for idx, url in enumerate(urls):
                logger.info(f"📄 Procesando tesis {idx+1}/{len(urls)}: {url}")
                detail = self.get_tesis_detail_robust(url)
                if detail:
                    tesis_list.append(detail)
            return tesis_list
        except Exception as e:
            logger.error(f"Error en scraping robusto: {e}")
            return []

    def get_tesis_detail_urls(self, max_documents: int = 100) -> List[str]:
        """Extraer URLs de detalle de tesis como texto, no como elementos Selenium"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        chrome_options = Options()
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        urls = []
        try:
            logger.info("🌐 Navegando a página inicial de búsqueda...")
            driver.get(self.search_url)
            time.sleep(12)
            # Seleccionar todas las épocas y hacer click en 'Ver todo' (ajusta según tu flujo)
            try:
                # Seleccionar todas las épocas
                epocas_btn = driver.find_element(By.XPATH, "//*[contains(text(),'Todo')]")
                epocas_btn.click()
                time.sleep(2)
                logger.info("🔘 Seleccionando todas las épocas...")
                logger.info("✅ Épocas seleccionadas")
            except Exception:
                logger.warning("No se pudo seleccionar todas las épocas")
            try:
                ver_todo_btn = driver.find_element(By.ID, "button-addon1_add")
                ver_todo_btn.click()
                time.sleep(10)
                logger.info("👁️ Haciendo click en 'Ver todo'...")
                logger.info("✅ Navegando al listado de tesis")
            except Exception:
                logger.warning("No se pudo hacer click en 'Ver todo'")
            logger.info(f"🔗 URL actual: {driver.current_url}")
            # Buscar enlaces a tesis
            links = driver.find_elements(By.CSS_SELECTOR, ".list-group-item a[href*='tesis']")
            for link in links[:max_documents]:
                href = link.get_attribute("href")
                if href:
                    urls.append(href)
            logger.info(f"🔗 Encontrados {len(urls)} enlaces a tesis")
        except Exception as e:
            logger.error(f"Error extrayendo URLs de detalle: {e}")
        finally:
            driver.quit()
        return urls

    def get_tesis_detail_robust(self, url: str) -> Optional[Dict]:
        """Obtener detalles completos de una tesis abriendo cada URL en una nueva sesión de Selenium"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        chrome_options = Options()
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        detail_data = None
        try:
            driver.get(url)
            time.sleep(8)
            # Extraer información relevante (ajusta selectores según la página)
            detail_data = {'url': url}
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, "h1, .titulo, .tesis-title, #titulo")
                detail_data['titulo'] = title_elem.text.strip()
            except Exception:
                detail_data['titulo'] = ''
            try:
                rubro_elem = driver.find_element(By.CSS_SELECTOR, ".rubro, .rubro-tesis, .categoria")
                detail_data['rubro'] = rubro_elem.text.strip()
            except Exception:
                detail_data['rubro'] = ''
            try:
                texto_elem = driver.find_element(By.CSS_SELECTOR, ".texto, .contenido, .tesis-text, #contenido")
                detail_data['texto'] = texto_elem.text.strip()
            except Exception:
                detail_data['texto'] = ''
            try:
                precedente_elem = driver.find_element(By.CSS_SELECTOR, ".precedente, .precedent, .antecedente")
                detail_data['precedente'] = precedente_elem.text.strip()
            except Exception:
                detail_data['precedente'] = ''
            # PDF
            pdf_url = ''
            try:
                pdf_elem = driver.find_element(By.CSS_SELECTOR, "a[href$='.pdf'], .pdf-link, #pdf-download")
                pdf_url = pdf_elem.get_attribute("href")
            except Exception:
                pass
            detail_data['pdf_url'] = pdf_url
            # ID SCJN
            try:
                scjn_id = url.split('/')[-1]
                detail_data['scjn_id'] = scjn_id
            except Exception:
                detail_data['scjn_id'] = ''
            # HTML completo
            detail_data['html_content'] = driver.page_source
        except Exception as e:
            logger.error(f"Error extrayendo detalles de tesis en {url}: {e}")
        finally:
            driver.quit()
        return detail_data
    
    def save_results(self, results: List[Dict], filename: str = None):
        """Guardar resultados en archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/scraping_results_{timestamp}.json'
        
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Resultados guardados en: {filename}")
        return filename 