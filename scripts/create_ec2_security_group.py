import boto3
import os

def create_ec2_security_group(vpc_id, group_name='ec2-file-transfer-sg', description='Allow SSH and outbound for file transfer'):
    ec2 = boto3.client('ec2')
    # Create Security Group
    response = ec2.create_security_group(
        GroupName=group_name,
        Description=description,
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    print(f"Security Group created: {sg_id}")

    # Allow SSH from anywhere (0.0.0.0/0)
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH from anywhere'}]
            }
        ]
    )
    print("Ingress rule for SSH added.")

    # Allow all outbound traffic
    ec2.authorize_security_group_egress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': '-1',
                'FromPort': -1,
                'ToPort': -1,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'All outbound'}]
            }
        ]
    )
    print("Egress rule for all outbound traffic added.")
    return sg_id

if __name__ == '__main__':
    vpc_id = os.environ.get('VPC_ID') or input('Enter VPC ID: ')
    sg_id = create_ec2_security_group(vpc_id)
    print(f"Use this Security Group ID in your EC2 launch: {sg_id}")
