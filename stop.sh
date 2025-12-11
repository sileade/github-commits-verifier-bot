#!/bin/bash

# ============================================================================
# GitHub Commits Verifier Bot - Graceful Shutdown Script
# ============================================================================

set -e

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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

main() {
    print_header "🚀 Stopping Services"
    
    print_info "Stopping all containers gracefully..."
    docker-compose down
    
    print_success "All services stopped"
    
    echo ""
    echo -e "${BLUE}Status:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}Services are stopped.${NC}"
    echo ""
    echo -e "${BLUE}To start again:${NC}"
    echo "  ./start.sh"
    echo ""
}

main
