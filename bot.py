#!/usr/bin/env python3
"""
Telegram Bot for GitHub Commits Verification
Проверка и подтверждение коммитов приложений в GitHub
"""

import os
import logging
from datetime import datetime
from typing import Optional
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
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
REPO_INPUT, COMMIT_INPUT, ACTION_CONFIRM, CONFIRM_ACTION, EXPORT_ACTION, BRANCH_INPUT, ANALYSIS_TYPE = range(7)

# Global service instances
db: Optional[Database] = None
github_service: Optional[GitHubService] = None


async def post_init(app: Application) -> None:
    """
    Initialize database and services after application startup
    """
    global db, github_service
    
    logger.info("Initializing services...")
    
    # Initialize database
    try:
        db = Database()
        await db.init()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Re-raise to stop the application if DB is critical
        raise
    
    # Initialize GitHub service
    github_token = os.getenv('GITHUB_TOKEN')
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    if not github_token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")
    
    github_service = GitHubService(github_token, ollama_host)
    await github_service.init_session()
    
    logger.info("Services initialized successfully")


async def post_shutdown(app: Application) -> None:
    """
    Clean up resources on shutdown
    """
    global db, github_service
    if db:
        await db.close()
    if github_service:
        await github_service.close_session()
    logger.info("Shutdown complete")


async def get_user_repositories_status() -> dict:
    """
    Get user repositories with their status and last commit dates
    Uses the global github_service instance.
    """
    if not github_service:
        logger.error("GitHubService not initialized.")
        return {}
        
    try:
        repos = await github_service.get_user_repositories()
        
        status_info = {}
        if repos:
            # Use asyncio.gather for concurrent fetching of last commit dates
            tasks = []
            repo_list = repos[:10] # Limit to 10 repos for display
            for repo in repo_list:
                tasks.append(github_service.get_last_commit(repo['full_name']))
            
            last_commits = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, repo in enumerate(repo_list):
                last_commit = last_commits[i]
                
                if isinstance(last_commit, Exception):
                    logger.warning(f"Error getting last commit for {repo['full_name']}: {last_commit}")
                    last_commit = None
                    
                status_info[repo['full_name']] = {
                    'name': repo['name'],
                    'stars': repo.get('stargazers_count', 0),
                    'language': repo.get('language', 'Unknown'),
                    'url': repo['html_url'],
                    'last_commit': last_commit,
                    'private': repo.get('private', False),
                }
        
        return status_info
    except Exception as e:
        logger.error(f"Error getting user repositories: {e}")
        return {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start command handler - show main menu with repository status
    """
    if not db:
        await update.message.reply_text("❌ Сервисы не инициализированы. Попробуйте позже.")
        return
        
    user_id = update.effective_user.id
    
    await db.add_user(user_id, update.effective_user.username or 'unknown')
    
    menu_text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃  🤖 GitHub Commits Verifier  ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "Добро пожаловать! Этот бот помогает проверять\n"
        "и подтверждать коммиты GitHub приложений.\n\n"
    )
    
    # Add repository status if available
    try:
        repos_status = await get_user_repositories_status()
        
        if repos_status:
            menu_text += "*📦 Ваши репозитории:*\n\n"
            
            for repo_full_name, repo_info in sorted(repos_status.items()):
                # Emoji for language
                lang_emoji = {
                    'Python': '🐍',
                    'JavaScript': '📜',
                    'TypeScript': '📘',
                    'Go': '🐹',
                    'Rust': '🦀',
                    'Java': '☕',
                    'C++': '⚙️',
                    'C#': '💎',
                    'PHP': '🐘',
                    'Ruby': '💎',
                }.get(repo_info['language'], '📄')
                
                # Status indicator
                privacy_emoji = '🔒' if repo_info['private'] else '🌐'
                
                menu_text += f"{privacy_emoji} *{repo_info['name']}*\n"
                menu_text += f"  {lang_emoji} {repo_info['language']} | ⭐ {repo_info['stars']}\n"
                
                if repo_info['last_commit']:
                    menu_text += f"  📅 Последний коммит: {repo_info['last_commit']}\n"
                else:
                    menu_text += f"  📅 Последний коммит: Не найден\n"
                
                menu_text += "\n"
    except Exception as e:
        logger.error(f"Error loading repositories status: {e}")
        menu_text += "*⚠️ Не удалось загрузить статус репозиториев*\n\n"
    
    menu_text += "\n*Выберите действие ниже:*"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Проверить коммит", callback_data='check_commit')],
        [InlineKeyboardButton("📄 Анализ истории коммитов", callback_data='analyze_history')],
        [InlineKeyboardButton("✅ Подтвердить коммит", callback_data='approve_commit')],
        [InlineKeyboardButton("❌ Отклонить коммит", callback_data='reject_commit')],
        [InlineKeyboardButton("📊 История", callback_data='history')],
        [InlineKeyboardButton("📈 Статистика", callback_data='stats_menu')],
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        menu_text,
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
        "/stats - Статистика проверок\n\n"
        "*Основные функции:*\n"
        "🔍 Проверить коммит - просмотр информации о коммите\n"
        "📄 Анализ истории - проанализировать последние коммиты с помощью AI\n"
        "✅ Подтвердить коммит - отметить коммит как легитимный\n"
        "❌ Отклонить коммит - отметить коммит как подозрительный\n"
        "📊 История - просмотр истории проверок\n"
        "📈 Статистика - ваша статистика проверок\n\n"
        "*🤖 Главная страница теперь показывает:*\n"
        "📦 Все ваши репозитории\n"
        "📅 Дату последнего коммита\n"
        "⭐ Количество звезд\n"
        "💾 Язык программирования\n\n"
        "*🤖 AI Анализ Коммитов:*\n"
        "🐍 Локальная AI (Mistral) анализирует:\n"
        "✅ Прогресс разработки\n"
        "✅ Качество коммитов\n"
        "✅ Основные паттерны\n"
        "✅ Security-related исправления\n"
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
            text="📝 Введите полный URL репозитория GitHub или имя в формате: `owner/repo`\n\nПример: `sileade/github-commits-verifier-bot`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'check_commit'
        return REPO_INPUT
    
    elif callback_data == 'analyze_history':
        await query.edit_message_text(
            text="📄 Введите название репозитория (owner/repo)\n\nПример: `sileade/github-commits-verifier-bot`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'analyze_history'
        return REPO_INPUT
    
    elif callback_data == 'approve_commit':
        await query.edit_message_text(
            text="✅ Введите SHA коммита для подтверждения:\n\nПример: `a1b2c3d4e5f6g7h8`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'approve_commit'
        return COMMIT_INPUT
    
    elif callback_data == 'reject_commit':
        await query.edit_message_text(
            text="❌ Введите SHA коммита для отклонения:\n\nПример: `a1b2c3d4e5f6g7h8`",
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'reject_commit'
        return COMMIT_INPUT
    
    elif callback_data == 'history':
        user_id = update.effective_user.id
        history = await db.get_user_history(user_id, limit=10)
        
        if not history:
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📋 История пуста              ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "Вы еще не выполнили никаких проверок.",
                reply_markup=reply_markup
            )
        else:
            history_text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃  📊 История проверок (10)     ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            )
            for i, record in enumerate(history, 1):
                status_emoji = "✅" if record['status'] == 'approved' else "❌"
                history_text += f"{i}. {status_emoji} `{record['repo']}`\n"
                history_text += f"   🔗 {record['commit_sha'][:8]}...\n"
                history_text += f"   📅 {record['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                history_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return ConversationHandler.END
    
    elif callback_data == 'stats_menu':
        user_id = update.effective_user.id
        stats = await db.get_user_stats(user_id)
        global_stats = await db.get_global_stats()
        
        stats_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  📈 Статистика проверок       ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "*Ваша статистика:*\n"
            f"✅ Подтверждено: {stats['approved']}\n"
            f"❌ Отклонено: {stats['rejected']}\n"
            f"📊 Всего проверок: {stats['total']}\n\n"
            "*Общая статистика:*\n"
            f"👥 Уникальных пользователей: {global_stats.get('unique_users', 0)}\n"
            f"📊 Всего проверок: {global_stats.get('total_verifications', 0)}\n"
            f"✅ Всего подтверждено: {global_stats.get('approved', 0)}\n"
            f"❌ Всего отклонено: {global_stats.get('rejected', 0)}\n"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    elif callback_data == 'settings':
        # Placeholder for settings menu
        settings_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⚙️ Настройки                 ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Настройки пока недоступны."
        )
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            settings_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    elif callback_data == 'back_to_menu':
        # Go back to start menu
        await start(update, context)
        return ConversationHandler.END
    
    # Action confirmation callbacks
    elif callback_data.startswith('approve_') or callback_data.startswith('reject_'):
        action, commit_sha = callback_data.split('_')
        repo = context.user_data.get('repo')
        
        if not repo:
            await query.edit_message_text("❌ Ошибка: Репозиторий не найден в контексте.")
            return ConversationHandler.END
            
        user_id = update.effective_user.id
        status = 'approved' if action == 'approve' else 'rejected'
        
        success = await db.add_verification(user_id, repo, commit_sha, status)
        
        if success:
            await query.edit_message_text(
                f"✅ Коммит `{commit_sha[:8]}` в репозитории `{repo}` был *{status}*.\n\n"
                "Отправьте /start для главного меню."
            )
        else:
            await query.edit_message_text(
                f"❌ Ошибка при записи статуса коммита `{commit_sha[:8]}`."
            )
        
        return ConversationHandler.END
    
    # Analysis type selection
    elif callback_data.startswith('analysis_type_'):
        analysis_type = callback_data.split('_')[-1]
        repo = context.user_data.get('repo')
        
        if not repo:
            await query.edit_message_text("❌ Ошибка: Репозиторий не найден в контексте.")
            return ConversationHandler.END
            
        await query.edit_message_text(f"⏳ Запускаю AI анализ типа: *{analysis_type}* для `{repo}`...")
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        
        commits = await github_service.get_commit_history(repo, limit=50)
        
        if not commits:
            await query.edit_message_text(f"❌ Не удалось получить историю коммитов для `{repo}`.")
            return ConversationHandler.END
            
        analysis_result = await github_service.analyze_commits_with_ai(repo, commits, analysis_type)
        
        if analysis_result:
            result_text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃  🤖 Результат AI Анализа      ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"*Репозиторий:* `{repo}`\n"
                f"*Тип анализа:* {analysis_type}\n\n"
                f"{analysis_result}"
            )
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                result_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ Ошибка при выполнении AI анализа для `{repo}`. Проверьте логи."
            )
            
        return ConversationHandler.END
        
    return ConversationHandler.END


async def handle_repo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle repository input from user
    """
    repo_input = update.message.text.strip()
    action = context.user_data.get('action')
    
    # Try to parse owner/repo from input
    try:
        if repo_input.startswith('http'):
            # Extract from URL
            parts = repo_input.rstrip('/').split('/')
            repo_path = f"{parts[-2]}/{parts[-1]}"
        else:
            # Direct format
            repo_path = repo_input
            
        context.user_data['repo'] = repo_path
        
    except Exception:
        await update.message.reply_text(
            "❌ Неверный формат репозитория. Пожалуйста, введите полный URL или `owner/repo`."
        )
        return REPO_INPUT
        
    if action == 'check_commit':
        await update.message.reply_text(
            f"✅ Репозиторий `{repo_path}` принят.\n\n"
            "📝 Теперь введите SHA коммита для проверки:\n\nПример: `a1b2c3d4e5f6g7h8`",
            parse_mode='Markdown'
        )
        return COMMIT_INPUT
        
    elif action == 'analyze_history':
        # Show analysis type selection
        analysis_text = (
            f"✅ Репозиторий `{repo_path}` принят.\n\n"
            "*Выберите тип AI анализа:*"
        )
        keyboard = [
            [InlineKeyboardButton("📝 Обзор", callback_data='analysis_type_summary')],
            [InlineKeyboardButton("✨ Качество кода", callback_data='analysis_type_quality')],
            [InlineKeyboardButton("🔒 Безопасность", callback_data='analysis_type_security')],
            [InlineKeyboardButton("🔄 Паттерны", callback_data='analysis_type_patterns')],
            [InlineKeyboardButton("🔙 Отмена", callback_data='back_to_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            analysis_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ANALYSIS_TYPE
        
    return ConversationHandler.END


async def handle_commit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle commit SHA input from user
    """
    commit_sha = update.message.text.strip()
    action = context.user_data.get('action')
    repo = context.user_data.get('repo')
    
    if not repo:
        await update.message.reply_text("❌ Ошибка: Репозиторий не найден в контексте. Начните с /start.")
        return ConversationHandler.END
        
    if action == 'check_commit':
        await update.message.reply_text(f"⏳ Ищу информацию о коммите `{commit_sha[:8]}` в `{repo}`...")
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        
        try:
            commit_info = await github_service.get_commit_info(repo, commit_sha)
            
            if commit_info:
                context.user_data['commit_sha'] = commit_sha
                
                # Get files info
                files = await github_service.get_commit_files(repo, commit_sha)
                
                # Build detailed commit info
                commit_details = (
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃  🔍 Информация о коммите      ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                )
                
                commit_details += f"📦 Репозиторий: `{commit_info['repo']}`\n"
                commit_details += f"🔗 SHA: `{commit_info['sha']}`\n"
                commit_details += f"👤 Автор: {commit_info['author']}\n"
                commit_details += f"📧 Email: `{commit_info['author_email']}`\n"
                commit_details += f"📅 Дата: {commit_info['date']}\n\n"
                
                # Commit message
                commit_details += f"💬 Сообщение:\n`{commit_info['message']}`\n\n"
                
                # Files info
                if files:
                    commit_details += f"*🗁 Изменено {len(files)} файлов:*\n"
                    for file in files[:5]:  # Show first 5
                        status_emoji = {  
                            'added': '🆕',
                            'modified': '✍️',
                            'removed': '❌',
                            'renamed': '📄',
                            'copied': '📃',
                        }.get(file['status'], '📄')
                        commit_details += f"{status_emoji} {file['filename']} (+{file['additions']}/-{file['deletions']})\n"
                    if len(files) > 5:
                        commit_details += f"... и еще {len(files) - 5} файлов\n"
                    commit_details += "\n"
                
                # Signature status
                signature_status = "🔐 Подписано GPG" if commit_info['verified'] else "⚠️ Не подписано"
                commit_details += f"{signature_status}\n\n"
                
                # Verification checks
                checks = await github_service.verify_commit(commit_info)
                commit_details += "*✓ Результаты проверки:*\n"
                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "❌"
                    commit_details += f"{status} {check_name}\n"
                
                commit_details += f"\n[🔗 Открыть на GitHub]({commit_info['url']})"
                
                # Action buttons
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
                    f"❌ Коммит не найден.\n\n"
                    f"📌 Введите другой SHA или отправьте /start",
                    parse_mode='Markdown'
                )
                return COMMIT_INPUT
        
        except Exception as e:
            logger.error(f"Error handling commit: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
            return ConversationHandler.END
            
    elif action == 'approve_commit' or action == 'reject_commit':
        user_id = update.effective_user.id
        status = 'approved' if action == 'approve_commit' else 'rejected'
        
        success = await db.add_verification(user_id, repo, commit_sha, status)
        
        if success:
            await update.message.reply_text(
                f"✅ Коммит `{commit_sha[:8]}` в репозитории `{repo}` был *{status}*.\n\n"
                "Отправьте /start для главного меню."
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка при записи статуса коммита `{commit_sha[:8]}`."
            )
        
        return ConversationHandler.END
        
    return ConversationHandler.END


async def handle_analysis_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle analysis type selection from inline keyboard
    """
    # This function is now mostly handled by button_callback, but we keep the state for clarity
    return await button_callback(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel conversation
    """
    await update.message.reply_text(
        "❌ Операция отменена.\n\nОтправьте /start для главного меню."
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log errors
    """
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """
    Start the bot
    """
    # Get tokens from environment
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    # Create application
    application = Application.builder().token(telegram_token).build()
    
    # Add post_init and post_shutdown callbacks
    application.post_init = post_init
    application.post_shutdown = post_shutdown
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(button_callback, pattern='^(check_commit|analyze_history|approve_commit|reject_commit)$'),
        ],
        states={
            REPO_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_repo_input)],
            COMMIT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commit_input)],
            ACTION_CONFIRM: [
                CallbackQueryHandler(button_callback, pattern='^(approve_|reject_).*'),
                CallbackQueryHandler(button_callback, pattern='^back_to_menu$'),
            ],
            ANALYSIS_TYPE: [
                CallbackQueryHandler(button_callback, pattern='^analysis_type_.*'),
                CallbackQueryHandler(button_callback, pattern='^back_to_menu$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('stats', lambda u, c: button_callback(u, c) if u.message else button_callback(u, c), filters=filters.COMMAND))
    application.add_handler(CallbackQueryHandler(button_callback, pattern='^(history|stats_menu|settings|back_to_menu|approve_|reject_|analysis_type_).*'))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
