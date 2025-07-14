#!/usr/bin/env python3
"""
Script para descargar PDFs faltantes y subirlos a Google Drive
"""

import os
import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.models import Tesis, get_session
from src.storage.google_drive import GoogleDriveManager
from src.scraper.selenium_scraper import SeleniumSCJNScraper

def download_and_upload_missing_pdfs():
    """Descargar PDFs faltantes y subirlos a Google Drive"""
    
    print("📥 === DESCARGAR PDFS FALTANTES ===")
    
    # Configurar Google Drive
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    # Cargar configuración desde .env si existe
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    # Verificar configuración de Google Drive
    gdrive = GoogleDriveManager()
    if not gdrive.folder_id:
        print("❌ Google Drive no está configurado correctamente")
        print("📋 Ejecuta primero: python3 find_correct_folder.py")
        return False
    
    print(f"✅ Google Drive configurado con folder ID: {gdrive.folder_id}")
    
    # Autenticar Google Drive
    try:
        gdrive.authenticate()
        print("✅ Google Drive autenticado")
    except Exception as e:
        print(f"❌ Error autenticando Google Drive: {e}")
        return False
    
    # Obtener tesis sin PDF en Google Drive
    session = get_session()
    tesis_sin_pdf = session.query(Tesis).filter(Tesis.google_drive_link.is_(None)).all()
    session.close()
    
    print(f"📊 Total de tesis sin PDF en Drive: {len(tesis_sin_pdf)}")
    
    if not tesis_sin_pdf:
        print("✅ Todas las tesis ya tienen PDF en Google Drive")
        return True
    
    # Crear scraper
    scraper = SeleniumSCJNScraper()
    
    # Procesar tesis
    success_count = 0
    error_count = 0
    
    for i, tesis in enumerate(tesis_sin_pdf[:10]):  # Limitar a 10 para prueba
        print(f"\n📄 Procesando tesis {i+1}/{min(10, len(tesis_sin_pdf))}: {tesis.scjn_id}")
        
        try:
            # Verificar si ya existe el PDF localmente
            pdf_path = f"data/pdfs/tesis_{tesis.scjn_id}.pdf"
            
            if not os.path.exists(pdf_path):
                print(f"  📥 Descargando PDF...")
                
                # Descargar PDF
                pdf_downloaded = scraper.download_pdf(tesis.url, tesis.scjn_id)
                
                if not pdf_downloaded:
                    print(f"  ❌ No se pudo descargar PDF para tesis {tesis.scjn_id}")
                    error_count += 1
                    continue
                
                # Esperar un poco para que se complete la descarga
                time.sleep(2)
            
            # Verificar que el PDF existe
            if not os.path.exists(pdf_path):
                print(f"  ❌ PDF no encontrado en {pdf_path}")
                error_count += 1
                continue
            
            print(f"  ✅ PDF descargado: {pdf_path}")
            
            # Subir a Google Drive
            print(f"  ☁️ Subiendo a Google Drive...")
            
            # Generar nombre del archivo
            filename = f"Tesis_{tesis.scjn_id}_{tesis.titulo[:50].replace('/', '_').replace(':', '_')}.pdf"
            
            result = gdrive.upload_file(pdf_path, filename)
            
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
            
            # Esperar entre descargas
            time.sleep(3)
            
        except Exception as e:
            print(f"  ❌ Error procesando tesis {tesis.scjn_id}: {e}")
            error_count += 1
    
    # Cerrar scraper
    scraper.close_driver()
    
    print(f"\n📊 Resumen:")
    print(f"✅ Tesis procesadas exitosamente: {success_count}")
    print(f"❌ Errores: {error_count}")
    
    return success_count > 0

def main():
    """Función principal"""
    success = download_and_upload_missing_pdfs()
    
    if success:
        print("\n🎉 ¡Proceso completado!")
        print("📋 Revisa Google Drive para ver las tesis subidas")
    else:
        print("\n❌ Error en el proceso")

if __name__ == "__main__":
    main() 