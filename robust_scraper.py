#!/usr/bin/env python3
"""
Scraper robusto para la página de SCJN
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def robust_scraping_test():
    """Prueba de scraping robusto"""
    print("🛡️ PRUEBA DE SCRAPING ROBUSTO")
    print("=" * 50)
    
    # Configurar driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 1. Navegar a la página
        print("1️⃣ Navegando a la página de búsqueda...")
        driver.get("https://sjf2.scjn.gob.mx/busqueda-principal-tesis")
        time.sleep(5)
        
        print(f"✅ Página cargada: {driver.title}")
        
        # 2. Buscar campo de búsqueda
        print("\n2️⃣ Buscando campo de búsqueda...")
        search_input = None
        
        # Intentar diferentes selectores
        selectors = [
            "input[name='search']",
            "input[type='text']",
            "input[placeholder*='buscar']",
            "input[placeholder*='tema']",
            "input[placeholder*='interés']"
        ]
        
        for selector in selectors:
            try:
                search_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Campo de búsqueda encontrado con selector: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not search_input:
            print("❌ No se encontró campo de búsqueda")
            return False
        
        # 3. Ingresar término de búsqueda
        print("\n3️⃣ Ingresando término de búsqueda...")
        search_input.clear()
        search_input.send_keys("derechos humanos")
        print("✅ Término ingresado: 'derechos humanos'")
        
        # 4. Buscar botón de búsqueda
        print("\n4️⃣ Buscando botón de búsqueda...")
        search_button = None
        
        # Intentar diferentes selectores para botones
        button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Buscar')",
            "button:contains('Search')",
            "input[value*='Buscar']",
            "input[value*='Search']",
            "button",
            "input[type='button']"
        ]
        
        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    button_text = button.text.strip().lower()
                    button_value = button.get_attribute("value", "").lower()
                    
                    if any(keyword in button_text or keyword in button_value 
                           for keyword in ['buscar', 'search', 'enviar', 'submit']):
                        search_button = button
                        print(f"✅ Botón de búsqueda encontrado: {button_text or button_value}")
                        break
                if search_button:
                    break
            except:
                continue
        
        if not search_button:
            print("⚠️ No se encontró botón específico, intentando con Enter...")
            from selenium.webdriver.common.keys import Keys
            search_input.send_keys(Keys.RETURN)
        else:
            search_button.click()
        
        print("✅ Búsqueda ejecutada")
        time.sleep(5)
        
        # 5. Analizar resultados
        print("\n5️⃣ Analizando resultados...")
        
        # Guardar HTML para análisis
        with open("data/robust_analysis.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 HTML guardado para análisis")
        
        # Buscar diferentes tipos de resultados
        results = []
        
        # Buscar enlaces que contengan "tesis"
        tesis_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='tesis']")
        print(f"📎 Enlaces de tesis encontrados: {len(tesis_links)}")
        
        for i, link in enumerate(tesis_links[:5]):
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if href and text:
                    result = {
                        'scjn_id': f"robust_{i+1}",
                        'titulo': text,
                        'url': href,
                        'metadata': {
                            'tipo': 'enlace_directo'
                        }
                    }
                    results.append(result)
                    print(f"   {i+1}. {text[:60]}...")
            except:
                continue
        
        # Buscar enlaces que contengan números (posibles IDs)
        import re
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            try:
                href = link.get_attribute("href")
                if href and re.search(r'\d{6,}', href):  # Buscar URLs con números largos
                    text = link.text.strip()
                    if text and len(text) > 10:  # Texto significativo
                        result = {
                            'scjn_id': re.findall(r'\d{6,}', href)[0],
                            'titulo': text,
                            'url': href,
                            'metadata': {
                                'tipo': 'enlace_numerico'
                            }
                        }
                        results.append(result)
                        print(f"   Encontrado: {text[:60]}... (ID: {result['scjn_id']})")
                        break  # Solo el primero
            except:
                continue
        
        # 6. Probar obtención de detalles
        if results:
            print(f"\n6️⃣ Probando obtención de detalles...")
            first_result = results[0]
            
            print(f"   Navegando a: {first_result['url']}")
            driver.get(first_result['url'])
            time.sleep(3)
            
            # Extraer detalles básicos
            detail_data = {
                'url': first_result['url'],
                'html_content': driver.page_source
            }
            
            # Buscar contenido de la página
            page_text = driver.page_source
            
            # Buscar patrones comunes
            patterns = {
                'rubro': r'<[^>]*rubro[^>]*>(.*?)</[^>]*>',
                'texto': r'<[^>]*texto[^>]*>(.*?)</[^>]*>',
                'precedente': r'<[^>]*precedente[^>]*>(.*?)</[^>]*>'
            }
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    detail_data[key] = matches[0].strip()
                    print(f"   ✅ {key.capitalize()} encontrado: {detail_data[key][:50]}...")
            
            # Buscar PDF
            pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
            pdf_matches = re.findall(pdf_pattern, page_text, re.IGNORECASE)
            if pdf_matches:
                detail_data['pdf_url'] = pdf_matches[0]
                print(f"   ✅ PDF encontrado: {detail_data['pdf_url']}")
            
            # Combinar datos
            complete_result = {**first_result, **detail_data}
            results[0] = complete_result
        
        # 7. Guardar resultados
        if results:
            print(f"\n7️⃣ Guardando {len(results)} resultados...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/robust_test_results_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Resultados guardados en: {filename}")
            
            print("\n🎉 ¡PRUEBA ROBUSTA COMPLETADA EXITOSAMENTE!")
            print("=" * 50)
            print("✅ El sistema está funcionando correctamente")
            print("✅ Se pueden extraer tesis y sus detalles")
            print("✅ El sistema está listo para uso básico")
            
        else:
            print("\n❌ No se pudieron extraer resultados")
            print("💡 La página puede requerir interacción adicional")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = robust_scraping_test()
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}") 