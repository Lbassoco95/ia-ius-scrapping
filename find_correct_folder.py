#!/usr/bin/env python3
"""
Script para encontrar el folder ID correcto de la unidad compartida
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def find_correct_folder():
    """Encontrar el folder ID correcto"""
    
    print("🔍 === ENCONTRAR FOLDER ID CORRECTO ===")
    print()
    print("📋 Instrucciones:")
    print("1. Ve a Google Drive en tu navegador")
    print("2. Navega a la unidad compartida donde tienes acceso")
    print("3. Ve a la carpeta específica donde quieres guardar las tesis")
    print("4. Copia la URL de la barra de direcciones")
    print()
    print("🔗 Ejemplos de URLs válidas:")
    print("• https://drive.google.com/drive/folders/1ABC123DEF456GHI789JKL")
    print("• https://drive.google.com/drive/u/0/folders/1ABC123DEF456GHI789JKL")
    print("• https://drive.google.com/drive/folders/1ABC123DEF456GHI789JKL?usp=sharing")
    print()
    
    # Solicitar URL
    url = input("🔗 Pega la URL de la carpeta: ").strip()
    
    if not url:
        print("❌ No se proporcionó URL")
        return None
    
    # Extraer folder ID
    folder_id = None
    
    if "/folders/" in url:
        parts = url.split("/folders/")
        if len(parts) > 1:
            folder_id = parts[1].split("?")[0].split("/")[0]
    
    if not folder_id:
        print("❌ No se pudo extraer el folder ID")
        return None
    
    print(f"✅ Folder ID extraído: {folder_id}")
    
    # Configurar y probar
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
    
    # Actualizar .env
    config_content = f"""# Configuración de Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={folder_id}
GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH=service_account.json
"""
    
    with open(".env", "w") as f:
        f.write(config_content)
    
    print("✅ Archivo .env actualizado")
    
    # Probar conexión
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        gdrive.authenticate()
        
        print("✅ Autenticación exitosa")
        
        # Probar acceso
        files = gdrive.list_files()
        print(f"✅ Acceso exitoso. Archivos en carpeta: {len(files)}")
        
        # Crear archivo de prueba
        test_file = "test_folder_access.txt"
        with open(test_file, "w") as f:
            f.write(f"Prueba de acceso al folder {folder_id}\n")
        
        result = gdrive.upload_file(test_file, "test_access.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Subida exitosa")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar
            os.remove(test_file)
            
            print(f"\n🎉 ¡Folder ID correcto encontrado: {folder_id}")
            return folder_id
        else:
            print("❌ Error en subida de prueba")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Función principal"""
    folder_id = find_correct_folder()
    
    if folder_id:
        print(f"\n✅ Configuración completada")
        print(f"📁 Folder ID: {folder_id}")
        print("🚀 El sistema está listo para subir tesis")
    else:
        print("\n❌ No se pudo configurar correctamente")

if __name__ == "__main__":
    main() 