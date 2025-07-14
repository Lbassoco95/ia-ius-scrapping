#!/usr/bin/env python3
"""
Script para ejecutar scraping durante una hora y mostrar estadísticas en tiempo real
"""

import sys
import os
import time
import logging
import json
from datetime import datetime, timedelta
from threading import Thread, Event

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.main import ScrapingOrchestrator
from src.database.models import get_session, Tesis

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraping_hour.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HourlyScrapingMonitor:
    """Monitor para scraping de una hora con estadísticas en tiempo real"""
    
    def __init__(self, duration_hours=1):
        self.duration_hours = duration_hours
        self.start_time = None
        self.end_time = None
        self.stop_event = Event()
        self.orchestrator = ScrapingOrchestrator()
        self.stats = {
            'tesis_encontradas': 0,
            'pdfs_descargados': 0,
            'enlaces_generados': 0,
            'errores': 0,
            'sesiones_completadas': 0
        }
    
    def get_current_stats(self):
        """Obtener estadísticas actuales de la base de datos"""
        try:
            session = get_session()
            
            # Contar tesis en la base de datos
            total_tesis = session.query(Tesis).count()
            tesis_con_pdf = session.query(Tesis).filter(Tesis.pdf_url.isnot(None)).count()
            tesis_con_drive = session.query(Tesis).filter(Tesis.google_drive_link.isnot(None)).count()
            
            session.close()
            
            return {
                'total_tesis': total_tesis,
                'tesis_con_pdf': tesis_con_pdf,
                'tesis_con_drive': tesis_con_drive
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'total_tesis': 0, 'tesis_con_pdf': 0, 'tesis_con_drive': 0}
    
    def show_progress(self):
        """Mostrar progreso en tiempo real"""
        while not self.stop_event.is_set():
            try:
                elapsed = time.time() - self.start_time.timestamp()
                remaining = (self.duration_hours * 3600) - elapsed
                
                if remaining <= 0:
                    break
                
                # Obtener estadísticas actuales
                db_stats = self.get_current_stats()
                
                # Calcular porcentaje de tiempo
                progress_percent = (elapsed / (self.duration_hours * 3600)) * 100
                
                # Mostrar estadísticas
                print("\n" + "="*60)
                print("📊 ESTADÍSTICAS EN TIEMPO REAL")
                print("="*60)
                print(f"⏱️  Tiempo transcurrido: {timedelta(seconds=int(elapsed))}")
                print(f"⏰ Tiempo restante: {timedelta(seconds=int(remaining))}")
                print(f"📈 Progreso: {progress_percent:.1f}%")
                print(f"📋 Total tesis en BD: {db_stats['total_tesis']}")
                print(f"📄 Tesis con PDF: {db_stats['tesis_con_pdf']}")
                print(f"🔗 Tesis con Google Drive: {db_stats['tesis_con_drive']}")
                print(f"📊 Tesis encontradas esta sesión: {self.stats['tesis_encontradas']}")
                print(f"📥 PDFs descargados esta sesión: {self.stats['pdfs_descargados']}")
                print(f"❌ Errores esta sesión: {self.stats['errores']}")
                print("="*60)
                
                time.sleep(30)  # Actualizar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error mostrando progreso: {e}")
                time.sleep(30)
    
    def run_scraping_session(self):
        """Ejecutar una sesión de scraping"""
        try:
            logger.info("🚀 Iniciando sesión de scraping...")
            
            # Ejecutar scraping con límite de documentos
            self.orchestrator.run_full_scraping(max_documents=50)  # 50 tesis por sesión
            
            self.stats['sesiones_completadas'] += 1
            logger.info("✅ Sesión de scraping completada")
            
        except Exception as e:
            self.stats['errores'] += 1
            logger.error(f"❌ Error en sesión de scraping: {e}")
    
    def run_hourly_scraping(self):
        """Ejecutar scraping durante una hora"""
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.duration_hours)
        
        logger.info(f"🎯 Iniciando scraping por {self.duration_hours} hora(s)")
        logger.info(f"⏰ Hora de inicio: {self.start_time.strftime('%H:%M:%S')}")
        logger.info(f"⏰ Hora de finalización: {self.end_time.strftime('%H:%M:%S')}")
        
        # Iniciar thread de monitoreo
        monitor_thread = Thread(target=self.show_progress)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        session_count = 0
        
        try:
            while datetime.now() < self.end_time and not self.stop_event.is_set():
                session_count += 1
                logger.info(f"🔄 Iniciando sesión {session_count}")
                
                # Ejecutar sesión de scraping
                self.run_scraping_session()
                
                # Pausa entre sesiones
                if datetime.now() < self.end_time:
                    logger.info("⏸️ Pausa de 2 minutos entre sesiones...")
                    time.sleep(120)  # 2 minutos de pausa
        
        except KeyboardInterrupt:
            logger.info("⏹️ Detención manual del scraping")
        finally:
            self.stop_event.set()
            self.end_time = datetime.now()
            
            # Mostrar estadísticas finales
            self.show_final_stats()
    
    def show_final_stats(self):
        """Mostrar estadísticas finales"""
        duration = self.end_time - self.start_time
        db_stats = self.get_current_stats()
        
        print("\n" + "🎉"*20)
        print("🎉 SCRAPING COMPLETADO 🎉")
        print("🎉"*20)
        print(f"⏱️  Duración total: {duration}")
        print(f"📊 Sesiones completadas: {self.stats['sesiones_completadas']}")
        print(f"📋 Total tesis en BD: {db_stats['total_tesis']}")
        print(f"📄 Tesis con PDF: {db_stats['tesis_con_pdf']}")
        print(f"🔗 Tesis con Google Drive: {db_stats['tesis_con_drive']}")
        print(f"❌ Errores totales: {self.stats['errores']}")
        
        # Guardar reporte
        report = {
            'fecha_inicio': self.start_time.isoformat(),
            'fecha_fin': self.end_time.isoformat(),
            'duracion_minutos': duration.total_seconds() / 60,
            'sesiones_completadas': self.stats['sesiones_completadas'],
            'total_tesis': db_stats['total_tesis'],
            'tesis_con_pdf': db_stats['tesis_con_pdf'],
            'tesis_con_drive': db_stats['tesis_con_drive'],
            'errores': self.stats['errores']
        }
        
        report_file = f"data/reporte_scraping_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('data', exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📄 Reporte guardado en: {report_file}")

def main():
    """Función principal"""
    print("🚀 INICIANDO SCRAPING DE 1 HORA")
    print("="*50)
    print("Este script ejecutará el scraping durante 1 hora")
    print("Mostrará estadísticas en tiempo real cada 30 segundos")
    print("Presiona Ctrl+C para detener manualmente")
    print("="*50)
    
    # Crear monitor
    monitor = HourlyScrapingMonitor(duration_hours=1)
    
    try:
        # Ejecutar scraping
        monitor.run_hourly_scraping()
        
    except KeyboardInterrupt:
        print("\n⏹️ Detención manual solicitada")
        monitor.stop_event.set()
        monitor.show_final_stats()
    
    except Exception as e:
        logger.error(f"❌ Error en scraping: {e}")
        monitor.show_final_stats()

if __name__ == "__main__":
    main() 