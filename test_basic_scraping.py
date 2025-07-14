#!/usr/bin/env python3
"""
Script de prueba básica del sistema de scraping SCJN
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from src.scraper.scraper import SCJNScraper
from src.database.models import get_session, Tesis

def test_basic_scraping():
    """Probar scraping básico sin APIs externas"""
    print("🧪 INICIANDO PRUEBA BÁSICA DE SCRAPING")
    print("=" * 50)
    
    try:
        # 1. Inicializar scraper
        print("1️⃣ Inicializando scraper...")
        scraper = SCJNScraper()
        print("✅ Scraper inicializado")
        
        # 2. Obtener página de búsqueda
        print("\n2️⃣ Obteniendo página de búsqueda...")
        html_content = scraper.get_search_page(page=1)
        
        if not html_content:
            print("❌ No se pudo obtener la página de búsqueda")
            return False
        
        print(f"✅ Página obtenida - {len(html_content)} caracteres")
        
        # 3. Parsear resultados
        print("\n3️⃣ Parseando resultados...")
        results = scraper.parse_search_results(html_content)
        
        if not results:
            print("❌ No se encontraron resultados en la página")
            return False
        
        print(f"✅ Encontrados {len(results)} resultados")
        
        # 4. Mostrar primeros resultados
        print("\n4️⃣ Primeros resultados encontrados:")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. ID: {result.get('scjn_id', 'N/A')}")
            print(f"      Título: {result.get('titulo', 'Sin título')[:100]}...")
            print(f"      URL: {result.get('url', 'N/A')}")
            print()
        
        # 5. Probar obtención de detalles (solo el primero)
        if results:
            print("5️⃣ Probando obtención de detalles...")
            first_result = results[0]
            detail_data = scraper.get_tesis_detail(first_result['url'])
            
            if detail_data:
                print("✅ Detalles obtenidos correctamente")
                print(f"   - Rubro: {detail_data.get('rubro', 'N/A')[:100]}...")
                print(f"   - Texto: {detail_data.get('texto', 'N/A')[:100]}...")
                print(f"   - PDF URL: {detail_data.get('pdf_url', 'No disponible')}")
            else:
                print("⚠️ No se pudieron obtener detalles")
        
        # 6. Guardar resultados en archivo
        print("\n6️⃣ Guardando resultados...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/test_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Resultados guardados en: {filename}")
        
        # 7. Verificar base de datos
        print("\n7️⃣ Verificando base de datos...")
        session = get_session()
        total_tesis = session.query(Tesis).count()
        session.close()
        
        print(f"✅ Base de datos accesible - Tesis actuales: {total_tesis}")
        
        print("\n🎉 ¡PRUEBA BÁSICA COMPLETADA EXITOSAMENTE!")
        print("=" * 50)
        print("✅ El sistema básico está funcionando correctamente")
        print("✅ Puedes proceder a configurar las APIs para funcionalidad completa")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_scraping()
    sys.exit(0 if success else 1) 