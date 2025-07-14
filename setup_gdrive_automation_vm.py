#!/usr/bin/env python3
"""
Script de configuración automática de Google Drive para VM
Configura cuenta de servicio y automatización completa
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VMGoogleDriveSetup:
    """Configurador de Google Drive para VM"""
    
    def __init__(self):
        self.base_dir = Path("/home/leopoldobassoconova/ia-scrapping-tesis")
        self.credentials_dir = self.base_dir / "credentials"
        self.service_account_path = self.credentials_dir / "service_account.json"
        self.env_file = self.base_dir / ".env"
        
    def check_vm_environment(self):
        """Verificar entorno de VM"""
        try:
            if not self.base_dir.exists():
                logger.error(f"❌ Directorio base no encontrado: {self.base_dir}")
                return False
            
            logger.info(f"✅ Entorno de VM verificado: {self.base_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando entorno: {e}")
            return False
    
    def create_service_account_instructions(self):
        """Mostrar instrucciones para crear cuenta de servicio"""
        print("\n🔧 CONFIGURACIÓN DE CUENTA DE SERVICIO")
        print("=" * 60)
        print("Para automatizar Google Drive en la VM, necesitas crear una cuenta de servicio:")
        print()
        print("1. Ve a Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        print("2. Selecciona tu proyecto: scjn-scraper-20250713")
        print()
        print("3. Ve a 'IAM y administración' > 'Cuentas de servicio'")
        print()
        print("4. Haz clic en 'Crear cuenta de servicio'")
        print("   - Nombre: scjn-drive-service")
        print("   - Descripción: Cuenta de servicio para subir PDFs de tesis")
        print()
        print("5. Asigna los siguientes roles:")
        print("   - Editor de Google Drive")
        print("   - Usuario de Google Drive")
        print()
        print("6. Haz clic en 'Crear y continuar'")
        print()
        print("7. En la pestaña 'Claves', haz clic en 'Agregar clave' > 'Crear nueva clave'")
        print("   - Tipo: JSON")
        print("   - Haz clic en 'Crear'")
        print()
        print("8. Se descargará un archivo JSON. Renómbralo a 'service_account.json'")
        print("   y súbelo a la VM usando:")
        print()
        print("   gcloud compute scp service_account.json scjn-scraper:/home/leopoldobassoconova/ia-scrapping-tesis/credentials/ --zone=us-central1-a")
        print()
        print("9. Comparte la carpeta de Google Drive con el email de la cuenta de servicio")
        print("   (aparece en el archivo JSON como 'client_email')")
        print()
        print("10. Obtén el ID de la carpeta de Google Drive y configúralo en .env")
        print()
        print("=" * 60)
    
    def setup_credentials_directory(self):
        """Configurar directorio de credenciales"""
        try:
            self.credentials_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directorio de credenciales creado: {self.credentials_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando directorio: {e}")
            return False
    
    def validate_service_account_file(self):
        """Validar archivo de cuenta de servicio"""
        try:
            if not self.service_account_path.exists():
                logger.error(f"❌ Archivo no encontrado: {self.service_account_path}")
                return False
            
            with open(self.service_account_path, 'r') as f:
                data = json.load(f)
            
            # Verificar campos requeridos
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in data:
                    logger.error(f"❌ Campo requerido faltante: {field}")
                    return False
            
            # Verificar tipo de cuenta de servicio
            if data.get('type') != 'service_account':
                logger.error("❌ El archivo no es una cuenta de servicio válida")
                return False
            
            logger.info(f"✅ Archivo de cuenta de servicio válido")
            logger.info(f"   Proyecto: {data.get('project_id')}")
            logger.info(f"   Email: {data.get('client_email')}")
            
            return True
            
        except json.JSONDecodeError:
            logger.error("❌ El archivo no es un JSON válido")
            return False
        except Exception as e:
            logger.error(f"❌ Error validando archivo: {e}")
            return False
    
    def setup_environment_variables(self):
        """Configurar variables de entorno"""
        try:
            # Leer archivo .env existente
            env_content = []
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    env_content = f.readlines()
            
            # Variables a configurar
            new_vars = {
                'GOOGLE_DRIVE_ENABLED': 'true',
                'GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH': 'credentials/service_account.json',
                'GOOGLE_DRIVE_FOLDER_ID': ''  # Se debe configurar manualmente
            }
            
            # Actualizar o agregar variables
            updated = False
            for var_name, var_value in new_vars.items():
                var_line = f"{var_name}={var_value}\n"
                
                # Buscar si ya existe
                found = False
                for i, line in enumerate(env_content):
                    if line.startswith(f"{var_name}="):
                        env_content[i] = var_line
                        found = True
                        updated = True
                        break
                
                if not found:
                    env_content.append(var_line)
                    updated = True
            
            # Escribir archivo actualizado
            if updated:
                with open(self.env_file, 'w') as f:
                    f.writelines(env_content)
                logger.info("✅ Variables de entorno actualizadas")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando variables: {e}")
            return False
    
    def test_google_drive_connection(self):
        """Probar conexión con Google Drive"""
        try:
            # Importar dependencias
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Crear credenciales
            credentials = service_account.Credentials.from_service_account_file(
                str(self.service_account_path),
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            # Construir servicio
            service = build('drive', 'v3', credentials=credentials)
            
            # Probar conexión
            about = service.about().get(fields="user").execute()
            user = about.get('user', {})
            
            logger.info(f"✅ Conexión exitosa con Google Drive")
            logger.info(f"   Usuario: {user.get('displayName', 'N/A')}")
            logger.info(f"   Email: {user.get('emailAddress', 'N/A')}")
            
            return True
            
        except ImportError:
            logger.error("❌ Dependencias de Google Drive no instaladas")
            logger.info("Ejecuta: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    def create_automation_script(self):
        """Crear script de automatización para VM"""
        script_content = '''#!/usr/bin/env python3
"""
Script de automatización de Google Drive para VM
Sube PDFs automáticamente durante el scraping
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gdrive_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def upload_pdf_to_drive(pdf_path: str, tesis_id: str):
    """Subir PDF a Google Drive"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        # Configuración
        service_account_path = "credentials/service_account.json"
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
        
        if not os.path.exists(service_account_path):
            logger.error("Archivo de cuenta de servicio no encontrado")
            return None
        
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF no encontrado: {pdf_path}")
            return None
        
        # Crear credenciales
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Construir servicio
        service = build('drive', 'v3', credentials=credentials)
        
        # Preparar archivo
        filename = f"tesis_{tesis_id}_{os.path.basename(pdf_path)}"
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }
        
        # Subir archivo
        media = MediaFileUpload(pdf_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        
        logger.info(f"✅ PDF subido: {filename} (ID: {file_id})")
        logger.info(f"   Enlace: {web_link}")
        
        return file_id
        
    except Exception as e:
        logger.error(f"❌ Error subiendo PDF: {e}")
        return None

def main():
    """Función principal"""
    logger.info("🚀 Iniciando automatización de Google Drive")
    
    # Verificar configuración
    if not os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true":
        logger.error("Google Drive no está habilitado")
        return False
    
    if not os.getenv("GOOGLE_DRIVE_FOLDER_ID"):
        logger.warning("GOOGLE_DRIVE_FOLDER_ID no configurado")
    
    logger.info("✅ Automatización configurada correctamente")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
        
        script_file = self.base_dir / "gdrive_automation_vm.py"
        with open(script_file, 'w') as f:
            f.write(script_content.strip())
        
        # Hacer ejecutable
        os.chmod(script_file, 0o755)
        
        logger.info(f"✅ Script de automatización creado: {script_file}")
        return True
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        print("\n🚀 CONFIGURACIÓN AUTOMÁTICA DE GOOGLE DRIVE PARA VM")
        print("=" * 60)
        
        # 1. Verificar entorno de VM
        if not self.check_vm_environment():
            return False
        
        # 2. Configurar directorio de credenciales
        if not self.setup_credentials_directory():
            return False
        
        # 3. Verificar si ya existe cuenta de servicio
        if self.service_account_path.exists():
            if self.validate_service_account_file():
                if self.test_google_drive_connection():
                    self.setup_environment_variables()
                    self.create_automation_script()
                    print("\n✅ Configuración completada exitosamente!")
                    print("   La cuenta de servicio ya está configurada y funcionando.")
                    return True
                else:
                    print("\n⚠️ La cuenta de servicio existe pero hay problemas de conexión.")
                    print("   Verifica que el archivo JSON sea correcto y que la carpeta de Drive")
                    print("   esté compartida con el email de la cuenta de servicio.")
                    return False
        
        # 4. Mostrar instrucciones si no existe
        self.create_service_account_instructions()
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Sigue las instrucciones arriba para crear la cuenta de servicio")
        print("2. Sube el archivo service_account.json a la VM usando gcloud compute scp")
        print("3. Ejecuta este script nuevamente para validar la configuración")
        print("4. Configura GOOGLE_DRIVE_FOLDER_ID en el archivo .env")
        print("5. Ejecuta: python gdrive_automation_vm.py")
        
        return False

def main():
    """Función principal"""
    setup = VMGoogleDriveSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 ¡Configuración completada!")
        print("El sistema ahora puede subir PDFs automáticamente a Google Drive.")
        print("Ejecuta: python gdrive_automation_vm.py para probar la automatización.")
    else:
        print("\n❌ Configuración incompleta")
        print("Sigue las instrucciones y ejecuta el script nuevamente.")

if __name__ == "__main__":
    main() 