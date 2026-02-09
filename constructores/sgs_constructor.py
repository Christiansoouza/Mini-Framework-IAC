from constructores.base_constructor import BaseConstructor
from utils.read_template import read_template
import os

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "security-groups",
    "sgs-rds-stack.yaml"
)

class SGSConstructor(BaseConstructor):
    """
    Construtor para Security Groups (ALB, ECS, RDS) via CloudFormation.
    """
    def __init__(self, name, profile, region, parameters=None):
        print(f"Inicializando SGSConstructor: {name} na região {region} com perfil {profile}")
        template_body = read_template(TEMPLATE_PATH)
        super().__init__(
            name=name,
            template_body=template_body,
            parameters=parameters or {},
            profile=profile,
            region=region
        )

    def output(self):
        return super().output()

    def export_outputs_json(self):
        import os
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
		
