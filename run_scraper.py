#!/usr/bin/env python3
"""
Script principal para ejecutar el scraper SCJN
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, 'src')

def main():
    print("🚀 INICIANDO SCRAPER SCJN")
    print("=" * 40)
    
    try:
        from scraper.selenium_scraper import SeleniumSCJNScraper
        from database.models import get_session, Tesis, create_tables
        
        # Crear tablas si no existen
        create_tables()
        
        # Crear scraper
        scraper = SeleniumSCJNScraper()
        scraper.setup_driver()
        
        # Términos de búsqueda
        search_terms = [
            "derechos humanos",
            "amparo",
            "constitucional",
            "penal",
            "civil",
            "laboral"
        ]
        
        total_processed = 0
        
        for term in search_terms:
            print(f"\n🔍 Buscando: {term}")
            
            try:
                # Navegar y buscar
                scraper.navigate_to_search_page()
                scraper.search_for_tesis(term)
                
                # Extraer resultados
                results = scraper.extract_search_results()
                print(f"📋 Encontrados: {len(results)} resultados")
                
                # Procesar primeros 10 resultados
                for i, result in enumerate(results[:10]):
                    try:
                        print(f"  📄 Procesando {i+1}/10: {result.get('titulo', 'Sin título')[:50]}...")
                        
                        # Obtener detalles
                        detail = scraper.get_tesis_detail(result.get('url', ''))
                        
                        # Guardar en base de datos
                        session = get_session()
                        
                        # Verificar si ya existe
                        existing = session.query(Tesis).filter_by(scjn_id=result.get('scjn_id')).first()
                        
                        if not existing:
                            tesis = Tesis(
                                scjn_id=result.get('scjn_id'),
                                titulo=result.get('titulo'),
                                url=result.get('url'),
                                rubro=detail.get('rubro') if detail else None,
                                texto=detail.get('texto') if detail else None,
                                precedente=detail.get('precedente') if detail else None,
                                pdf_url=detail.get('pdf_url') if detail else None,
                                meta_data=detail.get('metadata', {}) if detail else {}
                            )
                            session.add(tesis)
                            session.commit()
                            total_processed += 1
                            print(f"    ✅ Guardado")
                        else:
                            print(f"    ⏭️  Ya existe")
                        
                        session.close()
                        
                    except Exception as e:
                        print(f"    ❌ Error procesando: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ Error en búsqueda '{term}': {e}")
                continue
        
        # Cerrar scraper
        scraper.close_driver()
        
        print(f"\n🎉 SCRAPING COMPLETADO")
        print(f"📊 Total procesadas: {total_processed} tesis")
        
        # Mostrar estadísticas
        session = get_session()
        total_in_db = session.query(Tesis).count()
        session.close()
        
        print(f"📊 Total en base de datos: {total_in_db}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 