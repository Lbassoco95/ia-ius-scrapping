#!/usr/bin/env python3
"""
Script para monitorear el progreso del scraping de producción
"""

import logging
import sys
import os
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.models import get_session, Tesis, ScrapingSession

def monitor_production():
    """Monitorear el progreso del scraping"""
    
    print("📊 === MONITOREO DE PRODUCCIÓN ===")
    
    try:
        session = get_session()
        
        # Obtener estadísticas generales
        total_tesis = session.query(Tesis).count()
        tesis_procesadas = session.query(Tesis).filter(Tesis.procesado == True).count()
        tesis_con_pdf = session.query(Tesis).filter(Tesis.pdf_url.isnot(None)).count()
        tesis_con_gdrive = session.query(Tesis).filter(Tesis.google_drive_link.isnot(None)).count()
        
        print(f"\n📈 Estadísticas Generales:")
        print(f"  📄 Total de tesis: {total_tesis}")
        print(f"  ✅ Tesis procesadas: {tesis_procesadas}")
        print(f"  📥 Tesis con PDF: {tesis_con_pdf}")
        print(f"  ☁️ Tesis en Google Drive: {tesis_con_gdrive}")
        
        # Obtener sesiones recientes
        sesiones_recientes = session.query(ScrapingSession).order_by(
            ScrapingSession.fecha_inicio.desc()
        ).limit(5).all()
        
        print(f"\n🕒 Sesiones Recientes:")
        for sesion in sesiones_recientes:
            estado = "🟢 Completada" if sesion.estado == "completed" else "🟡 En curso" if sesion.estado == "running" else "🔴 Error"
            print(f"  {estado} {sesion.session_id} - {sesion.fecha_inicio.strftime('%H:%M:%S')} - {sesion.archivos_descargados} archivos")
        
        # Obtener últimas tesis agregadas
        ultimas_tesis = session.query(Tesis).order_by(
            Tesis.fecha_descarga.desc()
        ).limit(10).all()
        
        print(f"\n📋 Últimas Tesis Agregadas:")
        for tesis in ultimas_tesis:
            estado = "✅" if tesis.procesado else "⏳"
            pdf_icon = "📥" if tesis.pdf_url else "❌"
            gdrive_icon = "☁️" if tesis.google_drive_link else "❌"
            print(f"  {estado} {tesis.scjn_id} - {tesis.titulo[:50]}... {pdf_icon} {gdrive_icon}")
        
        # Verificar archivos PDF descargados
        pdf_dir = "data/pdfs"
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
            print(f"\n📁 Archivos PDF en disco: {len(pdf_files)}")
            for pdf_file in pdf_files[:5]:  # Mostrar solo los primeros 5
                print(f"  📄 {pdf_file}")
            if len(pdf_files) > 5:
                print(f"  ... y {len(pdf_files) - 5} más")
        
        session.close()
        
        # Verificar logs
        log_file = "logs/production_scraping.log"
        if os.path.exists(log_file):
            print(f"\n📋 Últimas líneas del log:")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Últimas 10 líneas
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"  ❌ Error leyendo log: {e}")
        
        print(f"\n⏰ Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")

def main():
    """Función principal"""
    while True:
        try:
            monitor_production()
            print("\n" + "="*50)
            print("🔄 Actualizando en 30 segundos... (Ctrl+C para salir)")
            time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 Monitoreo detenido")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main() 