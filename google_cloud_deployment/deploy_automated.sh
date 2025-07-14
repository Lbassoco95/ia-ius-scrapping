#!/bin/bash
# 🚀 Script de Despliegue Automático en Google Cloud - Sistema de Scraping Inteligente SCJN

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="scjn-scraper"
PROJECT_ID=""
ZONE="us-central1-a"
REGION="us-central1"
INSTANCE_TYPE="e2-medium"
DB_INSTANCE_CLASS="db-f1-micro"
S3_BUCKET="scjn-scraper-data"

echo -e "${BLUE}🚀 DESPLIEGUE AUTOMÁTICO EN GOOGLE CLOUD - SCJN SCRAPER${NC}"
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

# Verificar Google Cloud CLI
check_gcloud_cli() {
    print_status "Verificando Google Cloud CLI..."
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI no está instalado."
        print_warning "Instale con: curl https://sdk.cloud.google.com | bash"
        exit 1
    fi
    
    # Verificar configuración
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Google Cloud CLI no está autenticado. Ejecute: gcloud auth login"
        exit 1
    fi
    
    print_status "Google Cloud CLI configurado correctamente"
}

# Obtener o configurar proyecto
setup_project() {
    print_status "Configurando proyecto..."
    
    # Obtener proyecto actual
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
    
    if [ -z "$CURRENT_PROJECT" ]; then
        print_warning "No hay proyecto configurado"
        echo "Proyectos disponibles:"
        gcloud projects list --format="table(projectId,name)" --limit=10
        
        read -p "Ingrese el Project ID: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    else
        PROJECT_ID=$CURRENT_PROJECT
        print_status "Usando proyecto: $PROJECT_ID"
    fi
    
    # Habilitar APIs necesarias
    print_status "Habilitando APIs..."
    gcloud services enable compute.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable storage.googleapis.com
    gcloud services enable monitoring.googleapis.com
    gcloud services enable logging.googleapis.com
}

# Crear VPC y firewall
create_network() {
    print_status "Creando red y firewall..."
    
    # Crear VPC
    gcloud compute networks create $PROJECT_NAME-vpc --subnet-mode=auto
    
    # Crear firewall rules
    gcloud compute firewall-rules create $PROJECT_NAME-allow-ssh \
        --network $PROJECT_NAME-vpc \
        --allow tcp:22 \
        --source-ranges 0.0.0.0/0 \
        --description "Allow SSH access"
    
    gcloud compute firewall-rules create $PROJECT_NAME-allow-http \
        --network $PROJECT_NAME-vpc \
        --allow tcp:80,tcp:443 \
        --source-ranges 0.0.0.0/0 \
        --description "Allow HTTP/HTTPS access"
    
    print_status "Red y firewall creados"
}

# Crear service account
create_service_account() {
    print_status "Creando service account..."
    
    # Crear service account
    gcloud iam service-accounts create $PROJECT_NAME-sa \
        --description="Service account for SCJN scraper" \
        --display-name="SCJN Scraper SA" || true
    
    # Asignar roles
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$PROJECT_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/storage.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$PROJECT_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/monitoring.metricWriter"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$PROJECT_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/logging.logWriter"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$PROJECT_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client"
    
    print_status "Service account creado y configurado"
}

# Crear bucket Cloud Storage
create_storage_bucket() {
    print_status "Creando bucket Cloud Storage..."
    
    BUCKET_NAME="$S3_BUCKET-$PROJECT_ID"
    
    # Crear bucket
    gsutil mb -l $REGION gs://$BUCKET_NAME || true
    
    # Configurar lifecycle
    cat > lifecycle.json << EOF
{
  "rule": [
    {
      "action": {
        "type": "Delete"
      },
      "condition": {
        "age": 365,
        "matchesPrefix": ["backups/"]
      }
    },
    {
      "action": {
        "type": "SetStorageClass",
        "storageClass": "NEARLINE"
      },
      "condition": {
        "age": 30,
        "matchesPrefix": ["backups/"]
      }
    }
  ]
}
EOF
    
    gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
    print_status "Bucket Cloud Storage creado: $BUCKET_NAME"
}

# Crear instancia Cloud SQL
create_sql_instance() {
    print_status "Creando instancia Cloud SQL..."
    
    # Generar password seguro
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Crear instancia Cloud SQL
    gcloud sql instances create $PROJECT_NAME-db \
        --database-version=POSTGRES_14 \
        --tier=$DB_INSTANCE_CLASS \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=20GB \
        --backup-start-time=02:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=03 \
        --authorized-networks=0.0.0.0/0 \
        --require-ssl \
        --root-password=$DB_PASSWORD
    
    # Crear base de datos
    gcloud sql databases create scjn_database --instance=$PROJECT_NAME-db
    
    # Crear usuario
    gcloud sql users create scjn_user --instance=$PROJECT_NAME-db --password=$DB_PASSWORD
    
    print_status "Instancia Cloud SQL creada: $PROJECT_NAME-db"
    print_warning "Password de base de datos: $DB_PASSWORD (guárdalo seguro!)"
    
    # Obtener connection name
    CONNECTION_NAME=$(gcloud sql instances describe $PROJECT_NAME-db --format='get(connectionName)')
    print_status "Connection name: $CONNECTION_NAME"
}

# Crear instancia Compute Engine
create_compute_instance() {
    print_status "Creando instancia Compute Engine..."
    
    # Crear instancia
    gcloud compute instances create $PROJECT_NAME \
        --zone=$ZONE \
        --machine-type=$INSTANCE_TYPE \
        --network=$PROJECT_NAME-vpc \
        --maintenance-policy=MIGRATE \
        --provisioning-model=STANDARD \
        --service-account=$PROJECT_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --create-disk=auto-delete=yes,boot=yes,device-name=$PROJECT_NAME,image=projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts,mode=rw,size=50,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-standard \
        --no-shielded-secure-boot \
        --shielded-vtpm \
        --shielded-integrity-monitoring \
        --labels=env=production,app=scjn-scraper \
        --reservation-affinity=any
    
    print_status "Instancia Compute Engine creada: $PROJECT_NAME"
    
    # Obtener IP externa
    EXTERNAL_IP=$(gcloud compute instances describe $PROJECT_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
    print_status "IP externa: $EXTERNAL_IP"
}

# Configurar instancia
configure_instance() {
    print_status "Configurando instancia..."
    
    # Obtener IP externa
    EXTERNAL_IP=$(gcloud compute instances describe $PROJECT_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
    
    # Script de configuración
    cat > setup_instance.sh << 'EOF'
#!/bin/bash
set -e

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip

# Instalar Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Instalar ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Instalar Cloud SQL Proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Instalar Cloud Monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
sudo bash add-monitoring-agent-repo.sh
sudo apt-get update
sudo apt-get install stackdriver-agent

# Instalar Cloud Logging agent
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh
sudo apt-get update
sudo apt-get install google-fluentd

# Crear directorio del proyecto
mkdir -p /home/ubuntu/scjn-scraper
cd /home/ubuntu/scjn-scraper

# Clonar repositorio (reemplazar con tu URL)
# git clone [URL_DEL_REPOSITORIO] .

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar sistema
python setup_intelligent_scraper.py

# Crear script de inicio del proxy
cat > start_proxy.sh << 'PROXY_EOF'
#!/bin/bash
./cloud_sql_proxy -instances=[CONNECTION_NAME]=tcp:5432 &
sleep 5
PROXY_EOF

chmod +x start_proxy.sh

# Crear servicio systemd
sudo tee /etc/systemd/system/scjn-scraper.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=SCJN Intelligent Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/scjn-scraper
Environment=PATH=/home/ubuntu/scjn-scraper/venv/bin
ExecStartPre=/home/ubuntu/start_proxy.sh
ExecStart=/home/ubuntu/scjn-scraper/venv/bin/python start_auto_scraper.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable scjn-scraper
sudo systemctl start scjn-scraper

# Configurar logging
sudo tee /etc/google-fluentd/config.d/scjn-scraper.conf > /dev/null << 'LOGGING_EOF'
<source>
  @type tail
  path /home/ubuntu/scjn-scraper/logs/*.log
  pos_file /var/lib/google-fluentd/pos/scjn-scraper.pos
  read_from_head true
  tag scjn-scraper
  <parse>
    @type regexp
    expression /^(?<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?<level>\w+) - (?<message>.*)$/
  </parse>
</source>
LOGGING_EOF

# Reiniciar servicios
sudo systemctl restart stackdriver-agent
sudo systemctl restart google-fluentd

echo "✅ Instancia configurada correctamente"
EOF
    
    # Copiar script a la instancia
    gcloud compute scp setup_instance.sh ubuntu@$PROJECT_NAME:~/ --zone=$ZONE
    
    # Ejecutar script
    gcloud compute ssh ubuntu@$PROJECT_NAME --zone=$ZONE --command="chmod +x setup_instance.sh && ./setup_instance.sh"
    
    print_status "Instancia configurada"
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando despliegue automático en Google Cloud...${NC}"
    
    check_gcloud_cli
    setup_project
    create_network
    create_service_account
    create_storage_bucket
    create_sql_instance
    create_compute_instance
    configure_instance
    
    echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
    echo ""
    echo -e "${BLUE}📋 INFORMACIÓN DEL DESPLIEGUE:${NC}"
    echo "=================================="
    echo "🌐 IP externa: $EXTERNAL_IP"
    echo "🗄️ Cloud SQL: $PROJECT_NAME-db"
    echo "📦 Cloud Storage: $S3_BUCKET-$PROJECT_ID"
    echo "🔐 DB password: $DB_PASSWORD"
    echo "🔗 Connection name: $CONNECTION_NAME"
    echo ""
    echo -e "${YELLOW}📝 PRÓXIMOS PASOS:${NC}"
    echo "1. Conectar a la instancia: gcloud compute ssh $PROJECT_NAME --zone=$ZONE"
    echo "2. Verificar servicio: sudo systemctl status scjn-scraper"
    echo "3. Ver logs: sudo journalctl -u scjn-scraper -f"
    echo "4. Configurar monitoreo en Cloud Console"
    echo ""
    echo -e "${GREEN}✅ El sistema está funcionando automáticamente en Google Cloud!${NC}"
}

# Ejecutar función principal
main "$@" 