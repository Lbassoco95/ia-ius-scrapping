#!/usr/bin/env python3
"""
Script mejorado para descargar PDFs faltantes y subirlos a Google Drive
"""

import os
import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def download_and_upload_pdfs():
    """Descargar PDFs faltantes y subirlos a Google Drive"""
    
    print("📥 === DESCARGAR PDFS FALTANTES ===")
    
    # Configurar variables de entorno directamente
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    print("✅ Variables de entorno configuradas")
    
    try:
        from src.database.models import Tesis, get_session
        from src.storage.google_drive import GoogleDriveManager
        from src.scraper.selenium_scraper import SeleniumSCJNScraper
        
        # Verificar configuración de Google Drive
        gdrive = GoogleDriveManager()
        print(f"✅ Google Drive configurado con folder ID: {gdrive.folder_id}")
        
        # Autenticar Google Drive
        gdrive.authenticate()
        print("✅ Google Drive autenticado")
        
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
        
        # Procesar tesis (limitar a 5 para prueba)
        success_count = 0
        error_count = 0
        
        for i, tesis in enumerate(tesis_sin_pdf[:5]):
            print(f"\n📄 Procesando tesis {i+1}/5: {tesis.scjn_id}")
            print(f"  📝 Título: {tesis.titulo[:50]}...")
            
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
                    time.sleep(3)
                
                # Verificar que el PDF existe
                if not os.path.exists(pdf_path):
                    print(f"  ❌ PDF no encontrado en {pdf_path}")
                    error_count += 1
                    continue
                
                print(f"  ✅ PDF descargado: {pdf_path}")
                
                # Subir a Google Drive
                print(f"  ☁️ Subiendo a Google Drive...")
                
                # Generar nombre del archivo
                safe_title = tesis.titulo[:50].replace('/', '_').replace(':', '_').replace('\\', '_')
                filename = f"Tesis_{tesis.scjn_id}_{safe_title}.pdf"
                
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
                time.sleep(5)
                
            except Exception as e:
                print(f"  ❌ Error procesando tesis {tesis.scjn_id}: {e}")
                error_count += 1
        
        # Cerrar scraper
        scraper.close_driver()
        
        print(f"\n📊 Resumen:")
        print(f"✅ Tesis procesadas exitosamente: {success_count}")
        print(f"❌ Errores: {error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    success = download_and_upload_pdfs()
    
    if success:
        print("\n🎉 ¡Proceso completado!")
        print("📋 Revisa Google Drive para ver las tesis subidas")
        print("🔗 Ve a: https://drive.google.com/drive/u/0/folders/0AAL0nxoqH30XUk9PVA")
    else:
        print("\n❌ Error en el proceso")

if __name__ == "__main__":
    main() 