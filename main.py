import os
from constructores.ecs_constructor import EcsConstructor
from constructores.vpc_constructor import VpcConstructor
from constructores.ecr_constructor import EcrConstructor
from constructores.rds_constructor import RdsConstructor
from constructores.sgs_constructor import SGSConstructor
from constructores.execute_constructor import ExecuteConstructor
from variables.variables import (
    ecs_variables,
    vpc_variables,
    rds_variables,
    sgs_alb_variables,
    sgs_ecs_variables,
    sgs_rds_variables,
    ecr_variables
)

constructor_map = {
    "ecs": EcsConstructor,
    "vpc": VpcConstructor,
    "rds": RdsConstructor,
    "sgs-alb": SGSConstructor,
    "sgs-ecs": SGSConstructor,
    "sgs-rds": SGSConstructor,
    "ecr": EcrConstructor,
    "vpc-endpoint": VpcConstructor,  # ou outra classe
}

def executor(variables, constructor_key):
    constructor_class = constructor_map[constructor_key]
    try:
        print(f"Executando stack: {variables['stack_name']}")
        constructor = constructor_class(
            name=variables['stack_name'],
            template_path=variables['template_path'],
            parameters=variables.get('parameters', {}),
            # outros argumentos...
        )
        constructor.deploy()
    except Exception as e:
        print(f"Erro ao executar {variables['stack_name']}: {e}")

profile = "contapessoalatualizada"
region = "us-east-1"
name = "ecs-cluster"
desired_count = 1


# ecs = EcsConstructor(
#     name=name,
#     profile=profile,
#     region=region,
#     desired_count=desired_count,
# )

# ecs.plan()
# pass
# ecr_constructor = EcrConstructor(
#     name="ecr-repository",
#     profile=profile,
#     region=region
# )

# ecr_constructor.destroy()
# pass


# vpc = VpcConstructor(
#     name="vpc-stack-preview",
#     profile=profile,
#     region=region
# )
# vpc.deploy()

# from dotenv import load_dotenv

# project_root = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(project_root, "dotenvfiles", ".env")

# print("Caminho do arquivo .env:", env_path)
# if not os.path.exists(env_path):
#     raise FileNotFoundError(f"Arquivo .env não encontrado em: {env_path}")

# load_dotenv(env_path, override=True)
# print("Variáveis de ambiente carregadas com sucesso.")
# print("DATABASE_USER:", os.getenv("DATABASE_USER"))
# print("DATABASE_PASSWORD:", os.getenv("DATABASE_PASSWORD"))
# print("DATABASE_NAME:", os.getenv("DATABASE_NAME"))

rds_constructor = RdsConstructor(
    name="rds-stack-preview",
    profile=profile,
    region=region,
    parameters={
        "DBUser": os.getenv("DATABASE_USER"),
        "DBPassword": os.getenv("DATABASE_PASSWORD"),
        "DBName": os.getenv("DATABASE_NAME"),
        "VpcId": "vpc-0ca2dd29eb23bc02d",
        "PrivateSubnets": ["subnet-07b5e4eea26504a2d", "subnet-08437a2c2e38d53da"],
        "ECSSecurityGroup": "sg-034e3df3d4a62f807"
    }
)

rds_constructor.plan()




# sgs_alb_constructor = SGSConstructor(
#     name="sgs-alb-stack-preview",
#     profile=profile,
#     region=region,
#     parameters={
#         "VpcId": "vpc-0ca2dd29eb23bc02d",
#     }
# )
# sgs_alb_constructor.deploy()
# sgs_alb_constructor.export_outputs_json()

# sgs_ecs_constructor = SGSConstructor(
#     name="sgs-ecs-stack-preview",
#     profile=profile,
#     region=region,
#     parameters={
#         "VpcId": "vpc-0ca2dd29eb23bc02d",
#         "ALBSecurityGroup": "sg-0a84b9c7621334f6e",
#     }
# )
# sgs_ecs_constructor.deploy()
# sgs_ecs_constructor.export_outputs_json()


# sgs_constructor = SGSConstructor(
#     name="sgs-rds-stack-preview",
#     profile=profile,
#     region=region,
#     parameters={
#         "VpcId": "vpc-0ca2dd29eb23bc02d",
#         "ECSSecurityGroup": "sg-034e3df3d4a62f807"
#     }
# )

# sgs_constructor.deploy()
# sgs_constructor.export_outputs_json()
