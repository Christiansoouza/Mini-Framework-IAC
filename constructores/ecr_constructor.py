
import os
from constructores.base_constructor import BaseConstructor
from utils.read_template import read_template

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "ecr-stack.yaml"
)


class EcrConstructor(BaseConstructor):
    def __init__(
        self,
        name: str,
        profile: str,
        region: str,
        parameters: dict = {},
    ):
        print(f"Inicializando construtor ECR: {name} na região {region} com perfil {profile}")
        template = read_template(TEMPLATE_PATH)

        super().__init__(
            name=name,
            template_body=template,
            parameters=parameters,
            profile=profile,
            region=region,
        )


    def output(self) -> dict:
        outputs = self._get_outputs()

        return {
            "repository_uri": outputs.get("RepositoryUri"),
        }
    def export_outputs_json(self):
        import json
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output.json")
        # Carrega o arquivo se existir
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
        else:
            data = {}

        data[self.name] = self.output()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Outputs salvos em {output_path}")

    def send_image(self, image_tag: str, image_path: str):
        """Faz o push de uma imagem Docker para o repositório ECR criado, lendo o repository_uri do output.json"""
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

        # 2. Build da imagem
        full_image_name = f"{repository_uri}:{image_tag}"
        print(f"🔨 Construindo imagem Docker: {full_image_name} a partir de {image_path}")
        subprocess.run(["docker", "build", "-t", full_image_name, image_path], check=True)

        # 3. Push da imagem
        print(f"🚀 Fazendo push da imagem para ECR: {full_image_name}")
        subprocess.run(["docker", "push", full_image_name], check=True)

        print(f"✅ Imagem enviada com sucesso para {full_image_name}")