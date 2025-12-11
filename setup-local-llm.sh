#!/bin/bash

# ============================================================================
# Setup Local LLM (Ollama) for GitHub Commits Verifier Bot
# ============================================================================
# This script sets up Ollama and pulls a model for local AI analysis
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Install Docker: https://docs.docker.com/install"
        exit 1
    fi
    print_success "Docker is installed"
}

# Check Docker daemon
check_docker_daemon() {
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Start Docker and try again"
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Detect available GPUs
detect_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        print_success "NVIDIA GPU detected 🚀"
        return 0
    else
        print_warning "No NVIDIA GPU detected (CPU only, slower)"
        return 1
    fi
}

# Select model
select_model() {
    print_header "🤖 Select Model"
    
    echo "Choose which model to download:"
    echo ""
    echo "1) mistral           (7B, RECOMMENDED - fast + good quality)"
    echo "2) neural-chat       (7B, optimized for conversations)"
    echo "3) llama2            (7B, best quality but slower)"
    echo "4) dolphin-mixtral   (8.7B, smart + fast)"
    echo "5) openchat          (3.5B, ultra-light for low RAM)"
    echo "6) zephyr            (7B, good balance)"
    echo ""
    
    read -p "Enter choice (1-6, default 1): " choice
    choice=${choice:-1}
    
    case $choice in
        1) MODEL="mistral" ;;
        2) MODEL="neural-chat" ;;
        3) MODEL="llama2" ;;
        4) MODEL="dolphin-mixtral" ;;
        5) MODEL="openchat" ;;
        6) MODEL="zephyr" ;;
        *) MODEL="mistral" ;;
    esac
    
    print_success "Selected model: $MODEL"
}

# Start Ollama container
start_ollama() {
    print_header "📁 Starting Ollama Container"
    
    # Check if Ollama is already running
    if docker ps | grep -q ollama; then
        print_info "Ollama container is already running"
        return 0
    fi
    
    # Check if container exists but is stopped
    if docker ps -a | grep -q ollama; then
        print_info "Starting existing Ollama container..."
        docker start ollama
        sleep 5
        return 0
    fi
    
    # Start new container
    print_info "Pulling Ollama image..."
    docker pull ollama/ollama
    
    print_info "Starting Ollama container..."
    
    # Check for GPU support
    if detect_gpu; then
        # Use GPU
        docker run -d \
            --name ollama \
            --gpus all \
            -p 11434:11434 \
            -v ollama:/root/.ollama \
            --restart unless-stopped \
            ollama/ollama
        print_success "Ollama started with GPU support"
    else
        # CPU only
        docker run -d \
            --name ollama \
            -p 11434:11434 \
            -v ollama:/root/.ollama \
            --restart unless-stopped \
            ollama/ollama
        print_success "Ollama started (CPU mode)"
    fi
    
    # Wait for Ollama to be ready
    print_info "Waiting for Ollama to be ready (max 30s)..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama is ready"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    print_error "Ollama failed to start"
    docker logs ollama
    exit 1
}

# Pull model
pull_model() {
    print_header "📂 Pulling Model: $MODEL"
    
    print_info "Pulling $MODEL... This may take 5-10 minutes"
    docker exec ollama ollama pull $MODEL
    
    if [ $? -eq 0 ]; then
        print_success "Model $MODEL pulled successfully"
    else
        print_error "Failed to pull model $MODEL"
        exit 1
    fi
}

# Update .env
update_env() {
    print_header "⚙️ Updating Configuration"
    
    if [ ! -f .env ]; then
        print_warning ".env file not found, using .env.example"
        cp .env.example .env
    fi
    
    # Check if already configured for local LLM
    if grep -q "USE_LOCAL_MODEL=true" .env; then
        print_info ".env already configured for local LLM"
    else
        print_info "Updating .env for local LLM..."
        
        # Use sed to update values
        sed -i.bak \
            -e "s/^USE_LOCAL_MODEL=.*/USE_LOCAL_MODEL=true/" \
            -e "s/^OLLAMA_HOST=.*/OLLAMA_HOST=http:\/\/localhost:11434/" \
            -e "s/^LOCAL_MODEL=.*/LOCAL_MODEL=$MODEL/" \
            .env
        
        rm -f .env.bak
        print_success ".env updated with local LLM settings"
    fi
    
    # Show configuration
    echo ""
    print_info "Current configuration:"
    echo ""
    grep -E "^USE_LOCAL_MODEL=|^OLLAMA_HOST=|^LOCAL_MODEL=" .env || true
    echo ""
}

# Final instructions
print_final_instructions() {
    print_header "🌟 Setup Complete!"
    
    echo -e "${GREEN}✓ Ollama container is running${NC}"
    echo -e "${GREEN}✓ Model '$MODEL' is ready${NC}"
    echo -e "${GREEN}✓ .env configured for local LLM${NC}"
    
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo ""
    
    HAS_GPU=0
    if detect_gpu; then
        HAS_GPU=1
        echo "With GPU support detected, analysis should be fast (<5 sec)!"
    else
        echo "Running on CPU - analysis may take 5-30 seconds (consider adding GPU)"
    fi
    
    echo ""
    echo -e "${BLUE}Test Ollama:${NC}"
    echo "  curl http://localhost:11434/api/tags"
    echo ""
    echo -e "${BLUE}Restart bot:${NC}"
    echo "  docker-compose build --no-cache"
    echo "  docker-compose up -d"
    echo ""
    echo -e "${BLUE}Check logs:${NC}"
    echo "  docker-compose logs -f github-commits-bot"
    echo ""
    echo -e "${BLUE}Ollama commands:${NC}"
    echo "  docker exec ollama ollama list              # List models"
    echo "  docker exec ollama ollama pull llama2       # Add another model"
    echo "  docker logs -f ollama                        # Ollama logs"
    echo ""
    echo -e "${GREEN}Your bot now has free, private AI analysis! 🚀${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   🤖 Setup Local LLM (Ollama) for GitHub Bot         ║"
    echo "║                                                            ║"
    echo "║   Free, private, offline AI analysis! 🚀              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Check prerequisites
    check_docker
    check_docker_daemon
    
    # Select model
    select_model
    
    # Setup
    start_ollama
    pull_model
    update_env
    
    # Done
    print_final_instructions
}

# Run
main
