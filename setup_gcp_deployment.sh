#!/bin/bash
# 🚀 Configuración de Google Cloud para Despliegue SCJN Scraper

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 CONFIGURACIÓN DE GOOGLE CLOUD - SCJN SCRAPER${NC}"
echo "=========================================================="

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si gcloud está instalado
check_gcloud() {
    print_status "Verificando Google Cloud CLI..."
    
    if command -v gcloud &> /dev/null; then
        print_status "Google Cloud CLI ya está instalado"
        gcloud version
        return 0
    else
        print_warning "Google Cloud CLI no está instalado"
        return 1
    fi
}

# Instalar Google Cloud CLI
install_gcloud() {
    print_status "Instalando Google Cloud CLI..."
    
    # Descargar e instalar gcloud CLI
    curl https://sdk.cloud.google.com | bash
    
    # Recargar shell
    exec -l $SHELL
    
    # Verificar instalación
    if command -v gcloud &> /dev/null; then
        print_status "Google Cloud CLI instalado correctamente"
        return 0
    else
        print_error "Error instalando Google Cloud CLI"
        return 1
    fi
}

# Configurar autenticación
setup_auth() {
    print_status "Configurando autenticación..."
    
    # Verificar si ya está autenticado
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_status "Ya está autenticado en Google Cloud"
        gcloud auth list
        return 0
    fi
    
    print_warning "Necesita autenticarse en Google Cloud"
    print_warning "Se abrirá el navegador para autenticación..."
    
    # Iniciar autenticación
    gcloud auth login
    
    # Verificar autenticación
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_status "Autenticación exitosa"
        return 0
    else
        print_error "Error en autenticación"
        return 1
    fi
}

# Configurar proyecto
setup_project() {
    print_status "Configurando proyecto..."
    
    # Mostrar proyectos disponibles
    echo "Proyectos disponibles:"
    gcloud projects list --format="table(projectId,name)" --limit=10
    
    # Solicitar Project ID
    read -p "Ingrese el Project ID (o presione Enter para crear uno nuevo): " PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID="scjn-scraper-$(date +%Y%m%d)"
        print_status "Creando nuevo proyecto: $PROJECT_ID"
        gcloud projects create $PROJECT_ID --name="SCJN Scraper Production"
    fi
    
    # Configurar proyecto
    gcloud config set project $PROJECT_ID
    print_status "Proyecto configurado: $PROJECT_ID"
    
    # Habilitar APIs necesarias
    print_status "Habilitando APIs..."
    apis=(
        "compute.googleapis.com"
        "storage.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "cloudresourcemanager.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Habilitando: $api"
        gcloud services enable $api
    done
    
    return 0
}

# Configurar billing
setup_billing() {
    print_status "Configurando billing..."
    
    # Mostrar cuentas de billing
    echo "Cuentas de billing disponibles:"
    gcloud billing accounts list --format="table(ACCOUNT_ID,name,open)"
    
    # Solicitar cuenta de billing
    read -p "Ingrese el ACCOUNT_ID de billing: " BILLING_ACCOUNT
    
    if [ ! -z "$BILLING_ACCOUNT" ]; then
        gcloud billing projects link $(gcloud config get-value project) --billing-account=$BILLING_ACCOUNT
        print_status "Billing configurado"
    else
        print_warning "Billing no configurado - será necesario para crear recursos"
    fi
    
    return 0
}

# Crear service account para la aplicación
create_service_account() {
    print_status "Creando service account para la aplicación..."
    
    PROJECT_ID=$(gcloud config get-value project)
    SA_NAME="scjn-scraper-sa"
    SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Crear service account
    gcloud iam service-accounts create $SA_NAME \
        --description="Service account for SCJN scraper" \
        --display-name="SCJN Scraper SA" || true
    
    # Asignar roles necesarios
    roles=(
        "roles/storage.admin"
        "roles/monitoring.metricWriter"
        "roles/logging.logWriter"
        "roles/compute.instanceAdmin.v1"
    )
    
    for role in "${roles[@]}"; do
        print_status "Asignando rol: $role"
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="$role"
    done
    
    # Crear y descargar credenciales
    print_status "Creando credenciales..."
    mkdir -p credentials
    gcloud iam service-accounts keys create credentials/service-account.json \
        --iam-account=$SA_EMAIL
    
    print_status "Service account creado: $SA_EMAIL"
    print_status "Credenciales guardadas en: credentials/service-account.json"
    
    return 0
}

# Configurar variables de entorno
setup_env() {
    print_status "Configurando variables de entorno..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_status "Archivo .env creado desde env.example"
    fi
    
    # Configurar variables específicas para GCP
    PROJECT_ID=$(gcloud config get-value project)
    
    # Actualizar .env con configuraciones de GCP
    sed -i "s/GOOGLE_DRIVE_ENABLED=.*/GOOGLE_DRIVE_ENABLED=true/" .env
    sed -i "s/MAX_FILES_PER_SESSION=.*/MAX_FILES_PER_SESSION=5/" .env
    sed -i "s/GOOGLE_DRIVE_CREDENTIALS_PATH=.*/GOOGLE_DRIVE_CREDENTIALS_PATH=credentials\/service-account.json/" .env
    
    print_status "Variables de entorno configuradas para GCP"
    return 0
}

# Función principal
main() {
    print_status "Iniciando configuración de Google Cloud..."
    
    # Verificar/instalar gcloud CLI
    if ! check_gcloud; then
        if ! install_gcloud; then
            print_error "No se pudo instalar Google Cloud CLI"
            exit 1
        fi
    fi
    
    # Configurar autenticación
    if ! setup_auth; then
        print_error "Error en autenticación"
        exit 1
    fi
    
    # Configurar proyecto
    if ! setup_project; then
        print_error "Error configurando proyecto"
        exit 1
    fi
    
    # Configurar billing
    setup_billing
    
    # Crear service account
    if ! create_service_account; then
        print_error "Error creando service account"
        exit 1
    fi
    
    # Configurar variables de entorno
    setup_env
    
    print_status "Configuración completada exitosamente"
    echo ""
    print_status "Próximos pasos:"
    echo "1. Ejecutar: python3 deploy_gcp_production.py"
    echo "2. El sistema se desplegará en Google Cloud"
    echo "3. Se ejecutará la prueba de resguardo de 5 archivos"
    echo ""
    print_status "¡Listo para desplegar!"
}

# Ejecutar función principal
main "$@"