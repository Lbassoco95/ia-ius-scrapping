#!/usr/bin/env python3
"""
Script para analizar la estructura de los resultados de búsqueda
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def analyze_results_structure():
    """Analizar la estructura de los resultados"""
    
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
        print("🔍 Analizando estructura de resultados...")
        
        # Navegar a la página
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        driver.get(url)
        time.sleep(5)
        
        # Realizar búsqueda
        print("🔍 Realizando búsqueda...")
        
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
                time.sleep(5)
                
                print("📋 Analizando resultados...")
                
                # Buscar elementos que podrían ser resultados
                potential_selectors = [
                    ".item", "[class*='item']", ".result", "[class*='result']",
                    "tr", ".row", ".col", ".card", ".panel", ".list-group-item"
                ]
                
                for selector in potential_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"\n🔍 Selector '{selector}': {len(elements)} elementos")
                            
                            # Analizar los primeros 3 elementos
                            for i, elem in enumerate(elements[:3]):
                                try:
                                    text = elem.text.strip()
                                    if text and len(text) > 10:
                                        print(f"  Elemento {i+1}:")
                                        print(f"    Texto: {text[:200]}...")
                                        
                                        # Buscar enlaces dentro del elemento
                                        links = elem.find_elements(By.TAG_NAME, "a")
                                        if links:
                                            print(f"    Enlaces: {len(links)}")
                                            for j, link in enumerate(links[:3]):
                                                try:
                                                    link_text = link.text.strip()
                                                    link_href = link.get_attribute("href")
                                                    if link_text or link_href:
                                                        print(f"      Enlace {j+1}: '{link_text}' -> {link_href}")
                                                except:
                                                    continue
                                        
                                        # Buscar elementos con clases específicas
                                        classes = elem.get_attribute("class")
                                        if classes:
                                            print(f"    Clases: {classes}")
                                        
                                        print()
                                except Exception as e:
                                    print(f"    Error analizando elemento {i+1}: {e}")
                                    continue
                    except Exception as e:
                        print(f"Error con selector '{selector}': {e}")
                        continue
                
                # Buscar elementos específicos que podrían contener tesis
                print("\n🎯 BUSCANDO ELEMENTOS ESPECÍFICOS:")
                print("=" * 50)
                
                # Buscar elementos con texto que contenga "tesis"
                tesis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'tesis') or contains(text(), 'Tesis')]")
                print(f"Elementos con 'tesis': {len(tesis_elements)}")
                
                # Buscar elementos con texto que contenga números (posibles IDs)
                number_elements = driver.find_elements(By.XPATH, "//*[matches(text(), '\\d{6,}')]")
                print(f"Elementos con números largos (posibles IDs): {len(number_elements)}")
                
                # Buscar enlaces que contengan números
                number_links = driver.find_elements(By.XPATH, "//a[matches(@href, '\\d{6,}')]")
                print(f"Enlaces con números largos: {len(number_links)}")
                
                for i, link in enumerate(number_links[:5]):
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        print(f"  Enlace {i+1}: '{link_text}' -> {link_href}")
                    except:
                        continue
                
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
    analyze_results_structure() 