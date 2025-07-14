#!/usr/bin/env python3
"""
Script para analizar la estructura de la página de la SCJN
y encontrar los selectores correctos para el scraping
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def analyze_page_structure():
    """Analizar la estructura de la página de la SCJN"""
    
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
        print("🔍 Analizando página de la SCJN...")
        
        # Navegar a la página
        url = "https://www.scjn.gob.mx/consultas/jurisprudencia"
        driver.get(url)
        time.sleep(5)
        
        print(f"📄 Título de la página: {driver.title}")
        print(f"🌐 URL actual: {driver.current_url}")
        
        # Analizar elementos de búsqueda
        print("\n🔍 ANALIZANDO ELEMENTOS DE BÚSQUEDA:")
        print("=" * 50)
        
        # Buscar campos de entrada
        input_elements = driver.find_elements(By.TAG_NAME, "input")
        print(f"Encontrados {len(input_elements)} elementos input:")
        for i, elem in enumerate(input_elements[:10]):  # Mostrar solo los primeros 10
            try:
                input_type = elem.get_attribute("type")
                input_name = elem.get_attribute("name")
                input_id = elem.get_attribute("id")
                input_class = elem.get_attribute("class")
                input_placeholder = elem.get_attribute("placeholder")
                
                print(f"  Input {i+1}:")
                print(f"    Tipo: {input_type}")
                print(f"    Name: {input_name}")
                print(f"    ID: {input_id}")
                print(f"    Class: {input_class}")
                print(f"    Placeholder: {input_placeholder}")
                print()
            except:
                continue
        
        # Buscar botones
        print("\n🔘 ANALIZANDO BOTONES:")
        print("=" * 50)
        
        button_elements = driver.find_elements(By.TAG_NAME, "button")
        print(f"Encontrados {len(button_elements)} elementos button:")
        for i, elem in enumerate(button_elements[:10]):  # Mostrar solo los primeros 10
            try:
                button_text = elem.text.strip()
                button_type = elem.get_attribute("type")
                button_class = elem.get_attribute("class")
                button_id = elem.get_attribute("id")
                
                if button_text or button_class or button_id:
                    print(f"  Botón {i+1}:")
                    print(f"    Texto: '{button_text}'")
                    print(f"    Tipo: {button_type}")
                    print(f"    Class: {button_class}")
                    print(f"    ID: {button_id}")
                    print()
            except:
                continue
        
        # Buscar enlaces
        print("\n🔗 ANALIZANDO ENLACES:")
        print("=" * 50)
        
        link_elements = driver.find_elements(By.TAG_NAME, "a")
        print(f"Encontrados {len(link_elements)} elementos a:")
        for i, elem in enumerate(link_elements[:15]):  # Mostrar solo los primeros 15
            try:
                link_text = elem.text.strip()
                link_href = elem.get_attribute("href")
                link_class = elem.get_attribute("class")
                
                if link_text and link_href:
                    print(f"  Enlace {i+1}:")
                    print(f"    Texto: '{link_text}'")
                    print(f"    Href: {link_href}")
                    print(f"    Class: {link_class}")
                    print()
            except:
                continue
        
        # Buscar elementos con clases específicas
        print("\n📋 ANALIZANDO ELEMENTOS CON CLASES ESPECÍFICAS:")
        print("=" * 50)
        
        # Buscar elementos que podrían contener resultados
        potential_selectors = [
            ".resultado", ".result", ".tesis", ".jurisprudencia",
            ".item", ".elemento", ".contenido", ".lista",
            "[class*='result']", "[class*='tesis']", "[class*='item']"
        ]
        
        for selector in potential_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Selector '{selector}': {len(elements)} elementos encontrados")
                    for i, elem in enumerate(elements[:3]):  # Mostrar solo los primeros 3
                        try:
                            text = elem.text.strip()[:100]  # Primeros 100 caracteres
                            print(f"  Elemento {i+1}: {text}...")
                        except:
                            continue
                    print()
            except:
                continue
        
        # Analizar estructura general
        print("\n🏗️ ESTRUCTURA GENERAL DE LA PÁGINA:")
        print("=" * 50)
        
        # Buscar contenedores principales
        main_containers = driver.find_elements(By.CSS_SELECTOR, "main, .main, #main, .container, .content")
        print(f"Contenedores principales encontrados: {len(main_containers)}")
        
        # Buscar formularios
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Formularios encontrados: {len(forms)}")
        for i, form in enumerate(forms):
            try:
                form_action = form.get_attribute("action")
                form_method = form.get_attribute("method")
                print(f"  Formulario {i+1}: action='{form_action}', method='{form_method}'")
            except:
                continue
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_page_structure() 