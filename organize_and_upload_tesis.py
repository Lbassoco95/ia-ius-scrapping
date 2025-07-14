#!/usr/bin/env python3
"""
Script para organizar y subir tesis a Google Drive con estructura de carpetas
basada en el análisis de la información
"""

import sys
import os
import logging
import re
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.models import get_session, Tesis
from src.storage.google_drive import GoogleDriveManager
from src.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesisOrganizer:
    """Organizador de tesis con estructura de carpetas automática"""
    
    def __init__(self):
        self.drive_manager = GoogleDriveManager()
        self.drive_manager.authenticate()  # Forzar autenticación al inicializar
        self.folder_cache = {}  # Cache de carpetas creadas
        
    def analyze_tesis_info(self, tesis_data):
        """Analizar información de la tesis para determinar categorías"""
        categories = {
            'materia': 'Sin clasificar',
            'epoca': 'Sin clasificar', 
            'sala': 'Sin clasificar',
            'tipo': 'Tesis'
        }
        
        # Extraer información del título y texto
        title = tesis_data.get('titulo', '').upper()
        text = tesis_data.get('texto', '').upper()
        
        # Análisis de materia
        materias = {
            'CONSTITUCIONAL': 'Derecho Constitucional',
            'CIVIL': 'Derecho Civil',
            'PENAL': 'Derecho Penal',
            'ADMINISTRATIVO': 'Derecho Administrativo',
            'LABORAL': 'Derecho Laboral',
            'MERCANTIL': 'Derecho Mercantil',
            'FISCAL': 'Derecho Fiscal',
            'PROCESAL': 'Derecho Procesal',
            'AMPARO': 'Amparo',
            'DERECHOS HUMANOS': 'Derechos Humanos'
        }
        
        for keyword, materia in materias.items():
            if keyword in title or keyword in text:
                categories['materia'] = materia
                break
        
        # Análisis de época
        epocas = {
            '11A': '11a. Época',
            '10A': '10a. Época', 
            '9A': '9a. Época',
            '8A': '8a. Época',
            '7A': '7a. Época'
        }
        
        for keyword, epoca in epocas.items():
            if keyword in title or keyword in text:
                categories['epoca'] = epoca
                break
        
        # Análisis de sala
        salas = {
            'PLENO': 'Pleno',
            '1A. SALA': 'Primera Sala',
            '2A. SALA': 'Segunda Sala',
            'PRIMERA SALA': 'Primera Sala',
            'SEGUNDA SALA': 'Segunda Sala'
        }
        
        for keyword, sala in salas.items():
            if keyword in title or keyword in text:
                categories['sala'] = sala
                break
        
        return categories
    
    def create_folder_structure(self, categories):
        """Crear estructura de carpetas en Google Drive"""
        try:
            from src.config import Config
            # Estructura: Materia/Época/Sala
            unidad_compartida_id = Config.GOOGLE_DRIVE_FOLDER_ID
            materia_folder = self.get_or_create_folder(categories['materia'], parent_id=unidad_compartida_id)
            if not materia_folder:
                return None
            epoca_folder = self.get_or_create_folder(categories['epoca'], parent_id=materia_folder)
            if not epoca_folder:
                return materia_folder
            sala_folder = self.get_or_create_folder(categories['sala'], parent_id=epoca_folder)
            if not sala_folder:
                return epoca_folder
            return sala_folder
        except Exception as e:
            logger.error(f"❌ Error creando estructura de carpetas: {e}")
            return None
    
    def get_or_create_folder(self, folder_name, parent_id=None):
        """Obtener o crear carpeta en Google Drive"""
        try:
            # Verificar cache
            cache_key = f"{parent_id}_{folder_name}"
            if cache_key in self.folder_cache:
                return self.folder_cache[cache_key]
            
            # Verificar que el servicio esté disponible
            if not self.drive_manager.service:
                logger.error("❌ Servicio de Google Drive no disponible")
                return None
            
            # Buscar carpeta existente
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            files = self.drive_manager.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            if files.get('files'):
                folder_id = files['files'][0]['id']
                self.folder_cache[cache_key] = folder_id
                logger.info(f"✅ Carpeta encontrada: {folder_name}")
                return folder_id
            
            # Crear nueva carpeta
            if parent_id:
                folder_id = self.drive_manager.create_folder(folder_name, parent_id)
            else:
                folder_id = self.drive_manager.create_folder(folder_name)
                
            if folder_id:
                self.folder_cache[cache_key] = folder_id
                logger.info(f"✅ Carpeta creada: {folder_name}")
                return folder_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error con carpeta {folder_name}: {e}")
            return None
    
    def upload_tesis_with_organization(self, tesis_data, pdf_path):
        """Subir tesis organizada a Google Drive"""
        try:
            # Analizar información de la tesis
            categories = self.analyze_tesis_info(tesis_data)
            logger.info(f"📊 Categorías detectadas: {categories}")
            
            # Crear estructura de carpetas
            target_folder_id = self.create_folder_structure(categories)
            if not target_folder_id:
                logger.error("❌ No se pudo crear estructura de carpetas")
                return None
            
            # Crear nombre descriptivo del archivo
            filename = f"Tesis_{tesis_data['scjn_id']}_{categories['materia'].replace(' ', '_')}.pdf"
            
            # Subir archivo a la carpeta correspondiente
            result = self.drive_manager.upload_file(pdf_path, filename, target_folder_id)
            
            if result:
                file_id, web_link = result
                logger.info(f"✅ Tesis subida exitosamente")
                logger.info(f"📁 Ubicación: {categories['materia']}/{categories['epoca']}/{categories['sala']}")
                logger.info(f"🔗 Enlace: {web_link}")
                return (file_id, web_link)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error subiendo tesis organizada: {e}")
            return None

def complete_tesis_with_organization():
    """Completar proceso de tesis con organización automática"""
    
    logger.info("🚀 INICIANDO PROCESO CON ORGANIZACIÓN AUTOMÁTICA")
    logger.info("="*60)
    
    # Configurar variables de entorno
    os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
    os.environ['GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH'] = 'credentials/service_account.json'
    os.environ['GOOGLE_DRIVE_FOLDER_ID'] = '1IPkvCqNToQCmeF4J2mqDxDVbFsTGS1Bb'  # Carpeta real encontrada
    
    # Verificar PDF
    pdf_path = "data/pdfs/tesis_2030758.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF no encontrado: {pdf_path}")
        return False
    
    logger.info(f"✅ PDF encontrado: {pdf_path}")
    
    # Obtener datos de la tesis
    session = get_session()
    try:
        # Buscar por el scjn_id correcto
        tesis = session.query(Tesis).filter_by(scjn_id="2030758").first()
        if not tesis:
            logger.error("❌ Tesis no encontrada en la base de datos con scjn_id=2030758")
            return False
        
        # Solo actualizar los campos de Google Drive y pdf_url
        tesis.pdf_url = "https://sjf2.scjn.gob.mx/detalle/tesis/2030758"
        
        # Crear organizador
        organizer = TesisOrganizer()
        
        # Preparar datos de tesis
        tesis_data = {
            'scjn_id': tesis.scjn_id,
            'titulo': tesis.titulo,
            'texto': tesis.texto,
            'rubro': tesis.rubro
        }
        
        # Subir con organización
        result = organizer.upload_tesis_with_organization(tesis_data, pdf_path)
        
        if result:
            file_id, web_link = result
            tesis.google_drive_id = file_id
            tesis.google_drive_link = web_link
            
            # Guardar en base de datos
            session.commit()
            
            logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
            logger.info("✅ PDF descargado y subido a Google Drive")
            logger.info("✅ Organización automática aplicada")
            logger.info("✅ Base de datos actualizada")
            
            return True
        else:
            logger.error("❌ Error en el proceso de subida")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en el proceso: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Función principal"""
    success = complete_tesis_with_organization()
    
    if success:
        logger.info("🎉 ¡Tesis procesada y organizada exitosamente!")
    else:
        logger.error("❌ Error en el proceso")

if __name__ == "__main__":
    main() 