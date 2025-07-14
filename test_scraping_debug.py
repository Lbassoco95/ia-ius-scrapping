#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el scraping de tesis
"""

import sys
import os
import time
import logging

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraping_debug():
    """Probar scraping con debug detallado"""
    
    logger.info("🔍 Iniciando prueba de scraping con debug...")
    
    # Configurar driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Modo visible para debug
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        logger.info(f"🌐 Navegando a: {Config.SEARCH_URL}")
        driver.get(Config.SEARCH_URL)
        
        # Esperar a que la página cargue
        time.sleep(10)
        
        logger.info(f"📄 Título de la página: {driver.title}")
        logger.info(f"🔗 URL actual: {driver.current_url}")
        
        # Verificar si hay elementos de búsqueda
        logger.info("🔍 Buscando elementos de búsqueda...")
        
        search_selectors = [
            "input[name='search']",
            "input[type='text']",
            "input[placeholder*='buscar']",
            "input[placeholder*='Buscar']",
            "#search",
            ".search-input"
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_input = elements[0]
                    logger.info(f"✅ Encontrado campo de búsqueda con selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"❌ Error con selector {selector}: {e}")
        
        if not search_input:
            logger.error("❌ No se encontró campo de búsqueda")
            return
        
        # Intentar hacer una búsqueda
        logger.info("🔍 Realizando búsqueda...")
        search_input.clear()
        search_input.send_keys("derecho constitucional")
        
        # Buscar botón de búsqueda
        search_button_selectors = [
            "button.sjf-button-search",
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Buscar')",
            ".search-button",
            "#search-button"
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_button = elements[0]
                    logger.info(f"✅ Encontrado botón de búsqueda con selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"❌ Error con selector {selector}: {e}")
        
        if search_button:
            search_button.click()
            logger.info("✅ Búsqueda realizada")
        else:
            # Intentar con Enter
            search_input.send_keys("\n")
            logger.info("✅ Búsqueda realizada con Enter")
        
        # Esperar resultados
        time.sleep(10)
        
        # Buscar resultados
        logger.info("📋 Buscando resultados...")
        
        # Primero, buscar cualquier enlace que contenga "tesis" o "detalle"
        logger.info("🔍 Buscando enlaces a tesis...")
        
        tesis_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='tesis'], a[href*='detalle']")
        logger.info(f"🔗 Enlaces con 'tesis' o 'detalle' encontrados: {len(tesis_links)}")
        
        if tesis_links:
            logger.info("📋 Mostrando primeros 5 enlaces encontrados:")
            for i, link in enumerate(tesis_links[:5]):
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    logger.info(f"  {i+1}. {text} -> {href}")
                except Exception as e:
                    logger.warning(f"  Error obteniendo enlace {i+1}: {e}")
        
        # Buscar elementos que contengan estos enlaces
        result_selectors = [
            ".list-group-item a[href*='tesis']",
            ".list-group-item a[href*='detalle']",
            ".resultado a[href*='tesis']",
            ".tesis-item a[href*='tesis']",
            ".result-item a[href*='tesis']",
            "a[href*='tesis']",
            "a[href*='detalle']"
        ]
        
        tesis_elements = []
        for selector in result_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    tesis_elements = elements
                    logger.info(f"✅ Encontrados {len(elements)} elementos con selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"❌ Error con selector {selector}: {e}")
        
        if not tesis_elements:
            logger.error("❌ No se encontraron elementos de tesis con enlaces")
            
            # Mostrar estructura de la página
            logger.info("📄 Explorando estructura de la página...")
            
            # Buscar contenedores principales
            containers = driver.find_elements(By.CSS_SELECTOR, ".container, .row, .col, .main-content")
            logger.info(f"📦 Contenedores encontrados: {len(containers)}")
            
            # Buscar elementos con clase que contenga "result" o "item"
            result_classes = driver.find_elements(By.CSS_SELECTOR, "[class*='result'], [class*='item']")
            logger.info(f"📋 Elementos con clase 'result' o 'item': {len(result_classes)}")
            
            # Mostrar las primeras clases encontradas
            classes_found = set()
            for elem in result_classes[:10]:
                try:
                    class_attr = elem.get_attribute('class')
                    if class_attr:
                        classes_found.update(class_attr.split())
                except:
                    pass
            
            logger.info(f"🎨 Clases CSS encontradas: {list(classes_found)[:10]}")
            
            return
        
        logger.info(f"📊 Procesando {len(tesis_elements)} elementos...")
        
        # Procesar los primeros 3 elementos para debug
        for i, element in enumerate(tesis_elements[:3]):
            try:
                logger.info(f"\n--- Elemento {i+1} ---")
                
                # Mostrar texto del elemento
                text_content = element.text.strip()
                logger.info(f"📝 Texto: {text_content[:100]}...")
                
                # Buscar enlaces
                links = element.find_elements(By.TAG_NAME, "a")
                logger.info(f"🔗 Enlaces encontrados: {len(links)}")
                
                for j, link in enumerate(links):
                    try:
                        href = link.get_attribute('href')
                        link_text = link.text.strip()
                        logger.info(f"  Enlace {j+1}: {link_text} -> {href}")
                    except Exception as e:
                        logger.warning(f"  Error obteniendo enlace {j+1}: {e}")
                
                # Verificar si tiene PDF (simular get_tesis_detail)
                if links:
                    link_url = links[0].get_attribute('href')
                    if link_url:
                        logger.info(f"🔍 Verificando PDF en: {link_url}")
                        
                        # Navegar a la página de detalle
                        driver.get(link_url)
                        time.sleep(5)
                        
                        # Buscar enlaces de PDF
                        pdf_selectors = [
                            "a[href*='.pdf']",
                            "a[href*='download']",
                            "button[aria-label*='Descargar']",
                            "button[title*='Descargar']",
                            ".fa-download",
                            ".icon-download"
                        ]
                        
                        pdf_found = False
                        for pdf_selector in pdf_selectors:
                            try:
                                pdf_elements = driver.find_elements(By.CSS_SELECTOR, pdf_selector)
                                if pdf_elements:
                                    logger.info(f"✅ PDF encontrado con selector: {pdf_selector}")
                                    pdf_found = True
                                    break
                            except:
                                continue
                        
                        if not pdf_found:
                            logger.info("❌ No se encontró PDF en esta tesis")
                        
                        # Volver a la página de resultados
                        driver.get(Config.SEARCH_URL)
                        time.sleep(5)
                        
                        # Rehacer la búsqueda
                        search_input = driver.find_element(By.CSS_SELECTOR, "input[name='search']")
                        search_input.clear()
                        search_input.send_keys("derecho constitucional")
                        search_button = driver.find_element(By.CSS_SELECTOR, "button.sjf-button-search")
                        search_button.click()
                        time.sleep(10)
                        
                        # Reencontrar elementos
                        tesis_elements = driver.find_elements(By.CSS_SELECTOR, ".list-group-item, .resultado, .tesis-item")
                
            except Exception as e:
                logger.error(f"❌ Error procesando elemento {i+1}: {e}")
        
        logger.info("✅ Prueba de debug completada")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de debug: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_scraping_debug() 