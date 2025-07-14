#!/bin/bash
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
