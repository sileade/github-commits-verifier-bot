#!/bin/bash

# ============================================================================
# GitHub Commits Verifier Bot - Restart Script
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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

main() {
    print_header "🚁 Restarting Services"
    
    print_info "Stopping services..."
    docker-compose down
    
    print_info "Starting services..."
    docker-compose up -d
    
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    echo ""
    echo -e "${BLUE}Status:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}Services restarted!${NC}"
    echo ""
}

main
