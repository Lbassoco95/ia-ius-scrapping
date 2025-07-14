#!/usr/bin/env python3
"""
Script para actualizar la configuración de la aplicación para usar PostgreSQL
"""

import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/config_update.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AppConfigUpdater:
    def __init__(self, postgresql_config_file="config/postgresql_config.json"):
        self.postgresql_config_file = Path(postgresql_config_file)
        self.postgresql_config = None
        
    def load_postgresql_config(self):
        """Cargar configuración de PostgreSQL"""
        try:
            with open(self.postgresql_config_file, 'r') as f:
                self.postgresql_config = json.load(f)
            logger.info("✅ Configuración de PostgreSQL cargada")
            return True
        except Exception as e:
            logger.error(f"❌ Error cargando configuración PostgreSQL: {e}")
            return False
    
    def update_database_models(self):
        """Actualizar modelos de base de datos"""
        models_file = Path("src/database/models.py")
        
        if not models_file.exists():
            logger.error(f"❌ No se encontró el archivo de modelos: {models_file}")
            return False
        
        logger.info(f"📝 Actualizando modelos en: {models_file}")
        
        # Leer archivo actual
        with open(models_file, 'r') as f:
            content = f.read()
        
        # Buscar y reemplazar configuración de SQLite por PostgreSQL
        old_config = """
# Configuración SQLite
DATABASE_URL = "sqlite:///data/scjn_database.db"
engine = create_engine(DATABASE_URL, echo=False)
"""
        
        new_config = f"""
# Configuración PostgreSQL
DATABASE_URL = "postgresql://{self.postgresql_config['postgresql']['user']}:{self.postgresql_config['postgresql']['password']}@{self.postgresql_config['postgresql']['host']}:{self.postgresql_config['postgresql']['port']}/{self.postgresql_config['postgresql']['database']}"
engine = create_engine(DATABASE_URL, echo=False)
"""
        
        if old_config in content:
            content = content.replace(old_config, new_config)
            
            # Escribir archivo actualizado
            with open(models_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Modelos actualizados para PostgreSQL")
            return True
        else:
            logger.warning("⚠️ No se encontró configuración SQLite para reemplazar")
            return False
    
    def update_requirements(self):
        """Actualizar requirements.txt para incluir psycopg2"""
        requirements_file = Path("requirements.txt")
        
        if not requirements_file.exists():
            logger.error(f"❌ No se encontró requirements.txt")
            return False
        
        logger.info(f"📦 Actualizando requirements.txt")
        
        # Leer archivo actual
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Verificar si ya tiene psycopg2
        if "psycopg2" not in content:
            # Agregar psycopg2 al final
            content += "\n# PostgreSQL driver\npsycopg2-binary==2.9.9\n"
            
            # Escribir archivo actualizado
            with open(requirements_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ psycopg2-binary agregado a requirements.txt")
            return True
        else:
            logger.info("ℹ️ psycopg2 ya está en requirements.txt")
            return True
    
    def create_cloud_sql_proxy_script(self):
        """Crear script para Cloud SQL Proxy"""
        proxy_script = """#!/bin/bash
# Script para iniciar Cloud SQL Proxy

# Descargar Cloud SQL Proxy si no existe
if [ ! -f "cloud_sql_proxy" ]; then
    echo "📥 Descargando Cloud SQL Proxy..."
    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    chmod +x cloud_sql_proxy
fi

# Obtener connection name desde la configuración
CONNECTION_NAME=$(python3 -c "
import json
with open('config/postgresql_config.json', 'r') as f:
    config = json.load(f)
print(config['connection_name'])
")

echo "🔗 Iniciando Cloud SQL Proxy para: $CONNECTION_NAME"

# Iniciar proxy
./cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:5432 &

# Esperar a que el proxy esté listo
sleep 5

echo "✅ Cloud SQL Proxy iniciado"
"""
        
        proxy_file = Path("start_cloud_sql_proxy.sh")
        with open(proxy_file, 'w') as f:
            f.write(proxy_script)
        
        # Hacer ejecutable
        proxy_file.chmod(0o755)
        
        logger.info(f"✅ Script de Cloud SQL Proxy creado: {proxy_file}")
        return True
    
    def update_vm_cron_script(self):
        """Actualizar script de cron de la VM para usar PostgreSQL"""
        cron_script = """#!/bin/bash

# Script para ejecutar el scraping desde cron en Google Cloud VM
# Configurar variables de entorno
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Directorio del proyecto en la VM
PROJECT_DIR="/home/leopoldobassoconova/ia-scrapping-tesis"

# Activar entorno virtual
source "$PROJECT_DIR/venv/bin/activate"

# Configurar variables de entorno para Google Drive
export GOOGLE_DRIVE_ENABLED="true"
export GOOGLE_DRIVE_FOLDER_ID="0AAL0nxoqH30XUk9PVA"
export GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH="$PROJECT_DIR/service_account.json"

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Iniciar Cloud SQL Proxy
echo "🔗 Iniciando Cloud SQL Proxy..."
./start_cloud_sql_proxy.sh

# Crear log con timestamp
LOG_FILE="logs/vm_cron_scraper_$(date +%Y%m%d_%H%M%S).log"

# Ejecutar scraping
echo "=== INICIANDO SCRAPING AUTOMÁTICO EN VM $(date) ===" >> "$LOG_FILE"
python3 run_scraping_now.py >> "$LOG_FILE" 2>&1
echo "=== FINALIZADO SCRAPING AUTOMÁTICO EN VM $(date) ===" >> "$LOG_FILE"

# Desactivar entorno virtual
deactivate
"""
        
        cron_file = Path("vm_cron_scraper.sh")
        with open(cron_file, 'w') as f:
            f.write(cron_script)
        
        # Hacer ejecutable
        cron_file.chmod(0o755)
        
        logger.info(f"✅ Script de cron actualizado: {cron_file}")
        return True
    
    def create_migration_instructions(self):
        """Crear instrucciones de migración"""
        instructions = f"""
# 📋 Instrucciones de Migración a PostgreSQL

## ✅ Configuración Completada

Tu aplicación ha sido configurada para usar PostgreSQL en Google Cloud SQL.

### 🔧 Configuración Actual:
- **Host**: {self.postgresql_config['postgresql']['host']}
- **Puerto**: {self.postgresql_config['postgresql']['port']}
- **Base de datos**: {self.postgresql_config['postgresql']['database']}
- **Usuario**: {self.postgresql_config['postgresql']['user']}
- **Connection Name**: {self.postgresql_config['connection_name']}

### 🚀 Próximos Pasos:

1. **Instalar dependencias en la VM:**
   ```bash
   cd ~/ia-scrapping-tesis
   source venv/bin/activate
   pip install psycopg2-binary
   ```

2. **Subir archivos actualizados a la VM:**
   ```bash
   gcloud compute scp --recurse . scjn-scraper:~/ia-scrapping-tesis/ --zone=us-central1-a
   ```

3. **Ejecutar migración de datos:**
   ```bash
   # En la VM
   cd ~/ia-scrapping-tesis
   source venv/bin/activate
   python3 migrate_to_postgresql.py
   ```

4. **Probar conexión:**
   ```bash
   # En la VM
   ./start_cloud_sql_proxy.sh
   python3 -c "
   from src.database.models import get_session
   session = get_session()
   print('✅ Conexión exitosa a PostgreSQL')
   session.close()
   "
   ```

5. **Actualizar cron job en la VM:**
   ```bash
   # En la VM
   crontab -e
   # Cambiar la línea existente por:
   0 5 * * * /home/leopoldobassoconova/ia-scrapping-tesis/vm_cron_scraper.sh
   ```

### 🔍 Verificación:
- Los logs se guardarán en `logs/vm_cron_scraper_*.log`
- Puedes verificar la conexión con: `python3 -c "from src.database.models import get_session; session = get_session(); print('OK'); session.close()"`

### 📞 Monitoreo:
- Cloud SQL tiene backup automático configurado a las 2:00 AM
- Los logs de la aplicación se guardan en la VM
- Puedes monitorear desde Google Cloud Console

¡Tu sistema ahora está completamente en la nube! 🎉
"""
        
        instructions_file = Path("MIGRATION_INSTRUCTIONS.md")
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        logger.info(f"✅ Instrucciones de migración creadas: {instructions_file}")
        return True
    
    def run_update(self):
        """Ejecutar actualización completa"""
        logger.info("🔄 Iniciando actualización de configuración")
        
        try:
            # Cargar configuración PostgreSQL
            if not self.load_postgresql_config():
                return False
            
            # Actualizar modelos
            self.update_database_models()
            
            # Actualizar requirements
            self.update_requirements()
            
            # Crear script de Cloud SQL Proxy
            self.create_cloud_sql_proxy_script()
            
            # Actualizar script de cron
            self.update_vm_cron_script()
            
            # Crear instrucciones
            self.create_migration_instructions()
            
            logger.info("🎉 Actualización de configuración completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en actualización: {e}")
            return False

def main():
    """Función principal"""
    
    updater = AppConfigUpdater()
    success = updater.run_update()
    
    if success:
        print("🎉 Configuración actualizada exitosamente")
        print("📝 Revisa MIGRATION_INSTRUCTIONS.md para los próximos pasos")
    else:
        print("❌ Error en la actualización. Revisa los logs para más detalles")
    
    return success

if __name__ == "__main__":
    main() 