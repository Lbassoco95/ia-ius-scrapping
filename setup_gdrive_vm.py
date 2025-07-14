#!/usr/bin/env python3
"""
Script para configurar Google Drive API en la VM
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def setup_google_drive():
    """Configurar Google Drive API"""
    
    # Configuración de Google Drive
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    CREDENTIALS_FILE = 'credentials/client_secret.json'
    TOKEN_FILE = 'credentials/token.pickle'
    
    print("🔑 CONFIGURANDO GOOGLE DRIVE API")
    print("=" * 50)
    
    # Verificar que existe el archivo de credenciales
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: No se encuentra {CREDENTIALS_FILE}")
        return False
    
    print(f"✅ Archivo de credenciales encontrado: {CREDENTIALS_FILE}")
    
    # Crear credenciales
    creds = None
    
    # Cargar token existente si existe
    if os.path.exists(TOKEN_FILE):
        print("📁 Cargando token existente...")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, solicitar autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refrescando token...")
            creds.refresh(Request())
        else:
            print("🔐 Solicitando autorización...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para la próxima vez
        print("💾 Guardando credenciales...")
        os.makedirs('credentials', exist_ok=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    print("✅ Google Drive API configurada correctamente")
    
    # Crear archivo .env con la configuración
    env_content = f"""# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials/client_secret.json
GOOGLE_DRIVE_TOKEN_FILE=credentials/token.pickle
GOOGLE_DRIVE_FOLDER_ID=root  # Cambiar por el ID de tu carpeta específica

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Archivo .env actualizado")
    print("📁 Los PDFs se subirán a la carpeta raíz de Google Drive")
    print("💡 Para cambiar la carpeta, edita GOOGLE_DRIVE_FOLDER_ID en .env")
    
    return True

if __name__ == "__main__":
    setup_google_drive() 