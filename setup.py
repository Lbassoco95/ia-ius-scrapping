#!/usr/bin/env python3
"""
Script de instalación y configuración del sistema de scraping SCJN
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar progreso"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        'data',
        'data/pdfs',
        'credentials',
        'logs',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")

def install_dependencies():
    """Instalar dependencias de Python"""
    print("📦 Instalando dependencias...")
    
    # Actualizar pip
    if not run_command("pip install --upgrade pip", "Actualizando pip"):
        return False
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        return False
    
    return True

def setup_environment():
    """Configurar archivo de variables de entorno"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  El archivo .env ya existe. ¿Deseas sobrescribirlo? (y/N): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("📝 Manteniendo archivo .env existente")
            return True
    
    print("📝 Configurando variables de entorno...")
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive_credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here

# Database Configuration
DATABASE_URL=sqlite:///data/tesis_scjn.db

# SCJN URLs
SCJN_BASE_URL=https://sjf2.scjn.gob.mx
SEARCH_URL=https://sjf2.scjn.gob.mx/busqueda-principal-tesis

# Scraping Configuration
SCRAPING_INTERVAL=3600
MAX_DOCUMENTS_PER_RUN=100
DOWNLOAD_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scraper.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado")
    print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales")
    return True

def setup_google_drive():
    """Configurar Google Drive API"""
    print("🔧 Configuración de Google Drive API")
    print("""
Para configurar Google Drive API:

1. Ve a https://console.cloud.google.com/
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la Google Drive API
4. Crea credenciales de servicio:
   - Ve a "APIs & Services" > "Credentials"
   - Haz clic en "Create Credentials" > "Service Account"
   - Descarga el archivo JSON
5. Coloca el archivo JSON en credentials/google_drive_credentials.json
6. Comparte la carpeta de Google Drive con el email del service account

¿Deseas continuar con la configuración manual? (y/N): """, end="")
    
    response = input().strip().lower()
    if response == 'y':
        print("📋 Pasos para completar la configuración:")
        print("1. Descarga las credenciales de Google Drive")
        print("2. Colócalas en: credentials/google_drive_credentials.json")
        print("3. Edita el archivo .env con tu GOOGLE_DRIVE_FOLDER_ID")
    
    return True

def setup_openai():
    """Configurar OpenAI API"""
    print("🔧 Configuración de OpenAI API")
    print("""
Para configurar OpenAI API:

1. Ve a https://platform.openai.com/
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys"
4. Crea una nueva API key
5. Copia la key y edita el archivo .env

¿Deseas continuar con la configuración manual? (y/N): """, end="")
    
    response = input().strip().lower()
    if response == 'y':
        print("📋 Pasos para completar la configuración:")
        print("1. Obtén tu API key de OpenAI")
        print("2. Edita el archivo .env con tu OPENAI_API_KEY")
    
    return True

def test_installation():
    """Probar la instalación"""
    print("🧪 Probando instalación...")
    
    # Probar imports básicos
    try:
        import requests
        import beautifulsoup4
        import sqlalchemy
        print("✅ Dependencias básicas importadas correctamente")
    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        return False
    
    # Probar configuración
    try:
        from src.config import Config
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False
    
    # Probar base de datos
    try:
        from src.database.models import create_database
        create_database()
        print("✅ Base de datos creada correctamente")
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False
    
    print("✅ Instalación probada correctamente")
    return True

def show_next_steps():
    """Mostrar próximos pasos"""
    print("""
🎉 ¡Instalación completada!

📋 PRÓXIMOS PASOS:

1. 🔑 Configurar credenciales:
   - Edita el archivo .env con tus API keys
   - Configura Google Drive API
   - Configura OpenAI API

2. 🚀 Ejecutar scraping inicial:
   python src/scraper/main.py

3. 🌐 Iniciar API REST:
   python src/api/main.py

4. 💬 Usar chat de consultas:
   python src/chat/chat_interface.py

📚 DOCUMENTACIÓN:
- README.md: Guía completa del proyecto
- /docs: Documentación de la API (cuando esté ejecutándose)

🔧 COMANDOS ÚTILES:
- Scraping completo: python src/scraper/main.py full
- Scraping incremental: python src/scraper/main.py incremental
- API con documentación: http://localhost:8000/docs

¿Necesitas ayuda con algún paso específico?
""")

def main():
    """Función principal de instalación"""
    print("🚀 INSTALADOR - SISTEMA DE SCRAPING SCJN")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)
    
    # Configurar entorno
    if not setup_environment():
        print("❌ Error configurando entorno")
        sys.exit(1)
    
    # Configurar APIs
    setup_google_drive()
    setup_openai()
    
    # Probar instalación
    if not test_installation():
        print("❌ Error en pruebas de instalación")
        sys.exit(1)
    
    # Mostrar próximos pasos
    show_next_steps()

if __name__ == "__main__":
    main() 