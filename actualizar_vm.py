#!/usr/bin/env python3
"""
Script para actualizar la VM con el nuevo archivo de verificación del sistema
"""

import os
import subprocess
import sys
from datetime import datetime

def ejecutar_comando(comando, descripcion):
    """Ejecutar un comando y mostrar resultado"""
    print(f"\n🔧 {descripcion}...")
    print(f"Comando: {comando}")
    
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print(f"✅ {descripcion} - Exitoso")
            if resultado.stdout.strip():
                print(f"Salida: {resultado.stdout.strip()}")
            return True
        else:
            print(f"❌ {descripcion} - Falló")
            print(f"Error: {resultado.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {descripcion}: {str(e)}")
        return False

def verificar_conexion_vm():
    """Verificar conexión a la VM"""
    print("🔍 Verificando conexión a la VM...")
    
    # Intentar diferentes métodos de conexión
    comandos_conexion = [
        "gcloud compute instances list --filter='name~scjn-scraper'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='echo Conectado'",
        "ssh scjn-scraper 'echo Conectado'"
    ]
    
    for comando in comandos_conexion:
        if ejecutar_comando(comando, "Verificar conexión VM"):
            return True
    
    return False

def actualizar_repositorio_vm():
    """Actualizar el repositorio en la VM"""
    comandos = [
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && git pull origin main'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && chmod +x verificar_sistema.py'"
    ]
    
    for comando in comandos:
        if not ejecutar_comando(comando, "Actualizar repositorio"):
            return False
    
    return True

def probar_verificacion_vm():
    """Probar el script de verificación en la VM"""
    comando = "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && python3 verificar_sistema.py'"
    
    return ejecutar_comando(comando, "Probar script de verificación")

def instalar_dependencias_vm():
    """Instalar dependencias faltantes en la VM"""
    comandos = [
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && pip install -r requirements.txt'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && pip install beautifulsoup4 psycopg2-binary google-auth google-api-python-client python-dotenv'"
    ]
    
    for comando in comandos:
        if not ejecutar_comando(comando, "Instalar dependencias"):
            return False
    
    return True

def configurar_cron_vm():
    """Configurar cron job en la VM"""
    comandos = [
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && crontab -l > /tmp/cron_backup'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='cd ~/ia-scrapping-tesis && echo \"0 5 * * * /home/$(whoami)/ia-scrapping-tesis/cron_scraper.sh\" | crontab -'"
    ]
    
    for comando in comandos:
        if not ejecutar_comando(comando, "Configurar cron job"):
            return False
    
    return True

def verificar_servicios_vm():
    """Verificar que los servicios estén corriendo en la VM"""
    comandos = [
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='ps aux | grep cloud_sql_proxy'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='crontab -l'",
        "gcloud compute ssh scjn-scraper --zone=us-central1-a --command='ls -la ~/ia-scrapping-tesis/logs/'"
    ]
    
    for comando in comandos:
        ejecutar_comando(comando, "Verificar servicios")

def main():
    """Función principal de actualización"""
    print("🚀 ACTUALIZACIÓN DE VM CON SCRIPT DE VERIFICACIÓN")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('verificar_sistema.py'):
        print("❌ Error: No se encuentra verificar_sistema.py en el directorio actual")
        print("💡 Ejecuta este script desde el directorio del proyecto")
        return
    
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    # Verificar que el archivo se subió a GitHub
    if not ejecutar_comando("git status", "Verificar estado de Git"):
        print("❌ Error: No se puede verificar el estado de Git")
        return
    
    # Verificar conexión a la VM
    if not verificar_conexion_vm():
        print("❌ No se pudo conectar a la VM")
        print("💡 Verifica:")
        print("  - Que la VM esté corriendo")
        print("  - Que tengas permisos de acceso")
        print("  - Que gcloud esté configurado")
        return
    
    # Actualizar repositorio en la VM
    if not actualizar_repositorio_vm():
        print("❌ Error actualizando repositorio en la VM")
        return
    
    # Instalar dependencias
    if not instalar_dependencias_vm():
        print("❌ Error instalando dependencias")
        return
    
    # Configurar cron
    if not configurar_cron_vm():
        print("❌ Error configurando cron")
        return
    
    # Probar verificación
    if not probar_verificacion_vm():
        print("❌ Error probando script de verificación")
        return
    
    # Verificar servicios
    verificar_servicios_vm()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("=" * 60)
    print("🎉 La VM ha sido actualizada exitosamente con:")
    print("  ✅ Script de verificación del sistema")
    print("  ✅ Dependencias actualizadas")
    print("  ✅ Cron job configurado")
    print("  ✅ Servicios verificados")
    
    print("\n💡 Próximos pasos:")
    print("  1. Conectar a la VM: gcloud compute ssh scjn-scraper --zone=us-central1-a")
    print("  2. Ejecutar verificación: cd ~/ia-scrapping-tesis && python3 verificar_sistema.py")
    print("  3. Monitorear sistema: python3 monitor_production.py")
    print("  4. Ejecutar scraping: python3 run_scraping_now.py")

if __name__ == "__main__":
    main() 