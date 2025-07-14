#!/usr/bin/env python3
"""
Script para analizar la estructura de la página de la SCJN
y entender por qué no se encuentran resultados
"""

import logging
import sys
import os
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.selenium_scraper import SeleniumSCJNScraper

def analyze_page_structure():
    """Analizar la estructura de la página de la SCJN"""
    
    print("🔍 === ANÁLISIS DE LA PÁGINA DE LA SCJN ===")
    
    scraper = SeleniumSCJNScraper()
    
    try:
        # Configurar driver
        if not scraper.setup_driver():
            print("❌ No se pudo configurar el driver")
            return False
        
        # Navegar a la página
        if not scraper.navigate_to_search_page():
            print("❌ No se pudo navegar a la página")
            scraper.close_driver()
            return False
        
        print("✅ Página cargada correctamente")
        
        # Analizar estructura de la página
        print("\n📋 Analizando estructura de la página...")
        
        # Obtener título de la página
        page_title = scraper.driver.title
        print(f"📄 Título de la página: {page_title}")
        
        # Obtener URL actual
        current_url = scraper.driver.current_url
        print(f"🌐 URL actual: {current_url}")
        
        # Buscar elementos de búsqueda
        print("\n🔍 Analizando elementos de búsqueda...")
        
        # Buscar campos de entrada
        input_elements = scraper.driver.find_elements("tag name", "input")
        print(f"📝 Campos de entrada encontrados: {len(input_elements)}")
        
        for i, elem in enumerate(input_elements[:5]):  # Mostrar solo los primeros 5
            try:
                input_type = elem.get_attribute("type")
                input_placeholder = elem.get_attribute("placeholder")
                input_id = elem.get_attribute("id")
                input_class = elem.get_attribute("class")
                print(f"  Input {i+1}: type={input_type}, placeholder='{input_placeholder}', id='{input_id}', class='{input_class}'")
            except:
                continue
        
        # Buscar botones
        button_elements = scraper.driver.find_elements("tag name", "button")
        print(f"\n🔘 Botones encontrados: {len(button_elements)}")
        
        for i, elem in enumerate(button_elements[:5]):  # Mostrar solo los primeros 5
            try:
                button_text = elem.text
                button_id = elem.get_attribute("id")
                button_class = elem.get_attribute("class")
                print(f"  Botón {i+1}: text='{button_text}', id='{button_id}', class='{button_class}'")
            except:
                continue
        
        # Buscar enlaces
        link_elements = scraper.driver.find_elements("tag name", "a")
        print(f"\n🔗 Enlaces encontrados: {len(link_elements)}")
        
        # Filtrar enlaces que contengan "tesis"
        tesis_links = []
        for elem in link_elements:
            try:
                href = elem.get_attribute("href")
                text = elem.text
                if href and ("tesis" in href.lower() or "tesis" in text.lower()):
                    tesis_links.append((text, href))
            except:
                continue
        
        print(f"📚 Enlaces relacionados con tesis: {len(tesis_links)}")
        for text, href in tesis_links[:10]:  # Mostrar solo los primeros 10
            print(f"  📄 '{text}' -> {href}")
        
        # Buscar elementos con clases específicas
        print("\n🎨 Analizando clases CSS...")
        
        # Buscar elementos con clase "list-group-item"
        list_items = scraper.driver.find_elements("css selector", ".list-group-item")
        print(f"📋 Elementos .list-group-item: {len(list_items)}")
        
        # Buscar elementos con clase "item"
        items = scraper.driver.find_elements("css selector", ".item")
        print(f"📋 Elementos .item: {len(items)}")
        
        # Buscar elementos con clase "result"
        results = scraper.driver.find_elements("css selector", ".result")
        print(f"📋 Elementos .result: {len(results)}")
        
        # Buscar tablas
        tables = scraper.driver.find_elements("tag name", "table")
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        # Buscar filas de tabla
        rows = scraper.driver.find_elements("tag name", "tr")
        print(f"📊 Filas de tabla: {len(rows)}")
        
        # Intentar hacer una búsqueda manual
        print("\n🔍 Intentando búsqueda manual...")
        
        # Buscar campo de búsqueda
        search_input = None
        search_selectors = [
            "input[type='text']",
            "input[type='search']",
            "input[placeholder*='buscar']",
            "input[placeholder*='Buscar']",
            "input[placeholder*='tesis']",
            "input[placeholder*='Tesis']",
            "#search",
            ".search-input",
            "input.form-control"
        ]
        
        for selector in search_selectors:
            try:
                elements = scraper.driver.find_elements("css selector", selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        search_input = elem
                        print(f"✅ Campo de búsqueda encontrado con selector: {selector}")
                        break
                if search_input:
                    break
            except:
                continue
        
        if search_input:
            # Intentar escribir en el campo
            try:
                search_input.clear()
                search_input.send_keys("amparo")
                print("✅ Texto escrito en campo de búsqueda")
                
                # Buscar botón de búsqueda
                search_button = None
                button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Buscar')",
                    "button:contains('buscar')",
                    ".search-button",
                    "#search-button",
                    "button.btn"
                ]
                
                for selector in button_selectors:
                    try:
                        elements = scraper.driver.find_elements("css selector", selector)
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                search_button = elem
                                print(f"✅ Botón de búsqueda encontrado con selector: {selector}")
                                break
                        if search_button:
                            break
                    except:
                        continue
                
                if search_button:
                    # Hacer click en el botón
                    search_button.click()
                    print("✅ Botón de búsqueda clickeado")
                    
                    # Esperar resultados
                    time.sleep(5)
                    
                    # Analizar página después de la búsqueda
                    print("\n📊 Analizando resultados de búsqueda...")
                    
                    # Buscar elementos de resultado
                    result_elements = scraper.driver.find_elements("css selector", ".list-group-item")
                    print(f"📋 Elementos .list-group-item después de búsqueda: {len(result_elements)}")
                    
                    # Mostrar contenido de los primeros elementos
                    for i, elem in enumerate(result_elements[:3]):
                        try:
                            text = elem.text
                            print(f"  Elemento {i+1}: {text[:100]}...")
                        except:
                            continue
                    
                else:
                    print("⚠️ No se encontró botón de búsqueda")
                    
            except Exception as e:
                print(f"❌ Error en búsqueda manual: {e}")
        else:
            print("⚠️ No se encontró campo de búsqueda")
        
        # Obtener HTML de la página para análisis
        print("\n📄 Obteniendo HTML de la página...")
        page_source = scraper.driver.page_source
        
        # Guardar HTML para análisis
        with open("logs/page_analysis.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("✅ HTML guardado en logs/page_analysis.html")
        
        # Buscar patrones específicos en el HTML
        print("\n🔍 Analizando patrones en HTML...")
        
        # Buscar patrones de tesis
        tesis_patterns = [
            "detalle/tesis",
            "tesis/",
            "tesis",
            "jurisprudencia",
            "amparo",
            "constitucional"
        ]
        
        for pattern in tesis_patterns:
            count = page_source.lower().count(pattern.lower())
            print(f"  Patrón '{pattern}': {count} ocurrencias")
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
    finally:
        scraper.close_driver()
    
    return True

def main():
    """Función principal"""
    success = analyze_page_structure()
    
    if success:
        print("\n📋 Resumen del análisis:")
        print("✅ Se analizó la estructura de la página")
        print("✅ Se identificaron elementos de búsqueda")
        print("✅ Se guardó el HTML para análisis detallado")
        print("📁 Revisa logs/page_analysis.html para más detalles")
    else:
        print("\n❌ Error en el análisis")

if __name__ == "__main__":
    main() 