#!/usr/bin/env python3
"""
Script para analizar la estructura de la página de SCJN
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_scjn_page():
    """Analizar la estructura de la página de SCJN"""
    print("🔍 ANALIZANDO ESTRUCTURA DE LA PÁGINA SCJN")
    print("=" * 50)
    
    try:
        # Obtener página
        url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"✅ Página obtenida - Status: {response.status_code}")
        print(f"📄 Título de la página: {soup.title.string if soup.title else 'No encontrado'}")
        
        # Buscar elementos que podrían contener tesis
        print("\n🔍 Buscando elementos de tesis...")
        
        # Buscar enlaces que contengan "tesis"
        tesis_links = soup.find_all('a', href=lambda x: x and 'tesis' in x.lower())
        print(f"📎 Enlaces con 'tesis': {len(tesis_links)}")
        
        for i, link in enumerate(tesis_links[:5]):
            print(f"   {i+1}. {link.get('href', 'N/A')} - {link.get_text(strip=True)[:50]}...")
        
        # Buscar tablas
        tables = soup.find_all('table')
        print(f"\n📊 Tablas encontradas: {len(tables)}")
        
        # Buscar divs con clases específicas
        divs = soup.find_all('div', class_=True)
        classes = set()
        for div in divs:
            classes.update(div.get('class', []))
        
        print(f"\n🏷️ Clases de divs encontradas: {len(classes)}")
        relevant_classes = [cls for cls in classes if any(keyword in cls.lower() for keyword in ['tesis', 'resultado', 'busqueda', 'item', 'row'])]
        print(f"📋 Clases relevantes: {relevant_classes}")
        
        # Buscar elementos con estas clases
        for cls in relevant_classes:
            elements = soup.find_all(class_=cls)
            print(f"   {cls}: {len(elements)} elementos")
        
        # Buscar elementos con data attributes
        data_elements = soup.find_all(attrs={"data-": True})
        print(f"\n📊 Elementos con data attributes: {len(data_elements)}")
        
        # Guardar HTML para análisis manual
        with open('data/page_analysis.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"\n💾 HTML guardado en: data/page_analysis.html")
        
        # Buscar patrones específicos
        print("\n🔍 Buscando patrones específicos...")
        
        # Buscar números que podrían ser IDs de tesis
        import re
        numbers = re.findall(r'\d{7,}', response.text)
        unique_numbers = list(set(numbers))
        print(f"🔢 Números largos encontrados (posibles IDs): {len(unique_numbers)}")
        print(f"   Ejemplos: {unique_numbers[:10]}")
        
        # Buscar texto que contenga "tesis" o "jurisprudencia"
        tesis_text = soup.find_all(text=re.compile(r'tesis|jurisprudencia', re.IGNORECASE))
        print(f"📝 Texto con 'tesis' o 'jurisprudencia': {len(tesis_text)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando página: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_scjn_page() 