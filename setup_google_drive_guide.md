# 🔧 Guía de Configuración de Google Drive

## Pasos para configurar Google Drive:

### 1. Crear Proyecto en Google Cloud Console
- Ve a: https://console.cloud.google.com/
- Crea un nuevo proyecto: "SCJN-Scraper"

### 2. Habilitar Google Drive API
- APIs & Services > Library
- Busca "Google Drive API" > Enable

### 3. Crear Service Account
- APIs & Services > Credentials
- Create Credentials > Service Account
- Nombre: scjn-scraper-service

### 4. Generar Clave JSON
- En Service Accounts, clic en el creado
- Keys > Add Key > Create new key > JSON
- Descarga y renombra a: `google_drive_credentials.json`
- Mueve a: `credentials/google_drive_credentials.json`

### 5. Configurar Carpeta
- Ve a https://drive.google.com/
- Crea carpeta "SCJN-Tesis-PDFs"
- Share con el email del service account
- Copia el ID de la URL de la carpeta

### 6. Actualizar .env
```bash
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_aqui
```

## Verificación:
```bash
python3 test_pdf_functionality.py
``` 