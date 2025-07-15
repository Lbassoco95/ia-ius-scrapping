#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("🔍 VERIFICACIÓN DEL SISTEMA DE SCRAPING SCJN")
    print("=" * 50)
    print(f"📂 Directorio: {os.getcwd()}")
    
    # Verificar estructura de archivos
    print("\n📁 Estructura del proyecto:")
    archivos = ['src/', 'data/', 'logs/', 'venv/', '.env', 'credentials/', 'requirements.txt']
    for archivo in archivos:
        exists = "✅" if os.path.exists(archivo) else "❌"
        print(f"  {exists} {archivo}")
    
    # Verificar contenido de directorio src
    if os.path.exists('src/'):
        print("\n📋 Contenido de src/:")
        try:
            for item in os.listdir('src/'):
                print(f"    - {item}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("\n🔧 Variables de entorno (.env):")
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
                for line in lines[:10]:  # Solo primeras 10 líneas
                    if '=' in line and not line.startswith('#'):
                        key = line.split('=')[0]
                        print(f"    ✅ {key}")
        except Exception as e:
            print(f"    ❌ Error leyendo .env: {e}")
    
    # Verificar logs
    if os.path.exists('logs/'):
        print("\n📄 Logs disponibles:")
        try:
            log_files = [f for f in os.listdir('logs/') if f.endswith('.log')]
            if log_files:
                for log_file in log_files[:5]:
                    path = os.path.join('logs/', log_file)
                    size = os.path.getsize(path)
                    print(f"    📄 {log_file} ({size} bytes)")
            else:
                print("    ❌ No hay archivos de log")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Verificar base de datos
    if os.path.exists('data/'):
        print("\n🗄️  Base de datos:")
        try:
            db_files = [f for f in os.listdir('data/') if f.endswith('.db')]
            if db_files:
                for db_file in db_files:
                    path = os.path.join('data/', db_file)
                    size = os.path.getsize(path)
                    print(f"    🗄️  {db_file} ({size} bytes)")
            else:
                print("    ❌ No hay archivos de base de datos")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Verificar procesos
    print("\n🔍 Procesos relacionados:")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        scjn_processes = [line for line in lines if any(keyword in line.lower() for keyword in ['scjn', 'scraper', 'chrome', 'firefox']) and 'grep' not in line]
        if scjn_processes:
            for proc in scjn_processes[:3]:
                if proc.strip():
                    print(f"    🔄 {proc[:80]}...")
        else:
            print("    ❌ No hay procesos relacionados ejecutándose")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Verificar cron jobs
    print("\n⏰ Cron jobs:")
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    print(f"    ⏰ {line}")
        else:
            print("    ❌ No hay cron jobs configurados")
    except Exception as e:
        print("    ❌ Error verificando cron jobs")
    
    print("\n" + "=" * 50)
    print("✅ Verificación completada")

if __name__ == "__main__":
    main() 