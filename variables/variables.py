

import os


PATH_TEMPLATES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
)


ecs_variables = {
    "stack_name": "ecs-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "ecs-stack.yaml"),
    "parameters": {
        "ClusterName": "ecs-cluster-preview",
        "DesiredCount": 2,
    }
}

vpc_variables = {
    "stack_name": "vpc-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "vpc-stack.yaml"),
}

rds_variables = {
    "stack_name": "rds-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "rds-stack.yaml"),
    "parameters": {
        "DBUser": os.getenv("DATABASE_USER"),
        "DBPassword": os.getenv("DATABASE_PASSWORD"),
        "DBName": os.getenv("DATABASE_NAME"),
        "VpcId": "vpc-0ca2dd29eb23bc02d",
        "PrivateSubnets": "subnet-07b5e4eea26504a2d,subnet-08437a2c2e38d53da",
        "ECSSecurityGroup": "sg-034e3df3d4a62f807"
    }
}

sgs_alb_variables = {
    "stack_name": "sgs-alb-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-alb-stack.yaml"),
    "parameters": {
        "VpcId": "vpc-0ca2dd29eb23bc02d",
    }
}

sgs_ecs_variables = {
    "stack_name": "sgs-ecs-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-ecs-stack.yaml"),
    "parameters": {
        "VpcId": "vpc-0ca2dd29eb23bc02d",
        "ALBSecurityGroup": "sg-0a84b9c7621334f6e",
    }
}

sgs_rds_variables = {
    "stack_name": "sgs-rds-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-rds-stack.yaml"),
    "parameters": {
        "VpcId": "vpc-0ca2dd29eb23bc02d",
        "ECSSecurityGroup": "sg-034e3df3d4a62f807"
    }
}

ecr_variables = {
    "stack_name": "ecr-repository",
    "template_path": os.path.join(PATH_TEMPLATES, "ecr-stack.yaml"),
    "parameters": {
        "RepositoryName": "my-app-repo",
    }
}

vpc_endpoint_variables = {
    "stack_name": "vpc-endpoint-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "vpc-endpoint-stack.yaml"),
    "parameters": {
        "VpcId": "vpc-0ca2dd29eb23bc02d",
        "SubnetIds": ["subnet-07b5e4eea26504a2d", "subnet-08437a2c2e38d53da"],
        "SecurityGroupIds": ["sg-034e3df3d4a62f807"]
    }
}