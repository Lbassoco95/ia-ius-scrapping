#!/usr/bin/env python3
"""
Controlador para el sistema de scraping automático inteligente
- Manejo de fases inicial y de mantenimiento
- Control manual y automático
- Monitoreo de progreso
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.automation.auto_scraper import IntelligentAutoScraper

class AutoScraperController:
    """Controlador para el sistema de scraping automático"""
    
    def __init__(self):
        self.scraper = IntelligentAutoScraper()
    
    def show_menu(self):
        """Mostrar menú principal"""
        print("\n" + "="*60)
        print("🤖 CONTROLADOR DE SCRAPING INTELIGENTE SCJN")
        print("="*60)
        print("1. 📊 Ver estado del sistema")
        print("2. 🚀 Iniciar fase inicial (3 horas diarias)")
        print("3. 🔧 Ejecutar mantenimiento semanal")
        print("4. ⚙️  Configurar parámetros")
        print("5. 📈 Ver estadísticas detalladas")
        print("6. 🔄 Ejecutar sesión manual")
        print("7. ⏰ Iniciar modo automático")
        print("8. 🛑 Detener sistema")
        print("9. 📋 Ver logs recientes")
        print("0. ❌ Salir")
        print("="*60)
    
    def show_status(self):
        """Mostrar estado del sistema"""
        print("\n📊 ESTADO DEL SISTEMA")
        print("-" * 40)
        
        try:
            status = self.scraper.get_status()
            
            print(f"🎯 Fase actual: {status['current_phase'].upper()}")
            print(f"📈 Progreso inicial: {status['progress_percentage']}%")
            print(f"📁 Archivos descargados (inicial): {status['files_downloaded_initial']:,}")
            print(f"📊 Total en base de datos: {status['total_in_database']:,}")
            print(f"🔄 Total descargado: {status['total_downloaded']:,}")
            print(f"⚠️  Duplicados encontrados: {status['duplicates_found']:,}")
            print(f"❌ Errores: {status['errors']:,}")
            
            if status['current_phase'] == 'maintenance':
                if status['last_maintenance_date']:
                    last_maintenance = datetime.fromisoformat(status['last_maintenance_date'])
                    print(f"🔧 Último mantenimiento: {last_maintenance.strftime('%Y-%m-%d %H:%M')}")
                
                if status['next_maintenance_date']:
                    next_maintenance = datetime.fromisoformat(status['next_maintenance_date'])
                    print(f"⏰ Próximo mantenimiento: {next_maintenance.strftime('%Y-%m-%d %H:%M')}")
                
                print(f"🔍 Debe ejecutar mantenimiento: {'SÍ' if status['should_run_maintenance'] else 'NO'}")
            else:
                print(f"🔄 Debe transicionar: {'SÍ' if status['should_transition'] else 'NO'}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
    
    def start_initial_phase(self):
        """Iniciar fase inicial"""
        print("\n🚀 INICIANDO FASE INICIAL")
        print("-" * 30)
        print("📋 Configuración:")
        print(f"   • Horas diarias: {self.scraper.initial_phase_hours}")
        print(f"   • Hora de inicio: {self.scraper.initial_phase_start_time}")
        print(f"   • Archivos máximos por sesión: {self.scraper.max_files_per_session}")
        print(f"   • Archivos estimados totales: {self.scraper.total_estimated_files:,}")
        
        confirm = input("\n¿Desea iniciar la fase inicial? (s/n): ").lower()
        if confirm == 's':
            try:
                print("🚀 Iniciando fase inicial...")
                self.scraper.initial_phase_job()
                print("✅ Fase inicial completada")
            except Exception as e:
                print(f"❌ Error en fase inicial: {e}")
        else:
            print("❌ Operación cancelada")
    
    def run_maintenance(self):
        """Ejecutar mantenimiento semanal"""
        print("\n🔧 EJECUTANDO MANTENIMIENTO SEMANAL")
        print("-" * 35)
        
        status = self.scraper.get_status()
        if not status['should_run_maintenance']:
            print("⏰ No es momento de mantenimiento")
            if status['last_maintenance_date']:
                last_maintenance = datetime.fromisoformat(status['last_maintenance_date'])
                days_since = (datetime.now() - last_maintenance).days
                print(f"   Último mantenimiento: {days_since} días atrás")
            return
        
        confirm = input("¿Ejecutar mantenimiento semanal? (s/n): ").lower()
        if confirm == 's':
            try:
                print("🔧 Ejecutando mantenimiento...")
                self.scraper.maintenance_phase_job()
                print("✅ Mantenimiento completado")
            except Exception as e:
                print(f"❌ Error en mantenimiento: {e}")
        else:
            print("❌ Operación cancelada")
    
    def configure_parameters(self):
        """Configurar parámetros del sistema"""
        print("\n⚙️  CONFIGURACIÓN DE PARÁMETROS")
        print("-" * 35)
        
        print("1. Horas diarias en fase inicial")
        print("2. Hora de inicio diario")
        print("3. Hora de mantenimiento semanal")
        print("4. Archivos máximos por sesión")
        print("5. Archivos estimados totales")
        print("0. Volver")
        
        option = input("\nSeleccione opción: ")
        
        if option == "1":
            try:
                hours = int(input(f"Horas diarias actuales: {self.scraper.initial_phase_hours}. Nuevo valor: "))
                if 1 <= hours <= 24:
                    self.scraper.initial_phase_hours = hours
                    print(f"✅ Horas diarias actualizadas: {hours}")
                else:
                    print("❌ Valor inválido (1-24)")
            except ValueError:
                print("❌ Valor inválido")
        
        elif option == "2":
            time_str = input(f"Hora de inicio actual: {self.scraper.initial_phase_start_time}. Nuevo valor (HH:MM): ")
            try:
                datetime.strptime(time_str, "%H:%M")
                self.scraper.initial_phase_start_time = time_str
                print(f"✅ Hora de inicio actualizada: {time_str}")
            except ValueError:
                print("❌ Formato inválido (HH:MM)")
        
        elif option == "3":
            time_str = input(f"Hora de mantenimiento actual: {self.scraper.maintenance_phase_start_time}. Nuevo valor (HH:MM): ")
            try:
                datetime.strptime(time_str, "%H:%M")
                self.scraper.maintenance_phase_start_time = time_str
                print(f"✅ Hora de mantenimiento actualizada: {time_str}")
            except ValueError:
                print("❌ Formato inválido (HH:MM)")
        
        elif option == "4":
            try:
                max_files = int(input(f"Archivos máximos actuales: {self.scraper.max_files_per_session}. Nuevo valor: "))
                if max_files > 0:
                    self.scraper.max_files_per_session = max_files
                    print(f"✅ Archivos máximos actualizados: {max_files}")
                else:
                    print("❌ Valor inválido (>0)")
            except ValueError:
                print("❌ Valor inválido")
        
        elif option == "5":
            try:
                total_files = int(input(f"Archivos estimados actuales: {self.scraper.total_estimated_files:,}. Nuevo valor: "))
                if total_files > 0:
                    self.scraper.total_estimated_files = total_files
                    print(f"✅ Archivos estimados actualizados: {total_files:,}")
                else:
                    print("❌ Valor inválido (>0)")
            except ValueError:
                print("❌ Valor inválido")
        
        # Guardar configuración
        self.scraper.save_config()
    
    def show_detailed_stats(self):
        """Mostrar estadísticas detalladas"""
        print("\n📈 ESTADÍSTICAS DETALLADAS")
        print("-" * 30)
        
        try:
            stats = self.scraper.stats
            
            print("📊 Descargas por sesión:")
            if 'session_downloads' in stats:
                for session_id, count in stats['session_downloads'].items():
                    print(f"   {session_id}: {count} archivos")
            else:
                print("   No hay datos de sesiones")
            
            print(f"\n📅 Descargas por día:")
            if 'daily_downloads' in stats:
                for date, count in stats['daily_downloads'].items():
                    print(f"   {date}: {count} archivos")
            else:
                print("   No hay datos diarios")
            
            if 'phase_transitions' in stats and stats['phase_transitions']:
                print(f"\n🔄 Transiciones de fase:")
                for transition in stats['phase_transitions']:
                    date = datetime.fromisoformat(transition['date'])
                    print(f"   {date.strftime('%Y-%m-%d %H:%M')}: {transition['from_phase']} → {transition['to_phase']}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def run_manual_session(self):
        """Ejecutar sesión manual"""
        print("\n🔄 SESIÓN MANUAL")
        print("-" * 20)
        
        print("1. Fase inicial")
        print("2. Fase de mantenimiento")
        print("0. Volver")
        
        option = input("\nSeleccione fase: ")
        
        if option == "1":
            try:
                hours = int(input("Horas de ejecución (1-24): "))
                if 1 <= hours <= 24:
                    print(f"🚀 Ejecutando fase inicial por {hours} horas...")
                    self.scraper.run_manual_session(phase='initial', max_hours=hours)
                    print("✅ Sesión manual completada")
                else:
                    print("❌ Horas inválidas")
            except ValueError:
                print("❌ Valor inválido")
        
        elif option == "2":
            confirm = input("¿Ejecutar fase de mantenimiento? (s/n): ").lower()
            if confirm == 's':
                print("🔧 Ejecutando fase de mantenimiento...")
                self.scraper.run_manual_session(phase='maintenance')
                print("✅ Sesión manual completada")
            else:
                print("❌ Operación cancelada")
    
    def start_automatic_mode(self):
        """Iniciar modo automático"""
        print("\n⏰ INICIANDO MODO AUTOMÁTICO")
        print("-" * 30)
        
        status = self.scraper.get_status()
        if status['current_phase'] == 'initial':
            print("📅 Configuración:")
            print(f"   • Fase: {status['current_phase'].upper()}")
            print(f"   • Horario: Todos los días a las {self.scraper.initial_phase_start_time}")
            print(f"   • Duración: {self.scraper.initial_phase_hours} horas por sesión")
        else:
            print("📅 Configuración:")
            print(f"   • Fase: {status['current_phase'].upper()}")
            print(f"   • Horario: Lunes a las {self.scraper.maintenance_phase_start_time}")
            print(f"   • Frecuencia: Semanal")
        
        confirm = input("\n¿Iniciar modo automático? (s/n): ").lower()
        if confirm == 's':
            try:
                print("⏰ Iniciando programador automático...")
                print("💡 Presione Ctrl+C para detener")
                self.scraper.start_scheduler()
            except KeyboardInterrupt:
                print("\n🛑 Modo automático detenido")
            except Exception as e:
                print(f"❌ Error en modo automático: {e}")
        else:
            print("❌ Operación cancelada")
    
    def show_recent_logs(self):
        """Mostrar logs recientes"""
        print("\n📋 LOGS RECIENTES")
        print("-" * 20)
        
        log_file = "logs/auto_scraper.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Mostrar últimas 20 líneas
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    for line in recent_lines:
                        print(line.strip())
            except Exception as e:
                print(f"❌ Error leyendo logs: {e}")
        else:
            print("📄 No hay archivo de logs")
    
    def run(self):
        """Ejecutar controlador"""
        print("🤖 Iniciando controlador de scraping inteligente...")
        
        while True:
            try:
                self.show_menu()
                option = input("\nSeleccione opción: ")
                
                if option == "1":
                    self.show_status()
                elif option == "2":
                    self.start_initial_phase()
                elif option == "3":
                    self.run_maintenance()
                elif option == "4":
                    self.configure_parameters()
                elif option == "5":
                    self.show_detailed_stats()
                elif option == "6":
                    self.run_manual_session()
                elif option == "7":
                    self.start_automatic_mode()
                elif option == "8":
                    print("🛑 Deteniendo sistema...")
                    break
                elif option == "9":
                    self.show_recent_logs()
                elif option == "0":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                
                input("\nPresione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n🛑 Operación cancelada por el usuario")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presione Enter para continuar...")

if __name__ == "__main__":
    controller = AutoScraperController()
    controller.run() 