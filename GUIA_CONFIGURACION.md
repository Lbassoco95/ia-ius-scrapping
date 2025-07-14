# Guía de Configuración - Sistema de Scraping SCJN

Esta guía te ayudará a configurar completamente el sistema de scraping y análisis de tesis de la SCJN.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración de APIs](#configuración-de-apis)
4. [Configuración de Google Drive](#configuración-de-google-drive)
5. [Configuración de OpenAI](#configuración-de-openai)
6. [Primera Ejecución](#primera-ejecución)
7. [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos Previos

### Software Requerido
- **Python 3.8 o superior**
- **Git** (para clonar el repositorio)
- **Navegador web** (para configurar APIs)

### Cuentas Requeridas
- **Google Cloud Platform** (gratuita)
- **OpenAI** (requiere créditos)

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd ia-scrapping-tesis
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Ejecutar Instalador
```bash
python setup.py
```

El instalador automático:
- ✅ Instala todas las dependencias
- ✅ Crea la estructura de directorios
- ✅ Configura el archivo `.env`
- ✅ Proporciona guías para configurar APIs

## 🔑 Configuración de APIs

### Google Drive API

#### Paso 1: Crear Proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la facturación (requerido para APIs)

#### Paso 2: Habilitar Google Drive API
1. Ve a "APIs & Services" > "Library"
2. Busca "Google Drive API"
3. Haz clic en "Enable"

#### Paso 3: Crear Credenciales
1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "Service Account"
3. Completa la información:
   - **Name**: `scjn-scraper`
   - **Description**: `Service account for SCJN scraping`
4. Haz clic en "Create and Continue"
5. En "Grant this service account access to project":
   - Selecciona "Editor"
6. Haz clic en "Done"

#### Paso 4: Descargar Credenciales
1. En la lista de service accounts, haz clic en el que creaste
2. Ve a la pestaña "Keys"
3. Haz clic en "Add Key" > "Create new key"
4. Selecciona "JSON"
5. Descarga el archivo
6. **Renombra** el archivo a `google_drive_credentials.json`
7. **Mueve** el archivo a la carpeta `credentials/`

#### Paso 5: Configurar Google Drive
1. Ve a [Google Drive](https://drive.google.com/)
2. Crea una nueva carpeta llamada "SCJN Tesis"
3. Haz clic derecho en la carpeta > "Share"
4. Agrega el email del service account (está en el archivo JSON)
5. Dale permisos de "Editor"
6. Copia el ID de la carpeta de la URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_AQUI
   ```

#### Paso 6: Actualizar Configuración
Edita el archivo `.env`:
```env
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_aqui
```

### OpenAI API

#### Paso 1: Crear Cuenta
1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Verifica tu email

#### Paso 2: Agregar Método de Pago
1. Ve a "Billing"
2. Agrega un método de pago
3. **Importante**: OpenAI requiere un método de pago válido

#### Paso 3: Crear API Key
1. Ve a "API Keys"
2. Haz clic en "Create new secret key"
3. Dale un nombre descriptivo: `scjn-analyzer`
4. Copia la key (no la podrás ver de nuevo)

#### Paso 4: Actualizar Configuración
Edita el archivo `.env`:
```env
OPENAI_API_KEY=tu_api_key_aqui
```

## 🧪 Primera Ejecución

### 1. Verificar Configuración
```bash
python -c "from src.config import Config; Config.validate(); print('✅ Configuración válida')"
```

### 2. Ejecutar Scraping de Prueba
```bash
python src/scraper/main.py full 10
```
Esto descargará 10 tesis como prueba.

### 3. Verificar Base de Datos
```bash
python -c "from src.database.models import get_session, Tesis; session = get_session(); print(f'Tesis en BD: {session.query(Tesis).count()}')"
```

### 4. Probar Chat
```bash
python src/chat/chat_interface.py
```

### 5. Iniciar API
```bash
python src/api/main.py
```
Luego ve a: http://localhost:8000/docs

## 🔍 Solución de Problemas

### Error: "No module named 'requests'"
```bash
pip install -r requirements.txt
```

### Error: "Invalid API key"
- Verifica que tu API key de OpenAI sea correcta
- Asegúrate de que tengas créditos en tu cuenta

### Error: "Google Drive authentication failed"
- Verifica que el archivo `credentials/google_drive_credentials.json` existe
- Asegúrate de que el service account tenga permisos en la carpeta

### Error: "Database connection failed"
```bash
# Recrear base de datos
rm data/tesis_scjn.db
python -c "from src.database.models import create_database; create_database()"
```

### Error: "Permission denied" al descargar PDFs
```bash
# Verificar permisos de directorio
chmod 755 data/pdfs
```

### El scraping es muy lento
Ajusta en `.env`:
```env
SCRAPING_INTERVAL=1800  # 30 minutos
MAX_DOCUMENTS_PER_RUN=50
```

### Error de memoria
Reduce el número de documentos por ejecución:
```env
MAX_DOCUMENTS_PER_RUN=25
```

## 📊 Monitoreo y Mantenimiento

### Verificar Estado del Sistema
```bash
# Estadísticas de la base de datos
python -c "
from src.database.models import get_session, Tesis, Consulta
session = get_session()
print(f'Tesis totales: {session.query(Tesis).count()}')
print(f'Tesis analizadas: {session.query(Tesis).filter_by(analizado=True).count()}')
print(f'Consultas realizadas: {session.query(Consulta).count()}')
"
```

### Limpiar Archivos Temporales
```bash
# Limpiar PDFs descargados (opcional)
rm -rf data/pdfs/*
```

### Backup de Base de Datos
```bash
cp data/tesis_scjn.db data/backup_$(date +%Y%m%d).db
```

## 🔄 Automatización

### Scraping Automático (Cron Job)
```bash
# Agregar al crontab (ejecutar cada hora)
0 * * * * cd /path/to/ia-scrapping-tesis && python src/scraper/main.py incremental
```

### Monitoreo de Logs
```bash
# Ver logs en tiempo real
tail -f logs/scraper.log
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs**: `logs/scraper.log`
2. **Verifica la configuración**: archivo `.env`
3. **Prueba componentes individuales**:
   - Scraping: `python src/scraper/main.py full 1`
   - Chat: `python src/chat/chat_interface.py`
   - API: `python src/api/main.py`

## 🎯 Próximos Pasos

Una vez que el sistema esté funcionando:

1. **Configurar scraping automático** con cron jobs
2. **Personalizar análisis** modificando prompts en `src/analysis/ai_analyzer.py`
3. **Agregar filtros específicos** en `src/scraper/scjn_config.py`
4. **Desarrollar interfaz web** usando la API REST
5. **Implementar notificaciones** para nuevas tesis

---

¿Necesitas ayuda adicional? Revisa el README.md principal o crea un issue en el repositorio. 