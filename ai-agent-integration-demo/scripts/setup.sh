#!/bin/bash

# AI Agent Integration Demo - Setup Script
# This script sets up the complete demo environment

set -e  # Exit on any error

echo "🚀 AI Agent Integration Demo - Setup Script"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detected"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Windows (WSL/Cygwin) detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ is required but not found"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker $DOCKER_VERSION found"
    else
        print_error "Docker is required but not found"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker Compose $COMPOSE_VERSION found"
    else
        print_error "Docker Compose is required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_warning "Node.js not found - some Strands SDK features may be limited"
    fi
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1)
        print_success "$AWS_VERSION found"
    else
        print_warning "AWS CLI not found - please configure manually"
    fi
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Setup environment variables
setup_env_vars() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your credentials before running the demo"
        print_warning "Required: AWS credentials, Tacnode connection details"
    else
        print_success ".env file already exists"
    fi
}

# Setup Docker services
setup_docker_services() {
    print_status "Setting up Docker services..."
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Pull required images
    print_status "Pulling Docker images..."
    docker-compose pull
    
    # Start services
    print_status "Starting Docker services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_status "Checking service health..."
    
    # Check PostgreSQL (Tacnode)
    if docker-compose exec -T tacnode pg_isready -U tacnode_user -d ai_agents_demo &> /dev/null; then
        print_success "Tacnode database is ready"
    else
        print_error "Tacnode database is not ready"
        exit 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis is ready"
    else
        print_error "Redis is not ready"
        exit 1
    fi
    
    print_success "All Docker services are running"
}

# Initialize databases
initialize_databases() {
    print_status "Initializing databases..."
    
    # Activate Python environment
    source venv/bin/activate
    
    # Initialize Tacnode stores
    print_status "Initializing Tacnode stores..."
    python -c "
import asyncio
from src.stage3_tacnode_complete import TacnodeCompleteAgent

async def init():
    agent = TacnodeCompleteAgent()
    await agent.initialize()
    print('Tacnode stores initialized successfully')

asyncio.run(init())
"
    
    print_success "Databases initialized"
}

# Verify setup
verify_setup() {
    print_status "Verifying setup..."
    
    # Activate Python environment
    source venv/bin/activate
    
    # Test database connections
    print_status "Testing database connections..."
    python -c "
import psycopg2
import redis

# Test PostgreSQL
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='ai_agents_demo',
        user='tacnode_user',
        password='tacnode_password'
    )
    conn.close()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')

# Test Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"
    
    # Test AWS credentials (if configured)
    if [ -f ".env" ] && grep -q "AWS_ACCESS_KEY_ID" .env; then
        print_status "Testing AWS credentials..."
        python -c "
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    print('✅ AWS Bedrock access configured')
except Exception as e:
    print(f'⚠️  AWS Bedrock access not configured: {e}')
"
    else
        print_warning "AWS credentials not configured in .env file"
    fi
    
    print_success "Setup verification completed"
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    check_os
    check_prerequisites
    setup_python_env
    setup_env_vars
    setup_docker_services
    initialize_databases
    verify_setup
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your credentials"
    echo "2. Run the demo: ./scripts/run_demo.sh"
    echo "3. Or run individual stages:"
    echo "   - Stage 1: python src/stage1_basic_agentcore.py"
    echo "   - Stage 2: python src/stage2_strands_enhanced.py"
    echo "   - Stage 3: python src/stage3_tacnode_complete.py"
    echo ""
    echo "For troubleshooting, see: docs/troubleshooting/README.md"
    echo ""
}

# Run main function
main "$@"
