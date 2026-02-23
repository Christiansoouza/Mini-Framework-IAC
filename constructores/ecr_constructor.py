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