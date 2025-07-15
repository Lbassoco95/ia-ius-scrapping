# 🚀 GUÍA DE PRODUCCIÓN - SCJN SCRAPER

Guía completa para configurar y ejecutar el sistema de scraping SCJN en producción en la máquina virtual Ubuntu.

## 📋 Estado Actual

El sistema está configurado para:
- ✅ **Descargar PDFs** automáticamente de las tesis encontradas
- ✅ **Subir PDFs a Google Drive** con organización automática
- ✅ **Guardar enlaces** en la base de datos
- ✅ **Ejecutarse automáticamente** todos los días a las 8:00 AM
- ✅ **Monitoreo completo** con logs detallados

## 🛠️ Configuración en la VM

### 1. Verificar Preparación del Sistema

```bash
# En la VM, desde el directorio del proyecto
python verify_production_ready.py
```

Este comando verificará:
- ✅ Directorios y archivos necesarios
- ✅ Dependencias de Python
- ✅ Configuración de entorno
- ✅ Base de datos
- ✅ Credenciales de Google Drive
- ✅ Selenium/Chrome

### 2. Configurar Cron Job de Producción

```bash
# Configurar ejecución automática
./setup_production_cron.sh
```

Esto configurará:
- 📅 Ejecución diaria a las 8:00 AM
- 📝 Logs automáticos en `logs/cron_production.log`
- 🔄 Reinicio automático en caso de errores

### 3. Verificar Configuración

```bash
# Ver cron jobs configurados
crontab -l

# Ver logs en tiempo real
tail -f logs/cron_production.log
```

## 🔧 Comandos de Producción

### Ejecutar Manualmente

```bash
# Ejecutar scraper de producción manualmente
python production_scraper.py

# O usar el wrapper script
./run_production_scraper.sh
```

### Monitorear Sistema

```bash
# Ver logs de producción
tail -f logs/production_scraper_*.log

# Ver estado de la base de datos
python -c "from src.database.models import get_session, Tesis; session = get_session(); print(f'Total tesis: {session.query(Tesis).count()}'); print(f'Con PDF en Drive: {session.query(Tesis).filter(Tesis.google_drive_id.isnot(None)).count()}')"

# Ver archivos PDF descargados
ls -la data/pdfs/
```

### Gestionar Cron Jobs

```bash
# Ver cron jobs activos
crontab -l

# Editar cron jobs
crontab -e

# Eliminar todos los cron jobs
crontab -r
```

## 📊 Monitoreo y Logs

### Archivos de Log

- `logs/production_scraper_YYYYMMDD.log` - Logs del scraper de producción
- `logs/cron_production.log` - Logs del cron job
- `logs/auto_scraper.log` - Logs generales del sistema

### Información de Logs

Los logs incluyen:
- 📄 Número de tesis procesadas
- 📁 PDFs descargados y subidos a Drive
- ⏱️ Tiempo de ejecución
- ❌ Errores y advertencias
- 📊 Estadísticas de rendimiento

## 🔐 Configuración de Google Drive

### Verificar Credenciales

```bash
# Verificar que existan las credenciales
ls -la credentials/

# Archivos necesarios:
# - credentials/google_drive_credentials.json
# - credentials/service_account.json (opcional)
# - credentials/token.json (se genera automáticamente)
```

### Configurar Variables de Entorno

Editar `.env`:
```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_aqui
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive_credentials.json
```

## 📈 Métricas de Producción

### Estadísticas Diarias

El sistema registra automáticamente:
- 📊 Total de tesis en base de datos
- 📁 PDFs subidos a Google Drive
- ⏱️ Tiempo de ejecución
- 🔄 Nuevas tesis agregadas
- ❌ Errores encontrados

### Consultar Estadísticas

```bash
# Ver estadísticas de la base de datos
python -c "
from src.database.models import get_session, Tesis
from datetime import datetime, timedelta

session = get_session()
total = session.query(Tesis).count()
con_pdf = session.query(Tesis).filter(Tesis.google_drive_id.isnot(None)).count()
hoy = session.query(Tesis).filter(Tesis.fecha_descarga >= datetime.now().date()).count()

print(f'📊 ESTADÍSTICAS:')
print(f'   Total tesis: {total}')
print(f'   Con PDF en Drive: {con_pdf}')
print(f'   Agregadas hoy: {hoy}')
"
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de Chrome/Selenium**
   ```bash
   # Reinstalar ChromeDriver
   pip install --upgrade webdriver-manager
   ```

2. **Error de Google Drive**
   ```bash
   # Verificar credenciales
   python -c "from src.storage.google_drive import GoogleDriveManager; gdm = GoogleDriveManager(); gdm.authenticate()"
   ```

3. **Error de base de datos**
   ```bash
   # Recrear tablas
   python -c "from src.database.models import create_tables; create_tables()"
   ```

4. **Cron job no ejecuta**
   ```bash
   # Verificar permisos
   chmod +x run_production_scraper.sh
   
   # Verificar logs del sistema
   sudo tail -f /var/log/syslog | grep CRON
   ```

### Reiniciar Sistema

```bash
# Detener cron jobs
crontab -r

# Limpiar logs
rm -f logs/*.log

# Reconfigurar
./setup_production_cron.sh
```

## 📞 Soporte

### Logs de Debug

```bash
# Ver logs detallados
tail -f logs/production_scraper_$(date +%Y%m%d).log

# Buscar errores específicos
grep -i error logs/production_scraper_*.log
```

### Información del Sistema

```bash
# Verificar espacio en disco
df -h

# Verificar memoria
free -h

# Verificar procesos
ps aux | grep python
```

## 🎯 Próximos Pasos

1. **Ejecutar verificación**: `python verify_production_ready.py`
2. **Configurar cron**: `./setup_production_cron.sh`
3. **Probar manualmente**: `python production_scraper.py`
4. **Monitorear logs**: `tail -f logs/cron_production.log`

¡El sistema estará listo para producción automática! 🚀 