#!/usr/bin/env python3
"""
Rebuild container for ARM64 architecture
"""

import subprocess
import json
import os

def rebuild_arm64_container():
    """Rebuild container for ARM64 architecture"""
    print("🔄 Rebuilding container for ARM64 architecture...")
    
    # Load container info
    with open('tacnode-agent-container.json', 'r') as f:
        container_info = json.load(f)
    
    repository_uri = container_info['repository_uri']
    image_name = f"{repository_uri}:latest"
    
    try:
        # Change to agent_runtime directory
        os.chdir('agent_runtime')
        
        # Build ARM64 image
        cmd = [
            'docker', 'buildx', 'build',
            '--platform', 'linux/arm64',
            '-t', image_name,
            '--push',
            '.'
        ]
        
        print(f"🏗️  Building ARM64 image: {image_name}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ ARM64 Docker image built and pushed successfully")
        
        # Change back to parent directory
        os.chdir('..')
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ARM64 build failed: {e.stderr}")
        
        # Try alternative approach with regular build
        print("🔄 Trying alternative build approach...")
        try:
            cmd = [
                'docker', 'build',
                '--platform', 'linux/arm64',
                '-t', image_name,
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Push the image
            push_cmd = ['docker', 'push', image_name]
            result = subprocess.run(push_cmd, capture_output=True, text=True, check=True)
            
            print("✅ ARM64 Docker image built and pushed successfully (alternative method)")
            os.chdir('..')
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"❌ Alternative build also failed: {e2.stderr}")
            os.chdir('..')
            return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        os.chdir('..')
        return False

if __name__ == "__main__":
    success = rebuild_arm64_container()
    if success:
        print("🎉 Container rebuilt for ARM64!")
    else:
        print("❌ Failed to rebuild container")
