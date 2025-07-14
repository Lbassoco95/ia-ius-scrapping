# 🏛️ IA-IUS-SCRAPPING: Sistema Inteligente de Scraping SCJN

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Lbassoco95-green.svg)](https://github.com/Lbassoco95)

Sistema automatizado de scraping, almacenamiento y análisis inteligente de tesis y jurisprudencia de la **Suprema Corte de Justicia de la Nación (SCJN)** utilizando tecnologías de Inteligencia Artificial.

## 🚀 Características Principales

### 🔍 **Scraping Inteligente**
- **Automatización completa** del proceso de búsqueda y descarga
- **Detección automática** de nuevas tesis publicadas
- **Descarga masiva** de PDFs con gestión de errores
- **Extracción de metadatos** estructurados

### 🧠 **Análisis con IA**
- **Categorización automática** usando OpenAI GPT
- **Resumen inteligente** de contenido jurídico
- **Extracción de conceptos clave** y jurisprudencia
- **Análisis de tendencias** legales

### ☁️ **Almacenamiento en la Nube**
- **Integración con Google Drive** para almacenamiento seguro
- **Organización automática** por categorías y fechas
- **Backup automático** de datos críticos

### 📊 **Base de Datos Avanzada**
- **PostgreSQL** para producción escalable
- **SQLite** para desarrollo local
- **Consultas estructuradas** y búsquedas avanzadas
- **Relaciones entre documentos** y jurisprudencia

### 🤖 **Automatización Completa**
- **Ejecución programada** con cron jobs
- **Monitoreo continuo** del sistema
- **Alertas automáticas** por email
- **Logs detallados** para debugging

## 📋 Estado Actual del Proyecto

### ✅ **Funcionalidades Implementadas**
- [x] Scraping básico de SCJN
- [x] Descarga automática de PDFs
- [x] Integración con Google Drive
- [x] Análisis con OpenAI GPT
- [x] Base de datos SQLite/PostgreSQL
- [x] Sistema de logging
- [x] Configuración automatizada
- [x] Scripts de deployment en la nube

### 🔄 **En Desarrollo**
- [ ] API REST completa
- [ ] Interfaz web de consultas
- [ ] Chat inteligente
- [ ] Dashboard de monitoreo
- [ ] Análisis de tendencias

### 📈 **Próximas Funcionalidades**
- [ ] Machine Learning para clasificación
- [ ] Análisis de sentimientos jurídicos
- [ ] Predicción de tendencias legales
- [ ] Integración con otros sistemas jurídicos

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- Git
- Cuenta de Google Cloud Platform
- API Key de OpenAI (opcional)

### 1. **Clonar el Repositorio**
```bash
git clone https://github.com/Lbassoco95/ia-ius-scrapping.git
cd ia-ius-scrapping
```

### 2. **Configurar Entorno Virtual**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 4. **Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. **Configurar Google Drive API**
```bash
# Ejecutar el script de configuración
python setup_google_drive.py
```

## ⚙️ Configuración Detallada

### Variables de Entorno (.env)
```env
# OpenAI (Opcional)
OPENAI_ENABLED=true
OPENAI_API_KEY=tu_api_key_de_openai
OPENAI_MODEL=gpt-3.5-turbo

# Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive_credentials.json

# Base de Datos
DATABASE_URL=sqlite:///data/scjn_database.db
# Para PostgreSQL: postgresql://user:pass@localhost/scjn_db

# Scraping
SCJN_BASE_URL=https://sjf2.scjn.gob.mx
SEARCH_URL=https://sjf2.scjn.gob.mx/busqueda-principal-tesis
MAX_FILES_PER_SESSION=200
DEFAULT_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
TIMEZONE=America/Mexico_City
```

## 🚀 Uso Rápido

### **Ejecutar Scraping Manual**
```bash
python run_scraping_now.py
```

### **Configurar Scraping Automático**
```bash
python setup_cron.sh
```

### **Monitorear Sistema**
```bash
python monitor_production.py
```

### **Migrar a PostgreSQL**
```bash
python migrate_to_postgresql.py
```

## 📁 Estructura del Proyecto

```
ia-ius-scrapping/
├── 📁 src/                    # Código fuente principal
│   ├── 📁 scraper/           # Módulo de scraping SCJN
│   ├── 📁 storage/           # Gestión de Google Drive
│   ├── 📁 analysis/          # Análisis con IA
│   ├── 📁 database/          # Modelos de base de datos
│   ├── 📁 api/              # API REST (en desarrollo)
│   ├── 📁 chat/             # Interfaz de chat (en desarrollo)
│   └── 📁 automation/       # Automatización del sistema
├── 📁 data/                 # Datos descargados y procesados
├── 📁 credentials/          # Credenciales de APIs
├── 📁 logs/                # Logs del sistema
├── 📁 tests/               # Pruebas unitarias
├── 📁 aws_deployment/      # Scripts para AWS
├── 📁 google_cloud_deployment/ # Scripts para Google Cloud
└── 📄 *.py                 # Scripts principales
```

## 🔧 Scripts Principales

| Script | Descripción |
|--------|-------------|
| `run_scraping_now.py` | Ejecuta scraping inmediato |
| `auto_scraper_controller.py` | Controlador principal del sistema |
| `setup_google_drive.py` | Configuración de Google Drive |
| `migrate_to_postgresql.py` | Migración a PostgreSQL |
| `monitor_production.py` | Monitoreo del sistema |
| `production_scraper.py` | Scraper optimizado para producción |

## 📊 Estadísticas del Proyecto

- **Archivos de código**: 97
- **Líneas de código**: ~18,000
- **Dependencias**: 25+ paquetes Python
- **Integraciones**: Google Drive, OpenAI, PostgreSQL
- **Plataformas soportadas**: AWS, Google Cloud, Local

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 

1. **Fork** el proyecto
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### Guías de Contribución
- Sigue las convenciones de código Python (PEP 8)
- Agrega tests para nuevas funcionalidades
- Documenta cambios importantes
- Mantén la compatibilidad con versiones anteriores

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

- **Autor**: Leopoldo Bassoco
- **Email**: leo.bassoco@kawiil.mx
- **GitHub**: [@Lbassoco95](https://github.com/Lbassoco95)

## 🙏 Agradecimientos

- **SCJN** por proporcionar acceso público a su jurisprudencia
- **OpenAI** por las herramientas de IA
- **Google Cloud** por la infraestructura en la nube
- **Comunidad open source** por las librerías utilizadas

---

⭐ **¡Si este proyecto te es útil, considera darle una estrella en GitHub!** 