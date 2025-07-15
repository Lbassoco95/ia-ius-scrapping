#!/usr/bin/env python3
"""
Verificar que el sistema esté listo para producción
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, 'src')

def check_directories():
    """Verificar que existan todos los directorios necesarios"""
    print("📁 Verificando directorios...")
    
    required_dirs = [
        "data",
        "data/pdfs", 
        "logs",
        "credentials",
        "src",
        "src/scraper",
        "src/database",
        "src/storage",
        "src/config"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
            print(f"  ❌ Falta: {dir_path}")
        else:
            print(f"  ✅ Existe: {dir_path}")
    
    if missing_dirs:
        print(f"\n⚠️  Creando directorios faltantes...")
        for dir_path in missing_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Creado: {dir_path}")
    
    return len(missing_dirs) == 0

def check_files():
    """Verificar que existan todos los archivos necesarios"""
    print("\n📄 Verificando archivos...")
    
    required_files = [
        "production_scraper.py",
        "src/scraper/main.py",
        "src/database/models.py",
        "src/config.py",
        "requirements.txt",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"  ❌ Falta: {file_path}")
        else:
            print(f"  ✅ Existe: {file_path}")
    
    return len(missing_files) == 0

def check_environment():
    """Verificar variables de entorno"""
    print("\n🔧 Verificando configuración de entorno...")
    
    try:
        from src.config import Config
        
        # Verificar Google Drive
        if Config.GOOGLE_DRIVE_ENABLED:
            print("  ✅ Google Drive habilitado")
            if Config.GOOGLE_DRIVE_FOLDER_ID:
                print(f"  ✅ Folder ID configurado: {Config.GOOGLE_DRIVE_FOLDER_ID}")
            else:
                print("  ⚠️  GOOGLE_DRIVE_FOLDER_ID no configurado")
        else:
            print("  ℹ️  Google Drive deshabilitado")
        
        # Verificar base de datos
        print(f"  ✅ Base de datos: {Config.DATABASE_URL}")
        
        # Verificar URLs de SCJN
        print(f"  ✅ URL base SCJN: {Config.SCJN_BASE_URL}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando configuración: {e}")
        return False

def check_database():
    """Verificar base de datos"""
    print("\n🗄️ Verificando base de datos...")
    
    try:
        from src.database.models import create_tables, get_session, Tesis
        
        # Crear tablas si no existen
        create_tables()
        
        # Verificar conexión
        session = get_session()
        total_tesis = session.query(Tesis).count()
        print(f"  ✅ Base de datos conectada")
        print(f"  📊 Total tesis en BD: {total_tesis}")
        
        # Verificar campos de Google Drive
        tesis_con_drive = session.query(Tesis).filter(Tesis.google_drive_id.isnot(None)).count()
        print(f"  📁 Tesis con PDF en Drive: {tesis_con_drive}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando base de datos: {e}")
        return False

def check_dependencies():
    """Verificar dependencias de Python"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        "selenium",
        "beautifulsoup4", 
        "requests",
        "sqlalchemy",
        "google-auth",
        "google-api-python-client",
        "fastapi",
        "uvicorn"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def check_google_drive_credentials():
    """Verificar credenciales de Google Drive"""
    print("\n🔐 Verificando credenciales de Google Drive...")
    
    cred_files = [
        "credentials/google_drive_credentials.json",
        "credentials/service_account.json",
        "credentials/token.json"
    ]
    
    found_credentials = False
    for cred_file in cred_files:
        if Path(cred_file).exists():
            print(f"  ✅ Encontrado: {cred_file}")
            found_credentials = True
        else:
            print(f"  ❌ No encontrado: {cred_file}")
    
    if not found_credentials:
        print("  ⚠️  No se encontraron credenciales de Google Drive")
        print("     El sistema funcionará sin subida a Drive")
    
    return True

def check_selenium():
    """Verificar configuración de Selenium"""
    print("\n🌐 Verificando Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Verificar ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"  ✅ ChromeDriver: {driver_path}")
        
        # Verificar Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.quit()
            print("  ✅ Chrome/Selenium funcionando correctamente")
            return True
        except Exception as e:
            print(f"  ❌ Error con Chrome/Selenium: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error verificando Selenium: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DE PRODUCCIÓN - SCJN SCRAPER")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Directorios", check_directories),
        ("Archivos", check_files),
        ("Entorno", check_environment),
        ("Base de datos", check_database),
        ("Dependencias", check_dependencies),
        ("Credenciales Google Drive", check_google_drive_credentials),
        ("Selenium", check_selenium)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Error en verificación {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name:25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
        print("\n🚀 Próximos pasos:")
        print("   1. Ejecutar: ./setup_production_cron.sh")
        print("   2. Verificar: crontab -l")
        print("   3. Probar manualmente: python production_scraper.py")
        return True
    else:
        print("⚠️  CORREGIR PROBLEMAS ANTES DE PRODUCCIÓN")
        print("\n🔧 Comandos útiles:")
        print("   - Instalar dependencias: pip install -r requirements.txt")
        print("   - Configurar .env: cp env.example .env")
        print("   - Verificar logs: tail -f logs/production_scraper_*.log")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 