#!/bin/bash

# ============================================================================
# GitHub Commits Verifier Bot - Setup Script
# ============================================================================
# This script helps you configure the bot by:
# 1. Generating secure PostgreSQL password
# 2. Creating .env file with defaults
# 3. Prompting for Telegram Bot Token
# 4. Prompting for GitHub Personal Access Token
# 5. Setting up PostgreSQL container
# 6. Running database initialization
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"
MIN_PASSWORD_LENGTH=20

# Helper functions
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

# Check prerequisites
check_prerequisites() {
    print_header "Проверка необходимых инструментов"
    
    local missing_tools=0
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker не найден. Пожалуйста, установите Docker."
        missing_tools=$((missing_tools + 1))
    else
        print_success "Docker установлен"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не найден. Пожалуйста, установите Docker Compose."
        missing_tools=$((missing_tools + 1))
    else
        print_success "Docker Compose установлен"
    fi
    
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL не найден. Пожалуйста, установите OpenSSL."
        missing_tools=$((missing_tools + 1))
    else
        print_success "OpenSSL установлен"
    fi
    
    if [ $missing_tools -gt 0 ]; then
        print_error "$missing_tools инструментов не установлено. Пожалуйста, установите их и повторите."
        exit 1
    fi
}

# Generate secure password
generate_password() {
    local length=${1:-$MIN_PASSWORD_LENGTH}
    openssl rand -base64 $length | head -c $length
}

# Check if .env exists
check_env_file() {
    print_header "Проверка конфигурации"
    
    if [ -f "$ENV_FILE" ]; then
        print_warning "Файл $ENV_FILE уже существует."
        read -p "Хотите переконфигурировать? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Используется существующая конфигурация."
            return 1
        fi
    fi
    return 0
}

# Generate .env file
generate_env() {
    print_header "Генерация файла конфигурации"
    
    # Generate secure PostgreSQL password
    local pg_password=$(generate_password $MIN_PASSWORD_LENGTH)
    print_info "Сгенерирован пароль PostgreSQL ($(echo -n $pg_password | wc -c) символов)"
    
    # Create .env file
    cat > "$ENV_FILE" << EOF
# ============================================================================
# GitHub Commits Verifier Bot - Configuration File
# ============================================================================
# Автоматически сгенерирован setup.sh - $(date '+%Y-%m-%d %H:%M:%S')
# ============================================================================

# TELEGRAM BOT CONFIGURATION
TELEGRAM_BOT_TOKEN=

# GITHUB CONFIGURATION  
GITHUB_TOKEN=

# DATABASE CONFIGURATION (PostgreSQL)
POSTGRES_DB=github_verifier
POSTGRES_USER=github_bot
POSTGRES_PASSWORD=$pg_password
DATABASE_URL=postgresql://github_bot:$pg_password@postgres:5432/github_verifier

# LOGGING CONFIGURATION
LOG_LEVEL=INFO

# DOCKER CONFIGURATION
DOCKER_REGISTRY=docker.io
DOCKER_IMAGE_TAG=latest
EOF
    
    print_success "Файл $ENV_FILE создан"
}

# Prompt for Telegram token
prompt_telegram_token() {
    print_header "Конфигурация Telegram"
    
    echo -e "${BLUE}Как получить Telegram Bot Token:${NC}"
    echo "1. Откройте Telegram и найдите @BotFather"
    echo "2. Отправьте /newbot"
    echo "3. Следуйте инструкциям"
    echo "4. Скопируйте полученный токен"
    echo ""
    
    read -p "Введите ваш Telegram Bot Token (или нажмите Enter чтобы пропустить): " telegram_token
    
    if [ -n "$telegram_token" ]; then
        # Update .env file
        sed -i.bak "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$telegram_token/" "$ENV_FILE"
        rm -f "$ENV_FILE.bak"
        print_success "Telegram Bot Token сохранён"
    else
        print_warning "Telegram Bot Token не введён. Пожалуйста, добавьте его позже в $ENV_FILE"
    fi
}

# Prompt for GitHub token
prompt_github_token() {
    print_header "Конфигурация GitHub"
    
    echo -e "${BLUE}Как получить GitHub Personal Access Token:${NC}"
    echo "1. Перейдите на https://github.com/settings/tokens"
    echo "2. Нажмите 'Generate new token (classic)'"
    echo "3. Выберите scopes: repo, read:user"
    echo "4. Скопируйте полученный токен"
    echo ""
    
    read -p "Введите ваш GitHub Personal Access Token (или нажмите Enter чтобы пропустить): " github_token
    
    if [ -n "$github_token" ]; then
        # Update .env file
        sed -i.bak "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" "$ENV_FILE"
        rm -f "$ENV_FILE.bak"
        print_success "GitHub Token сохранён"
    else
        print_warning "GitHub Token не введён. Пожалуйста, добавьте его позже в $ENV_FILE"
    fi
}

# Start PostgreSQL
start_postgres() {
    print_header "Запуск PostgreSQL"
    
    echo "Проверка существующих контейнеров..."
    if docker-compose ps postgres 2>/dev/null | grep -q postgres; then
        print_info "PostgreSQL контейнер уже запущен"
        return 0
    fi
    
    print_info "Поднимаю PostgreSQL контейнер..."
    docker-compose up -d postgres
    
    print_info "Ожидание инициализации PostgreSQL (максимум 60 секунд)..."
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U github_bot -d github_verifier &>/dev/null; then
            print_success "PostgreSQL готов к работе"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    print_error "PostgreSQL не инициализировался за отведённое время"
    return 1
}

# Initialize database
init_database() {
    print_header "Инициализация базы данных"
    
    print_info "Создаю таблицы..."
    
    docker-compose exec -T postgres psql -U github_bot -d github_verifier << EOF
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create verifications table
CREATE TABLE IF NOT EXISTS verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    repo TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('approved', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_verifications_user_id ON verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_verifications_commit_sha ON verifications(commit_sha);
CREATE INDEX IF NOT EXISTS idx_verifications_created_at ON verifications(created_at DESC);

EOF
    
    if [ $? -eq 0 ]; then
        print_success "База данных инициализирована"
    else
        print_error "Ошибка при инициализации базы данных"
        return 1
    fi
}

# Build bot image
build_bot_image() {
    print_header "Сборка Docker образа"
    
    print_info "Собираю Docker образ для бота..."
    
    if docker-compose build github-commits-bot; then
        print_success "Docker образ успешно собран"
    else
        print_error "Ошибка при сборке Docker образа"
        return 1
    fi
}

# Final instructions
print_final_instructions() {
    print_header "Установка завершена"
    
    echo -e "${GREEN}✓ Конфигурация создана${NC}"
    echo -e "${GREEN}✓ PostgreSQL запущен${NC}"
    echo -e "${GREEN}✓ База данных инициализирована${NC}"
    echo -e "${GREEN}✓ Docker образ собран${NC}"
    
    echo ""
    echo -e "${BLUE}Следующие шаги:${NC}"
    echo ""
    
    if grep -q "TELEGRAM_BOT_TOKEN=$" "$ENV_FILE"; then
        echo -e "${YELLOW}1. Добавьте Telegram Bot Token в $ENV_FILE${NC}"
    else
        echo -e "${GREEN}1. Telegram Bot Token уже добавлен${NC}"
    fi
    
    if grep -q "GITHUB_TOKEN=$" "$ENV_FILE"; then
        echo -e "${YELLOW}2. Добавьте GitHub Personal Access Token в $ENV_FILE${NC}"
    else
        echo -e "${GREEN}2. GitHub Token уже добавлен${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Запуск бота:${NC}"
    echo "  docker-compose up -d github-commits-bot"
    echo ""
    echo -e "${BLUE}Проверка статуса:${NC}"
    echo "  docker-compose ps"
    echo ""
    echo -e "${BLUE}Просмотр логов:${NC}"
    echo "  docker-compose logs -f github-commits-bot"
    echo ""
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   🤖 GitHub Commits Verifier Bot - Setup Script           ║"
    echo "║                                                            ║"
    echo "║   Вас приветствует интерактивная установка бота           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Check existing .env
    if ! check_env_file; then
        print_info "Используется существующая конфигурация из $ENV_FILE"
        # Still prompt for tokens even if .env exists
        read -p "Хотите обновить токены? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            prompt_telegram_token
            prompt_github_token
        fi
    else
        # Step 3: Generate .env
        generate_env
        
        # Step 4: Prompt for tokens
        prompt_telegram_token
        prompt_github_token
    fi
    
    # Step 5: Start PostgreSQL
    if ! start_postgres; then
        print_error "Не удалось запустить PostgreSQL"
        exit 1
    fi
    
    # Step 6: Initialize database
    if ! init_database; then
        print_error "Не удалось инициализировать базу данных"
        exit 1
    fi
    
    # Step 7: Build bot image
    if ! build_bot_image; then
        print_error "Не удалось собрать Docker образ"
        exit 1
    fi
    
    # Step 8: Print final instructions
    print_final_instructions
}

# Run main
main
