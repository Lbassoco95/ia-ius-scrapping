#!/usr/bin/env python3
"""
Script para encontrar la URL correcta de las tesis de la SCJN
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def find_tesis_url():
    """Encontrar la URL correcta de las tesis"""
    
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
        print("🔍 Buscando la URL correcta de las tesis...")
        
        # Probar diferentes URLs posibles
        possible_urls = [
            "https://www.scjn.gob.mx/consultas/jurisprudencia",
            "https://www.scjn.gob.mx/consultas/jurisprudencia/tesis",
            "https://www.scjn.gob.mx/tesis",
            "https://www.scjn.gob.mx/consultas/tesis",
            "https://sjf2.scjn.gob.mx/busqueda-principal-tesis",
            "https://sjf2.scjn.gob.mx/tesis",
            "https://www.scjn.gob.mx/consultas/jurisprudencia/tesis-y-jurisprudencia"
        ]
        
        for url in possible_urls:
            print(f"\n🌐 Probando URL: {url}")
            try:
                driver.get(url)
                time.sleep(3)
                
                title = driver.title
                current_url = driver.current_url
                
                print(f"  Título: {title}")
                print(f"  URL final: {current_url}")
                
                # Buscar elementos relacionados con tesis
                tesis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'tesis') or contains(text(), 'Tesis')]")
                jurisprudencia_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'jurisprudencia') or contains(text(), 'Jurisprudencia')]")
                
                print(f"  Elementos con 'tesis': {len(tesis_elements)}")
                print(f"  Elementos con 'jurisprudencia': {len(jurisprudencia_elements)}")
                
                # Buscar enlaces que contengan "tesis"
                tesis_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'tesis') or contains(text(), 'tesis') or contains(text(), 'Tesis')]")
                print(f"  Enlaces relacionados con tesis: {len(tesis_links)}")
                
                for i, link in enumerate(tesis_links[:5]):  # Mostrar solo los primeros 5
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        if link_text or link_href:
                            print(f"    Enlace {i+1}: '{link_text}' -> {link_href}")
                    except:
                        continue
                
                # Si encontramos elementos relacionados con tesis, analizar más
                if len(tesis_elements) > 0 or len(tesis_links) > 0:
                    print(f"  ✅ Esta URL parece prometedora!")
                    
                    # Buscar formularios de búsqueda
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    print(f"  Formularios encontrados: {len(forms)}")
                    
                    # Buscar campos de entrada
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    print(f"  Campos de entrada: {len(inputs)}")
                    
                    # Buscar botones
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    print(f"  Botones: {len(buttons)}")
                    
                    # Si parece ser la página correcta, hacer una búsqueda de prueba
                    if len(inputs) > 0:
                        print("  🔍 Intentando búsqueda de prueba...")
                        try:
                            # Buscar un campo de entrada de texto
                            text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "search"]]
                            if text_inputs:
                                search_input = text_inputs[0]
                                search_input.clear()
                                search_input.send_keys("derecho")
                                time.sleep(2)
                                
                                # Buscar botón de búsqueda
                                search_buttons = [btn for btn in buttons if btn.get_attribute("type") == "submit" or "buscar" in btn.text.lower()]
                                if search_buttons:
                                    search_buttons[0].click()
                                    time.sleep(5)
                                    
                                    # Verificar si hay resultados
                                    results = driver.find_elements(By.XPATH, "//*[contains(@class, 'result') or contains(@class, 'item') or contains(@class, 'tesis')]")
                                    print(f"    Resultados encontrados: {len(results)}")
                                    
                                    if len(results) > 0:
                                        print(f"    ✅ ¡URL confirmada! Esta es la página correcta.")
                                        return url
                        except Exception as e:
                            print(f"    ❌ Error en búsqueda de prueba: {e}")
                
            except Exception as e:
                print(f"  ❌ Error accediendo a la URL: {e}")
                continue
        
        print("\n❌ No se encontró una URL definitiva para las tesis")
        return None
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return None
    
    finally:
        driver.quit()

if __name__ == "__main__":
    correct_url = find_tesis_url()
    if correct_url:
        print(f"\n🎯 URL correcta encontrada: {correct_url}")
    else:
        print("\n❌ No se pudo encontrar la URL correcta") 