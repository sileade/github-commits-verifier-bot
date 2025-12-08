# 🤖 GitHub Commits Verifier Bot v3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT%2D3.5-blue.svg)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-LocalLLM-green.svg)](https://ollama.ai/)

**Professional Telegram bot for verifying GitHub commits with AI-powered analysis (cloud or local), diff viewing, and code export to branches.**

> Check commits, analyze with AI (free local or cloud), view diffs, export code to branches—all from Telegram with one command setup!

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

## ✨ Key Features

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
oollama:
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
- ✅ дождётся healthcheck'ов

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
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz12345678

# GitHub Configuration  
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx

# PostgreSQL Configuration (auto-generated)
POSTGRES_DB=github_verifier
POSTGRES_USER=github_bot
POSTGRES_PASSWORD=secure_random_password
DATABASE_URL=postgresql://github_bot:password@postgres:5432/github_verifier

# AI Analysis - Cloud (Optional)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# AI Analysis - Local (Auto-loads model)
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral

# Logging
LOG_LEVEL=INFO
```

---

## 📖 Getting Tokens

### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow instructions:
   - **Bot name:** "GitHub Commits Verifier"
   - **Username:** `github_commits_verifier_bot` (must be unique)
4. Copy the token
5. Add to `.env`: `TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz12345678`

### GitHub Personal Access Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✓ `repo` - Full control of repositories
   - ✓ `read:user` - Read user profile data
4. Generate & copy token (won't show again!)
5. Add to `.env`: `GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx`

### OpenAI API Key (Optional)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key
4. Add to `.env`: `OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 💻 Usage

### Bot Commands

```
/start              Open main menu
/help               Show help information
/stats              Display verification statistics
```

### Main Menu

```
🔍 Check Commit     → Analyze commit legitimacy + AI insights
✅ Approve Commit   → Mark as verified
❌ Reject Commit    → Mark as suspicious
📊 History         → View recent verifications
📈 Statistics      → See approval/rejection stats
⚙️ Settings        → Configure preferences
```

### Example Workflow

1. **Open Telegram** and find your bot
2. **Send `/start`** to see main menu
3. **Select "🔍 Check Commit"**
4. **Enter repository:** `owner/repo` or full GitHub URL
5. **Enter commit SHA:** `a1b2c3d4e5f6g7h8` or shortened `a1b2c3d4`
6. **View commit details:**
   - Author, date, message
   - Files changed with +/- counts
   - **🤖 AI Analysis** (if enabled):
     - Summary of changes
     - Impact assessment
     - Code strengths
     - Potential concerns
     - Review recommendation
   - GPG signature status
   - Verification results
   - GitHub link
7. **Action buttons:**
   - `✅ Approve` - Mark as verified
   - `❌ Reject` - Mark as suspicious
   - `📄 Show diff` - View code changes
   - `📤 Export code` - Export to branch

---

## 🐳 Docker Management

### Service Status

```bash
# View all services
docker-compose ps

# Expected output:
# NAME                              STATUS
# github-commits-postgres  (healthy)
# ollama                   (healthy)
# github-commits-verifier-bot       (healthy)
```

### View Logs

```bash
# Bot logs (real-time)
docker-compose logs -f github-commits-bot

# Ollama logs (model downloading)
docker-compose logs -f ollama

# Database logs
docker-compose logs -f postgres

# Both services
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50 github-commits-bot

# Filter by pattern
docker-compose logs github-commits-bot | grep error
```

### Service Control

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Full restart (rebuild)
docker-compose up -d --build

# Remove containers and volumes
docker-compose down -v
```

### Resource Monitoring

```bash
# View container statistics
docker stats

# Check database size
docker exec postgres psql -U github_bot -d github_verifier \
  -c "SELECT pg_size_pretty(pg_database_size('github_verifier'));"

# Check downloaded models in Ollama
docker exec ollama ollama list
```

---

## 💾 Database

### PostgreSQL Configuration

```
Host:       postgres (or localhost:5432)
Database:   github_verifier
User:       github_bot
Password:   [generated by setup.sh]
```

### Schema

**Users Table:**
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Verifications Table:**
```sql
CREATE TABLE verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    repo TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('approved', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_verifications_user_id ON verifications(user_id);
CREATE INDEX idx_verifications_commit_sha ON verifications(commit_sha);
CREATE INDEX idx_verifications_created_at ON verifications(created_at DESC);
```

### Database Operations

```bash
# Connect to database
docker exec -it postgres psql -U github_bot -d github_verifier

# List tables
\dt

# Show table structure
\d verifications

# Query examples
SELECT COUNT(*) FROM verifications;
SELECT status, COUNT(*) FROM verifications GROUP BY status;
SELECT * FROM verifications WHERE user_id = 123456789 ORDER BY created_at DESC LIMIT 10;

# Backup database
docker exec postgres pg_dump -U github_bot github_verifier > backup.sql

# Restore from backup
docker exec -i postgres psql -U github_bot github_verifier < backup.sql
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | Yes | - |
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for cloud AI analysis | No | - |
| `USE_LOCAL_MODEL` | Enable local LLM (Ollama) | No | false |
| `OLLAMA_HOST` | Ollama server URL | No | http://localhost:11434 |
| `LOCAL_MODEL` | Local model name (mistral, llama2, etc) | No | mistral |
| `DATABASE_URL` | PostgreSQL connection string | Auto | postgresql://github_bot:password@postgres:5432/github_verifier |
| `POSTGRES_DB` | Database name | Auto | github_verifier |
| `POSTGRES_USER` | Database user | Auto | github_bot |
| `POSTGRES_PASSWORD` | Database password | Auto | [generated] |
| `LOG_LEVEL` | Logging level (INFO/DEBUG) | No | INFO |

### Volume Mounts

```yaml
Volumes:
  - postgres_data:/var/lib/postgresql/data  # Database persistence
  - ollama_data:/root/.ollama               # Model cache (auto-loaded)
  - ./logs:/app/logs                        # Application logs
  - ./.env:/app/.env:ro                    # Configuration (read-only)
```

### Resource Limits

```yaml
Resources:
  PostgreSQL:
    CPU limit: 1 core
    Memory limit: 512 MB
  Ollama:
    CPU limit: 2 cores
    Memory limit: 8 GB
  Bot:
    CPU limit: 1 core
    Memory limit: 512 MB
```

---

## 📝 Project Structure

```
github-commits-verifier-bot/
├── 📄 bot.py                    # Main bot application (450+ lines)
├── 📄 github_service.py         # GitHub API integration (300+ lines)
├── 📄 database.py               # PostgreSQL management (250+ lines)
├── 📄 ai_analyzer.py            # OpenAI analysis (300+ lines)
├── 📄 local_analyzer.py         # Local LLM analysis (300+ lines)
├── 📄 hybrid_ai_manager.py      # AI manager (200+ lines)
├── 📄 bot_ai_integration.py     # AI integration helpers (200+ lines)
├── 📄 requirements.txt          # Python dependencies
├── 🐳 Dockerfile                # Container definition
├── 🐳 docker-compose.yml        # Services orchestration (with auto model loading)
├── 📋 .env.example              # Configuration template
├── 📋 .env                      # Auto-generated configuration
├── 📋 README.md                 # This file
├── 📋 FEATURES_v3.md            # Detailed feature documentation
├── 📋 ai_analyzer_integration.md # OpenAI integration guide
├── 📋 local_analyzer_integration.md # Local LLM integration guide
├── 📋 LOCAL_LLM_SETUP.md        # Complete Local LLM setup guide
├── 📋 OLLAMA_MODELS.md          # Available models reference
├── 📋 LICENSE                   # MIT License
├── 🚀 setup.sh                  # Automated setup script
├── 🚀 start.sh                  # Start script (with auto model loading)
├── 🚀 stop.sh                   # Stop script
├── 🚀 restart.sh                # Restart script
├── 📂 logs/
│   └── bot.log                  # Application logs
└── .gitignore

🐳 Docker Services:
├── github-commits-postgres      # PostgreSQL 16 database
├── ollama                       # Ollama with auto model loading
└── github-commits-verifier-bot  # Main bot container

💾 Docker Volumes:
├── postgres_data                # Database persistence
└── ollama_data                  # Model cache (auto-loaded on startup)
```

---

## 🔧 Troubleshooting

### Setup Issues

| Issue | Solution |
|-------|----------|
| "Docker not found" | Install Docker: https://docs.docker.com/install |
| "Permission denied" on setup.sh | Run: `chmod +x setup.sh` |
| "PostgreSQL timeout" | Ensure Docker daemon is running, wait longer |
| .env already exists | Choose to reconfigure in setup.sh prompt |
| "version obsolete" warning | Ignore, it's a Docker Compose v2 info message |

### Bot Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Verify TELEGRAM_BOT_TOKEN in .env |
| "Connection refused" | Check: `docker-compose ps` |
| "GitHub API error" | Verify GITHUB_TOKEN has correct scopes |
| Database errors | Check logs: `docker-compose logs postgres` |
| "Ollama not available" | Check if Ollama container is running and healthy |
| "Model not found" | Wait for auto-download or manual: `docker exec ollama ollama pull mistral` |
| Ollama unhealthy | Check logs: `docker logs ollama`, wait for model to finish loading |

### AI Analysis Issues

| Issue | Solution |
|-------|----------|
| "No AI analysis shown" | Set OPENAI_API_KEY or USE_LOCAL_MODEL=true |
| "OPENAI_API_KEY not found" | Add API key to .env or disable AI |
| "Local LLM timeout" | Increase timeout in .env or use smaller model |
| "Out of memory" | Use smaller model (openchat) or add more RAM |
| "Model downloading forever" | Check internet connection, disk space |
| Ollama model auto-load failed | Check docker logs: `docker logs -f ollama` |

### Health Checks

```bash
# View container health
docker-compose ps

# Check PostgreSQL connectivity
docker exec postgres pg_isready -U github_bot

# Check Ollama (if using local LLM)
curl http://localhost:11434/api/tags

# Test bot connectivity
docker exec github-commits-bot python -c "print('Bot OK')"

# View system logs
docker-compose logs --tail=100 github-commits-bot

# Test Ollama model loading
docker exec ollama ollama list
```

---

## 🔄 Updates & Maintenance

### Update Bot Code

```bash
# Pull latest changes
git pull origin main

# Rebuild image (includes new dependencies)
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Database Backup

```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U github_bot github_verifier > backup-$(date +%Y%m%d).sql

# Compress backup
tar -czf backup-$(date +%Y%m%d).tar.gz backup-*.sql

# Restore from backup
docker exec -i postgres psql -U github_bot github_verifier < backup.sql
```

### Model Management

```bash
# Check current models
docker exec ollama ollama list

# Update/re-download model
docker exec ollama ollama pull mistral

# Switch to different model
# Edit .env: LOCAL_MODEL=llama2
# Restart: docker-compose restart
```

### Cleanup

```bash
# Remove unused Docker images
docker image prune -a

# Remove dangling volumes
docker volume prune

# Full cleanup (WARNING: removes all data!)
docker-compose down -v
rm -rf logs/ data/ .env
```

---

## 📚 Documentation

- **[FEATURES_v3.md](FEATURES_v3.md)** - Detailed feature documentation
- **[ai_analyzer_integration.md](ai_analyzer_integration.md)** - Cloud AI (OpenAI) integration guide
- **[local_analyzer_integration.md](local_analyzer_integration.md)** - Local AI (Ollama) integration guide
- **[LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md)** - Complete local LLM setup guide
- **[OLLAMA_MODELS.md](OLLAMA_MODELS.md)** - Available Ollama models reference
- **[.env.example](.env.example)** - Configuration template with descriptions
- **[Dockerfile](Dockerfile)** - Container build instructions
- **[docker-compose.yml](docker-compose.yml)** - Services definition with auto-loading

---

## 📊 Performance

### Response Times

- **Commit Check:** 2-3 seconds
- **Diff Retrieval:** 1-2 seconds (varies by size)
- **AI Analysis (Local, CPU):** 5-30 seconds
- **AI Analysis (Local, GPU):** <5 seconds ⚡
- **AI Analysis (Cloud):** 3-5 seconds
- **Export to Branch:** 3-5 seconds
- **Database Query:** <100ms

### Resource Usage

- **Bot Container:** ~150-200 MB RAM
- **PostgreSQL Container:** ~50-100 MB RAM
- **Local LLM (7B model):** ~4GB RAM (CPU) or ~2GB VRAM (GPU)
- **Database Size:** ~1 MB per 1000 verifications
- **Model Cache:** ~4.4 GB (Mistral)

---

## 💰 Cost Comparison

| Method | Setup | Cost/Analysis | Cost/1000 |
|--------|-------|--|--|
| **Local Ollama (CPU)** | 10 min | $0 | $0 |
| **Local Ollama (GPU)** | 10 min | $0 | $0 |
| **OpenAI GPT-3.5** | 2 min | $0.0005 | $0.50 |
| **OpenAI GPT-4** | 2 min | $0.03 | $30 |

**💡 Local Ollama pays for itself after ~1000 commits!** 🎉

---

## 🤝 Contributing

### Bug Reports

[Open an issue](https://github.com/sileade/github-commits-verifier-bot/issues) with:
- Error message and logs
- Steps to reproduce
- Your environment (OS, Docker version)
- Bot version

### Feature Requests

[Start a discussion](https://github.com/sileade/github-commits-verifier-bot/discussions) with:
- Feature description
- Use case
- Expected behavior

### Pull Requests

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

```
Copyright (c) 2024 sileade

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot Library
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub Python Library
- [asyncpg](https://github.com/MagicStack/asyncpg) - PostgreSQL Python Driver
- [OpenAI](https://openai.com/) - Cloud AI Analysis
- [Ollama](https://ollama.ai/) - Local LLM Support with auto-loading
- [Docker](https://www.docker.com/) - Containerization

---

## 📞 Support

- 🐛 **Bug Report:** [Open Issue](https://github.com/sileade/github-commits-verifier-bot/issues/new)
- 💡 **Feature Request:** [Start Discussion](https://github.com/sileade/github-commits-verifier-bot/discussions/new)
- 🤝 **Contribute:** [Create Pull Request](https://github.com/sileade/github-commits-verifier-bot/pulls/new)
- 📧 **Contact:** [@sileade](https://github.com/sileade)

---

**Made with ❤️ for DevOps engineers by [@sileade](https://github.com/sileade)**

⭐ If this project helps you, please consider giving it a star!
