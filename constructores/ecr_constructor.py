
import os
from constructores.base_constructor import BaseConstructor
from utils.read_template import read_template

class EcrConstructor(BaseConstructor):
    def __init__(
        self,
        template_path:str,
        name: str,
        profile: str,
        region: str,
        parameters: dict = {},
    ):
        print(f"Inicializando construtor ECR: {name} na região {region} com perfil {profile}")
        template = read_template(template_path)

        super().__init__(
            name=name,
            template_body=template,
            parameters=parameters,
            profile=profile,
            region=region,
        )

    def send_image(self, image_tag: str = "latest", source_image: str = "metabase/metabase:latest"):
        """
        Faz pull da imagem do Metabase (ou outra), faz tag para o ECR privado e faz push para uso em subnet privada.
        :param image_tag: Tag a ser usada no ECR (ex: 'latest')
        :param source_image: Imagem de origem (ex: 'metabase/metabase:latest')
        """
        import subprocess
        import json
        import os

        # Caminho do output.json
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output.json")
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Arquivo de outputs não encontrado: {output_path}")

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Busca pelo nome do stack
        stack_outputs = data.get(self.name)
        if not stack_outputs:
            raise ValueError(f"Outputs para o stack '{self.name}' não encontrados em {output_path}")

        repository_uri = stack_outputs.get("repository_uri")
        if not repository_uri:
            raise ValueError("URI do repositório ECR não encontrado nos outputs do arquivo JSON")

        # 1. Login no ECR
        region = self.session.region_name
        profile = self.session.profile_name
        login_cmd = [
            "aws", "ecr", "get-login-password",
            "--region", region,
            "--profile", profile
        ]
        login_proc = subprocess.run(login_cmd, capture_output=True, check=True, text=True)
        subprocess.run(
            [
                "docker", "login",
                "--username", "AWS",
                "--password-stdin",
                repository_uri.split('/')[0]
            ],
            input=login_proc.stdout,
            check=True,
            text=True
        )

        # 2. Pull da imagem do Docker Hub
        print(f"⬇️  Fazendo pull da imagem de origem: {source_image}")
        subprocess.run(["docker", "pull", source_image], check=True)

        # 3. Tag para o ECR
        full_image_name = f"{repository_uri}:{image_tag}"
        print(f"🏷  Taggeando imagem para: {full_image_name}")
        subprocess.run(["docker", "tag", source_image, full_image_name], check=True)

        # 4. Push da imagem
        print(f"🚀 Fazendo push da imagem para ECR: {full_image_name}")
        subprocess.run(["docker", "push", full_image_name], check=True)

        print(f"✅ Imagem enviada com sucesso para {full_image_name}")