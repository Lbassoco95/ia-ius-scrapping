#!/usr/bin/env python3
"""
Configuración del sistema de scraping SCJN
- Variables de entorno
- Configuración de base de datos
- URLs y endpoints
"""

import os
from pathlib import Path
from typing import Optional
import pytz

class Config:
    """Configuración principal del sistema"""
    
    # Directorios base
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    
    # URLs de SCJN
    SCJN_BASE_URL = "https://sjf2.scjn.gob.mx"
    SEARCH_URL = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
    TESIS_URL = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
    
    # Base de datos
    DATABASE_URL = "sqlite:///data/scjn_database.db"
    
    # Configuración de scraping
    DEFAULT_TIMEOUT = 30
    DEFAULT_WAIT_TIME = 5
    MAX_RETRIES = 3
    MAX_DOCUMENTS_PER_RUN = 100  # Valor por defecto para el scraping
    
    # Límites de scraping
    MAX_FILES_PER_SESSION = 200
    MAX_HOURS_PER_SESSION = 3
    ESTIMATED_FILES_PER_HOUR = 30
    
    # Configuración de fases
    INITIAL_PHASE_HOURS = 3
    INITIAL_PHASE_START_TIME = "09:00"
    MAINTENANCE_PHASE_START_TIME = "08:00"
    
    # Configuración de archivos
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_FORMATS = ['.pdf', '.doc', '.docx']
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/auto_scraper.log"
    
    # Configuración de Selenium
    SELENIUM_HEADLESS = True
    SELENIUM_WINDOW_SIZE = "1920,1080"
    SELENIUM_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # Configuración de Google Drive (opcional)
    GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true"
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "credentials/google_drive_credentials.json")
    GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH", "credentials/service_account.json")
    
    # Configuración de OpenAI (opcional)
    OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    DOWNLOAD_TIMEOUT = 30  # Timeout para descargas en segundos
    
    TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")
    @classmethod
    def get_timezone(cls):
        return pytz.timezone(cls.TIMEZONE)
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.CREDENTIALS_DIR,
            cls.DATA_DIR / "pdfs",
            cls.DATA_DIR / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_database_url(cls) -> str:
        """Obtener URL de base de datos"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_log_config(cls) -> dict:
        """Obtener configuración de logging"""
        return {
            'level': cls.LOG_LEVEL,
            'format': cls.LOG_FORMAT,
            'file': cls.LOG_FILE
        }
    
    @classmethod
    def get_selenium_config(cls) -> dict:
        """Obtener configuración de Selenium"""
        return {
            'headless': cls.SELENIUM_HEADLESS,
            'window_size': cls.SELENIUM_WINDOW_SIZE,
            'user_agent': cls.SELENIUM_USER_AGENT,
            'timeout': cls.DEFAULT_TIMEOUT
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validar configuración del sistema"""
        try:
            # Crear directorios
            cls.create_directories()
            
            # Verificar configuración básica
            if not cls.SCJN_BASE_URL:
                print("❌ URL base de SCJN no configurada")
                return False
            
            if not cls.SEARCH_URL:
                print("❌ URL de búsqueda no configurada")
                return False
            
            # Verificar configuración opcional
            if cls.GOOGLE_DRIVE_ENABLED and not cls.GOOGLE_DRIVE_FOLDER_ID:
                print("⚠️ Google Drive habilitado pero sin folder ID")
            
            if cls.OPENAI_ENABLED and not cls.OPENAI_API_KEY:
                print("⚠️ OpenAI habilitado pero sin API key")
            
            print("✅ Configuración válida")
            return True
            
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False
    
    @classmethod
    def validate(cls):
        """Alias para validate_config (retrocompatibilidad)"""
        return cls.validate_config()
    
    @classmethod
    def print_config(cls):
        """Imprimir configuración actual"""
        print("\n📋 CONFIGURACIÓN DEL SISTEMA")
        print("=" * 40)
        print(f"📁 Directorio base: {cls.BASE_DIR}")
        print(f"🗄️ Base de datos: {cls.DATABASE_URL}")
        print(f"🌐 URL SCJN: {cls.SCJN_BASE_URL}")
        print(f"🔍 URL búsqueda: {cls.SEARCH_URL}")
        print(f"⏰ Horas fase inicial: {cls.INITIAL_PHASE_HOURS}")
        print(f"📊 Archivos máximos por sesión: {cls.MAX_FILES_PER_SESSION}")
        print(f"🤖 Selenium headless: {cls.SELENIUM_HEADLESS}")
        print(f"📁 Google Drive: {'✅ Habilitado' if cls.GOOGLE_DRIVE_ENABLED else '❌ Deshabilitado'}")
        print(f"🧠 OpenAI: {'✅ Habilitado' if cls.OPENAI_ENABLED else '❌ Deshabilitado'}")
        print("=" * 40)

# Configuración de desarrollo
class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    LOG_LEVEL = "DEBUG"
    SELENIUM_HEADLESS = False  # Ver navegador en desarrollo

# Configuración de producción
class ProductionConfig(Config):
    """Configuración para producción"""
    LOG_LEVEL = "INFO"
    SELENIUM_HEADLESS = True
    MAX_FILES_PER_SESSION = 100  # Más conservador en producción

# Configuración de testing
class TestingConfig(Config):
    """Configuración para testing"""
    DATABASE_URL = "sqlite:///data/test_database.db"
    LOG_LEVEL = "DEBUG"
    MAX_FILES_PER_SESSION = 5

# Función para obtener configuración según entorno
def get_config(env: str = None) -> Config:
    """Obtener configuración según entorno"""
    if not env:
        env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig) 