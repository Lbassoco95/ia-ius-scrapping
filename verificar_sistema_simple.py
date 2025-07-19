#!/usr/bin/env python3
"""
Verificación simple del sistema de scraping SCJN
- Prueba de configuración básica
- Prueba de base de datos
- Prueba de módulos principales
"""

import sys
import os
import time
from datetime import datetime

def test_basic_imports():
    """Probar imports básicos"""
    print("🔧 Probando imports básicos...")
    
    try:
        import requests
        print("✅ requests - OK")
    except ImportError as e:
        print(f"❌ requests - Error: {e}")
        return False
    
    try:
        import selenium
        print("✅ selenium - OK")
    except ImportError as e:
        print(f"❌ selenium - Error: {e}")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4 - OK")
    except ImportError as e:
        print(f"❌ beautifulsoup4 - Error: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy - OK")
    except ImportError as e:
        print(f"❌ sqlalchemy - Error: {e}")
        return False
    
    try:
        import pytz
        print("✅ pytz - OK")
    except ImportError as e:
        print(f"❌ pytz - Error: {e}")
        return False
    
    return True

def test_database_basic():
    """Probar base de datos básica"""
    print("\n🗄️ Probando base de datos básica...")
    
    try:
        # Agregar src al path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from database.models import create_tables, check_database_health
        
        # Crear tablas
        create_tables()
        print("✅ Tablas creadas correctamente")
        
        # Verificar salud
        health = check_database_health()
        if health['status'] == 'healthy':
            print("✅ Base de datos saludable")
            print(f"   • Tesis: {health['total_tesis']}")
            print(f"   • Sesiones: {health['total_sessions']}")
            print(f"   • Estadísticas: {health['total_stats']}")
            return True
        else:
            print(f"❌ Base de datos con problemas: {health['error']}")
            return False
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_file_structure():
    """Probar estructura de archivos"""
    print("\n📁 Probando estructura de archivos...")
    
    required_files = [
        'requirements.txt',
        'README.md',
        'src/database/models.py',
        'src/scraper/selenium_scraper.py',
        'auto_scraper_controller.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Existe")
        else:
            print(f"❌ {file_path} - No existe")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️ Archivos faltantes: {len(missing_files)}")
        return False
    else:
        print("✅ Todos los archivos principales existen")
        return True

def test_configuration_files():
    """Probar archivos de configuración"""
    print("\n⚙️ Probando archivos de configuración...")
    
    config_files = [
        '.env',
        'env.example'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} - Existe")
        else:
            print(f"⚠️ {config_file} - No existe (opcional)")
    
    # Verificar si hay archivo .env
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        return True
    else:
        print("⚠️ Archivo .env no encontrado - usar env.example como base")
        return True

def test_network_connectivity():
    """Probar conectividad de red"""
    print("\n🌐 Probando conectividad de red...")
    
    try:
        import requests
        
        # Probar conexión a SCJN
        response = requests.get('https://sjf2.scjn.gob.mx', timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a SCJN exitosa")
            return True
        else:
            print(f"⚠️ Conexión a SCJN con código: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a SCJN: {e}")
        return False

def test_python_environment():
    """Probar entorno Python"""
    print("\n🐍 Probando entorno Python...")
    
    import platform
    print(f"✅ Python version: {platform.python_version()}")
    print(f"✅ Platform: {platform.platform()}")
    
    # Verificar directorio de trabajo
    print(f"✅ Directorio de trabajo: {os.getcwd()}")
    
    # Verificar permisos de escritura
    try:
        test_file = "test_write_permission.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Permisos de escritura - OK")
    except Exception as e:
        print(f"❌ Error de permisos: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🧪 VERIFICACIÓN SIMPLE DEL SISTEMA SCJN")
    print("=" * 50)
    
    tests = [
        ("Entorno Python", test_python_environment),
        ("Imports básicos", test_basic_imports),
        ("Estructura de archivos", test_file_structure),
        ("Archivos de configuración", test_configuration_files),
        ("Conectividad de red", test_network_connectivity),
        ("Base de datos básica", test_database_basic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("🎉 ¡Sistema listo para funcionar!")
    elif passed >= total * 0.8:
        print("⚠️ Sistema funcional con algunas advertencias")
    else:
        print("❌ Sistema con problemas significativos")
    
    print("\n🔧 PRÓXIMOS PASOS:")
    if passed >= total * 0.8:
        print("1. Instalar Firefox para scraping completo")
        print("2. Configurar variables de entorno (.env)")
        print("3. Ejecutar scraping de prueba")
    else:
        print("1. Revisar dependencias faltantes")
        print("2. Verificar configuración")
        print("3. Revisar permisos de archivos")

if __name__ == "__main__":
    main()