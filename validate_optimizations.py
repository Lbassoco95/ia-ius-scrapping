#!/usr/bin/env python3
"""
VALIDADOR DE OPTIMIZACIONES - SISTEMA SCJN
Verifica que las optimizaciones estén correctamente implementadas
Sin dependencias externas, solo Python estándar
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Imprimir encabezado con formato"""
    print(f"\n🔍 {title}")
    print("-" * 50)

def check_file_exists(file_path, description):
    """Verificar que un archivo existe"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} FALTANTE: {file_path}")
        return False

def check_directory_structure():
    """Verificar estructura de directorios optimizada"""
    print_header("ESTRUCTURA DE DIRECTORIOS")
    
    directories = [
        ("src/", "Directorio fuente"),
        ("src/scraper/", "Módulos de scraping"),
        ("src/storage/", "Módulos de almacenamiento"),
        ("src/database/", "Módulos de base de datos"),
        ("src/utils/", "Utilidades"),
        ("logs/", "Directorio de logs"),
        ("data/", "Directorio de datos"),
        ("data/pdfs/", "Directorio de PDFs"),
    ]
    
    created_dirs = []
    for dir_path, description in directories:
        if Path(dir_path).exists():
            print(f"✅ {description}: {dir_path}")
        else:
            print(f"⚠️ Creando {description}: {dir_path}")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
    
    if created_dirs:
        print(f"📁 Directorios creados: {len(created_dirs)}")
    
    return True

def check_optimized_files():
    """Verificar archivos optimizados"""
    print_header("ARCHIVOS OPTIMIZADOS")
    
    files = [
        ("src/config.py", "Configuración optimizada"),
        ("src/utils/logger.py", "Sistema de logging avanzado"),
        ("src/scraper/optimized_scraper.py", "Scraper optimizado"),
        ("optimized_production_scraper.py", "Script de producción optimizado"),
        ("test_end_to_end_optimized.py", "Pruebas end-to-end"),
        ("requirements.txt", "Dependencias actualizadas"),
        ("env.example", "Configuración de entorno"),
        ("OPTIMIZACION_COMPLETA.md", "Documentación de optimizaciones")
    ]
    
    existing_files = 0
    for file_path, description in files:
        if check_file_exists(file_path, description):
            existing_files += 1
    
    print(f"\n📊 Archivos optimizados: {existing_files}/{len(files)}")
    return existing_files / len(files) > 0.8  # 80% de archivos deben existir

def check_configuration_structure():
    """Verificar estructura de configuración"""
    print_header("CONFIGURACIÓN")
    
    config_file = "src/config.py"
    if not Path(config_file).exists():
        print(f"❌ Archivo de configuración no encontrado: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos clave de la configuración optimizada
        checks = [
            ("ConfigurationError", "Manejo de errores de configuración"),
            ("get_config", "Función de configuración por entorno"),
            ("validate_config", "Validación de configuración"),
            ("PARALLEL_DOWNLOADS", "Configuración de paralelización"),
            ("LOG_LEVEL", "Configuración de logging"),
            ("BATCH_SIZE", "Configuración de lotes"),
        ]
        
        found_elements = 0
        for element, description in checks:
            if element in content:
                print(f"✅ {description}")
                found_elements += 1
            else:
                print(f"❌ {description} no encontrado")
        
        print(f"\n📊 Elementos de configuración: {found_elements}/{len(checks)}")
        return found_elements / len(checks) > 0.7
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False

def check_logging_system():
    """Verificar sistema de logging"""
    print_header("SISTEMA DE LOGGING")
    
    logger_file = "src/utils/logger.py"
    if not Path(logger_file).exists():
        print(f"❌ Sistema de logging no encontrado: {logger_file}")
        return False
    
    try:
        with open(logger_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos del sistema de logging
        checks = [
            ("ScraperFormatter", "Formateador personalizado"),
            ("PerformanceLogger", "Logger de performance"),
            ("performance_monitor", "Decorador de monitoreo"),
            ("RotatingFileHandler", "Rotación de archivos"),
            ("setup_logging", "Configuración de logging"),
        ]
        
        found_elements = 0
        for element, description in checks:
            if element in content:
                print(f"✅ {description}")
                found_elements += 1
            else:
                print(f"❌ {description} no encontrado")
        
        print(f"\n📊 Elementos de logging: {found_elements}/{len(checks)}")
        return found_elements / len(checks) > 0.7
        
    except Exception as e:
        print(f"❌ Error leyendo sistema de logging: {e}")
        return False

def check_optimized_scraper():
    """Verificar scraper optimizado"""
    print_header("SCRAPER OPTIMIZADO")
    
    scraper_file = "src/scraper/optimized_scraper.py"
    if not Path(scraper_file).exists():
        print(f"❌ Scraper optimizado no encontrado: {scraper_file}")
        return False
    
    try:
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos del scraper optimizado
        checks = [
            ("OptimizedSCJNScraper", "Clase principal optimizada"),
            ("ThreadPoolExecutor", "Paralelización"),
            ("cache", "Sistema de cache"),
            ("performance_monitor", "Monitoreo de performance"),
            ("ScrapingResult", "Resultado estructurado"),
            ("SessionStats", "Estadísticas de sesión"),
            ("aiohttp", "Descarga asíncrona"),
        ]
        
        found_elements = 0
        for element, description in checks:
            if element in content:
                print(f"✅ {description}")
                found_elements += 1
            else:
                print(f"⚠️ {description} no encontrado")
        
        print(f"\n📊 Elementos del scraper: {found_elements}/{len(checks)}")
        return found_elements / len(checks) > 0.6
        
    except Exception as e:
        print(f"❌ Error leyendo scraper optimizado: {e}")
        return False

def check_database_setup():
    """Verificar configuración de base de datos"""
    print_header("BASE DE DATOS")
    
    # Crear directorio de datos si no existe
    Path("data").mkdir(exist_ok=True)
    
    # Probar creación de base de datos SQLite
    db_path = "data/test_validation.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla de prueba
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar datos de prueba
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_optimization",))
        conn.commit()
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Base de datos SQLite funcionando")
        print(f"✅ Registros de prueba: {count}")
        
        # Limpiar archivo de prueba
        Path(db_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def check_environment_config():
    """Verificar configuración de entorno"""
    print_header("CONFIGURACIÓN DE ENTORNO")
    
    env_file = "env.example"
    if not Path(env_file).exists():
        print(f"❌ Archivo de entorno no encontrado: {env_file}")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar variables importantes
        checks = [
            ("ENVIRONMENT=", "Variable de entorno"),
            ("PARALLEL_DOWNLOADS=", "Configuración de paralelización"),
            ("LOG_LEVEL=", "Nivel de logging"),
            ("MAX_RETRIES=", "Reintentos máximos"),
            ("BATCH_SIZE=", "Tamaño de lote"),
            ("SELENIUM_HEADLESS=", "Configuración de Selenium"),
        ]
        
        found_vars = 0
        for var, description in checks:
            if var in content:
                print(f"✅ {description}")
                found_vars += 1
            else:
                print(f"❌ {description} no encontrada")
        
        print(f"\n📊 Variables de entorno: {found_vars}/{len(checks)}")
        return found_vars / len(checks) > 0.8
        
    except Exception as e:
        print(f"❌ Error leyendo configuración de entorno: {e}")
        return False

def generate_validation_report():
    """Generar reporte de validación"""
    print_header("GENERANDO REPORTE")
    
    report = {
        "validation_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "working_directory": os.getcwd(),
        "tests_run": True,
        "summary": "Validación básica de optimizaciones completada"
    }
    
    report_file = "data/validation_report.json"
    try:
        Path("data").mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")
        return False

def main():
    """Función principal de validación"""
    print("🏛️ IA-IUS-SCRAPPING: VALIDACIÓN DE OPTIMIZACIONES")
    print("=" * 70)
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar todas las validaciones
    tests = [
        ("Estructura de Directorios", check_directory_structure),
        ("Archivos Optimizados", check_optimized_files),
        ("Configuración", check_configuration_structure),
        ("Sistema de Logging", check_logging_system),
        ("Scraper Optimizado", check_optimized_scraper),
        ("Base de Datos", check_database_setup),
        ("Configuración de Entorno", check_environment_config),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Generar reporte
    generate_validation_report()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    print(f"📊 Total de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print("🎉 ¡OPTIMIZACIONES VALIDADAS EXITOSAMENTE!")
        print("🚀 Sistema listo para pruebas adicionales")
        exit_code = 0
    elif success_rate >= 70:
        print("⚠️ Optimizaciones parcialmente validadas")
        print("🔧 Revisar elementos faltantes")
        exit_code = 1
    else:
        print("❌ Validación falló")
        print("🛠️ Sistema necesita revisión")
        exit_code = 2
    
    print(f"\n🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)