#!/bin/bash
# Script de inicio para SCJN Scraper - Producción

echo "🚀 Iniciando SCJN Scraper en producción..."

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

# Configurar variables de entorno
cat > .env << EOF
DATABASE_URL=sqlite:///data/scjn_database.db
GOOGLE_DRIVE_ENABLED=true
MAX_FILES_PER_SESSION=5
LOG_LEVEL=INFO
TIMEZONE=America/Mexico_City
EOF

# Configurar cron job para scraping cada 6 horas
echo "0 */6 * * * cd /home/scraper/scjn-scraper && /home/scraper/scjn-scraper/venv/bin/python backup_test_production.py" | crontab -u scraper -

# Cambiar permisos
chown -R scraper:scraper /home/scraper/scjn-scraper

echo "✅ Configuración completada"
echo "🔄 Ejecutando prueba de backup..."

# Ejecutar prueba de backup
cd /home/scraper/scjn-scraper
source venv/bin/activate
python backup_test_production.py

echo "🎉 Sistema SCJN Scraper iniciado en producción"
