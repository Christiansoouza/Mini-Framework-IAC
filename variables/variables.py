import os
from utils.read_json_file import read_json_file

PATH_TEMPLATES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
)

DATA_OUTPUT = read_json_file(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output.json')
)

PROJECT_NAME = "metabase"
ENVIRONMENT = 'hml'

ecs_variables = {
    "stack_name": "ecs-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "ecs-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "VpcId": DATA_OUTPUT["VpcId"],
        "SubnetIds": ",".join(DATA_OUTPUT["SubnetIds"]),
        "SecurityGroupIds": ",".join(DATA_OUTPUT["SecurityGroupIds"]),
        "ContainerImage": DATA_OUTPUT["ContainerImage"],
        "ContainerCpu": 1024,
        "ContainerMemory": 2048,
        "TaskFamily": "metabase-task",
        "ContainerName": "metabase",
        "ContainerPort": 3000,
        "NetworkMode": "awsvpc",
        "OperatingSystemFamily": "LINUX",
        "RdsEndpoint": DATA_OUTPUT["RdsEndpoint"],
        "RdsDbName": "metabase",
        "DatabaseSecretArn": DATA_OUTPUT["DatabaseSecretArn"],
        "MaxTaskCount": 4,
        "TargetGroupArn": DATA_OUTPUT["TargetGroupArn"]
    }
}

vpc_variables = {
    "stack_name": "vpc-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "vpc-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
    }
}

rds_variables = {
    "stack_name": "rds-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "rds-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "DBUser": os.getenv("DATABASE_USER"),
        "DBPassword": os.getenv("DATABASE_PASSWORD"),
        "DBName": os.getenv("DATABASE_NAME"),
        "VpcId": DATA_OUTPUT["VpcId"],
        "PrivateSubnets": ",".join(DATA_OUTPUT["PrivateSubnets"]),
        "ECSSecurityGroup": DATA_OUTPUT["ECSSecurityGroup"]
    }
}

sgs_alb_variables = {
    "stack_name": "sgs-alb-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-alb-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "VpcId": DATA_OUTPUT["VpcId"],
    }
}

sgs_ecs_variables = {
    "stack_name": "sgs-ecs-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-ecs-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "VpcId": DATA_OUTPUT["VpcId"],
        "ALBSecurityGroup": DATA_OUTPUT["ALBSecurityGroup"],
    }
}

sgs_rds_variables = {
    "stack_name": "sgs-rds-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "security-groups/sgs-rds-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "VpcId": DATA_OUTPUT["VpcId"],
        "ECSSecurityGroup": DATA_OUTPUT["ECSSecurityGroup"],
    }
}

ecr_variables = {
    "stack_name": "ecr-repository",
    "template_path": os.path.join(PATH_TEMPLATES, "ecr-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "RepositoryName": "my-app-repo",
    }
}

vpc_endpoint_variables = {
    "stack_name": "vpc-endpoint-stack-preview",
    "template_path": os.path.join(PATH_TEMPLATES, "vpc-endpoint-stack.yaml"),
    "parameters": {
        "ProjectName": PROJECT_NAME,
        "Environment": ENVIRONMENT,
        "VpcId": DATA_OUTPUT["VpcId"],
        "SubnetIds": ",".join(DATA_OUTPUT["PrivateSubnets"]),
        "SecurityGroupIds": ",".join(DATA_OUTPUT["ECSSecurityGroup"])
    }
}