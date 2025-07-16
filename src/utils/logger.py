#!/usr/bin/env python3
"""
Sistema de logging optimizado para el scraper SCJN
- Rotación automática de archivos
- Múltiples handlers (console, file, error file)
- Formateo mejorado con contexto
- Monitoreo de performance
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import functools
import time
import sys

from src.config import Config

class ScraperFormatter(logging.Formatter):
    """Formateador personalizado para el scraper"""
    
    # Colores para consola
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, use_colors=False, include_context=True):
        super().__init__()
        self.use_colors = use_colors
        self.include_context = include_context
    
    def format(self, record):
        # Formato base
        if self.include_context:
            format_str = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        else:
            format_str = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Aplicar colores si está habilitado
        if self.use_colors and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            format_str = f"{color}{format_str}{self.COLORS['RESET']}"
        
        formatter = logging.Formatter(format_str, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

class PerformanceLogger:
    """Logger para métricas de performance"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Iniciar timer para una operación"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str, context: Dict[str, Any] = None):
        """Finalizar timer y loggear duración"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            context_str = f" - {context}" if context else ""
            self.logger.info(f"⏱️ {operation}: {duration:.2f}s{context_str}")
            del self.start_times[operation]
            return duration
        return None

def performance_monitor(operation_name: str = None):
    """Decorador para monitorear performance de funciones"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            perf_logger = PerformanceLogger()
            
            perf_logger.start_timer(op_name)
            try:
                result = func(*args, **kwargs)
                perf_logger.end_timer(op_name, {"status": "success"})
                return result
            except Exception as e:
                perf_logger.end_timer(op_name, {"status": "error", "error": str(e)})
                raise
        return wrapper
    return decorator

class ScraperLogger:
    """Clase principal para configurar logging del scraper"""
    
    def __init__(self, name: str = "scraper", config: Optional[Config] = None):
        self.name = name
        self.config = config or Config
        self.logger = None
        self.performance_logger = PerformanceLogger(f"{name}.performance")
        
    def setup_logging(self) -> logging.Logger:
        """Configurar sistema de logging completo"""
        
        # Crear logger principal
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Crear directorios de logs
        self.config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 1. Handler para consola con colores
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ScraperFormatter(use_colors=True, include_context=False)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. Handler para archivo general con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.config.LOG_FILE,
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=self.config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = ScraperFormatter(use_colors=False, include_context=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 3. Handler separado para errores
        error_handler = logging.handlers.RotatingFileHandler(
            filename=self.config.LOGS_DIR / "errors.log",
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. Handler para performance
        perf_handler = logging.handlers.RotatingFileHandler(
            filename=self.config.LOGS_DIR / "performance.log",
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = ScraperFormatter(use_colors=False, include_context=False)
        perf_handler.setFormatter(perf_formatter)
        self.performance_logger.logger.addHandler(perf_handler)
        
        # Log inicial
        self.logger.info(f"🚀 Sistema de logging inicializado - Nivel: {self.config.LOG_LEVEL}")
        self.logger.debug(f"📁 Archivos de log en: {self.config.LOGS_DIR}")
        
        return self.logger
    
    def get_logger(self) -> logging.Logger:
        """Obtener logger configurado"""
        if not self.logger:
            self.setup_logging()
        return self.logger
    
    def get_performance_logger(self) -> PerformanceLogger:
        """Obtener logger de performance"""
        return self.performance_logger
    
    def log_system_info(self):
        """Loggear información del sistema"""
        self.logger.info("=" * 60)
        self.logger.info("🖥️ INFORMACIÓN DEL SISTEMA")
        self.logger.info("=" * 60)
        self.logger.info(f"🐍 Python: {sys.version.split()[0]}")
        self.logger.info(f"📁 Directorio de trabajo: {os.getcwd()}")
        self.logger.info(f"⏰ Zona horaria: {self.config.TIMEZONE}")
        self.logger.info(f"🗄️ Base de datos: {self.config.DATABASE_URL}")
        self.logger.info(f"📁 Google Drive: {'✅' if self.config.GOOGLE_DRIVE_ENABLED else '❌'}")
        self.logger.info(f"🧠 OpenAI: {'✅' if self.config.OPENAI_ENABLED else '❌'}")
        self.logger.info("=" * 60)
    
    def log_scraping_session_start(self, session_info: Dict[str, Any]):
        """Loggear inicio de sesión de scraping"""
        self.logger.info("🚀 INICIANDO SESIÓN DE SCRAPING")
        self.logger.info("-" * 40)
        for key, value in session_info.items():
            self.logger.info(f"   {key}: {value}")
        self.logger.info("-" * 40)
    
    def log_scraping_session_end(self, session_stats: Dict[str, Any]):
        """Loggear finalización de sesión de scraping"""
        self.logger.info("✅ FINALIZANDO SESIÓN DE SCRAPING")
        self.logger.info("-" * 40)
        for key, value in session_stats.items():
            self.logger.info(f"   {key}: {value}")
        self.logger.info("-" * 40)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Loggear error con contexto adicional"""
        self.logger.error(f"❌ Error: {type(error).__name__}: {str(error)}")
        if context:
            self.logger.error("📋 Contexto del error:")
            for key, value in context.items():
                self.logger.error(f"   {key}: {value}")
    
    def create_child_logger(self, name: str) -> logging.Logger:
        """Crear logger hijo con la misma configuración"""
        child_name = f"{self.name}.{name}"
        return logging.getLogger(child_name)

# Instancia global del logger
_scraper_logger = None

def get_logger(name: str = "scraper", config: Optional[Config] = None) -> logging.Logger:
    """Obtener logger configurado (función global)"""
    global _scraper_logger
    
    if not _scraper_logger:
        _scraper_logger = ScraperLogger(name, config)
        _scraper_logger.setup_logging()
    
    return _scraper_logger.get_logger()

def get_performance_logger() -> PerformanceLogger:
    """Obtener logger de performance (función global)"""
    global _scraper_logger
    
    if not _scraper_logger:
        _scraper_logger = ScraperLogger()
        _scraper_logger.setup_logging()
    
    return _scraper_logger.get_performance_logger()

def setup_logging(name: str = "scraper", config: Optional[Config] = None) -> logging.Logger:
    """Configurar logging del sistema (función global)"""
    global _scraper_logger
    
    _scraper_logger = ScraperLogger(name, config)
    logger = _scraper_logger.setup_logging()
    _scraper_logger.log_system_info()
    
    return logger

# Funciones de conveniencia
def log_info(message: str):
    """Log de info rápido"""
    get_logger().info(message)

def log_error(message: str):
    """Log de error rápido"""
    get_logger().error(message)

def log_warning(message: str):
    """Log de warning rápido"""
    get_logger().warning(message)

def log_debug(message: str):
    """Log de debug rápido"""
    get_logger().debug(message)