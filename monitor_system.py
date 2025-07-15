#!/usr/bin/env python3
"""
Monitor del sistema de scraping SCJN
"""

import sys
import os
import json
from datetime import datetime, timedelta
sys.path.insert(0, 'src')

def check_system_status():
    """Verificar estado del sistema"""
    print("🔍 MONITOR DEL SISTEMA SCJN")
    print("=" * 40)
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'database': {},
        'files': {},
        'processes': {},
        'logs': {}
    }
    
    try:
        # Verificar base de datos
        from database.models import get_session, Tesis, ScrapingSession
        
        session = get_session()
        total_tesis = session.query(Tesis).count()
        recent_tesis = session.query(Tesis).filter(
            Tesis.fecha_descarga >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Última sesión
        last_session = session.query(ScrapingSession).order_by(
            ScrapingSession.fecha_inicio.desc()
        ).first()
        
        session.close()
        
        status['database'] = {
            'total_tesis': total_tesis,
            'recent_tesis': recent_tesis,
            'last_session': last_session.fecha_inicio.isoformat() if last_session else None
        }
        
        print(f"🗄️  Base de datos: {total_tesis} tesis total, {recent_tesis} recientes")
        
    except Exception as e:
        status['database']['error'] = str(e)
        print(f"❌ Error base de datos: {e}")
    
    # Verificar archivos
    try:
        db_size = os.path.getsize('data/scjn_database.db') if os.path.exists('data/scjn_database.db') else 0
        log_files = [f for f in os.listdir('logs') if f.endswith('.log')] if os.path.exists('logs') else []
        
        status['files'] = {
            'database_size_mb': round(db_size / (1024*1024), 2),
            'log_files': log_files
        }
        
        print(f"📁 Archivos: BD {status['files']['database_size_mb']}MB, {len(log_files)} logs")
        
    except Exception as e:
        status['files']['error'] = str(e)
        print(f"❌ Error archivos: {e}")
    
    # Verificar procesos
    try:
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'python.*scraper'], capture_output=True, text=True)
        processes = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        status['processes'] = {
            'scraper_processes': len(processes)
        }
        
        print(f"🔄 Procesos: {len(processes)} scraper activos")
        
    except Exception as e:
        status['processes']['error'] = str(e)
        print(f"❌ Error procesos: {e}")
    
    # Verificar logs recientes
    try:
        if os.path.exists('logs/cron_scraper.log'):
            with open('logs/cron_scraper.log', 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                status['logs']['recent_entries'] = recent_lines
                print(f"📄 Logs: {len(lines)} líneas total")
        else:
            status['logs']['recent_entries'] = []
            print("📄 Logs: No hay archivo de log")
            
    except Exception as e:
        status['logs']['error'] = str(e)
        print(f"❌ Error logs: {e}")
    
    # Guardar estado
    with open('data/system_status.json', 'w') as f:
        json.dump(status, f, indent=2, default=str)
    
    print(f"\n✅ Estado guardado en: data/system_status.json")
    
    return status

def show_recommendations(status):
    """Mostrar recomendaciones basadas en el estado"""
    print("\n💡 RECOMENDACIONES:")
    print("=" * 30)
    
    if status['database']['total_tesis'] == 0:
        print("🚀 Ejecuta el scraper: python3 run_scraper.py")
    
    if status['database']['recent_tesis'] == 0:
        print("⏰ Configura cron job: ./setup_cron.sh")
    
    if status['files']['database_size_mb'] > 100:
        print("🗂️  Considera limpiar datos antiguos")
    
    if status['processes']['scraper_processes'] > 1:
        print("⚠️  Múltiples procesos activos - verifica")

if __name__ == "__main__":
    status = check_system_status()
    show_recommendations(status) 