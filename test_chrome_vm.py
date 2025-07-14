#!/usr/bin/env python3
"""
🧪 Prueba Simple de Chrome en la VM
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def test_chrome():
    """Prueba básica de Chrome"""
    print("🧪 PRUEBA DE CHROME EN LA VM")
    print("=" * 40)
    
    try:
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Sin interfaz gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        print("1️⃣ Configurando Chrome...")
        service = Service("/usr/local/bin/chromedriver")
        
        print("2️⃣ Inicializando driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Driver inicializado")
        
        print("3️⃣ Navegando a Google...")
        driver.get("https://www.google.com")
        print("✅ Navegación exitosa")
        
        print(f"📄 Título: {driver.title}")
        
        print("4️⃣ Navegando a SCJN...")
        driver.get("https://www.scjn.gob.mx")
        print("✅ Navegación a SCJN exitosa")
        
        print(f"📄 Título: {driver.title}")
        
        print("\n🎉 ¡Prueba completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        try:
            driver.quit()
            print("🔒 Driver cerrado")
        except:
            pass

if __name__ == "__main__":
    test_chrome() 