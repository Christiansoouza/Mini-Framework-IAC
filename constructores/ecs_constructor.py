import os
from .base_constructor import BaseConstructor
from utils.read_template import read_template


class EcsConstructor(BaseConstructor):
    def __init__(
        self,
        template_path:str,
        name: str,
        profile: str,
        region: str,
        desired_count: int = 2,
    ):
        print(f"Inicializando construtor ECS: {name} na região {region} com perfil {profile}")
        template = read_template(template_path)


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
