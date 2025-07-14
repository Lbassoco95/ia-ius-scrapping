#!/usr/bin/env python3
"""
Script para subir PDFs existentes a Google Drive
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def upload_existing_pdfs():
    """Subir PDFs existentes a Google Drive"""
    
    print("☁️ === SUBIR PDFS EXISTENTES A GOOGLE DRIVE ===")
    
    # Configurar variables de entorno directamente
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    print("✅ Variables de entorno configuradas")
    
    try:
        from src.database.models import Tesis, get_session
        from src.storage.google_drive import GoogleDriveManager
        
        # Verificar configuración de Google Drive
        gdrive = GoogleDriveManager()
        print(f"✅ Google Drive configurado con folder ID: {gdrive.folder_id}")
        
        # Autenticar Google Drive
        gdrive.authenticate()
        print("✅ Google Drive autenticado")
        
        # Verificar PDFs existentes
        pdfs_dir = Path("data/pdfs")
        if not pdfs_dir.exists():
            print("❌ Directorio de PDFs no encontrado")
            return False
        
        pdf_files = list(pdfs_dir.glob("tesis_*.pdf"))
        print(f"📊 PDFs encontrados: {len(pdf_files)}")
        
        if not pdf_files:
            print("❌ No se encontraron PDFs para subir")
            return False
        
        # Mostrar PDFs encontrados
        for pdf_file in pdf_files:
            print(f"  📄 {pdf_file.name}")
        
        # Obtener tesis sin PDF en Google Drive
        session = get_session()
        tesis_sin_pdf = session.query(Tesis).filter(Tesis.google_drive_link.is_(None)).all()
        session.close()
        
        print(f"📊 Tesis sin PDF en Drive: {len(tesis_sin_pdf)}")
        
        # Procesar PDFs existentes
        success_count = 0
        error_count = 0
        
        for pdf_file in pdf_files:
            # Extraer ID de tesis del nombre del archivo
            filename = pdf_file.name
            if filename.startswith("tesis_") and filename.endswith(".pdf"):
                tesis_id = filename[6:-4]  # Remover "tesis_" y ".pdf"
                
                print(f"\n📄 Procesando: {filename}")
                print(f"  🆔 ID de tesis: {tesis_id}")
                
                # Buscar tesis en la base de datos
                session = get_session()
                tesis = session.query(Tesis).filter(Tesis.scjn_id == tesis_id).first()
                session.close()
                
                if not tesis:
                    print(f"  ❌ Tesis {tesis_id} no encontrada en la base de datos")
                    error_count += 1
                    continue
                
                print(f"  📝 Título: {tesis.titulo[:50]}...")
                
                # Verificar si ya tiene enlace de Google Drive
                if tesis.google_drive_link:
                    print(f"  ✅ Ya tiene enlace de Google Drive")
                    continue
                
                try:
                    # Subir a Google Drive
                    print(f"  ☁️ Subiendo a Google Drive...")
                    
                    # Generar nombre del archivo
                    safe_title = tesis.titulo[:50].replace('/', '_').replace(':', '_').replace('\\', '_')
                    filename = f"Tesis_{tesis.scjn_id}_{safe_title}.pdf"
                    
                    result = gdrive.upload_file(str(pdf_file), filename)
                    
                    if result:
                        file_id, web_link = result
                        print(f"  ✅ Subido exitosamente")
                        print(f"  🔗 Enlace: {web_link}")
                        
                        # Actualizar base de datos
                        session = get_session()
                        tesis_db = session.query(Tesis).filter(Tesis.id == tesis.id).first()
                        if tesis_db:
                            tesis_db.google_drive_id = file_id
                            tesis_db.google_drive_link = web_link
                            session.commit()
                            print(f"  💾 Base de datos actualizada")
                        session.close()
                        
                        success_count += 1
                    else:
                        print(f"  ❌ Error subiendo a Google Drive")
                        error_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Error procesando {filename}: {e}")
                    error_count += 1
        
        print(f"\n📊 Resumen:")
        print(f"✅ PDFs subidos exitosamente: {success_count}")
        print(f"❌ Errores: {error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    success = upload_existing_pdfs()
    
    if success:
        print("\n🎉 ¡Proceso completado!")
        print("📋 Revisa Google Drive para ver las tesis subidas")
        print("🔗 Ve a: https://drive.google.com/drive/u/0/folders/0AAL0nxoqH30XUk9PVA")
    else:
        print("\n❌ Error en el proceso")

if __name__ == "__main__":
    main() 