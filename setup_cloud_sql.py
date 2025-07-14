#!/usr/bin/env python3
"""
Script para configurar Cloud SQL automáticamente
"""

import subprocess
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/cloud_sql_setup.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CloudSQLSetup:
    def __init__(self, project_id, region="us-central1"):
        self.project_id = project_id
        self.region = region
        self.instance_name = "scjn-scraper-db"
        self.database_name = "scjn_database"
        self.user_name = "scjn_user"
        self.password = None
        
    def generate_secure_password(self):
        """Generar password seguro"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        self.password = ''.join(secrets.choice(alphabet) for i in range(16))
        return self.password
    
    def run_gcloud_command(self, command, check=True):
        """Ejecutar comando gcloud"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                logger.info(f"✅ Comando exitoso: {command}")
                return result.stdout.strip()
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error ejecutando comando: {command}")
            logger.error(f"   Error: {e.stderr}")
            return False
    
    def check_project_exists(self):
        """Verificar que el proyecto existe"""
        logger.info(f"🔍 Verificando proyecto: {self.project_id}")
        
        result = self.run_gcloud_command(f"gcloud projects describe {self.project_id}", check=False)
        if result:
            logger.info(f"✅ Proyecto {self.project_id} encontrado")
            return True
        else:
            logger.error(f"❌ Proyecto {self.project_id} no encontrado")
            return False
    
    def enable_apis(self):
        """Habilitar APIs necesarias"""
        logger.info("🔧 Habilitando APIs necesarias...")
        
        apis = [
            "compute.googleapis.com",
            "sqladmin.googleapis.com",
            "storage.googleapis.com",
            "monitoring.googleapis.com"
        ]
        
        for api in apis:
            logger.info(f"   Habilitando {api}...")
            self.run_gcloud_command(f"gcloud services enable {api}")
    
    def create_sql_instance(self):
        """Crear instancia de Cloud SQL"""
        logger.info(f"🗄️ Creando instancia Cloud SQL: {self.instance_name}")
        
        command = f"""
        gcloud sql instances create {self.instance_name} \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region={self.region} \
            --storage-type=SSD \
            --storage-size=20GB \
            --backup-start-time=02:00 \
            --maintenance-window-day=SUN \
            --maintenance-window-hour=03 \
            --authorized-networks=0.0.0.0/0 \
            --require-ssl
        """
        
        return self.run_gcloud_command(command)
    
    def create_database(self):
        """Crear base de datos"""
        logger.info(f"📊 Creando base de datos: {self.database_name}")
        
        command = f"gcloud sql databases create {self.database_name} --instance={self.instance_name}"
        return self.run_gcloud_command(command)
    
    def create_user(self):
        """Crear usuario de base de datos"""
        if not self.password:
            self.generate_secure_password()
        
        logger.info(f"👤 Creando usuario: {self.user_name}")
        
        command = f"gcloud sql users create {self.user_name} --instance={self.instance_name} --password='{self.password}'"
        return self.run_gcloud_command(command)
    
    def get_connection_info(self):
        """Obtener información de conexión"""
        logger.info("🔗 Obteniendo información de conexión...")
        
        # Obtener connection name
        connection_name = self.run_gcloud_command(
            f"gcloud sql instances describe {self.instance_name} --format='get(connectionName)'"
        )
        
        # Obtener IP pública
        public_ip = self.run_gcloud_command(
            f"gcloud sql instances describe {self.instance_name} --format='get(ipAddresses[0].ipAddress)'"
        )
        
        return {
            'connection_name': connection_name,
            'public_ip': public_ip,
            'database': self.database_name,
            'user': self.user_name,
            'password': self.password
        }
    
    def save_config(self, connection_info):
        """Guardar configuración en archivo"""
        config = {
            'postgresql': {
                'host': connection_info['public_ip'],
                'port': 5432,
                'database': connection_info['database'],
                'user': connection_info['user'],
                'password': connection_info['password'],
                'sslmode': 'require'
            },
            'connection_name': connection_info['connection_name'],
            'setup_date': str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip())
        }
        
        config_file = Path("config/postgresql_config.json")
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 Configuración guardada en: {config_file}")
        return config_file
    
    def setup_complete(self):
        """Ejecutar configuración completa"""
        logger.info("🚀 Iniciando configuración de Cloud SQL")
        
        try:
            # Verificar proyecto
            if not self.check_project_exists():
                return False
            
            # Habilitar APIs
            self.enable_apis()
            
            # Crear instancia
            if not self.create_sql_instance():
                logger.warning("⚠️ La instancia ya existe o hubo un error")
            
            # Crear base de datos
            if not self.create_database():
                logger.warning("⚠️ La base de datos ya existe o hubo un error")
            
            # Crear usuario
            if not self.create_user():
                logger.warning("⚠️ El usuario ya existe o hubo un error")
            
            # Obtener información de conexión
            connection_info = self.get_connection_info()
            
            # Guardar configuración
            config_file = self.save_config(connection_info)
            
            logger.info("🎉 Configuración de Cloud SQL completada")
            logger.info(f"📝 Configuración guardada en: {config_file}")
            logger.info(f"🔗 Connection Name: {connection_info['connection_name']}")
            logger.info(f"🌐 IP Pública: {connection_info['public_ip']}")
            logger.info(f"👤 Usuario: {connection_info['user']}")
            logger.info(f"🔑 Password: {connection_info['password']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en configuración: {e}")
            return False

def main():
    """Función principal"""
    
    # Obtener project ID
    project_id = subprocess.run(
        "gcloud config get-value project",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    if not project_id:
        logger.error("❌ No se pudo obtener el project ID")
        logger.info("💡 Ejecuta: gcloud config set project [TU_PROJECT_ID]")
        return False
    
    logger.info(f"🏗️ Configurando Cloud SQL para proyecto: {project_id}")
    
    # Crear setup y ejecutar
    setup = CloudSQLSetup(project_id)
    success = setup.setup_complete()
    
    if success:
        print("🎉 Configuración de Cloud SQL completada exitosamente")
        print("📝 Ahora puedes ejecutar la migración con: python3 migrate_to_postgresql.py")
    else:
        print("❌ Error en la configuración. Revisa los logs para más detalles")
    
    return success

if __name__ == "__main__":
    main() 