#!/usr/bin/env python3
"""
Script de debug para capturar la página después de hacer click en "Ver todo"
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

def debug_search_flow():
    """Debug del flujo de búsqueda completo"""
    
    print("🔍 === DEBUG DEL FLUJO DE BÚSQUEDA ===")
    
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
        
        # 1. Buscar campo de búsqueda
        print("\n1️⃣ Buscando campo de búsqueda...")
        search_input = None
        search_selectors = [
            "input[type='text']",
            "input[placeholder*='Escriba el tema']",
            "input.form-control.sjf-input-search"
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
        
        if not search_input:
            print("❌ No se encontró campo de búsqueda")
            return False
        
        # 2. Escribir término de búsqueda
        print("\n2️⃣ Escribiendo término de búsqueda...")
        search_input.clear()
        search_input.send_keys("amparo")
        print("✅ Texto escrito: 'amparo'")
        
        # 3. Buscar botón de búsqueda
        print("\n3️⃣ Buscando botón de búsqueda...")
        search_button = None
        button_selectors = [
            "button.btn.sjf-button-search",
            "button[class*='btn']",
            "button:contains('Ver todo')",
            "#button-addon1_add"
        ]
        
        for selector in button_selectors:
            try:
                elements = scraper.driver.find_elements("css selector", selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        button_text = elem.text.strip()
                        if "Ver todo" in button_text or "Buscar" in button_text:
                            search_button = elem
                            print(f"✅ Botón encontrado: '{button_text}' con selector: {selector}")
                            break
                if search_button:
                    break
            except:
                continue
        
        if not search_button:
            print("❌ No se encontró botón de búsqueda")
            return False
        
        # 4. Hacer click en el botón
        print("\n4️⃣ Haciendo click en botón de búsqueda...")
        search_button.click()
        print("✅ Click realizado")
        
        # 5. Esperar resultados
        print("\n5️⃣ Esperando resultados...")
        time.sleep(8)  # Esperar más tiempo
        
        # 6. Analizar página después de la búsqueda
        print("\n6️⃣ Analizando página después de la búsqueda...")
        
        # Obtener URL actual
        current_url = scraper.driver.current_url
        print(f"🌐 URL actual: {current_url}")
        
        # Buscar elementos de resultado
        result_selectors = [
            ".list-group-item",
            ".item",
            ".result",
            "tr",
            ".row",
            ".col",
            ".card"
        ]
        
        for selector in result_selectors:
            elements = scraper.driver.find_elements("css selector", selector)
            if elements:
                print(f"📋 Elementos '{selector}': {len(elements)}")
                
                # Mostrar contenido de los primeros elementos
                for i, elem in enumerate(elements[:3]):
                    try:
                        text = elem.text.strip()
                        if text:
                            print(f"  Elemento {i+1}: {text[:100]}...")
                    except:
                        continue
        
        # 7. Buscar enlaces específicos
        print("\n7️⃣ Buscando enlaces específicos...")
        
        # Buscar enlaces que contengan "detalle" o "tesis"
        links = scraper.driver.find_elements("tag name", "a")
        detail_links = []
        
        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and ("detalle" in href.lower() or "tesis" in href.lower()):
                    detail_links.append((text, href))
            except:
                continue
        
        print(f"🔗 Enlaces de detalle encontrados: {len(detail_links)}")
        for text, href in detail_links[:5]:
            print(f"  📄 '{text}' -> {href}")
        
        # 8. Guardar HTML de la página
        print("\n8️⃣ Guardando HTML de la página...")
        page_source = scraper.driver.page_source
        
        # Guardar HTML para análisis
        with open("logs/debug_search_results.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("✅ HTML guardado en logs/debug_search_results.html")
        
        # 9. Buscar patrones específicos
        print("\n9️⃣ Analizando patrones en HTML...")
        
        patterns = [
            "detalle/tesis",
            "tesis/",
            "tesis",
            "amparo",
            "constitucional",
            "list-group-item",
            "button-addon1_add"
        ]
        
        for pattern in patterns:
            count = page_source.lower().count(pattern.lower())
            print(f"  Patrón '{pattern}': {count} ocurrencias")
        
        print("\n✅ Debug completado")
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
    finally:
        scraper.close_driver()
    
    return True

def main():
    """Función principal"""
    success = debug_search_flow()
    
    if success:
        print("\n📋 Resumen del debug:")
        print("✅ Se ejecutó el flujo completo de búsqueda")
        print("✅ Se capturó la página después de la búsqueda")
        print("✅ Se guardó el HTML para análisis")
        print("📁 Revisa logs/debug_search_results.html para más detalles")
    else:
        print("\n❌ Error en el debug")

if __name__ == "__main__":
    main() 