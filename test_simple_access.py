#!/usr/bin/env python3
"""
Script simple para probar el acceso a la página de tesis
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def test_simple_access():
    """Probar acceso simple a la página"""
    
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
        print("🔍 Probando acceso simple...")
        
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        print(f"🌐 Accediendo a: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        print(f"📄 Título: {driver.title}")
        print(f"🌐 URL actual: {driver.current_url}")
        
        # Verificar si la página cargó correctamente
        if "tesis" in driver.title.lower() or "búsqueda" in driver.title.lower():
            print("✅ Página cargada correctamente")
            
            # Contar elementos básicos
            inputs = driver.find_elements("tag name", "input")
            buttons = driver.find_elements("tag name", "button")
            links = driver.find_elements("tag name", "a")
            
            print(f"📊 Elementos encontrados:")
            print(f"  - Inputs: {len(inputs)}")
            print(f"  - Botones: {len(buttons)}")
            print(f"  - Enlaces: {len(links)}")
            
            return True
        else:
            print("❌ Página no cargó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_simple_access()
    if success:
        print("\n✅ Prueba exitosa")
    else:
        print("\n❌ Prueba fallida") 