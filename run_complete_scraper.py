#!/usr/bin/env python3
"""
Script completo para ejecutar scraping e integración de resultados
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔄 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("📤 SALIDA:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  ERRORES:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - EXITOSO")
            return True
        else:
            print(f"❌ {description} - FALLÓ (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    print("🚀 INICIANDO PROCESO COMPLETO DE SCRAPING")
    print("=" * 60)
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Paso 1: Ejecutar scraper robusto
    success = run_command(
        "python3 robust_scraper.py",
        "Ejecutando scraper robusto"
    )
    
    if not success:
        print("❌ Falló el scraping. Deteniendo proceso.")
        return False
    
    # Esperar un momento para que se complete la escritura de archivos
    print("\n⏳ Esperando 5 segundos para completar escritura de archivos...")
    time.sleep(5)
    
    # Paso 2: Integrar resultados a la base de datos
    success = run_command(
        "python3 integrate_results_fixed.py",
        "Integrando resultados a la base de datos"
    )
    
    if not success:
        print("❌ Falló la integración. Verificar manualmente.")
        return False
    
    # Paso 3: Verificar estado final
    print("\n📊 VERIFICANDO ESTADO FINAL")
    print("=" * 50)
    
    # Contar archivos JSON generados
    json_files = [f for f in os.listdir('data') if f.startswith('robust_test_results_') and f.endswith('.json')]
    print(f"📄 Archivos JSON generados: {len(json_files)}")
    
    # Verificar base de datos
    db_check = run_command(
        "python3 -c \"import sys; sys.path.insert(0, 'src'); from database.models import get_session, Tesis; session = get_session(); count = session.query(Tesis).count(); print(f'📊 Total tesis en BD: {count}'); session.close()\"",
        "Verificando base de datos"
    )
    
    print(f"\n🎉 PROCESO COMPLETADO")
    print(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 