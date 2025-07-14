#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de scraping inteligente
- Prueba de configuración
- Prueba de base de datos
- Prueba de scraper
- Prueba de controlador
"""

import sys
import os
import time
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_configuration():
    """Probar configuración del sistema"""
    print("🔧 Probando configuración...")
    
    try:
        from src.config import Config
        
        # Validar configuración
        if Config.validate_config():
            print("✅ Configuración válida")
            Config.print_config()
            return True
        else:
            print("❌ Configuración inválida")
            return False
            
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_database():
    """Probar base de datos"""
    print("\n🗄️ Probando base de datos...")
    
    try:
        from src.database.models import create_tables, check_database_health, get_database_info
        
        # Crear tablas
        create_tables()
        print("✅ Tablas creadas")
        
        # Verificar salud
        health = check_database_health()
        if health['status'] == 'healthy':
            print("✅ Base de datos saludable")
            print(f"   • Tesis: {health['total_tesis']}")
            print(f"   • Sesiones: {health['total_sessions']}")
            print(f"   • Estadísticas: {health['total_stats']}")
        else:
            print(f"❌ Base de datos con problemas: {health['error']}")
            return False
        
        # Obtener información
        info = get_database_info()
        if info:
            print("✅ Información de BD obtenida")
        else:
            print("❌ Error obteniendo información de BD")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_scraper():
    """Probar scraper"""
    print("\n🤖 Probando scraper...")
    
    try:
        from src.scraper.selenium_scraper import SeleniumSCJNScraper
        
        scraper = SeleniumSCJNScraper()
        
        # Probar conexión
        print("🔗 Probando conexión con SCJN...")
        if scraper.test_connection():
            print("✅ Conexión exitosa con SCJN")
        else:
            print("❌ Error conectando con SCJN")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en scraper: {e}")
        return False

def test_auto_scraper():
    """Probar auto scraper"""
    print("\n🔄 Probando auto scraper...")
    
    try:
        from src.automation.auto_scraper import IntelligentAutoScraper
        
        scraper = IntelligentAutoScraper()
        
        # Obtener estado
        status = scraper.get_status()
        print("✅ Auto scraper inicializado")
        print(f"   • Fase: {status['current_phase']}")
        print(f"   • Progreso: {status['progress_percentage']}%")
        print(f"   • Archivos en BD: {status['total_in_database']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en auto scraper: {e}")
        return False

def test_controller():
    """Probar controlador"""
    print("\n🎮 Probando controlador...")
    
    try:
        from auto_scraper_controller import AutoScraperController
        
        controller = AutoScraperController()
        print("✅ Controlador inicializado")
        
        # Probar obtención de estado
        try:
            controller.show_status()
            print("✅ Estado del sistema obtenido")
        except Exception as e:
            print(f"⚠️ Error obteniendo estado: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en controlador: {e}")
        return False

def test_daemon():
    """Probar daemon"""
    print("\n⏰ Probando daemon...")
    
    try:
        from start_auto_scraper import AutoScraperDaemon
        
        daemon = AutoScraperDaemon()
        print("✅ Daemon inicializado")
        
        # Probar verificación de estado
        if daemon.is_running():
            print("⚠️ Daemon ya está ejecutándose")
        else:
            print("✅ Daemon no está ejecutándose (esperado)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en daemon: {e}")
        return False

def run_quick_test():
    """Ejecutar prueba rápida del sistema"""
    print("🚀 PRUEBA RÁPIDA DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_configuration),
        ("Base de datos", test_database),
        ("Scraper", test_scraper),
        ("Auto scraper", test_auto_scraper),
        ("Controlador", test_controller),
        ("Daemon", test_daemon)
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
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Sistema completamente funcional!")
        return True
    elif passed >= total * 0.8:
        print("⚠️ Sistema funcional con algunos problemas menores")
        return True
    else:
        print("❌ Sistema con problemas significativos")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n📋 PRÓXIMOS PASOS PARA PRODUCCIÓN")
    print("=" * 40)
    
    print("1. 🚀 Configurar sistema:")
    print("   python setup_intelligent_scraper.py")
    
    print("\n2. 🎮 Usar controlador:")
    print("   python auto_scraper_controller.py")
    
    print("\n3. ⏰ Iniciar modo automático:")
    print("   python start_auto_scraper.py start")
    
    print("\n4. 📊 Monitorear:")
    print("   python start_auto_scraper.py status")
    print("   tail -f logs/auto_scraper.log")
    
    print("\n5. 🔧 Configurar (opcional):")
    print("   - Google Drive para almacenamiento")
    print("   - OpenAI para análisis de contenido")
    print("   - Horarios personalizados")

def main():
    """Función principal"""
    print("🧪 SISTEMA DE PRUEBAS - SCRAPING INTELIGENTE SCJN")
    print("=" * 60)
    
    # Ejecutar pruebas
    success = run_quick_test()
    
    if success:
        show_next_steps()
    else:
        print("\n🔧 PROBLEMAS DETECTADOS")
        print("=" * 25)
        print("1. Verificar dependencias instaladas")
        print("2. Revisar configuración")
        print("3. Verificar permisos de archivos")
        print("4. Revisar logs de error")

if __name__ == "__main__":
    main() 