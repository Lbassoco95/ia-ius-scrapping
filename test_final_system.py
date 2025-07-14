#!/usr/bin/env python3
"""
Script de prueba final del sistema completo
"""

import os
import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_final_system():
    """Prueba final del sistema completo"""
    
    print("🧪 === PRUEBA FINAL DEL SISTEMA ===")
    
    # Configurar variables de entorno
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    print("✅ Variables de entorno configuradas")
    
    try:
        from src.database.models import Tesis, get_session
        from src.storage.google_drive import GoogleDriveManager
        from src.scraper.selenium_scraper import SeleniumSCJNScraper
        
        # 1. Probar Google Drive
        print("\n☁️ Probando Google Drive...")
        gdrive = GoogleDriveManager()
        gdrive.authenticate()
        files = gdrive.list_files()
        print(f"✅ Google Drive: {len(files)} archivos en carpeta")
        
        # 2. Probar base de datos
        print("\n🗄️ Probando base de datos...")
        session = get_session()
        total_tesis = session.query(Tesis).count()
        tesis_con_pdf = session.query(Tesis).filter(Tesis.google_drive_link.isnot(None)).count()
        session.close()
        print(f"✅ Base de datos: {total_tesis} tesis total, {tesis_con_pdf} con PDF")
        
        # 3. Probar scraper con Firefox
        print("\n🌐 Probando scraper con Firefox...")
        scraper = SeleniumSCJNScraper()
        
        # Configurar Firefox
        if scraper.setup_driver():
            print("✅ Driver Firefox configurado")
            
            # Probar navegación
            if scraper.navigate_to_search_page():
                print("✅ Navegación a página de búsqueda exitosa")
                
                # Probar búsqueda
                if scraper.search_for_tesis("amparo"):
                    print("✅ Búsqueda exitosa")
                    
                    # Extraer algunos resultados
                    results = scraper.extract_search_results()
                    print(f"✅ Extraídos {len(results)} resultados")
                    
                    if results:
                        # Probar descarga de PDF del primer resultado
                        first_result = results[0]
                        print(f"\n📥 Probando descarga de PDF para: {first_result.get('scjn_id', 'N/A')}")
                        
                        pdf_path = scraper.download_pdf(first_result.get('url', ''), first_result.get('scjn_id', 'test'))
                        
                        if pdf_path and os.path.exists(pdf_path):
                            print(f"✅ PDF descargado: {pdf_path}")
                            
                            # Probar subida a Google Drive
                            print("☁️ Probando subida a Google Drive...")
                            filename = f"Test_Final_{first_result.get('scjn_id', 'test')}.pdf"
                            result = gdrive.upload_file(pdf_path, filename)
                            
                            if result:
                                file_id, web_link = result
                                print(f"✅ Subida exitosa")
                                print(f"🔗 Enlace: {web_link}")
                                
                                # Limpiar archivo de prueba
                                os.remove(pdf_path)
                                print("✅ Archivo de prueba eliminado")
                                
                                print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
                                return True
                            else:
                                print("❌ Error subiendo a Google Drive")
                        else:
                            print("❌ Error descargando PDF")
                    else:
                        print("❌ No se encontraron resultados")
                else:
                    print("❌ Error en búsqueda")
            else:
                print("❌ Error navegando a página de búsqueda")
        else:
            print("❌ Error configurando driver")
        
        # Cerrar scraper
        scraper.close_driver()
        
        return False
        
    except Exception as e:
        print(f"❌ Error en prueba final: {e}")
        return False

def setup_cron_job():
    """Configurar cron job para mañana a las 5 AM"""
    
    print("\n⏰ === CONFIGURANDO CRON JOB ===")
    
    # Obtener ruta absoluta del script principal
    script_path = os.path.abspath("start_auto_scraper.py")
    venv_python = os.path.abspath("venv/bin/python3")
    
    print(f"📁 Script: {script_path}")
    print(f"🐍 Python: {venv_python}")
    
    # Crear comando cron
    cron_command = f"0 5 * * * cd {os.getcwd()} && {venv_python} {script_path} >> logs/cron.log 2>&1"
    
    print(f"\n📋 Comando cron:")
    print(cron_command)
    
    # Crear script para agregar al cron
    cron_script = f"""#!/bin/bash
# Agregar al cron job
(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -
echo "✅ Cron job configurado para ejecutar mañana a las 5:00 AM"
"""
    
    with open("setup_cron.sh", "w") as f:
        f.write(cron_script)
    
    os.chmod("setup_cron.sh", 0o755)
    
    print("\n📝 Para configurar el cron job, ejecuta:")
    print("bash setup_cron.sh")
    
    return True

def main():
    """Función principal"""
    print("🚀 PREPARANDO SISTEMA PARA PRODUCCIÓN")
    
    # Probar sistema
    system_ok = test_final_system()
    
    if system_ok:
        print("\n✅ Sistema probado exitosamente")
        
        # Configurar cron job
        setup_cron_job()
        
        print("\n🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
        print("📋 Mañana a las 5:00 AM se ejecutará automáticamente")
        print("📊 Los resultados se guardarán en Google Drive")
        print("📝 Logs disponibles en: logs/auto_scraper.log")
        
    else:
        print("\n❌ Error en la prueba del sistema")
        print("📋 Revisa los errores antes de configurar el cron job")

if __name__ == "__main__":
    main() 