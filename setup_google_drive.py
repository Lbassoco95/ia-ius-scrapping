#!/usr/bin/env python3
"""
Script para configurar Google Drive
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.storage.google_drive import GoogleDriveManager

def setup_google_drive():
    """Configurar Google Drive"""
    
    print("☁️ === CONFIGURACIÓN DE GOOGLE DRIVE ===")
    
    # 1. Verificar archivo de cuenta de servicio
    service_account_path = "service_account.json"
    if not os.path.exists(service_account_path):
        print(f"❌ Archivo de cuenta de servicio no encontrado: {service_account_path}")
        print("📋 Por favor, coloca el archivo service_account.json en el directorio raíz")
        return False
    
    print("✅ Archivo de cuenta de servicio encontrado")
    
    # 2. Configurar variables de entorno
    print("\n🔧 Configurando variables de entorno...")
    
    # Habilitar Google Drive
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = service_account_path
    
    # Solicitar folder ID
    print("\n📁 Configuración del Folder ID:")
    print("1. Ve a Google Drive")
    print("2. Navega a la carpeta donde quieres guardar las tesis")
    print("3. Copia el ID de la URL (después de /folders/)")
    print("4. O usa el ID de la unidad compartida si tienes uno")
    
    folder_id = input("\n🔗 Ingresa el Folder ID: ").strip()
    
    if not folder_id:
        print("❌ No se proporcionó Folder ID")
        return False
    
    # Configurar folder ID
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
    
    print(f"✅ Folder ID configurado: {folder_id}")
    
    # 3. Probar conexión
    print("\n🧪 Probando conexión a Google Drive...")
    
    try:
        gdrive = GoogleDriveManager()
        
        # Verificar configuración
        if not gdrive.folder_id:
            print("❌ Folder ID no se configuró correctamente")
            return False
        
        print(f"✅ Folder ID detectado: {gdrive.folder_id}")
        
        # Autenticar
        gdrive.authenticate()
        print("✅ Autenticación exitosa")
        
        # Listar archivos existentes
        files = gdrive.list_files()
        print(f"✅ Conexión exitosa. Archivos en carpeta: {len(files)}")
        
        # Mostrar algunos archivos
        for file in files[:5]:
            print(f"  📄 {file.get('name', 'Sin nombre')}")
        
        if len(files) > 5:
            print(f"  ... y {len(files) - 5} más")
        
        # 4. Crear archivo de configuración
        config_content = f"""# Configuración de Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={folder_id}
GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH={service_account_path}
"""
        
        with open(".env", "w") as f:
            f.write(config_content)
        
        print("\n✅ Configuración guardada en .env")
        
        # 5. Probar subida de archivo de prueba
        print("\n🧪 Probando subida de archivo...")
        
        # Crear archivo de prueba
        test_file_path = "test_google_drive.txt"
        with open(test_file_path, "w") as f:
            f.write("Archivo de prueba para Google Drive\n")
            f.write(f"Creado el: {os.popen('date').read().strip()}\n")
        
        # Subir archivo
        result = gdrive.upload_file(test_file_path, "test_google_drive.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Archivo de prueba subido exitosamente")
            print(f"📄 ID: {file_id}")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar archivo de prueba
            os.remove(test_file_path)
            print("✅ Archivo de prueba local eliminado")
        else:
            print("❌ Error subiendo archivo de prueba")
            return False
        
        print("\n🎉 ¡Google Drive configurado exitosamente!")
        print("📋 El sistema ahora puede subir tesis automáticamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Google Drive: {e}")
        return False

def main():
    """Función principal"""
    success = setup_google_drive()
    
    if success:
        print("\n📋 Resumen:")
        print("✅ Google Drive habilitado")
        print("✅ Folder ID configurado")
        print("✅ Autenticación exitosa")
        print("✅ Subida de archivos funcionando")
        print("\n🚀 El sistema está listo para subir tesis a Google Drive")
    else:
        print("\n❌ Error en la configuración")
        print("📋 Revisa los pasos e intenta nuevamente")

if __name__ == "__main__":
    main() 