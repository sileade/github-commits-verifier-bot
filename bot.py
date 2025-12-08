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

# Database and GitHub service (initialized at startup)
db: Optional[Database] = None
github_service: Optional[GitHubService] = None


async def post_init(app: Application) -> None:
    """
    Initialize database and services after application startup
    """
    global db, github_service
    
    logger.info("Initializing services...")
    
    # Initialize database
    db = Database()
    await db.init()
    
    # Initialize GitHub service
    github_token = os.getenv('GITHUB_TOKEN')
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    if not github_token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")
    github_service = GitHubService(github_token, ollama_host)
    
    logger.info("Services initialized successfully")


async def post_shutdown(app: Application) -> None:
    """
    Clean up resources on shutdown
    """
    global db
    if db:
        await db.close()
    logger.info("Shutdown complete")


async def get_user_repositories_status(github_token: str) -> dict:
    """
    Get user repositories with their status and last commit dates
    """
    try:
        service = GitHubService(github_token)
        repos = await service.get_user_repositories()
        
        status_info = {}
        for repo in repos[:10]:  # Limit to 10 repos for display
            try:
                last_commit = await service.get_last_commit(repo['full_name'])
                status_info[repo['full_name']] = {
                    'name': repo['name'],
                    'stars': repo.get('stargazers_count', 0),
                    'language': repo.get('language', 'Unknown'),
                    'url': repo['html_url'],
                    'last_commit': last_commit,
                    'private': repo.get('private', False),
                }
            except Exception as e:
                logger.warning(f"Error getting last commit for {repo['full_name']}: {e}")
                status_info[repo['full_name']] = {
                    'name': repo['name'],
                    'stars': repo.get('stargazers_count', 0),
                    'language': repo.get('language', 'Unknown'),
                    'url': repo['html_url'],
                    'last_commit': None,
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
    user_id = update.effective_user.id
    github_token = os.getenv('GITHUB_TOKEN')
    
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
        repos_status = await get_user_repositories_status(github_token)
        
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
                history_text += f"   📅 {record['created_at']}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(history_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif callback_data == 'stats_menu':
        user_id = update.effective_user.id
        stats = await db.get_user_stats(user_id)
        
        stats_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  📈 Ваша статистика            ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        )
        
        stats_text += f"✅ Подтверждено: **{stats['approved']}**\n"
        stats_text += f"❌ Отклонено: **{stats['rejected']}**\n"
        stats_text += f"🔍 Всего проверено: **{stats['total']}**\n\n"
        
        if stats['total'] > 0:
            approval_ratio = (stats['approved'] / stats['total']) * 100
            stats_text += f"📊 Процент одобрений: **{approval_ratio:.1f}%**\n\n"
            
            # Visual bar
            bar_length = 20
            filled = int((approval_ratio / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            stats_text += f"[{bar}]\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif callback_data == 'settings':
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⚙️ Настройки                  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Используйте /help для информации о конфигурации.",
            reply_markup=reply_markup
        )
    
    elif callback_data == 'back_to_menu':
        # Return to main menu
        await start(update, context)
    
    return ConversationHandler.END


async def handle_repo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle repository input
    """
    repo_input = update.message.text.strip()
    
    action = context.user_data.get('action')
    
    if action == 'analyze_history':
        # Analyze commit history with AI
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            # Show loading message
            msg = await update.message.reply_text(
                f"📄 Загружаю историю коммитов из `{repo_input}`...\n\n"
                f"Инициализация Mistral AI...",
                parse_mode='Markdown'
            )
            
            # Get commit history
            commits = await github_service.get_commit_history(repo_input, limit=50)
            
            if not commits:
                await msg.edit_text(
                    f"❌ Не удалось получить историю коммитов."
                )
                return REPO_INPUT
            
            await msg.edit_text(
                f"📄 Последние {len(commits)} коммитов загружены!\n\n"
                f"🤖 Анализирую с помощью Mistral (may take 30-60 seconds)...",
                parse_mode='Markdown'
            )
            
            # Show analysis type menu
            keyboard = [
                [InlineKeyboardButton("📈 Обзор прогресса", callback_data='analyze_summary')],
                [InlineKeyboardButton("✅ Оценка качества", callback_data='analyze_quality')],
                [InlineKeyboardButton("🔐 Поиск Security фиксов", callback_data='analyze_security')],
                [InlineKeyboardButton(📈 Выявление паттернов", callback_data='analyze_patterns')],
                [InlineKeyboardButton("🔙 Отмена", callback_data='back_to_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            context.user_data['commits'] = commits
            context.user_data['repo'] = repo_input
            
            await msg.edit_text(
                f"📄 *На что вы хотите сосредоточить анализ?*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return ANALYSIS_TYPE
        except Exception as e:
            logger.error(f"Error in analyze_history: {e}")
            await msg.edit_text(f"❌ Ошибка: {str(e)}")
            return REPO_INPUT
    else:
        # Original check_commit flow
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            repo_info = await github_service.get_repository(repo_input)
            
            if repo_info:
                context.user_data['repo'] = repo_input
                await update.message.reply_text(
                    f"✅ Репозиторий найден!\n\n"
                    f"📦 `{repo_info['full_name']}`\n"
                    f"⭐ Stars: {repo_info['stars']}\n"
                    f"💾 Language: {repo_info['language']}\n\n"
                    f"📌 Введите SHA коммита для проверки:",
                    parse_mode='Markdown'
                )
                return COMMIT_INPUT
            else:
                await update.message.reply_text(
                    "❌ Репозиторий не найден.\n\n"
                    "Проверьте URL или имя в формате `owner/repo`",
                    parse_mode='Markdown'
                )
                return REPO_INPUT
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
            return REPO_INPUT


async def handle_analysis_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle analysis type selection
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Map callback to analysis type
    analysis_types = {
        'analyze_summary': 'summary',
        'analyze_quality': 'quality',
        'analyze_security': 'security',
        'analyze_patterns': 'patterns',
    }
    
    if callback_data not in analysis_types:
        return ANALYSIS_TYPE
    
    analysis_type = analysis_types[callback_data]
    commits = context.user_data.get('commits', [])
    repo = context.user_data.get('repo', '')
    
    try:
        await query.edit_message_text(
            f"🤖 Провожу AI анализ... (цисло могут занять 30-60 секунд)\n\n"
            f"📄 Тип: {analysis_type}\n"
            f"📦 Репозиторий: `{repo}`\n"
            f"д Коммитов: {len(commits)}",
            parse_mode='Markdown'
        )
        
        # Call AI analysis
        result = await github_service.analyze_commits_with_ai(repo, commits, analysis_type)
        
        if result:
            # Format result
            result_text = f"""
🤖 *AI Анализ ({analysis_type})*
📦 Репозиторий: `{repo}`
📅 Коммитов: {len(commits)}

*Результат:*

{result}
"""
            
            # If result is too long, send in parts
            if len(result_text) > 4000:
                await query.edit_message_text(
                    result_text[:4000] + "\n\n... (результат обрезан)",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(result_text, parse_mode='Markdown')
        else:
            await query.edit_message_text(
                "❌ Не удалось проанализировать (твердятся, что Оллама работает)"
            )
    except Exception as e:
        logger.error(f"Error in handle_analysis_type: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    
    return ConversationHandler.END


async def handle_commit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle commit SHA input
    """
    commit_sha = update.message.text.strip()
    
    await update.message.chat.send_action(ChatAction.TYPING)
    
    action = context.user_data.get('action')
    repo = context.user_data.get('repo', 'unknown')
    
    try:
        if action == 'check_commit':
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
                    commit_details += f"*🗁 Отсканыры {len(files)} файлов:*\n"
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
    
    # Add post_init callback
    application.post_init = post_init
    application.post_shutdown = post_shutdown
    
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
                CallbackQueryHandler(button_callback),
            ],
            ANALYSIS_TYPE: [
                CallbackQueryHandler(handle_analysis_type),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
