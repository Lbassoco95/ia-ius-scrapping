#!/usr/bin/env python3
"""
Script para obtener el folder ID correcto de la unidad compartida
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_shared_drive_info():
    """Obtener información de la unidad compartida"""
    
    print("🔍 === OBTENER FOLDER ID DE UNIDAD COMPARTIDA ===")
    print()
    print("📋 Para obtener el folder ID correcto:")
    print("1. Ve a Google Drive")
    print("2. Navega a la unidad compartida donde tienes acceso")
    print("3. Ve a la carpeta específica donde quieres guardar las tesis")
    print("4. Copia la URL completa")
    print()
    print("🔗 La URL se ve así:")
    print("https://drive.google.com/drive/folders/FOLDER_ID_AQUI")
    print()
    print("📝 O si estás dentro de la carpeta:")
    print("https://drive.google.com/drive/u/0/folders/FOLDER_ID_AQUI")
    print()
    
    url = input("🔗 Pega la URL de la carpeta: ").strip()
    
    if not url:
        print("❌ No se proporcionó URL")
        return None
    
    # Extraer folder ID de la URL
    folder_id = None
    
    if "/folders/" in url:
        # Buscar el folder ID después de /folders/
        parts = url.split("/folders/")
        if len(parts) > 1:
            folder_id = parts[1].split("?")[0].split("/")[0]
    
    if not folder_id:
        print("❌ No se pudo extraer el folder ID de la URL")
        print("📋 Asegúrate de que la URL contenga /folders/")
        return None
    
    print(f"✅ Folder ID extraído: {folder_id}")
    
    # Configurar variables de entorno
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
    
    # Crear archivo .env
    config_content = f"""# Configuración de Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={folder_id}
GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH=service_account.json
"""
    
    with open(".env", "w") as f:
        f.write(config_content)
    
    print("✅ Configuración guardada en .env")
    
    # Probar conexión
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        print(f"✅ GoogleDriveManager creado")
        print(f"✅ Folder ID configurado: {gdrive.folder_id}")
        
        # Probar autenticación
        gdrive.authenticate()
        print("✅ Autenticación exitosa")
        
        # Probar listar archivos
        print("🧪 Probando acceso a la carpeta...")
        files = gdrive.list_files()
        print(f"✅ Acceso exitoso. Archivos en carpeta: {len(files)}")
        
        # Mostrar algunos archivos
        for file in files[:5]:
            print(f"  📄 {file.get('name', 'Sin nombre')}")
        
        if len(files) > 5:
            print(f"  ... y {len(files) - 5} más")
        
        # Crear archivo de prueba
        test_file_path = "test_shared_drive.txt"
        with open(test_file_path, "w") as f:
            f.write("Archivo de prueba para unidad compartida\n")
            f.write(f"Folder ID: {folder_id}\n")
            f.write("Configuración completada exitosamente\n")
        
        # Subir archivo de prueba
        print("\n🧪 Probando subida de archivo...")
        result = gdrive.upload_file(test_file_path, "test_shared_drive.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Archivo de prueba subido exitosamente")
            print(f"📄 ID: {file_id}")
            print(f"🔗 Enlace: {web_link}")
            
            # Limpiar
            os.remove(test_file_path)
            print("✅ Archivo de prueba local eliminado")
            
            print("\n🎉 ¡Unidad compartida configurada exitosamente!")
            print(f"📁 Folder ID: {folder_id}")
            print("📋 El sistema ahora puede subir tesis automáticamente")
            
            return folder_id
        else:
            print("❌ Error subiendo archivo de prueba")
            return None
        
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return None

def main():
    """Función principal"""
    folder_id = get_shared_drive_info()
    
    if folder_id:
        print("\n📋 Resumen:")
        print("✅ Google Drive habilitado")
        print(f"✅ Folder ID configurado: {folder_id}")
        print("✅ Autenticación exitosa")
        print("✅ Acceso a unidad compartida funcionando")
        print("✅ Subida de archivos funcionando")
        print("\n🚀 El sistema está listo para subir tesis a la unidad compartida")
    else:
        print("\n❌ Error en la configuración")
        print("📋 Revisa los pasos e intenta nuevamente")

if __name__ == "__main__":
    main() 