# ☁️ Despliegue en Google Cloud - Sistema de Scraping Inteligente SCJN

Guía completa para desplegar el sistema de scraping en Google Cloud Platform (GCP).

## 🎯 Arquitectura Recomendada

### **Compute Engine + Cloud SQL + Cloud Storage**
- **Compute Engine**: VM para el scraper (e2-medium recomendado)
- **Cloud SQL**: Base de datos PostgreSQL
- **Cloud Storage**: Almacenamiento de PDFs y backups
- **Cloud Monitoring**: Monitoreo y logs

### **Ventajas de Google Cloud:**
- ✅ **Alta disponibilidad**: 99.9% uptime
- ✅ **Escalabilidad**: Auto-scaling automático
- ✅ **Seguridad**: IAM, VPC, Firewall rules
- ✅ **Monitoreo**: Cloud Monitoring integrado
- ✅ **Backup automático**: Cloud SQL + Cloud Storage
- ✅ **Costo optimizado**: ~$40-70/mes

## 📋 Requisitos Previos

### **Cuenta Google Cloud**
- Proyecto GCP activo
- Facturación habilitada
- APIs habilitadas: Compute Engine, Cloud SQL, Cloud Storage

### **Herramientas Locales**
```bash
# Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Terraform (opcional)
brew install terraform
```

## 🚀 Despliegue en Google Cloud

### **Paso 1: Configurar Proyecto**

#### **Inicializar proyecto:**
```bash
# Configurar proyecto
gcloud config set project [TU_PROJECT_ID]

# Habilitar APIs necesarias
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### **Paso 2: Crear VPC y Firewall**

#### **Crear red personalizada:**
```bash
# Crear VPC
gcloud compute networks create scjn-scraper-vpc --subnet-mode=auto

# Crear firewall rules
gcloud compute firewall-rules create allow-ssh \
  --network scjn-scraper-vpc \
  --allow tcp:22 \
  --source-ranges 0.0.0.0/0

gcloud compute firewall-rules create allow-http \
  --network scjn-scraper-vpc \
  --allow tcp:80,tcp:443 \
  --source-ranges 0.0.0.0/0
```

### **Paso 3: Crear Instancia Compute Engine**

#### **Especificaciones recomendadas:**
```bash
# Crear instancia
gcloud compute instances create scjn-scraper \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --network=scjn-scraper-vpc \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=[SERVICE_ACCOUNT]@[PROJECT_ID].iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --create-disk=auto-delete=yes,boot=yes,device-name=scjn-scraper,image=projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts,mode=rw,size=50,type=projects/[PROJECT_ID]/zones/us-central1-a/diskTypes/pd-standard \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --labels=env=production,app=scjn-scraper \
  --reservation-affinity=any
```

### **Paso 4: Crear Base de Datos Cloud SQL**

#### **Crear instancia PostgreSQL:**
```bash
# Crear instancia Cloud SQL
gcloud sql instances create scjn-scraper-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=20GB \
  --backup-start-time=02:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=03 \
  --authorized-networks=0.0.0.0/0 \
  --require-ssl

# Crear base de datos
gcloud sql databases create scjn_database --instance=scjn-scraper-db

# Crear usuario
gcloud sql users create scjn_user --instance=scjn-scraper-db --password=[PASSWORD_SEGURO]
```

### **Paso 5: Crear Bucket Cloud Storage**

#### **Crear bucket para almacenamiento:**
```bash
# Crear bucket
gsutil mb -l us-central1 gs://scjn-scraper-data-[PROJECT_ID]

# Configurar lifecycle
gsutil lifecycle set lifecycle.json gs://scjn-scraper-data-[PROJECT_ID]
```

#### **Archivo lifecycle.json:**
```json
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
```

### **Paso 6: Configurar Service Account**

#### **Crear service account con permisos:**
```bash
# Crear service account
gcloud iam service-accounts create scjn-scraper-sa \
  --description="Service account for SCJN scraper" \
  --display-name="SCJN Scraper SA"

# Asignar roles
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:scjn-scraper-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:scjn-scraper-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:scjn-scraper-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### **Paso 7: Configurar Instancia**

#### **Conectar y configurar:**
```bash
# Conectar a la instancia
gcloud compute ssh scjn-scraper --zone=us-central1-a

# En la instancia, ejecutar:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget

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
```

### **Paso 8: Desplegar Código**

#### **Clonar y configurar proyecto:**
```bash
# En la instancia
cd /home/ubuntu
git clone [URL_DEL_REPOSITORIO] scjn-scraper
cd scjn-scraper

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar sistema
python setup_intelligent_scraper.py
```

### **Paso 9: Configurar Base de Datos**

#### **Actualizar configuración para Cloud SQL:**
```bash
# Obtener IP de la instancia
INSTANCE_IP=$(gcloud compute instances describe scjn-scraper --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

# Obtener connection name
CONNECTION_NAME=$(gcloud sql instances describe scjn-scraper-db --format='get(connectionName)')

# Configurar Cloud SQL Proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Crear script de conexión
cat > start_proxy.sh << 'EOF'
#!/bin/bash
./cloud_sql_proxy -instances=[CONNECTION_NAME]=tcp:5432 &
sleep 5
EOF

chmod +x start_proxy.sh
```

### **Paso 10: Configurar Servicio**

#### **Crear servicio systemd:**
```bash
sudo tee /etc/systemd/system/scjn-scraper.service > /dev/null << 'EOF'
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
EOF

# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable scjn-scraper
sudo systemctl start scjn-scraper
```

## 📊 Monitoreo con Cloud Monitoring

### **Configurar Cloud Monitoring:**
```bash
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

# Configurar logging
sudo tee /etc/google-fluentd/config.d/scjn-scraper.conf > /dev/null << 'EOF'
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
EOF

# Reiniciar servicios
sudo systemctl restart stackdriver-agent
sudo systemctl restart google-fluentd
```

## 💰 Estimación de Costos

### **Costo Mensual Estimado:**
- **Compute Engine e2-medium**: ~$25/mes
- **Cloud SQL db-f1-micro**: ~$10/mes
- **Cloud Storage (50GB)**: ~$1/mes
- **Cloud Monitoring**: ~$5/mes
- **Data Transfer**: ~$5/mes
- **Total**: ~$46/mes

### **Optimización de Costos:**
- Usar Preemptible VMs para desarrollo
- Configurar auto-scaling
- Implementar lifecycle policies
- Usar Committed Use Discounts

## 🔒 Seguridad

### **Mejores Prácticas:**
- Usar IAM roles específicos
- Configurar firewall rules restrictivas
- Habilitar Cloud Audit Logs
- Usar VPC privadas
- Implementar backup encryption

## 🚀 Script de Despliegue Automático

### **Script completo para GCP:**
```bash
#!/bin/bash
# Despliegue automático en Google Cloud

set -e

PROJECT_ID="[TU_PROJECT_ID]"
ZONE="us-central1-a"
REGION="us-central1"

echo "🚀 Desplegando en Google Cloud..."

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar APIs
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com

# Crear recursos
gcloud compute networks create scjn-scraper-vpc --subnet-mode=auto
gcloud compute firewall-rules create allow-ssh --network scjn-scraper-vpc --allow tcp:22 --source-ranges 0.0.0.0/0

# Crear service account
gcloud iam service-accounts create scjn-scraper-sa --display-name="SCJN Scraper SA"

# Crear instancia
gcloud compute instances create scjn-scraper \
  --zone=$ZONE \
  --machine-type=e2-medium \
  --network=scjn-scraper-vpc \
  --service-account=scjn-scraper-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# Crear base de datos
gcloud sql instances create scjn-scraper-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=$REGION

# Crear bucket
gsutil mb -l $REGION gs://scjn-scraper-data-$PROJECT_ID

echo "✅ Despliegue completado!"
```

## 📞 Comandos de Mantenimiento

### **Comandos útiles:**
```bash
# Ver estado de la instancia
gcloud compute instances describe scjn-scraper --zone=us-central1-a

# Conectar a la instancia
gcloud compute ssh scjn-scraper --zone=us-central1-a

# Ver logs de Cloud SQL
gcloud sql logs tail scjn-scraper-db

# Ver logs de la aplicación
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_name=scjn-scraper" --limit=50

# Crear snapshot de la instancia
gcloud compute disks snapshot [DISK_NAME] --snapshot-names scjn-scraper-snapshot-$(date +%Y%m%d)

# Backup de la base de datos
gcloud sql export sql scjn-scraper-db gs://scjn-scraper-data-[PROJECT_ID]/backups/backup-$(date +%Y%m%d).sql --database=scjn_database
```

---

**¡El sistema estará funcionando automáticamente en Google Cloud con alta disponibilidad y monitoreo completo!** 🎉 