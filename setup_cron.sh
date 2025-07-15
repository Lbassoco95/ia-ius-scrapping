#!/bin/bash
echo "⏰ CONFIGURANDO CRON JOB PARA SCRAPER SCJN"
echo "=========================================="

# Obtener directorio actual
CURRENT_DIR=$(pwd)
echo "📂 Directorio: $CURRENT_DIR"

# Crear script de ejecución
cat > run_scraper_cron.sh << EOF
#!/bin/bash
cd $CURRENT_DIR
source venv/bin/activate
python3 run_scraper.py >> logs/cron_scraper.log 2>&1
EOF

chmod +x run_scraper_cron.sh
echo "✅ Script de ejecución creado"

# Crear directorio de logs si no existe
mkdir -p logs
echo "✅ Directorio de logs creado"

# Mostrar instrucciones para cron
echo ""
echo "🔧 PARA CONFIGURAR CRON JOB:"
echo "1. Ejecuta: crontab -e"
echo "2. Agrega una de estas líneas:"
echo ""
echo "   # Ejecutar cada 6 horas"
echo "   0 */6 * * * $CURRENT_DIR/run_scraper_cron.sh"
echo ""
echo "   # Ejecutar diario a las 2 AM"
echo "   0 2 * * * $CURRENT_DIR/run_scraper_cron.sh"
echo ""
echo "   # Ejecutar cada 12 horas"
echo "   0 */12 * * * $CURRENT_DIR/run_scraper_cron.sh"
echo ""
echo "3. Guarda y sale (Ctrl+X, Y, Enter)"
echo ""
echo "📊 Para ver logs: tail -f logs/cron_scraper.log"
