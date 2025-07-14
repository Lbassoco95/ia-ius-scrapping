#!/usr/bin/env python3
"""
Script de prueba usando Selenium para el scraping de SCJN
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from src.scraper.selenium_scraper import SeleniumSCJNScraper

def test_selenium_scraping():
    """Probar scraping con Selenium"""
    print("🧪 INICIANDO PRUEBA CON SELENIUM")
    print("=" * 50)
    
    scraper = SeleniumSCJNScraper()
    
    try:
        # 1. Configurar driver
        print("1️⃣ Configurando driver de Chrome...")
        if not scraper.setup_driver():
            print("❌ No se pudo configurar el driver")
            return False
        print("✅ Driver configurado")
        
        # 2. Navegar a la página
        print("\n2️⃣ Navegando a la página de SCJN...")
        if not scraper.navigate_to_search_page():
            print("❌ No se pudo navegar a la página")
            return False
        print("✅ Navegación exitosa")
        
        # 3. Realizar búsqueda
        print("\n3️⃣ Realizando búsqueda...")
        if not scraper.search_for_tesis():
            print("⚠️ No se pudo realizar búsqueda, continuando...")
        
        # 4. Extraer resultados
        print("\n4️⃣ Extrayendo resultados...")
        results = scraper.extract_search_results()
        
        if not results:
            print("❌ No se encontraron resultados")
            return False
        
        print(f"✅ Encontrados {len(results)} resultados")
        
        # 5. Mostrar resultados
        print("\n5️⃣ Primeros resultados:")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. ID: {result.get('scjn_id', 'N/A')}")
            print(f"      Título: {result.get('titulo', 'Sin título')[:80]}...")
            print(f"      URL: {result.get('url', 'N/A')}")
            print()
        
        # 6. Probar obtención de detalles (solo el primero)
        if results:
            print("6️⃣ Probando obtención de detalles...")
            first_result = results[0]
            detail_data = scraper.get_tesis_detail(first_result['url'])
            
            if detail_data:
                print("✅ Detalles obtenidos correctamente")
                print(f"   - Rubro: {detail_data.get('rubro', 'N/A')[:80]}...")
                print(f"   - Texto: {detail_data.get('texto', 'N/A')[:80]}...")
                print(f"   - PDF URL: {detail_data.get('pdf_url', 'No disponible')}")
            else:
                print("⚠️ No se pudieron obtener detalles")
        
        # 7. Guardar resultados
        print("\n7️⃣ Guardando resultados...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = scraper.save_results(results, f'data/selenium_test_results_{timestamp}.json')
        print(f"✅ Resultados guardados en: {filename}")
        
        print("\n🎉 ¡PRUEBA CON SELENIUM COMPLETADA EXITOSAMENTE!")
        print("=" * 50)
        print("✅ El sistema con Selenium está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    success = test_selenium_scraping()
    sys.exit(0 if success else 1) 