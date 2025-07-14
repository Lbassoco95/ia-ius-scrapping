#!/usr/bin/env python3
"""
Configuración rápida de Google Drive con unidad compartida
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_gdrive_quick():
    """Configuración rápida de Google Drive"""
    
    print("☁️ === CONFIGURACIÓN RÁPIDA DE GOOGLE DRIVE ===")
    
    # Configurar variables de entorno
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    # Usar el folder ID de la unidad compartida que mencionaste antes
    # Si tienes un folder ID específico, cámbialo aquí
    folder_id = "0AAqX9jQHVyqUk9PVA"  # ID de unidad compartida
    
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
    
    print(f"✅ Google Drive habilitado")
    print(f"✅ Folder ID configurado: {folder_id}")
    print(f"✅ Ruta de cuenta de servicio: service_account.json")
    
    # Crear archivo .env
    config_content = f"""# Configuración de Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={folder_id}
GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH=service_account.json
"""
    
    with open(".env", "w") as f:
        f.write(config_content)
    
    print("✅ Configuración guardada en .env")
    
    # Probar configuración
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        print(f"✅ GoogleDriveManager creado")
        print(f"✅ Folder ID detectado: {gdrive.folder_id}")
        
        # Probar autenticación
        gdrive.authenticate()
        print("✅ Autenticación exitosa")
        
        # Listar archivos
        files = gdrive.list_files()
        print(f"✅ Conexión exitosa. Archivos en carpeta: {len(files)}")
        
        # Crear carpeta de tesis si no existe
        tesis_folder_name = "Tesis SCJN"
        tesis_folder_id = None
        
        # Buscar si ya existe la carpeta
        for file in files:
            if file.get('name') == tesis_folder_name:
                tesis_folder_id = file.get('id')
                break
        
        if not tesis_folder_id:
            # Crear carpeta
            tesis_folder_id = gdrive.create_folder(tesis_folder_name, folder_id)
            print(f"✅ Carpeta '{tesis_folder_name}' creada con ID: {tesis_folder_id}")
        else:
            print(f"✅ Carpeta '{tesis_folder_name}' ya existe con ID: {tesis_folder_id}")
        
        # Actualizar configuración para usar la carpeta de tesis
        if tesis_folder_id:
            os.environ["GOOGLE_DRIVE_FOLDER_ID"] = tesis_folder_id
        
        # Crear archivo de prueba
        test_file_path = "test_gdrive_setup.txt"
        with open(test_file_path, "w") as f:
            f.write("Archivo de prueba para Google Drive\n")
            f.write("Configuración completada exitosamente\n")
        
        # Subir archivo de prueba
        if tesis_folder_id:
            result = gdrive.upload_file(test_file_path, "test_setup.txt", tesis_folder_id)
        else:
            result = gdrive.upload_file(test_file_path, "test_setup.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Archivo de prueba subido exitosamente")
            print(f"📄 ID: {file_id}")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar
            os.remove(test_file_path)
            print("✅ Archivo de prueba local eliminado")
        else:
            print("❌ Error subiendo archivo de prueba")
            return False
        
        print("\n🎉 ¡Google Drive configurado exitosamente!")
        print(f"📁 Carpeta de tesis: {tesis_folder_name}")
        print(f"🔗 ID de carpeta: {tesis_folder_id}")
        print("📋 El sistema ahora puede subir tesis automáticamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Google Drive: {e}")
        return False

def main():
    """Función principal"""
    success = setup_gdrive_quick()
    
    if success:
        print("\n📋 Resumen:")
        print("✅ Google Drive habilitado")
        print("✅ Folder ID configurado")
        print("✅ Carpeta de tesis creada")
        print("✅ Autenticación exitosa")
        print("✅ Subida de archivos funcionando")
        print("\n🚀 El sistema está listo para subir tesis a Google Drive")
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main() 