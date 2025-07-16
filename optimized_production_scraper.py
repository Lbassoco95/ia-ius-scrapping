#!/usr/bin/env python3
"""
SCRAPER DE PRODUCCIÓN OPTIMIZADO - SCJN
Sistema completo optimizado con todas las mejoras:
- Configuración robusta
- Logging avanzado
- Paralelización inteligente
- Manejo robusto de errores
- Monitoreo de performance
- Cache inteligente
"""

import sys
import os
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Agregar src al path
sys.path.insert(0, 'src')

def signal_handler(signum, frame):
    """Manejar señales del sistema para shutdown limpio"""
    print(f"\n⚠️ Recibida señal {signum}, cerrando sistema de forma segura...")
    sys.exit(0)

def setup_signal_handlers():
    """Configurar manejadores de señales"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_system_requirements():
    """Verificar requerimientos del sistema"""
    print("🔍 VERIFICANDO REQUERIMIENTOS DEL SISTEMA")
    print("-" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ requerido, encontrado: {sys.version}")
        return False
    print(f"✅ Python: {sys.version.split()[0]}")
    
    # Verificar dependencias críticas
    critical_deps = [
        ('selenium', 'selenium'),
        ('requests', 'requests'),
        ('sqlalchemy', 'sqlalchemy'),
        ('google.auth', 'google-auth'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_deps = []
    for dep_name, import_name in critical_deps:
        try:
            __import__(import_name)
            print(f"✅ {dep_name}")
        except ImportError:
            print(f"❌ {dep_name} - FALTANTE")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\n❌ Dependencias faltantes: {', '.join(missing_deps)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def validate_environment():
    """Validar configuración del entorno"""
    print("\n🔧 VALIDANDO CONFIGURACIÓN")
    print("-" * 30)
    
    try:
        from src.config import get_config, ConfigurationError
        
        # Obtener configuración de producción
        config = get_config("production")
        
        # Validar configuración
        if not config.validate_config():
            print("❌ Configuración inválida")
            return False, None
        
        print("✅ Configuración validada")
        return True, config
        
    except ConfigurationError as e:
        print(f"❌ Error de configuración: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Error inesperado en configuración: {e}")
        return False, None

def check_database_connection(config):
    """Verificar conexión a base de datos"""
    print("\n🗄️ VERIFICANDO BASE DE DATOS")
    print("-" * 30)
    
    try:
        from src.database.models import create_tables, get_session, Tesis
        
        # Crear tablas si no existen
        create_tables()
        print("✅ Tablas de base de datos verificadas")
        
        # Verificar conexión
        session = get_session()
        total_tesis = session.query(Tesis).count()
        session.close()
        
        print(f"✅ Conexión exitosa - Tesis en BD: {total_tesis:,}")
        return True
        
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        return False

def check_google_drive_setup(config):
    """Verificar configuración de Google Drive"""
    if not config.GOOGLE_DRIVE_ENABLED:
        print("\nℹ️ Google Drive deshabilitado")
        return True
    
    print("\n☁️ VERIFICANDO GOOGLE DRIVE")
    print("-" * 30)
    
    try:
        from src.storage.google_drive_service import GoogleDriveServiceManager
        
        drive_manager = GoogleDriveServiceManager()
        drive_manager.authenticate()
        
        print("✅ Autenticación con Google Drive exitosa")
        print(f"✅ Folder ID configurado: {config.GOOGLE_DRIVE_FOLDER_ID}")
        return True
        
    except Exception as e:
        print(f"❌ Error de Google Drive: {e}")
        print("⚠️ Continuando sin Google Drive...")
        return False

def run_system_diagnostics(config):
    """Ejecutar diagnósticos del sistema"""
    print("\n🔍 DIAGNÓSTICOS DEL SISTEMA")
    print("=" * 50)
    
    diagnostics = {
        "base_de_datos": check_database_connection(config),
        "google_drive": check_google_drive_setup(config)
    }
    
    # Verificar espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage(config.DATA_DIR)
        free_gb = free / (1024**3)
        
        if free_gb < 1:  # Menos de 1GB libre
            print(f"⚠️ Poco espacio libre: {free_gb:.1f}GB")
        else:
            print(f"✅ Espacio libre: {free_gb:.1f}GB")
            
        diagnostics["espacio_disco"] = free_gb > 1
        
    except Exception as e:
        print(f"⚠️ No se pudo verificar espacio en disco: {e}")
        diagnostics["espacio_disco"] = True
    
    # Verificar conectividad
    try:
        import requests
        response = requests.get(config.SCJN_BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Conectividad con SCJN: OK")
            diagnostics["conectividad"] = True
        else:
            print(f"⚠️ SCJN responde con código: {response.status_code}")
            diagnostics["conectividad"] = False
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        diagnostics["conectividad"] = False
    
    # Resumen de diagnósticos
    passed = sum(diagnostics.values())
    total = len(diagnostics)
    
    print(f"\n📊 RESUMEN: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("✅ Sistema listo para producción")
        return True
    else:
        print("⚠️ Sistema con advertencias, pero puede continuar")
        return True  # Continuar aunque haya advertencias

def create_monitoring_session(config):
    """Crear sesión de monitoreo"""
    try:
        session_data = {
            "session_id": f"prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment": "production",
            "start_time": datetime.now().isoformat(),
            "config": {
                "max_documents": config.MAX_DOCUMENTS_PER_RUN,
                "max_hours": config.MAX_HOURS_PER_SESSION,
                "parallel_downloads": config.PARALLEL_DOWNLOADS,
                "batch_size": config.BATCH_SIZE
            }
        }
        
        # Guardar sesión para monitoreo
        session_file = config.DATA_DIR / "current_session.json"
        import json
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        return session_data
        
    except Exception as e:
        print(f"⚠️ Error creando sesión de monitoreo: {e}")
        return {"session_id": "unknown", "start_time": datetime.now().isoformat()}

def run_optimized_scraping(config, session_data):
    """Ejecutar scraping optimizado"""
    print("\n🚀 INICIANDO SCRAPING OPTIMIZADO")
    print("=" * 60)
    
    try:
        from src.scraper.optimized_scraper import OptimizedSCJNScraper
        from src.utils.logger import setup_logging
        
        # Configurar logging optimizado
        logger = setup_logging("production_scraper", config)
        
        # Loggear información de sesión
        logger.info("🚀 INICIANDO SESIÓN DE SCRAPING OPTIMIZADA")
        for key, value in session_data.items():
            if key != "config":
                logger.info(f"   {key}: {value}")
        
        # Configurar parámetros de producción
        max_documents = config.MAX_DOCUMENTS_PER_RUN
        max_hours = config.MAX_HOURS_PER_SESSION
        
        logger.info("⚙️ CONFIGURACIÓN DE PRODUCCIÓN:")
        logger.info(f"   📊 Documentos máximos: {max_documents}")
        logger.info(f"   ⏰ Tiempo máximo: {max_hours} horas")
        logger.info(f"   ⚡ Descargas paralelas: {config.PARALLEL_DOWNLOADS}")
        logger.info(f"   📦 Tamaño de lote: {config.BATCH_SIZE}")
        logger.info(f"   🔄 Máximo reintentos: {config.MAX_RETRIES}")
        
        # Inicializar scraper optimizado
        scraper = OptimizedSCJNScraper(config)
        
        # Ejecutar scraping con límite de tiempo
        start_time = time.time()
        max_seconds = max_hours * 3600
        
        logger.info(f"⏰ Tiempo máximo: {max_seconds/3600:.1f} horas")
        
        # Ejecutar scraping
        session_stats = scraper.run_complete_scraping(max_documents=max_documents)
        
        # Calcular duración real
        actual_duration = time.time() - start_time
        
        # Log resumen final
        logger.info("=" * 60)
        logger.info("🎯 RESUMEN FINAL DE PRODUCCIÓN")
        logger.info("=" * 60)
        logger.info(f"⏱️ Duración real: {actual_duration/3600:.2f} horas")
        logger.info(f"📊 Total procesados: {session_stats.total_processed}")
        logger.info(f"✅ Exitosos: {session_stats.successful}")
        logger.info(f"❌ Fallidos: {session_stats.failed}")
        logger.info(f"📄 PDFs descargados: {session_stats.pdfs_downloaded}")
        logger.info(f"☁️ Subidos a Drive: {session_stats.uploaded_to_drive}")
        
        if session_stats.successful > 0:
            success_rate = (session_stats.successful / session_stats.total_processed) * 100
            logger.info(f"📈 Tasa de éxito: {success_rate:.1f}%")
            
            throughput = session_stats.total_processed / (actual_duration / 3600)
            logger.info(f"⚡ Throughput: {throughput:.1f} tesis/hora")
        
        if session_stats.errors:
            logger.warning(f"⚠️ Errores encontrados: {len(session_stats.errors)}")
            
        logger.info("=" * 60)
        
        return session_stats
        
    except Exception as e:
        print(f"❌ Error crítico en scraping: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_session_results(config, session_data, session_stats):
    """Guardar resultados de la sesión"""
    try:
        if not session_stats:
            return
            
        # Actualizar datos de sesión
        session_data.update({
            "end_time": datetime.now().isoformat(),
            "duration_hours": session_stats.total_time / 3600,
            "results": {
                "total_processed": session_stats.total_processed,
                "successful": session_stats.successful,
                "failed": session_stats.failed,
                "pdfs_downloaded": session_stats.pdfs_downloaded,
                "uploaded_to_drive": session_stats.uploaded_to_drive,
                "errors_count": len(session_stats.errors),
                "success_rate": (session_stats.successful / max(1, session_stats.total_processed)) * 100
            }
        })
        
        # Guardar historial de sesiones
        import json
        history_file = config.DATA_DIR / "session_history.json"
        
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        history.append(session_data)
        
        # Mantener solo las últimas 100 sesiones
        if len(history) > 100:
            history = history[-100:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        
        print(f"✅ Resultados guardados en {history_file}")
        
    except Exception as e:
        print(f"⚠️ Error guardando resultados: {e}")

def cleanup_old_files(config):
    """Limpiar archivos antiguos"""
    try:
        print("\n🧹 LIMPIEZA DE ARCHIVOS")
        print("-" * 25)
        
        # Limpiar logs antiguos (más de 30 días)
        logs_dir = config.LOGS_DIR
        if logs_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=30)
            
            cleaned = 0
            for log_file in logs_dir.glob("*.log.*"):
                try:
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                        log_file.unlink()
                        cleaned += 1
                except:
                    pass
            
            if cleaned > 0:
                print(f"✅ Logs antiguos limpiados: {cleaned}")
        
        # Limpiar cache antigua
        cache_file = config.DATA_DIR / "scraping_cache.json"
        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Si el cache tiene más de 7 días, limpiarlo parcialmente
                if 'last_updated' in cache_data:
                    last_update = datetime.fromisoformat(cache_data['last_updated'])
                    if datetime.now() - last_update > timedelta(days=7):
                        # Mantener solo las URLs más recientes
                        if len(cache_data.get('processed_urls', [])) > 10000:
                            cache_data['processed_urls'] = cache_data['processed_urls'][-5000:]
                            cache_data['last_updated'] = datetime.now().isoformat()
                            
                            with open(cache_file, 'w') as f:
                                json.dump(cache_data, f, indent=2)
                            
                            print("✅ Cache optimizado")
            except:
                pass
        
    except Exception as e:
        print(f"⚠️ Error en limpieza: {e}")

def main():
    """Función principal del scraper de producción optimizado"""
    print("🏛️ IA-IUS-SCRAPPING: SCRAPER DE PRODUCCIÓN OPTIMIZADO")
    print("=" * 70)
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Configurar manejadores de señales
    setup_signal_handlers()
    
    try:
        # 1. Verificar requerimientos
        if not check_system_requirements():
            print("❌ Sistema no cumple con los requerimientos")
            return 1
        
        # 2. Validar configuración
        valid, config = validate_environment()
        if not valid:
            print("❌ Configuración inválida")
            return 1
        
        # 3. Ejecutar diagnósticos
        if not run_system_diagnostics(config):
            print("❌ Diagnósticos fallaron")
            return 1
        
        # 4. Crear sesión de monitoreo
        session_data = create_monitoring_session(config)
        
        # 5. Ejecutar scraping optimizado
        session_stats = run_optimized_scraping(config, session_data)
        
        # 6. Guardar resultados
        save_session_results(config, session_data, session_stats)
        
        # 7. Limpiar archivos antiguos
        cleanup_old_files(config)
        
        # 8. Resumen final
        print("\n" + "=" * 70)
        print("🎯 EJECUCIÓN COMPLETADA")
        print("=" * 70)
        
        if session_stats:
            print(f"📊 Tesis procesadas: {session_stats.total_processed}")
            print(f"✅ Exitosas: {session_stats.successful}")
            print(f"⏱️ Tiempo total: {session_stats.total_time/3600:.2f} horas")
            
            if session_stats.total_processed > 0:
                success_rate = (session_stats.successful / session_stats.total_processed) * 100
                print(f"📈 Tasa de éxito: {success_rate:.1f}%")
            
            print("✅ Scraping completado exitosamente")
        else:
            print("⚠️ Scraping completado con errores")
        
        print(f"🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupción por usuario")
        return 2
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)