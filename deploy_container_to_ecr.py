#!/usr/bin/env python3
"""
Deploy TACNode Agent Container to Amazon ECR
"""

import boto3
import subprocess
import json
import time
import os
from datetime import datetime

class ECRDeployment:
    """Handle ECR repository creation and container deployment"""
    
    def __init__(self):
        self.ecr = boto3.client('ecr', region_name='us-east-1')
        self.sts = boto3.client('sts', region_name='us-east-1')
        
        # Get account ID
        self.account_id = self.sts.get_caller_identity()['Account']
        self.region = 'us-east-1'
        self.repository_name = 'tacnode-agentcore-runtime'
        self.image_tag = 'latest'
        
        print(f"🏗️  ECR Deployment Configuration:")
        print(f"   Account ID: {self.account_id}")
        print(f"   Region: {self.region}")
        print(f"   Repository: {self.repository_name}")
        print(f"   Tag: {self.image_tag}")
    
    def create_ecr_repository(self):
        """Create ECR repository if it doesn't exist"""
        print("\n📦 Creating ECR Repository...")
        
        try:
            # Check if repository exists
            response = self.ecr.describe_repositories(repositoryNames=[self.repository_name])
            print(f"✅ Repository '{self.repository_name}' already exists")
            repository_uri = response['repositories'][0]['repositoryUri']
            
        except self.ecr.exceptions.RepositoryNotFoundException:
            # Create repository
            print(f"🔨 Creating new repository '{self.repository_name}'...")
            
            response = self.ecr.create_repository(
                repositoryName=self.repository_name,
                imageScanningConfiguration={'scanOnPush': True},
                encryptionConfiguration={'encryptionType': 'AES256'},
                tags=[
                    {'Key': 'Project', 'Value': 'TACNodeAgentCore'},
                    {'Key': 'Environment', 'Value': 'Production'},
                    {'Key': 'Purpose', 'Value': 'AgentCoreRuntime'}
                ]
            )
            
            repository_uri = response['repository']['repositoryUri']
            print(f"✅ Created repository: {repository_uri}")
        
        except Exception as e:
            print(f"❌ Error with ECR repository: {e}")
            return None
        
        return repository_uri
    
    def get_docker_login_token(self):
        """Get Docker login token for ECR"""
        print("\n🔐 Getting ECR login token...")
        
        try:
            response = self.ecr.get_authorization_token()
            token = response['authorizationData'][0]['authorizationToken']
            endpoint = response['authorizationData'][0]['proxyEndpoint']
            
            print(f"✅ Got authorization token for {endpoint}")
            return token, endpoint
            
        except Exception as e:
            print(f"❌ Error getting ECR token: {e}")
            return None, None
    
    def docker_login(self, token, endpoint):
        """Login to ECR with Docker"""
        print("\n🐳 Logging into ECR with Docker...")
        
        try:
            # Decode token and login
            import base64
            username, password = base64.b64decode(token).decode().split(':')
            
            cmd = [
                'docker', 'login',
                '--username', username,
                '--password-stdin',
                endpoint
            ]
            
            result = subprocess.run(
                cmd,
                input=password,
                text=True,
                capture_output=True,
                check=True
            )
            
            print("✅ Docker login successful")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker login failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Docker login error: {e}")
            return False
    
    def build_docker_image(self, repository_uri):
        """Build the Docker image"""
        print("\n🔨 Building Docker image...")
        
        try:
            # Change to agent_runtime directory
            os.chdir('agent_runtime')
            
            # Build image
            image_name = f"{repository_uri}:{self.image_tag}"
            
            cmd = [
                'docker', 'build',
                '-t', image_name,
                '.'
            ]
            
            print(f"🏗️  Building image: {image_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Docker image built successfully")
            print(f"   Image: {image_name}")
            
            # Change back to parent directory
            os.chdir('..')
            
            return image_name
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker build failed: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ Docker build error: {e}")
            return None
    
    def push_docker_image(self, image_name):
        """Push Docker image to ECR"""
        print(f"\n📤 Pushing image to ECR: {image_name}")
        
        try:
            cmd = ['docker', 'push', image_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Docker image pushed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker push failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Docker push error: {e}")
            return False
    
    def verify_image_in_ecr(self):
        """Verify the image was pushed to ECR"""
        print("\n🔍 Verifying image in ECR...")
        
        try:
            response = self.ecr.describe_images(
                repositoryName=self.repository_name,
                imageIds=[{'imageTag': self.image_tag}]
            )
            
            if response['imageDetails']:
                image = response['imageDetails'][0]
                print("✅ Image verified in ECR:")
                print(f"   Image digest: {image['imageDigest']}")
                print(f"   Image size: {image['imageSizeInBytes']} bytes")
                print(f"   Pushed at: {image['imagePushedAt']}")
                return True
            else:
                print("❌ Image not found in ECR")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying image: {e}")
            return False
    
    def deploy_complete_container(self):
        """Complete container deployment process"""
        print("🚀 Starting Complete Container Deployment")
        print("=" * 60)
        
        # Step 1: Create ECR repository
        repository_uri = self.create_ecr_repository()
        if not repository_uri:
            return None
        
        # Step 2: Get Docker login token
        token, endpoint = self.get_docker_login_token()
        if not token:
            return None
        
        # Step 3: Docker login
        if not self.docker_login(token, endpoint):
            return None
        
        # Step 4: Build Docker image
        image_name = self.build_docker_image(repository_uri)
        if not image_name:
            return None
        
        # Step 5: Push Docker image
        if not self.push_docker_image(image_name):
            return None
        
        # Step 6: Verify image in ECR
        if not self.verify_image_in_ecr():
            return None
        
        print("\n" + "="*60)
        print("🎉 CONTAINER DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        
        print(f"\n✅ CONTAINER DETAILS:")
        print(f"   Repository URI: {repository_uri}")
        print(f"   Image Name: {image_name}")
        print(f"   Account ID: {self.account_id}")
        print(f"   Region: {self.region}")
        
        # Save container info for next steps
        container_info = {
            'repository_uri': repository_uri,
            'image_name': image_name,
            'account_id': self.account_id,
            'region': self.region,
            'repository_name': self.repository_name,
            'image_tag': self.image_tag,
            'deployed_at': datetime.now().isoformat()
        }
        
        with open('tacnode-agent-container.json', 'w') as f:
            json.dump(container_info, f, indent=2)
        
        print(f"✅ Container info saved to: tacnode-agent-container.json")
        
        return container_info

def main():
    print("🐳 TACNode Agent Container Deployment to ECR")
    print("=" * 60)
    
    deployment = ECRDeployment()
    
    try:
        # Deploy container
        container_info = deployment.deploy_complete_container()
        
        if container_info:
            print("\n🎯 READY FOR AGENTCORE RUNTIME DEPLOYMENT!")
            print("   Container is now available in ECR")
            print("   Ready to create AgentCore Runtime")
        else:
            print("\n❌ Container deployment failed")
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()
