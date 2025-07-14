#!/usr/bin/env python3
"""
Script de prueba simplificado para Google Drive compartido
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

def test_google_drive_upload():
    """Probar subida de archivo a Google Drive compartido"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        print("🚀 Iniciando prueba de Google Drive compartido...")
        
        # Configuración
        service_account_path = "credentials/service_account.json"
        
        print(f"🔑 Archivo de credenciales: {service_account_path}")
        
        if not os.path.exists(service_account_path):
            print("❌ Archivo de cuenta de servicio no encontrado")
            return False
        
        # Crear credenciales
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Construir servicio
        service = build('drive', 'v3', credentials=credentials)
        
        # Crear archivo de prueba
        test_file_path = "test_upload.txt"
        test_content = f"Archivo de prueba - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nEste archivo fue subido automáticamente por el sistema de scraping SCJN."
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        print(f"📝 Archivo de prueba creado: {test_file_path}")
        
        # Preparar archivo para subir (sin especificar carpeta)
        filename = f"test_scjn_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_metadata = {
            'name': filename
            # No especificamos 'parents' para subir directamente al Drive compartido
        }
        
        # Subir archivo
        media = MediaFileUpload(test_file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        web_link = file.get('webViewLink')
        
        print(f"✅ Archivo subido exitosamente!")
        print(f"   Nombre: {file_name}")
        print(f"   ID: {file_id}")
        print(f"   Enlace: {web_link}")
        
        # Limpiar archivo de prueba local
        os.remove(test_file_path)
        print(f"🧹 Archivo de prueba local eliminado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA DE GOOGLE DRIVE COMPARTIDO")
    print("=" * 45)
    
    # Verificar configuración
    if not os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true":
        print("❌ Google Drive no está habilitado")
        return False
    
    # Ejecutar prueba
    success = test_google_drive_upload()
    
    if success:
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("Google Drive compartido está configurado correctamente.")
        print("El sistema de scraping ahora puede subir PDFs automáticamente.")
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("Revisa la configuración y los permisos.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 