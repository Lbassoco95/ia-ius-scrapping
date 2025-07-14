#!/usr/bin/env python3
"""
Script para debuggear los botones en la página de búsqueda principal
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_page_buttons():
    """Debuggear botones en la página de búsqueda"""
    
    logger.info("🔍 Iniciando debug de botones...")
    
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
        # 1. Ir a la página de búsqueda principal
        logger.info("🌐 Navegando a página de búsqueda principal...")
        driver.get("https://sjf2.scjn.gob.mx/busqueda-principal-tesis")
        time.sleep(10)
        
        logger.info(f"📄 Título de la página: {driver.title}")
        logger.info(f"🔗 URL actual: {driver.current_url}")
        
        # 2. Buscar todos los botones en la página
        logger.info("🔍 Buscando todos los botones...")
        
        # Buscar por diferentes selectores
        button_selectors = [
            "button",
            "input[type='button']",
            "input[type='submit']",
            "a[role='button']",
            ".btn",
            "[class*='button']"
        ]
        
        all_buttons = []
        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                all_buttons.extend(buttons)
                logger.info(f"✅ Encontrados {len(buttons)} elementos con selector: {selector}")
            except Exception as e:
                logger.warning(f"❌ Error con selector {selector}: {e}")
        
        # Eliminar duplicados
        unique_buttons = []
        seen_texts = set()
        
        for button in all_buttons:
            try:
                text = button.text.strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique_buttons.append(button)
            except:
                pass
        
        logger.info(f"📋 Total de botones únicos encontrados: {len(unique_buttons)}")
        
        # Mostrar información de cada botón
        for i, button in enumerate(unique_buttons[:20]):  # Mostrar solo los primeros 20
            try:
                text = button.text.strip()
                tag_name = button.tag_name
                class_attr = button.get_attribute('class')
                id_attr = button.get_attribute('id')
                onclick = button.get_attribute('onclick')
                
                logger.info(f"\n--- Botón {i+1} ---")
                logger.info(f"📝 Texto: '{text}'")
                logger.info(f"🏷️ Tag: {tag_name}")
                logger.info(f"🎨 Clase: {class_attr}")
                logger.info(f"🆔 ID: {id_attr}")
                logger.info(f"🖱️ OnClick: {onclick}")
                
                # Verificar si es visible
                is_displayed = button.is_displayed()
                is_enabled = button.is_enabled()
                logger.info(f"👁️ Visible: {is_displayed}")
                logger.info(f"✅ Habilitado: {is_enabled}")
                
            except Exception as e:
                logger.warning(f"Error obteniendo info del botón {i+1}: {e}")
        
        # Buscar específicamente botones que contengan "ver" o "todo"
        logger.info("\n🔍 Buscando botones con 'ver' o 'todo'...")
        
        ver_todo_selectors = [
            "//button[contains(text(), 'Ver')]",
            "//button[contains(text(), 'ver')]",
            "//button[contains(text(), 'Todo')]",
            "//button[contains(text(), 'todo')]",
            "//a[contains(text(), 'Ver')]",
            "//a[contains(text(), 'ver')]",
            "//input[contains(@value, 'Ver')]",
            "//input[contains(@value, 'ver')]"
        ]
        
        for selector in ver_todo_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"✅ Encontrados {len(elements)} elementos con XPath: {selector}")
                    for j, elem in enumerate(elements):
                        try:
                            text = elem.text.strip() or elem.get_attribute('value') or elem.get_attribute('placeholder')
                            logger.info(f"  {j+1}. Texto: '{text}' - Tag: {elem.tag_name}")
                        except:
                            pass
            except Exception as e:
                logger.warning(f"❌ Error con XPath {selector}: {e}")
        
        # Buscar enlaces que puedan ser botones
        logger.info("\n🔍 Buscando enlaces que puedan ser botones...")
        
        links = driver.find_elements(By.TAG_NAME, "a")
        logger.info(f"🔗 Total de enlaces encontrados: {len(links)}")
        
        for i, link in enumerate(links[:10]):  # Mostrar solo los primeros 10
            try:
                text = link.text.strip()
                href = link.get_attribute('href')
                class_attr = link.get_attribute('class')
                
                if text and ('ver' in text.lower() or 'todo' in text.lower()):
                    logger.info(f"🔗 Enlace {i+1}: '{text}' -> {href} (clase: {class_attr})")
            except:
                pass
        
        logger.info("✅ Debug de botones completado")
        
    except Exception as e:
        logger.error(f"❌ Error en debug: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page_buttons() 