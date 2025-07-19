#!/usr/bin/env python3
"""
🚀 Despliegue en Google Cloud - Sistema de Scraping SCJN
Configuración para producción con prueba de resguardo de 5 archivos
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deploy_gcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GCPDeployer:
    def __init__(self):
        self.project_id = "scjn-scraper-production"
        self.zone = "us-central1-a"
        self.region = "us-central1"
        self.instance_name = "scjn-scraper-vm"
        self.machine_type = "e2-medium"
        self.bucket_name = "scjn-scraper-backups"
        
    def check_gcloud_cli(self):
        """Verificar que gcloud CLI esté instalado y configurado"""
        logger.info("🔍 Verificando Google Cloud CLI...")
        
        try:
            # Verificar instalación
            result = subprocess.run(['gcloud', 'version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ Google Cloud CLI instalado")
            
            # Verificar autenticación
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                                  capture_output=True, text=True, check=True)
            if 'ACTIVE' not in result.stdout:
                logger.error("❌ Google Cloud CLI no está autenticado")
                logger.info("Ejecute: gcloud auth login")
                return False
                
            logger.info("✅ Google Cloud CLI autenticado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error verificando gcloud: {e}")
            return False
        except FileNotFoundError:
            logger.error("❌ Google Cloud CLI no está instalado")
            return False
    
    def setup_project(self):
        """Configurar proyecto de Google Cloud"""
        logger.info("🔧 Configurando proyecto...")
        
        try:
            # Crear proyecto si no existe
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
            
            logger.info("✅ Proyecto configurado correctamente")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error configurando proyecto: {e}")
            return False
    
    def create_storage_bucket(self):
        """Crear bucket de Cloud Storage para backups"""
        logger.info("🪣 Creando bucket de Cloud Storage...")
        
        try:
            # Crear bucket
            subprocess.run(['gsutil', 'mb', '-l', self.region, 
                          f'gs://{self.bucket_name}'], 
                         capture_output=True)
            
            # Configurar lifecycle para backups
            lifecycle_config = {
                "rule": [
                    {
                        "action": {"type": "Delete"},
                        "condition": {
                            "age": 365,
                            "matchesPrefix": ["backups/"]
                        }
                    },
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                        "condition": {
                            "age": 30,
                            "matchesPrefix": ["backups/"]
                        }
                    }
                ]
            }
            
            with open('lifecycle.json', 'w') as f:
                json.dump(lifecycle_config, f)
            
            subprocess.run(['gsutil', 'lifecycle', 'set', 'lifecycle.json', 
                          f'gs://{self.bucket_name}'], 
                         check=True)
            
            os.remove('lifecycle.json')
            logger.info("✅ Bucket de Cloud Storage creado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creando bucket: {e}")
            return False
    
    def create_vm_instance(self):
        """Crear instancia de VM en Google Cloud"""
        logger.info("🖥️ Creando instancia VM...")
        
        try:
            # Crear instancia
            subprocess.run([
                'gcloud', 'compute', 'instances', 'create', self.instance_name,
                '--zone', self.zone,
                '--machine-type', self.machine_type,
                '--image-family', 'ubuntu-2004-lts',
                '--image-project', 'ubuntu-os-cloud',
                '--boot-disk-size', '50GB',
                '--boot-disk-type', 'pd-ssd',
                '--tags', 'scjn-scraper',
                '--metadata', 'startup-script=' + self.get_startup_script()
            ], check=True)
            
            logger.info("✅ Instancia VM creada")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creando VM: {e}")
            return False
    
    def get_startup_script(self):
        """Obtener script de inicio para la VM"""
        return '''#!/bin/bash
# Script de inicio para SCJN Scraper

# Actualizar sistema
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl wget

# Instalar Firefox para scraping
apt-get install -y firefox-esr

# Crear usuario para el scraper
useradd -m -s /bin/bash scraper
usermod -aG sudo scraper

# Clonar repositorio
cd /home/scraper
git clone https://github.com/Lbassoco95/ia-ius-scrapping.git
chown -R scraper:scraper ia-ius-scrapping

# Configurar entorno
cd ia-ius-scrapping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p data/pdfs logs credentials

# Configurar variables de entorno
cp env.example .env
sed -i 's/DATABASE_URL=.*/DATABASE_URL=sqlite:\/\/\/home\/scraper\/ia-ius-scrapping\/data\/scjn_database.db/' .env
sed -i 's/GOOGLE_DRIVE_ENABLED=.*/GOOGLE_DRIVE_ENABLED=true/' .env
sed -i 's/MAX_FILES_PER_SESSION=.*/MAX_FILES_PER_SESSION=5/' .env

# Configurar cron job para scraping
echo "0 */6 * * * cd /home/scraper/ia-ius-scrapping && /home/scraper/ia-ius-scrapping/venv/bin/python run_scraping_now.py" | crontab -u scraper -

# Iniciar scraping de prueba
cd /home/scraper/ia-ius-scrapping
source venv/bin/activate
python run_scraping_now.py
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
                f'scraper@{vm_ip}:/home/scraper/ia-ius-scrapping',
                '--zone', self.zone
            ], check=True)
            
            logger.info("✅ Código desplegado")
            return vm_ip
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error desplegando código: {e}")
            return None
    
    def configure_backup_test(self):
        """Configurar prueba de resguardo de 5 archivos"""
        logger.info("🔄 Configurando prueba de resguardo...")
        
        try:
            # Crear script de prueba de backup
            backup_test_script = '''#!/usr/bin/env python3
"""
Prueba de resguardo de 5 archivos en producción
"""

import os
import sys
import time
from datetime import datetime
import subprocess

# Agregar src al path
sys.path.append('/home/scraper/ia-ius-scrapping/src')

def test_backup_5_files():
    """Probar resguardo de 5 archivos"""
    print("🧪 PRUEBA DE RESGUARDO - 5 ARCHIVOS")
    print("=" * 50)
    
    try:
        # Importar componentes
        from database.models import create_tables, get_session, Tesis
        from storage.google_drive import GoogleDriveManager
        
        # Crear tablas
        create_tables()
        print("✅ Base de datos configurada")
        
        # Configurar Google Drive
        gdrive = GoogleDriveManager()
        print("✅ Google Drive configurado")
        
        # Simular 5 archivos de prueba
        test_files = []
        for i in range(5):
            test_file = {
                'scjn_id': f'TEST_{i+1:03d}',
                'titulo': f'Tesis de prueba {i+1}',
                'url': f'https://sjf2.scjn.gob.mx/tesis/{i+1}',
                'pdf_url': f'https://sjf2.scjn.gob.mx/pdf/{i+1}.pdf',
                'fecha_descarga': datetime.now()
            }
            test_files.append(test_file)
        
        print(f"📄 Archivos de prueba creados: {len(test_files)}")
        
        # Guardar en base de datos
        session = get_session()
        for file_data in test_files:
            tesis = Tesis(**file_data)
            session.add(tesis)
        session.commit()
        session.close()
        
        print("✅ Archivos guardados en base de datos")
        
        # Crear backup en Google Drive
        backup_folder = f"backup_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        gdrive.create_folder(backup_folder)
        
        # Subir archivos de prueba
        for i, file_data in enumerate(test_files):
            # Crear archivo de prueba
            test_content = f"Contenido de prueba para {file_data['titulo']}"
            test_filename = f"test_file_{i+1}.txt"
            
            with open(test_filename, 'w') as f:
                f.write(test_content)
            
            # Subir a Google Drive
            gdrive.upload_file(test_filename, backup_folder)
            os.remove(test_filename)
            
            print(f"📤 Archivo {i+1}/5 subido: {test_filename}")
        
        print("✅ Backup completado en Google Drive")
        
        # Verificar archivos en Google Drive
        files = gdrive.list_files(backup_folder)
        print(f"📊 Archivos en backup: {len(files)}")
        
        if len(files) == 5:
            print("🎉 PRUEBA EXITOSA: 5 archivos resguardados correctamente")
            return True
        else:
            print(f"❌ PRUEBA FALLIDA: Se esperaban 5 archivos, se encontraron {len(files)}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de backup: {e}")
        return False

if __name__ == "__main__":
    test_backup_5_files()
'''
            
            with open('backup_test.py', 'w') as f:
                f.write(backup_test_script)
            
            logger.info("✅ Script de prueba de backup creado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando prueba de backup: {e}")
            return False
    
    def run_production_test(self, vm_ip):
        """Ejecutar prueba de producción"""
        logger.info("🚀 Ejecutando prueba de producción...")
        
        try:
            # Ejecutar prueba de backup
            subprocess.run([
                'gcloud', 'compute', 'ssh', f'scraper@{vm_ip}',
                '--zone', self.zone,
                '--command', 'cd /home/scraper/ia-ius-scrapping && source venv/bin/activate && python backup_test.py'
            ], check=True)
            
            logger.info("✅ Prueba de producción ejecutada")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error ejecutando prueba: {e}")
            return False
    
    def deploy(self):
        """Desplegar sistema completo"""
        logger.info("🚀 INICIANDO DESPLIEGUE EN GOOGLE CLOUD")
        logger.info("=" * 50)
        
        # Verificar gcloud CLI
        if not self.check_gcloud_cli():
            return False
        
        # Configurar proyecto
        if not self.setup_project():
            return False
        
        # Crear bucket de storage
        if not self.create_storage_bucket():
            return False
        
        # Crear VM
        if not self.create_vm_instance():
            return False
        
        # Configurar prueba de backup
        if not self.configure_backup_test():
            return False
        
        # Desplegar código
        vm_ip = self.deploy_code()
        if not vm_ip:
            return False
        
        # Ejecutar prueba de producción
        if not self.run_production_test(vm_ip):
            return False
        
        logger.info("🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE")
        logger.info(f"🌐 VM disponible en: {vm_ip}")
        logger.info("📊 Prueba de resguardo de 5 archivos ejecutada")
        
        return True

def main():
    """Función principal"""
    print("🚀 DESPLIEGUE EN GOOGLE CLOUD - SCJN SCRAPER")
    print("=" * 50)
    
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar deployer
    deployer = GCPDeployer()
    
    # Ejecutar despliegue
    success = deployer.deploy()
    
    if success:
        print("\n🎉 ¡DESPLIEGUE EXITOSO!")
        print("El sistema está funcionando en Google Cloud")
        print("Prueba de resguardo de 5 archivos completada")
    else:
        print("\n❌ DESPLIEGUE FALLIDO")
        print("Revisar logs en logs/deploy_gcp.log")

if __name__ == "__main__":
    main()