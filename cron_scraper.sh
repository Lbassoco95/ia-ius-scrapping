#!/bin/bash

# Script para ejecutar el scraping desde cron
# Configurar variables de entorno
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Directorio del proyecto
PROJECT_DIR="/Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis"

# Activar entorno virtual
source "$PROJECT_DIR/venv/bin/activate"

# Configurar variables de entorno para Google Drive
export GOOGLE_DRIVE_ENABLED="true"
export GOOGLE_DRIVE_FOLDER_ID="0AAL0nxoqH30XUk9PVA"
export GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH="$PROJECT_DIR/service_account.json"

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Crear log con timestamp
LOG_FILE="logs/cron_scraper_$(date +%Y%m%d_%H%M%S).log"

# Ejecutar scraping
echo "=== INICIANDO SCRAPING AUTOMÁTICO $(date) ===" >> "$LOG_FILE"
python3 run_scraping_now.py >> "$LOG_FILE" 2>&1
echo "=== FINALIZADO SCRAPING AUTOMÁTICO $(date) ===" >> "$LOG_FILE"

# Desactivar entorno virtual
deactivate 