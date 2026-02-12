import boto3
import subprocess
import sys
import os

# Configurações
AWS_REGION = 'us-east-1'
PROFILE = 'contapessoalatualizada'  # ajuste para seu profile
REPOSITORY_NAME = os.getenv('REPOSITORY_NAME')
ECR_IMAGE = os.getenv('ECR_IMAGE')

session = boto3.Session(profile_name=PROFILE, region_name=AWS_REGION)
ecr = session.client('ecr')

# 1. Cria o repositório se não existir
def create_ecr_repository(repo_name):
    try:
        response = ecr.create_repository(repositoryName=repo_name)
        print(f'Repositório {repo_name} criado.')
        return response['repository']['repositoryUri']
    except ecr.exceptions.RepositoryAlreadyExistsException:
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        print(f'Repositório {repo_name} já existe.')
        return response['repositories'][0]['repositoryUri']

# 2. Login no ECR
def ecr_login(repository_uri):
    print('Fazendo login no ECR...')
    password = session.client('ecr').get_authorization_token()['authorizationData'][0]['authorizationToken']
    endpoint = repository_uri.split('/')[0]
    login_cmd = f'aws ecr get-login-password --region {AWS_REGION} --profile {PROFILE} | docker login --username AWS --password-stdin {endpoint}'
    result = subprocess.run(login_cmd, shell=True)
    if result.returncode != 0:
        print('Erro ao fazer login no ECR.')
        sys.exit(1)
    print('Login realizado com sucesso.')

# 3. Garante que a imagem existe localmente (faz pull do Docker Hub se necessário) e tagueia para o ECR
def ensure_image_and_tag(local_image, repository_uri):
    # Verifica se a imagem existe localmente
    check_cmd = f'docker image inspect {local_image}'
    result = subprocess.run(check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        # Se não existe, faz pull do Docker Hub
        print(f'Imagem {local_image} não encontrada localmente. Fazendo pull do Docker Hub...')
        pull_cmd = f'docker pull {local_image}'
        result_pull = subprocess.run(pull_cmd, shell=True)
        if result_pull.returncode != 0:
            print('Erro ao fazer pull da imagem do Docker Hub.')
            sys.exit(1)
        print('Pull realizado com sucesso.')
    # Tagueia para o ECR
    tag_cmd = f'docker tag {local_image} {repository_uri}:latest'
    print(f'Tagging: {tag_cmd}')
    result_tag = subprocess.run(tag_cmd, shell=True)
    if result_tag.returncode != 0:
        print('Erro ao taguear a imagem.')
        sys.exit(1)

# 4. Push para o ECR
def push_image(repository_uri):
    push_cmd = f'docker push {repository_uri}:latest'
    print(f'Push: {push_cmd}')
    result = subprocess.run(push_cmd, shell=True)
    if result.returncode != 0:
        print('Erro ao enviar a imagem.')
        sys.exit(1)
    print('Imagem enviada com sucesso!')

if __name__ == '__main__':
    repo_uri = create_ecr_repository(REPOSITORY_NAME) 
    ecr_login(repo_uri) 
    ensure_image_and_tag(ECR_IMAGE, repo_uri) 
    push_image(repo_uri)