#!/usr/bin/env python3
"""
Script simple para probar Google Drive
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gdrive():
    """Probar Google Drive"""
    
    print("🧪 === PRUEBA SIMPLE DE GOOGLE DRIVE ===")
    
    # Cargar configuración desde .env
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    print(f"📋 Configuración actual:")
    print(f"  GOOGLE_DRIVE_ENABLED: {os.getenv('GOOGLE_DRIVE_ENABLED', 'No configurado')}")
    print(f"  GOOGLE_DRIVE_FOLDER_ID: {os.getenv('GOOGLE_DRIVE_FOLDER_ID', 'No configurado')}")
    print(f"  GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH: {os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH', 'No configurado')}")
    
    # Verificar archivo de cuenta de servicio
    service_account_path = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH', 'service_account.json')
    if not os.path.exists(service_account_path):
        print(f"❌ Archivo de cuenta de servicio no encontrado: {service_account_path}")
        return False
    
    print(f"✅ Archivo de cuenta de servicio encontrado")
    
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        print(f"✅ GoogleDriveManager creado")
        print(f"✅ Folder ID detectado: {gdrive.folder_id}")
        
        if not gdrive.folder_id:
            print("❌ Folder ID no configurado")
            return False
        
        # Autenticar
        gdrive.authenticate()
        print("✅ Autenticación exitosa")
        
        # Listar archivos
        files = gdrive.list_files()
        print(f"✅ Conexión exitosa. Archivos en carpeta: {len(files)}")
        
        # Mostrar archivos existentes
        for file in files[:5]:
            print(f"  📄 {file.get('name', 'Sin nombre')}")
        
        if len(files) > 5:
            print(f"  ... y {len(files) - 5} más")
        
        # Crear archivo de prueba
        test_file = "test_gdrive_simple.txt"
        with open(test_file, "w") as f:
            f.write("Prueba simple de Google Drive\n")
            f.write("Si ves este archivo, Google Drive funciona correctamente\n")
        
        # Subir archivo
        result = gdrive.upload_file(test_file, "test_simple.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Archivo de prueba subido exitosamente")
            print(f"📄 ID: {file_id}")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar
            os.remove(test_file)
            print("✅ Archivo de prueba local eliminado")
            
            print("\n🎉 ¡Google Drive funciona correctamente!")
            return True
        else:
            print("❌ Error subiendo archivo de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    success = test_gdrive()
    
    if success:
        print("\n✅ Google Drive está configurado y funcionando")
        print("🚀 Puedes ejecutar el script de descarga de PDFs")
    else:
        print("\n❌ Google Drive no está configurado correctamente")
        print("📋 Necesitas configurar el folder ID correcto")

if __name__ == "__main__":
    main() 