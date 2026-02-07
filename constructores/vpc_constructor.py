
import os
from models.vpc_models import VpcModel
from constructores.base_constructor import BaseConstructor
from utils.read_template import read_template

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "vpc-stack.yaml"
)


class VpcConstructor(BaseConstructor):
    def __init__(
        self,
        name: str,
        profile: str,
        region: str,
    ):
        print(f"Inicializando construtor VPC: {name} na região {region} com perfil {profile}")
        template = read_template(TEMPLATE_PATH)


        params = None


        super().__init__(
            name=name,
            template_body=template,
            parameters=params,
            profile=profile,
            region=region,
        )

    def output(self) -> VpcModel:
        outputs = self._get_outputs()

        return VpcModel(
            vpc_id=outputs.get("VpcId"),
            public_subnets=[
                outputs.get("PublicSubnet1Id"),
                outputs.get("PublicSubnet2Id"),
            ],
            private_subnets=[
                outputs.get("PrivateSubnet1Id"),
                outputs.get("PrivateSubnet2Id"),
            ],
        )
    def export_outputs_json(self):
        ...