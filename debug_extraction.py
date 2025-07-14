#!/usr/bin/env python3
"""
Script de debug para probar la extracción de datos
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def debug_extraction():
    """Debug de la extracción de datos"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    service = Service(executable_path="/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔍 Debug de extracción de datos...")
        
        # Navegar y buscar
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        driver.get(url)
        time.sleep(5)
        
        # Seleccionar época
        epoca_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Época')]")
        if epoca_links:
            epoca_links[0].click()
            time.sleep(2)
        
        # Buscar y realizar búsqueda
        inputs = driver.find_elements(By.TAG_NAME, "input")
        search_input = None
        for inp in inputs:
            if inp.get_attribute("type") in ["text", "search"] and inp.is_displayed():
                search_input = inp
                break
        
        if search_input:
            search_input.clear()
            search_input.send_keys("derecho")
            time.sleep(2)
            
            buttons = driver.find_elements(By.TAG_NAME, "button")
            search_button = None
            for btn in buttons:
                if btn.get_attribute("type") == "submit" and btn.is_displayed():
                    search_button = btn
                    break
            
            if search_button:
                search_button.click()
                time.sleep(8)
                
                print("📋 Probando extracción...")
                
                # Buscar elemento de resultado
                result_selectors = [
                    ".list-group-item",
                    ".item",
                    "[class*='item']"
                ]
                
                target_element = None
                for selector in result_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 10:
                                target_element = elem
                                break
                        if target_element:
                            break
                    except:
                        continue
                
                if target_element:
                    print(f"🎯 Elemento encontrado: {target_element.text[:100]}...")
                    
                    # Probar extracción de ID
                    print("\n🔍 Extrayendo ID...")
                    id_selectors = [
                        ".list-item-text.fw-bold",
                        ".list-item-text",
                        "[class*='list-item-text']",
                        "a[class*='fw-bold']"
                    ]
                    
                    scjn_id = ""
                    for selector in id_selectors:
                        try:
                            id_elem = target_element.find_element(By.CSS_SELECTOR, selector)
                            id_text = id_elem.text.strip()
                            print(f"  Selector '{selector}': '{id_text}'")
                            numbers = re.findall(r'\d{6,}', id_text)
                            if numbers:
                                scjn_id = numbers[0]
                                print(f"  ✅ ID extraído: {scjn_id}")
                                break
                        except Exception as e:
                            print(f"  ❌ Error con selector '{selector}': {e}")
                    
                    # Probar extracción de título
                    print("\n🔍 Extrayendo título...")
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
                            title_elem = target_element.find_element(By.CSS_SELECTOR, selector)
                            titulo = title_elem.text.strip()
                            url = title_elem.get_attribute("href")
                            print(f"  Selector '{selector}': '{titulo[:50]}...'")
                            print(f"  URL: {url}")
                            if titulo and url:
                                print(f"  ✅ Título extraído: {titulo[:50]}...")
                                break
                        except Exception as e:
                            print(f"  ❌ Error con selector '{selector}': {e}")
                    
                    # Probar extracción de metadatos
                    print("\n🔍 Extrayendo metadatos...")
                    metadata_selectors = [
                        ".list-item-text2",
                        "[class*='list-item-text2']"
                    ]
                    
                    metadata = {}
                    for selector in metadata_selectors:
                        try:
                            meta_elem = target_element.find_element(By.CSS_SELECTOR, selector)
                            metadata_text = meta_elem.text.strip()
                            print(f"  Selector '{selector}': '{metadata_text[:50]}...'")
                            if metadata_text:
                                parts = metadata_text.split(';')
                                if len(parts) >= 4:
                                    metadata['organo'] = parts[0].strip()
                                    metadata['epoca'] = parts[1].strip()
                                    metadata['publicacion'] = parts[2].strip()
                                    metadata['numero'] = parts[3].strip()
                                    print(f"  ✅ Metadatos extraídos: {metadata}")
                                break
                        except Exception as e:
                            print(f"  ❌ Error con selector '{selector}': {e}")
                    
                    # Resultado final
                    print("\n📊 RESULTADO FINAL:")
                    print("=" * 50)
                    print(f"ID: {scjn_id}")
                    print(f"Título: {titulo[:50]}...")
                    print(f"URL: {url}")
                    print(f"Metadatos: {metadata}")
                    
                    if scjn_id or titulo:
                        print("✅ Extracción exitosa")
                    else:
                        print("❌ Extracción fallida")
                    
                else:
                    print("❌ No se encontró elemento de resultado")
                
            else:
                print("❌ No se encontró botón de búsqueda")
        else:
            print("❌ No se encontró campo de búsqueda")
        
        print("\n✅ Debug completado")
        
    except Exception as e:
        print(f"❌ Error durante el debug: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_extraction() 