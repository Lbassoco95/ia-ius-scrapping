#!/usr/bin/env python3
"""
Script de prueba usando Selenium para la página de búsqueda de la SCJN
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def test_selenium_scjn():
    """Probar acceso a la página de la SCJN con Selenium"""
    
    url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        print("🚀 Iniciando Selenium para la SCJN...")
        print(f"URL: {url}")
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navegar a la página
        print("📄 Cargando página...")
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        print("⏳ Esperando a que la página cargue...")
        time.sleep(10)  # Esperar 10 segundos para que Angular cargue
        
        # Verificar si hay elementos de búsqueda
        print("🔍 Buscando elementos de la página...")
        
        # Buscar formularios de búsqueda
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"📝 Formularios encontrados: {len(forms)}")
        
        # Buscar campos de entrada
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"⌨️ Campos de entrada encontrados: {len(inputs)}")
        
        for i, inp in enumerate(inputs[:5]):  # Mostrar solo los primeros 5
            input_type = inp.get_attribute("type")
            input_name = inp.get_attribute("name")
            input_id = inp.get_attribute("id")
            print(f"  {i+1}. Tipo: {input_type}, Nombre: {input_name}, ID: {input_id}")
        
        # Buscar botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Botones encontrados: {len(buttons)}")
        
        for i, btn in enumerate(buttons[:5]):  # Mostrar solo los primeros 5
            btn_text = btn.text
            btn_type = btn.get_attribute("type")
            print(f"  {i+1}. Texto: '{btn_text}', Tipo: {btn_type}")
        
        # Buscar enlaces
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"🔗 Enlaces encontrados: {len(links)}")
        
        # Buscar elementos con texto relacionado a tesis
        tesis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'tesis') or contains(text(), 'Tesis')]")
        print(f"📋 Elementos con 'tesis': {len(tesis_elements)}")
        
        # Buscar tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        # Buscar divs con clases específicas
        divs = driver.find_elements(By.TAG_NAME, "div")
        print(f"📦 Divs encontrados: {len(divs)}")
        
        # Guardar el HTML final
        html_content = driver.page_source
        with open('data/scjn_selenium_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 HTML con Selenium guardado en: data/scjn_selenium_analysis.html")
        
        # Intentar hacer una búsqueda simple
        print("\n🔍 Intentando hacer una búsqueda...")
        
        # Buscar campo de búsqueda
        search_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='search']")
        if search_inputs:
            print(f"✅ Campo de búsqueda encontrado: {len(search_inputs)}")
            
            # Intentar escribir en el primer campo de búsqueda
            try:
                search_inputs[0].clear()
                search_inputs[0].send_keys("derecho constitucional")
                print("✅ Texto ingresado en campo de búsqueda")
                
                # Buscar botón de búsqueda
                search_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Buscar') or contains(text(), 'Search')]")
                if search_buttons:
                    print("✅ Botón de búsqueda encontrado")
                    search_buttons[0].click()
                    print("✅ Búsqueda ejecutada")
                    
                    # Esperar resultados
                    time.sleep(5)
                    
                    # Buscar resultados
                    results = driver.find_elements(By.XPATH, "//*[contains(@class, 'result') or contains(@class, 'item') or contains(@class, 'row')]")
                    print(f"📋 Posibles resultados encontrados: {len(results)}")
                    
                else:
                    print("❌ No se encontró botón de búsqueda")
                    
            except Exception as e:
                print(f"❌ Error en búsqueda: {e}")
        else:
            print("❌ No se encontraron campos de búsqueda")
        
        # Cerrar driver
        driver.quit()
        print("✅ Driver cerrado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Selenium: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    test_selenium_scjn() 