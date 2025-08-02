#!/bin/bash

# AI Agent Integration Demo - Cleanup Script
# This script cleans up the demo environment

set -e  # Exit on any error

echo "🧹 AI Agent Integration Demo - Cleanup Script"
echo "=============================================="
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

# Stop and remove Docker containers
cleanup_docker() {
    print_status "Stopping and removing Docker containers..."
    
    if docker-compose ps -q | grep -q .; then
        docker-compose down -v
        print_success "Docker containers stopped and removed"
    else
        print_status "No Docker containers running"
    fi
    
    # Remove Docker images (optional)
    if [ "${1:-}" = "--remove-images" ]; then
        print_status "Removing Docker images..."
        docker-compose down --rmi all
        print_success "Docker images removed"
    fi
}

# Clean up Python environment
cleanup_python() {
    print_status "Cleaning up Python environment..."
    
    if [ -d "venv" ]; then
        print_status "Removing Python virtual environment..."
        rm -rf venv
        print_success "Python virtual environment removed"
    else
        print_status "No Python virtual environment found"
    fi
}

# Clean up generated data
cleanup_data() {
    print_status "Cleaning up generated data..."
    
    if [ -d "data" ]; then
        print_status "Removing generated data files..."
        rm -rf data
        print_success "Generated data files removed"
    else
        print_status "No generated data files found"
    fi
    
    if [ -d "logs" ]; then
        print_status "Removing log files..."
        rm -rf logs
        print_success "Log files removed"
    else
        print_status "No log files found"
    fi
}

# Clean up environment file
cleanup_env() {
    if [ "${1:-}" = "--remove-env" ]; then
        if [ -f ".env" ]; then
            print_status "Removing .env file..."
            rm .env
            print_success ".env file removed"
        else
            print_status "No .env file found"
        fi
    else
        print_status "Keeping .env file (use --remove-env to remove)"
    fi
}

# Clean up cache files
cleanup_cache() {
    print_status "Cleaning up cache files..."
    
    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # Node.js cache (if exists)
    if [ -d "node_modules" ]; then
        rm -rf node_modules
    fi
    
    if [ -f "package-lock.json" ]; then
        rm package-lock.json
    fi
    
    print_success "Cache files cleaned"
}

# Show cleanup options
show_help() {
    echo "AI Agent Integration Demo - Cleanup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all              Clean everything (containers, images, data, env, cache)"
    echo "  --docker           Stop and remove Docker containers"
    echo "  --remove-images    Also remove Docker images"
    echo "  --python           Remove Python virtual environment"
    echo "  --data             Remove generated data and logs"
    echo "  --remove-env       Remove .env file"
    echo "  --cache            Remove cache files"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Basic cleanup (containers, python, data, cache)"
    echo "  $0 --all           # Complete cleanup including images and .env"
    echo "  $0 --docker        # Only stop Docker containers"
    echo ""
}

# Main cleanup function
main() {
    local remove_images=false
    local remove_env=false
    local clean_docker=true
    local clean_python=true
    local clean_data=true
    local clean_cache=true
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                remove_images=true
                remove_env=true
                clean_docker=true
                clean_python=true
                clean_data=true
                clean_cache=true
                shift
                ;;
            --docker)
                clean_docker=true
                clean_python=false
                clean_data=false
                clean_cache=false
                shift
                ;;
            --remove-images)
                remove_images=true
                shift
                ;;
            --python)
                clean_docker=false
                clean_python=true
                clean_data=false
                clean_cache=false
                shift
                ;;
            --data)
                clean_docker=false
                clean_python=false
                clean_data=true
                clean_cache=false
                shift
                ;;
            --remove-env)
                remove_env=true
                shift
                ;;
            --cache)
                clean_docker=false
                clean_python=false
                clean_data=false
                clean_cache=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "Starting cleanup process..."
    echo ""
    
    # Confirm cleanup
    if [ "$remove_images" = true ] || [ "$remove_env" = true ]; then
        print_warning "This will perform a complete cleanup including:"
        [ "$remove_images" = true ] && echo "  • Docker images"
        [ "$remove_env" = true ] && echo "  • Environment configuration (.env)"
        echo ""
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleanup cancelled"
            exit 0
        fi
    fi
    
    # Perform cleanup
    if [ "$clean_docker" = true ]; then
        if [ "$remove_images" = true ]; then
            cleanup_docker --remove-images
        else
            cleanup_docker
        fi
    fi
    
    if [ "$clean_python" = true ]; then
        cleanup_python
    fi
    
    if [ "$clean_data" = true ]; then
        cleanup_data
    fi
    
    if [ "$remove_env" = true ]; then
        cleanup_env --remove-env
    else
        cleanup_env
    fi
    
    if [ "$clean_cache" = true ]; then
        cleanup_cache
    fi
    
    echo ""
    print_success "Cleanup completed successfully!"
    echo ""
    
    if [ "$remove_env" = false ]; then
        print_status "To run the demo again:"
        print_status "1. Run: ./scripts/setup.sh"
        print_status "2. Run: ./scripts/run_demo.sh"
    else
        print_status "To run the demo again:"
        print_status "1. Run: ./scripts/setup.sh"
        print_status "2. Configure .env file with your credentials"
        print_status "3. Run: ./scripts/run_demo.sh"
    fi
    echo ""
}

# Handle no arguments (default cleanup)
if [ $# -eq 0 ]; then
    main
else
    main "$@"
fi
