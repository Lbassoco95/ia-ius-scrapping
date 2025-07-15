#!/bin/bash

# Script para configurar cron job de producción en la VM
# Este script configura la ejecución automática del scraper de producción

echo "🚀 CONFIGURANDO CRON JOB DE PRODUCCIÓN"
echo "======================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "production_scraper.py" ]; then
    echo "❌ Error: No se encuentra production_scraper.py"
    echo "   Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Error: No se encuentra el entorno virtual (venv/)"
    echo "   Ejecuta: python3 -m venv venv"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs
mkdir -p data/pdfs

# Obtener la ruta absoluta del proyecto
PROJECT_DIR=$(pwd)
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
PRODUCTION_SCRIPT="$PROJECT_DIR/production_scraper.py"
LOG_FILE="$PROJECT_DIR/logs/cron_production.log"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo "🐍 Python del entorno virtual: $VENV_PYTHON"
echo "📄 Script de producción: $PRODUCTION_SCRIPT"
echo "📝 Archivo de log: $LOG_FILE"

# Crear script wrapper para el cron job
cat > run_production_scraper.sh << EOF
#!/bin/bash
# Wrapper script para ejecutar el scraper de producción desde cron

# Cambiar al directorio del proyecto
cd $PROJECT_DIR

# Activar entorno virtual y ejecutar scraper
source venv/bin/activate
python production_scraper.py >> $LOG_FILE 2>&1

# Verificar el resultado
if [ \$? -eq 0 ]; then
    echo "\$(date): ✅ Scraper de producción completado exitosamente" >> $LOG_FILE
else
    echo "\$(date): ❌ Error en scraper de producción" >> $LOG_FILE
fi
EOF

# Hacer ejecutable el script wrapper
chmod +x run_production_scraper.sh

echo "✅ Script wrapper creado: run_production_scraper.sh"

# Crear entrada de cron job
# Ejecutar todos los días a las 8:00 AM
CRON_JOB="0 8 * * * $PROJECT_DIR/run_production_scraper.sh"

echo ""
echo "📅 Configurando cron job..."
echo "   Horario: Todos los días a las 8:00 AM"
echo "   Comando: $CRON_JOB"

# Agregar al crontab del usuario actual
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✅ Cron job configurado exitosamente"
echo ""
echo "📋 RESUMEN DE CONFIGURACIÓN:"
echo "   - Script de producción: production_scraper.py"
echo "   - Wrapper script: run_production_scraper.sh"
echo "   - Logs: $LOG_FILE"
echo "   - Horario: Todos los días a las 8:00 AM"
echo "   - Entorno virtual: $VENV_PYTHON"
echo ""
echo "🔧 COMANDOS ÚTILES:"
echo "   - Ver cron jobs: crontab -l"
echo "   - Editar cron jobs: crontab -e"
echo "   - Ver logs: tail -f $LOG_FILE"
echo "   - Ejecutar manualmente: ./run_production_scraper.sh"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Asegúrate de que las credenciales de Google Drive estén configuradas"
echo "   - Verifica que el archivo .env tenga las variables necesarias"
echo "   - El sistema descargará PDFs y los subirá automáticamente a Google Drive" 