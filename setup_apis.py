#!/usr/bin/env python3
"""
🔑 Configuración de APIs - OpenAI y Google Drive

Este script ayuda a configurar las APIs necesarias para el sistema de scraping.
"""

import os
import json
from pathlib import Path

def setup_openai_api():
    """Configurar API de OpenAI"""
    print("🤖 CONFIGURACIÓN DE OPENAI API")
    print("=" * 40)
    
    print("📋 Pasos para obtener tu API key:")
    print("1. Ve a: https://platform.openai.com/api-keys")
    print("2. Inicia sesión o crea una cuenta")
    print("3. Haz clic en 'Create new secret key'")
    print("4. Copia la API key (empieza con 'sk-')")
    print("5. Guárdala en un lugar seguro")
    print()
    
    api_key = input("🔑 Ingresa tu OpenAI API key (sk-...): ").strip()
    
    if not api_key.startswith("sk-"):
        print("❌ Error: La API key debe empezar con 'sk-'")
        return False
    
    # Guardar en archivo de configuración
    config_dir = Path("data/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "openai_api_key": api_key,
        "openai_model": "gpt-4",
        "max_tokens": 2000
    }
    
    with open(config_dir / "openai_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ OpenAI API configurada correctamente")
    return True

def setup_google_drive_api():
    """Configurar API de Google Drive"""
    print("\n📁 CONFIGURACIÓN DE GOOGLE DRIVE API")
    print("=" * 40)
    
    print("📋 Pasos para configurar Google Drive:")
    print("1. Ve a: https://console.cloud.google.com/")
    print("2. Selecciona tu proyecto")
    print("3. Ve a: APIs & Services > Library")
    print("4. Busca 'Google Drive API' y habilítala")
    print("5. Ve a: APIs & Services > Credentials")
    print("6. Crea credenciales OAuth2")
    print("7. Descarga el archivo JSON")
    print()
    
    print("¿Ya tienes el archivo de credenciales JSON?")
    choice = input("1. Sí, tengo el archivo\n2. No, necesito ayuda\nTu elección (1-2): ")
    
    if choice == "1":
        file_path = input("📁 Ruta al archivo JSON de credenciales: ").strip()
        
        if not os.path.exists(file_path):
            print("❌ Error: El archivo no existe")
            return False
        
        # Copiar archivo a la configuración
        config_dir = Path("data/config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy(file_path, config_dir / "google_drive_credentials.json")
        
        print("✅ Credenciales de Google Drive copiadas")
        return True
    
    else:
        print("\n🔧 GUÍA DETALLADA PARA GOOGLE DRIVE API:")
        print("=" * 50)
        print("1. Ve a: https://console.cloud.google.com/")
        print("2. Selecciona tu proyecto: scjn-scraper-20250713")
        print("3. Ve a: APIs & Services > Library")
        print("4. Busca 'Google Drive API'")
        print("5. Haz clic en 'Enable'")
        print("6. Ve a: APIs & Services > Credentials")
        print("7. Haz clic en 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("8. Tipo de aplicación: 'Desktop application'")
        print("9. Nombre: 'SCJN Scraper'")
        print("10. Haz clic en 'Create'")
        print("11. Descarga el archivo JSON")
        print("12. Ejecuta este script nuevamente")
        print()
        print("💡 El archivo descargado se llamará algo como:")
        print("   client_secret_123456789-abcdefg.json")
        
        return False

def create_setup_script():
    """Crear script para configurar APIs en la VM"""
    script_content = '''#!/bin/bash
# 🔑 Script de Configuración de APIs en la VM

echo "🔑 CONFIGURANDO APIS EN LA VM"
echo "============================="

# Verificar que estamos en la VM
if [ ! -d "/home/ubuntu/scjn-scraper" ]; then
    echo "❌ Error: Este script debe ejecutarse en la VM"
    exit 1
fi

cd /home/ubuntu/scjn-scraper

# Configurar OpenAI API
echo "🤖 Configurando OpenAI API..."
if [ -f "data/config/openai_config.json" ]; then
    echo "✅ OpenAI API ya configurada"
else
    echo "❌ OpenAI API no configurada"
    echo "Ejecuta: python3 setup_apis.py"
fi

# Configurar Google Drive API
echo "📁 Configurando Google Drive API..."
if [ -f "data/config/google_drive_credentials.json" ]; then
    echo "✅ Google Drive API ya configurada"
    
    # Instalar dependencias de Google Drive
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    
    # Probar conexión
    python3 -c "
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Cargar credenciales
with open('data/config/google_drive_credentials.json', 'r') as f:
    creds_data = json.load(f)

# Crear credenciales
creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

# Probar conexión
service = build('drive', 'v3', credentials=creds)
about = service.about().get(fields='user').execute()
print(f'✅ Conectado a Google Drive como: {about[\"user\"][\"emailAddress\"]}')
"
else
    echo "❌ Google Drive API no configurada"
    echo "Ejecuta: python3 setup_apis.py"
fi

echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "1. Configurar APIs con: python3 setup_apis.py"
echo "2. Probar conexiones"
echo "3. Iniciar prueba inicial"
'''
    
    with open("setup_apis_vm.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("setup_apis_vm.sh", 0o755)
    print("✅ Script de configuración en VM creado: setup_apis_vm.sh")

def main():
    """Función principal"""
    print("🔑 CONFIGURACIÓN DE APIS - SCJN SCRAPER")
    print("=" * 50)
    print()
    
    print("📋 Este script te ayudará a configurar:")
    print("1. OpenAI API (para análisis de IA)")
    print("2. Google Drive API (para subida de archivos)")
    print()
    
    # Configurar OpenAI
    openai_ok = setup_openai_api()
    
    # Configurar Google Drive
    drive_ok = setup_google_drive_api()
    
    # Crear script para VM
    create_setup_script()
    
    print("\n🎯 RESUMEN:")
    if openai_ok:
        print("✅ OpenAI API: Configurada")
    else:
        print("❌ OpenAI API: Pendiente")
    
    if drive_ok:
        print("✅ Google Drive API: Configurada")
    else:
        print("❌ Google Drive API: Pendiente")
    
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. Esperar a que la VM esté lista")
    print("2. Conectar a la VM")
    print("3. Ejecutar: ./setup_apis_vm.sh")
    print("4. Configurar APIs si es necesario")
    print("5. Iniciar prueba inicial")

if __name__ == "__main__":
    main() 