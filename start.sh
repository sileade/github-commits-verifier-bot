#!/bin/bash

# ============================================================================
# GitHub Commits Verifier Bot - Complete Automated Startup Script
# ============================================================================
# This script handles:
# 1. Environment setup and validation
# 2. Docker image build
# 3. Container startup and health checks
# 4. Model initialization (if using local LLM)
# 5. Database initialization
# 6. Service readiness verification
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
ENV_FILE=".env"
PROJECT_NAME="github-commits-bot"
BUILD_NO_CACHE=${BUILD_NO_CACHE:-false}

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

print_step() {
    echo -e "${MAGENTA}✔ $1${NC}"
}

# Check .env file
check_env() {
    print_header "✅ Environment Setup"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_error ".env file not found!"
        echo "Please run './setup.sh' first to create .env file"
        exit 1
    fi
    
    print_success ".env file found"
    
    # Validate required tokens
    if ! grep -q "TELEGRAM_BOT_TOKEN=" "$ENV_FILE" || grep -q "TELEGRAM_BOT_TOKEN=$" "$ENV_FILE"; then
        print_error "TELEGRAM_BOT_TOKEN not set in .env"
        exit 1
    fi
    print_success "TELEGRAM_BOT_TOKEN configured"
    
    if ! grep -q "GITHUB_TOKEN=" "$ENV_FILE" || grep -q "GITHUB_TOKEN=$" "$ENV_FILE"; then
        print_error "GITHUB_TOKEN not set in .env"
        exit 1
    fi
    print_success "GITHUB_TOKEN configured"
    
    # Check if using local LLM
    if grep -q "USE_LOCAL_MODEL=true" "$ENV_FILE"; then
        print_success "Local LLM (Ollama) enabled"
        USE_LOCAL_LLM=true
    else
        print_info "Local LLM disabled (using OpenAI or no AI)"
        USE_LOCAL_LLM=false
    fi
}

# Check Docker
check_docker() {
    print_header "🐳 Docker Check"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        exit 1
    fi
    print_success "Docker installed"
    
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon not running"
        exit 1
    fi
    print_success "Docker daemon running"
}

# Build Docker image
build_image() {
    print_header "🐳 Building Docker Image"
    
    local build_cmd="docker-compose build"
    
    if [ "$BUILD_NO_CACHE" = "true" ]; then
        build_cmd="$build_cmd --no-cache"
        print_info "Building without cache..."
    fi
    
    if $build_cmd github-commits-bot; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Start services
start_services() {
    print_header "🚀 Starting Services"
    
    print_step "Starting PostgreSQL..."
    docker-compose up -d postgres
    print_success "PostgreSQL started"
    
    if [ "$USE_LOCAL_LLM" = "true" ]; then
        print_step "Starting Ollama..."
        docker-compose up -d ollama
        print_success "Ollama started"
    else
        print_info "Skipping Ollama (not enabled)"
    fi
    
    print_step "Starting GitHub Commits Bot..."
    docker-compose up -d github-commits-bot
    print_success "Bot started"
}

# Wait for services to be healthy
wait_healthy() {
    print_header "⏳ Waiting for Services"
    
    local max_attempts=60
    local attempt=0
    
    # PostgreSQL
    print_info "Waiting for PostgreSQL to be healthy..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U github_bot &>/dev/null; then
            print_success "PostgreSQL is healthy"
            break
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -ge $max_attempts ]; then
        print_error "PostgreSQL failed to become healthy"
        docker-compose logs postgres
        exit 1
    fi
    
    # Ollama (if enabled)
    if [ "$USE_LOCAL_LLM" = "true" ]; then
        attempt=0
        print_info "Waiting for Ollama to be healthy..."
        while [ $attempt -lt $max_attempts ]; do
            if docker exec ollama curl -s http://localhost:11434/api/tags &>/dev/null; then
                print_success "Ollama is healthy"
                break
            fi
            echo -n "."
            sleep 1
            attempt=$((attempt + 1))
        done
        
        if [ $attempt -ge $max_attempts ]; then
            print_warning "Ollama timeout - might still be loading model"
        fi
    fi
    
    # Bot
    attempt=0
    print_info "Waiting for Bot to be healthy..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps github-commits-bot | grep -q "healthy\|running"; then
            print_success "Bot is running"
            break
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -ge $max_attempts ]; then
        print_error "Bot failed to start"
        docker-compose logs github-commits-bot
        exit 1
    fi
}

# Initialize model (if using local LLM)
initialize_model() {
    if [ "$USE_LOCAL_LLM" != "true" ]; then
        return
    fi
    
    print_header "🤖 Initializing Local LLM Model"
    
    local model=$(grep "^LOCAL_MODEL=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '\r')
    model=${model:-mistral}
    
    print_info "Checking if model '$model' is available..."
    
    if docker exec ollama ollama list | grep -q "$model"; then
        print_success "Model '$model' is already loaded"
        return
    fi
    
    print_step "Pulling model '$model'..."
    print_warning "This may take 5-15 minutes on first run"
    echo ""
    
    if docker exec ollama ollama pull "$model"; then
        print_success "Model '$model' pulled successfully"
    else
        print_error "Failed to pull model '$model'"
        print_info "You can pull it manually with:"
        echo "  docker exec ollama ollama pull $model"
    fi
}

# Show status
show_status() {
    print_header "📈 Service Status"
    
    docker-compose ps
}

# Show next steps
show_instructions() {
    print_header "🌟 Setup Complete!"
    
    echo -e "${GREEN}All services are running and healthy!${NC}"
    echo ""
    echo -e "${BLUE}Your bot is ready to use!${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  📈 View bot logs:        docker-compose logs -f github-commits-bot"
    echo "  📈 View all logs:       docker-compose logs -f"
    echo "  🐳 View services:       docker-compose ps"
    echo "  🚀 Stop services:       docker-compose down"
    echo "  🚀 Restart services:    docker-compose restart"
    echo ""
    
    if [ "$USE_LOCAL_LLM" = "true" ]; then
        echo -e "${BLUE}Local LLM (Ollama) commands:${NC}"
        echo "  🤖 View Ollama logs:     docker logs -f ollama"
        echo "  📂 List models:         docker exec ollama ollama list"
        echo "  📂 Pull another model:  docker exec ollama ollama pull llama2"
        echo ""
    fi
    
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Open Telegram and find your bot"
    echo "  2. Send /start to see the main menu"
    echo "  3. Try checking your first commit!"
    echo ""
    echo -e "${GREEN}Happy verifying! 🚀${NC}"
    echo ""
}

# Main execution
main() {
    clear
    
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   🤖 GitHub Commits Verifier Bot - Complete Startup     ║"
    echo "║                                                            ║"
    echo "║   Building full stack with PostgreSQL + Bot + Ollama   ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Execute startup sequence
    check_env
    check_docker
    build_image
    start_services
    wait_healthy
    initialize_model
    show_status
    show_instructions
}

# Run
main
