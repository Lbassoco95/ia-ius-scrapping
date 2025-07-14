#!/usr/bin/env python3
"""
Script mejorado de Selenium para la página de búsqueda de la SCJN
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

def test_improved_selenium_scjn():
    """Probar acceso mejorado a la página de la SCJN con Selenium"""
    
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
        print("🚀 Iniciando Selenium mejorado para la SCJN...")
        print(f"URL: {url}")
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navegar a la página
        print("📄 Cargando página...")
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        print("⏳ Esperando a que la página cargue...")
        time.sleep(15)  # Esperar más tiempo para que Angular cargue
        
        # Buscar el campo de búsqueda usando el selector correcto
        print("🔍 Buscando campo de búsqueda...")
        search_input = driver.find_element(By.CSS_SELECTOR, "input[name='search']")
        print(f"✅ Campo de búsqueda encontrado: {search_input.get_attribute('placeholder')}")
        
        # Escribir en el campo de búsqueda
        search_term = "derecho constitucional"
        search_input.clear()
        search_input.send_keys(search_term)
        print(f"✅ Texto ingresado: '{search_term}'")
        
        # Buscar el botón de búsqueda usando el selector correcto
        print("🔍 Buscando botón de búsqueda...")
        search_button = driver.find_element(By.CSS_SELECTOR, "button.sjf-button-search")
        print(f"✅ Botón de búsqueda encontrado: {search_button.text}")
        
        # Hacer clic en el botón de búsqueda
        search_button.click()
        print("✅ Búsqueda ejecutada")
        
        # Esperar a que se carguen los resultados
        print("⏳ Esperando resultados...")
        time.sleep(10)
        
        # Buscar resultados
        print("🔍 Buscando resultados...")
        
        # Buscar elementos que puedan ser resultados de tesis
        possible_results = driver.find_elements(By.CSS_SELECTOR, ".list-group-item, .resultado, .tesis-item, .item")
        print(f"📋 Posibles resultados encontrados: {len(possible_results)}")
        
        # Buscar enlaces que contengan "tesis"
        tesis_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'tesis') or contains(text(), 'tesis')]")
        print(f"🔗 Enlaces de tesis encontrados: {len(tesis_links)}")
        
        # Buscar tablas que puedan contener resultados
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        # Buscar elementos con texto relacionado a tesis
        tesis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'tesis') or contains(text(), 'Tesis')]")
        print(f"📋 Elementos con 'tesis': {len(tesis_elements)}")
        
        # Mostrar algunos ejemplos de resultados
        if possible_results:
            print("\n📋 Ejemplos de posibles resultados:")
            for i, result in enumerate(possible_results[:3]):
                text = result.text[:100] if result.text else "Sin texto"
                print(f"  {i+1}. {text}...")
        
        if tesis_links:
            print("\n🔗 Ejemplos de enlaces de tesis:")
            for i, link in enumerate(tesis_links[:3]):
                href = link.get_attribute('href') or "Sin href"
                text = link.text[:50] if link.text else "Sin texto"
                print(f"  {i+1}. {text} - {href}")
        
        # Guardar el HTML final
        html_content = driver.page_source
        with open('data/scjn_improved_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 HTML mejorado guardado en: data/scjn_improved_analysis.html")
        
        # Intentar extraer información de resultados si los hay
        if possible_results:
            print("\n📊 Intentando extraer información de resultados...")
            
            extracted_data = []
            for i, result in enumerate(possible_results[:5]):  # Solo los primeros 5
                try:
                    # Buscar título
                    title_element = result.find_element(By.CSS_SELECTOR, ".block-with-text, .list-item-text, h3, h4, strong")
                    title = title_element.text if title_element else "Sin título"
                    
                    # Buscar enlace
                    link_element = result.find_element(By.TAG_NAME, "a")
                    link = link_element.get_attribute('href') if link_element else None
                    
                    # Buscar texto adicional
                    text_elements = result.find_elements(By.CSS_SELECTOR, "p, span, div")
                    additional_text = " ".join([elem.text for elem in text_elements if elem.text and elem.text != title])[:200]
                    
                    extracted_data.append({
                        'index': i + 1,
                        'title': title,
                        'link': link,
                        'additional_text': additional_text
                    })
                    
                except Exception as e:
                    print(f"  ❌ Error extrayendo resultado {i+1}: {e}")
                    continue
            
            if extracted_data:
                print("\n📋 Datos extraídos:")
                for item in extracted_data:
                    print(f"  {item['index']}. {item['title']}")
                    if item['link']:
                        print(f"     Enlace: {item['link']}")
                    if item['additional_text']:
                        print(f"     Texto: {item['additional_text'][:100]}...")
                    print()
                
                # Guardar datos extraídos
                with open('data/extracted_results.json', 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                print("💾 Datos extraídos guardados en: data/extracted_results.json")
        
        # Cerrar driver
        driver.quit()
        print("✅ Driver cerrado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Selenium mejorado: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    test_improved_selenium_scjn() 