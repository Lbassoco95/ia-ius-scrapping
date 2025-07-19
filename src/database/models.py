#!/usr/bin/env python3
"""
Modelos de base de datos para el sistema de scraping SCJN
- Tabla de tesis
- Configuración de SQLAlchemy
- Funciones de utilidad
"""

import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Configuración de base de datos
DATABASE_URL = "sqlite:///data/scjn_database.db"

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug
    connect_args={"check_same_thread": False}  # Para SQLite
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

class Tesis(Base):
    """Modelo para almacenar tesis y jurisprudencia"""
    
    __tablename__ = "tesis"
    
    id = Column(Integer, primary_key=True, index=True)
    scjn_id = Column(String(50), unique=True, index=True, nullable=False)
    titulo = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    rubro = Column(Text, nullable=True)
    texto = Column(Text, nullable=True)
    precedente = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    google_drive_id = Column(String(100), nullable=True)  # ID de Google Drive
    google_drive_link = Column(String(500), nullable=True)  # Enlace web de Google Drive
    metadata_json = Column(JSON, nullable=True)
    fecha_descarga = Column(DateTime, default=datetime.now)
    html_content = Column(Text, nullable=True)
    procesado = Column(Boolean, default=False)
    analizado = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Tesis(scjn_id='{self.scjn_id}', titulo='{self.titulo[:50]}...')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'scjn_id': self.scjn_id,
            'titulo': self.titulo,
            'url': self.url,
            'rubro': self.rubro,
            'texto': self.texto,
            'precedente': self.precedente,
            'pdf_url': self.pdf_url,
            'google_drive_id': self.google_drive_id,
            'google_drive_link': self.google_drive_link,
            'metadata': self.metadata_json,
            'fecha_descarga': self.fecha_descarga.isoformat() if self.fecha_descarga else None,
            'html_content': self.html_content,
            'procesado': self.procesado,
            'analizado': self.analizado
        }

class ScrapingSession(Base):
    """Modelo para registrar sesiones de scraping"""
    
    __tablename__ = "scraping_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    fase = Column(String(20), nullable=False)  # 'initial' o 'maintenance'
    fecha_inicio = Column(DateTime, default=datetime.now)
    fecha_fin = Column(DateTime, nullable=True)
    archivos_descargados = Column(Integer, default=0)
    duplicados_encontrados = Column(Integer, default=0)
    errores = Column(Integer, default=0)
    duracion_minutos = Column(Integer, nullable=True)
    estado = Column(String(20), default='running')  # 'running', 'completed', 'error'
    
    def __repr__(self):
        return f"<ScrapingSession(session_id='{self.session_id}', fase='{self.fase}')>"

class ScrapingStats(Base):
    """Modelo para estadísticas de scraping"""
    
    __tablename__ = "scraping_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now, index=True)
    total_descargado = Column(Integer, default=0)
    total_duplicados = Column(Integer, default=0)
    total_errores = Column(Integer, default=0)
    fase_actual = Column(String(20), nullable=True)
    progreso_porcentual = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<ScrapingStats(fecha='{self.fecha}', total='{self.total_descargado}')>"

def get_session() -> Session:
    """Obtener sesión de base de datos"""
    return SessionLocal()

def create_tables():
    """Crear todas las tablas"""
    try:
        # Crear directorio data si no existe
        os.makedirs("data", exist_ok=True)
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas correctamente")
        
        # Crear índices adicionales
        create_indexes()
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise

def create_database():
    """Alias para crear todas las tablas (retrocompatibilidad)"""
    return create_tables()

def create_indexes():
    """Crear índices adicionales para optimización"""
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            # Índices para búsquedas frecuentes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tesis_fecha_descarga ON tesis(fecha_descarga)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tesis_procesado ON tesis(procesado)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tesis_analizado ON tesis(analizado)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sessions_fecha ON scraping_sessions(fecha_inicio)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stats_fecha ON scraping_stats(fecha)"))
            conn.commit()
            
        logger.info("✅ Índices creados correctamente")
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creando índices: {e}")

def check_database_health():
    """Verificar salud de la base de datos"""
    try:
        session = get_session()
        
        # Verificar conexión
        from sqlalchemy import text
        session.execute(text("SELECT 1"))
        
        # Contar registros
        total_tesis = session.query(Tesis).count()
        total_sessions = session.query(ScrapingSession).count()
        total_stats = session.query(ScrapingStats).count()
        
        session.close()
        
        return {
            'status': 'healthy',
            'total_tesis': total_tesis,
            'total_sessions': total_sessions,
            'total_stats': total_stats
        }
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error verificando base de datos: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def backup_database():
    """Crear backup de la base de datos"""
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"data/backup_scjn_database_{timestamp}.db"
        
        shutil.copy2("data/scjn_database.db", backup_path)
        logger.info(f"✅ Backup creado: {backup_path}")
        
        return backup_path
        
    except Exception as e:
        logger.error(f"❌ Error creando backup: {e}")
        return None

def cleanup_old_data(days_to_keep: int = 30):
    """Limpiar datos antiguos"""
    try:
        session = get_session()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Limpiar sesiones antiguas
        old_sessions = session.query(ScrapingSession).filter(
            ScrapingSession.fecha_inicio < cutoff_date
        ).delete()
        
        # Limpiar estadísticas antiguas
        old_stats = session.query(ScrapingStats).filter(
            ScrapingStats.fecha < cutoff_date
        ).delete()
        
        session.commit()
        session.close()
        
        logger.info(f"✅ Limpieza completada: {old_sessions} sesiones, {old_stats} estadísticas")
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error en limpieza: {e}")

def get_database_info():
    """Obtener información de la base de datos"""
    try:
        session = get_session()
        
        # Estadísticas generales
        total_tesis = session.query(Tesis).count()
        tesis_procesadas = session.query(Tesis).filter(Tesis.procesado == True).count()
        tesis_analizadas = session.query(Tesis).filter(Tesis.analizado == True).count()
        
        # Última descarga
        ultima_descarga = session.query(Tesis).order_by(Tesis.fecha_descarga.desc()).first()
        
        # Sesiones recientes
        sesiones_recientes = session.query(ScrapingSession).order_by(
            ScrapingSession.fecha_inicio.desc()
        ).limit(5).all()
        
        session.close()
        
        return {
            'total_tesis': total_tesis,
            'tesis_procesadas': tesis_procesadas,
            'tesis_analizadas': tesis_analizadas,
            'ultima_descarga': ultima_descarga.fecha_descarga if ultima_descarga else None,
            'sesiones_recientes': [
                {
                    'session_id': s.session_id,
                    'fase': s.fase,
                    'fecha_inicio': s.fecha_inicio,
                    'archivos_descargados': s.archivos_descargados,
                    'estado': s.estado
                }
                for s in sesiones_recientes
            ]
        }
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error obteniendo información: {e}")
        return None 