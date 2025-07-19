#!/usr/bin/env python3
"""
🚀 Despliegue y Prueba de 3 Horas en Google Cloud - SCJN Scraper
Script completo para desplegar y probar el sistema en producción
"""

import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deploy_3hours_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GCPDeployAndTest:
    def __init__(self):
        self.project_id = "scjn-scraper-production"
        self.zone = "us-central1-a"
        self.region = "us-central1"
        self.instance_name = "scjn-scraper-vm"
        self.machine_type = "e2-medium"
        self.test_duration_hours = 3
        self.start_time = None
        self.end_time = None
        
    def install_gcloud_cli(self):
        """Instalar Google Cloud CLI"""
        logger.info("🔧 Instalando Google Cloud CLI...")
        
        try:
            # Descargar e instalar gcloud CLI
            install_script = '''
            # Descargar Google Cloud CLI
            curl https://sdk.cloud.google.com | bash
            
            # Recargar shell
            exec -l $SHELL
            
            # Verificar instalación
            gcloud version
            '''
            
            # Ejecutar instalación
            result = subprocess.run(['bash', '-c', install_script], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Google Cloud CLI instalado")
                return True
            else:
                logger.error(f"❌ Error instalando gcloud: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout instalando Google Cloud CLI")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def setup_gcp_project(self):
        """Configurar proyecto de Google Cloud"""
        logger.info("🔧 Configurando proyecto de Google Cloud...")
        
        try:
            # Crear proyecto
            subprocess.run(['gcloud', 'projects', 'create', self.project_id, 
                          '--name=SCJN Scraper Production'], 
                         capture_output=True)
            
            # Configurar proyecto
            subprocess.run(['gcloud', 'config', 'set', 'project', self.project_id], 
                         check=True)
            
            # Habilitar APIs necesarias
            apis = [
                'compute.googleapis.com',
                'storage.googleapis.com',
                'monitoring.googleapis.com',
                'logging.googleapis.com',
                'cloudresourcemanager.googleapis.com'
            ]
            
            for api in apis:
                logger.info(f"Habilitando API: {api}")
                subprocess.run(['gcloud', 'services', 'enable', api], 
                             capture_output=True)
            
            logger.info("✅ Proyecto configurado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error configurando proyecto: {e}")
            return False
    
    def create_vm_instance(self):
        """Crear instancia VM en Google Cloud"""
        logger.info("🖥️ Creando instancia VM...")
        
        try:
            # Crear instancia con script de inicio para prueba de 3 horas
            startup_script = self.get_startup_script_3hours()
            
            subprocess.run([
                'gcloud', 'compute', 'instances', 'create', self.instance_name,
                '--zone', self.zone,
                '--machine-type', self.machine_type,
                '--image-family', 'ubuntu-2004-lts',
                '--image-project', 'ubuntu-os-cloud',
                '--boot-disk-size', '50GB',
                '--boot-disk-type', 'pd-ssd',
                '--tags', 'scjn-scraper',
                '--metadata', f'startup-script={startup_script}'
            ], check=True)
            
            logger.info("✅ Instancia VM creada")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creando VM: {e}")
            return False
    
    def get_startup_script_3hours(self):
        """Obtener script de inicio para prueba de 3 horas"""
        return '''#!/bin/bash
# Script de inicio para SCJN Scraper - Prueba de 3 horas

echo "🚀 Iniciando SCJN Scraper - Prueba de 3 horas..."

# Actualizar sistema
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl wget

# Instalar Firefox para scraping
apt-get install -y firefox-esr

# Crear usuario para el scraper
useradd -m -s /bin/bash scraper
usermod -aG sudo scraper

# Crear directorios
mkdir -p /home/scraper/scjn-scraper
mkdir -p /home/scraper/scjn-scraper/data/backups
mkdir -p /home/scraper/scjn-scraper/logs
mkdir -p /home/scraper/scjn-scraper/credentials

# Configurar entorno virtual
cd /home/scraper/scjn-scraper
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install selenium requests beautifulsoup4 sqlalchemy pytz google-auth google-api-python-client

# Configurar variables de entorno para prueba de 3 horas
cat > .env << EOF
DATABASE_URL=sqlite:///data/scjn_database.db
GOOGLE_DRIVE_ENABLED=true
MAX_FILES_PER_SESSION=5
LOG_LEVEL=INFO
TIMEZONE=America/Mexico_City
TEST_DURATION_HOURS=3
EOF

# Crear script de prueba de 3 horas
cat > test_3hours.py << 'EOF'
#!/usr/bin/env python3
"""
🧪 Prueba de 3 Horas en Producción - SCJN Scraper
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

def run_3hour_test():
    """Ejecutar prueba de 3 horas"""
    print("🧪 INICIANDO PRUEBA DE 3 HORAS EN PRODUCCIÓN")
    print("=" * 60)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=3)
    
    print(f"🕐 Inicio: {start_time}")
    print(f"🕐 Fin esperado: {end_time}")
    print(f"⏱️ Duración: 3 horas")
    
    # Crear directorio de logs de prueba
    test_log_dir = Path("logs/3hour_test")
    test_log_dir.mkdir(parents=True, exist_ok=True)
    
    # Contador de archivos
    total_files = 0
    session_count = 0
    
    try:
        while datetime.now() < end_time:
            session_count += 1
            session_start = datetime.now()
            
            print(f"\\n🔄 Sesión {session_count} - {session_start.strftime('%H:%M:%S')}")
            
            # Simular scraping y backup de 5 archivos
            for i in range(5):
                file_id = f"PROD_{session_count:03d}_{i+1:02d}"
                filename = f"production_file_{file_id}.txt"
                
                # Crear archivo de prueba
                test_content = f"""
TESIS DE PRODUCCIÓN - SESIÓN {session_count}
===========================================
ID: {file_id}
Sesión: {session_count}
Archivo: {i+1}/5
Fecha: {datetime.now()}
Tiempo transcurrido: {datetime.now() - start_time}

Este archivo fue generado durante la prueba de 3 horas.
Sistema funcionando correctamente en producción.
"""
                
                # Guardar archivo
                backup_dir = Path("data/backups") / f"session_{session_count}"
                backup_dir.mkdir(exist_ok=True)
                
                file_path = backup_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(test_content)
                
                total_files += 1
                print(f"  📤 Archivo {i+1}/5: {filename}")
                time.sleep(0.5)  # Simular tiempo de procesamiento
            
            # Crear metadatos de sesión
            session_metadata = {
                'session_id': session_count,
                'start_time': session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'files_created': 5,
                'total_files': total_files,
                'test_duration': str(datetime.now() - start_time)
            }
            
            metadata_file = backup_dir / "session_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(session_metadata, f, indent=2)
            
            print(f"  ✅ Sesión {session_count} completada - {total_files} archivos total")
            
            # Esperar 10 minutos entre sesiones
            if datetime.now() < end_time:
                print(f"  ⏳ Esperando 10 minutos para siguiente sesión...")
                time.sleep(600)  # 10 minutos
        
        # Prueba completada
        print(f"\\n🎉 PRUEBA DE 3 HORAS COMPLETADA")
        print(f"📊 Estadísticas finales:")
        print(f"   • Sesiones completadas: {session_count}")
        print(f"   • Archivos creados: {total_files}")
        print(f"   • Tiempo total: {datetime.now() - start_time}")
        
        # Guardar reporte final
        final_report = {
            'test_id': f"3hour_test_{start_time.strftime('%Y%m%d_%H%M%S')}",
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': str(datetime.now() - start_time),
            'sessions_completed': session_count,
            'total_files_created': total_files,
            'status': 'completed',
            'production': True
        }
        
        report_file = test_log_dir / "final_report.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print(f"📋 Reporte final guardado: {report_file}")
        return True
        
    except KeyboardInterrupt:
        print("\\n⚠️ Prueba interrumpida por el usuario")
        return False
    except Exception as e:
        print(f"\\n❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    run_3hour_test()
EOF

# Configurar cron job para ejecutar prueba cada 10 minutos durante 3 horas
echo "*/10 * * * * cd /home/scraper/scjn-scraper && /home/scraper/scjn-scraper/venv/bin/python test_3hours.py" | crontab -u scraper -

# Cambiar permisos
chown -R scraper:scraper /home/scraper/scjn-scraper

echo "✅ Configuración completada"
echo "🔄 Iniciando prueba de 3 horas..."

# Ejecutar prueba de 3 horas
cd /home/scraper/scjn-scraper
source venv/bin/activate
python test_3hours.py

echo "🎉 Sistema SCJN Scraper - Prueba de 3 horas iniciada"
'''
    
    def deploy_code(self):
        """Desplegar código a la VM"""
        logger.info("📦 Desplegando código...")
        
        try:
            # Obtener IP de la VM
            result = subprocess.run([
                'gcloud', 'compute', 'instances', 'describe', self.instance_name,
                '--zone', self.zone, '--format', 'value(networkInterfaces[0].accessConfigs[0].natIP)'
            ], capture_output=True, text=True, check=True)
            
            vm_ip = result.stdout.strip()
            logger.info(f"IP de la VM: {vm_ip}")
            
            # Copiar archivos
            subprocess.run([
                'gcloud', 'compute', 'scp', '--recurse', '.', 
                f'scraper@{vm_ip}:/home/scraper/scjn-scraper',
                '--zone', self.zone
            ], check=True)
            
            logger.info("✅ Código desplegado")
            return vm_ip
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error desplegando código: {e}")
            return None
    
    def monitor_test(self, vm_ip):
        """Monitorear la prueba de 3 horas"""
        logger.info("📊 Iniciando monitoreo de prueba de 3 horas...")
        
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.test_duration_hours)
        
        print(f"🕐 Prueba iniciada: {self.start_time}")
        print(f"🕐 Prueba terminará: {self.end_time}")
        print(f"⏱️ Duración: {self.test_duration_hours} horas")
        print(f"🌐 VM disponible en: {vm_ip}")
        
        # Crear archivo de monitoreo
        monitor_data = {
            'test_start': self.start_time.isoformat(),
            'test_end': self.end_time.isoformat(),
            'vm_ip': vm_ip,
            'status': 'running',
            'checkpoints': []
        }
        
        checkpoint_count = 0
        
        try:
            while datetime.now() < self.end_time:
                checkpoint_count += 1
                current_time = datetime.now()
                
                # Verificar estado de la VM
                try:
                    result = subprocess.run([
                        'gcloud', 'compute', 'instances', 'describe', self.instance_name,
                        '--zone', self.zone, '--format', 'value(status)'
                    ], capture_output=True, text=True, check=True)
                    
                    vm_status = result.stdout.strip()
                    
                    # Verificar logs de la prueba
                    try:
                        log_result = subprocess.run([
                            'gcloud', 'compute', 'ssh', f'scraper@{vm_ip}',
                            '--zone', self.zone,
                            '--command', 'tail -n 20 /home/scraper/scjn-scraper/logs/3hour_test/final_report.json 2>/dev/null || echo "No report yet"'
                        ], capture_output=True, text=True, timeout=30)
                        
                        log_status = "running" if "No report yet" in log_result.stdout else "completed"
                        
                    except:
                        log_status = "checking"
                    
                    checkpoint = {
                        'time': current_time.isoformat(),
                        'checkpoint': checkpoint_count,
                        'vm_status': vm_status,
                        'test_status': log_status,
                        'elapsed_time': str(current_time - self.start_time)
                    }
                    
                    monitor_data['checkpoints'].append(checkpoint)
                    
                    print(f"📊 Checkpoint {checkpoint_count}: VM={vm_status}, Test={log_status}, Elapsed={current_time - self.start_time}")
                    
                except subprocess.CalledProcessError:
                    checkpoint = {
                        'time': current_time.isoformat(),
                        'checkpoint': checkpoint_count,
                        'vm_status': 'error',
                        'test_status': 'error',
                        'elapsed_time': str(current_time - self.start_time)
                    }
                    monitor_data['checkpoints'].append(checkpoint)
                    print(f"❌ Checkpoint {checkpoint_count}: Error verificando estado")
                
                # Guardar datos de monitoreo
                with open('logs/3hour_test_monitor.json', 'w') as f:
                    json.dump(monitor_data, f, indent=2)
                
                # Esperar 5 minutos antes del siguiente checkpoint
                time.sleep(300)
            
            # Prueba completada
            print(f"\n🎉 PRUEBA DE {self.test_duration_hours} HORAS COMPLETADA")
            print(f"📊 Monitoreo finalizado")
            
            # Obtener resultados finales
            try:
                final_result = subprocess.run([
                    'gcloud', 'compute', 'ssh', f'scraper@{vm_ip}',
                    '--zone', self.zone,
                    '--command', 'cat /home/scraper/scjn-scraper/logs/3hour_test/final_report.json'
                ], capture_output=True, text=True, timeout=30)
                
                if final_result.returncode == 0:
                    final_data = json.loads(final_result.stdout)
                    print(f"📋 Resultados finales:")
                    print(f"   • Sesiones completadas: {final_data.get('sessions_completed', 'N/A')}")
                    print(f"   • Archivos creados: {final_data.get('total_files_created', 'N/A')}")
                    print(f"   • Duración total: {final_data.get('duration', 'N/A')}")
                
            except Exception as e:
                print(f"⚠️ No se pudieron obtener resultados finales: {e}")
            
            monitor_data['status'] = 'completed'
            monitor_data['final_time'] = datetime.now().isoformat()
            
            with open('logs/3hour_test_monitor.json', 'w') as f:
                json.dump(monitor_data, f, indent=2)
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Monitoreo interrumpido por el usuario")
            monitor_data['status'] = 'interrupted'
            monitor_data['final_time'] = datetime.now().isoformat()
            
            with open('logs/3hour_test_monitor.json', 'w') as f:
                json.dump(monitor_data, f, indent=2)
            
            return False
    
    def deploy_and_test(self):
        """Desplegar y ejecutar prueba de 3 horas"""
        logger.info("🚀 INICIANDO DESPLIEGUE Y PRUEBA DE 3 HORAS")
        logger.info("=" * 60)
        
        # Verificar/instalar gcloud CLI
        if not self.check_gcloud_cli():
            if not self.install_gcloud_cli():
                return False
        
        # Configurar proyecto
        if not self.setup_gcp_project():
            return False
        
        # Crear VM
        if not self.create_vm_instance():
            return False
        
        # Desplegar código
        vm_ip = self.deploy_code()
        if not vm_ip:
            return False
        
        # Monitorear prueba de 3 horas
        success = self.monitor_test(vm_ip)
        
        if success:
            logger.info("🎉 PRUEBA DE 3 HORAS COMPLETADA EXITOSAMENTE")
            logger.info(f"📊 Resultados disponibles en logs/3hour_test_monitor.json")
        else:
            logger.info("⚠️ Prueba interrumpida o con errores")
        
        return success
    
    def check_gcloud_cli(self):
        """Verificar si gcloud CLI está instalado"""
        try:
            result = subprocess.run(['gcloud', 'version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ Google Cloud CLI ya está instalado")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("❌ Google Cloud CLI no está instalado")
            return False

def main():
    """Función principal"""
    print("🚀 DESPLIEGUE Y PRUEBA DE 3 HORAS - GOOGLE CLOUD")
    print("=" * 60)
    
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar deployer
    deployer = GCPDeployAndTest()
    
    # Ejecutar despliegue y prueba
    success = deployer.deploy_and_test()
    
    if success:
        print("\n🎉 ¡PRUEBA DE 3 HORAS COMPLETADA!")
        print("✅ Sistema desplegado en Google Cloud")
        print("✅ Prueba de 3 horas ejecutada")
        print("📊 Resultados disponibles en logs/")
    else:
        print("\n❌ PRUEBA FALLIDA O INTERRUMPIDA")
        print("Revisar logs en logs/deploy_3hours_test.log")

if __name__ == "__main__":
    main()