# 🤖 GitHub Commits Verifier Bot

Professional Telegram bot for verifying and confirming the legitimacy of GitHub commits. Analyze commits, approve/reject them, export changes to branches, and view diffs—all through an intuitive Telegram interface with PostgreSQL backend and comprehensive history tracking.

**v3.0 Release: PostgreSQL, Diff Viewing, Code Export** 🚀

**One-Command Setup with ./setup.sh!**

---

## ✨ Key Features

🔍 **Commit Verification** - Get detailed commit information with automatic legitimacy checks

✅ **Approval System** - Mark commits as verified and legitimate

❌ **Rejection Tracking** - Flag suspicious commits for review

📄 **Diff Viewing** - See complete code changes with syntax-aware formatting

📈 **Code Export** - Cherry-pick commits to existing or new branches

📊 **Verification History** - Browse all your commit reviews with full history

📈 **Statistics Dashboard** - Track approval/rejection metrics with visual charts

📁 **File Change Logs** - See which files changed with detailed +/- statistics

🔐 **PostgreSQL Persistence** - Enterprise-grade database backend

🔗 **GitHub Integration** - Full GitHub API support for commits, branches, and code

🎨 **Beautiful UI** - Box-framed menus, visual indicators, emoji-rich interface

⚡ **Auto-Setup** - Single command to configure everything

🐳 **Production-Ready** - Docker Compose, health checks, security hardening

---

## 🚀 Quick Start (1 Command!)

### Prerequisites

- **Docker & Docker Compose** (v3.8+)
- **OpenSSL** (for secure password generation)
- **Git**
- **Telegram Bot Token** (from [@BotFather](https://t.me/botfather))
- **GitHub Personal Access Token** (from GitHub Settings)

### One-Command Setup

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot
chmod +x setup.sh
./setup.sh
```

**That's it!** The script will:

✅ Generate secure PostgreSQL password  
✅ Create `.env` file with configuration  
✅ Prompt for Telegram Bot Token  
✅ Prompt for GitHub Personal Access Token  
✅ Start PostgreSQL container  
✅ Initialize database with tables & indexes  
✅ Build Docker image for bot  
✅ Provide next steps  

---

## 📋 Setup Script Walkthrough

### Step 1: Run Setup

```bash
./setup.sh
```

The script checks for Docker, Docker Compose, and OpenSSL:

```
✓ Docker installed
✓ Docker Compose installed
✓ OpenSSL installed
```

### Step 2: Generate Configuration

If `.env` doesn't exist, the script generates it with:
- Secure random PostgreSQL password
- Default database settings
- Template for your tokens

### Step 3: Telegram Bot Token

Follow the prompts:
```
How to get Telegram Bot Token:
1. Open Telegram and find @BotFather
2. Send /newbot
3. Follow instructions
4. Copy the token

Enter your Telegram Bot Token (or press Enter to skip): 123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567
✓ Telegram Bot Token saved
```

### Step 4: GitHub Token

Follow the prompts:
```
How to get GitHub Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click 'Generate new token (classic)'
3. Select scopes: repo, read:user
4. Copy the token

Enter your GitHub Personal Access Token (or press Enter to skip): ghp_xxxxxxxxxxxxxxxxxxxxx
✓ GitHub Token saved
```

### Step 5: Automatic Setup

Script automatically:
```
=== Starting PostgreSQL ===
✓ PostgreSQL container started
⏳ Waiting for initialization (max 60 seconds)...
✓ PostgreSQL ready

=== Initializing Database ===
✓ Database initialized

=== Building Docker Image ===
✓ Docker image built successfully
```

### Step 6: Next Steps

```
=== Setup Complete ===

✓ Configuration created
✓ PostgreSQL started
✓ Database initialized
✓ Docker image built

Next steps:
  1. Start the bot: docker-compose up -d github-commits-bot
  2. Check status: docker-compose ps
  3. View logs: docker-compose logs -f github-commits-bot
```

---

## 🚀 Quick Start After Setup

After running `./setup.sh`, use the quick start script:

```bash
chmod +x quick-start.sh
./quick-start.sh
```

This will:
- ✅ Start PostgreSQL
- ✅ Start the bot
- ✅ Show service status
- ✅ Provide useful commands

---

## 📁 What Gets Created

After setup, your project structure looks like:

```
github-commits-verifier-bot/
├── 📄 .env                  ← Configuration (auto-generated)
├── 🐳 docker-compose.yml    ← Services definition
├── 🐳 Dockerfile            ← Bot container
├── 📄 bot.py                ← Main bot logic
├── 📄 github_service.py     ← GitHub API integration
├── 📄 database.py           ← PostgreSQL management
├── 📄 requirements.txt       ← Python dependencies
├── 📁 logs/                 ← Application logs
│   └── bot.log
└── .env.example             ← Configuration template

🐳 Docker Containers:
├── github-commits-postgres  ← PostgreSQL database
└── github-commits-verifier-bot  ← Main bot

💾 Docker Volumes:
└── postgres_data            ← Database persistence
```

---

## 🔧 Manual Configuration (Optional)

If you want to configure manually:

```bash
# Copy template
cp .env.example .env

# Edit .env with your tokens
nano .env

# Start services
docker-compose up -d
```

---

## 🐳 Docker Commands

### View Service Status

```bash
# Check all running services
docker-compose ps

# Shows:
# NAME                    STATUS
# github-commits-postgres (healthy)
# github-commits-bot      (healthy)
```

### View Logs

```bash
# Bot logs (real-time)
docker-compose logs -f github-commits-bot

# Database logs
docker-compose logs -f postgres

# Both services
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50 github-commits-bot
```

### Stop Services

```bash
# Graceful stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Services

```bash
docker-compose restart github-commits-bot
```

---

## 🔑 Obtaining Tokens

### Telegram Bot Token

1. **Open Telegram** and search for [@BotFather](https://t.me/botfather)
2. **Send `/newbot`**
3. **Choose bot name:** "GitHub Commits Verifier"
4. **Choose username:** `github_commits_verifier_bot` (must be unique)
5. **Receive token:** Looks like `123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz12345678`
6. **Add to .env:** `TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz12345678`

### GitHub Personal Access Token

1. **Go to:** https://github.com/settings/tokens
2. **Click:** "Generate new token (classic)"
3. **Select scopes:**
   - ☑ `repo` - Full control of repositories
   - ☑ `read:user` - Read user data
4. **Generate & copy:** Token immediately (won't show again)
5. **Add to .env:** `GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx`

---

## 📱 Using the Bot

### Bot Commands

```
/start              Open main menu
/help               Show help information
/stats              Display verification statistics
```

### Main Menu Options

```
🔍 Check Commit       → Analyze commit legitimacy
✅ Approve Commit     → Mark as verified
❌ Reject Commit      → Mark as suspicious
📊 History           → View recent verifications
📈 Statistics        → See approval/rejection stats
⚙️ Settings          → Configure preferences
```

### Example Workflow

1. Open Telegram, find your bot
2. Send `/start`
3. Select "🔍 Check Commit"
4. Enter repository: `sileade/github-commits-verifier-bot`
5. Enter commit SHA: `a1b2c3d4e5f6g7h8`
6. See commit info, files changed, verification results
7. Click "📄 Show diff" to view code changes
8. Click "✅ Approve" to mark as verified
9. Click "📈 Export code" to cherry-pick to another branch

---

## 🔄 Database Configuration

### PostgreSQL Details

```env
# Auto-generated by setup.sh
POSTGRES_DB=github_verifier
POSTGRES_USER=github_bot
POSTGRES_PASSWORD=<secure_random_password>
DATABASE_URL=postgresql://github_bot:password@postgres:5432/github_verifier
```

### Tables Created

**Users Table:**
```sql
user_id BIGINT PRIMARY KEY
username TEXT
created_at TIMESTAMP
```

**Verifications Table:**
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT (foreign key)
repo TEXT
commit_sha TEXT
status TEXT (approved/rejected)
created_at TIMESTAMP
```

### Database Queries

```bash
# Connect to database
docker exec -it postgres psql -U github_bot -d github_verifier

# Count verifications
SELECT COUNT(*) FROM verifications;

# View user statistics
SELECT user_id, COUNT(*) as total FROM verifications GROUP BY user_id;

# View approvals vs rejections
SELECT status, COUNT(*) FROM verifications GROUP BY status;
```

---

## 🆘 Troubleshooting

### Setup Script Issues

| Issue | Solution |
|-------|----------|
| "Docker not found" | Install Docker: https://docs.docker.com/install |
| "Permission denied" | Run `chmod +x setup.sh` |
| "PostgreSQL timeout" | Check Docker is running, wait 60s |
| ".env already exists" | Choose to reconfigure or keep existing |

### Bot Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Check TELEGRAM_BOT_TOKEN in .env |
| "Connection refused" | Ensure postgres container is healthy: `docker-compose ps` |
| Database errors | Check PostgreSQL logs: `docker-compose logs postgres` |

### Check Service Health

```bash
# View container status
docker-compose ps

# Check PostgreSQL
docker exec postgres pg_isready -U github_bot

# Check bot logs for errors
docker-compose logs github-commits-bot | grep -i error
```

---

## 📚 Features in Detail

### Diff Viewing

- Click "📄 Show diff" on any commit
- Small diffs (<4KB): Displayed in chat
- Large diffs: Downloaded as `.patch` file
- Full patch format for patching other branches

### Code Export

- **Export to existing branch:** Select from list, auto cherry-pick
- **Create new branch:** Enter name, bot creates and cherry-picks
- **Get GitHub link:** Click to view in browser

### File Change Logs

- Shows first 5 files inline
- Displays status: 🆕 added, ✏️ modified, ❌ removed
- Shows +additions/-deletions for each file
- Summary if more files exist

---

## 🔄 Update & Maintenance

### Update Bot Code

```bash
# Pull latest changes
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart
docker-compose up -d
```

### Backup Database

```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U github_bot github_verifier > backup.sql

# Restore from backup
docker exec -i postgres psql -U github_bot github_verifier < backup.sql
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove dangling volumes
docker volume prune

# Full cleanup (WARNING: removes all data)
docker-compose down -v
rm -rf data/ logs/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🤝 Support

- 🐛 Found a bug? [Open an issue](https://github.com/sileade/github-commits-verifier-bot/issues)
- 💡 Have a suggestion? [Start a discussion](https://github.com/sileade/github-commits-verifier-bot/discussions)
- 🎉 Want to contribute? [Submit a PR](https://github.com/sileade/github-commits-verifier-bot/pulls)

---

**Made with ❤️ for DevOps engineers**
