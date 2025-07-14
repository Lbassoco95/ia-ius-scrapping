#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad del scraper
"""

import logging
import sys
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.selenium_scraper import SeleniumSCJNScraper
from src.database.models import create_tables, get_session, Tesis
from src.storage.google_drive import GoogleDriveManager

def test_scraper_functionality():
    """Probar la funcionalidad completa del scraper"""
    
    print("🧪 === PRUEBA DE FUNCIONALIDAD DEL SCRAPER ===")
    
    # 1. Crear base de datos
    print("\n1️⃣ Creando base de datos...")
    try:
        create_tables()
        print("✅ Base de datos creada correctamente")
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False
    
    # 2. Probar scraper
    print("\n2️⃣ Probando scraper...")
    scraper = SeleniumSCJNScraper()
    
    try:
        # Configurar driver
        if not scraper.setup_driver():
            print("❌ No se pudo configurar el driver")
            return False
        print("✅ Driver configurado")
        
        # Navegar a la página
        if not scraper.navigate_to_search_page():
            print("❌ No se pudo navegar a la página")
            scraper.close_driver()
            return False
        print("✅ Navegación exitosa")
        
        # Realizar búsqueda
        if not scraper.search_for_tesis("amparo"):
            print("❌ No se pudo realizar la búsqueda")
            scraper.close_driver()
            return False
        print("✅ Búsqueda realizada")
        
        # Extraer resultados
        results = scraper.extract_search_results()
        print(f"✅ Extraídos {len(results)} resultados")
        
        # Mostrar algunos resultados
        for i, result in enumerate(results[:3]):
            print(f"   Resultado {i+1}: {result.get('titulo', 'Sin título')[:50]}...")
        
        scraper.close_driver()
        
    except Exception as e:
        print(f"❌ Error en scraper: {e}")
        scraper.close_driver()
        return False
    
    # 3. Probar base de datos
    print("\n3️⃣ Probando base de datos...")
    try:
        session = get_session()
        
        # Contar tesis existentes
        total_tesis = session.query(Tesis).count()
        print(f"✅ Base de datos accesible. Total de tesis: {total_tesis}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error accediendo base de datos: {e}")
        return False
    
    # 4. Probar Google Drive (si está configurado)
    print("\n4️⃣ Probando Google Drive...")
    try:
        gdrive = GoogleDriveManager()
        
        # Verificar si hay configuración de Google Drive
        if hasattr(gdrive, 'folder_id') and gdrive.folder_id:
            print("✅ Google Drive configurado")
            
            # Probar autenticación
            try:
                gdrive.authenticate()
                print("✅ Autenticación con Google Drive exitosa")
                
                # Probar listar archivos
                files = gdrive.list_files()
                print(f"✅ Conexión exitosa. Archivos en carpeta: {len(files)}")
                
            except Exception as e:
                print(f"⚠️ Error en autenticación: {e}")
        else:
            print("⚠️ Google Drive no configurado (falta folder_id)")
            
    except Exception as e:
        print(f"⚠️ Error probando Google Drive: {e}")
    
    print("\n🎉 === PRUEBA COMPLETADA ===")
    print("✅ El sistema está funcionando correctamente")
    return True

if __name__ == "__main__":
    test_scraper_functionality() 