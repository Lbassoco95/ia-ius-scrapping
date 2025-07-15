#!/usr/bin/env python3
"""
Verificación completa del sistema de scraping SCJN
"""

import sys
import os
import json
from datetime import datetime
import subprocess

sys.path.insert(0, 'src')

def check_directories():
    """Verificar estructura de directorios"""
    print("📁 VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    print("-" * 40)
    
    required_dirs = [
        'data',
        'data/pdfs',
        'logs',
        'credentials',
        'src',
        'src/database',
        'src/scraper',
        'src/storage',
        'src/analysis'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - FALTANTE")
            missing_dirs.append(dir_path)
    
    # Crear directorios faltantes
    if missing_dirs:
        print("\n🔧 Creando directorios faltantes...")
        for dir_path in missing_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ Creado: {dir_path}")
            except Exception as e:
                print(f"❌ Error creando {dir_path}: {e}")
    
    return len(missing_dirs) == 0

def check_database():
    """Verificar base de datos"""
    print("\n🗄️ VERIFICANDO BASE DE DATOS")
    print("-" * 40)
    
    try:
        from database.models import get_session, Tesis, create_tables
        
        # Crear tablas si no existen
        create_tables()
        
        session = get_session()
        total_tesis = session.query(Tesis).count()
        
        # Verificar estructura de la tabla
        sample_tesis = session.query(Tesis).first()
        
        print(f"✅ Base de datos: Conectada")
        print(f"📊 Total tesis: {total_tesis}")
        
        if sample_tesis:
            print(f"📋 Campos disponibles:")
            print(f"   - scjn_id: {sample_tesis.scjn_id}")
            print(f"   - titulo: {sample_tesis.titulo[:50]}...")
            print(f"   - pdf_url: {sample_tesis.pdf_url}")
            print(f"   - google_drive_id: {sample_tesis.google_drive_id}")
            print(f"   - google_drive_link: {sample_tesis.google_drive_link}")
        else:
            print("⚠️  No hay tesis en la base de datos")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def check_google_drive_config():
    """Verificar configuración de Google Drive"""
    print("\n☁️ VERIFICANDO CONFIGURACIÓN DE GOOGLE DRIVE")
    print("-" * 40)
    
    # Verificar archivo de credenciales
    cred_files = [
        'credentials/google_drive_credentials.json',
        'credentials/service_account.json',
        '.env'
    ]
    
    cred_found = False
    for cred_file in cred_files:
        if os.path.exists(cred_file):
            print(f"✅ {cred_file} - ENCONTRADO")
            cred_found = True
        else:
            print(f"❌ {cred_file} - NO ENCONTRADO")
    
    # Verificar variables de entorno
    env_vars = [
        'GOOGLE_DRIVE_FOLDER_ID',
        'GOOGLE_DRIVE_ENABLED'
    ]
    
    print("\n🔧 Variables de entorno:")
    for var in env_vars:
        value = os.getenv(var, 'NO CONFIGURADA')
        print(f"   {var}: {value}")
    
    # Probar conexión con Google Drive
    try:
        from storage.google_drive import GoogleDriveManager
        
        drive_manager = GoogleDriveManager()
        drive_manager.authenticate()
        
        print("✅ Conexión con Google Drive: EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con Google Drive: {e}")
        print("💡 Para configurar Google Drive:")
        print("   1. Crear proyecto en Google Cloud Console")
        print("   2. Habilitar Google Drive API")
        print("   3. Crear service account y descargar credenciales")
        print("   4. Colocar archivo en credentials/google_drive_credentials.json")
        return False

def check_pdf_download():
    """Verificar funcionalidad de descarga de PDFs"""
    print("\n📄 VERIFICANDO DESCARGA DE PDFS")
    print("-" * 40)
    
    # Verificar directorio de PDFs
    pdf_dir = 'data/pdfs'
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        print(f"✅ Directorio PDFs: {pdf_dir}")
        print(f"📊 PDFs existentes: {len(pdf_files)}")
        
        if pdf_files:
            print("📋 PDFs encontrados:")
            for pdf in pdf_files[:5]:  # Mostrar solo los primeros 5
                print(f"   - {pdf}")
        else:
            print("⚠️  No hay PDFs descargados")
    else:
        print(f"❌ Directorio PDFs no existe: {pdf_dir}")
    
    # Verificar permisos
    try:
        test_file = os.path.join(pdf_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Permisos de escritura: CORRECTOS")
    except Exception as e:
        print(f"❌ Error de permisos: {e}")
        return False
    
    return True

def check_scraper_components():
    """Verificar componentes del scraper"""
    print("\n🔍 VERIFICANDO COMPONENTES DEL SCRAPER")
    print("-" * 40)
    
    components = [
        'src/scraper/selenium_scraper.py',
        'src/scraper/scraper.py',
        'src/scraper/main.py',
        'robust_scraper.py',
        'integrate_results_fixed.py'
    ]
    
    missing_components = []
    for component in components:
        if os.path.exists(component):
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - FALTANTE")
            missing_components.append(component)
    
    return len(missing_components) == 0

def check_dependencies():
    """Verificar dependencias instaladas"""
    print("\n📦 VERIFICANDO DEPENDENCIAS")
    print("-" * 40)
    
    required_packages = [
        'selenium',
        'beautifulsoup4',
        'requests',
        'sqlalchemy',
        'google-auth',
        'google-api-python-client',
        'fastapi',
        'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Para instalar dependencias faltantes:")
        print(f"   pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_json_files():
    """Verificar archivos JSON de resultados"""
    print("\n📄 VERIFICANDO ARCHIVOS JSON")
    print("-" * 40)
    
    json_files = [f for f in os.listdir('data') if f.startswith('robust_test_results_') and f.endswith('.json')]
    
    if json_files:
        print(f"✅ Archivos JSON encontrados: {len(json_files)}")
        
        # Mostrar el más reciente
        json_files.sort(reverse=True)
        latest_file = json_files[0]
        
        try:
            with open(os.path.join('data', latest_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                print(f"📊 Estructura: Lista con {len(data)} elementos")
                if data:
                    sample = data[0]
                    print(f"📋 Campos disponibles:")
                    for key in sample.keys():
                        print(f"   - {key}")
            else:
                print(f"📊 Estructura: {type(data)}")
                
        except Exception as e:
            print(f"❌ Error leyendo JSON: {e}")
    else:
        print("⚠️  No se encontraron archivos JSON de resultados")
    
    return len(json_files) > 0

def run_test_scraping():
    """Ejecutar prueba de scraping"""
    print("\n🧪 EJECUTANDO PRUEBA DE SCRAPING")
    print("-" * 40)
    
    try:
        # Ejecutar scraper robusto
        result = subprocess.run(['python3', 'robust_scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Scraping básico: EXITOSO")
            print("📤 Salida:")
            print(result.stdout[-500:])  # Últimas 500 caracteres
        else:
            print("❌ Scraping básico: FALLÓ")
            print("📤 Error:")
            print(result.stderr[-500:])
            return False
        
        # Verificar si se generó nuevo archivo JSON
        json_files = [f for f in os.listdir('data') if f.startswith('robust_test_results_') and f.endswith('.json')]
        if json_files:
            print(f"✅ Nuevo archivo JSON generado: {json_files[-1]}")
        else:
            print("⚠️  No se generó nuevo archivo JSON")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en prueba de scraping")
        return False
    except Exception as e:
        print(f"❌ Error en prueba de scraping: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DE SCRAPING SCJN")
    print("=" * 60)
    print(f"⏰ Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar cada componente
    checks = [
        ("Estructura de directorios", check_directories),
        ("Base de datos", check_database),
        ("Configuración Google Drive", check_google_drive_config),
        ("Descarga de PDFs", check_pdf_download),
        ("Componentes del scraper", check_scraper_components),
        ("Dependencias", check_dependencies),
        ("Archivos JSON", check_json_files)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n{'='*60}")
        results[name] = check_func()
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} verificaciones exitosas")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE OPERATIVO")
        print("\n🚀 ¿Ejecutar prueba de scraping completa? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            print("\n🧪 INICIANDO PRUEBA DE SCRAPING...")
            if run_test_scraping():
                print("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
            else:
                print("❌ PRUEBA FALLÓ")
    else:
        print("⚠️  HAY PROBLEMAS QUE NECESITAN ATENCIÓN")
        print("\n🔧 Problemas detectados:")
        for name, result in results.items():
            if not result:
                print(f"   - {name}")
        
        print("\n💡 Recomendaciones:")
        if not results["Configuración Google Drive"]:
            print("   1. Configurar Google Drive API")
        if not results["Dependencias"]:
            print("   2. Instalar dependencias faltantes")
        if not results["Estructura de directorios"]:
            print("   3. Crear directorios faltantes")

if __name__ == "__main__":
    main() 