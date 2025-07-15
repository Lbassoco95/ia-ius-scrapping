#!/usr/bin/env python3
"""
Script de monitoreo del sistema de scraping
"""

import sys
import os
import json
from datetime import datetime, timedelta
import glob

sys.path.insert(0, 'src')

def check_database():
    """Verificar estado de la base de datos"""
    print("📊 VERIFICANDO BASE DE DATOS")
    print("-" * 30)
    
    try:
        from database.models import get_session, Tesis
        
        session = get_session()
        total_tesis = session.query(Tesis).count()
        
        # Obtener la tesis más reciente
        latest_tesis = session.query(Tesis).order_by(Tesis.fecha_descarga.desc()).first()
        
        print(f"📋 Total de tesis: {total_tesis}")
        
        if latest_tesis:
            print(f"📅 Última tesis descargada: {latest_tesis.fecha_descarga}")
            print(f"🆔 ID de última tesis: {latest_tesis.scjn_id}")
        else:
            print("⚠️  No hay tesis en la base de datos")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def check_json_files():
    """Verificar archivos JSON de resultados"""
    print("\n📄 VERIFICANDO ARCHIVOS JSON")
    print("-" * 30)
    
    try:
        json_files = glob.glob('data/robust_test_results_*.json')
        
        if not json_files:
            print("⚠️  No se encontraron archivos JSON")
            return False
        
        print(f"📁 Total archivos JSON: {len(json_files)}")
        
        # Ordenar por fecha de modificación
        json_files.sort(key=os.path.getmtime, reverse=True)
        
        latest_file = json_files[0]
        latest_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        
        print(f"📅 Archivo más reciente: {os.path.basename(latest_file)}")
        print(f"⏰ Fecha de modificación: {latest_time}")
        
        # Verificar contenido del archivo más reciente
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                print(f"📊 Resultados en archivo: {len(data)}")
            else:
                print(f"📊 Estructura del archivo: {type(data)}")
                
        except Exception as e:
            print(f"⚠️  Error leyendo archivo JSON: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos JSON: {e}")
        return False

def check_logs():
    """Verificar archivos de logs"""
    print("\n📝 VERIFICANDO LOGS")
    print("-" * 30)
    
    log_files = [
        'logs/cron_scraper.log',
        'logs/scraper.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            
            print(f"📄 {log_file}:")
            print(f"   📏 Tamaño: {file_size} bytes")
            print(f"   ⏰ Última modificación: {mod_time}")
            
            # Mostrar últimas líneas del log
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   📋 Últimas 3 líneas:")
                        for line in lines[-3:]:
                            print(f"      {line.strip()}")
            except Exception as e:
                print(f"   ⚠️  Error leyendo log: {e}")
        else:
            print(f"⚠️  {log_file}: No existe")

def check_cron_jobs():
    """Verificar cron jobs configurados"""
    print("\n⏰ VERIFICANDO CRON JOBS")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print("📋 Cron jobs configurados:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("⚠️  No hay cron jobs configurados")
            
    except Exception as e:
        print(f"❌ Error verificando cron jobs: {e}")

def main():
    print("🔍 MONITOREO DEL SISTEMA DE SCRAPING")
    print("=" * 50)
    print(f"⏰ Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar cada componente
    db_ok = check_database()
    json_ok = check_json_files()
    check_logs()
    check_cron_jobs()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEL ESTADO")
    print("-" * 30)
    
    if db_ok and json_ok:
        print("✅ Sistema funcionando correctamente")
    else:
        print("⚠️  Hay problemas en el sistema")
    
    print("\n🔧 COMANDOS ÚTILES:")
    print("- Ejecutar scraper completo: python3 run_complete_scraper.py")
    print("- Ver logs en tiempo real: tail -f logs/cron_scraper.log")
    print("- Configurar cron: bash setup_cron_complete.sh")
    print("- Verificar BD: python3 -c \"import sys; sys.path.insert(0, 'src'); from database.models import get_session, Tesis; session = get_session(); print(f'Total: {session.query(Tesis).count()}'); session.close()\"")

if __name__ == "__main__":
    main()
