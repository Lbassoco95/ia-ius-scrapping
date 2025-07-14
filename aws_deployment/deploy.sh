#!/bin/bash
# 🚀 Script de Despliegue Automático en AWS - Sistema de Scraping Inteligente SCJN

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="scjn-scraper"
REGION="us-east-1"
INSTANCE_TYPE="t3.medium"
DB_INSTANCE_CLASS="db.t3.micro"
S3_BUCKET="scjn-scraper-data-$(date +%Y%m%d)"

echo -e "${BLUE}🚀 DESPLIEGUE AUTOMÁTICO EN AWS - SCJN SCRAPER${NC}"
echo "=================================================="

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

# Verificar AWS CLI
check_aws_cli() {
    print_status "Verificando AWS CLI..."
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI no está instalado. Instale con: pip install awscli"
        exit 1
    fi
    
    # Verificar configuración
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI no está configurado. Ejecute: aws configure"
        exit 1
    fi
    
    print_status "AWS CLI configurado correctamente"
}

# Crear recursos de red
create_network_resources() {
    print_status "Creando recursos de red..."
    
    # Crear VPC
    VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
    aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=$PROJECT_NAME-vpc
    print_status "VPC creada: $VPC_ID"
    
    # Crear Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
    aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
    aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value=$PROJECT_NAME-igw
    print_status "Internet Gateway creado: $IGW_ID"
    
    # Crear subnets
    SUBNET_1_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${REGION}a --query 'Subnet.SubnetId' --output text)
    SUBNET_2_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${REGION}b --query 'Subnet.SubnetId' --output text)
    aws ec2 create-tags --resources $SUBNET_1_ID --tags Key=Name,Value=$PROJECT_NAME-subnet-1
    aws ec2 create-tags --resources $SUBNET_2_ID --tags Key=Name,Value=$PROJECT_NAME-subnet-2
    print_status "Subnets creadas: $SUBNET_1_ID, $SUBNET_2_ID"
    
    # Crear route table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
    aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
    aws ec2 associate-route-table --subnet-id $SUBNET_1_ID --route-table-id $ROUTE_TABLE_ID
    aws ec2 associate-route-table --subnet-id $SUBNET_2_ID --route-table-id $ROUTE_TABLE_ID
    print_status "Route table configurada: $ROUTE_TABLE_ID"
}

# Crear security groups
create_security_groups() {
    print_status "Creando security groups..."
    
    # Security group para EC2
    EC2_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-ec2-sg --description "Security group for EC2 instance" --vpc-id $VPC_ID --query 'GroupId' --output text)
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
    print_status "Security group EC2 creado: $EC2_SG_ID"
    
    # Security group para RDS
    RDS_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-rds-sg --description "Security group for RDS instance" --vpc-id $VPC_ID --query 'GroupId' --output text)
    aws ec2 authorize-security-group-ingress --group-id $RDS_SG_ID --protocol tcp --port 5432 --source-group $EC2_SG_ID
    print_status "Security group RDS creado: $RDS_SG_ID"
}

# Crear key pair
create_key_pair() {
    print_status "Creando key pair..."
    
    if [ -f "$PROJECT_NAME-key.pem" ]; then
        print_warning "Key pair ya existe, usando existente"
    else
        aws ec2 create-key-pair --key-name $PROJECT_NAME-key --query 'KeyMaterial' --output text > $PROJECT_NAME-key.pem
        chmod 400 $PROJECT_NAME-key.pem
        print_status "Key pair creado: $PROJECT_NAME-key.pem"
    fi
}

# Crear bucket S3
create_s3_bucket() {
    print_status "Creando bucket S3..."
    
    aws s3 mb s3://$S3_BUCKET --region $REGION
    
    # Configurar lifecycle para backups
    cat > s3-lifecycle.json << EOF
{
    "Rules": [
        {
            "ID": "BackupLifecycle",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "backups/"
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ],
            "Expiration": {
                "Days": 365
            }
        }
    ]
}
EOF
    
    aws s3api put-bucket-lifecycle-configuration --bucket $S3_BUCKET --lifecycle-configuration file://s3-lifecycle.json
    print_status "Bucket S3 creado: $S3_BUCKET"
}

# Crear instancia RDS
create_rds_instance() {
    print_status "Creando instancia RDS..."
    
    # Crear subnet group
    aws rds create-db-subnet-group \
        --db-subnet-group-name $PROJECT_NAME-subnet-group \
        --db-subnet-group-description "Subnet group for $PROJECT_NAME" \
        --subnet-ids $SUBNET_1_ID $SUBNET_2_ID
    
    # Generar password seguro
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Crear instancia RDS
    aws rds create-db-instance \
        --db-instance-identifier $PROJECT_NAME-db \
        --db-instance-class $DB_INSTANCE_CLASS \
        --engine postgres \
        --master-username admin \
        --master-user-password $DB_PASSWORD \
        --allocated-storage 20 \
        --db-subnet-group-name $PROJECT_NAME-subnet-group \
        --vpc-security-group-ids $RDS_SG_ID \
        --backup-retention-period 7 \
        --storage-encrypted \
        --tags Key=Name,Value=$PROJECT_NAME-db
    
    print_status "Instancia RDS creada: $PROJECT_NAME-db"
    print_warning "Password de base de datos: $DB_PASSWORD (guárdalo seguro!)"
    
    # Esperar a que RDS esté disponible
    print_status "Esperando a que RDS esté disponible..."
    aws rds wait db-instance-available --db-instance-identifier $PROJECT_NAME-db
    
    # Obtener endpoint
    RDS_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $PROJECT_NAME-db --query 'DBInstances[0].Endpoint.Address' --output text)
    print_status "RDS endpoint: $RDS_ENDPOINT"
}

# Crear instancia EC2
create_ec2_instance() {
    print_status "Creando instancia EC2..."
    
    # Obtener AMI de Ubuntu
    AMI_ID=$(aws ssm get-parameters --names /aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id --query 'Parameters[0].Value' --output text)
    
    # Crear instancia
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $PROJECT_NAME-key \
        --security-group-ids $EC2_SG_ID \
        --subnet-id $SUBNET_1_ID \
        --iam-instance-profile Name=$PROJECT_NAME-ec2-role \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME}]" \
        --query 'Instances[0].InstanceId' --output text)
    
    print_status "Instancia EC2 creada: $INSTANCE_ID"
    
    # Esperar a que esté ejecutándose
    print_status "Esperando a que la instancia esté ejecutándose..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Obtener IP pública
    PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    print_status "IP pública: $PUBLIC_IP"
}

# Crear IAM roles
create_iam_roles() {
    print_status "Creando IAM roles..."
    
    # Trust policy para EC2
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
    
    # Crear role para EC2
    aws iam create-role --role-name $PROJECT_NAME-ec2-role --assume-role-policy-document file://trust-policy.json
    
    # Adjuntar políticas
    aws iam attach-role-policy --role-name $PROJECT_NAME-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
    aws iam attach-role-policy --role-name $PROJECT_NAME-ec2-role --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
    
    # Crear instance profile
    aws iam create-instance-profile --instance-profile-name $PROJECT_NAME-ec2-role
    aws iam add-role-to-instance-profile --instance-profile-name $PROJECT_NAME-ec2-role --role-name $PROJECT_NAME-ec2-role
    
    print_status "IAM roles creados"
}

# Configurar instancia EC2
configure_ec2_instance() {
    print_status "Configurando instancia EC2..."
    
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

# Instalar CloudWatch Agent
sudo apt install -y amazon-cloudwatch-agent

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

echo "✅ Instancia configurada correctamente"
EOF
    
    # Copiar script a la instancia
    scp -i $PROJECT_NAME-key.pem -o StrictHostKeyChecking=no setup_instance.sh ubuntu@$PUBLIC_IP:~/
    
    # Ejecutar script
    ssh -i $PROJECT_NAME-key.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "chmod +x setup_instance.sh && ./setup_instance.sh"
    
    print_status "Instancia EC2 configurada"
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando despliegue automático...${NC}"
    
    check_aws_cli
    create_network_resources
    create_security_groups
    create_key_pair
    create_s3_bucket
    create_iam_roles
    create_rds_instance
    create_ec2_instance
    configure_ec2_instance
    
    echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
    echo ""
    echo -e "${BLUE}📋 INFORMACIÓN DEL DESPLIEGUE:${NC}"
    echo "=================================="
    echo "🌐 IP pública: $PUBLIC_IP"
    echo "🗄️ RDS endpoint: $RDS_ENDPOINT"
    echo "🔑 Key pair: $PROJECT_NAME-key.pem"
    echo "📦 S3 bucket: $S3_BUCKET"
    echo "🔐 DB password: $DB_PASSWORD"
    echo ""
    echo -e "${YELLOW}📝 PRÓXIMOS PASOS:${NC}"
    echo "1. Conectar a la instancia: ssh -i $PROJECT_NAME-key.pem ubuntu@$PUBLIC_IP"
    echo "2. Verificar servicio: sudo systemctl status scjn-scraper"
    echo "3. Ver logs: sudo journalctl -u scjn-scraper -f"
    echo "4. Configurar monitoreo en CloudWatch"
    echo ""
    echo -e "${GREEN}✅ El sistema está funcionando automáticamente en AWS!${NC}"
}

# Ejecutar función principal
main "$@" 