#!/bin/bash

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
