#!/usr/bin/env python3
"""
Script de producción listo para ejecutar automáticamente
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """Configurar entorno de producción"""
    
    # Configurar variables de entorno
    os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
    os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
    
    # Crear directorios necesarios
    Path("data/pdfs").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    print("✅ Entorno de producción configurado")

def test_google_drive():
    """Probar Google Drive"""
    
    try:
        from src.storage.google_drive import GoogleDriveManager
        
        gdrive = GoogleDriveManager()
        gdrive.authenticate()
        
        # Crear archivo de prueba
        test_file = "test_production.txt"
        with open(test_file, "w") as f:
            f.write(f"Prueba de producción - {datetime.now()}\n")
        
        result = gdrive.upload_file(test_file, "test_production.txt")
        
        if result:
            file_id, web_link = result
            print(f"✅ Google Drive funcionando: {web_link}")
            os.remove(test_file)
            return True
        else:
            print("❌ Error en Google Drive")
            return False
            
    except Exception as e:
        print(f"❌ Error Google Drive: {e}")
        return False

def test_database():
    """Probar base de datos"""
    
    try:
        from src.database.models import Tesis, get_session
        
        session = get_session()
        total_tesis = session.query(Tesis).count()
        session.close()
        
        print(f"✅ Base de datos: {total_tesis} tesis")
        return True
        
    except Exception as e:
        print(f"❌ Error base de datos: {e}")
        return False

def test_scraper():
    """Probar scraper"""
    
    try:
        from src.scraper.selenium_scraper import SeleniumSCJNScraper
        
        scraper = SeleniumSCJNScraper()
        
        if scraper.setup_driver():
            print("✅ Scraper configurado")
            scraper.close_driver()
            return True
        else:
            print("❌ Error configurando scraper")
            return False
            
    except Exception as e:
        print(f"❌ Error scraper: {e}")
        return False

def create_production_script():
    """Crear script de producción"""
    
    production_script = '''#!/usr/bin/env python3
"""
Script de producción para ejecución automática
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/production.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal de producción"""
    
    logger.info("🚀 Iniciando scraping automático")
    
    try:
        # Configurar entorno
        os.environ["GOOGLE_DRIVE_ENABLED"] = "true"
        os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "0AAL0nxoqH30XUk9PVA"
        os.environ["GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH"] = "service_account.json"
        
        # Importar módulos
        from src.scraper.main import SCJNScraper
        from src.storage.google_drive import GoogleDriveManager
        
        # Inicializar componentes
        scraper = SCJNScraper()
        gdrive = GoogleDriveManager()
        gdrive.authenticate()
        
        logger.info("✅ Componentes inicializados")
        
        # Ejecutar scraping
        results = scraper.run_scraping_session()
        
        logger.info(f"✅ Scraping completado: {len(results)} tesis procesadas")
        
        # Subir PDFs a Google Drive
        uploaded_count = 0
        for tesis in results:
            if tesis.get('pdf_path') and os.path.exists(tesis['pdf_path']):
                try:
                    filename = f"Tesis_{tesis['scjn_id']}_{tesis['titulo'][:50]}.pdf"
                    result = gdrive.upload_file(tesis['pdf_path'], filename)
                    if result:
                        uploaded_count += 1
                        logger.info(f"✅ Subido: {filename}")
                except Exception as e:
                    logger.error(f"❌ Error subiendo {tesis['scjn_id']}: {e}")
        
        logger.info(f"✅ {uploaded_count} PDFs subidos a Google Drive")
        
    except Exception as e:
        logger.error(f"❌ Error en producción: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Scraping automático completado exitosamente")
    else:
        print("❌ Error en scraping automático")
'''
    
    with open("production_scraper.py", "w") as f:
        f.write(production_script)
    
    os.chmod("production_scraper.py", 0o755)
    print("✅ Script de producción creado: production_scraper.py")

def setup_cron():
    """Configurar cron job"""
    
    # Obtener rutas absolutas
    script_path = os.path.abspath("production_scraper.py")
    venv_python = os.path.abspath("venv/bin/python3")
    work_dir = os.getcwd()
    
    # Comando cron para ejecutar mañana a las 5:00 AM
    cron_command = f"0 5 * * * cd {work_dir} && {venv_python} {script_path}"
    
    # Crear script de configuración
    cron_setup = f'''#!/bin/bash
echo "⏰ Configurando cron job para mañana a las 5:00 AM..."

# Agregar al cron
(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -

echo "✅ Cron job configurado"
echo "📋 Comando: {cron_command}"
echo "📝 Para ver cron jobs: crontab -l"
echo "📝 Para remover: crontab -r"
'''
    
    with open("setup_cron.sh", "w") as f:
        f.write(cron_setup)
    
    os.chmod("setup_cron.sh", 0o755)
    
    print("✅ Script de configuración de cron creado: setup_cron.sh")
    print(f"📋 Comando cron: {cron_command}")

def main():
    """Función principal"""
    
    print("🚀 PREPARANDO SISTEMA PARA PRODUCCIÓN")
    print("=" * 50)
    
    # Configurar entorno
    setup_environment()
    
    # Probar componentes
    print("\n🧪 Probando componentes...")
    
    tests = [
        ("Google Drive", test_google_drive),
        ("Base de datos", test_database),
        ("Scraper", test_scraper)
    ]
    
    all_tests_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 Probando {test_name}...")
        if test_func():
            print(f"✅ {test_name} OK")
        else:
            print(f"❌ {test_name} FALLÓ")
            all_tests_passed = False
    
    if all_tests_passed:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        
        # Crear script de producción
        create_production_script()
        
        # Configurar cron
        setup_cron()
        
        print("\n" + "=" * 50)
        print("🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
        print("=" * 50)
        print("📋 Para activar la ejecución automática:")
        print("   bash setup_cron.sh")
        print("\n📋 Para ejecutar manualmente:")
        print("   python3 production_scraper.py")
        print("\n📋 Para ver logs:")
        print("   tail -f logs/production.log")
        print("\n⏰ Mañana a las 5:00 AM se ejecutará automáticamente")
        
    else:
        print("\n❌ Algunos tests fallaron")
        print("📋 Revisa los errores antes de configurar producción")

if __name__ == "__main__":
    main() 