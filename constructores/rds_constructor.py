from .base_constructor import BaseConstructor
from utils.read_template import read_template
import os

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "rds-stack.yaml"
)


class RdsConstructor(BaseConstructor):
    def __init__(
        self,
        name: str,
        profile: str,
        region: str,
        parameters: dict = {},
    ):
        print(f"Inicializando construtor VPC: {name} na região {region} com perfil {profile}")
        template = read_template(TEMPLATE_PATH)

        super().__init__(
            name=name,
            template_body=template,
            parameters=parameters,
            profile=profile,
            region=region,
        )
    
    def output(self):
        return super().output()
    
    def export_outputs_json(self):
        return super().export_outputs_json()