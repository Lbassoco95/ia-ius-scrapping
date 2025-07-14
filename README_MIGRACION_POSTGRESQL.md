# 🗄️ Migración de SQLite a PostgreSQL en Google Cloud

Guía completa para migrar tu sistema de scraping SCJN de SQLite local a PostgreSQL en Google Cloud SQL.

## 📋 Resumen

Este proceso migrará tu sistema completo a la nube:
- ✅ **Base de datos**: SQLite → PostgreSQL (Cloud SQL)
- ✅ **Almacenamiento**: Local → Google Cloud
- ✅ **Ejecución**: Local → VM de Google Cloud (24/7)
- ✅ **Monitoreo**: Logs locales → Cloud Monitoring

## 🚀 Scripts de Migración Creados

### 1. `migrate_to_postgresql.py`
**Propósito**: Migrar datos de SQLite a PostgreSQL
- Conecta a ambas bases de datos
- Crea esquema en PostgreSQL
- Migra todas las tablas (tesis, scraping_sessions, scraping_stats)
- Verifica la integridad de la migración

### 2. `setup_cloud_sql.py`
**Propósito**: Configurar Cloud SQL automáticamente
- Crea instancia PostgreSQL en Cloud SQL
- Configura base de datos y usuario
- Genera password seguro
- Guarda configuración en `config/postgresql_config.json`

### 3. `update_app_config.py`
**Propósito**: Actualizar aplicación para usar PostgreSQL
- Modifica `src/database/models.py` para usar PostgreSQL
- Actualiza `requirements.txt` con psycopg2-binary
- Crea script de Cloud SQL Proxy
- Actualiza script de cron de la VM
- Genera instrucciones de migración

### 4. `migrate_to_cloud_complete.py`
**Propósito**: Script maestro que ejecuta todo el proceso
- Verifica prerequisitos
- Ejecuta todos los scripts en orden
- Sube archivos a la VM
- Configura cron job automático

## 📊 Datos Actuales

Tu base de datos SQLite contiene:
- **60 tesis** con metadatos completos
- **2 sesiones** de scraping
- **0 estadísticas** (tabla vacía)

## 🔧 Proceso de Migración

### Opción 1: Migración Automática (Recomendada)

```bash
# Ejecutar migración completa
python3 migrate_to_cloud_complete.py
```

Este script hará todo automáticamente:
1. ✅ Configurar Cloud SQL
2. ✅ Actualizar configuración de la aplicación
3. ✅ Instalar dependencias
4. ✅ Subir archivos a la VM
5. ✅ Migrar datos a PostgreSQL
6. ✅ Probar conexión
7. ✅ Configurar cron job automático

### Opción 2: Migración Manual (Paso a Paso)

#### Paso 1: Configurar Cloud SQL
```bash
python3 setup_cloud_sql.py
```

#### Paso 2: Actualizar Configuración
```bash
python3 update_app_config.py
```

#### Paso 3: Instalar Dependencias
```bash
pip install psycopg2-binary
```

#### Paso 4: Subir a la VM
```bash
gcloud compute scp --recurse . scjn-scraper:~/ia-scrapping-tesis/ --zone=us-central1-a
```

#### Paso 5: Migrar Datos en la VM
```bash
gcloud compute ssh scjn-scraper --zone=us-central1-a
cd ia-scrapping-tesis
source venv/bin/activate
pip install psycopg2-binary
python3 migrate_to_postgresql.py
```

#### Paso 6: Probar Conexión
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

#### Paso 7: Actualizar Cron Job
```bash
# En la VM
chmod +x vm_cron_scraper.sh
crontab -e
# Agregar: 0 5 * * * /home/leopoldobassoconova/ia-scrapping-tesis/vm_cron_scraper.sh
```

## 🔍 Verificación

### Verificar Migración
```bash
# En la VM
python3 -c "
from src.database.models import Tesis, get_session
session = get_session()
count = session.query(Tesis).count()
print(f'✅ {count} tesis en PostgreSQL')
session.close()
"
```

### Verificar Cron Job
```bash
# En la VM
crontab -l
# Debe mostrar: 0 5 * * * /home/leopoldobassoconova/ia-scrapping-tesis/vm_cron_scraper.sh
```

### Verificar Logs
```bash
# En la VM
ls -la logs/vm_cron_scraper_*.log
tail -f logs/vm_cron_scraper_$(date +%Y%m%d)_*.log
```

## 📈 Ventajas de PostgreSQL en Cloud SQL

### 🚀 Rendimiento
- **Índices optimizados**: Búsquedas más rápidas
- **JSONB nativo**: Mejor manejo de metadatos
- **Concurrencia**: Múltiples conexiones simultáneas

### 🔒 Seguridad
- **SSL/TLS**: Conexiones encriptadas
- **IAM**: Control de acceso granular
- **Backup automático**: Diario a las 2:00 AM
- **VPC**: Red privada virtual

### 📊 Escalabilidad
- **Auto-scaling**: Se adapta a la carga
- **Alta disponibilidad**: 99.9% uptime
- **Monitoreo**: Cloud Monitoring integrado

### 💰 Costo
- **db-f1-micro**: ~$10/mes
- **Backup incluido**: Sin costo adicional
- **Monitoreo incluido**: Sin costo adicional

## 🔧 Configuración Técnica

### Cadena de Conexión PostgreSQL
```
postgresql://scjn_user:password@host:5432/scjn_database
```

### Variables de Entorno
```bash
export GOOGLE_DRIVE_ENABLED="true"
export GOOGLE_DRIVE_FOLDER_ID="0AAL0nxoqH30XUk9PVA"
export GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH="service_account.json"
```

### Cloud SQL Proxy
El script `start_cloud_sql_proxy.sh` maneja la conexión segura a Cloud SQL.

## 🚨 Solución de Problemas

### Error de Conexión
```bash
# Verificar Cloud SQL Proxy
ps aux | grep cloud_sql_proxy

# Reiniciar proxy
pkill cloud_sql_proxy
./start_cloud_sql_proxy.sh
```

### Error de Migración
```bash
# Verificar logs
tail -f logs/migration.log

# Reintentar migración
python3 migrate_to_postgresql.py
```

### Error de Cron
```bash
# Verificar cron job
crontab -l

# Probar script manualmente
./vm_cron_scraper.sh
```

## 📞 Monitoreo y Mantenimiento

### Cloud Console
- **Cloud SQL**: https://console.cloud.google.com/sql
- **Compute Engine**: https://console.cloud.google.com/compute
- **Cloud Monitoring**: https://console.cloud.google.com/monitoring

### Comandos Útiles
```bash
# Ver estado de la VM
gcloud compute instances describe scjn-scraper --zone=us-central1-a

# Conectar a la VM
gcloud compute ssh scjn-scraper --zone=us-central1-a

# Ver logs de Cloud SQL
gcloud sql logs tail scjn-scraper-db

# Backup manual
gcloud sql export sql scjn-scraper-db gs://bucket/backup.sql --database=scjn_database
```

## 🎉 Resultado Final

Después de la migración tendrás:
- ✅ **Sistema 24/7**: Funciona sin tu computadora
- ✅ **Base de datos profesional**: PostgreSQL en la nube
- ✅ **Backup automático**: Diario a las 2:00 AM
- ✅ **Monitoreo completo**: Logs y métricas
- ✅ **Escalabilidad**: Se adapta al crecimiento
- ✅ **Seguridad**: Conexiones encriptadas

¡Tu sistema de scraping SCJN estará completamente profesionalizado en Google Cloud! 🚀 