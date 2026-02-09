
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
