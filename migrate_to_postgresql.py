#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL para el sistema de scraping SCJN
"""

import sqlite3
import psycopg2
import json
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/migration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    def __init__(self, sqlite_db_path, pg_config):
        """
        Inicializar migrador
        
        Args:
            sqlite_db_path: Ruta al archivo SQLite
            pg_config: Diccionario con configuración de PostgreSQL
        """
        self.sqlite_db_path = sqlite_db_path
        self.pg_config = pg_config
        self.sqlite_conn = None
        self.pg_conn = None
        
    def connect_sqlite(self):
        """Conectar a SQLite"""
        try:
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info("✅ Conexión a SQLite establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a SQLite: {e}")
            return False
    
    def connect_postgresql(self):
        """Conectar a PostgreSQL"""
        try:
            self.pg_conn = psycopg2.connect(**self.pg_config)
            logger.info("✅ Conexión a PostgreSQL establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    def create_postgresql_schema(self):
        """Crear esquema en PostgreSQL"""
        schema_sql = """
        -- Tabla tesis
        CREATE TABLE IF NOT EXISTS tesis (
            id SERIAL PRIMARY KEY,
            scjn_id VARCHAR(50) NOT NULL UNIQUE,
            titulo TEXT,
            url VARCHAR(500),
            rubro TEXT,
            texto TEXT,
            precedente TEXT,
            pdf_url VARCHAR(500),
            google_drive_id VARCHAR(100),
            google_drive_link VARCHAR(500),
            metadata_json JSONB,
            fecha_descarga TIMESTAMP,
            html_content TEXT,
            procesado BOOLEAN DEFAULT FALSE,
            analizado BOOLEAN DEFAULT FALSE
        );
        
        -- Tabla scraping_sessions
        CREATE TABLE IF NOT EXISTS scraping_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL UNIQUE,
            fase VARCHAR(20) NOT NULL,
            fecha_inicio TIMESTAMP,
            fecha_fin TIMESTAMP,
            archivos_descargados INTEGER DEFAULT 0,
            duplicados_encontrados INTEGER DEFAULT 0,
            errores INTEGER DEFAULT 0,
            duracion_minutos INTEGER DEFAULT 0,
            estado VARCHAR(20)
        );
        
        -- Tabla scraping_stats
        CREATE TABLE IF NOT EXISTS scraping_stats (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP,
            total_descargado INTEGER DEFAULT 0,
            total_duplicados INTEGER DEFAULT 0,
            total_errores INTEGER DEFAULT 0,
            fase_actual VARCHAR(20),
            progreso_porcentual INTEGER DEFAULT 0
        );
        
        -- Índices
        CREATE INDEX IF NOT EXISTS idx_tesis_scjn_id ON tesis(scjn_id);
        CREATE INDEX IF NOT EXISTS idx_tesis_fecha_descarga ON tesis(fecha_descarga);
        CREATE INDEX IF NOT EXISTS idx_tesis_procesado ON tesis(procesado);
        CREATE INDEX IF NOT EXISTS idx_tesis_analizado ON tesis(analizado);
        CREATE INDEX IF NOT EXISTS idx_tesis_metadata ON tesis USING GIN(metadata_json);
        
        CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON scraping_sessions(session_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_fecha ON scraping_sessions(fecha_inicio);
        
        CREATE INDEX IF NOT EXISTS idx_stats_fecha ON scraping_stats(fecha);
        """
        
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute(schema_sql)
                self.pg_conn.commit()
                logger.info("✅ Esquema PostgreSQL creado exitosamente")
                return True
        except Exception as e:
            logger.error(f"❌ Error creando esquema PostgreSQL: {e}")
            return False
    
    def migrate_tesis_table(self):
        """Migrar tabla tesis"""
        try:
            # Obtener datos de SQLite
            cursor_sqlite = self.sqlite_conn.cursor()
            cursor_sqlite.execute("SELECT * FROM tesis")
            tesis_data = cursor_sqlite.fetchall()
            
            logger.info(f"📊 Migrando {len(tesis_data)} registros de tesis...")
            
            # Migrar a PostgreSQL
            cursor_pg = self.pg_conn.cursor()
            
            for i, row in enumerate(tesis_data):
                # Convertir metadata_json si es necesario
                metadata = row['metadata_json']
                if metadata and isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = None
                
                # Insertar en PostgreSQL
                cursor_pg.execute("""
                    INSERT INTO tesis (
                        scjn_id, titulo, url, rubro, texto, precedente,
                        pdf_url, google_drive_id, google_drive_link,
                        metadata_json, fecha_descarga, html_content,
                        procesado, analizado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (scjn_id) DO UPDATE SET
                        titulo = EXCLUDED.titulo,
                        url = EXCLUDED.url,
                        rubro = EXCLUDED.rubro,
                        texto = EXCLUDED.texto,
                        precedente = EXCLUDED.precedente,
                        pdf_url = EXCLUDED.pdf_url,
                        google_drive_id = EXCLUDED.google_drive_id,
                        google_drive_link = EXCLUDED.google_drive_link,
                        metadata_json = EXCLUDED.metadata_json,
                        fecha_descarga = EXCLUDED.fecha_descarga,
                        html_content = EXCLUDED.html_content,
                        procesado = EXCLUDED.procesado,
                        analizado = EXCLUDED.analizado
                """, (
                    row['scjn_id'], row['titulo'], row['url'], row['rubro'],
                    row['texto'], row['precedente'], row['pdf_url'],
                    row['google_drive_id'], row['google_drive_link'],
                    json.dumps(metadata) if metadata else None,
                    row['fecha_descarga'], row['html_content'],
                    row['procesado'], row['analizado']
                ))
                
                if (i + 1) % 10 == 0:
                    logger.info(f"   Progreso: {i + 1}/{len(tesis_data)} tesis migradas")
            
            self.pg_conn.commit()
            logger.info(f"✅ Tabla tesis migrada exitosamente: {len(tesis_data)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrando tabla tesis: {e}")
            return False
    
    def migrate_scraping_sessions_table(self):
        """Migrar tabla scraping_sessions"""
        try:
            cursor_sqlite = self.sqlite_conn.cursor()
            cursor_sqlite.execute("SELECT * FROM scraping_sessions")
            sessions_data = cursor_sqlite.fetchall()
            
            logger.info(f"📊 Migrando {len(sessions_data)} registros de sesiones...")
            
            cursor_pg = self.pg_conn.cursor()
            
            for row in sessions_data:
                cursor_pg.execute("""
                    INSERT INTO scraping_sessions (
                        session_id, fase, fecha_inicio, fecha_fin,
                        archivos_descargados, duplicados_encontrados,
                        errores, duracion_minutos, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id) DO UPDATE SET
                        fase = EXCLUDED.fase,
                        fecha_inicio = EXCLUDED.fecha_inicio,
                        fecha_fin = EXCLUDED.fecha_fin,
                        archivos_descargados = EXCLUDED.archivos_descargados,
                        duplicados_encontrados = EXCLUDED.duplicados_encontrados,
                        errores = EXCLUDED.errores,
                        duracion_minutos = EXCLUDED.duracion_minutos,
                        estado = EXCLUDED.estado
                """, (
                    row['session_id'], row['fase'], row['fecha_inicio'],
                    row['fecha_fin'], row['archivos_descargados'],
                    row['duplicados_encontrados'], row['errores'],
                    row['duracion_minutos'], row['estado']
                ))
            
            self.pg_conn.commit()
            logger.info(f"✅ Tabla scraping_sessions migrada exitosamente: {len(sessions_data)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrando tabla scraping_sessions: {e}")
            return False
    
    def migrate_scraping_stats_table(self):
        """Migrar tabla scraping_stats"""
        try:
            cursor_sqlite = self.sqlite_conn.cursor()
            cursor_sqlite.execute("SELECT * FROM scraping_stats")
            stats_data = cursor_sqlite.fetchall()
            
            logger.info(f"📊 Migrando {len(stats_data)} registros de estadísticas...")
            
            cursor_pg = self.pg_conn.cursor()
            
            for row in stats_data:
                cursor_pg.execute("""
                    INSERT INTO scraping_stats (
                        fecha, total_descargado, total_duplicados,
                        total_errores, fase_actual, progreso_porcentual
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['fecha'], row['total_descargado'],
                    row['total_duplicados'], row['total_errores'],
                    row['fase_actual'], row['progreso_porcentual']
                ))
            
            self.pg_conn.commit()
            logger.info(f"✅ Tabla scraping_stats migrada exitosamente: {len(stats_data)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrando tabla scraping_stats: {e}")
            return False
    
    def verify_migration(self):
        """Verificar que la migración fue exitosa"""
        try:
            # Contar registros en ambas bases de datos
            cursor_sqlite = self.sqlite_conn.cursor()
            cursor_pg = self.pg_conn.cursor()
            
            # Contar tesis
            cursor_sqlite.execute("SELECT COUNT(*) FROM tesis")
            sqlite_tesis_count = cursor_sqlite.fetchone()[0]
            
            cursor_pg.execute("SELECT COUNT(*) FROM tesis")
            pg_tesis_count = cursor_pg.fetchone()[0]
            
            # Contar sesiones
            cursor_sqlite.execute("SELECT COUNT(*) FROM scraping_sessions")
            sqlite_sessions_count = cursor_sqlite.fetchone()[0]
            
            cursor_pg.execute("SELECT COUNT(*) FROM scraping_sessions")
            pg_sessions_count = cursor_pg.fetchone()[0]
            
            # Contar estadísticas
            cursor_sqlite.execute("SELECT COUNT(*) FROM scraping_stats")
            sqlite_stats_count = cursor_sqlite.fetchone()[0]
            
            cursor_pg.execute("SELECT COUNT(*) FROM scraping_stats")
            pg_stats_count = cursor_pg.fetchone()[0]
            
            logger.info("📊 Verificación de migración:")
            logger.info(f"   Tesis: SQLite={sqlite_tesis_count}, PostgreSQL={pg_tesis_count}")
            logger.info(f"   Sesiones: SQLite={sqlite_sessions_count}, PostgreSQL={pg_sessions_count}")
            logger.info(f"   Estadísticas: SQLite={sqlite_stats_count}, PostgreSQL={pg_stats_count}")
            
            success = (
                sqlite_tesis_count == pg_tesis_count and
                sqlite_sessions_count == pg_sessions_count and
                sqlite_stats_count == pg_stats_count
            )
            
            if success:
                logger.info("✅ Verificación exitosa: todos los registros migrados correctamente")
            else:
                logger.warning("⚠️ Verificación fallida: algunos registros no coinciden")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error en verificación: {e}")
            return False
    
    def close_connections(self):
        """Cerrar conexiones"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.pg_conn:
            self.pg_conn.close()
        logger.info("🔌 Conexiones cerradas")
    
    def run_migration(self):
        """Ejecutar migración completa"""
        logger.info("🚀 Iniciando migración de SQLite a PostgreSQL")
        
        try:
            # Conectar a ambas bases de datos
            if not self.connect_sqlite():
                return False
            
            if not self.connect_postgresql():
                return False
            
            # Crear esquema en PostgreSQL
            if not self.create_postgresql_schema():
                return False
            
            # Migrar tablas
            if not self.migrate_tesis_table():
                return False
            
            if not self.migrate_scraping_sessions_table():
                return False
            
            if not self.migrate_scraping_stats_table():
                return False
            
            # Verificar migración
            if not self.verify_migration():
                return False
            
            logger.info("🎉 Migración completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en migración: {e}")
            return False
        finally:
            self.close_connections()

def main():
    """Función principal"""
    
    # Configuración de PostgreSQL (ajusta según tu configuración)
    pg_config = {
        'host': 'localhost',  # Cambiar por IP de Cloud SQL
        'port': 5432,
        'database': 'scjn_database',
        'user': 'scjn_user',
        'password': 'TU_PASSWORD_AQUI',  # Cambiar por tu password
        'sslmode': 'require'  # Para Cloud SQL
    }
    
    # Ruta a la base de datos SQLite
    sqlite_db_path = "data/scjn_database.db"
    
    # Verificar que existe el archivo SQLite
    if not Path(sqlite_db_path).exists():
        logger.error(f"❌ No se encontró el archivo SQLite: {sqlite_db_path}")
        return False
    
    # Crear migrador y ejecutar
    migrator = SQLiteToPostgreSQLMigrator(sqlite_db_path, pg_config)
    success = migrator.run_migration()
    
    if success:
        print("🎉 Migración completada exitosamente")
        print("📝 Recuerda actualizar la configuración de tu aplicación para usar PostgreSQL")
    else:
        print("❌ Error en la migración. Revisa los logs para más detalles")
    
    return success

if __name__ == "__main__":
    main() 