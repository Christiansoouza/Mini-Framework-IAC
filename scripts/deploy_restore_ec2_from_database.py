import boto3
import os
import time
import botocore
from botocore.exceptions import ClientError
from utils.read_json_file import read_json_file

data = read_json_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.json'))


# Dados do RDS
DB_HOST = data.get("endpoint") # Exemplo: metabase-db.xxxxxxxx.region.rds.amazonaws.com DB_PORT = os.getenv('DATABASE_PORT') DB_USER = os.getenv('DATABASE_USER') DB_PASSWORD = os.getenv('DATABASE_PASSWORD') DB_NAME = os.getenv('DATABASE_NAME') BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metabase_backup.sql') VPC_ID = 'vpc-0ca2dd29eb23bc02d' RDS_SG_ID = 'sg-034e3df3d4a62f807'
RDS_SG_ID = data.get("sgs-rds-stack-preview")  # ID do Security Group do RDS
VPC_ID = data.get("vpc-stack-preview")  # ID da VPC

profile_name = "contapessoalatualizada"  
region = "us-east-1" 


BUCKET_NAME =os.getenv('BUCKET_NAME', 'metabase-backups-chris-20260211')
ROLE_NAME =  os.getenv('ROLE_NAME', 'EC2-S3-Backup-Role')
POLICY_NAME = os.getenv('POLICY_NAME', 'S3-Read-Metabase-Backup')
S3_KEY = os.getenv('S3_KEY', 'backups/metabase_backup.sql')
BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metabase_backup.sql')

DB_PORT = os.getenv('DATABASE_PORT', '5432')
DB_USER = os.getenv('DATABASE_USER', 'metabase_user')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD','Metabase2026!#')
DB_NAME = os.getenv('DATABASE_NAME','metabase')

session = boto3.Session(profile_name=profile_name, region_name=region)

import boto3
import json
import time


def create_policy_and_role():
    iam = session.client("iam")

    # 1️⃣ Criar Policy
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }

    try:
        response = iam.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = response["Policy"]["Arn"]
        print("✅ Policy criada")
    except iam.exceptions.EntityAlreadyExistsException:
        policy_arn = f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{POLICY_NAME}"
        print("⚠️ Policy já existe")

    # 2️⃣ Criar Role
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        print("✅ Role criada")
    except iam.exceptions.EntityAlreadyExistsException:
        print("⚠️ Role já existe")

    # 3️⃣ Anexar Policy na Role
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn=policy_arn
    )
    print("✅ Policy anexada na Role")

    # 4️⃣ Criar Instance Profile
    try:
        iam.create_instance_profile(InstanceProfileName=ROLE_NAME)
        print("✅ Instance Profile criado")
    except iam.exceptions.EntityAlreadyExistsException:
        print("⚠️ Instance Profile já existe")

    # Pequena espera (IAM demora alguns segundos)
    time.sleep(5)

    # 5️⃣ Adicionar Role ao Instance Profile
    try:
        iam.add_role_to_instance_profile(
            InstanceProfileName=ROLE_NAME,
            RoleName=ROLE_NAME
        )
        print("✅ Role associada ao Instance Profile")
    except Exception:
        print("⚠️ Role já associada")

    print("🎯 IAM configurado com sucesso!")





def change_sgs_to_allow_ec2_access(ip_address):
  
    ec2 = session.client('ec2')
    # Adiciona regra temporária
    print('Adicionando regra temporária ao SG do RDS...')
    ec2.authorize_security_group_ingress(
        GroupId=RDS_SG_ID,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{
                'CidrIp': f'{ip_address}/32',
                'Description': 'Permite restore temporario'
            }]
        }]
    )
    print('Regra temporária adicionada.')

s3 = session.client("s3")
def create_bucket_if_not_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        print("✅ Bucket já existe.")
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        
        if error_code == 404:
            print("🚀 Criando bucket...")
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": region
                    }
                )
            print("✅ Bucket criado com sucesso.")
        else:
            raise

def upload_file():
    print("📤 Enviando arquivo para o S3...")
    s3.upload_file(BACKUP_FILE, BUCKET_NAME, S3_KEY)
    print("✅ Upload concluído.")

def create_ec2_security_group(vpc_id, group_name='ec2-file-transfer-sg-bashionhost', description='Allow SSH and outbound for file transfer'):
    ec2 = session.client('ec2')
    # Create Security Group
    response = ec2.create_security_group(
        GroupName=group_name,
        Description=description,
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    print(f"Security Group created: {sg_id}")

    # Allow SSH from anywhere (0.0.0.0/0)
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH from anywhere'}]
                }
            ]
        )
        print("Ingress rule for SSH added.")
    except Exception as e:
        if 'InvalidPermission.Duplicate' in str(e):
            print('Ingress rule for SSH already exists, continuing.')
        else:
            print('Erro ao adicionar ingress rule:', e)
    # Allow all outbound traffic
    try:
        ec2.authorize_security_group_egress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'FromPort': -1,
                    'ToPort': -1,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'All outbound'}]
                }
            ]
        )
        print("Egress rule for all outbound traffic added.")
    except Exception as e:
        if 'InvalidPermission.Duplicate' in str(e):
            print('Egress rule already exists, continuing.')
        else:
            print('Erro ao adicionar egress rule:', e)
    return sg_id



def create_key_pair(key_name, save_path):
    ec2 = session.client('ec2')
    try:
        response = ec2.create_key_pair(KeyName=key_name)
        private_key = response['KeyMaterial']
        pem_path = os.path.join(save_path, f"{key_name}.pem")
        with open(pem_path, 'w') as f:
            f.write(private_key)
        os.chmod(pem_path, 0o400)
        print(f"Key pair '{key_name}' criada e salva em: {pem_path}")
        return pem_path
    except ec2.exceptions.ClientError as e:
        if 'InvalidKeyPair.Duplicate' in str(e):
            print(f"Key pair '{key_name}' já existe. Usando existente.")
            return os.path.join(save_path, f"{key_name}.pem")
        else:
            print("Erro ao criar key pair:", e)
            return None


def create_instance_restore():

    # create_policy_and_role()
    # Configurações - preencha com seus dados
    AMI_ID = 'ami-0c1fe732b5494dc14'  # AMI Amazon Linux 2 na sua região
    INSTANCE_TYPE = 't3.micro'
    KEY_NAME = 'chris-key-2'  # Nome do par de chaves EC2
    SECURITY_GROUP_ID = create_ec2_security_group(VPC_ID, 'ec2-restore-sg-bashionhost334s4tesdsdte', 'SG para instancia de restore')  # Cria um SG temporário
    SUBNET_ID = 'subnet-0bc879f0da69c1ef0'  # Subnet privada na VPC
    NAME_FILE = 'metabase_backup.sql'  # Caminho local do backup

    print("Criando instância EC2 para restaurar backup do RDS...")
    print(f"Configurações: AMI={AMI_ID}, Tipo={INSTANCE_TYPE}, Key={KEY_NAME}, SG={SECURITY_GROUP_ID}, Subnet={SUBNET_ID}")
    print("Dados da variavel de ambiente: DB_HOST =", DB_HOST)
    print("Dados da variavel de ambiente: DB_PORT =", DB_PORT)
    print("Dados da variavel de ambiente: DB_USER =", DB_USER)
    print("Dados da variavel de ambiente: DB_PASSWORD =", "****" if DB_PASSWORD else None)
    print("Dados da variavel de ambiente: DB_NAME =", DB_NAME)


    # Salva o .pem na mesma pasta do script
    create_key_pair(KEY_NAME, os.path.dirname(os.path.abspath(__file__)))


    USER_DATA_SCRIPT = f'''#!/bin/bash
    set -e

    LOG_FILE="/home/ec2-user/restore.log"
    BACKUP_FILE="/home/ec2-user/metabase_backup.sql"

    echo "Iniciando script em $(date)" > $LOG_FILE

    yum update -y >> $LOG_FILE 2>&1
    yum install -y postgresql15 aws-cli >> $LOG_FILE 2>&1

    export DB_HOST="{DB_HOST}"
    export DB_PORT="{DB_PORT}"
    export DB_USER="{DB_USER}"
    export DB_PASSWORD="{DB_PASSWORD}"
    export DB_NAME="{DB_NAME}"

    echo "Baixando backup do S3..." >> $LOG_FILE

    aws s3 cp s3://{BUCKET_NAME}/{S3_KEY} . >> $LOG_FILE 2>&1

    if [ ! -f "$NAME_FILE" ]; then
        echo "Erro: arquivo não foi baixado." >> $LOG_FILE
        exit 1
    fi

    echo "Backup baixado com sucesso." >> $LOG_FILE
    echo "Iniciando restore em $(date)" >> $LOG_FILE

    PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -f $BACKUP_FILE >> $LOG_FILE 2>&1

    STATUS=$?

    if [ $STATUS -eq 0 ]; then
        echo "Restore concluído com sucesso em $(date)" >> $LOG_FILE
        shutdown -h now
    else
        echo "Restore falhou em $(date). Verifique o log." >> $LOG_FILE
        exit 1
    fi
    '''



    ec2 = session.resource('ec2')
    print('Criando instância EC2...')
    network_interface = {
        'SubnetId': SUBNET_ID,
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': True,
        'Groups': [SECURITY_GROUP_ID]
    }
    instance = ec2.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[network_interface],
        UserData=USER_DATA_SCRIPT,
        IamInstanceProfile={
            'Name': ROLE_NAME
        },
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'restore-metabase-backup'}]
        }]
    )[0]
    print('Esperando a instância iniciar...')
    instance.wait_until_running()
    instance.reload()
    public_dns = instance.public_dns_name
    ip_address = instance.public_ip_address
    ip_address = instance.private_ip_address if not ip_address else ip_address
    
    if not ip_address:
        print('Atenção: A instância EC2 não recebeu IP público. Verifique se a subnet permite IP público ou ajuste a configuração.')
    else:
        print(f'Instância iniciada: {public_dns} ({ip_address})')
    create_bucket_if_not_exists(BUCKET_NAME)
    upload_file()
    # Copia o arquivo de backup via scp
    print('Copiando arquivo de backup para a EC2...')
    print('A instância será desligada após o restore.')
    print('Aguardando a instância desligar...')


    # Espera a instância ser parada
    instance.wait_until_stopped()
    print('Destruindo a instância EC2...')
    instance.terminate()
    instance.wait_until_terminated()
    print('Instância EC2 destruída com segurança.')

    print('Removendo regra temporária do SG do RDS...')
    ec2.revoke_security_group_ingress(
        GroupId=RDS_SG_ID,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{
                'CidrIp': f'{ip_address}/32'
            }]
        }]
    )
    print('Regra temporária removida. SG do RDS voltou ao normal.')


def run_script():
    create_instance_restore()

if __name__ == '__main__':
    run_script()