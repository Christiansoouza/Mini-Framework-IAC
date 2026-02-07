import os
from .base_constructor import BaseConstructor
from utils.read_template import read_template

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "ecs-stack.yaml"
)

class EcsConstructor(BaseConstructor):
    def __init__(
        self,
        name: str,
        profile: str,
        region: str,
        desired_count: int = 2,
    ):
        print(f"Inicializando construtor ECS: {name} na região {region} com perfil {profile}")
        template = read_template(TEMPLATE_PATH)


        params = {
            "ClusterName": name,
            "DesiredCount": desired_count,
        }

        super().__init__(
            name=name,
            template_body=template,
            parameters=params,
            profile=profile,
            region=region,
        )

    def output(self):
        return {
            "stack_name": self.name
        }
