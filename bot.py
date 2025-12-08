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


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle button callbacks - main menu and actions
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Main menu callbacks
    if callback_data == 'check_commit':
        await query.edit_message_text(
            text="📝 Введите полный URL репозитория GitHub или имя в формате: `owner/repo`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'check_commit'
        return REPO_INPUT
    
    elif callback_data == 'approve_commit':
        await query.edit_message_text(
            text="✅ Введите SHA коммита для подтверждения:",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'approve_commit'
        return COMMIT_INPUT
    
    elif callback_data == 'reject_commit':
        await query.edit_message_text(
            text="❌ Введите SHA коммита для отклонения:",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'reject_commit'
        return COMMIT_INPUT
    
    elif callback_data == 'history':
        user_id = update.effective_user.id
        history = await db.get_user_history(user_id, limit=10)
        
        if not history:
            await query.edit_message_text(
                "📋 История проверок пуста.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]])
            )
        else:
            history_text = "*📊 История проверок (последние 10):*\n\n"
            for i, record in enumerate(history, 1):
                status_emoji = "✅" if record['status'] == 'approved' else "❌"
                history_text += f"{i}. {status_emoji} {record['repo']} - {record['commit_sha'][:8]}...\n"
                history_text += f"   📅 {record['created_at']}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(history_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif callback_data == 'settings':
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚙️ *Настройки*\n\nИспользуйте /help для информации о конфигурации.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == 'back_to_menu':
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("🔍 Проверить коммит", callback_data='check_commit')],
            [InlineKeyboardButton("✅ Подтвердить коммит", callback_data='approve_commit')],
            [InlineKeyboardButton("❌ Отклонить коммит", callback_data='reject_commit')],
            [InlineKeyboardButton("📊 История", callback_data='history')],
            [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🤖 *GitHub Commits Verifier Bot*\n\n"
            "Главное меню. Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END


async def handle_commit_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle commit action callbacks (approve/reject buttons from commit info)
    """
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse callback: approve_<sha> or reject_<sha>
        if callback_data.startswith('approve_'):
            commit_sha = callback_data.replace('approve_', '')
            status = 'approved'
            status_emoji = '✅'
        elif callback_data.startswith('reject_'):
            commit_sha = callback_data.replace('reject_', '')
            status = 'rejected'
            status_emoji = '❌'
        else:
            return ConversationHandler.END
        
        await query.answer()
        
        # Get repo from context (was stored during check_commit)
        repo = context.user_data.get('repo', 'unknown')
        user_id = update.effective_user.id
        
        # Save to database
        success = await db.add_verification(
            user_id=user_id,
            repo=repo,
            commit_sha=commit_sha,
            status=status
        )
        
        if success:
            # Edit message with result
            response_text = (
                f"{status_emoji} *Коммит успешно обработан*\n\n"
                f"📦 Репозиторий: `{repo}`\n"
                f"🔗 SHA: `{commit_sha[:8]}...`\n"
                f"📋 Статус: *{status.upper()}*\n\n"
                f"{'🔐 Коммит одобрен' if status == 'approved' else '⚠️ Коммит отклонен'}"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔍 Проверить еще", callback_data='check_commit')],
                [InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Ошибка при сохранении. Попробуйте еще раз."
            )
    
    except Exception as e:
        logger.error(f"Error in handle_commit_action_callback: {e}")
        await query.answer(f"Ошибка: {str(e)}", show_alert=True)
    
    return ConversationHandler.END


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
                
                # Build commit details message
                commit_details = (
                    f"*🔍 Информация о коммите:*\n\n"
                    f"📦 Репозиторий: `{commit_info['repo']}`\n"
                    f"🔗 SHA: `{commit_info['sha']}`\n"
                    f"👤 Автор: {commit_info['author']}\n"
                    f"📧 Email: `{commit_info['author_email']}`\n"
                    f"📅 Дата: {commit_info['date']}\n"
                    f"📝 Сообщение: {commit_info['message']}\n\n"
                )
                
                # Add signature info
                signature_status = "🔐 Подписано GPG" if commit_info['verified'] else "⚠️ Не подписано"
                commit_details += f"{signature_status}\n\n"
                
                # Verification checks
                checks = await github_service.verify_commit(commit_info)
                commit_details += f"*✓ Результаты проверки:*\n"
                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "⚠️"
                    commit_details += f"{status} {check_name}\n"
                
                # Add link to commit
                commit_details += f"\n[🔗 Открыть на GitHub]({commit_info['url']})"
                
                # Create action buttons
                keyboard = [
                    [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{commit_sha}"),
                     InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{commit_sha}")],
                    [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    commit_details,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                return ACTION_CONFIRM
            else:
                await update.message.reply_text(
                    f"❌ Коммит не найден. Проверьте SHA.\n\n"
                    f"📌 Введите другой SHA или отправьте /start для главного меню.",
                    parse_mode='Markdown'
                )
                return COMMIT_INPUT
        
        elif action in ['approve_commit', 'reject_commit']:
            # Direct approval/rejection without checking first
            status = 'approved' if action == 'approve_commit' else 'rejected'
            status_emoji = '✅' if status == 'approved' else '❌'
            
            # Save to database
            success = await db.add_verification(
                user_id=update.effective_user.id,
                repo=repo,
                commit_sha=commit_sha,
                status=status
            )
            
            if success:
                response_text = (
                    f"{status_emoji} *Коммит успешно обработан*\n\n"
                    f"📦 Репозиторий: `{repo}`\n"
                    f"🔗 SHA: `{commit_sha[:8]}...`\n"
                    f"📋 Статус: *{status.upper()}*\n\n"
                    f"{'🔐 Коммит одобрен' if status == 'approved' else '⚠️ Коммит отклонен'}"
                )
                
                keyboard = [
                    [InlineKeyboardButton("✅ Еще подтверждение", callback_data='approve_commit'),
                     InlineKeyboardButton("❌ Еще отклонение", callback_data='reject_commit')],
                    [InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    response_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при сохранении коммита. Попробуйте еще раз."
                )
    
    except Exception as e:
        logger.error(f"Error handling commit: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel conversation
    """
    await update.message.reply_text(
        "❌ Операция отменена.\n\nОтправьте /start для главного меню."
    )
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
    
    # Calculate approval ratio
    if stats['total'] > 0:
        approval_ratio = (stats['approved'] / stats['total']) * 100
        stats_text += f"\n📈 Процент одобрений: {approval_ratio:.1f}%"
    
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')


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
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(button_callback),
        ],
        states={
            REPO_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_repo_input)],
            COMMIT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commit_input)],
            ACTION_CONFIRM: [
                CallbackQueryHandler(handle_commit_action_callback, pattern=r'^(approve|reject)_'),
                CallbackQueryHandler(button_callback),
            ],
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
