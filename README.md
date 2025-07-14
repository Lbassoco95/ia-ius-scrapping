# Sistema de Scraping y Análisis de Tesis SCJN

Este proyecto automatiza la recolección, almacenamiento y análisis de tesis y jurisprudencia de la Suprema Corte de Justicia de la Nación (SCJN).

## Características

- 🔍 **Scraping automático** de la página de búsqueda de tesis
- 📥 **Descarga automática** de PDFs a Google Drive
- 🧠 **Análisis con IA** usando OpenAI GPT
- 📊 **Base de datos** para consultas estructuradas
- 💬 **Chat integrado** para consultas en lenguaje natural
- 🏷️ **Categorización automática** de documentos

## Instalación

1. **Clonar el repositorio:**
```bash
git clone <tu-repositorio>
cd ia-scrapping-tesis
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Configurar Google Drive API:**
   - Crear proyecto en Google Cloud Console
   - Habilitar Google Drive API
   - Descargar credenciales JSON
   - Colocar en `credentials/google_drive_credentials.json`

## Configuración

### Variables de entorno (.env)
```
# OpenAI
OPENAI_API_KEY=tu_api_key_de_openai

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive_credentials.json
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_de_google_drive

# Database
DATABASE_URL=sqlite:///tesis_scjn.db

# Scraping
SCJN_BASE_URL=https://sjf2.scjn.gob.mx
SEARCH_URL=https://sjf2.scjn.gob.mx/busqueda-principal-tesis
```

## Uso

### 1. Ejecutar scraping inicial
```bash
python src/scraper/main.py
```

### 2. Iniciar servidor web
```bash
python src/api/main.py
```

### 3. Usar el chat de consultas
```bash
python src/chat/chat_interface.py
```

## Estructura del Proyecto

```
ia-scrapping-tesis/
├── src/
│   ├── scraper/          # Módulo de scraping
│   ├── storage/          # Gestión de Google Drive
│   ├── analysis/         # Análisis con IA
│   ├── database/         # Base de datos
│   ├── api/             # API REST
│   └── chat/            # Interfaz de chat
├── data/                # Datos descargados
├── credentials/         # Credenciales de APIs
├── logs/               # Logs del sistema
└── tests/              # Pruebas unitarias
```

## Funcionalidades

### Scraping Automático
- Monitoreo continuo de nuevas tesis
- Descarga automática de PDFs
- Extracción de metadatos

### Análisis con IA
- Categorización automática
- Resumen de contenido
- Extracción de conceptos clave
- Análisis de jurisprudencia

### Base de Datos
- Almacenamiento estructurado
- Búsquedas avanzadas
- Relaciones entre documentos

### Chat Inteligente
- Consultas en lenguaje natural
- Respuestas basadas en el contenido
- Sugerencias de documentos relacionados

## Contribuir

1. Fork el proyecto
2. Crear rama para nueva funcionalidad
3. Commit cambios
4. Push a la rama
5. Abrir Pull Request

## Licencia

MIT License 