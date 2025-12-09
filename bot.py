#!/usr/bin/env python3
"""
Telegram Bot for GitHub Commits Verification
Проверка и подтверждение коммитов приложений в GitHub
"""

import os
import logging
import asyncio
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
REPO_INPUT, COMMIT_INPUT, ACTION_CONFIRM, CONFIRM_ACTION, EXPORT_ACTION, BRANCH_INPUT, ANALYSIS_TYPE, COMMIT_LIST, BOT_CONTROL = range(9)

# Global service instances
db: Optional[Database] = None
github_service: Optional[GitHubService] = None


async def post_init(_app: Application) -> None:
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
        logger.error("Failed to initialize database: %s", e)
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


async def post_shutdown(_app: Application) -> None:
    """
    Clean up resources on shutdown
    """
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
                    logger.warning("Error getting last commit for %s: %s", repo['full_name'], last_commit)
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
        logger.error("Error getting user repositories: %s", e)
        return {}


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start command handler - show main menu with repository status
    """
    if not db:
        await update.message.reply_text("❌ Сервисы не инициализированы. Попробуйте позже.")
        return
        
    user_id = update.effective_user.id
    
    await db.add_user(user_id, update.effective_user.username or 'unknown')
    
    menu_text = (
        "🤖 *GitHub Commits Verifier*\n\n"
        "Проверка и анализ коммитов GitHub\n"
        "с помощью AI и автоматизации\n\n"
    )
    
    # Add repository status if available
    try:
        repos_status = await get_user_repositories_status()
        
        if repos_status:
            menu_text += "*📦 Ваши репозитории:*\n\n"
            
            for _, repo_info in sorted(repos_status.items()):
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
                    menu_text += "  📅 Последний коммит: Не найден\n"
                
                menu_text += "\n"
    except Exception as e:
        logger.error("Error loading repositories status: %s", e)
        menu_text += "*⚠️ Не удалось загрузить статус репозиториев*\n\n"
    
    menu_text += "\n*Выберите действие:*"
    
    # Two-column layout optimized for mobile
    keyboard = [
        [InlineKeyboardButton("🔍 Проверить", callback_data='check_commit'),
         InlineKeyboardButton("✅ Подтвердить", callback_data='approve_commit')],
        [InlineKeyboardButton("📄 История", callback_data='analyze_history'),
         InlineKeyboardButton("❌ Отклонить", callback_data='reject_commit')],
        [InlineKeyboardButton("📊 Мои данные", callback_data='history'),
         InlineKeyboardButton("📈 Статистика", callback_data='stats_menu')],
        [InlineKeyboardButton("📊 GitHub Аналитика", callback_data='github_analytics'),
         InlineKeyboardButton("🤖 Управление", callback_data='bot_control')],
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        menu_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Help command
    """
    help_text = (
        "📚 *Справка по командам*\n\n"
        "`/start` - Главное меню\n"
        "`/help` - Эта справка\n"
        "`/stats` - Статистика проверок\n\n"
        "*Основные функции:*\n\n"
        "🔍 *Проверить* - информация о коммите\n"
        "✅ *Подтвердить* - отметить как легитимный\n"
        "📄 *История* - анализ последних коммитов\n"
        "❌ *Отклонить* - отметить как подозрительный\n"
        "📊 *Мои данные* - история проверок\n"
        "📈 *Статистика* - ваша статистика\n\n"
        "*🤖 AI Анализ:*\n\n"
        "• Прогресс разработки\n"
        "• Качество коммитов\n"
        "• Основные паттерны\n"
        "• Security-анализ\n"
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
            text=(
                "📝 Введите полный URL репозитория GitHub или имя в формате: "
                "`owner/repo`\n\nПример: `sileade/github-commits-verifier-bot`"
            ),
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
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="✅ Введите репозиторий (owner/repo) для просмотра коммитов:\n\nПример: `sileade/github-commits-verifier-bot`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        context.user_data['action'] = 'approve_commit'
        return REPO_INPUT
    
    elif callback_data == 'reject_commit':
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="❌ Введите репозиторий (owner/repo) для просмотра коммитов:\n\nПример: `sileade/github-commits-verifier-bot`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        context.user_data['action'] = 'reject_commit'
        return REPO_INPUT
    
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
    
    elif callback_data == 'github_analytics':
        # GitHub Analytics Dashboard
        await query.answer()
        await query.edit_message_text("⏳ Загрузка аналитики GitHub...")
        
        try:
            # Get user's repositories
            repos = await github_service.get_user_repositories()
            
            if not repos:
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "❌ Не удалось загрузить репозитории.",
                    reply_markup=reply_markup
                )
                return ConversationHandler.END
            
            # Calculate statistics
            total_repos = len(repos)
            total_stars = sum(r.get('stars', 0) for r in repos)
            languages = {}
            for repo in repos:
                lang = repo.get('language', 'Unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            top_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'N/A'
            
            analytics_text = (
                "📊 *GitHub Аналитика*\n\n"
                f"📦 Всего репозиториев: *{total_repos}*\n"
                f"⭐ Всего звёзд: *{total_stars}*\n"
                f"💻 Основной язык: *{top_language}*\n\n"
                "*Топ-5 репозиториев:*\n"
            )
            
            # Sort by stars and show top 5
            sorted_repos = sorted(repos, key=lambda x: x.get('stars', 0), reverse=True)[:5]
            for i, repo in enumerate(sorted_repos, 1):
                analytics_text += f"{i}. `{repo['name']}` - ⭐ {repo.get('stars', 0)}\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                analytics_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error("Error in GitHub analytics: %s", e)
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Ошибка при загрузке аналитики.",
                reply_markup=reply_markup
            )
        
        return ConversationHandler.END
    
    elif callback_data == 'bot_control':
        # Bot Control Panel
        control_text = (
            "🤖 *Панель управления ботом*\n\n"
            "⚠️ *Внимание:* Эти команды доступны только администраторам.\n\n"
            "💻 *Команды для сервера:*\n"
            "```bash\n"
            "# Перезапуск бота\n"
            "cd /opt/github-commits-verifier-bot\n"
            "./restart.sh\n\n"
            "# Остановка бота\n"
            "./stop.sh\n\n"
            "# Запуск бота\n"
            "./start.sh\n\n"
            "# Просмотр логов\n"
            "docker logs -f github-commits-verifier-bot\n\n"
            "# Обновление бота\n"
            "./update.sh\n"
            "```\n\n"
            "👁️ *Статус:* Бот работает нормально"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить бот", callback_data='update_bot')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            control_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    elif callback_data == 'update_bot':
        # Quick update bot from repository
        await query.answer()
        await query.edit_message_text(
            "⏳ *Обновление бота...*\n\n"
            "📥 Получение последних изменений из GitHub...",
            parse_mode='Markdown'
        )
        
        try:
            import subprocess
            import os
            
            # Check if update script exists
            update_script = '/opt/github-commits-verifier-bot/update.sh'
            if not os.path.exists(update_script):
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='bot_control')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "❌ *Ошибка*\n\n"
                    f"Скрипт обновления не найден: `{update_script}`\n\n"
                    "💻 Выполните вручную:\n"
                    "```bash\n"
                    "cd /opt/github-commits-verifier-bot\n"
                    "git pull origin main\n"
                    "./restart.sh\n"
                    "```",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
            
            # Run update script
            result = subprocess.run(
                [update_script],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                cwd='/opt/github-commits-verifier-bot'
            )
            
            if result.returncode == 0:
                keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "✅ *Бот успешно обновлён!*\n\n"
                    "🔄 Бот был перезапущен с последней версией из GitHub.\n\n"
                    "👁️ Проверьте работу бота, отправив /start",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='bot_control')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                error_msg = result.stderr[:500] if result.stderr else 'Неизвестная ошибка'
                await query.edit_message_text(
                    "❌ *Ошибка при обновлении*\n\n"
                    f"```\n{error_msg}\n```\n\n"
                    "💻 Попробуйте выполнить вручную:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except subprocess.TimeoutExpired:
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='bot_control')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ *Таймаут*\n\n"
                "Обновление заняло слишком много времени (>5 мин).\n\n"
                "💻 Проверьте логи сервера.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error("Error updating bot: %s", e)
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='bot_control')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ *Ошибка*\n\n"
                f"Не удалось выполнить обновление: `{str(e)}`\n\n"
                "💻 Выполните вручную:\n"
                "```bash\n"
                "cd /opt/github-commits-verifier-bot\n"
                "./update.sh\n"
                "```",
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
        # Parse callback data: action_sha_repo
        parts = callback_data.split('_', 1)
        action = parts[0]
        
        if len(parts) > 1 and '_' in parts[1]:
            # New format: approve_sha_owner/repo
            sha_and_repo = parts[1]
            # Find the last underscore to split SHA and repo
            last_underscore = sha_and_repo.rfind('_')
            commit_sha = sha_and_repo[:last_underscore]
            repo = sha_and_repo[last_underscore+1:]
        else:
            # Old format: approve_sha (get repo from context)
            commit_sha = parts[1] if len(parts) > 1 else ''
            repo = context.user_data.get('repo')
        
        if not repo:
            await query.edit_message_text("❌ Ошибка: Репозиторий не найден.")
            return ConversationHandler.END
            
        user_id = update.effective_user.id
        status = 'approved' if action == 'approve' else 'rejected'
        status_emoji = "✅" if action == 'approve' else "❌"
        status_text = "подтверждён" if action == 'approve' else "отклонён"
        
        success = await db.add_verification(user_id, repo, commit_sha, status)
        
        keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if success:
            await query.edit_message_text(
                f"{status_emoji} *Коммит {status_text}*\n\n"
                f"📦 Репозиторий: `{repo}`\n"
                f"🔑 SHA: `{commit_sha[:8]}`\n"
                f"📊 Статус: *{status_text}*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ Ошибка при записи статуса коммита `{commit_sha[:8]}`.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
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
            [InlineKeyboardButton("📝 Обзор", callback_data='analysis_type_summary'),
             InlineKeyboardButton("✨ Качество", callback_data='analysis_type_quality')],
            [InlineKeyboardButton("🔒 Безопасность", callback_data='analysis_type_security'),
             InlineKeyboardButton("🔄 Паттерны", callback_data='analysis_type_patterns')],
            [InlineKeyboardButton("🔙 Отмена", callback_data='back_to_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            analysis_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ANALYSIS_TYPE
    
    elif action in ['approve_commit', 'reject_commit']:
        # Show commit list for selection
        await update.message.reply_text("⏳ Загрузка коммитов...")
        
        commits = await github_service.get_commit_history(repo_path, limit=10)
        
        if not commits:
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ Не удалось получить коммиты для `{repo_path}`.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Build commit list with buttons
        action_emoji = "✅" if action == 'approve_commit' else "❌"
        action_text = "Подтвердить" if action == 'approve_commit' else "Отклонить"
        
        commits_text = (
            f"{action_emoji} *{action_text} коммит*\n\n"
            f"📦 Репозиторий: `{repo_path}`\n"
            f"📝 Последние коммиты:\n\n"
        )
        
        keyboard = []
        for i, commit in enumerate(commits[:10], 1):
            sha = commit['sha'][:8]
            message = commit['message'][:50] + '...' if len(commit['message']) > 50 else commit['message']
            commits_text += f"{i}. `{sha}` - {message}\n"
            
            # Add button for each commit
            button_text = f"{i}. {sha}"
            callback_prefix = 'approve_' if action == 'approve_commit' else 'reject_'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{callback_prefix}{commit['sha']}_{repo_path}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            commits_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return COMMIT_LIST
        
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
                        commit_details += (
                            f"{status_emoji} {file['filename']} "
                            f"(+{file['additions']}/-{file['deletions']})\n"
                        )
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
                    "❌ Коммит не найден.\n\n"
                    "📌 Введите другой SHA или отправьте /start",
                    parse_mode='Markdown'
                )
                return COMMIT_INPUT
        
        except Exception as e:
            logger.error("Error handling commit: %s", e)
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


async def cancel(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel conversation
    """
    await update.message.reply_text(
        "❌ Операция отменена.\n\nОтправьте /start для главного меню."
    )
    return ConversationHandler.END


async def error_handler(_update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    application.add_handler(
        CommandHandler(
            'stats',
            lambda u, c: button_callback(u, c) if u.message else button_callback(u, c),
            filters=filters.COMMAND
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            button_callback,
            pattern='^(history|stats_menu|settings|back_to_menu|approve_|reject_|analysis_type_).*'
        )
    )
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
