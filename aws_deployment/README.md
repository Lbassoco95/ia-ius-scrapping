# 🚀 Despliegue en AWS - Sistema de Scraping Inteligente SCJN

Guía completa para desplegar el sistema de scraping en Amazon Web Services (AWS).

## 🎯 Arquitectura Recomendada

### **EC2 + RDS + S3**
- **EC2**: Instancia para el scraper (t3.medium recomendado)
- **RDS**: Base de datos PostgreSQL (más robusta que SQLite)
- **S3**: Almacenamiento de PDFs y backups
- **CloudWatch**: Monitoreo y logs

### **Ventajas de AWS:**
- ✅ **Alta disponibilidad**: 99.9% uptime
- ✅ **Escalabilidad**: Ajustar recursos según necesidad
- ✅ **Seguridad**: IAM, VPC, Security Groups
- ✅ **Monitoreo**: CloudWatch integrado
- ✅ **Backup automático**: RDS + S3
- ✅ **Costo optimizado**: ~$50-80/mes

## 📋 Requisitos Previos

### **Cuenta AWS**
- Cuenta AWS activa
- Acceso a EC2, RDS, S3, CloudWatch
- Permisos de administrador

### **Herramientas Locales**
```bash
# AWS CLI
pip install awscli

# Terraform (opcional, para infraestructura como código)
brew install terraform

# Docker (opcional)
brew install docker
```

## 🏗️ Opciones de Despliegue

### **Opción 1: Despliegue Manual (Recomendado para empezar)**
- Configuración paso a paso
- Control total
- Ideal para aprendizaje

### **Opción 2: Terraform (Infraestructura como código)**
- Automatización completa
- Reproducible
- Ideal para producción

### **Opción 3: Docker + ECS**
- Contenedores
- Escalabilidad automática
- Ideal para alta demanda

## 🚀 Despliegue Manual en AWS

### **Paso 1: Crear Instancia EC2**

#### **Especificaciones Recomendadas:**
- **Tipo**: t3.medium (2 vCPU, 4 GB RAM)
- **Sistema Operativo**: Ubuntu 22.04 LTS
- **Almacenamiento**: 50 GB SSD
- **Región**: us-east-1 (N. Virginia)

#### **Comandos AWS CLI:**
```bash
# Crear key pair
aws ec2 create-key-pair --key-name scjn-scraper-key --query 'KeyMaterial' --output text > scjn-scraper-key.pem
chmod 400 scjn-scraper-key.pem

# Crear security group
aws ec2 create-security-group --group-name scjn-scraper-sg --description "Security group for SCJN scraper"

# Configurar reglas de seguridad
aws ec2 authorize-security-group-ingress --group-name scjn-scraper-sg --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name scjn-scraper-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name scjn-scraper-sg --protocol tcp --port 443 --cidr 0.0.0.0/0

# Lanzar instancia
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name scjn-scraper-key \
  --security-group-ids scjn-scraper-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=scjn-scraper}]'
```

### **Paso 2: Configurar Instancia**

#### **Conectar a la instancia:**
```bash
# Obtener IP pública
aws ec2 describe-instances --filters "Name=tag:Name,Values=scjn-scraper" --query 'Reservations[].Instances[].PublicIpAddress' --output text

# Conectar via SSH
ssh -i scjn-scraper-key.pem ubuntu@[IP_PUBLICA]
```

#### **Instalar dependencias en la instancia:**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Instalar Chrome y ChromeDriver
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

### **Paso 3: Desplegar Código**

#### **Clonar y configurar proyecto:**
```bash
# Clonar repositorio
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

### **Paso 4: Configurar Base de Datos RDS**

#### **Crear instancia RDS:**
```bash
# Crear subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name scjn-scraper-subnet-group \
  --db-subnet-group-description "Subnet group for SCJN scraper" \
  --subnet-ids subnet-xxxxx subnet-yyyyy

# Crear instancia RDS
aws rds create-db-instance \
  --db-instance-identifier scjn-scraper-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password [PASSWORD_SEGURO] \
  --allocated-storage 20 \
  --db-subnet-group-name scjn-scraper-subnet-group \
  --vpc-security-group-ids sg-xxxxx
```

#### **Configurar conexión a RDS:**
```bash
# En la instancia EC2, actualizar configuración
nano src/config.py

# Cambiar DATABASE_URL a:
DATABASE_URL = "postgresql://admin:[PASSWORD]@[RDS_ENDPOINT]:5432/scjn_database"
```

### **Paso 5: Configurar S3 para Almacenamiento**

#### **Crear bucket S3:**
```bash
# Crear bucket
aws s3 mb s3://scjn-scraper-data-[REGION]

# Configurar lifecycle para backups
aws s3api put-bucket-lifecycle-configuration \
  --bucket scjn-scraper-data-[REGION] \
  --lifecycle-configuration file://s3-lifecycle.json
```

#### **Configurar acceso desde EC2:**
```bash
# Crear IAM role para EC2
aws iam create-role --role-name EC2S3Access --assume-role-policy-document file://trust-policy.json

# Adjuntar política S3
aws iam attach-role-policy --role-name EC2S3Access --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Adjuntar role a instancia
aws ec2 associate-iam-instance-profile --instance-id i-xxxxx --iam-instance-profile Name=EC2S3Access
```

### **Paso 6: Configurar Monitoreo con CloudWatch**

#### **Instalar CloudWatch Agent:**
```bash
# En la instancia EC2
sudo apt install -y amazon-cloudwatch-agent

# Configurar agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

#### **Configurar logs:**
```bash
# Crear configuración de logs
sudo nano /opt/aws/amazon-cloudwatch-agent/bin/config.json

# Iniciar agent
sudo systemctl start amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent
```

### **Paso 7: Configurar Sistema como Servicio**

#### **Crear servicio systemd:**
```bash
sudo nano /etc/systemd/system/scjn-scraper.service
```

```ini
[Unit]
Description=SCJN Intelligent Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/scjn-scraper
Environment=PATH=/home/ubuntu/scjn-scraper/venv/bin
ExecStart=/home/ubuntu/scjn-scraper/venv/bin/python start_auto_scraper.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **Iniciar servicio:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable scjn-scraper
sudo systemctl start scjn-scraper
sudo systemctl status scjn-scraper
```

## 📊 Monitoreo y Mantenimiento

### **CloudWatch Dashboard**
- Métricas de CPU, memoria, disco
- Logs del sistema
- Alertas automáticas

### **Comandos de Mantenimiento:**
```bash
# Ver estado del servicio
sudo systemctl status scjn-scraper

# Ver logs
sudo journalctl -u scjn-scraper -f

# Reiniciar servicio
sudo systemctl restart scjn-scraper

# Ver logs de la aplicación
tail -f logs/auto_scraper.log
```

### **Backup Automático:**
```bash
# Script de backup diario
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
aws s3 cp data/scjn_database.db s3://scjn-scraper-data/backups/database_$DATE.db
aws s3 cp data/ s3://scjn-scraper-data/backups/data_$DATE/ --recursive
```

## 💰 Estimación de Costos

### **Costo Mensual Estimado:**
- **EC2 t3.medium**: ~$30/mes
- **RDS db.t3.micro**: ~$15/mes
- **S3 (50GB)**: ~$1/mes
- **CloudWatch**: ~$5/mes
- **Data Transfer**: ~$5/mes
- **Total**: ~$56/mes

### **Optimización de Costos:**
- Usar Spot Instances para desarrollo
- Configurar auto-scaling
- Implementar lifecycle policies en S3
- Usar Reserved Instances para producción

## 🔒 Seguridad

### **Mejores Prácticas:**
- Usar IAM roles en lugar de access keys
- Configurar Security Groups restrictivos
- Habilitar CloudTrail para auditoría
- Usar VPC privadas
- Implementar backup encryption

## 🚀 Despliegue Rápido con Scripts

### **Script de Despliegue Automático:**
```bash
# Ejecutar script de despliegue
chmod +x aws_deployment/deploy.sh
./aws_deployment/deploy.sh
```

### **Script de Configuración:**
```bash
# Configurar instancia
chmod +x aws_deployment/setup_instance.sh
./aws_deployment/setup_instance.sh
```

## 📞 Soporte y Troubleshooting

### **Problemas Comunes:**
1. **Conexión SSH**: Verificar security groups
2. **Base de datos**: Verificar VPC y security groups
3. **S3 acceso**: Verificar IAM roles
4. **Servicio no inicia**: Verificar logs y permisos

### **Comandos de Diagnóstico:**
```bash
# Verificar conectividad
ping google.com
curl -I https://www.scjn.gob.mx

# Verificar servicios
sudo systemctl status scjn-scraper
sudo systemctl status amazon-cloudwatch-agent

# Verificar recursos
htop
df -h
free -h
```

---

**¡El sistema estará funcionando automáticamente en AWS con alta disponibilidad y monitoreo completo!** 🎉 