#!/usr/bin/env python3
"""
Configuración paso a paso de Google Drive para el sistema de scraping
"""

import os
import json
from pathlib import Path

def create_env_template():
    """Crear plantilla de archivo .env"""
    env_content = """# Google Drive Configuration
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive_credentials.json

# Database Configuration
DATABASE_URL=sqlite:///data/scjn_database.db

# Scraping Configuration
SCRAPING_INTERVAL=3600
MAX_DOCUMENTS_PER_RUN=100
DOWNLOAD_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scraper.log
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado")

def create_credentials_template():
    """Crear plantilla de credenciales"""
    cred_template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    # Crear directorio credentials si no existe
    os.makedirs('credentials', exist_ok=True)
    
    with open('credentials/google_drive_credentials.json', 'w') as f:
        json.dump(cred_template, f, indent=2)
    
    print("✅ Plantilla de credenciales creada")

def main():
    """Configuración principal de Google Drive"""
    print("☁️ CONFIGURACIÓN DE GOOGLE DRIVE")
    print("=" * 50)
    
    print("📋 Este script te ayudará a configurar Google Drive paso a paso.")
    print()
    
    # Paso 1: Verificar si ya está configurado
    if os.path.exists('credentials/google_drive_credentials.json'):
        print("⚠️  Ya existe un archivo de credenciales.")
        response = input("¿Deseas sobrescribirlo? (y/N): ").strip().lower()
        if response != 'y':
            print("📝 Manteniendo configuración existente")
            return
    
    # Paso 2: Crear archivos de configuración
    print("\n🔧 PASO 1: Creando archivos de configuración...")
    create_env_template()
    create_credentials_template()
    
    # Paso 3: Instrucciones
    print("\n📚 PASO 2: Configurar Google Cloud Console")
    print("=" * 50)
    print("1. Ve a https://console.cloud.google.com/")
    print("2. Crea un nuevo proyecto o selecciona uno existente")
    print("3. Habilita la facturación (requerido para APIs)")
    print("4. Ve a 'APIs & Services' > 'Library'")
    print("5. Busca 'Google Drive API' y haz clic en 'Enable'")
    print("6. Ve a 'APIs & Services' > 'Credentials'")
    print("7. Haz clic en 'Create Credentials' > 'Service Account'")
    print("8. Completa la información:")
    print("   - Name: scjn-scraper")
    print("   - Description: Service account for SCJN scraping")
    print("9. Haz clic en 'Create and Continue'")
    print("10. En 'Grant this service account access to project':")
    print("    - Selecciona 'Editor'")
    print("11. Haz clic en 'Done'")
    
    input("\n⏸️  Presiona Enter cuando hayas completado estos pasos...")
    
    # Paso 4: Descargar credenciales
    print("\n📥 PASO 3: Descargar credenciales")
    print("=" * 50)
    print("1. En la lista de service accounts, haz clic en 'scjn-scraper'")
    print("2. Ve a la pestaña 'Keys'")
    print("3. Haz clic en 'Add Key' > 'Create new key'")
    print("4. Selecciona 'JSON'")
    print("5. Descarga el archivo")
    print("6. Renombra el archivo a 'google_drive_credentials.json'")
    print("7. Mueve el archivo a la carpeta 'credentials/'")
    
    input("\n⏸️  Presiona Enter cuando hayas descargado las credenciales...")
    
    # Paso 5: Configurar Google Drive
    print("\n📁 PASO 4: Configurar Google Drive")
    print("=" * 50)
    print("1. Ve a https://drive.google.com/")
    print("2. Crea una nueva carpeta llamada 'SCJN Tesis'")
    print("3. Haz clic derecho en la carpeta > 'Share'")
    print("4. Agrega el email del service account (está en el archivo JSON)")
    print("5. Dale permisos de 'Editor'")
    print("6. Copia el ID de la carpeta de la URL:")
    print("   https://drive.google.com/drive/folders/FOLDER_ID_AQUI")
    
    folder_id = input("\n📋 Ingresa el ID de la carpeta: ").strip()
    
    if folder_id:
        # Actualizar archivo .env
        with open('.env', 'r') as f:
            env_content = f.read()
        
        env_content = env_content.replace('your_folder_id_here', folder_id)
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ ID de carpeta actualizado en .env")
    
    # Paso 6: Verificar configuración
    print("\n🔍 PASO 5: Verificar configuración")
    print("=" * 50)
    
    if os.path.exists('credentials/google_drive_credentials.json'):
        try:
            with open('credentials/google_drive_credentials.json', 'r') as f:
                cred_data = json.load(f)
            
            if cred_data.get('type') == 'service_account':
                print("✅ Archivo de credenciales válido")
                print(f"📧 Service account: {cred_data.get('client_email')}")
            else:
                print("❌ Archivo de credenciales no válido")
        except Exception as e:
            print(f"❌ Error leyendo credenciales: {e}")
    else:
        print("❌ Archivo de credenciales no encontrado")
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
        
        if 'your_folder_id_here' not in env_content:
            print("✅ Archivo .env configurado")
        else:
            print("⚠️  Archivo .env necesita configuración")
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 50)
    print("📋 Próximos pasos:")
    print("1. Ejecutar: python3 verify_complete_system.py")
    print("2. Si todo está bien, ejecutar: python3 test_extended_scraping.py")
    print("3. Monitorear con: python3 monitor_extended_test.py")

if __name__ == "__main__":
    main() 