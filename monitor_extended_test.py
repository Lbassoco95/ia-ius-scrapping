#!/usr/bin/env python3
"""
Monitoreo en tiempo real de la prueba extendida
"""

import os
import time
from datetime import datetime, timedelta
import sys

sys.path.insert(0, 'src')

def get_current_stats():
    """Obtener estadísticas actuales"""
    try:
        from database.models import get_session, Tesis
        session = get_session()
        total_tesis = session.query(Tesis).count()
        
        # Obtener tesis de las últimas 3 horas
        three_hours_ago = datetime.now() - timedelta(hours=3)
        recent_tesis = session.query(Tesis).filter(
            Tesis.fecha_descarga >= three_hours_ago
        ).count()
        
        session.close()
        
        # Contar archivos JSON
        json_files = [f for f in os.listdir('data') if f.startswith('robust_test_results_') and f.endswith('.json')]
        
        return {
            'total_tesis': total_tesis,
            'recent_tesis': recent_tesis,
            'json_files': len(json_files)
        }
    except Exception as e:
        return {'error': str(e)}

def read_log_tail(lines=10):
    """Leer las últimas líneas del log"""
    try:
        if os.path.exists('logs/extended_test.log'):
            with open('logs/extended_test.log', 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        else:
            return ["Log file not found yet..."]
    except Exception as e:
        return [f"Error reading log: {e}"]

def main():
    """Monitoreo en tiempo real"""
    print("🔍 MONITOREO EN TIEMPO REAL - PRUEBA EXTENDIDA")
    print("=" * 50)
    print("Presiona Ctrl+C para salir")
    print()
    
    try:
        while True:
            # Limpiar pantalla (simulado)
            print("\033[2J\033[H")  # Clear screen
            
            # Obtener estadísticas
            stats = get_current_stats()
            
            # Mostrar estadísticas
            print("📊 ESTADÍSTICAS ACTUALES")
            print("-" * 30)
            if 'error' not in stats:
                print(f"📋 Total tesis en BD: {stats['total_tesis']}")
                print(f"🆕 Tesis últimas 3h: {stats['recent_tesis']}")
                print(f"📁 Archivos JSON: {stats['json_files']}")
            else:
                print(f"❌ Error: {stats['error']}")
            
            print()
            print("📝 ÚLTIMAS ENTRADAS DEL LOG")
            print("-" * 30)
            
            # Mostrar últimas líneas del log
            log_lines = read_log_tail(15)
            for line in log_lines:
                print(line.strip())
            
            print()
            print(f"⏰ Última actualización: {datetime.now().strftime('%H:%M:%S')}")
            print("🔄 Actualizando en 30 segundos...")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoreo detenido por el usuario")
        print("📊 Estadísticas finales:")
        stats = get_current_stats()
        if 'error' not in stats:
            print(f"   Total tesis: {stats['total_tesis']}")
            print(f"   Archivos JSON: {stats['json_files']}")

if __name__ == "__main__":
    main() 