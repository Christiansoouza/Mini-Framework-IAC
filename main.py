from constructores.ecs_constructor import EcsConstructor
from constructores.vpc_constructor import VpcConstructor
from constructores.ecr_constructor import EcrConstructor




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
ecr_constructor = EcrConstructor(
    name="ecr-repository",
    profile=profile,
    region=region
)

ecr_constructor.destroy()
pass