import boto3
import requests
import os

# Configurações
RDS_SG_ID = 'sg-034e3df3d4a62f807'  # Altere para o SG do seu RDS

profile_name = "contapessoalatualizada"  # Altere para o nome do profile desejado
region = "us-east-1"  # Altere para a região desejada

session = boto3.Session(profile_name=profile_name, region_name=region)
ec2 = session.client('ec2')

def get_my_ip():
    # Busca apenas IPv4
    try:
        ip = requests.get('https://api.ipify.org').text.strip()
        # Valida se é IPv4
        import ipaddress
        ipaddress.IPv4Address(ip)
        return ip
    except Exception:
        print('Não foi possível obter IPv4 público. Informe manualmente:')
        return input('Seu IPv4 público: ')

def liberar_ip():
    ip = get_my_ip()
    print(f"Liberando IP {ip} no SG {RDS_SG_ID} (porta 5432)...")
    try:
        ec2.authorize_security_group_ingress(
            GroupId=RDS_SG_ID,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'IpRanges': [{
                    'CidrIp': f'{ip}/32',
                    'Description': 'restore-temp'
                }]
            }]
        )
        print('Regra adicionada.')
    except Exception as e:
        if 'InvalidPermission.Duplicate' in str(e):
            print('Regra já existe no SG, seguindo normalmente.')
        else:
            print('Erro ao adicionar regra no SG:', e)
    return ip

def remover_ip(ip):
    print(f"Removendo IP {ip} do SG {RDS_SG_ID}...")
    ec2.revoke_security_group_ingress(
        GroupId=RDS_SG_ID,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{
                'CidrIp': f'{ip}/32'
            }]
        }]
    )
    print('Regra removida.')

if __name__ == '__main__':
    ip = liberar_ip()

    # Inputs para dados do banco e backup
    DB_HOST = "metabase-db.copgisqwgh9a.us-east-1.rds.amazonaws.com"  # Exemplo: metabase-db.xxxxxxxx.region.rds.amazonaws.com
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    DB_USER = os.getenv('DATABASE_USER', 'metabase_user')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD','Metabase2026!#')
    DB_NAME = os.getenv('DATABASE_NAME','metabase')
    BACKUP_FILE = 'metabase_backup.sql'  # Caminho local do backup a ser restaurado

    print('Iniciando restore do backup Postgres...')
    import subprocess
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    restore_cmd = [
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-f', BACKUP_FILE
    ]
    try:
        result = subprocess.run(restore_cmd, env=env, check=True)
        print('Restore concluído com sucesso.')
    except Exception as e:
        print('Erro ao restaurar o backup:', e)
    remover_ip(ip)
    print('Pronto! SG do RDS voltou ao normal.')
