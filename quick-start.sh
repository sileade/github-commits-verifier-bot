#!/bin/bash

# ============================================================================
# GitHub Commits Verifier Bot - Quick Start Script
# ============================================================================
# This script quickly starts the bot after initial setup
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
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

# Check .env file
if [ ! -f ".env" ]; then
    print_error ".env файл не найден!"
    print_info "Запустите сначала: ./setup.sh"
    exit 1
fi

# Check if Telegram token is set
if ! grep -q "TELEGRAM_BOT_TOKEN=[a-zA-Z0-9]" .env; then
    print_error "TELEGRAM_BOT_TOKEN не установлен в .env!"
    print_info "Пожалуйста, добавьте ваш Telegram Bot Token"
    exit 1
fi

# Check if GitHub token is set
if ! grep -q "GITHUB_TOKEN=[a-zA-Z0-9]" .env; then
    print_error "GITHUB_TOKEN не установлен в .env!"
    print_info "Пожалуйста, добавьте ваш GitHub Personal Access Token"
    exit 1
fi

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🤖 GitHub Commits Verifier Bot - Quick Start             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_info "Проверка статуса контейнеров..."

# Start services
print_info "Запуск PostgreSQL..."
docker-compose up -d postgres

print_info "Ожидание инициализации PostgreSQL..."
sleep 10

print_info "Запуск бота..."
docker-compose up -d github-commits-bot

echo ""
print_success "Сервисы запущены!"

echo ""
echo -e "${BLUE}Статус:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}Полезные команды:${NC}"
echo "  Логи бота:        docker-compose logs -f github-commits-bot"
echo "  Логи БД:          docker-compose logs -f postgres"
echo "  Статус:           docker-compose ps"
echo "  Остановка:        docker-compose down"
echo ""
echo -e "${GREEN}Бот готов к работе! 🚀${NC}"
