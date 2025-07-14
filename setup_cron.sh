#!/bin/bash
echo "⏰ Configurando cron job para mañana a las 5:00 AM..."

# Agregar al cron
(crontab -l 2>/dev/null; echo "0 5 * * * cd /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis && /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis/venv/bin/python3 /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis/production_scraper.py") | crontab -

echo "✅ Cron job configurado"
echo "📋 Comando: 0 5 * * * cd /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis && /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis/venv/bin/python3 /Users/leopoldobassoconova/Library/Mobile Documents/com~apple~CloudDocs/REPOSITORIOS/ia-scrapping-tesis/production_scraper.py"
echo "📝 Para ver cron jobs: crontab -l"
echo "📝 Para remover: crontab -r"
