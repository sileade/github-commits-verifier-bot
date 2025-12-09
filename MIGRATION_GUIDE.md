# Примитение Новых Объектов - Практический Пример

## 1. Интеграция Конфигурации

### Шаг 1: Обновить bot.py

```python
# Не так (CTANАРО):
import os
import logging

logging.basicConfig(...)
logger = logging.getLogger(__name__)

db = None
github_service = None

async def post_init(app):
    global db, github_service
    db = Database()
    await db.init()
    github_service = GitHubService(os.getenv('GITHUB_TOKEN'))

# ТАК (НОВО):
from config import get_config
from utils import InputSanitizer, RepositoryParser, CommitValidator

# Главная конфигурация загружается одножды:
config = get_config()

db = None
github_service = None

async def post_init(app):
    global db, github_service
    db = Database(config.database.url)
    await db.init()
    github_service = GitHubService(config.github.token)
    app.bot_data['config'] = config
    logger.info(f"Initialized with config: {config.to_dict()}")
```

### Шаг 2: Обновить Обработчики

```python
# Не так (CTANАРО):
async def handle_repo_input(update, context):
    repo_input = update.message.text.strip()  # Затем код НЕ валидирует
    
    try:
        if repo_input.startswith('http'):
            parts = repo_input.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        else:
            owner, repo = repo_input.split('/')
        
        repo_info = await github_service.get_repository(repo_input)
        if repo_info:
            # ...
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

# ТАК (НОВО):
async def handle_repo_input(update, context):
    try:
        # 1. Очистить входные данные
        repo_input = InputSanitizer.sanitize_repo_path(update.message.text)
        
        # 2. Валидировать репозиторий
        owner, repo = RepositoryParser.parse_repo_path(repo_input)
        
        context.user_data['repo'] = f"{owner}/{repo}"
        
        # 3. Получить данные
        repo_info = await github_service.get_repository(f"{owner}/{repo}")
        if repo_info:
            await update.message.reply_text(
                f"✅ Понадо: {repo_info['full_name']}"
            )
        else:
            await update.message.reply_text(Еnot found")
    
    except ValueError as e:
        # Отдельная обработка ошибок конвалидации
        logger.warning(f"Invalid input: {e}")
        await update.message.reply_text(
            f"⚠️ {str(e)}\n\nПопни понад: owner/repo"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await update.message.reply_text("❌ Ошибка сервера")
```

### Шаг 3: Обновить Commit Обработку

```python
# Не так (CTANАРО):
async def handle_commit_input(update, context):
    commit_sha = update.message.text.strip()  # НЕ нормализировано
    repo = context.user_data.get('repo', 'unknown')
    
    try:
        # Просто валидация длины
        if len(commit_sha) < 7:
            await update.message.reply_text("❌ Не введи SHA")
            return COMMIT_INPUT

# ТАК (НОВО):
async def handle_commit_input(update, context):
    try:
        # 1. Очистить и нормализировать
        commit_sha = InputSanitizer.sanitize_commit_sha(update.message.text)
        
        # 2. Валидировать формат
        if not CommitValidator.validate_commit_sha(commit_sha):
            raise ValueError(
                f"Invalid SHA format. Expected 7-40 hex chars, got: {commit_sha}"
            )
        
        # 3. Получить данные
        repo = context.user_data.get('repo')
        commit_info = await github_service.get_commit_info(repo, commit_sha)
        
        if commit_info:
            # ...
            context.user_data['commit_sha'] = commit_sha
        else:
            await update.message.reply_text(Оне найден")
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        await update.message.reply_text(f"⚠️ {str(e)}")
        return COMMIT_INPUT
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await update.message.reply_text("❌ Ошибка сервера")
        return ConversationHandler.END
```

## 2. Обновить github_service.py

### Рекомендуемые исправления:

```python
from config import Config
from utils import RepositoryParser

class GitHubService:
    def __init__(self, token: str, config: Config = None):
        self.token = token
        self.config = config or Config()
        self.api_timeout = self.config.github.api_timeout
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
    
    async def _parse_repo_path(self, repo_path: str):
        """
        Вытячите теперь всегда использует утилиты
        """
        return RepositoryParser.parse_repo_path(repo_path)
    
    async def get_repository(self, repo_path: str):
        """
        Обновленная реализация с правильной обработкой
        """
        try:
            # Одноместная либерта
            owner, repo = await self._parse_repo_path(repo_path)
            
            # Адрес
            url = f"{self.api_url}/repos/{owner}/{repo}"
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.api_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return {
                'full_name': data['full_name'],
                'url': data['html_url'],
                'description': data.get('description', ''),
                'stars': data['stargazers_count'],
                'language': data.get('language', 'N/A'),
            }
        except ValueError as e:
            logger.warning(f"Repository path parsing error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API error: {e}")
            return None
```

## 3. Обновить database.py

```python
from config import get_config

config = get_config()

class Database:
    def __init__(self, db_url: Optional[str] = None):
        # Теперь всегда работаетя с config
        self.db_url = db_url or config.database.url
        self.pool_min = config.database.pool_min_size
        self.pool_max = config.database.pool_max_size
        self.pool = None
    
    async def init(self) -> None:
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=self.pool_min,
                max_size=self.pool_max,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
            )
            logger.info(f"Connected to PostgreSQL "
                       f"({self.pool_min}-{self.pool_max} connections)")
            await self._init_tables()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
```

## 4. Проверка Кода

```bash
# Проверить качество
pylint bot.py --disable=all --enable=E,F
pyflakes bot.py github_service.py database.py
python -m py_compile bot.py config.py utils.py

# Проверить типы (если установлен mypy)
mypy bot.py --ignore-missing-imports --no-error-summary 2>/dev/null || true
```

## 5. Подготовка К Производству

```bash
# 1. Обновить .env
echo "LOG_LEVEL=INFO" >> .env
echo "CACHE_ENABLED=true" >> .env
echo "AI_PROVIDER=hybrid" >> .env

# 2. Попробуйте конфигурацию
python -c "from config import get_config; c = get_config(); print(c.to_dict())"

# 3. Перезапустите Docker
docker-compose down
docker-compose up -d

# 4. Объёдините хеширование
docker-compose logs -f bot
```

## 6. ОМ Чек-лист

- [ ] Копировать utils.py и config.py в проект
- [ ] Обновить import в bot.py
- [ ] Обновить import в github_service.py
- [ ] Обновить import в database.py
- [ ] Удалить дублированные контролеры аргументов
- [ ] Не забудьте жабать тесты
- [ ] Проверить танинг в расчету работы

---

## тОцжеМ

При любого вопроса, смотрите:
1. `REFACTORING_REPORT.md` - детальные анализ и стратегия
2. `IMPROVEMENTS_SUMMARY.md` - сразу увидеть ресультаты
3. Новые модули: `utils.py` и `config.py`
