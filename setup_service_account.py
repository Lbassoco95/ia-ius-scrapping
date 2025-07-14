#!/usr/bin/env python3
"""
Script para configurar cuenta de servicio de Google Drive
Permite automatización completa sin intervención manual
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceAccountSetup:
    """Configurador de cuenta de servicio para Google Drive"""
    
    def __init__(self):
        self.credentials_dir = Path("credentials")
        self.service_account_path = self.credentials_dir / "service_account.json"
        self.project_id = "scjn-scraper-20250713"  # Tu proyecto de Google Cloud
        
    def create_credentials_directory(self):
        """Crear directorio de credenciales"""
        try:
            self.credentials_dir.mkdir(exist_ok=True)
            logger.info(f"✅ Directorio de credenciales creado: {self.credentials_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando directorio de credenciales: {e}")
            return False
    
    def check_existing_service_account(self) -> bool:
        """Verificar si ya existe archivo de cuenta de servicio"""
        if self.service_account_path.exists():
            logger.info(f"✅ Archivo de cuenta de servicio encontrado: {self.service_account_path}")
            return True
        return False
    
    def create_service_account_instructions(self):
        """Mostrar instrucciones para crear cuenta de servicio"""
        print("\n🔧 CONFIGURACIÓN DE CUENTA DE SERVICIO")
        print("=" * 50)
        print("Para automatizar completamente Google Drive, necesitas crear una cuenta de servicio:")
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
        print("   y súbelo a la VM en: /home/leopoldobassoconova/ia-scrapping-tesis/credentials/")
        print()
        print("9. Comparte la carpeta de Google Drive con el email de la cuenta de servicio")
        print("   (aparece en el archivo JSON como 'client_email')")
        print()
        print("=" * 50)
    
    def validate_service_account_file(self) -> bool:
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
    
    def test_google_drive_connection(self) -> bool:
        """Probar conexión con Google Drive"""
        try:
            # Importar aquí para evitar errores si no están instaladas las dependencias
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
            logger.info("   Ejecuta: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    def setup_environment_variables(self):
        """Configurar variables de entorno"""
        env_file = Path(".env")
        env_content = []
        
        # Leer archivo .env existente si existe
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Variables a agregar/actualizar
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
            with open(env_file, 'w') as f:
                f.writelines(env_content)
            logger.info("✅ Variables de entorno actualizadas en .env")
        else:
            logger.info("ℹ️ Variables de entorno ya configuradas")
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        print("\n🚀 CONFIGURACIÓN AUTOMÁTICA DE CUENTA DE SERVICIO")
        print("=" * 60)
        
        # 1. Crear directorio de credenciales
        if not self.create_credentials_directory():
            return False
        
        # 2. Verificar si ya existe cuenta de servicio
        if self.check_existing_service_account():
            if self.validate_service_account_file():
                if self.test_google_drive_connection():
                    self.setup_environment_variables()
                    print("\n✅ Configuración completada exitosamente!")
                    print("   La cuenta de servicio ya está configurada y funcionando.")
                    return True
                else:
                    print("\n⚠️ La cuenta de servicio existe pero hay problemas de conexión.")
                    print("   Verifica que el archivo JSON sea correcto y que la carpeta de Drive")
                    print("   esté compartida con el email de la cuenta de servicio.")
                    return False
        
        # 3. Mostrar instrucciones si no existe
        self.create_service_account_instructions()
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Sigue las instrucciones arriba para crear la cuenta de servicio")
        print("2. Sube el archivo service_account.json a la VM")
        print("3. Ejecuta este script nuevamente para validar la configuración")
        print("4. Configura GOOGLE_DRIVE_FOLDER_ID en el archivo .env")
        
        return False

def main():
    """Función principal"""
    setup = ServiceAccountSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 ¡Configuración completada!")
        print("El sistema ahora puede subir PDFs automáticamente a Google Drive.")
    else:
        print("\n❌ Configuración incompleta")
        print("Sigue las instrucciones y ejecuta el script nuevamente.")

if __name__ == "__main__":
    main() 