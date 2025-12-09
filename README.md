# 🤖 GitHub Commits Verifier Bot v3.5 - Major Feature Update

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT%2D3.5-blue.svg)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-LocalLLM-green.svg)](https://ollama.ai/)

**Professional Telegram bot for verifying GitHub commits with AI-powered analysis (cloud or local), diff viewing, and code export to branches.**

> **🚀 v3.7 Update:** This version completes the UI improvement with repository selectors for all menu items and functional bot control buttons (Start/Stop/Restart).

---

## ✨ Key Features & Recent Improvements

### 🚀 **NEW in v3.7: Complete UI Improvement**

#### 🗂️ **Repository Selector for All Menu Items**
- **Zero manual input!** All menu items now use button-based repository selection.
- 🔍 **Check Commit:** Select repository from your GitHub repos, then select commit from list.
- 📄 **Analyze History:** Select repository from your GitHub repos to view commit history.
- ✅ **Approve Commit:** Select repository, then select commit to approve.
- ❌ **Reject Commit:** Select repository, then select commit to reject.
- Repositories are displayed in a 2-column grid for easy browsing.
- Each repository button shows the repository name (truncated if too long).

#### 🎮 **Functional Bot Control Buttons**
- **▶️ Start Bot:** Executes `docker-compose up -d` to start the bot service.
- **⏸️ Stop Bot:** Executes `docker-compose down` to stop the bot service.
- **🔄 Restart Bot:** Executes `docker-compose restart` to restart the bot service.
- **🔄 Update Bot:** Runs `update.sh` script to pull latest code from GitHub and restart.
- All buttons show real-time status and error messages.
- Includes timeout protection (60 seconds for start/stop/restart, 5 minutes for update).

### 🚀 **v3.5 Features**

#### 📄 **Commit List Browsing**
- Displays a list of the last 10 commits from the selected repository.
- Each commit shows its short SHA (8 characters) and message (truncated to 50 characters).
- Simply click on a commit button to view details or approve/reject it.
- Includes a "Back" button to return to the previous menu.

#### 🔙 **Back Buttons Everywhere**
- Every submenu now has a "Back" button for easy navigation.
- No more getting stuck in submenus - always one click away from the main menu.
- Improved user experience with intuitive navigation flow.

#### 📊 **GitHub Analytics Dashboard**
- New analytics panel accessible from the main menu.
- Displays comprehensive repository statistics:
  - **Total repositories:** Count of all your GitHub repos
  - **Total stars:** Sum of stars across all repositories
  - **Primary language:** Most commonly used programming language
  - **Top 5 repositories:** Sorted by star count with quick overview
- Helps you understand your GitHub presence at a glance.

#### 🤖 **Bot Control Panel with Quick Update**
- **One-click bot updates!** New "Update Bot" button in the control panel.
- Automatically runs the `update.sh` script from within Telegram.
- Shows real-time status during the update process.
- Handles errors gracefully with helpful fallback instructions.
- Includes all essential bot management commands:
  - Restart bot
  - Stop bot
  - Start bot
  - View logs
  - Update bot (automated)
- Perfect for administrators who want to manage the bot without SSH access.

### 📱 **New Interface Design (v3.4)**
- **Two-Column Menu:** The main menu and other menus now use a two-column layout, making them more compact and easier to navigate on mobile devices.
- **Mobile-Friendly Buttons:** Buttons now have shorter, more intuitive labels with emojis for better visual appeal.
- **Simplified Interface:** The UI has been simplified to reduce clutter and improve user experience.
- **Adaptive Layout:** The new layout is designed to be responsive and adapt to different screen sizes.

### 🚀 **NEW in v3.3: Code Quality & Stability**
- **Comprehensive Refactoring:** The entire codebase was analyzed and refactored to improve stability and performance.
- **Bug Fixes:** Fixed critical bugs, including a missing `asyncio` import and incorrect method arguments.
- **Code Quality:** Removed all unused imports, fixed f-strings without placeholders, and resolved all `pylint` warnings.
- **Improved Logging:** Converted all logging f-strings to lazy % formatting for better performance.
- **Enhanced Stability:** Improved exception handling to prevent crashes and ensure the bot remains responsive.

### 🚀 **NEW in v3.1: Performance & Stability**
- **Asynchronous I/O:** Replaced blocking `requests` with non-blocking `aiohttp` in `github_service.py` for all GitHub and Ollama API calls. This eliminates event loop blocking and drastically improves concurrency.
- **Optimized Startup:** Parallel fetching of repository status using `asyncio.gather` speeds up the main menu load time.
- **Improved Database Handling:** Stricter environment variable checking for `DATABASE_URL` and better error handling in `database.py`.

### 🔍 Commit Verification
- Detailed commit information with author, date, message
- GPG signature verification
- Automatic legitimacy checks
- Clickable GitHub links

### 🤖 AI-Powered Analysis (Local or Cloud)

**Choose your AI:**

| Feature | Local (Ollama) 🏠 | Cloud (OpenAI) ☁️ |
|---------|---|---|
| **Cost** | 💰 FREE | ~$0.0005 per analysis |
| **Privacy** | 🔒 100% local | Cloud-based |
| **Speed** | ⚡ 5-30 sec (CPU) or <5 sec (GPU) | 2-5 seconds |
| **Quality** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Internet** | ❌ Not needed | ✅ Required |
| **Setup** | 🐳 Automatic with Docker | 🔑 API key |
| **Auto Model Load** | ✅ Yes (Mistral) | N/A |

**AI Features:**
- **Smart Summaries** - AI generates brief summary of what changed
- **Impact Assessment** - Understands how changes affect codebase
- **Code Review** - Identifies strengths and concerns automatically
- **Security Analysis** - Detects potential security issues
- **Quality Score** - Rates commit quality 1-10
- **Recommendations** - Suggests APPROVE/REVIEW/REJECT

### ✅ Approval System
- Mark commits as verified/legitimate
- Track approval metrics
- Full audit trail in PostgreSQL

### ❌ Rejection Tracking
- Flag suspicious commits
- Statistics dashboard
- Historical records

### 📄 Diff Viewing
- View complete code changes inline
- Small diffs (<4KB): Display in chat
- Large diffs: Download as `.patch` file
- Full patch format for external tools

### 📝 File Change Logs
- Status indicators: 🆕 added, ✏️ modified, ❌ removed, 📄 renamed, 📋 copied
- Line counters: +additions/-deletions
- First 5 files shown, summary for larger commits

### 📤 Code Export to Branches
- **Export to existing branch:** Select from dropdown, auto cherry-pick
- **Create new branch:** Enter name, bot creates and cherry-picks
- **Get GitHub link:** Click to view in browser

### 📊 History & Statistics
- Browse verification history
- Approval/rejection ratio visualization
- Per-user statistics
- Global statistics (if admin)

### 💾 PostgreSQL Persistence
- Enterprise-grade RDBMS backend
- ACID transaction support
- Automatic backups capability
- Scalable architecture

### 🔗 GitHub Integration
- Full GitHub REST API support
- Commit verification
- Branch management
- Cherry-pick operations
- File diff viewing

### 🎨 Beautiful UI
- Box-framed menus (Unicode borders)
- Emoji-rich interface
- Visual indicators for status
- Intuitive inline keyboards

### 🐳 Production-Ready
- Docker Compose setup
- Health checks
- Resource limits
- Security hardening
- Non-root user execution
- Graceful shutdown
- **Auto model loading for Ollama**

---

## ⚡ Quick Start (One Command)

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot
chmod +x setup.sh && ./setup.sh
```

The setup script will:
- ✅ Generate secure PostgreSQL password
- ✅ Create `.env` configuration
- ✅ Prompt for Telegram & GitHub tokens
- ✅ Start PostgreSQL container
- ✅ Initialize database
- ✅ Build Docker image
- ✅ Ready to use!

Then start the bot:
```bash
./start.sh
# or
docker-compose up -d
```

> **Note:** First startup will auto-download Mistral model (~5-15 minutes). Subsequent startups are instant! ⚡

---

## 🤖 AI Analysis: Local vs Cloud

### Option 1: Local LLM (FREE) 🏠 — **RECOMMENDED**

**Best for:** Teams valuing privacy, cost, and offline capability

```bash
# Quick setup (2 steps!)
chmod +x setup.sh start.sh
./setup.sh  # Select YES for Ollama
./start.sh  # Auto-downloads Mistral on first run
```

Features:
- 💰 **Completely FREE** after initial setup
- 🔒 **100% private** - no data leaves your servers
- 🌐 **Offline capable** - no internet required
- ⚡ **Fast with GPU** - <5 seconds per analysis
- 🎯 **Customizable** - run Mistral, Llama2, Neural Chat, etc.
- **✅ Auto-loads model on startup** - no manual steps needed!

Models available (auto-loadable):
- **Mistral** (7B) - Recommended, fast + good quality **[AUTO-SELECTED]**
- **Llama2** (7B/13B) - Best quality
- **Neural Chat** (7B) - Optimized for chat
- **Dolphin Mixtral** (8.7B) - Smart + fast
- **OpenChat** (3.5B) - Ultra-light

See [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md) for detailed guide.

### Option 2: Cloud (OpenAI) ☁️

**Best for:** Teams wanting best quality without infrastructure

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Features:
- 🎯 **Highest quality** - GPT-3.5 Turbo
- ⚡ **Fastest** - 2-5 seconds per analysis
- 🔧 **No setup** - just add API key
- 📊 **Usage stats** - track costs easily

Costs:
- ~$0.0005 per analysis
- ~$0.50 per 1000 commits
- ~$5 per 10,000 commits

See [ai_analyzer_integration.md](ai_analyzer_integration.md) for details.

### Option 3: Hybrid (Smart) 🧠

**Best for:** Cost-conscious teams wanting fallback

```env
# Use BOTH - bot auto-selects best option
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Behavior:
1. Try local Mistral first (instant, free)
2. If slow/unavailable → fallback to OpenAI
3. User never waits, never pays unnecessarily

---

## 🧩 Minimal Checklist for Full Local Setup (GPU, No OpenAI)

> Оптимизировано под типичный стенд: Linux + Docker + NVIDIA GPU + домашний/офисный сервер.

### 1. Хостовая машина

- OS: Linux (Debian/Ubuntu/Proxmox LXC/VM)
- Docker + Docker Compose установлены
- NVIDIA драйвера и nvidia-container-toolkit (для GPU)
- ОЗУ: от 8 ГБ (лучше 16+)
- VRAM: от 4 ГБ (для 7B модели) или 8+ ГБ (для 13B)

Проверка:
```bash
docker --version
docker-compose --version
nvidia-smi          # если есть GPU
```

### 2. Клонируем репозиторий

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot
chmod +x setup.sh start.sh stop.sh restart.sh
```

### 3. Базовая конфигурация (.env)

```bash
./setup.sh
```

**Скрипт спросит:**
- `TELEGRAM_BOT_TOKEN` — от BotFather
- `GITHUB_TOKEN` — Personal Access Token (repo + read:user)
- `USE_LOCAL_MODEL` — **выбираешь YES**
- `LOCAL_MODEL` — mistral (рекомендуется)

Дальше **руками добавляешь в .env:**

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral
OPENAI_API_KEY=  # оставить пустым
```

### 4. Включаем GPU для Ollama (опционально, но сильно рекомендуется)

В `docker-compose.yml` в сервисе `ollama` раскомментируешь:

```yaml
ollama:
  # ...
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
```

> На хосте должен быть настроен `nvidia-container-toolkit`.

### 5. Первый запуск

```bash
./start.sh
```

Скрипт **автоматически**:
- ✅ проверит `.env`
- ✅ соберёт Docker образ
- ✅ поднимет PostgreSQL
- ✅ поднимет Ollama
- ✅ **автоматически скачает модель mistral** (5-15 минут)
- ✅ запустит бота
- ✅ дождётся healthcheck-ов

### 6. Проверка что всё живо

```bash
docker-compose ps

# Ожидаемое состояние:
# github-commits-postgres       Up (healthy)
# ollama                        Up (healthy)
# github-commits-verifier-bot   Up (healthy)
```

Логи:
```bash
docker logs -f ollama              # скачивание модели
docker logs -f github-commits-bot   # логи бота
```

### 7. Telegram

- Открыть Telegram
- Найти своего бота по username
- Отправить `/start`
- Проверить первый коммит

### 8. Дальнейшая рутина

Остановить:
```bash
./stop.sh
```

Запустить снова:
```bash
./start.sh
```

Перебилдить (после обновления кода):
```bash
git pull origin main
./restart.sh
```

---

## 🛠️ Prerequisites

- **Docker & Docker Compose** v3.8+ (auto-downloads Mistral)
- **OpenSSL** (for password generation)
- **Git**
- **Telegram Bot Token** ([get from @BotFather](https://t.me/botfather))
- **GitHub Personal Access Token** ([generate here](https://github.com/settings/tokens))
- **OpenAI API Key** (optional, for cloud AI) OR **Ollama** (auto-loads model)

### Check Prerequisites

```bash
docker --version
docker-compose --version
openssl version
```

---

## 📦 Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot

# Run setup script
chmod +x setup.sh
./setup.sh
```

The script will guide you through:
1. ✓ Checking prerequisites
2. ✓ Generating secure password
3. ✓ Creating `.env` file
4. ✓ Collecting Telegram token
5. ✓ Collecting GitHub token
6. ✓ Starting PostgreSQL
7. ✓ Initializing database
8. ✓ Building Docker image

### Option 2: Manual Setup

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your tokens
nano .env

# Start services
docker-compose up -d
```

### Configuration Template

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

# GitHub Configuration
GITHUB_TOKEN=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN

# Database Configuration
# NOTE: The bot now strictly requires DATABASE_URL to be set.
DATABASE_URL=postgresql://user:password@postgres:5432/github_verifier
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=github_verifier

# AI Configuration (Local Ollama)
# USE_LOCAL_MODEL=true # Uncomment to enable local AI
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral

# AI Configuration (Cloud OpenAI)
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # Uncomment to enable cloud AI
# OPENAI_MODEL=gpt-3.5-turbo

# Logging
LOG_LEVEL=INFO
```
