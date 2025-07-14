#!/usr/bin/env python3
"""
Script de configuración rápida para el sistema de scraping inteligente
- Configuración automática de parámetros
- Verificación de dependencias
- Inicialización del sistema
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        'selenium',
        'requests',
        'beautifulsoup4',
        'sqlalchemy',
        'schedule',
        'webdriver-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Instalando paquetes faltantes...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencias instaladas correctamente")
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias")
            return False
    
    return True

def create_directories():
    """Crear directorios necesarios"""
    print("\n📁 Creando directorios...")
    
    directories = [
        'data',
        'data/pdfs',
        'logs',
        'credentials',
        'src/automation',
        'src/scraper',
        'src/database',
        'src/config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def create_config_file():
    """Crear archivo de configuración inicial"""
    print("\n⚙️  Creando configuración inicial...")
    
    config = {
        'current_phase': 'initial',
        'initial_phase_completed': False,
        'last_maintenance_date': None,
        'total_estimated_files': 50000,
        'files_downloaded_initial': 0
    }
    
    try:
        with open('data/scraper_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Configuración creada")
    except Exception as e:
        print(f"❌ Error creando configuración: {e}")

def create_stats_file():
    """Crear archivo de estadísticas inicial"""
    print("\n📊 Creando estadísticas iniciales...")
    
    stats = {
        'total_downloaded': 0,
        'daily_downloads': {},
        'session_downloads': {},
        'duplicates_found': 0,
        'errors': 0,
        'phase_transitions': []
    }
    
    try:
        with open('data/scraping_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        print("✅ Estadísticas creadas")
    except Exception as e:
        print(f"❌ Error creando estadísticas: {e}")

def setup_database():
    """Configurar base de datos"""
    print("\n🗄️  Configurando base de datos...")
    
    try:
        # Importar después de verificar dependencias
        sys.path.append('src')
        from src.database.models import create_tables
        
        create_tables()
        print("✅ Base de datos configurada")
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")

def show_configuration_menu():
    """Mostrar menú de configuración"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN DEL SISTEMA INTELIGENTE")
    print("="*60)
    print("1. 🚀 Configuración rápida (recomendado)")
    print("2. ⚙️  Configuración personalizada")
    print("3. 📊 Ver configuración actual")
    print("4. 🔄 Reiniciar configuración")
    print("0. ❌ Salir")
    print("="*60)

def quick_setup():
    """Configuración rápida con valores por defecto"""
    print("\n🚀 CONFIGURACIÓN RÁPIDA")
    print("-" * 30)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error en dependencias")
        return False
    
    # Crear directorios
    create_directories()
    
    # Crear archivos de configuración
    create_config_file()
    create_stats_file()
    
    # Configurar base de datos
    setup_database()
    
    print("\n✅ Configuración rápida completada")
    print("\n📋 Configuración aplicada:")
    print("   • Fase inicial: 3 horas diarias")
    print("   • Horario inicial: 9:00 AM")
    print("   • Mantenimiento: Lunes 8:00 AM")
    print("   • Archivos máximos por sesión: 200")
    print("   • Archivos estimados totales: 50,000")
    
    return True

def custom_setup():
    """Configuración personalizada"""
    print("\n⚙️  CONFIGURACIÓN PERSONALIZADA")
    print("-" * 35)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error en dependencias")
        return False
    
    # Crear directorios
    create_directories()
    
    # Configurar parámetros
    print("\n📋 Configurar parámetros:")
    
    try:
        hours = int(input("Horas diarias en fase inicial (1-24) [3]: ") or "3")
        if not 1 <= hours <= 24:
            print("❌ Valor inválido, usando 3 horas")
            hours = 3
        
        start_time = input("Hora de inicio diario (HH:MM) [09:00]: ") or "09:00"
        try:
            from datetime import datetime
            datetime.strptime(start_time, "%H:%M")
        except ValueError:
            print("❌ Formato inválido, usando 09:00")
            start_time = "09:00"
        
        maintenance_time = input("Hora de mantenimiento semanal (HH:MM) [08:00]: ") or "08:00"
        try:
            datetime.strptime(maintenance_time, "%H:%M")
        except ValueError:
            print("❌ Formato inválido, usando 08:00")
            maintenance_time = "08:00"
        
        max_files = int(input("Archivos máximos por sesión (50-500) [200]: ") or "200")
        if not 50 <= max_files <= 500:
            print("❌ Valor inválido, usando 200")
            max_files = 200
        
        total_files = int(input("Archivos estimados totales (10000-100000) [50000]: ") or "50000")
        if not 10000 <= total_files <= 100000:
            print("❌ Valor inválido, usando 50000")
            total_files = 50000
        
        # Crear configuración personalizada
        config = {
            'current_phase': 'initial',
            'initial_phase_completed': False,
            'last_maintenance_date': None,
            'total_estimated_files': total_files,
            'files_downloaded_initial': 0,
            'initial_phase_hours': hours,
            'initial_phase_start_time': start_time,
            'maintenance_phase_start_time': maintenance_time,
            'max_files_per_session': max_files
        }
        
        with open('data/scraper_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        create_stats_file()
        setup_database()
        
        print("\n✅ Configuración personalizada completada")
        print(f"\n📋 Configuración aplicada:")
        print(f"   • Fase inicial: {hours} horas diarias")
        print(f"   • Horario inicial: {start_time}")
        print(f"   • Mantenimiento: Lunes {maintenance_time}")
        print(f"   • Archivos máximos por sesión: {max_files}")
        print(f"   • Archivos estimados totales: {total_files:,}")
        
        return True
        
    except ValueError as e:
        print(f"❌ Error en configuración: {e}")
        return False

def show_current_config():
    """Mostrar configuración actual"""
    print("\n📊 CONFIGURACIÓN ACTUAL")
    print("-" * 25)
    
    config_file = 'data/scraper_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"🎯 Fase actual: {config.get('current_phase', 'N/A')}")
            print(f"📈 Archivos descargados: {config.get('files_downloaded_initial', 0):,}")
            print(f"📊 Archivos estimados: {config.get('total_estimated_files', 0):,}")
            print(f"⏰ Horas diarias: {config.get('initial_phase_hours', 3)}")
            print(f"🌅 Hora inicio: {config.get('initial_phase_start_time', '09:00')}")
            print(f"🔧 Hora mantenimiento: {config.get('maintenance_phase_start_time', '08:00')}")
            print(f"📁 Archivos máximos: {config.get('max_files_per_session', 200)}")
            
        except Exception as e:
            print(f"❌ Error leyendo configuración: {e}")
    else:
        print("❌ No hay configuración actual")
    
    stats_file = 'data/scraping_stats.json'
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
            
            print(f"\n📈 Estadísticas:")
            print(f"   • Total descargado: {stats.get('total_downloaded', 0):,}")
            print(f"   • Duplicados: {stats.get('duplicates_found', 0):,}")
            print(f"   • Errores: {stats.get('errors', 0):,}")
            
        except Exception as e:
            print(f"❌ Error leyendo estadísticas: {e}")

def reset_configuration():
    """Reiniciar configuración"""
    print("\n🔄 REINICIANDO CONFIGURACIÓN")
    print("-" * 30)
    
    confirm = input("¿Está seguro? Esto eliminará toda la configuración actual (s/n): ").lower()
    if confirm == 's':
        try:
            # Eliminar archivos de configuración
            files_to_remove = [
                'data/scraper_config.json',
                'data/scraping_stats.json'
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  Eliminado: {file_path}")
            
            # Recrear configuración
            create_config_file()
            create_stats_file()
            setup_database()
            
            print("✅ Configuración reiniciada")
            
        except Exception as e:
            print(f"❌ Error reiniciando configuración: {e}")
    else:
        print("❌ Operación cancelada")

def main():
    """Función principal"""
    print("🤖 CONFIGURADOR DEL SISTEMA DE SCRAPING INTELIGENTE")
    print("=" * 60)
    
    while True:
        try:
            show_configuration_menu()
            option = input("\nSeleccione opción: ")
            
            if option == "1":
                quick_setup()
            elif option == "2":
                custom_setup()
            elif option == "3":
                show_current_config()
            elif option == "4":
                reset_configuration()
            elif option == "0":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
            
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n🛑 Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Presione Enter para continuar...")

if __name__ == "__main__":
    main() 