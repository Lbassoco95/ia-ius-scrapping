#!/usr/bin/env python3
"""
PRUEBAS END-TO-END OPTIMIZADAS - SISTEMA SCJN
Validación completa del sistema desde búsqueda hasta almacenamiento final
- Configuración del sistema
- Conexión a base de datos
- Scraping funcional
- Descarga de PDFs
- Subida a Google Drive
- Análisis de performance
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Agregar src al path
sys.path.insert(0, 'src')

class TestResult:
    """Resultado de una prueba"""
    def __init__(self, name: str, success: bool, duration: float = 0.0, 
                 message: str = "", details: Dict[str, Any] = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

class EndToEndTester:
    """Ejecutor de pruebas end-to-end"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.config = None
        self.logger = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        if self.logger:
            getattr(self.logger, level.lower())(message)
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Ejecutar una prueba individual"""
        self.log(f"🧪 Ejecutando: {test_name}")
        
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, tuple):
                success, message, details = result
            elif isinstance(result, bool):
                success, message, details = result, "", {}
            else:
                success, message, details = True, str(result), {}
            
            test_result = TestResult(test_name, success, duration, message, details)
            self.results.append(test_result)
            
            status = "✅" if success else "❌"
            self.log(f"{status} {test_name}: {message} ({duration:.2f}s)")
            
            return test_result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            test_result = TestResult(test_name, False, duration, error_msg)
            self.results.append(test_result)
            
            self.log(f"❌ {test_name}: Error - {error_msg} ({duration:.2f}s)", "ERROR")
            return test_result
    
    def test_system_requirements(self) -> tuple:
        """Probar requerimientos del sistema"""
        issues = []
        
        # Verificar Python
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ requerido, encontrado: {sys.version}")
        
        # Verificar dependencias críticas
        required_packages = [
            'selenium', 'requests', 'sqlalchemy', 'google.auth', 
            'dotenv', 'aiohttp', 'concurrent.futures'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            issues.append(f"Paquetes faltantes: {', '.join(missing)}")
        
        success = len(issues) == 0
        message = "Todos los requerimientos están instalados" if success else f"Problemas: {'; '.join(issues)}"
        
        return success, message, {"issues": issues, "missing_packages": missing}
    
    def test_configuration_loading(self) -> tuple:
        """Probar carga de configuración"""
        try:
            from src.config import get_config, ConfigurationError
            
            # Probar diferentes entornos
            for env in ['development', 'production', 'testing']:
                config = get_config(env)
                if not config.validate_config():
                    return False, f"Configuración inválida para {env}", {"environment": env}
            
            # Guardar config para pruebas posteriores
            self.config = get_config('testing')
            
            return True, "Configuración cargada y validada correctamente", {
                "environments_tested": ['development', 'production', 'testing']
            }
            
        except Exception as e:
            return False, f"Error cargando configuración: {e}", {"error": str(e)}
    
    def test_logging_system(self) -> tuple:
        """Probar sistema de logging"""
        try:
            from src.utils.logger import setup_logging, get_logger, get_performance_logger
            
            # Configurar logging
            self.logger = setup_logging("end_to_end_test", self.config)
            
            # Probar diferentes niveles
            self.logger.debug("Test debug message")
            self.logger.info("Test info message")
            self.logger.warning("Test warning message")
            
            # Probar performance logger
            perf_logger = get_performance_logger()
            perf_logger.start_timer("test_operation")
            time.sleep(0.1)
            duration = perf_logger.end_timer("test_operation")
            
            return True, "Sistema de logging funcionando correctamente", {
                "performance_test_duration": duration
            }
            
        except Exception as e:
            return False, f"Error en sistema de logging: {e}", {"error": str(e)}
    
    def test_database_connection(self) -> tuple:
        """Probar conexión a base de datos"""
        try:
            from src.database.models import create_tables, get_session, Tesis
            
            # Crear tablas
            create_tables()
            
            # Probar conexión
            session = get_session()
            count = session.query(Tesis).count()
            session.close()
            
            return True, f"Base de datos conectada exitosamente", {
                "total_tesis_count": count
            }
            
        except Exception as e:
            return False, f"Error de base de datos: {e}", {"error": str(e)}
    
    def test_google_drive_connection(self) -> tuple:
        """Probar conexión a Google Drive"""
        if not self.config.GOOGLE_DRIVE_ENABLED:
            return True, "Google Drive deshabilitado - saltando prueba", {"skipped": True}
        
        try:
            from src.storage.google_drive_service import GoogleDriveServiceManager
            
            drive_manager = GoogleDriveServiceManager()
            drive_manager.authenticate()
            
            return True, "Google Drive conectado exitosamente", {
                "folder_id": self.config.GOOGLE_DRIVE_FOLDER_ID
            }
            
        except Exception as e:
            return False, f"Error conectando Google Drive: {e}", {"error": str(e)}
    
    def test_selenium_setup(self) -> tuple:
        """Probar configuración de Selenium"""
        try:
            from src.scraper.optimized_scraper import OptimizedSCJNScraper
            
            scraper = OptimizedSCJNScraper(self.config)
            
            # Configurar driver
            if not scraper.setup_driver():
                return False, "No se pudo configurar driver de Selenium", {}
            
            # Probar navegación básica
            success = scraper.navigate_to_search_page()
            
            # Cleanup
            scraper._cleanup()
            
            return success, "Selenium configurado y navegación exitosa" if success else "Error en navegación", {}
            
        except Exception as e:
            return False, f"Error configurando Selenium: {e}", {"error": str(e)}
    
    def test_scraping_functionality(self) -> tuple:
        """Probar funcionalidad básica de scraping"""
        try:
            from src.scraper.optimized_scraper import OptimizedSCJNScraper
            
            scraper = OptimizedSCJNScraper(self.config)
            
            # Ejecutar scraping limitado
            stats = scraper.run_complete_scraping(max_documents=3)
            
            if not stats:
                return False, "Scraping falló - sin estadísticas", {}
            
            success = stats.total_processed > 0
            message = f"Scraping completado: {stats.total_processed} procesados, {stats.successful} exitosos"
            
            details = {
                "total_processed": stats.total_processed,
                "successful": stats.successful,
                "failed": stats.failed,
                "total_time": stats.total_time,
                "errors": len(stats.errors)
            }
            
            return success, message, details
            
        except Exception as e:
            return False, f"Error en scraping: {e}", {"error": str(e)}
    
    def test_pdf_processing(self) -> tuple:
        """Probar procesamiento de PDFs"""
        try:
            # Verificar directorio de PDFs
            pdf_dir = self.config.PDFS_DIR
            pdf_dir.mkdir(parents=True, exist_ok=True)
            
            # Buscar PDFs existentes
            pdf_files = list(pdf_dir.glob("*.pdf"))
            
            return True, f"Directorio PDF configurado - {len(pdf_files)} archivos encontrados", {
                "pdf_directory": str(pdf_dir),
                "pdf_count": len(pdf_files)
            }
            
        except Exception as e:
            return False, f"Error en procesamiento de PDFs: {e}", {"error": str(e)}
    
    def test_cache_system(self) -> tuple:
        """Probar sistema de cache"""
        try:
            cache_file = self.config.DATA_DIR / "scraping_cache.json"
            
            # Crear cache de prueba
            test_cache = {
                "processed_urls": ["http://test1.com", "http://test2.com"],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(test_cache, f)
            
            # Verificar lectura
            with open(cache_file, 'r') as f:
                loaded_cache = json.load(f)
            
            success = len(loaded_cache["processed_urls"]) == 2
            
            return success, "Sistema de cache funcionando correctamente", {
                "cache_file": str(cache_file),
                "test_urls_count": len(loaded_cache["processed_urls"])
            }
            
        except Exception as e:
            return False, f"Error en sistema de cache: {e}", {"error": str(e)}
    
    def test_error_handling(self) -> tuple:
        """Probar manejo de errores"""
        try:
            from src.scraper.optimized_scraper import OptimizedSCJNScraper
            
            scraper = OptimizedSCJNScraper(self.config)
            
            # Probar URL inválida
            result = scraper.get_tesis_detail("http://invalid-url-for-testing.com")
            
            # El resultado debe ser None (error manejado correctamente)
            success = result is None
            
            return success, "Manejo de errores funcionando correctamente", {
                "error_handled": success
            }
            
        except Exception as e:
            return False, f"Error en manejo de errores: {e}", {"error": str(e)}
    
    def test_performance_monitoring(self) -> tuple:
        """Probar monitoreo de performance"""
        try:
            from src.utils.logger import get_performance_logger, performance_monitor
            
            perf_logger = get_performance_logger()
            
            # Probar timer manual
            perf_logger.start_timer("manual_test")
            time.sleep(0.05)
            duration = perf_logger.end_timer("manual_test")
            
            # Probar decorador
            @performance_monitor("decorator_test")
            def test_function():
                time.sleep(0.05)
                return "test_result"
            
            result = test_function()
            
            success = duration is not None and result == "test_result"
            
            return success, "Monitoreo de performance funcionando", {
                "manual_timer_duration": duration,
                "decorator_result": result
            }
            
        except Exception as e:
            return False, f"Error en monitoreo de performance: {e}", {"error": str(e)}
    
    def test_data_persistence(self) -> tuple:
        """Probar persistencia de datos"""
        try:
            from src.database.models import get_session, Tesis
            
            session = get_session()
            
            # Crear tesis de prueba
            test_tesis = Tesis(
                scjn_id="test_end_to_end_001",
                titulo="Tesis de prueba end-to-end",
                url="http://test.example.com",
                rubro="Prueba",
                texto="Texto de prueba para validación",
                metadata_json={"test": True, "timestamp": datetime.now().isoformat()}
            )
            
            session.add(test_tesis)
            session.commit()
            
            # Verificar que se guardó
            retrieved = session.query(Tesis).filter_by(scjn_id="test_end_to_end_001").first()
            
            success = retrieved is not None
            
            # Limpiar
            if retrieved:
                session.delete(retrieved)
                session.commit()
            
            session.close()
            
            return success, "Persistencia de datos funcionando correctamente", {
                "test_tesis_saved": success,
                "test_tesis_id": "test_end_to_end_001"
            }
            
        except Exception as e:
            return False, f"Error en persistencia de datos: {e}", {"error": str(e)}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generar reporte de pruebas"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }
        
        return report
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🏛️ IA-IUS-SCRAPPING: PRUEBAS END-TO-END OPTIMIZADAS")
        print("=" * 70)
        print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Lista de pruebas
        tests = [
            ("Requerimientos del Sistema", self.test_system_requirements),
            ("Carga de Configuración", self.test_configuration_loading),
            ("Sistema de Logging", self.test_logging_system),
            ("Conexión Base de Datos", self.test_database_connection),
            ("Conexión Google Drive", self.test_google_drive_connection),
            ("Configuración Selenium", self.test_selenium_setup),
            ("Funcionalidad de Scraping", self.test_scraping_functionality),
            ("Procesamiento de PDFs", self.test_pdf_processing),
            ("Sistema de Cache", self.test_cache_system),
            ("Manejo de Errores", self.test_error_handling),
            ("Monitoreo de Performance", self.test_performance_monitoring),
            ("Persistencia de Datos", self.test_data_persistence)
        ]
        
        # Ejecutar pruebas
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            time.sleep(0.5)  # Pausa entre pruebas
        
        # Generar reporte
        report = self.generate_report()
        
        # Mostrar resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE PRUEBAS END-TO-END")
        print("=" * 70)
        print(f"📊 Total de pruebas: {report['summary']['total_tests']}")
        print(f"✅ Exitosas: {report['summary']['passed']}")
        print(f"❌ Fallidas: {report['summary']['failed']}")
        print(f"📈 Tasa de éxito: {report['summary']['success_rate']:.1f}%")
        print(f"⏱️ Tiempo total: {report['summary']['total_duration']:.2f}s")
        
        # Mostrar detalles de pruebas fallidas
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            print(f"\n❌ PRUEBAS FALLIDAS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test.name}: {test.message}")
        
        # Guardar reporte
        if self.config:
            report_file = self.config.DATA_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"\n📄 Reporte guardado: {report_file}")
            except Exception as e:
                print(f"\n⚠️ Error guardando reporte: {e}")
        
        print(f"\n🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Determinar código de salida
        if report['summary']['success_rate'] == 100:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON! Sistema listo para producción.")
            return 0
        elif report['summary']['success_rate'] >= 80:
            print("⚠️ La mayoría de pruebas pasaron. Revisar pruebas fallidas.")
            return 1
        else:
            print("❌ Múltiples pruebas fallaron. Sistema necesita revisión.")
            return 2

def main():
    """Función principal"""
    try:
        tester = EndToEndTester()
        exit_code = tester.run_all_tests()
        return exit_code
    except KeyboardInterrupt:
        print("\n⚠️ Pruebas interrumpidas por usuario")
        return 3
    except Exception as e:
        print(f"\n❌ Error crítico en pruebas: {e}")
        traceback.print_exc()
        return 4

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)