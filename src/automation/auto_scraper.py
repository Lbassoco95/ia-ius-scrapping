#!/usr/bin/env python3
"""
Sistema de scraping automático inteligente para SCJN
- Fase inicial: 3 horas diarias hasta descargar todo el historial
- Fase de mantenimiento: Lunes semanal para nuevas publicaciones
- Control inteligente de tiempo y duplicados
"""

import time
import json
import logging
try:
    import schedule
except ImportError:
    schedule = None
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import sqlite3
from pathlib import Path

from src.scraper.selenium_scraper import SeleniumSCJNScraper
from src.database.models import get_session, Tesis, create_tables
from src.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntelligentAutoScraper:
    """Sistema de scraping automático inteligente con fases"""
    
    def __init__(self):
        self.scraper = SeleniumSCJNScraper()
        self.session = get_session()
        self.stats_file = "data/scraping_stats.json"
        self.config_file = "data/scraper_config.json"
        
        # Configuración de fases
        self.initial_phase_hours = 3  # Horas diarias en fase inicial
        self.initial_phase_start_time = "09:00"  # Hora de inicio
        self.maintenance_phase_day = "monday"  # Día de mantenimiento
        self.maintenance_phase_start_time = "08:00"  # Hora de inicio mantenimiento
        
        # Límites y control
        self.max_files_per_session = 200  # Máximo archivos por sesión
        self.session_timeout_hours = 24  # Timeout máximo por sesión
        self.estimated_files_per_hour = 30  # Estimación de archivos por hora
        
        # Crear directorios necesarios
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/pdfs", exist_ok=True)
        
        # Crear tablas si no existen
        create_tables()
        
        # Cargar configuración y estadísticas
        self.load_config()
        self.load_stats()
    
    def load_config(self):
        """Cargar configuración del scraper"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_phase = config.get('current_phase', 'initial')
                    self.initial_phase_completed = config.get('initial_phase_completed', False)
                    self.last_maintenance_date = config.get('last_maintenance_date')
                    self.total_estimated_files = config.get('total_estimated_files', 50000)
                    self.files_downloaded_initial = config.get('files_downloaded_initial', 0)
            else:
                self.current_phase = 'initial'
                self.initial_phase_completed = False
                self.last_maintenance_date = None
                self.total_estimated_files = 50000
                self.files_downloaded_initial = 0
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self.current_phase = 'initial'
            self.initial_phase_completed = False
            self.last_maintenance_date = None
            self.total_estimated_files = 50000
            self.files_downloaded_initial = 0
    
    def save_config(self):
        """Guardar configuración del scraper"""
        try:
            config = {
                'current_phase': self.current_phase,
                'initial_phase_completed': self.initial_phase_completed,
                'last_maintenance_date': self.last_maintenance_date,
                'total_estimated_files': self.total_estimated_files,
                'files_downloaded_initial': self.files_downloaded_initial
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def load_stats(self):
        """Cargar estadísticas de scraping"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            else:
                self.stats = {
                    'total_downloaded': 0,
                    'daily_downloads': {},
                    'session_downloads': {},
                    'duplicates_found': 0,
                    'errors': 0,
                    'phase_transitions': []
                }
        except Exception as e:
            logger.error(f"Error cargando estadísticas: {e}")
            self.stats = {
                'total_downloaded': 0,
                'daily_downloads': {},
                'session_downloads': {},
                'duplicates_found': 0,
                'errors': 0,
                'phase_transitions': []
            }
    
    def save_stats(self):
        """Guardar estadísticas de scraping"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")
    
    def is_duplicate(self, scjn_id: str) -> bool:
        """Verificar si una tesis ya existe en la base de datos"""
        try:
            existing = self.session.query(Tesis).filter_by(scjn_id=scjn_id).first()
            return existing is not None
        except Exception as e:
            logger.error(f"Error verificando duplicado {scjn_id}: {e}")
            return False
    
    def should_transition_to_maintenance(self) -> bool:
        """Verificar si debe transicionar a fase de mantenimiento"""
        if self.initial_phase_completed:
            return True
        
        # Calcular progreso de fase inicial
        progress_percentage = (self.files_downloaded_initial / self.total_estimated_files) * 100
        
        # Transicionar si hemos descargado más del 95% o si han pasado más de 30 días
        if progress_percentage >= 95:
            logger.info(f"🎯 Fase inicial completada: {progress_percentage:.1f}% de archivos descargados")
            return True
        
        # Verificar si han pasado más de 30 días desde el inicio
        if 'phase_transitions' in self.stats and self.stats['phase_transitions']:
            first_transition = datetime.fromisoformat(self.stats['phase_transitions'][0]['date'])
            days_since_start = (datetime.now() - first_transition).days
            if days_since_start >= 30:
                logger.info(f"⏰ Transición por tiempo: {days_since_start} días desde inicio")
                return True
        
        return False
    
    def should_run_maintenance(self) -> bool:
        """Verificar si debe ejecutar mantenimiento semanal"""
        if not self.last_maintenance_date:
            return True
        
        last_maintenance = datetime.fromisoformat(self.last_maintenance_date)
        days_since_maintenance = (datetime.now() - last_maintenance).days
        
        # Ejecutar si han pasado 7 días o más
        return days_since_maintenance >= 7
    
    def get_search_terms_for_phase(self) -> List[str]:
        """Obtener términos de búsqueda según la fase"""
        if self.current_phase == 'initial':
            # Términos amplios para fase inicial
            return [
                "amparo", "derechos humanos", "responsabilidad civil", "contrato",
                "propiedad", "familia", "laboral", "penal", "administrativo",
                "constitucional", "fiscal", "mercantil", "agrario", "ambiental",
                "electoral", "comercial", "civil", "procesal", "internacional",
                "tributario", "seguridad social", "competencia", "consumidor"
            ]
        else:
            # Términos recientes para mantenimiento
            current_year = datetime.now().year
            return [
                str(current_year),
                str(current_year - 1),
                "reciente",
                "nuevo",
                "actualizado",
                "modificado"
            ]
    
    def initial_phase_job(self):
        """Trabajo de fase inicial (3 horas diarias)"""
        logger.info("🚀 Iniciando fase inicial (3 horas diarias)...")
        
        if self.should_transition_to_maintenance():
            self.transition_to_maintenance_phase()
            return
        
        session_start = datetime.now()
        session_end = session_start + timedelta(hours=self.initial_phase_hours)
        downloaded_count = 0
        
        try:
            if not self.scraper.setup_driver():
                logger.error("❌ No se pudo configurar el driver")
                return
            
            search_terms = self.get_search_terms_for_phase()
            
            for term in search_terms:
                # Verificar límites de tiempo y archivos
                if datetime.now() >= session_end:
                    logger.info("⏰ Tiempo de sesión agotado")
                    break
                
                if downloaded_count >= self.max_files_per_session:
                    logger.info("📊 Límite de archivos por sesión alcanzado")
                    break
                
                logger.info(f"🔍 Buscando: {term}")
                
                try:
                    if not self.scraper.navigate_to_search_page():
                        continue
                    
                    if not self.scraper.search_for_tesis(term):
                        continue
                    
                    results = self.scraper.extract_search_results()
                    
                    for result in results:
                        # Verificar límites
                        if datetime.now() >= session_end:
                            break
                        
                        if downloaded_count >= self.max_files_per_session:
                            break
                        
                        scjn_id = result.get('scjn_id')
                        if not scjn_id:
                            continue
                        
                        # Verificar duplicado
                        if self.is_duplicate(scjn_id):
                            self.stats['duplicates_found'] += 1
                            continue
                        
                        # Obtener detalles
                        try:
                            detail_data = self.scraper.get_tesis_detail(result['url'])
                            if detail_data:
                                self.save_tesis_to_db(result, detail_data)
                                downloaded_count += 1
                                self.files_downloaded_initial += 1
                                self.update_session_stats(downloaded_count)
                                
                                logger.info(f"✅ Descargado: {scjn_id} ({downloaded_count})")
                                time.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"❌ Error procesando {scjn_id}: {e}")
                            self.stats['errors'] += 1
                            continue
                    
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"❌ Error en búsqueda '{term}': {e}")
                    continue
            
            session_duration = datetime.now() - session_start
            logger.info(f"🎉 Sesión inicial completada: {downloaded_count} archivos en {session_duration}")
            
            # Verificar si debe transicionar
            if self.should_transition_to_maintenance():
                self.transition_to_maintenance_phase()
            
        except Exception as e:
            logger.error(f"❌ Error en fase inicial: {e}")
            self.stats['errors'] += 1
        finally:
            self.scraper.close_driver()
            self.save_stats()
            self.save_config()
    
    def maintenance_phase_job(self):
        """Trabajo de fase de mantenimiento (lunes semanal)"""
        logger.info("🔧 Iniciando fase de mantenimiento (lunes semanal)...")
        
        if not self.should_run_maintenance():
            logger.info("⏰ No es momento de mantenimiento")
            return
        
        session_start = datetime.now()
        downloaded_count = 0
        
        try:
            if not self.scraper.setup_driver():
                logger.error("❌ No se pudo configurar el driver")
                return
            
            search_terms = self.get_search_terms_for_phase()
            
            for term in search_terms:
                logger.info(f"🔍 Verificando: {term}")
                
                try:
                    if not self.scraper.navigate_to_search_page():
                        continue
                    
                    if not self.scraper.search_for_tesis(term):
                        continue
                    
                    results = self.scraper.extract_search_results()
                    
                    for result in results[:50]:  # Limitar a 50 por término
                        scjn_id = result.get('scjn_id')
                        if not scjn_id:
                            continue
                        
                        # Verificar duplicado
                        if self.is_duplicate(scjn_id):
                            continue
                        
                        # Obtener detalles
                        try:
                            detail_data = self.scraper.get_tesis_detail(result['url'])
                            if detail_data:
                                self.save_tesis_to_db(result, detail_data)
                                downloaded_count += 1
                                self.update_session_stats(downloaded_count)
                                logger.info(f"✅ Nuevo archivo: {scjn_id}")
                                time.sleep(2)
                        except Exception as e:
                            logger.error(f"❌ Error procesando {scjn_id}: {e}")
                            continue
                    
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"❌ Error verificando '{term}': {e}")
                    continue
            
            # Actualizar fecha de último mantenimiento
            self.last_maintenance_date = datetime.now().isoformat()
            self.save_config()
            
            session_duration = datetime.now() - session_start
            logger.info(f"🎉 Mantenimiento completado: {downloaded_count} nuevos archivos en {session_duration}")
            
        except Exception as e:
            logger.error(f"❌ Error en mantenimiento: {e}")
        finally:
            self.scraper.close_driver()
            self.save_stats()
    
    def transition_to_maintenance_phase(self):
        """Transicionar a fase de mantenimiento"""
        logger.info("🔄 Transicionando a fase de mantenimiento...")
        
        self.current_phase = 'maintenance'
        self.initial_phase_completed = True
        
        # Registrar transición
        transition = {
            'date': datetime.now().isoformat(),
            'from_phase': 'initial',
            'to_phase': 'maintenance',
            'files_downloaded_initial': self.files_downloaded_initial
        }
        
        if 'phase_transitions' not in self.stats:
            self.stats['phase_transitions'] = []
        self.stats['phase_transitions'].append(transition)
        
        self.save_config()
        self.save_stats()
        
        logger.info("✅ Transición completada: Ahora en fase de mantenimiento")
    
    def update_session_stats(self, count: int = 1):
        """Actualizar estadísticas de sesión"""
        today = datetime.now().strftime('%Y-%m-%d')
        session_id = f"{today}_{self.current_phase}"
        
        if 'session_downloads' not in self.stats:
            self.stats['session_downloads'] = {}
        
        if session_id not in self.stats['session_downloads']:
            self.stats['session_downloads'][session_id] = 0
        
        self.stats['session_downloads'][session_id] += count
        self.stats['total_downloaded'] += count
    
    def save_tesis_to_db(self, result: Dict, detail_data: Dict):
        """Guardar tesis en base de datos"""
        try:
            tesis = Tesis(
                scjn_id=result.get('scjn_id'),
                titulo=result.get('titulo', ''),
                url=result.get('url', ''),
                rubro=detail_data.get('rubro', ''),
                texto=detail_data.get('texto', ''),
                precedente=detail_data.get('precedente', ''),
                pdf_url=detail_data.get('pdf_url', ''),
                metadata=json.dumps(result.get('metadata', {})),
                fecha_descarga=datetime.now(),
                html_content=detail_data.get('html_content', '')
            )
            
            self.session.add(tesis)
            self.session.commit()
            
        except Exception as e:
            logger.error(f"❌ Error guardando en BD: {e}")
            self.session.rollback()
    
    def get_status(self) -> Dict:
        """Obtener estado completo del sistema"""
        total_in_db = self.session.query(Tesis).count()
        
        # Calcular progreso de fase inicial
        progress_percentage = 0
        if self.total_estimated_files > 0:
            progress_percentage = (self.files_downloaded_initial / self.total_estimated_files) * 100
        
        # Próximo mantenimiento
        next_maintenance = None
        if self.last_maintenance_date:
            last_maintenance = datetime.fromisoformat(self.last_maintenance_date)
            next_maintenance = last_maintenance + timedelta(days=7)
        
        return {
            'current_phase': self.current_phase,
            'initial_phase_completed': self.initial_phase_completed,
            'progress_percentage': round(progress_percentage, 1),
            'files_downloaded_initial': self.files_downloaded_initial,
            'total_estimated_files': self.total_estimated_files,
            'total_in_database': total_in_db,
            'total_downloaded': self.stats.get('total_downloaded', 0),
            'duplicates_found': self.stats.get('duplicates_found', 0),
            'errors': self.stats.get('errors', 0),
            'last_maintenance_date': self.last_maintenance_date,
            'next_maintenance_date': next_maintenance.isoformat() if next_maintenance else None,
            'should_run_maintenance': self.should_run_maintenance(),
            'should_transition': self.should_transition_to_maintenance()
        }
    
    def start_scheduler(self):
        """Iniciar programador inteligente"""
        if not schedule:
            logger.error("❌ Módulo 'schedule' no disponible. Instale con: pip install schedule")
            return
            
        logger.info("⏰ Configurando programador inteligente...")
        
        if self.current_phase == 'initial':
            # Fase inicial: todos los días a las 9:00 AM por 3 horas
            schedule.every().day.at(self.initial_phase_start_time).do(self.initial_phase_job)
            logger.info(f"📅 Fase inicial: Todos los días a las {self.initial_phase_start_time}")
        else:
            # Fase de mantenimiento: lunes a las 8:00 AM
            schedule.every().monday.at(self.maintenance_phase_start_time).do(self.maintenance_phase_job)
            logger.info(f"📅 Fase de mantenimiento: Lunes a las {self.maintenance_phase_start_time}")
        
        # Ejecutar trabajo pendiente si es necesario
        if self.current_phase == 'initial':
            logger.info("🚀 Ejecutando trabajo inicial pendiente...")
            self.initial_phase_job()
        elif self.should_run_maintenance():
            logger.info("🔧 Ejecutando mantenimiento pendiente...")
            self.maintenance_phase_job()
        
        logger.info("✅ Programador inteligente iniciado")
        
        # Bucle principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    
    def run_manual_session(self, phase: Optional[str] = None, max_hours: Optional[int] = None):
        """Ejecutar sesión manual"""
        if phase:
            self.current_phase = phase
        
        if max_hours:
            self.initial_phase_hours = max_hours
        
        logger.info(f"🔄 Ejecutando sesión manual: {self.current_phase} ({max_hours or self.initial_phase_hours} horas)")
        
        if self.current_phase == 'initial':
            self.initial_phase_job()
        else:
            self.maintenance_phase_job() 