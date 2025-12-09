#!/bin/bash

#############################################################
# GitHub Commits Verifier Bot - Update Script
# Safely updates the bot with backup and rollback support
#############################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_DIR="/opt/github-commits-verifier-bot"
BACKUP_DIR="/opt/bot-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/backup-${TIMESTAMP}"

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  GitHub Commits Verifier Bot - Update Script${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_requirements() {
    print_info "Проверка требований..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then 
        print_error "Пожалуйста, запустите скрипт с правами root или через sudo"
        exit 1
    fi
    
    # Check if bot directory exists
    if [ ! -d "$BOT_DIR" ]; then
        print_error "Директория бота не найдена: $BOT_DIR"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose не установлен"
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "git не установлен"
        exit 1
    fi
    
    print_success "Все требования выполнены"
}

create_backup() {
    print_info "Создание резервной копии..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Copy current bot directory to backup
    cp -r "$BOT_DIR" "$BACKUP_PATH"
    
    # Save current git commit hash
    cd "$BOT_DIR"
    git rev-parse HEAD > "$BACKUP_PATH/.git-commit"
    
    print_success "Резервная копия создана: $BACKUP_PATH"
}

stop_bot() {
    print_info "Остановка бота..."
    
    cd "$BOT_DIR"
    
    if [ -f "stop.sh" ]; then
        ./stop.sh
    else
        docker-compose down
    fi
    
    print_success "Бот остановлен"
}

update_code() {
    print_info "Обновление кода из GitHub..."
    
    cd "$BOT_DIR"
    
    # Stash any local changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "Обнаружены локальные изменения, сохраняем их..."
        git stash
    fi
    
    # Pull latest changes
    git pull origin main
    
    # Get new version from README
    NEW_VERSION=$(grep -oP '# 🤖 GitHub Commits Verifier Bot v\K[0-9.]+' README.md | head -1)
    
    print_success "Код обновлен до версии v$NEW_VERSION"
}

rebuild_bot() {
    print_info "Пересборка Docker образа..."
    
    cd "$BOT_DIR"
    
    # Rebuild and start
    docker-compose build --no-cache
    
    print_success "Образ пересобран"
}

start_bot() {
    print_info "Запуск обновленного бота..."
    
    cd "$BOT_DIR"
    
    if [ -f "start.sh" ]; then
        ./start.sh
    else
        docker-compose up -d
    fi
    
    print_success "Бот запущен"
}

verify_bot() {
    print_info "Проверка статуса бота..."
    
    cd "$BOT_DIR"
    
    # Wait for containers to start
    sleep 5
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Бот работает корректно"
        echo ""
        docker-compose ps
        return 0
    else
        print_error "Бот не запустился!"
        return 1
    fi
}

rollback() {
    print_warning "Откат к предыдущей версии..."
    
    # Stop current version
    cd "$BOT_DIR"
    docker-compose down
    
    # Restore from backup
    rm -rf "$BOT_DIR"
    cp -r "$BACKUP_PATH" "$BOT_DIR"
    
    # Restore git commit
    cd "$BOT_DIR"
    OLD_COMMIT=$(cat .git-commit)
    git checkout "$OLD_COMMIT"
    
    # Restart
    docker-compose up -d
    
    print_success "Откат выполнен успешно"
}

cleanup_old_backups() {
    print_info "Очистка старых резервных копий (старше 7 дней)..."
    
    find "$BACKUP_DIR" -type d -name "backup-*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Очистка завершена"
}

show_logs() {
    print_info "Последние логи бота:"
    echo ""
    docker logs --tail 50 github-commits-bot
}

# Main execution
main() {
    print_header
    
    # Check requirements
    check_requirements
    echo ""
    
    # Confirm update
    print_warning "Это обновит бота до последней версии из GitHub"
    read -p "Продолжить? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Обновление отменено"
        exit 0
    fi
    echo ""
    
    # Create backup
    create_backup
    echo ""
    
    # Stop bot
    stop_bot
    echo ""
    
    # Update code
    update_code
    echo ""
    
    # Rebuild
    rebuild_bot
    echo ""
    
    # Start bot
    start_bot
    echo ""
    
    # Verify
    if verify_bot; then
        echo ""
        print_success "✨ Обновление завершено успешно! ✨"
        echo ""
        print_info "Резервная копия сохранена в: $BACKUP_PATH"
        print_info "Для отката выполните: sudo $0 --rollback"
        echo ""
        
        # Show logs
        read -p "Показать логи бота? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            show_logs
        fi
        
        # Cleanup old backups
        echo ""
        cleanup_old_backups
    else
        echo ""
        print_error "Обновление не удалось!"
        read -p "Откатить к предыдущей версии? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
        exit 1
    fi
}

# Handle rollback flag
if [ "$1" == "--rollback" ]; then
    print_header
    
    # Find latest backup
    LATEST_BACKUP=$(ls -td "$BACKUP_DIR"/backup-* 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        print_error "Резервные копии не найдены"
        exit 1
    fi
    
    print_warning "Откат к резервной копии: $LATEST_BACKUP"
    read -p "Продолжить? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Откат отменен"
        exit 0
    fi
    
    BACKUP_PATH="$LATEST_BACKUP"
    rollback
    exit 0
fi

# Run main function
main
