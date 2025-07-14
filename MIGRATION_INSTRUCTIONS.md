
# 📋 Instrucciones de Migración a PostgreSQL

## ✅ Configuración Completada

Tu aplicación ha sido configurada para usar PostgreSQL en Google Cloud SQL.

### 🔧 Configuración Actual:
- **Host**: 35.184.183.187
- **Puerto**: 5432
- **Base de datos**: scjn_database
- **Usuario**: scjn_user
- **Connection Name**: scjn-scraper-20250713:us-central1:scjn-scraper-db

### 🚀 Próximos Pasos:

1. **Instalar dependencias en la VM:**
   ```bash
   cd ~/ia-scrapping-tesis
   source venv/bin/activate
   pip install psycopg2-binary
   ```

2. **Subir archivos actualizados a la VM:**
   ```bash
   gcloud compute scp --recurse . scjn-scraper:~/ia-scrapping-tesis/ --zone=us-central1-a
   ```

3. **Ejecutar migración de datos:**
   ```bash
   # En la VM
   cd ~/ia-scrapping-tesis
   source venv/bin/activate
   python3 migrate_to_postgresql.py
   ```

4. **Probar conexión:**
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

5. **Actualizar cron job en la VM:**
   ```bash
   # En la VM
   crontab -e
   # Cambiar la línea existente por:
   0 5 * * * /home/leopoldobassoconova/ia-scrapping-tesis/vm_cron_scraper.sh
   ```

### 🔍 Verificación:
- Los logs se guardarán en `logs/vm_cron_scraper_*.log`
- Puedes verificar la conexión con: `python3 -c "from src.database.models import get_session; session = get_session(); print('OK'); session.close()"`

### 📞 Monitoreo:
- Cloud SQL tiene backup automático configurado a las 2:00 AM
- Los logs de la aplicación se guardan en la VM
- Puedes monitorear desde Google Cloud Console

¡Tu sistema ahora está completamente en la nube! 🎉
