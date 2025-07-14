#!/usr/bin/env python3
"""
Script de prueba para analizar la estructura de la página de búsqueda de la SCJN
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_scjn_page():
    """Analizar la estructura de la página de búsqueda de la SCJN"""
    
    url = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
    
    try:
        print("🔍 Analizando página de búsqueda de la SCJN...")
        print(f"URL: {url}")
        
        # Hacer request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Tamaño del contenido: {len(response.text)} caracteres")
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Información básica
        print(f"\n📋 Título: {soup.title.string if soup.title else 'No encontrado'}")
        
        # Buscar formularios de búsqueda
        forms = soup.find_all('form')
        print(f"\n📝 Formularios encontrados: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"  Formulario {i+1}:")
            print(f"    Action: {form.get('action', 'No especificado')}")
            print(f"    Method: {form.get('method', 'No especificado')}")
            
            # Buscar campos de entrada
            inputs = form.find_all('input')
            print(f"    Campos de entrada: {len(inputs)}")
            for inp in inputs:
                print(f"      - {inp.get('name', 'Sin nombre')} ({inp.get('type', 'Sin tipo')})")
        
        # Buscar enlaces que puedan ser de tesis
        links = soup.find_all('a', href=True)
        tesis_links = [link for link in links if 'tesis' in link.get('href', '').lower()]
        print(f"\n🔗 Enlaces de tesis encontrados: {len(tesis_links)}")
        
        for i, link in enumerate(tesis_links[:5]):  # Mostrar solo los primeros 5
            print(f"  {i+1}. {link.get('href')} - {link.get_text()[:50]}...")
        
        # Buscar tablas que puedan contener resultados
        tables = soup.find_all('table')
        print(f"\n📊 Tablas encontradas: {len(tables)}")
        
        # Buscar divs con clases que puedan ser resultados
        divs = soup.find_all('div', class_=True)
        result_divs = [div for div in divs if any(word in div.get('class', []) for word in ['resultado', 'tesis', 'item', 'row'])]
        print(f"\n📋 Divs que podrían ser resultados: {len(result_divs)}")
        
        for i, div in enumerate(result_divs[:3]):  # Mostrar solo los primeros 3
            classes = ' '.join(div.get('class', []))
            print(f"  {i+1}. Clases: {classes}")
            print(f"     Texto: {div.get_text()[:100]}...")
        
        # Guardar HTML para análisis posterior
        with open('data/scjn_page_analysis.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"\n💾 HTML guardado en: data/scjn_page_analysis.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando página: {e}")
        return False

if __name__ == "__main__":
    analyze_scjn_page() 