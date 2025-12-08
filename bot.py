#!/usr/bin/env python3
"""
Telegram Bot for GitHub Commits Verification
Проверка и подтверждение комитов приложений в GitHub
"""

import os
import logging
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ChatAction

from github_service import GitHubService
from database import Database

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
REPO_INPUT, COMMIT_INPUT, ACTION_CONFIRM = range(3)

# Database initialization
db = Database()

# GitHub service
github_service: Optional[GitHubService] = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start command handler
    """
    user_id = update.effective_user.id
    await db.add_user(user_id, update.effective_user.username or 'unknown')
    
    keyboard = [
        [InlineKeyboardButton("🔍 Проверить коммит", callback_data='check_commit')],
        [InlineKeyboardButton("✅ Подтвердить коммит", callback_data='approve_commit')],
        [InlineKeyboardButton("❌ Отклонить коммит", callback_data='reject_commit')],
        [InlineKeyboardButton("📊 История", callback_data='history')],
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *GitHub Commits Verifier Bot*\n\n"
        "Добро пожаловать! Этот бот помогает проверять и подтверждать коммиты GitHub приложений.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Help command
    """
    help_text = (
        "*📚 Справка по командам:*\n\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/check_repo - Проверить репозиторий\n"
        "/stats - Статистика проверок\n\n"
        "*Основные функции:*\n"
        "🔍 Проверить коммит - просмотр информации о коммите\n"
        "✅ Подтвердить коммит - отметить коммит как легитимный\n"
        "❌ Отклонить коммит - отметить коммит как подозрительный\n"
        "📊 История - просмотр истории проверок\n"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle button callbacks
    """
    query = update.callback_query
    await query.answer()
    
    if query.data == 'check_commit':
        await query.edit_message_text(
            text="📝 Введите полный URL репозитория GitHub или имя в формате: `owner/repo`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'check_commit'
        return REPO_INPUT
    
    elif query.data == 'approve_commit':
        await query.edit_message_text(
            text="✅ Введите ID коммита для подтверждения (SHA):",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'approve_commit'
        return COMMIT_INPUT
    
    elif query.data == 'reject_commit':
        await query.edit_message_text(
            text="❌ Введите ID коммита для отклонения (SHA):",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'reject_commit'
        return COMMIT_INPUT
    
    elif query.data == 'history':
        user_id = update.effective_user.id
        history = await db.get_user_history(user_id, limit=10)
        
        if not history:
            await query.edit_message_text("📋 История проверок пуста.")
        else:
            history_text = "*📊 История проверок (последние 10):*\n\n"
            for record in history:
                history_text += f"• {record['repo']} - {record['commit_sha'][:8]}...\n  Статус: {record['status']}\n  Дата: {record['created_at']}\n\n"
            await query.edit_message_text(history_text, parse_mode='Markdown')
    
    elif query.data == 'settings':
        await query.edit_message_text(
            text="⚙️ *Настройки*\n\nИспользуйте /help для информации о конфигурации.",
            parse_mode='Markdown'
        )


async def handle_repo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle repository input
    """
    repo_input = update.message.text.strip()
    
    # Send typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Get repository info
        repo_info = await github_service.get_repository(repo_input)
        
        if repo_info:
            context.user_data['repo'] = repo_input
            await update.message.reply_text(
                f"✅ Репозиторий найден: `{repo_info['full_name']}`\n\n"
                f"📌 Введите SHA коммита для проверки:",
                parse_mode='Markdown'
            )
            return COMMIT_INPUT
        else:
            await update.message.reply_text(
                "❌ Репозиторий не найден. Проверьте URL или имя в формате `owner/repo`",
                parse_mode='Markdown'
            )
            return REPO_INPUT
    except Exception as e:
        logger.error(f"Error getting repository: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        return REPO_INPUT


async def handle_commit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle commit SHA input
    """
    commit_sha = update.message.text.strip()
    
    # Send typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    action = context.user_data.get('action')
    repo = context.user_data.get('repo', 'unknown')
    
    try:
        if action == 'check_commit':
            # Get commit info
            commit_info = await github_service.get_commit_info(repo, commit_sha)
            
            if commit_info:
                context.user_data['commit_sha'] = commit_sha
                commit_details = (
                    f"*🔍 Информация о коммите:*\n\n"
                    f"📦 Репозиторий: `{commit_info['repo']}`\n"
                    f"🔗 SHA: `{commit_info['sha']}`\n"
                    f"👤 Автор: {commit_info['author']}\n"
                    f"📅 Дата: {commit_info['date']}\n"
                    f"📝 Сообщение: {commit_info['message']}\n\n"
                    f"✅ Подписано: {'Да' if commit_info['verified'] else 'Нет'}\n"
                )
                
                # Verification checks
                checks = await github_service.verify_commit(commit_info)
                commit_details += f"\n*✓ Результаты проверки:*\n"
                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "⚠️"
                    commit_details += f"{status} {check_name}\n"
                
                keyboard = [
                    [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{commit_sha}")],
                    [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{commit_sha}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="start")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    commit_details,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return ACTION_CONFIRM
        
        elif action in ['approve_commit', 'reject_commit']:
            status = 'approved' if action == 'approve_commit' else 'rejected'
            
            # Save to database
            await db.add_verification(
                user_id=update.effective_user.id,
                repo=repo,
                commit_sha=commit_sha,
                status=status
            )
            
            # Log the action
            status_emoji = "✅" if status == 'approved' else "❌"
            await update.message.reply_text(
                f"{status_emoji} Коммит {status_emoji} успешно обработан:\n\n"
                f"Репозиторий: `{repo}`\n"
                f"SHA: `{commit_sha}`\n"
                f"Статус: {status}",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error handling commit: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel conversation
    """
    await update.message.reply_text("❌ Операция отменена.")
    return ConversationHandler.END


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show statistics
    """
    user_id = update.effective_user.id
    stats = await db.get_user_stats(user_id)
    
    stats_text = (
        f"*📊 Ваша статистика:*\n\n"
        f"✅ Подтверждено: {stats['approved']}\n"
        f"❌ Отклонено: {stats['rejected']}\n"
        f"🔍 Всего проверено: {stats['total']}\n"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log the error and send a message to notify the developer
    """
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """
    Start the bot
    """
    global github_service
    
    # Get tokens from environment
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    if not github_token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")
    
    # Initialize services
    github_service = GitHubService(github_token)
    
    # Create application
    application = Application.builder().token(telegram_token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback)],
        states={
            REPO_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_repo_input)],
            COMMIT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commit_input)],
            ACTION_CONFIRM: [CallbackQueryHandler(button_callback)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
