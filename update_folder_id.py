#!/usr/bin/env python3
"""
Script para actualizar el folder ID correcto
"""

import os

def update_folder_id():
    """Actualizar el folder ID correcto"""
    
    print("🔧 === ACTUALIZAR FOLDER ID ===")
    
    # Folder ID correcto de la URL proporcionada
    correct_folder_id = "0AAL0nxoqH30XUk9PVA"
    
    print(f"✅ Folder ID correcto: {correct_folder_id}")
    
    # Crear archivo .env con la configuración correcta
    config_content = f"""# Configuración de Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={correct_folder_id}
GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH=service_account.json
"""
    
    with open(".env", "w") as f:
        f.write(config_content)
    
    print("✅ Archivo .env actualizado")
    
    # Configurar variables de entorno
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = correct_folder_id
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    print("✅ Variables de entorno configuradas")
    
    # Probar la configuración
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        print(f"✅ GoogleDriveManager creado")
        print(f"✅ Folder ID detectado: {gdrive.folder_id}")
        
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
        test_file = "test_updated_folder.txt"
        with open(test_file, "w") as f:
            f.write("Prueba con folder ID actualizado\n")
            f.write(f"Folder ID: {correct_folder_id}\n")
            f.write("Configuración correcta\n")
        
        # Subir archivo
        result = gdrive.upload_file(test_file, "test_updated.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Archivo de prueba subido exitosamente")
            print(f"📄 ID: {file_id}")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar
            os.remove(test_file)
            print("✅ Archivo de prueba local eliminado")
            
            print("\n🎉 ¡Folder ID actualizado correctamente!")
            return True
        else:
            print("❌ Error subiendo archivo de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    success = update_folder_id()
    
    if success:
        print("\n✅ Google Drive configurado correctamente")
        print("🚀 Ahora puedes ejecutar el script de descarga de PDFs")
        print("📋 Ejecuta: python3 download_missing_pdfs.py")
    else:
        print("\n❌ Error actualizando la configuración")

if __name__ == "__main__":
    main() 