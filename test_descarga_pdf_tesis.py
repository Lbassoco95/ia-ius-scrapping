#!/usr/bin/env python3
"""
Script de prueba para descargar el PDF de una tesis específica de la SCJN y subirlo a Google Drive
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from src.storage.google_drive import GoogleDriveManager
from src.database.models import get_session, Tesis
from selenium.webdriver.common.action_chains import ActionChains

TESIS_ID = "2030758"
TESIS_URL = f"https://sjf2.scjn.gob.mx/detalle/tesis/{TESIS_ID}"
# Configurar Selenium para descargas automáticas
PDF_DIR = os.path.abspath("data/pdfs")
# Quitar headless para ver la ventana
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Comentado para modo visible
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_prefs = {
    "download.default_directory": PDF_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", chrome_prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print(f"Navegando a {TESIS_URL}")
    driver.get(TESIS_URL)
    time.sleep(8)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Buscar botón de descarga por aria-label, clase o ícono
    download_button = None
    try:
        # Buscar por aria-label o title
        download_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Descargar'], button[title*='Descargar']")
    except:
        # Buscar por ícono
        try:
            download_button = driver.find_element(By.CSS_SELECTOR, ".fa-download, .icon-download")
        except:
            pass

    if not download_button:
        print("No se encontró botón de descarga en la página.")
        driver.quit()
        exit(1)

    print("Botón de descarga encontrado. Haciendo click...")
    ActionChains(driver).move_to_element(download_button).click().perform()
    time.sleep(15)  # Esperar más tiempo para descarga

    # Listar archivos descargados
    print("Archivos en la carpeta de descargas:")
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    for f in pdf_files:
        print(" -", f)

    # Detectar el PDF descargado más reciente
    if pdf_files:
        # Tomar el archivo PDF más reciente
        pdf_files_full = [os.path.join(PDF_DIR, f) for f in pdf_files]
        latest_pdf = max(pdf_files_full, key=os.path.getctime)
        print(f"PDF detectado: {latest_pdf}")
        # Renombrar si es necesario
        pdf_filename = f"tesis_{TESIS_ID}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        if os.path.basename(latest_pdf) != pdf_filename:
            os.rename(latest_pdf, pdf_path)
            print(f"Archivo renombrado a {pdf_path}")
        else:
            pdf_path = latest_pdf
        print(f"PDF listo en {pdf_path}")
        # Subir a Google Drive y guardar en BD como antes...
        drive = GoogleDriveManager()
        print("Subiendo PDF a Google Drive...")
        result = drive.upload_file(pdf_path, pdf_filename)
        if result:
            file_id, web_link = result
            print(f"PDF subido a Google Drive. ID: {file_id}, Enlace: {web_link}")
        else:
            print("Error subiendo PDF a Google Drive.")
            web_link = None
            file_id = None
        session = get_session()
        tesis = session.query(Tesis).filter_by(scjn_id=TESIS_ID).first()
        if tesis:
            tesis.pdf_url = pdf_path
            tesis.google_drive_id = file_id
            tesis.google_drive_link = web_link
            session.commit()
            print("Información de PDF y Google Drive guardada en la base de datos.")
        else:
            print("No se encontró la tesis en la base de datos para actualizar.")
        session.close()
    else:
        print("No se descargó el PDF. Verifica permisos o cambios en la página.")
finally:
    driver.quit() 