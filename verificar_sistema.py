#!/usr/bin/env python3
"""
Script para verificar el funcionamiento completo del sistema de scraping SCJN
"""

import os
import sys
import json
from datetime import datetime
import traceback

def verificar_configuracion():
    """Verificar que todas las configuraciones estén en su lugar"""
    print("🔧 Verificando configuración...")
    
    # Verificar archivos de configuración
    archivos_requeridos = [
        'service_account.json',
        '.env',
        'logs/'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - Encontrado")
        else:
            print(f"❌ {archivo} - No encontrado")
    
    # Verificar variables de entorno (cargar desde .env si existe)
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    print("\n📋 Variables de entorno:")
    env_vars = ['GOOGLE_DRIVE_ENABLED', 'GOOGLE_DRIVE_FOLDER_ID']
    for var in env_vars:
        value = os.getenv(var, 'No configurado')
        configured = value != 'No configurado' and value != ''
        print(f"  {var}: {'✅ Configurado' if configured else '❌ No configurado'}")
    
    return True

def verificar_estructura_directorios():
    """Verificar estructura de directorios"""
    print("\n📁 Verificando estructura de directorios...")
    
    directorios = ['src/', 'data/', 'logs/', 'credentials/']
    for directorio in directorios:
        if os.path.exists(directorio):
            print(f"✅ {directorio} - Existe")
        else:
            print(f"❌ {directorio} - No existe")
    
    return True

def verificar_python_path():
    """Verificar que el path de Python esté configurado"""
    print("\n🐍 Verificando Python path...")
    
    # Agregar src al path si no está
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✅ Agregado {src_path} al Python path")
    
    return True

def verificar_cloud_sql_proxy():
    """Verificar si Cloud SQL Proxy está corriendo"""
    print("\n☁️ Verificando Cloud SQL Proxy...")
    
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if 'cloud_sql_proxy' in result.stdout:
            print("✅ Cloud SQL Proxy está corriendo")
            return True
        else:
            print("❌ Cloud SQL Proxy no está corriendo")
            print("💡 Ejecuta: ./start_cloud_sql_proxy.sh")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando Cloud SQL Proxy: {str(e)}")
        return False

def verificar_cron_job():
    """Verificar si el cron job está configurado"""
    print("\n⏰ Verificando cron job...")
    
    try:
        import subprocess
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        if result.returncode == 0:
            cron_lines = result.stdout.strip().split('\n')
            cron_scjn = [line for line in cron_lines if 'ia-scrapping-tesis' in line or 'scjn' in line.lower()]
            
            if cron_scjn:
                print("✅ Cron job configurado:")
                for line in cron_scjn:
                    print(f"  {line}")
                return True
            else:
                print("❌ No se encontró cron job para el scraper")
                return False
        else:
            print("❌ Error verificando cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando cron: {str(e)}")
        return False

def verificar_logs():
    """Verificar logs recientes"""
    print("\n📄 Verificando logs...")
    
    if os.path.exists('logs/'):
        log_files = [f for f in os.listdir('logs/') if f.endswith('.log')]
        
        if log_files:
            print(f"✅ Encontrados {len(log_files)} archivos de log")
            
            # Mostrar logs más recientes
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join('logs/', x)), reverse=True)
            
            print("📋 Logs más recientes:")
            for log_file in log_files[:3]:
                path = os.path.join('logs/', log_file)
                size = os.path.getsize(path)
                print(f"  - {log_file} ({size} bytes)")
            
            return True
        else:
            print("❌ No se encontraron archivos de log")
            return False
    else:
        print("❌ Directorio logs/ no existe")
        return False

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencias = [
        'selenium',
        'requests',
        'beautifulsoup4',
        'sqlalchemy',
        'psycopg2-binary',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
        'openai',
        'python-dotenv'
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - No instalado")
            faltantes.append(dep)
    
    if faltantes:
        print(f"\n💡 Instalar dependencias faltantes:")
        print(f"pip install {' '.join(faltantes)}")
        return False
    
    return True

def verificar_base_datos():
    """Verificar conexión a base de datos"""
    print("\n🗄️ Verificando base de datos...")
    
    try:
        from src.database.models import get_session
        session = get_session()
        session.close()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {str(e)}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DEL SISTEMA DE SCRAPING SCJN")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    if 'ia-scrapping-tesis' not in os.getcwd():
        if os.path.exists('ia-scrapping-tesis'):
            os.chdir('ia-scrapping-tesis')
        elif os.path.exists('../ia-scrapping-tesis'):
            os.chdir('../ia-scrapping-tesis')
    
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    resultados = []
    
    # Ejecutar verificaciones básicas
    resultados.append(("Configuración", verificar_configuracion()))
    resultados.append(("Estructura directorios", verificar_estructura_directorios()))
    resultados.append(("Python path", verificar_python_path()))
    resultados.append(("Dependencias", verificar_dependencias()))
    resultados.append(("Base de datos", verificar_base_datos()))
    resultados.append(("Cloud SQL Proxy", verificar_cloud_sql_proxy()))
    resultados.append(("Cron Job", verificar_cron_job()))
    resultados.append(("Logs", verificar_logs()))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    problemas = 0
    for nombre, resultado in resultados:
        status = "✅ OK" if resultado else "❌ PROBLEMA"
        print(f"{nombre}: {status}")
        if not resultado:
            problemas += 1
    
    print(f"\n📈 Resultado: {len(resultados) - problemas}/{len(resultados)} verificaciones exitosas")
    
    if problemas == 0:
        print("\n🎉 ¡Sistema base funcionando correctamente!")
        print("\n💡 Próximos pasos:")
        print("  1. Ejecutar scraping manual: python3 run_scraping_now.py")
        print("  2. Monitorear sistema: python3 monitor_production.py")
        print("  3. Configurar automatización: python3 setup_cron.sh")
    else:
        print(f"\n⚠️  Sistema tiene {problemas} problema(s). Resolver antes de continuar.")
        print("\n🔧 Pasos sugeridos:")
        if not any(resultado for nombre, resultado in resultados if nombre == "Cloud SQL Proxy"):
            print("  - Iniciar Cloud SQL Proxy: ./start_cloud_sql_proxy.sh")
        if not any(resultado for nombre, resultado in resultados if nombre == "Cron Job"):
            print("  - Configurar cron job: crontab -e")
        if not any(resultado for nombre, resultado in resultados if nombre == "Dependencias"):
            print("  - Instalar dependencias: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 