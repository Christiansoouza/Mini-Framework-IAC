import os
from dotenv import load_dotenv

# Carrega o .env automaticamente ao importar o pacote variables
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, "dotenvfiles", ".env")
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Arquivo .env não encontrado no caminho: {env_path}")
load_dotenv(env_path, override=True)

