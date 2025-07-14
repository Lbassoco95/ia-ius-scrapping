#!/usr/bin/env python3
"""
Script de inicio para el sistema de scraping automático inteligente
- Inicia el sistema en modo daemon/servicio
- Configuración automática de fases
- Logging detallado
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.automation.auto_scraper import IntelligentAutoScraper

class AutoScraperDaemon:
    """Daemon para el sistema de scraping automático"""
    
    def __init__(self):
        self.scraper = None
        self.running = False
        self.pid_file = "data/scraper_daemon.pid"
        self.log_file = "logs/daemon.log"
        
        # Configurar logging
        self.setup_logging()
        
        # Crear directorios necesarios
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Configurar señales
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_logging(self):
        """Configurar logging del daemon"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """Manejador de señales para detener el daemon"""
        self.logger.info(f"🛑 Señal recibida: {signum}")
        self.stop()
    
    def write_pid(self):
        """Escribir PID del daemon"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            self.logger.error(f"Error escribiendo PID: {e}")
    
    def remove_pid(self):
        """Remover archivo PID"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
        except Exception as e:
            self.logger.error(f"Error removiendo PID: {e}")
    
    def is_running(self):
        """Verificar si el daemon ya está ejecutándose"""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificar si el proceso existe
            os.kill(pid, 0)
            return True
        except (ValueError, OSError):
            # PID inválido o proceso no existe
            self.remove_pid()
            return False
    
    def start(self):
        """Iniciar el daemon"""
        if self.is_running():
            self.logger.error("❌ El daemon ya está ejecutándose")
            return False
        
        self.logger.info("🚀 Iniciando daemon de scraping inteligente...")
        
        try:
            # Inicializar scraper
            self.scraper = IntelligentAutoScraper()
            self.logger.info("✅ Scraper inicializado")
            
            # Escribir PID
            self.write_pid()
            self.logger.info(f"📝 PID guardado: {os.getpid()}")
            
            # Mostrar estado inicial
            status = self.scraper.get_status()
            self.logger.info(f"📊 Estado inicial:")
            self.logger.info(f"   • Fase: {status['current_phase']}")
            self.logger.info(f"   • Progreso: {status['progress_percentage']}%")
            self.logger.info(f"   • Archivos en BD: {status['total_in_database']:,}")
            
            # Iniciar programador
            self.running = True
            self.logger.info("⏰ Iniciando programador automático...")
            
            if status['current_phase'] == 'initial':
                self.logger.info(f"📅 Fase inicial: Todos los días a las {self.scraper.initial_phase_start_time}")
            else:
                self.logger.info(f"📅 Fase mantenimiento: Lunes a las {self.scraper.maintenance_phase_start_time}")
            
            # Bucle principal
            while self.running:
                try:
                    # Ejecutar trabajos pendientes
                    if status['current_phase'] == 'initial':
                        if not status['should_transition']:
                            self.logger.info("🚀 Ejecutando trabajo inicial...")
                            self.scraper.initial_phase_job()
                        else:
                            self.logger.info("🔄 Transicionando a mantenimiento...")
                            self.scraper.transition_to_maintenance_phase()
                    else:
                        if status['should_run_maintenance']:
                            self.logger.info("🔧 Ejecutando mantenimiento...")
                            self.scraper.maintenance_phase_job()
                    
                    # Actualizar estado
                    status = self.scraper.get_status()
                    
                    # Esperar antes de la siguiente verificación
                    time.sleep(3600)  # 1 hora
                    
                except Exception as e:
                    self.logger.error(f"❌ Error en bucle principal: {e}")
                    time.sleep(300)  # 5 minutos en caso de error
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando daemon: {e}")
            self.remove_pid()
            return False
    
    def stop(self):
        """Detener el daemon"""
        self.logger.info("🛑 Deteniendo daemon...")
        self.running = False
        
        if self.scraper:
            try:
                self.scraper.scraper.close_driver()
                self.logger.info("✅ Driver cerrado")
            except Exception as e:
                self.logger.error(f"❌ Error cerrando driver: {e}")
        
        self.remove_pid()
        self.logger.info("✅ Daemon detenido")
    
    def status(self):
        """Mostrar estado del daemon"""
        if self.is_running():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                print(f"✅ Daemon ejecutándose (PID: {pid})")
                
                # Mostrar estado del scraper
                scraper = IntelligentAutoScraper()
                status = scraper.get_status()
                
                print(f"📊 Estado del sistema:")
                print(f"   • Fase: {status['current_phase']}")
                print(f"   • Progreso: {status['progress_percentage']}%")
                print(f"   • Archivos en BD: {status['total_in_database']:,}")
                print(f"   • Total descargado: {status['total_downloaded']:,}")
                
                if status['current_phase'] == 'maintenance':
                    if status['last_maintenance_date']:
                        last_maintenance = datetime.fromisoformat(status['last_maintenance_date'])
                        print(f"   • Último mantenimiento: {last_maintenance.strftime('%Y-%m-%d %H:%M')}")
                    
                    if status['next_maintenance_date']:
                        next_maintenance = datetime.fromisoformat(status['next_maintenance_date'])
                        print(f"   • Próximo mantenimiento: {next_maintenance.strftime('%Y-%m-%d %H:%M')}")
                
                return True
            except Exception as e:
                print(f"❌ Error obteniendo estado: {e}")
                return False
        else:
            print("❌ Daemon no está ejecutándose")
            return False

def show_usage():
    """Mostrar uso del script"""
    print("🤖 SISTEMA DE SCRAPING AUTOMÁTICO INTELIGENTE")
    print("=" * 50)
    print("Uso: python start_auto_scraper.py [comando]")
    print("\nComandos:")
    print("  start   - Iniciar daemon")
    print("  stop    - Detener daemon")
    print("  restart - Reiniciar daemon")
    print("  status  - Mostrar estado")
    print("  help    - Mostrar esta ayuda")
    print("\nEjemplos:")
    print("  python start_auto_scraper.py start")
    print("  python start_auto_scraper.py status")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        show_usage()
        return 1
    
    command = sys.argv[1].lower()
    daemon = AutoScraperDaemon()
    
    if command == "start":
        if daemon.start():
            print("✅ Daemon iniciado correctamente")
            return 0
        else:
            print("❌ Error iniciando daemon")
            return 1
    
    elif command == "stop":
        if daemon.is_running():
            try:
                with open(daemon.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                print("✅ Señal de detención enviada")
                return 0
            except Exception as e:
                print(f"❌ Error deteniendo daemon: {e}")
                return 1
        else:
            print("❌ Daemon no está ejecutándose")
            return 1
    
    elif command == "restart":
        if daemon.is_running():
            try:
                with open(daemon.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                print("✅ Daemon detenido")
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error deteniendo daemon: {e}")
        
        if daemon.start():
            print("✅ Daemon reiniciado correctamente")
            return 0
        else:
            print("❌ Error reiniciando daemon")
            return 1
    
    elif command == "status":
        daemon.status()
        return 0
    
    elif command == "help":
        show_usage()
        return 0
    
    else:
        print(f"❌ Comando inválido: {command}")
        show_usage()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 