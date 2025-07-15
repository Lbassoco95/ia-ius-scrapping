#!/bin/bash

# Script para configurar cron job del scraper completo
echo "🔄 CONFIGURANDO CRON JOB PARA SCRAPER COMPLETO"
echo "=============================================="

# Obtener la ruta absoluta del directorio actual
CURRENT_DIR=$(pwd)
echo "📁 Directorio actual: $CURRENT_DIR"

# Crear el comando completo con activación del entorno virtual
CRON_COMMAND="cd $CURRENT_DIR && source venv/bin/activate && python3 run_complete_scraper.py >> logs/cron_scraper.log 2>&1"

# Crear el archivo de cron temporal
TEMP_CRON=$(mktemp)

# Agregar la línea de cron (ejecutar cada día a las 2:00 AM)
echo "0 2 * * * $CRON_COMMAND" > $TEMP_CRON

# Mostrar el contenido que se agregará
echo "📋 Contenido del cron job:"
cat $TEMP_CRON

# Preguntar confirmación
echo ""
read -p "¿Deseas agregar este cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Agregar al crontab del usuario actual
    crontab -l 2>/dev/null | cat - $TEMP_CRON | crontab -
    
    echo "✅ Cron job agregado exitosamente"
    echo ""
    echo "📊 Cron jobs actuales:"
    crontab -l
    
    # Crear directorio de logs si no existe
    mkdir -p logs
    echo "📁 Directorio de logs creado: logs/"
    
    echo ""
    echo "🎯 El scraper se ejecutará automáticamente cada día a las 2:00 AM"
    echo "📝 Los logs se guardarán en: logs/cron_scraper.log"
    
else
    echo "❌ Cron job no agregado"
fi

# Limpiar archivo temporal
rm $TEMP_CRON

echo ""
echo "🔧 OPCIONES ADICIONALES:"
echo "1. Para ejecutar manualmente: python3 run_complete_scraper.py"
echo "2. Para ver logs: tail -f logs/cron_scraper.log"
echo "3. Para listar cron jobs: crontab -l"
echo "4. Para editar cron jobs: crontab -e"
echo "5. Para remover cron jobs: crontab -r"
