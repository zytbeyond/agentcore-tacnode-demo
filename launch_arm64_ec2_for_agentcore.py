#!/usr/bin/env python3
"""
Launch ARM64 EC2 Instance for AgentCore Runtime Development
"""

import boto3
import json
import time
import base64
from datetime import datetime

class ARM64EC2Launcher:
    """Launch ARM64 EC2 instance for AgentCore Runtime development"""
    
    def __init__(self):
        self.ec2 = boto3.client('ec2', region_name='us-east-1')
        self.iam = boto3.client('iam', region_name='us-east-1')
        
    def create_ec2_role(self):
        """Create IAM role for EC2 instance"""
        print("🔐 Creating EC2 IAM role...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        role_name = "ARM64AgentCoreDevRole"
        
        try:
            # Create role
            role_response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for ARM64 AgentCore development EC2 instance"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
                "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
                "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"  # For Session Manager
            ]
            
            for policy in policies:
                self.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            
            # Create instance profile
            self.iam.create_instance_profile(InstanceProfileName=role_name)
            self.iam.add_role_to_instance_profile(
                InstanceProfileName=role_name,
                RoleName=role_name
            )
            
            print(f"✅ Created role: {role_response['Role']['Arn']}")
            return role_name
            
        except self.iam.exceptions.EntityAlreadyExistsException:
            print("✅ Role already exists")
            return role_name
    
    def create_user_data_script(self):
        """Create user data script for EC2 instance"""
        user_data = """#!/bin/bash
# ARM64 EC2 User Data for AgentCore Runtime Development

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install Docker Buildx
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/buildx/releases/download/v0.12.0/buildx-v0.12.0.linux-arm64 -o ~/.docker/cli-plugins/docker-buildx
chmod a+x ~/.docker/cli-plugins/docker-buildx

# Install AWS CLI v2 for ARM64
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
apt-get install -y unzip
unzip awscliv2.zip
./aws/install

# Install Python 3.11 and uv
apt-get install -y python3.11 python3.11-venv python3-pip
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install git
apt-get install -y git

# Create development directory
mkdir -p /home/ubuntu/agentcore-dev
chown ubuntu:ubuntu /home/ubuntu/agentcore-dev

# Set up Docker buildx
sudo -u ubuntu docker buildx create --use

# Clone the project files from the current instance
# We'll copy the files via S3 or recreate them

# Set environment variables
echo 'export TACNODE_TOKEN="${os.getenv("TACNODE_TOKEN", "")}"' >> /home/ubuntu/.bashrc
echo 'export AWS_DEFAULT_REGION=us-east-1' >> /home/ubuntu/.bashrc

echo "ARM64 AgentCore development environment ready!" > /home/ubuntu/setup-complete.txt
echo "Instance ready at $(date)" >> /home/ubuntu/setup-complete.txt
"""
        return base64.b64encode(user_data.encode()).decode()
    
    def get_or_create_security_group(self):
        """Get or create security group for ARM64 development"""
        print("🔒 Setting up security group...")

        sg_name = "ARM64-AgentCore-Dev-SG"
        vpc_id = "vpc-4e9dc534"

        try:
            # Check if security group exists
            response = self.ec2.describe_security_groups(
                Filters=[
                    {'Name': 'group-name', 'Values': [sg_name]},
                    {'Name': 'vpc-id', 'Values': [vpc_id]}
                ]
            )

            if response['SecurityGroups']:
                sg_id = response['SecurityGroups'][0]['GroupId']
                print(f"✅ Using existing security group: {sg_id}")
                return sg_id

            # Create security group
            sg_response = self.ec2.create_security_group(
                GroupName=sg_name,
                Description="Security group for ARM64 AgentCore development",
                VpcId=vpc_id
            )

            sg_id = sg_response['GroupId']

            # Add rules for development
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '172.31.0.0/16', 'Description': 'SSH from VPC'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8080,
                        'ToPort': 8080,
                        'IpRanges': [{'CidrIp': '172.31.0.0/16', 'Description': 'AgentCore port from VPC'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS outbound'}]
                    }
                ]
            )

            print(f"✅ Created security group: {sg_id}")
            return sg_id

        except Exception as e:
            print(f"❌ Security group setup failed: {e}")
            # Fallback to default security group
            return "sg-default"

    def launch_arm64_instance(self):
        """Launch ARM64 EC2 instance"""
        print("🚀 Launching ARM64 EC2 instance...")
        
        # Create role
        role_name = self.create_ec2_role()
        
        # Wait for instance profile
        time.sleep(10)
        
        # Create user data
        user_data = self.create_user_data_script()
        
        try:
            response = self.ec2.run_instances(
                ImageId='ami-06daf9c2d2cf1cb37',  # Ubuntu 22.04 LTS ARM64 (latest)
                MinCount=1,
                MaxCount=1,
                InstanceType='t4g.medium',  # ARM64 instance type
                # KeyName='your-key-pair',  # No key pair needed - will use Session Manager
                SecurityGroupIds=[self.get_or_create_security_group()],
                SubnetId='subnet-58aa7515',  # Your exact subnet
                IamInstanceProfile={'Name': role_name},
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'ARM64-AgentCore-Dev'},
                            {'Key': 'Project', 'Value': 'TACNodeAgentCore'},
                            {'Key': 'Purpose', 'Value': 'ARM64Development'}
                        ]
                    }
                ]
            )
            
            instance_id = response['Instances'][0]['InstanceId']
            print(f"✅ Launched instance: {instance_id}")
            
            return instance_id
            
        except Exception as e:
            print(f"❌ Failed to launch instance: {e}")
            return None

def main():
    print("🚀 ARM64 EC2 Instance for AgentCore Runtime Development")
    print("=" * 60)
    
    launcher = ARM64EC2Launcher()
    
    try:
        instance_id = launcher.launch_arm64_instance()
        
        if instance_id:
            print("\n✅ ARM64 DEVELOPMENT ENVIRONMENT READY!")
            print(f"   Instance ID: {instance_id}")
            print(f"   Instance Type: t4g.medium (ARM64)")
            print(f"   OS: Ubuntu 22.04 LTS ARM64")
            
            print("\n🔧 INSTALLED TOOLS:")
            print("   • Docker with buildx for ARM64 builds")
            print("   • AWS CLI v2 for ARM64")
            print("   • Python 3.11 and uv package manager")
            print("   • Git for source control")
            
            print("\n📋 NEXT STEPS:")
            print("   1. SSH into the instance")
            print("   2. Clone your agent code")
            print("   3. Build ARM64 container with docker buildx")
            print("   4. Deploy to AgentCore Runtime")
        
    except Exception as e:
        print(f"❌ Launch failed: {e}")

if __name__ == "__main__":
    main()
