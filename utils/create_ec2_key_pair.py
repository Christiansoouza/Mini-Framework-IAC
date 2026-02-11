import boto3
import os



if __name__ == "__main__":
    key_name = "chris-key"  # Altere se quiser outro nome
    save_path = os.path.dirname(os.path.abspath(__file__))  # Salva na mesma pasta do script
    os.makedirs(save_path, exist_ok=True)
    create_key_pair(key_name, save_path)
