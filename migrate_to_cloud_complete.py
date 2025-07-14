#!/usr/bin/env python3
"""
Script maestro para migración completa a Google Cloud
"""

import subprocess
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/cloud_migration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CloudMigrationMaster:
    def __init__(self):
        self.steps_completed = []
        
    def run_command(self, command, description):
        """Ejecutar comando con descripción"""
        logger.info(f"🚀 {description}")
        print(f"\n🔄 {description}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ {description} completado")
            self.steps_completed.append(description)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error en {description}: {e.stderr}")
            print(f"❌ Error en {description}")
            return False
    
    def check_prerequisites(self):
        """Verificar prerequisitos"""
        logger.info("🔍 Verificando prerequisitos...")
        
        # Verificar gcloud
        if not self.run_command("gcloud --version", "Verificar gcloud CLI"):
            print("❌ gcloud CLI no está instalado o configurado")
            return False
        
        # Verificar proyecto
        project = subprocess.run(
            "gcloud config get-value project",
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if not project:
            print("❌ No hay proyecto configurado en gcloud")
            print("💡 Ejecuta: gcloud config set project [TU_PROJECT_ID]")
            return False
        
        logger.info(f"✅ Proyecto configurado: {project}")
        return True
    
    def setup_cloud_sql(self):
        """Configurar Cloud SQL"""
        return self.run_command(
            "python3 setup_cloud_sql.py",
            "Configurar Cloud SQL"
        )
    
    def update_app_config(self):
        """Actualizar configuración de la aplicación"""
        return self.run_command(
            "python3 update_app_config.py",
            "Actualizar configuración de la aplicación"
        )
    
    def install_dependencies(self):
        """Instalar dependencias"""
        return self.run_command(
            "pip install psycopg2-binary",
            "Instalar psycopg2-binary"
        )
    
    def upload_to_vm(self):
        """Subir archivos a la VM"""
        return self.run_command(
            "gcloud compute scp --recurse . scjn-scraper:~/ia-scrapping-tesis/ --zone=us-central1-a",
            "Subir archivos a la VM"
        )
    
    def run_migration_on_vm(self):
        """Ejecutar migración en la VM"""
        return self.run_command(
            "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ia-scrapping-tesis && source venv/bin/activate && pip install psycopg2-binary && python3 migrate_to_postgresql.py'",
            "Ejecutar migración en la VM"
        )
    
    def test_connection_on_vm(self):
        """Probar conexión en la VM"""
        return self.run_command(
            "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ia-scrapping-tesis && source venv/bin/activate && ./start_cloud_sql_proxy.sh && sleep 5 && python3 -c \"from src.database.models import get_session; session = get_session(); print(\\\"✅ Conexión exitosa a PostgreSQL\\\"); session.close()\"'",
            "Probar conexión a PostgreSQL en la VM"
        )
    
    def update_cron_on_vm(self):
        """Actualizar cron job en la VM"""
        return self.run_command(
            "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ia-scrapping-tesis && chmod +x vm_cron_scraper.sh && crontab -l > temp_cron && sed \"/ia-scrapping-tesis/d\" temp_cron > new_cron && echo \"0 5 * * * /home/leopoldobassoconova/ia-scrapping-tesis/vm_cron_scraper.sh\" >> new_cron && crontab new_cron && rm temp_cron new_cron'",
            "Actualizar cron job en la VM"
        )
    
    def run_complete_migration(self):
        """Ejecutar migración completa"""
        logger.info("🚀 Iniciando migración completa a Google Cloud")
        print("🎯 MIGRACIÓN COMPLETA A GOOGLE CLOUD")
        print("=" * 50)
        
        try:
            # Paso 1: Verificar prerequisitos
            if not self.check_prerequisites():
                return False
            
            # Paso 2: Configurar Cloud SQL
            if not self.setup_cloud_sql():
                print("❌ Error configurando Cloud SQL")
                return False
            
            # Paso 3: Actualizar configuración de la aplicación
            if not self.update_app_config():
                print("❌ Error actualizando configuración")
                return False
            
            # Paso 4: Instalar dependencias localmente
            if not self.install_dependencies():
                print("❌ Error instalando dependencias")
                return False
            
            # Paso 5: Subir archivos a la VM
            if not self.upload_to_vm():
                print("❌ Error subiendo archivos a la VM")
                return False
            
            # Paso 6: Ejecutar migración en la VM
            if not self.run_migration_on_vm():
                print("❌ Error ejecutando migración en la VM")
                return False
            
            # Paso 7: Probar conexión en la VM
            if not self.test_connection_on_vm():
                print("❌ Error probando conexión en la VM")
                return False
            
            # Paso 8: Actualizar cron job en la VM
            if not self.update_cron_on_vm():
                print("❌ Error actualizando cron job en la VM")
                return False
            
            # Éxito
            logger.info("🎉 Migración completa exitosa")
            print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("=" * 50)
            print("✅ Tu sistema ahora está completamente en Google Cloud")
            print("✅ Base de datos migrada a Cloud SQL (PostgreSQL)")
            print("✅ Scraper configurado para ejecutarse automáticamente a las 5:00 AM")
            print("✅ Sistema funcionando 24/7 sin necesidad de tu computadora")
            
            print("\n📊 Resumen de pasos completados:")
            for i, step in enumerate(self.steps_completed, 1):
                print(f"   {i}. {step}")
            
            print("\n🔍 Para monitorear:")
            print("   - Logs de la VM: gcloud compute ssh scjn-scraper --zone=us-central1-a")
            print("   - Cloud SQL: https://console.cloud.google.com/sql")
            print("   - Compute Engine: https://console.cloud.google.com/compute")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en migración completa: {e}")
            print(f"❌ Error en migración: {e}")
            return False

def main():
    """Función principal"""
    
    print("🌤️  MIGRACIÓN A GOOGLE CLOUD - SISTEMA SCJN")
    print("=" * 50)
    print("Este script migrará tu sistema completo a Google Cloud:")
    print("  • Creará Cloud SQL (PostgreSQL)")
    print("  • Migrará datos de SQLite a PostgreSQL")
    print("  • Configurará la VM para usar la nueva base de datos")
    print("  • Actualizará el cron job automático")
    print("=" * 50)
    
    # Preguntar confirmación
    response = input("\n¿Continuar con la migración? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'sí', 'si']:
        print("❌ Migración cancelada")
        return False
    
    # Ejecutar migración
    migrator = CloudMigrationMaster()
    success = migrator.run_complete_migration()
    
    if success:
        print("\n🎉 ¡FELICITACIONES! Tu sistema está ahora en la nube")
        print("💡 Puedes apagar tu computadora, el sistema seguirá funcionando")
    else:
        print("\n❌ La migración no se completó. Revisa los logs para más detalles")
    
    return success

if __name__ == "__main__":
    main() 