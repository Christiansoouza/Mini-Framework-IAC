from typing import Literal
from constructores.base_constructor import BaseConstructor
from constructores.ecs_constructor import EcsConstructor
from constructores.vpc_constructor import VpcConstructor
from constructores.ecr_constructor import EcrConstructor
from constructores.rds_constructor import RdsConstructor
from constructores.sgs_constructor import SGSConstructor
from scripts.deploy_restore_ec2_from_database import create_instance_restore
from variables.variables import (
    ecs_variables,
    vpc_variables,
    rds_variables,
    sgs_alb_variables,
    sgs_ecs_variables,
    sgs_rds_variables,
    ecr_variables
)


PROFILE = "contapessoalatualizada"
REGION = "us-east-1"



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


            

def executor(variables:dict, constructor_key:str, profile:str, region:str, action:Literal["deploy","plan", "destroy"] = "plan"):

    def action_executor(action:Literal["deploy","plan","destroy"], constructor:BaseConstructor):
        match action:
            case "deploy":
                constructor.deploy()
                constructor.export_outputs_json()
            case "plan":
                constructor.plan()
            case "destroy":
                constructor.destroy()
            case _:
                raise ValueError(f"Ação '{action}' não suportada. Use 'deploy' ou 'plan'.")
            
    constructor_class = constructor_map[constructor_key]

    try:
        print(f"Executando stack: {variables['stack_name']} ({action})")
        constructor = constructor_class(
            name=variables['stack_name'],
            profile=profile,
            region=region,
            template_path=variables['template_path'],
            parameters=variables.get('parameters', {})
        )

        action_executor(action, constructor)

    except Exception as e:
        print(f"Erro ao executar {variables['stack_name']}: {e}")

def run_all():
    stacks = [
        (ecs_variables, "ecs"),
        (vpc_variables, "vpc"),
        (rds_variables, "rds"),
        (sgs_alb_variables, "sgs-alb"),
        (sgs_ecs_variables, "sgs-ecs"),
        (sgs_rds_variables, "sgs-rds"),
        (ecr_variables, "ecr")
    ]

    for vars, key in stacks:
        executor(vars, key, PROFILE, REGION, action="deploy")

def run():
    executor(ecs_variables, "ecs", PROFILE, REGION, "deploy")

def plan():
    executor(ecs_variables, "ecs", PROFILE, REGION, "plan")

if __name__ == "__main__":
    run()