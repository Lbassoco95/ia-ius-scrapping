#!/usr/bin/env python3
"""
Script para analizar la estructura de un elemento de resultado individual
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def analyze_single_result():
    """Analizar la estructura de un elemento de resultado"""
    
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
        print("🔍 Analizando elemento de resultado individual...")
        
        # Navegar a la página
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        driver.get(url)
        time.sleep(5)
        
        # Realizar búsqueda
        print("🔍 Realizando búsqueda...")
        
        # Seleccionar época
        epoca_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Época')]")
        if epoca_links:
            epoca_links[0].click()
            time.sleep(2)
        
        # Buscar campo de búsqueda
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
            
            # Buscar botón de búsqueda
            buttons = driver.find_elements(By.TAG_NAME, "button")
            search_button = None
            for btn in buttons:
                if btn.get_attribute("type") == "submit" and btn.is_displayed():
                    search_button = btn
                    break
            
            if search_button:
                search_button.click()
                time.sleep(8)
                
                print("📋 Analizando elemento individual...")
                
                # Buscar el primer elemento de resultado
                result_selectors = [
                    ".list-group-item",
                    ".item",
                    "[class*='item']",
                    ".result",
                    "[class*='result']"
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
                    print(f"🎯 Elemento encontrado con selector '{selector}'")
                    print(f"📄 Texto completo: {target_element.text}")
                    print(f"🏷️ Clases: {target_element.get_attribute('class')}")
                    print(f"🆔 ID: {target_element.get_attribute('id')}")
                    
                    # Analizar estructura interna
                    print("\n🔍 ESTRUCTURA INTERNA:")
                    print("=" * 50)
                    
                    # Buscar enlaces
                    links = target_element.find_elements(By.TAG_NAME, "a")
                    print(f"Enlaces encontrados: {len(links)}")
                    for i, link in enumerate(links):
                        try:
                            link_text = link.text.strip()
                            link_href = link.get_attribute("href")
                            link_class = link.get_attribute("class")
                            print(f"  Enlace {i+1}:")
                            print(f"    Texto: '{link_text}'")
                            print(f"    Href: {link_href}")
                            print(f"    Clases: {link_class}")
                        except:
                            continue
                    
                    # Buscar elementos con texto
                    text_elements = target_element.find_elements(By.XPATH, ".//*[text()]")
                    print(f"\nElementos con texto: {len(text_elements)}")
                    for i, elem in enumerate(text_elements[:10]):  # Solo los primeros 10
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 3:
                                tag = elem.tag_name
                                classes = elem.get_attribute("class")
                                print(f"  Elemento {i+1} ({tag}): '{text}' (clases: {classes})")
                        except:
                            continue
                    
                    # Buscar elementos específicos
                    print("\n🎯 ELEMENTOS ESPECÍFICOS:")
                    print("=" * 50)
                    
                    # Buscar títulos
                    titles = target_element.find_elements(By.XPATH, ".//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6 | .//strong | .//b")
                    print(f"Elementos de título: {len(titles)}")
                    for i, title in enumerate(titles):
                        try:
                            text = title.text.strip()
                            if text:
                                print(f"  Título {i+1}: '{text}'")
                        except:
                            continue
                    
                    # Buscar números (posibles IDs)
                    import re
                    text_content = target_element.text
                    numbers = re.findall(r'\d{6,}', text_content)
                    print(f"Números largos encontrados: {numbers}")
                    
                    # Buscar elementos con clases específicas
                    specific_classes = ["title", "titulo", "id", "numero", "registro", "fecha"]
                    for class_name in specific_classes:
                        elements = target_element.find_elements(By.CSS_SELECTOR, f"[class*='{class_name}']")
                        if elements:
                            print(f"Elementos con clase '{class_name}': {len(elements)}")
                            for i, elem in enumerate(elements[:3]):
                                try:
                                    text = elem.text.strip()
                                    if text:
                                        print(f"  {class_name} {i+1}: '{text}'")
                                except:
                                    continue
                    
                else:
                    print("❌ No se encontró ningún elemento de resultado")
                
            else:
                print("❌ No se encontró botón de búsqueda")
        else:
            print("❌ No se encontró campo de búsqueda")
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_single_result() 