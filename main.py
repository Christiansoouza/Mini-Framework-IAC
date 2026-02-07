from constructores.ecs_constructor import EcsConstructor
from constructores.vpc_constructor import VpcConstructor




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
vpc = VpcConstructor(
    name="vpc-stack-preview",
    profile=profile,
    region=region,
)

vpc.destroy()
pass