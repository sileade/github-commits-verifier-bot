# 🤖 GitHub Commits Verifier Bot

Professional Telegram bot for verifying and confirming the legitimacy of GitHub commits. Allows you to analyze commits, approve or reject them through a convenient Telegram interface with persistent storage and comprehensive history tracking.

**Deploy with Docker Compose in seconds!**

---

## ✨ Key Features

🔍 **Commit Verification** - Get detailed commit information with automatic legitimacy checks

✅ **Approval System** - Mark commits as verified and legitimate

❌ **Rejection Tracking** - Flag suspicious commits for review

📊 **Verification History** - Browse all your commit reviews with full history

📈 **Statistics Dashboard** - Track approval/rejection metrics

🔐 **Persistent Storage** - All data saved in SQLite with Docker volumes

🐳 **Docker-Ready** - Production-optimized Docker Compose setup

---

## 🔍 Automatic Legitimacy Checks

When you verify a commit, the bot automatically evaluates:

✓ **GPG Signature** - Cryptographic signature verification from GitHub
✓ **Known Author** - Author verification and tracking
✓ **Commit Message** - Validation of commit message presence
✓ **Valid Date** - Timestamp correctness verification

---

## 📋 Prerequisites

- **Docker & Docker Compose** (v3.8+)
- **Telegram Bot Token** (get from [@BotFather](https://t.me/botfather))
- **GitHub Personal Access Token** (PAT with `repo` access)
- **Unix-like environment** (Linux, macOS, WSL2 on Windows)

---

## 🚀 Quick Start (30 seconds)

### Step 1: Clone Repository

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your tokens:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# GitHub Configuration  
GITHUB_TOKEN=your_github_personal_access_token_here

# Logging
LOG_LEVEL=INFO
```

### Step 3: Start Services

```bash
docker-compose up -d
```

### Step 4: Verify Running

```bash
docker-compose logs -f github-commits-bot
```

You should see:
```
Starting bot...
```

Now open Telegram and send `/start` to your bot! 🎉

---

## 🐳 Docker Compose Configuration

Our Docker Compose setup includes:

### Service Configuration
```yaml
- Auto-restart on failure
- Health checks every 30s
- Resource limits (1 CPU, 512MB RAM)
- Security: Non-root user (UID 1000)
- Logging: JSON with rotation (max 10MB per file)
```

### Volume Mounts
```
./data          → /app/data          (SQLite database)
./logs          → /app/logs          (Application logs)
./.env          → /app/.env (ro)     (Configuration)
```

### Network
```
Bridge network: bot_network
Subnet: 172.28.0.0/16
```

---

## 📱 Usage Guide

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Open main menu with all options |
| `/help` | Show help information and commands |
| `/check_repo` | Verify a specific repository |
| `/stats` | Display your verification statistics |

### Interactive Menu Flow

**Main Menu Options:**
```
🔍 Check Commit       → Analyze commit legitimacy
✅ Approve Commit     → Mark as verified
❌ Reject Commit      → Mark as suspicious
📊 History           → View recent verifications
⚙️ Settings          → Configure preferences
```

### Step-by-Step Example

**Verify a GitHub Commit:**

1. Send `/start` to bot
2. Select "🔍 Check Commit"
3. Enter repository: `owner/repo` or full GitHub URL
4. Enter commit SHA (e.g., `a1b2c3d4e5f6g7h8...`)
5. Bot displays:
   - Commit author & date
   - Commit message
   - Verification results
   - Action buttons (Approve/Reject)

**Approve a Commit:**

1. Send `/start`
2. Select "✅ Approve Commit"
3. Enter commit SHA
4. Commit saved to database as verified ✓

**View Your History:**

1. Send `/start`
2. Select "📊 History"
3. See last 10 verifications with dates & statuses

**Check Statistics:**

1. Send `/stats`
2. View totals:
   - ✅ Approved commits
   - ❌ Rejected commits
   - 📈 Total verified

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────┐
│   Telegram Bot API              │
│  (telegram.org)                 │
└────────────┬────────────────────┘
             │
             │ python-telegram-bot
             │ (v20.7)
             │
             ▼
┌─────────────────────────────────┐
│   Bot Engine (bot.py)           │
│  • Conversation management      │
│  • Command handlers             │
│  • User interactions            │
└────────────┬──────────┬─────────┘
             │          │
             │          │ SQLite
             │          ▼
             │  ┌──────────────────┐
             │  │  SQLite DB       │
             │  │ /app/data/       │
             │  │ verifications.db │
             │  │                  │
             │  │ • Users table    │
             │  │ • Verifications  │
             │  └──────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  GitHub Service (github_service)│
│  • Repository info              │
│  • Commit details               │
│  • Signature verification       │
└────────────┬────────────────────┘
             │
             │ REST API
             ▼
┌─────────────────────────────────┐
│   GitHub API                    │
│  api.github.com                 │
└─────────────────────────────────┘
```

### Data Flow

```
User (Telegram)  →  Bot  →  GitHub Service  →  GitHub API
    ↓                                              ↓
    └──────→  Database (SQLite)  ←───────────────┘
```

---

## 📁 Project Structure

```
github-commits-verifier-bot/
├── 📄 bot.py                      (Main application - 400+ lines)
├── 📄 github_service.py            (GitHub API integration - 250+ lines)
├── 📄 database.py                  (SQLite management - 200+ lines)
├── 📄 requirements.txt             (Python dependencies)
├── 🐳 Dockerfile                  (Multi-stage build, optimized)
├── 🐳 docker-compose.yml          (Production-ready config)
├── 📝 .env.example                (Configuration template)
├── 📝 README.md                   (This file)
├── 📝 LICENSE                     (MIT License)
└── .gitignore                     (Git exclusions)

📁 Runtime Directories (created on first run):
├── 📁 data/
│   └── verifications.db           (SQLite database)
└── 📁 logs/
    └── bot.log                    (Application logs)
```

---

## ⚙️ Container Management

### View Running Containers

```bash
docker-compose ps
```

Expected output:
```
NAME                              STATUS
github-commits-verifier-bot       Up (healthy)
```

### Check Logs in Real-time

```bash
# Follow logs (live)
docker-compose logs -f github-commits-bot

# Last 100 lines
docker-compose logs --tail=100 github-commits-bot

# Last 30 minutes of logs
docker-compose logs --since=30m github-commits-bot
```

### Restart Service

```bash
# Graceful restart (waits 30s)
docker-compose restart github-commits-bot

# Force restart
docker-compose kill github-commits-bot
docker-compose up -d
```

### Stop Service

```bash
# Stop container (can be restarted)
docker-compose stop

# Remove containers (cleans up)
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### Rebuild Image

```bash
# Rebuild without cache (recommended after code changes)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

### Execute Commands in Container

```bash
# Run Python command
docker exec github-commits-bot python -c "print('Test')"

# Interactive shell
docker exec -it github-commits-bot /bin/bash

# Query database
docker exec github-commits-bot sqlite3 /app/data/verifications.db "SELECT COUNT(*) FROM verifications;"
```

### Database Management

```bash
# Backup database
docker exec github-commits-bot cp /app/data/verifications.db /app/data/verifications.db.backup

# Check database
docker exec github-commits-bot sqlite3 /app/data/verifications.db ".tables"

# Export data
docker exec github-commits-bot sqlite3 /app/data/verifications.db "SELECT * FROM verifications;" > verifications.csv
```

---

## 🔑 Obtaining Required Tokens

### GitHub Personal Access Token (PAT)

**Step 1:** Go to GitHub Settings
- Log in to GitHub
- Click profile icon → Settings
- Left sidebar → Developer settings
- Personal access tokens → Tokens (classic)

**Step 2:** Create New Token
- Click "Generate new token (classic)"
- Name: `github-commits-bot` (or your preferred name)
- Expiration: 90 days or No expiration

**Step 3:** Select Scopes
```
☑ repo              Full control of private repositories
  ☑ repo:status     Access commit status
  ☑ repo:invite     Access repository invitations
☑ read:user         Read user profile data
```

**Step 4:** Generate & Copy
- Click "Generate token"
- **IMPORTANT:** Copy token immediately (won't show again)
- Paste into `.env` as `GITHUB_TOKEN=`

### Telegram Bot Token

**Step 1:** Find BotFather
- Open Telegram
- Search for [@BotFather](https://t.me/botfather)
- Start chat

**Step 2:** Create Bot
- Send `/newbot`
- Follow instructions:
  - Bot name: "GitHub Commits Verifier" (display name)
  - Username: `github_commits_verifier_bot` (must be unique)

**Step 3:** Receive Token
- BotFather sends HTTP API token
- Looks like: `123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz12345678`
- Paste into `.env` as `TELEGRAM_BOT_TOKEN=`

**Step 4:** (Optional) Configure Bot Commands
- Send `/setcommands` to BotFather
- Copy-paste these commands:
```
start - Open main menu
help - Show help information
check_repo - Check repository
stats - Show statistics
```

---

## 🐳 Docker Compose Production Features

### Health Checks

Container automatically checks database accessibility:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import sqlite3; ..."]
  interval: 30s      # Check every 30 seconds
  timeout: 10s       # Wait max 10 seconds
  retries: 3         # Fail after 3 failures
  start_period: 40s  # Initial grace period
```

Check status:
```bash
docker-compose ps  # Shows "(healthy)" or "(unhealthy)"
```

### Resource Limits

Container is limited to prevent runaway resources:
```yaml
deploy:
  resources:
    limits:
      cpus: '1'              # Max 1 CPU core
      memory: 512M           # Max 512 MB RAM
    reservations:
      cpus: '0.5'            # Reserve 0.5 cores
      memory: 256M           # Reserve 256 MB
```

### Logging Rotation

Automatic log rotation prevents disk issues:
```yaml
logging:
  options:
    max-size: "10m"         # Max 10 MB per file
    max-file: "5"           # Keep 5 files max
```

### Security

```yaml
security_opt:
  - no-new-privileges:true  # Container can't escalate privileges
user: "1000:1000"          # Run as non-root user
stop_signal: SIGTERM        # Graceful shutdown signal
stop_grace_period: 30s      # Wait 30s before force kill
```

---

## 🔧 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs github-commits-bot
```

**Common issues:**

| Issue | Solution |
|-------|----------|
| `TELEGRAM_BOT_TOKEN not found` | Edit `.env`, ensure token is set |
| `GITHUB_TOKEN not found` | Edit `.env`, add GitHub token |
| `Permission denied` | Run `chmod +x docker-compose.yml` |
| `Port already in use` | Change port in docker-compose.yml |

### Database Errors

```bash
# Check database integrity
docker exec github-commits-bot sqlite3 /app/data/verifications.db "PRAGMA integrity_check;"

# Reset database
rm data/verifications.db
docker-compose restart github-commits-bot
```

### GitHub API Errors

| Status | Meaning | Fix |
|--------|---------|-----|
| 401 Unauthorized | Bad token | Verify GitHub token is correct |
| 404 Not Found | Repo doesn't exist | Check repo path format: `owner/repo` |
| 403 Forbidden | No permission | Verify token has `repo` scope |
| 422 Unprocessable | Invalid commit SHA | Ensure SHA is valid (40 chars) |

### Telegram Errors

| Error | Solution |
|-------|----------|
| Bot not responding | Check `TELEGRAM_BOT_TOKEN` |
| Bot offline | Verify container is running: `docker-compose ps` |
| Old commands | Update bot commands via [@BotFather](https://t.me/botfather) |

### Performance Issues

```bash
# Check container stats
docker stats github-commits-bot

# View memory usage
docker-compose logs github-commits-bot | grep -i memory

# Increase resource limits in docker-compose.yml
# Then: docker-compose up -d
```

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,      -- Telegram user ID
    username TEXT NOT NULL,            -- Telegram username
    created_at TIMESTAMP DEFAULT NOW   -- Registration date
);
```

### Verifications Table
```sql
CREATE TABLE verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,          -- Foreign key to users
    repo TEXT NOT NULL,                -- Repository path
    commit_sha TEXT NOT NULL,          -- Full commit SHA
    status TEXT NOT NULL,              -- 'approved' or 'rejected'
    created_at TIMESTAMP DEFAULT NOW,  -- Verification date
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Index for fast commit lookups
CREATE INDEX idx_commit_sha ON verifications(commit_sha);
```

### Query Examples

```bash
# Get user's verification count
docker exec github-commits-bot sqlite3 /app/data/verifications.db \
  "SELECT status, COUNT(*) FROM verifications WHERE user_id = ? GROUP BY status;"

# Find all verifications for a commit
docker exec github-commits-bot sqlite3 /app/data/verifications.db \
  "SELECT * FROM verifications WHERE commit_sha LIKE 'abc123%';"

# Export all data as CSV
docker exec github-commits-bot sqlite3 /app/data/verifications.db \
  ".mode csv" \
  "SELECT * FROM verifications;" > verifications.csv
```

---

## 📚 References & Documentation

- **[python-telegram-bot Docs](https://docs.python-telegram-bot.org/)** - Telegram bot library
- **[GitHub REST API](https://docs.github.com/en/rest)** - GitHub API reference
- **[PyGithub Docs](https://pygithub.readthedocs.io/)** - Python GitHub wrapper
- **[Docker Documentation](https://docs.docker.com/)** - Docker & Compose guide
- **[SQLite Docs](https://www.sqlite.org/docs.html)** - Database documentation

---

## 🔄 Update & Maintenance

### Update Bot Code

```bash
# Pull latest changes
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart service
docker-compose up -d
```

### Backup Data

```bash
# Backup database
cp data/verifications.db data/verifications.db.backup.$(date +%Y%m%d)

# Backup entire directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/
```

### Clean Up

```bash
# Remove old logs
find logs/ -name "*.log" -mtime +30 -delete

# Remove unused images
docker image prune -a

# Remove dangling volumes
docker volume prune
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Include license in distributions
- ⚠️ No liability
- ⚠️ No warranty

---

## 🤝 Support & Contributions

### Report Issues

Found a bug? Have a feature request?

→ **[Open an Issue](https://github.com/sileade/github-commits-verifier-bot/issues)**

Include:
- Error message and logs
- Steps to reproduce
- Your environment (OS, Docker version)
- Bot version

### Contribute

Want to improve the bot?

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 👤 Author

**sileade** - [@sileade](https://github.com/sileade)

---

## 📞 Need Help?

- 📖 Check [Troubleshooting](#-troubleshooting) section
- 🔍 Search [existing issues](https://github.com/sileade/github-commits-verifier-bot/issues)
- 💬 Create new issue with details
- 📧 Contact maintainer

---

**Made with ❤️ for the DevOps community**
