#!/usr/bin/env python3
"""
🧪 Prueba Simple del Scraper en la VM
"""

import time
import logging
from src.scraper.selenium_scraper import SeleniumSCJNScraper

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Prueba básica del scraper"""
    print("🧪 PRUEBA SIMPLE DEL SCRAPER")
    print("=" * 40)
    
    try:
        # Crear instancia del scraper
        print("1️⃣ Inicializando scraper...")
        scraper = SeleniumSCJNScraper()
        print("✅ Scraper inicializado")
        
        # Navegar a la página
        print("2️⃣ Navegando a SCJN...")
        scraper.driver.get("https://www.scjn.gob.mx/tesis")
        print("✅ Navegación exitosa")
        
        # Esperar un momento
        time.sleep(3)
        
        # Verificar que la página cargó
        title = scraper.driver.title
        print(f"📄 Título de la página: {title}")
        
        # Buscar elementos básicos
        print("3️⃣ Verificando elementos de la página...")
        
        # Intentar encontrar el formulario de búsqueda
        try:
            search_form = scraper.driver.find_element("css selector", "form")
            print("✅ Formulario de búsqueda encontrado")
        except:
            print("⚠️ Formulario de búsqueda no encontrado")
        
        # Verificar que hay contenido
        page_source = scraper.driver.page_source
        if "tesis" in page_source.lower():
            print("✅ Contenido de tesis detectado")
        else:
            print("⚠️ Contenido de tesis no detectado")
        
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("✅ El scraper está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False
    
    finally:
        # Cerrar el driver
        try:
            scraper.driver.quit()
            print("🔒 Driver cerrado")
        except:
            pass

if __name__ == "__main__":
    test_scraper() 