# 🚀 Complete Automated Docker Setup Guide

## Overview

This guide covers the **fully automated setup** with zero manual configuration needed. Everything is built into the docker-compose and startup scripts.

### What Gets Set Up

- 💾 **PostgreSQL 16** - Database with automatic initialization
- 🤖 **Ollama** - Optional local LLM (Mistral, Llama2, etc.)
- 📄 **GitHub Commits Bot** - Main application
- 🔒 **Health Checks** - Automatic service verification
- 📁 **Logging** - Centralized container logs
- 📤 **Resource Limits** - Memory and CPU constraints
- 🔐 **Security** - Non-root user, no new privileges

---

## Quick Start (3 Commands!)

```bash
# 1. Setup configuration (Telegram + GitHub tokens)
./setup.sh

# 2. Make startup script executable
chmod +x start.sh

# 3. Start everything (fully automated!)
./start.sh
```

That's it! 🌟

---

## Detailed Setup Process

### Step 1: Initial Configuration

```bash
./setup.sh
```

**This script:**
- ✅ Checks Docker installation
- ✅ Generates secure PostgreSQL password
- ✅ Creates `.env` file
- ✅ Prompts for Telegram Bot Token
- ✅ Prompts for GitHub Personal Access Token
- ✅ Optionally prompts for OpenAI API Key
- ✅ Validates all configuration

**Output:**
```
✓ Docker installed
✓ Docker Compose installed
✓ OpenSSL installed
✓ PostgreSQL password generated
✓ .env file created
? Enter your Telegram Bot Token: [input]
✓ Telegram Bot Token saved
? Enter your GitHub Personal Access Token: [input]
✓ GitHub Token saved

===== Setup Complete! =====
Next: chmod +x start.sh && ./start.sh
```

### Step 2: Start All Services

```bash
chmod +x start.sh
./start.sh
```

**This script automatically:**

1. 🐳 **Validates Environment**
   - Checks .env file exists
   - Verifies required tokens are set
   - Detects if local LLM is enabled

2. 🐳 **Checks Docker**
   - Verifies Docker is installed
   - Confirms Docker daemon is running

3. 📂 **Builds Image**
   - Rebuilds Docker image with all dependencies
   - Uses optimized multi-stage build
   - Takes 2-5 minutes (cached after first run)

4. 🚀 **Starts Services**
   - PostgreSQL starts first
   - Ollama starts (if enabled)
   - Bot starts after dependencies are ready

5. ⏳ **Waits for Health**
   - Verifies PostgreSQL is ready
   - Checks Ollama health (if enabled)
   - Confirms bot is running

6. 🤖 **Initializes LLM** (if enabled)
   - Checks if model is loaded
   - Pulls model if needed (first run: 5-15 minutes)
   - Verifies model is ready

7. 🌟 **Shows Status & Instructions**

**Expected Output:**
```
==================================================
🤖 GitHub Commits Verifier Bot - Complete Startup
==================================================

✓ .env file found
✓ TELEGRAM_BOT_TOKEN configured
✓ GITHUB_TOKEN configured
✓ Local LLM (Ollama) enabled

==================================================
🐳 Docker Check
==================================================

✓ Docker installed
✓ Docker daemon running

==================================================
🐳 Building Docker Image
==================================================

✓ Docker image built successfully

==================================================
🚀 Starting Services
==================================================

✔ Starting PostgreSQL...
✓ PostgreSQL started
✔ Starting Ollama...
✓ Ollama started
✔ Starting GitHub Commits Bot...
✓ Bot started

==================================================
⏳ Waiting for Services
==================================================

✓ PostgreSQL is healthy
✓ Ollama is healthy
✓ Bot is running

==================================================
🤖 Initializing Local LLM Model
==================================================

✓ Model 'mistral' is already loaded

==================================================
🌟 Setup Complete!
==================================================

All services are running and healthy!
...
```

---

## Automated docker-compose Features

### Health Checks

Each service has automatic health checks:

```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U github_bot"]
  interval: 10s
  timeout: 5s
  retries: 5

# Ollama
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 10s
  timeout: 5s
  retries: 5

# Bot
healthcheck:
  test: ["CMD", "python", "-c", "print('Bot running')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Docker automatically:**
- ✅ Monitors service health
- ✅ Restarts unhealthy containers
- ✅ Manages dependencies (bot waits for postgres + ollama)

### Resource Limits

Each service has defined resource limits:

```yaml
PostgreSQL:
  CPU: 1 core (limit), 0.5 core (reservation)
  RAM: 512 MB (limit), 256 MB (reservation)

Ollama:
  CPU: 2 cores (limit), 1 core (reservation)
  RAM: 8 GB (limit), 4 GB (reservation)

Bot:
  CPU: 1 core (limit), 0.5 core (reservation)
  RAM: 512 MB (limit), 256 MB (reservation)
```

### Networking

```yaml
networks:
  bot_network:
    driver: bridge
    subnet: 172.28.0.0/16
```

**Services communicate via:**
- `postgres:5432` - Database
- `ollama:11434` - Local LLM API
- Internal network isolation

### Volumes

```yaml
volumes:
  postgres_data:      # Database persistence
  ollama_data:        # Model cache
  ./logs:/app/logs    # Application logs (local mount)
  ./.env:/app/.env:ro # Configuration (read-only)
```

---

## Useful Commands

### View Status

```bash
# See all running services
docker-compose ps

# Output:
# NAME                      STATUS
# github-commits-postgres   Up (healthy)
# ollama                    Up (healthy)
# github-commits-verifier-bot  Up (healthy)
```

### View Logs

```bash
# Bot logs (real-time)
./start.sh  # Then in another terminal:
docker-compose logs -f github-commits-bot

# Database logs
docker-compose logs -f postgres

# Ollama logs
docker-compose logs -f ollama

# All logs
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# Search logs
docker-compose logs | grep -i error
```

### Restart Services

```bash
# Graceful restart (recommended)
./restart.sh

# Or manually
docker-compose down
docker-compose up -d

# Restart specific service
docker-compose restart github-commits-bot
```

### Stop Services

```bash
# Graceful shutdown
./stop.sh

# Or manually
docker-compose down

# With volume cleanup (WARNING: removes data!)
docker-compose down -v
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it github-commits-postgres psql -U github_bot -d github_verifier

# Backup database
docker exec github-commits-postgres pg_dump -U github_bot github_verifier > backup.sql

# Check database size
docker exec -it github-commits-postgres psql -U github_bot -d github_verifier \
  -c "SELECT pg_size_pretty(pg_database_size('github_verifier'));"
```

### Ollama Management (if enabled)

```bash
# List loaded models
docker exec ollama ollama list

# Pull another model
docker exec ollama ollama pull llama2

# Run a model interactively
docker exec ollama ollama run mistral "What is 2+2?"

# View Ollama logs
docker logs -f ollama
```

### Bot Management

```bash
# Execute Python command in bot
docker exec github-commits-bot python -c "print('test')"

# Enter bot container shell
docker exec -it github-commits-bot /bin/bash

# Rebuild bot image without cache
docker-compose build --no-cache github-commits-bot
docker-compose up -d
```

---

## Configuration Options

### Enable Local LLM (Ollama)

In `.env`:

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral  # or llama2, neural-chat, dolphin-mixtral, etc.
```

On next `./start.sh`, it will:
- ✅ Start Ollama container
- ✅ Pull the specified model
- ✅ Configure bot to use local LLM

### Enable GPU Support (NVIDIA)

Uncomment in `docker-compose.yml` under `ollama` service:

```yaml
# Uncomment for GPU support (NVIDIA CUDA)
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
```

Then:
```bash
docker-compose build --no-cache
./start.sh
```

**Speed improvement:**
- CPU: 5-30 seconds per analysis
- GPU: <5 seconds per analysis (10x faster!)

### Change Model

```bash
# Update .env
LOCAL_MODEL=llama2

# Restart
./restart.sh
```

Model will be automatically pulled on next startup.

### Disable Components

**Disable local LLM:**
```env
USE_LOCAL_MODEL=false
```

**Disable Ollama container (faster startup):**
```yaml
# In docker-compose.yml, comment out ollama service
# ollama:  # DISABLED
#   image: ...
```

Then remove from bot depends_on:
```yaml
depends_on:
  postgres:
    condition: service_healthy
  # ollama:  # REMOVED
  #   condition: service_healthy
```

---

## Troubleshooting

### "Container exits immediately"

```bash
# Check logs
docker-compose logs --tail=20 github-commits-bot

# Verify .env is valid
cat .env | grep TELEGRAM_BOT_TOKEN

# Rebuild without cache
docker-compose build --no-cache
./start.sh
```

### "PostgreSQL won't start"

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify volume
docker volume ls | grep postgres

# Remove corrupted volume and restart
docker volume rm github-commits-bot_postgres_data
./start.sh
```

### "Ollama timeout"

```bash
# Check if model is downloading
docker logs -f ollama

# Increase timeout or wait longer
# First model pull takes 5-15 minutes

# Manually pull model
docker exec ollama ollama pull mistral
```

### "Bot can't connect to database"

```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# Check connection string
grep DATABASE_URL .env

# Manual test
docker exec -it github-commits-postgres psql -U github_bot -d github_verifier -c "SELECT 1"
```

### "Out of memory"

```bash
# Check memory usage
docker stats

# Reduce resource limits in docker-compose.yml
# Or use smaller model
LOCAL_MODEL=openchat  # 3.5B instead of 7B

# Or add swap
# See your OS documentation for adding swap
```

---

## Full Workflow Example

### First Time Setup

```bash
# Clone repository
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot

# Run setup (interactive)
./setup.sh
# Follow prompts:
# - Enter Telegram Bot Token
# - Enter GitHub Personal Access Token
# - (Optional) Enter OpenAI API Key
# - (Optional) Enable local LLM

# Make scripts executable
chmod +x start.sh stop.sh restart.sh

# Start everything (fully automatic!)
./start.sh
# This will:
# - Build Docker image
# - Start PostgreSQL
# - Start Ollama (if enabled)
# - Start bot
# - Wait for all services to be healthy
# - Show status and next steps
```

### Daily Usage

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f github-commits-bot

# Stop for the day
./stop.sh
```

### Restart/Update

```bash
# Restart all services
./restart.sh

# Update code
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
./start.sh
```

---

## Security Considerations

✅ **Implemented:**
- Non-root user execution (UID 1000)
- No new privileges flag
- Read-only .env mount
- Private network (bot_network)
- Health checks
- Resource limits
- Proper signal handling (SIGTERM)

⚠️ **Remember:**
- Keep `.env` file private (has tokens!)
- Use strong PostgreSQL password
- Keep tokens in `.env` only, never in code
- Regularly backup database

---

## Architecture

```
┌──────────────────────────────────────────┐
│     Docker-Compose Network (172.28.0.0/16)
├──────────────────────────────────────────┤
│                                           │
│  ┌──────────────┐  ┌──────────┐  ┌─────┐
│  │  PostgreSQL  │  │  Ollama  │  │ Bot │
│  │    :5432     │  │ :11434   │  │     │
│  └──────────────┘  └──────────┘  └─────┘
│        ▲                ▲            ▲   │
│        │                │            │   │
│        └────────────────┼────────────┘   │
│                         │                │
│                    (localhost)            │
│                   (Host machine)          │
│                                           │
└──────────────────────────────────────────┘
```

---

## File Organization

```
github-commits-verifier-bot/
├── start.sh              # ⭐ Main startup script
├── stop.sh               # Shutdown script
├── restart.sh            # Restart script
├── setup.sh              # Initial configuration
├── docker-compose.yml    # ⭐ Full stack definition
├── Dockerfile            # ⭐ Multi-stage build
├── .env                  # Configuration (auto-generated)
├── .env.example          # Template
├── bot.py                # Bot application
├── github_service.py     # GitHub integration
├── database.py           # PostgreSQL async driver
├── ai_analyzer.py        # OpenAI integration
├── local_analyzer.py     # Ollama integration
├── requirements.txt      # Python dependencies
├── README.md             # Main documentation
└── logs/                 # Application logs
    └── bot.log
```

---

## Performance Tuning

### Faster Startup

```bash
# Disable local LLM if not needed
USE_LOCAL_MODEL=false

# Or use smaller model
LOCAL_MODEL=openchat  # 3.5B (2 seconds)
```

### Better Performance

```bash
# Enable GPU
# In docker-compose.yml:
runtime: nvidia

# Use faster model
LOCAL_MODEL=mistral  # 7B (5 seconds)
```

### Production-Ready

```bash
# Use highest quality
LOCAL_MODEL=llama2:13b  # 13B (10 seconds)
# Or
OPENAI_API_KEY=sk-...   # Cloud (2-5 seconds)
```

---

## Next Steps

1. ✅ Run `./setup.sh`
2. ✅ Run `./start.sh`
3. ✅ Open Telegram, find your bot
4. ✅ Send `/start`
5. ✅ Try checking your first commit!

**Happy verifying!** 🚀
