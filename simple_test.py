#!/usr/bin/env python3
"""
Prueba simple para analizar la página de SCJN
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def simple_page_analysis():
    """Análisis simple de la página de SCJN"""
    print("🔍 ANÁLISIS SIMPLE DE LA PÁGINA SCJN")
    print("=" * 50)
    
    # Configurar driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navegar a la página
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        print(f"🌐 Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que cargue
        time.sleep(10)
        
        # Obtener información básica
        print(f"📄 Título: {driver.title}")
        print(f"🔗 URL actual: {driver.current_url}")
        
        # Verificar si hay mensaje de navegador desactualizado
        try:
            outdated = driver.find_element(By.ID, "jhipster-error")
            if outdated.is_displayed():
                print("⚠️ Página detecta navegador desactualizado")
                print("📝 Contenido del mensaje:")
                print(outdated.text)
        except:
            print("✅ No hay mensaje de navegador desactualizado")
        
        # Buscar elementos básicos
        print("\n🔍 Buscando elementos básicos...")
        
        # Buscar todos los enlaces
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"📎 Enlaces totales: {len(links)}")
        
        # Mostrar primeros enlaces
        for i, link in enumerate(links[:10]):
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and text:
                print(f"   {i+1}. {text[:50]}... -> {href}")
        
        # Buscar elementos con texto que contenga "tesis"
        page_text = driver.page_source.lower()
        if "tesis" in page_text:
            print("\n✅ La palabra 'tesis' aparece en la página")
        else:
            print("\n❌ La palabra 'tesis' NO aparece en la página")
        
        # Buscar formularios
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"\n📝 Formularios encontrados: {len(forms)}")
        
        # Buscar inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"⌨️ Inputs encontrados: {len(inputs)}")
        for inp in inputs:
            input_type = inp.get_attribute("type")
            input_name = inp.get_attribute("name")
            input_placeholder = inp.get_attribute("placeholder")
            print(f"   - Tipo: {input_type}, Nombre: {input_name}, Placeholder: {input_placeholder}")
        
        # Buscar botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Botones encontrados: {len(buttons)}")
        for btn in buttons:
            btn_text = btn.text.strip()
            btn_type = btn.get_attribute("type")
            if btn_text:
                print(f"   - {btn_text} (tipo: {btn_type})")
        
        # Guardar HTML para análisis
        with open("data/simple_analysis.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"\n💾 HTML guardado en: data/simple_analysis.html")
        
        # Verificar si es una SPA (Single Page Application)
        if "angular" in page_text or "react" in page_text or "vue" in page_text:
            print("🔄 Parece ser una aplicación de página única (SPA)")
        
        # Buscar scripts
        scripts = driver.find_elements(By.TAG_NAME, "script")
        print(f"📜 Scripts encontrados: {len(scripts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    simple_page_analysis() 