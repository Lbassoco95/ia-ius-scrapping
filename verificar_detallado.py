#!/usr/bin/env python3
"""
Script de verificación detallada del sistema de scraping SCJN
Incluye verificación de entorno virtual, configuración, estructura y importaciones
"""

import os
import sys
import subprocess
import importlib

def verificar_entorno_virtual():
    """Verificar el entorno virtual y Python"""
    print("🐍 VERIFICACIÓN DEL ENTORNO VIRTUAL")
    print("=" * 40)
    
    # Verificar si estamos en un entorno virtual
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Entorno virtual activo: {'✅ Sí' if in_venv else '❌ No'}")
    
    # Verificar versión de Python
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Python version: {result.stdout.strip()}")
        else:
            print("❌ Error obteniendo versión de Python")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Verificar paquetes principales
    print("\n📦 Paquetes principales:")
    paquetes_principales = [
        'selenium', 'requests', 'sqlalchemy', 'beautifulsoup4',
        'google-auth', 'google-api-python-client', 'openai', 'python-dotenv'
    ]
    
    for paquete in paquetes_principales:
        try:
            importlib.import_module(paquete.replace('-', '_'))
            print(f"  ✅ {paquete}")
        except ImportError:
            print(f"  ❌ {paquete} - No instalado")
    
    return True

def verificar_configuracion():
    """Verificar archivo de configuración .env"""
    print("\n🔧 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 40)
    
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        return False
    
    print("📋 Contenido de .env (primeras 10 líneas):")
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10]):
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key = line.split('=')[0]
                        print(f"  ✅ {key}")
                    else:
                        print(f"  📄 {line.strip()}")
                elif line.strip():
                    print(f"  💬 {line.strip()}")
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
        return False
    
    return True

def verificar_estructura_codigo():
    """Verificar estructura del código fuente"""
    print("\n📁 VERIFICACIÓN DE ESTRUCTURA DE CÓDIGO")
    print("=" * 40)
    
    if not os.path.exists('src/'):
        print("❌ Directorio src/ no encontrado")
        return False
    
    print("📋 Archivos Python en src/:")
    try:
        result = subprocess.run(['find', 'src/', '-name', '*.py'], capture_output=True, text=True)
        if result.returncode == 0:
            archivos = result.stdout.strip().split('\n')
            for archivo in archivos[:15]:  # Mostrar primeros 15 archivos
                if archivo:
                    print(f"  📄 {archivo}")
            if len(archivos) > 15:
                print(f"  ... y {len(archivos) - 15} archivos más")
        else:
            print("❌ Error buscando archivos Python")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Verificar módulos principales
    print("\n📦 Módulos principales:")
    modulos_principales = [
        'src/database', 'src/scraper', 'src/storage', 
        'src/analysis', 'src/api', 'src/automation'
    ]
    
    for modulo in modulos_principales:
        if os.path.exists(modulo):
            archivos = len([f for f in os.listdir(modulo) if f.endswith('.py')])
            print(f"  ✅ {modulo}/ ({archivos} archivos)")
        else:
            print(f"  ❌ {modulo}/ - No existe")
    
    return True

def probar_importaciones():
    """Probar importaciones básicas del sistema"""
    print("\n🧪 PRUEBAS DE IMPORTACIONES")
    print("=" * 40)
    
    # Agregar src al path
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Pruebas de importación
    pruebas = [
        ('database.models', 'get_session'),
        ('scraper.selenium_scraper', 'SeleniumScraper'),
        ('storage.google_drive', 'GoogleDriveService'),
        ('config', 'Config'),
        ('automation.auto_scraper', 'AutoScraper')
    ]
    
    for modulo, clase in pruebas:
        try:
            mod = importlib.import_module(modulo)
            if hasattr(mod, clase):
                print(f"  ✅ {modulo}.{clase} - OK")
            else:
                print(f"  ⚠️  {modulo}.{clase} - Módulo OK, clase no encontrada")
        except ImportError as e:
            print(f"  ❌ {modulo}.{clase} - Error: {e}")
        except Exception as e:
            print(f"  ❌ {modulo}.{clase} - Error: {e}")
    
    return True

def verificar_base_datos():
    """Verificar conexión a base de datos"""
    print("\n🗄️ VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 40)
    
    try:
        # Agregar src al path
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from database.models import get_session
        session = get_session()
        session.close()
        print("✅ Conexión a base de datos exitosa")
        
        # Verificar archivos de BD
        if os.path.exists('data/'):
            db_files = [f for f in os.listdir('data/') if f.endswith('.db')]
            if db_files:
                for db_file in db_files:
                    path = os.path.join('data/', db_file)
                    size = os.path.getsize(path)
                    print(f"  🗄️  {db_file} ({size} bytes)")
            else:
                print("  ⚠️  No hay archivos de base de datos")
        
        return True
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        return False

def ejecutar_scripts_prueba():
    """Ejecutar scripts de prueba disponibles"""
    print("\n🚀 EJECUCIÓN DE SCRIPTS DE PRUEBA")
    print("=" * 40)
    
    scripts_prueba = [
        'simple_test_vm.py',
        'test_basic_scraping.py',
        'test_system.py',
        'test_final_system.py'
    ]
    
    for script in scripts_prueba:
        if os.path.exists(script):
            print(f"\n📋 Ejecutando {script}:")
            try:
                result = subprocess.run(['python3', script], 
                                      capture_output=True, text=True, 
                                      timeout=30)  # Timeout de 30 segundos
                
                if result.returncode == 0:
                    print(f"  ✅ {script} - Exitoso")
                    # Mostrar primeras líneas de salida
                    output_lines = result.stdout.strip().split('\n')
                    for line in output_lines[:5]:
                        if line.strip():
                            print(f"    📄 {line}")
                    if len(output_lines) > 5:
                        print(f"    ... y {len(output_lines) - 5} líneas más")
                else:
                    print(f"  ❌ {script} - Falló")
                    if result.stderr.strip():
                        print(f"    Error: {result.stderr.strip()}")
                        
            except subprocess.TimeoutExpired:
                print(f"  ⏰ {script} - Timeout (30s)")
            except Exception as e:
                print(f"  ❌ {script} - Error: {e}")
        else:
            print(f"  ⚠️  {script} - No encontrado")
    
    return True

def verificar_logs_recientes():
    """Verificar logs recientes del sistema"""
    print("\n📄 VERIFICACIÓN DE LOGS RECIENTES")
    print("=" * 40)
    
    if not os.path.exists('logs/'):
        print("❌ Directorio logs/ no existe")
        return False
    
    try:
        # Encontrar el log más reciente
        result = subprocess.run([
            'find', 'logs/', '-name', '*.log', '-type', 'f', 
            '-exec', 'ls', '-t', '{}', '+'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            log_files = result.stdout.strip().split('\n')
            if log_files:
                ultimo_log = log_files[0]
                print(f"📄 Último log: {ultimo_log}")
                
                # Mostrar últimas 20 líneas del log más reciente
                try:
                    tail_result = subprocess.run([
                        'tail', '-20', ultimo_log
                    ], capture_output=True, text=True)
                    
                    if tail_result.returncode == 0:
                        print("📋 Últimas 20 líneas:")
                        lines = tail_result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                print(f"    📄 {line}")
                    else:
                        print("❌ Error leyendo el log")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("❌ No se encontraron archivos de log")
        else:
            print("❌ No hay logs recientes")
            
    except Exception as e:
        print(f"❌ Error verificando logs: {e}")
    
    # Mostrar estadísticas de logs
    try:
        log_files = [f for f in os.listdir('logs/') if f.endswith('.log')]
        if log_files:
            print(f"\n📊 Estadísticas de logs:")
            print(f"  📄 Total de archivos de log: {len(log_files)}")
            
            # Mostrar logs más grandes
            log_sizes = []
            for log_file in log_files:
                path = os.path.join('logs/', log_file)
                size = os.path.getsize(path)
                log_sizes.append((log_file, size))
            
            log_sizes.sort(key=lambda x: x[1], reverse=True)
            print("  📄 Logs más grandes:")
            for log_file, size in log_sizes[:3]:
                print(f"    📄 {log_file} ({size} bytes)")
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
    
    return True

def verificar_servicios():
    """Verificar servicios del sistema"""
    print("\n🔍 VERIFICACIÓN DE SERVICIOS")
    print("=" * 40)
    
    # Verificar procesos
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        scjn_processes = [line for line in lines if any(keyword in line.lower() for keyword in ['scjn', 'scraper', 'chrome', 'firefox']) and 'grep' not in line]
        
        if scjn_processes:
            print("🔄 Procesos relacionados:")
            for proc in scjn_processes[:3]:
                if proc.strip():
                    print(f"  🔄 {proc[:80]}...")
        else:
            print("❌ No hay procesos relacionados ejecutándose")
    except Exception as e:
        print(f"❌ Error verificando procesos: {e}")
    
    # Verificar cron jobs
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("\n⏰ Cron jobs configurados:")
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    if 'ia-scrapping-tesis' in line or 'scjn' in line.lower():
                        print(f"  ⏰ {line}")
        else:
            print("\n❌ No hay cron jobs configurados")
    except Exception as e:
        print(f"\n❌ Error verificando cron jobs: {e}")
    
    return True

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DETALLADA DEL SISTEMA DE SCRAPING SCJN")
    print("=" * 60)
    print(f"📂 Directorio: {os.getcwd()}")
    print(f"🕐 Fecha: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("Entorno virtual", verificar_entorno_virtual()))
    resultados.append(("Configuración", verificar_configuracion()))
    resultados.append(("Estructura código", verificar_estructura_codigo()))
    resultados.append(("Importaciones", probar_importaciones()))
    resultados.append(("Base de datos", verificar_base_datos()))
    resultados.append(("Scripts de prueba", ejecutar_scripts_prueba()))
    resultados.append(("Logs recientes", verificar_logs_recientes()))
    resultados.append(("Servicios", verificar_servicios()))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN DETALLADA")
    print("=" * 60)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        status = "✅ OK" if resultado else "❌ PROBLEMA"
        print(f"{nombre}: {status}")
    
    print(f"\n📈 Resultado: {exitosos}/{total} verificaciones exitosas")
    
    if exitosos == total:
        print("\n🎉 ¡Sistema completamente funcional!")
        print("\n💡 Próximos pasos:")
        print("  1. Ejecutar scraping: python3 run_scraping_now.py")
        print("  2. Monitorear: python3 monitor_production.py")
        print("  3. Verificar logs: tail -f logs/production.log")
    else:
        print(f"\n⚠️  Sistema tiene {total - exitosos} problema(s).")
        print("🔧 Revisar y corregir antes de continuar.")

if __name__ == "__main__":
    main() 