#!/usr/bin/env python3
"""
Prueba extendida de scraping - 3 horas de ejecución continua
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime, timedelta
import threading

sys.path.insert(0, 'src')

def log_message(message):
    """Escribir mensaje con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Guardar en archivo de log
    with open('logs/extended_test.log', 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def get_database_count():
    """Obtener conteo actual de la base de datos"""
    try:
        from database.models import get_session, Tesis
        session = get_session()
        count = session.query(Tesis).count()
        session.close()
        return count
    except Exception as e:
        log_message(f"❌ Error obteniendo conteo BD: {e}")
        return 0

def get_json_files_count():
    """Obtener número de archivos JSON generados"""
    try:
        json_files = [f for f in os.listdir('data') if f.startswith('robust_test_results_') and f.endswith('.json')]
        return len(json_files)
    except Exception as e:
        log_message(f"❌ Error contando archivos JSON: {e}")
        return 0

def run_single_scraping_cycle():
    """Ejecutar un ciclo completo de scraping"""
    try:
        log_message("🔄 Iniciando ciclo de scraping...")
        
        # Ejecutar scraper
        result = subprocess.run(['python3', 'robust_scraper.py'], 
                              capture_output=True, text=True, timeout=300)  # 5 minutos timeout
        
        if result.returncode == 0:
            log_message("✅ Scraping completado exitosamente")
            
            # Integrar resultados
            integrate_result = subprocess.run(['python3', 'integrate_results_fixed.py'], 
                                            capture_output=True, text=True, timeout=60)
            
            if integrate_result.returncode == 0:
                log_message("✅ Integración completada exitosamente")
                return True
            else:
                log_message(f"⚠️  Integración con errores: {integrate_result.stderr}")
                return False
        else:
            log_message(f"❌ Error en scraping: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("⏰ Timeout en ciclo de scraping")
        return False
    except Exception as e:
        log_message(f"❌ Error ejecutando ciclo: {e}")
        return False

def monitor_progress():
    """Monitorear progreso en tiempo real"""
    start_time = datetime.now()
    initial_count = get_database_count()
    initial_files = get_json_files_count()
    
    log_message(f"📊 MONITOREO INICIADO")
    log_message(f"📋 Tesis iniciales en BD: {initial_count}")
    log_message(f"📁 Archivos JSON iniciales: {initial_files}")
    
    while True:
        try:
            current_time = datetime.now()
            elapsed = current_time - start_time
            
            # Obtener métricas actuales
            current_count = get_database_count()
            current_files = get_json_files_count()
            
            # Calcular progreso
            new_tesis = current_count - initial_count
            new_files = current_files - initial_files
            
            # Mostrar estado
            log_message(f"⏱️  Tiempo transcurrido: {elapsed}")
            log_message(f"📊 Tesis en BD: {current_count} (+{new_tesis})")
            log_message(f"📁 Archivos JSON: {current_files} (+{new_files})")
            log_message(f"📈 Progreso: {new_tesis} nuevas tesis, {new_files} nuevos archivos")
            
            # Verificar si hemos completado 3 horas
            if elapsed.total_seconds() >= 10800:  # 3 horas = 10800 segundos
                log_message("🎯 PRUEBA EXTENDIDA COMPLETADA - 3 HORAS")
                break
                
            # Esperar 5 minutos antes del siguiente reporte
            time.sleep(300)
            
        except Exception as e:
            log_message(f"❌ Error en monitoreo: {e}")
            time.sleep(60)

def main():
    """Función principal de la prueba extendida"""
    print("🚀 INICIANDO PRUEBA EXTENDIDA DE SCRAPING - 3 HORAS")
    print("=" * 60)
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Limpiar log anterior
    with open('logs/extended_test.log', 'w', encoding='utf-8') as f:
        f.write(f"=== PRUEBA EXTENDIDA INICIADA: {datetime.now()} ===\n")
    
    log_message("🎯 PRUEBA EXTENDIDA INICIADA - 3 HORAS DE EJECUCIÓN")
    
    # Iniciar monitoreo en hilo separado
    monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
    monitor_thread.start()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=3)
    cycle_count = 0
    successful_cycles = 0
    
    log_message(f"⏰ Inicio: {start_time}")
    log_message(f"⏰ Fin programado: {end_time}")
    
    try:
        while datetime.now() < end_time:
            cycle_count += 1
            log_message(f"🔄 CICLO #{cycle_count}")
            
            # Ejecutar ciclo de scraping
            if run_single_scraping_cycle():
                successful_cycles += 1
                log_message(f"✅ Ciclo #{cycle_count} completado exitosamente")
            else:
                log_message(f"⚠️  Ciclo #{cycle_count} con problemas")
            
            # Esperar 10 minutos entre ciclos
            log_message("⏳ Esperando 10 minutos antes del siguiente ciclo...")
            time.sleep(600)  # 10 minutos
            
    except KeyboardInterrupt:
        log_message("⚠️  PRUEBA INTERRUMPIDA POR EL USUARIO")
    except Exception as e:
        log_message(f"❌ ERROR CRÍTICO: {e}")
    
    # Resumen final
    final_time = datetime.now()
    total_duration = final_time - start_time
    final_count = get_database_count()
    final_files = get_json_files_count()
    
    log_message("=" * 60)
    log_message("📊 RESUMEN FINAL DE LA PRUEBA EXTENDIDA")
    log_message("=" * 60)
    log_message(f"⏰ Duración total: {total_duration}")
    log_message(f"🔄 Ciclos ejecutados: {cycle_count}")
    log_message(f"✅ Ciclos exitosos: {successful_cycles}")
    log_message(f"📊 Tesis finales en BD: {final_count}")
    log_message(f"📁 Archivos JSON finales: {final_files}")
    log_message(f"📈 Tesis nuevas: {final_count - get_database_count()}")
    log_message(f"📈 Archivos nuevos: {final_files - get_json_files_count()}")
    
    if successful_cycles > 0:
        log_message("🎉 PRUEBA EXTENDIDA COMPLETADA EXITOSAMENTE")
    else:
        log_message("❌ PRUEBA EXTENDIDA SIN ÉXITO")
    
    log_message("=" * 60)

if __name__ == "__main__":
    main() 