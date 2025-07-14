#!/usr/bin/env python3
"""
🎯 Configuración Inicial con Prueba de 3 Horas - SCJN Scraper

Este script configura el sistema para:
1. Hacer una prueba inicial de 3 horas cuando se conecte por primera vez
2. Verificar que todo funciona correctamente
3. Configurar el horario diario basado en la hora de inicio de la prueba
"""

import os
import json
import datetime
from pathlib import Path

def setup_initial_test():
    """Configura el sistema para prueba inicial de 3 horas"""
    
    print("🎯 CONFIGURACIÓN INICIAL CON PRUEBA DE 3 HORAS")
    print("=" * 50)
    
    # Crear directorio de configuración si no existe
    config_dir = Path("data/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Obtener hora actual
    now = datetime.datetime.now()
    start_time = now.strftime("%H:%M")
    
    # Calcular hora de fin (3 horas después)
    end_time = (now + datetime.timedelta(hours=3)).strftime("%H:%M")
    
    # Configuración para prueba inicial
    initial_config = {
        "test_mode": True,
        "test_start_time": start_time,
        "test_end_time": end_time,
        "test_date": now.strftime("%Y-%m-%d"),
        "daily_start_time": start_time,  # Usar la hora de inicio como horario diario
        "daily_end_time": end_time,      # Usar la hora de fin como horario diario
        "max_files_per_day": 50,
        "max_files_per_test": 50,
        "phase": "INITIAL_TEST",
        "created_at": now.isoformat()
    }
    
    # Guardar configuración
    config_file = config_dir / "initial_test_config.json"
    with open(config_file, 'w') as f:
        json.dump(initial_config, f, indent=2)
    
    print(f"✅ Configuración de prueba inicial creada:")
    print(f"   📅 Fecha: {now.strftime('%Y-%m-%d')}")
    print(f"   🕐 Hora de inicio: {start_time}")
    print(f"   🕐 Hora de fin: {end_time}")
    print(f"   📁 Archivo: {config_file}")
    
    # Crear script de activación de prueba
    create_test_activation_script(start_time, end_time)
    
    # Crear script de verificación
    create_verification_script()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Conectar a la VM cuando esté lista")
    print("2. Ejecutar: python setup_initial_test.py")
    print("3. Ejecutar: ./activate_initial_test.sh")
    print("4. Monitorear durante 3 horas")
    print("5. Verificar resultados")
    print("6. Si todo está bien, activar modo automático")
    
    return initial_config

def create_test_activation_script(start_time, end_time):
    """Crea script para activar la prueba inicial"""
    
    script_content = f'''#!/bin/bash
# 🚀 Script de Activación de Prueba Inicial - SCJN Scraper

echo "🎯 ACTIVANDO PRUEBA INICIAL DE 3 HORAS"
echo "======================================"
echo "🕐 Hora de inicio: {start_time}"
echo "🕐 Hora de fin: {end_time}"
echo ""

# Verificar que el sistema esté listo
echo "✅ Verificando sistema..."
if ! systemctl is-active --quiet scjn-scraper; then
    echo "❌ El servicio scjn-scraper no está activo"
    echo "Iniciando servicio..."
    sudo systemctl start scjn-scraper
    sleep 5
fi

# Verificar base de datos
echo "✅ Verificando base de datos..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='scjn_database',
        user='scjn_user',
        password='[PASSWORD]'
    )
    print('✅ Base de datos conectada correctamente')
    conn.close()
except Exception as e:
    print(f'❌ Error en base de datos: {{e}}')
    exit(1)
"

# Verificar scraper
echo "✅ Verificando scraper..."
python3 -c "
from src.scraper.selenium_scraper import SeleniumScraper
try:
    scraper = SeleniumScraper()
    print('✅ Scraper inicializado correctamente')
except Exception as e:
    print(f'❌ Error en scraper: {{e}}')
    exit(1)
"

# Activar modo de prueba
echo "🎯 Activando modo de prueba..."
python3 -c "
import json
from datetime import datetime

config = {{
    'test_mode': True,
    'test_start_time': '{start_time}',
    'test_end_time': '{end_time}',
    'max_files_per_test': 50,
    'phase': 'INITIAL_TEST'
}}

with open('data/config/test_active.json', 'w') as f:
    json.dump(config, f, indent=2)

print('✅ Modo de prueba activado')
"

# Iniciar scraping de prueba
echo "🚀 Iniciando scraping de prueba..."
python3 start_auto_scraper.py test

echo ""
echo "🎉 ¡Prueba inicial iniciada!"
echo "📊 Monitorea los logs con: sudo journalctl -u scjn-scraper -f"
echo "📈 Verifica progreso con: tail -f logs/auto_scraper.log"
echo "⏰ La prueba terminará automáticamente a las {end_time}"
'''
    
    with open("activate_initial_test.sh", 'w') as f:
        f.write(script_content)
    
    os.chmod("activate_initial_test.sh", 0o755)
    print(f"✅ Script de activación creado: activate_initial_test.sh")

def create_verification_script():
    """Crea script para verificar resultados de la prueba"""
    
    script_content = '''#!/bin/bash
# 📊 Script de Verificación de Prueba Inicial - SCJN Scraper

echo "📊 VERIFICACIÓN DE RESULTADOS DE PRUEBA"
echo "======================================="

# Verificar archivos descargados
echo "📁 Archivos descargados:"
ls -la data/pdfs/ | wc -l
echo ""

# Verificar base de datos
echo "🗄️ Registros en base de datos:"
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='scjn_database',
        user='scjn_user',
        password='[PASSWORD]'
    )
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM tesis')
    count = cur.fetchone()[0]
    print(f'✅ Tesis en base de datos: {count}')
    
    cur.execute('SELECT COUNT(*) FROM tesis WHERE created_at >= NOW() - INTERVAL \\'3 hours\\'')
    recent = cur.fetchone()[0]
    print(f'✅ Tesis de las últimas 3 horas: {recent}')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
"

# Verificar logs
echo ""
echo "📋 Últimos logs del sistema:"
tail -20 logs/auto_scraper.log

# Verificar estado del servicio
echo ""
echo "🔧 Estado del servicio:"
sudo systemctl status scjn-scraper --no-pager

# Preguntar si activar modo automático
echo ""
echo "🎯 ¿Quieres activar el modo automático diario?"
echo "1. Sí, activar modo automático"
echo "2. No, mantener en modo manual"
read -p "Tu elección (1-2): " choice

if [ "$choice" = "1" ]; then
    echo "🚀 Activando modo automático..."
    python3 -c "
import json
from datetime import datetime

# Leer configuración de prueba
with open('data/config/initial_test_config.json', 'r') as f:
    config = json.load(f)

# Configurar modo automático
auto_config = {
    'test_mode': False,
    'daily_start_time': config['daily_start_time'],
    'daily_end_time': config['daily_end_time'],
    'max_files_per_day': 50,
    'phase': 'INITIAL',
    'activated_at': datetime.now().isoformat()
}

with open('data/config/auto_mode.json', 'w') as f:
    json.dump(auto_config, f, indent=2)

print('✅ Modo automático activado')
print(f'🕐 Horario diario: {config[\"daily_start_time\"]} - {config[\"daily_end_time\"]}')
"

    echo "✅ Modo automático activado"
    echo "🕐 El sistema funcionará diariamente de $(python3 -c "import json; config=json.load(open('data/config/auto_mode.json')); print(f'{config[\"daily_start_time\"]} a {config[\"daily_end_time\"]}')")"
else
    echo "ℹ️ Sistema mantenido en modo manual"
fi
'''
    
    with open("verify_test_results.sh", 'w') as f:
        f.write(script_content)
    
    os.chmod("verify_test_results.sh", 0o755)
    print(f"✅ Script de verificación creado: verify_test_results.sh")

if __name__ == "__main__":
    setup_initial_test() 