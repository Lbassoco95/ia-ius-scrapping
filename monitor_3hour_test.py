#!/usr/bin/env python3
"""
📊 Monitoreo en Tiempo Real - Prueba de 3 Horas SCJN Scraper
Script para monitorear el progreso de la prueba de 3 horas
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def monitor_test_progress():
    """Monitorear progreso de la prueba de 3 horas"""
    print("📊 MONITOREO EN TIEMPO REAL - PRUEBA DE 3 HORAS")
    print("=" * 60)
    
    monitor_file = Path("logs/3hour_test/monitor_data.json")
    final_report_file = Path("logs/3hour_test/final_report.json")
    
    last_checkpoint = 0
    
    try:
        while True:
            # Verificar si existe el archivo de monitoreo
            if monitor_file.exists():
                with open(monitor_file, 'r', encoding='utf-8') as f:
                    monitor_data = json.load(f)
                
                current_time = datetime.now()
                checkpoints = monitor_data.get('checkpoints', [])
                
                if len(checkpoints) > last_checkpoint:
                    # Nuevos checkpoints disponibles
                    new_checkpoints = checkpoints[last_checkpoint:]
                    
                    for checkpoint in new_checkpoints:
                        checkpoint_time = datetime.fromisoformat(checkpoint['time'])
                        elapsed = checkpoint['elapsed_time']
                        session = checkpoint['session_count']
                        files = checkpoint['total_files']
                        
                        print(f"📊 {checkpoint_time.strftime('%H:%M:%S')} - Sesión {session}, Archivos: {files}, Tiempo: {elapsed}")
                    
                    last_checkpoint = len(checkpoints)
                    
                    # Mostrar estadísticas actuales
                    if checkpoints:
                        latest = checkpoints[-1]
                        print(f"📈 Progreso actual: {latest['session_count']} sesiones, {latest['total_files']} archivos")
                
                # Verificar si la prueba ha terminado
                if monitor_data.get('status') == 'completed':
                    print("\n🎉 ¡PRUEBA COMPLETADA!")
                    break
                    
            # Verificar reporte final
            if final_report_file.exists():
                with open(final_report_file, 'r', encoding='utf-8') as f:
                    final_data = json.load(f)
                
                print("\n🎉 ¡PRUEBA DE 3 HORAS COMPLETADA!")
                print("=" * 40)
                print(f"📊 RESULTADOS FINALES:")
                print(f"   • Sesiones completadas: {final_data.get('sessions_completed', 'N/A')}")
                print(f"   • Archivos creados: {final_data.get('total_files_created', 'N/A')}")
                print(f"   • Duración total: {final_data.get('duration', 'N/A')}")
                print(f"   • Estado: {final_data.get('status', 'N/A')}")
                break
            
            # Esperar 30 segundos antes del siguiente check
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n⚠️ Monitoreo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en monitoreo: {e}")

def show_current_status():
    """Mostrar estado actual de la prueba"""
    print("📊 ESTADO ACTUAL DE LA PRUEBA")
    print("=" * 40)
    
    monitor_file = Path("logs/3hour_test/monitor_data.json")
    final_report_file = Path("logs/3hour_test/final_report.json")
    
    if final_report_file.exists():
        with open(final_report_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        print("🎉 PRUEBA COMPLETADA")
        print(f"   • Sesiones: {final_data.get('sessions_completed', 'N/A')}")
        print(f"   • Archivos: {final_data.get('total_files_created', 'N/A')}")
        print(f"   • Duración: {final_data.get('duration', 'N/A')}")
        
    elif monitor_file.exists():
        with open(monitor_file, 'r', encoding='utf-8') as f:
            monitor_data = json.load(f)
        
        checkpoints = monitor_data.get('checkpoints', [])
        if checkpoints:
            latest = checkpoints[-1]
            print("🔄 PRUEBA EN PROGRESO")
            print(f"   • Sesión actual: {latest['session_count']}")
            print(f"   • Archivos creados: {latest['total_files']}")
            print(f"   • Tiempo transcurrido: {latest['elapsed_time']}")
        else:
            print("⏳ PRUEBA INICIANDO...")
    else:
        print("❌ No se encontró información de la prueba")

def show_file_structure():
    """Mostrar estructura de archivos creados"""
    print("\n📁 ESTRUCTURA DE ARCHIVOS CREADOS")
    print("=" * 40)
    
    backup_dir = Path("data/backups/3hour_test")
    if backup_dir.exists():
        sessions = [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        sessions.sort()
        
        print(f"📂 Directorio: {backup_dir}")
        print(f"📊 Sesiones encontradas: {len(sessions)}")
        
        for session_dir in sessions:
            session_id = session_dir.name.replace('session_', '')
            files = list(session_dir.glob("*.txt"))
            metadata = list(session_dir.glob("*.json"))
            
            print(f"   📁 Sesión {session_id}: {len(files)} archivos + {len(metadata)} metadata")
            
            # Mostrar algunos archivos de ejemplo
            if files:
                for i, file_path in enumerate(files[:3]):  # Solo mostrar primeros 3
                    file_size = file_path.stat().st_size
                    print(f"      📄 {file_path.name} ({file_size} bytes)")
                
                if len(files) > 3:
                    print(f"      ... y {len(files) - 3} archivos más")
    else:
        print("❌ No se encontró directorio de backup")

def main():
    """Función principal"""
    print("📊 MONITOREO DE PRUEBA DE 3 HORAS - SCJN SCRAPER")
    print("=" * 60)
    
    # Mostrar estado actual
    show_current_status()
    
    # Mostrar estructura de archivos
    show_file_structure()
    
    # Preguntar si quiere monitoreo en tiempo real
    print("\n" + "=" * 60)
    response = input("¿Desea iniciar monitoreo en tiempo real? (s/n): ").lower()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n🔄 Iniciando monitoreo en tiempo real...")
        print("Presione Ctrl+C para detener")
        monitor_test_progress()
    else:
        print("✅ Monitoreo finalizado")

if __name__ == "__main__":
    main()