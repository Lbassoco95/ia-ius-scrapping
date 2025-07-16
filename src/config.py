#!/usr/bin/env python3
"""
Configuración optimizada del sistema de scraping SCJN
- Variables de entorno con validación
- Configuración centralizada y robusta
- URLs y endpoints optimizados
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import pytz
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ConfigurationError(Exception):
    """Excepción para errores de configuración"""
    pass

class Config:
    """Configuración principal optimizada del sistema"""
    
    # Directorios base
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    BACKUPS_DIR = DATA_DIR / "backups"
    PDFS_DIR = DATA_DIR / "pdfs"
    
    # URLs de SCJN - Optimizadas
    SCJN_BASE_URL = os.getenv("SCJN_BASE_URL", "https://sjf2.scjn.gob.mx")
    SEARCH_URL = os.getenv("SEARCH_URL", "https://sjf2.scjn.gob.mx/busqueda-principal-tesis")
    TESIS_URL = SEARCH_URL  # Alias para compatibilidad
    
    # Base de datos con validación
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/scjn_database.db")
    
    # Configuración de scraping optimizada
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    DEFAULT_WAIT_TIME = int(os.getenv("DEFAULT_WAIT_TIME", "5"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    MAX_DOCUMENTS_PER_RUN = int(os.getenv("MAX_DOCUMENTS_PER_RUN", "100"))
    
    # Límites de scraping mejorados
    MAX_FILES_PER_SESSION = int(os.getenv("MAX_FILES_PER_SESSION", "200"))
    MAX_HOURS_PER_SESSION = int(os.getenv("MAX_HOURS_PER_SESSION", "3"))
    ESTIMATED_FILES_PER_HOUR = int(os.getenv("ESTIMATED_FILES_PER_HOUR", "30"))
    
    # Configuración de fases optimizada
    INITIAL_PHASE_HOURS = int(os.getenv("INITIAL_PHASE_HOURS", "3"))
    INITIAL_PHASE_START_TIME = os.getenv("INITIAL_PHASE_START_TIME", "09:00")
    MAINTENANCE_PHASE_START_TIME = os.getenv("MAINTENANCE_PHASE_START_TIME", "08:00")
    
    # Configuración de archivos
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    SUPPORTED_FORMATS = ['.pdf', '.doc', '.docx']
    
    # Configuración de logging mejorada
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "scraper.log"
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Configuración de Selenium optimizada
    SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    SELENIUM_WINDOW_SIZE = os.getenv("SELENIUM_WINDOW_SIZE", "1920,1080")
    SELENIUM_USER_AGENT = os.getenv("SELENIUM_USER_AGENT", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    SELENIUM_IMPLICIT_WAIT = int(os.getenv("SELENIUM_IMPLICIT_WAIT", "10"))
    SELENIUM_PAGE_LOAD_TIMEOUT = int(os.getenv("SELENIUM_PAGE_LOAD_TIMEOUT", "30"))
    
    # Configuración de Google Drive robusta
    GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true"
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    GOOGLE_DRIVE_CREDENTIALS_PATH = Path(os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", 
        str(CREDENTIALS_DIR / "google_drive_credentials.json")))
    GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH = Path(os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH", 
        str(CREDENTIALS_DIR / "service_account.json")))
    
    # Configuración de OpenAI robusta
    OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    # Configuración de tiempo optimizada
    TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")
    DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
    
    # Configuración de monitoreo
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
    
    # Configuración de performance
    PARALLEL_DOWNLOADS = int(os.getenv("PARALLEL_DOWNLOADS", "3"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    @classmethod
    def get_timezone(cls):
        """Obtener zona horaria configurada"""
        try:
            return pytz.timezone(cls.TIMEZONE)
        except Exception:
            return pytz.timezone("UTC")
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios de forma robusta"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.CREDENTIALS_DIR,
            cls.PDFS_DIR,
            cls.BACKUPS_DIR
        ]
        
        created_dirs = []
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(directory))
            except Exception as e:
                raise ConfigurationError(f"No se pudo crear directorio {directory}: {e}")
        
        return created_dirs
    
    @classmethod
    def get_database_url(cls) -> str:
        """Obtener URL de base de datos validada"""
        if not cls.DATABASE_URL:
            raise ConfigurationError("DATABASE_URL no configurada")
        return cls.DATABASE_URL
    
    @classmethod
    def get_log_config(cls) -> Dict[str, Any]:
        """Obtener configuración de logging optimizada"""
        return {
            'level': cls.LOG_LEVEL,
            'format': cls.LOG_FORMAT,
            'file': str(cls.LOG_FILE),
            'max_size': cls.LOG_MAX_SIZE,
            'backup_count': cls.LOG_BACKUP_COUNT
        }
    
    @classmethod
    def get_selenium_config(cls) -> Dict[str, Any]:
        """Obtener configuración optimizada de Selenium"""
        return {
            'headless': cls.SELENIUM_HEADLESS,
            'window_size': cls.SELENIUM_WINDOW_SIZE,
            'user_agent': cls.SELENIUM_USER_AGENT,
            'timeout': cls.DEFAULT_TIMEOUT,
            'implicit_wait': cls.SELENIUM_IMPLICIT_WAIT,
            'page_load_timeout': cls.SELENIUM_PAGE_LOAD_TIMEOUT
        }
    
    @classmethod
    def get_google_drive_config(cls) -> Dict[str, Any]:
        """Obtener configuración validada de Google Drive"""
        if cls.GOOGLE_DRIVE_ENABLED:
            if not cls.GOOGLE_DRIVE_FOLDER_ID:
                raise ConfigurationError("Google Drive habilitado pero GOOGLE_DRIVE_FOLDER_ID no configurado")
            
            credentials_path = cls.GOOGLE_DRIVE_CREDENTIALS_PATH
            service_account_path = cls.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH
            
            if not credentials_path.exists() and not service_account_path.exists():
                raise ConfigurationError("Google Drive habilitado pero no se encontraron credenciales")
        
        return {
            'enabled': cls.GOOGLE_DRIVE_ENABLED,
            'folder_id': cls.GOOGLE_DRIVE_FOLDER_ID,
            'credentials_path': str(cls.GOOGLE_DRIVE_CREDENTIALS_PATH),
            'service_account_path': str(cls.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH)
        }
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """Obtener configuración validada de OpenAI"""
        if cls.OPENAI_ENABLED and not cls.OPENAI_API_KEY:
            raise ConfigurationError("OpenAI habilitado pero OPENAI_API_KEY no configurado")
        
        return {
            'enabled': cls.OPENAI_ENABLED,
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'max_tokens': cls.OPENAI_MAX_TOKENS,
            'temperature': cls.OPENAI_TEMPERATURE
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validar configuración completa del sistema"""
        try:
            # Crear directorios
            created_dirs = cls.create_directories()
            print(f"✅ Directorios creados/verificados: {len(created_dirs)}")
            
            # Verificar configuración básica
            if not cls.SCJN_BASE_URL:
                raise ConfigurationError("SCJN_BASE_URL no configurada")
            
            if not cls.SEARCH_URL:
                raise ConfigurationError("SEARCH_URL no configurada")
            
            # Validar configuraciones opcionales
            try:
                cls.get_google_drive_config()
            except ConfigurationError as e:
                print(f"⚠️ Google Drive: {e}")
            
            try:
                cls.get_openai_config()
            except ConfigurationError as e:
                print(f"⚠️ OpenAI: {e}")
            
            # Validar zona horaria
            try:
                cls.get_timezone()
            except Exception:
                print(f"⚠️ Zona horaria inválida: {cls.TIMEZONE}, usando UTC")
            
            print("✅ Configuración validada correctamente")
            return True
            
        except ConfigurationError as e:
            print(f"❌ Error de configuración: {e}")
            return False
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False
    
    @classmethod
    def validate(cls):
        """Alias para validate_config (retrocompatibilidad)"""
        return cls.validate_config()
    
    @classmethod
    def print_config(cls):
        """Imprimir configuración actual de forma detallada"""
        print("\n📋 CONFIGURACIÓN OPTIMIZADA DEL SISTEMA")
        print("=" * 50)
        print(f"📁 Directorio base: {cls.BASE_DIR}")
        print(f"🗄️ Base de datos: {cls.DATABASE_URL}")
        print(f"🌐 URL SCJN: {cls.SCJN_BASE_URL}")
        print(f"🔍 URL búsqueda: {cls.SEARCH_URL}")
        print(f"⏰ Timeout por defecto: {cls.DEFAULT_TIMEOUT}s")
        print(f"🔄 Máximo reintentos: {cls.MAX_RETRIES}")
        print(f"📊 Docs máximos por ejecución: {cls.MAX_DOCUMENTS_PER_RUN}")
        print(f"📁 Archivos máximos por sesión: {cls.MAX_FILES_PER_SESSION}")
        print(f"⏰ Horas máximas por sesión: {cls.MAX_HOURS_PER_SESSION}")
        print(f"🤖 Selenium headless: {cls.SELENIUM_HEADLESS}")
        print(f"📁 Google Drive: {'✅ Habilitado' if cls.GOOGLE_DRIVE_ENABLED else '❌ Deshabilitado'}")
        print(f"🧠 OpenAI: {'✅ Habilitado' if cls.OPENAI_ENABLED else '❌ Deshabilitado'}")
        print(f"📊 Monitoreo: {'✅ Habilitado' if cls.MONITORING_ENABLED else '❌ Deshabilitado'}")
        print(f"⚡ Descargas paralelas: {cls.PARALLEL_DOWNLOADS}")
        print(f"📦 Tamaño de lote: {cls.BATCH_SIZE}")
        print("=" * 50)

# Configuraciones específicas por entorno mejoradas
class DevelopmentConfig(Config):
    """Configuración optimizada para desarrollo"""
    LOG_LEVEL = "DEBUG"
    SELENIUM_HEADLESS = False
    MAX_DOCUMENTS_PER_RUN = 10
    PARALLEL_DOWNLOADS = 1

class ProductionConfig(Config):
    """Configuración optimizada para producción"""
    LOG_LEVEL = "INFO"
    SELENIUM_HEADLESS = True
    MAX_FILES_PER_SESSION = 150
    PARALLEL_DOWNLOADS = 2

class TestingConfig(Config):
    """Configuración optimizada para testing"""
    DATABASE_URL = f"sqlite:///{Config.DATA_DIR}/test_database.db"
    LOG_LEVEL = "DEBUG"
    MAX_FILES_PER_SESSION = 5
    MAX_DOCUMENTS_PER_RUN = 3
    PARALLEL_DOWNLOADS = 1

def get_config(env: str = None) -> Config:
    """Obtener configuración optimizada según entorno"""
    if not env:
        env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    
    # Validar configuración al cargarla
    if not config_class.validate_config():
        raise ConfigurationError(f"Configuración inválida para entorno: {env}")
    
    return config_class 