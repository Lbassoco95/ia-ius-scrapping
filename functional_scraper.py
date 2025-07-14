#!/usr/bin/env python3
"""
Scraper funcional para la página de SCJN basado en el análisis real
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def functional_scraping_test():
    """Prueba de scraping funcional"""
    print("🚀 PRUEBA DE SCRAPING FUNCIONAL")
    print("=" * 50)
    
    # Configurar driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        # 1. Navegar a la página
        print("1️⃣ Navegando a la página de búsqueda...")
        driver.get("https://sjf2.scjn.gob.mx/busqueda-principal-tesis")
        time.sleep(5)
        
        print(f"✅ Página cargada: {driver.title}")
        
        # 2. Realizar búsqueda básica
        print("\n2️⃣ Realizando búsqueda básica...")
        
        # Buscar campo de búsqueda
        search_input = driver.find_element(By.NAME, "search")
        search_input.clear()
        search_input.send_keys("amparo")  # Término de búsqueda común
        print("✅ Término de búsqueda ingresado: 'amparo'")
        
        # Buscar botón de búsqueda
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_button.click()
        print("✅ Búsqueda ejecutada")
        
        # Esperar resultados
        time.sleep(5)
        
        # 3. Extraer resultados
        print("\n3️⃣ Extrayendo resultados...")
        
        # Buscar tabla de resultados
        try:
            results_table = driver.find_element(By.TAG_NAME, "table")
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            print(f"✅ Encontrada tabla con {len(rows)} filas")
            
            results = []
            for i, row in enumerate(rows[1:6]):  # Saltar encabezado, tomar primeros 5
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        # Extraer enlace y título
                        link_element = cells[1].find_element(By.TAG_NAME, "a")
                        href = link_element.get_attribute("href")
                        title = link_element.text.strip()
                        
                        if href and title:
                            result = {
                                'scjn_id': f"test_{i+1}",
                                'titulo': title,
                                'url': href,
                                'metadata': {
                                    'materia': cells[0].text.strip() if len(cells) > 0 else '',
                                    'fecha': cells[2].text.strip() if len(cells) > 2 else ''
                                }
                            }
                            results.append(result)
                            print(f"   {i+1}. {title[:60]}...")
                            
                except Exception as e:
                    print(f"   Error procesando fila {i+1}: {e}")
                    continue
            
            if results:
                print(f"\n✅ Extraídos {len(results)} resultados")
                
                # 4. Probar obtención de detalles
                print("\n4️⃣ Probando obtención de detalles...")
                first_result = results[0]
                
                print(f"   Navegando a: {first_result['url']}")
                driver.get(first_result['url'])
                time.sleep(3)
                
                # Extraer detalles
                detail_data = {
                    'url': first_result['url'],
                    'html_content': driver.page_source
                }
                
                # Buscar campos específicos
                try:
                    rubro_element = driver.find_element(By.CSS_SELECTOR, ".rubro, [data-field='rubro'], .tesis-rubro")
                    detail_data['rubro'] = rubro_element.text.strip()
                    print(f"   ✅ Rubro extraído: {detail_data['rubro'][:50]}...")
                except:
                    print("   ⚠️ No se pudo extraer rubro")
                
                try:
                    texto_element = driver.find_element(By.CSS_SELECTOR, ".texto, [data-field='texto'], .tesis-texto")
                    detail_data['texto'] = texto_element.text.strip()
                    print(f"   ✅ Texto extraído: {detail_data['texto'][:50]}...")
                except:
                    print("   ⚠️ No se pudo extraer texto")
                
                # Buscar PDF
                try:
                    pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='.pdf']")
                    if pdf_links:
                        detail_data['pdf_url'] = pdf_links[0].get_attribute("href")
                        print(f"   ✅ PDF encontrado: {detail_data['pdf_url']}")
                    else:
                        print("   ⚠️ No se encontró enlace de PDF")
                except:
                    print("   ⚠️ Error buscando PDF")
                
                # Combinar datos
                complete_result = {**first_result, **detail_data}
                results[0] = complete_result
                
            else:
                print("❌ No se encontraron resultados en la tabla")
                results = []
                
        except NoSuchElementException:
            print("❌ No se encontró tabla de resultados")
            results = []
        
        # 5. Guardar resultados
        if results:
            print("\n5️⃣ Guardando resultados...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/functional_test_results_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Resultados guardados en: {filename}")
            
            print("\n🎉 ¡PRUEBA FUNCIONAL COMPLETADA EXITOSAMENTE!")
            print("=" * 50)
            print("✅ El sistema básico está funcionando correctamente")
            print("✅ Se pueden extraer tesis y sus detalles")
            print("✅ El sistema está listo para uso básico")
            
        else:
            print("\n❌ No se pudieron extraer resultados")
            print("💡 Sugerencias:")
            print("   - Verificar que la página no haya cambiado")
            print("   - Probar con diferentes términos de búsqueda")
            print("   - Revisar si hay captcha o verificación")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = functional_scraping_test()
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}") 