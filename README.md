# 🤖 GitHub Commits Verifier Bot v3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

**Professional Telegram bot for verifying GitHub commits with advanced features like diff viewing, code export, and PostgreSQL persistence.**

> Check commits, view diffs, export code to branches—all from Telegram with one command setup!

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
./quick-start.sh
# or
docker-compose up -d
```

---

## ✨ Key Features

### 🔍 Commit Verification
- Detailed commit information with author, date, message
- GPG signature verification
- Automatic legitimacy checks
- Clickable GitHub links

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

---

## 🛠️ Prerequisites

- **Docker & Docker Compose** v3.8+
- **OpenSSL** (for password generation)
- **Git**
- **Telegram Bot Token** ([get from @BotFather](https://t.me/botfather))
- **GitHub Personal Access Token** ([generate here](https://github.com/settings/tokens))

### Check Prerequisites

```bash
docker --version
docker-compose --version
openssl version
```

---

## 🚀 Installation

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
🔍 Check Commit     → Analyze commit legitimacy
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
# github-commits-verifier-bot       (healthy)
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

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | Yes |
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |
| `POSTGRES_DB` | Database name | Auto-generated |
| `POSTGRES_USER` | Database user | Auto-generated |
| `POSTGRES_PASSWORD` | Database password | Auto-generated |
| `LOG_LEVEL` | Logging level (INFO/DEBUG) | No (default: INFO) |

### Volume Mounts

```yaml
Volumes:
  - postgres_data:/var/lib/postgresql/data  # Database persistence
  - ./logs:/app/logs                         # Application logs
  - ./.env:/app/.env:ro                     # Configuration (read-only)
```

### Resource Limits

```yaml
Resources:
  PostgreSQL:
    CPU limit: 1 core
    Memory limit: 512 MB
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
├── 📄 requirements.txt          # Python dependencies
├── 🐳 Dockerfile                # Container definition
├── 🐳 docker-compose.yml        # Services orchestration
├── 📝 .env.example              # Configuration template
├── 📝 .env                      # Auto-generated configuration
├── 📝 README.md                 # This file
├── 📝 FEATURES_v3.md            # Detailed feature documentation
├── 📝 LICENSE                   # MIT License
├── 🚀 setup.sh                  # Automated setup script
├── 🚀 quick-start.sh            # Quick start script
├── 📁 logs/
│   └── bot.log                  # Application logs
└── .gitignore

📦 Docker Services:
├── github-commits-postgres      # PostgreSQL 16 database
└── github-commits-verifier-bot  # Main bot container

💾 Docker Volumes:
└── postgres_data                # Database persistence
```

---

## 🐛 Troubleshooting

### Setup Issues

| Issue | Solution |
|-------|----------|
| "Docker not found" | Install Docker: https://docs.docker.com/install |
| "Permission denied" on setup.sh | Run: `chmod +x setup.sh` |
| "PostgreSQL timeout" | Ensure Docker daemon is running, wait longer |
| .env already exists | Choose to reconfigure in setup.sh prompt |

### Bot Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Verify TELEGRAM_BOT_TOKEN in .env |
| "Connection refused" | Check: `docker-compose ps` |
| "GitHub API error" | Verify GITHUB_TOKEN has correct scopes |
| Database errors | Check logs: `docker-compose logs postgres` |

### Health Checks

```bash
# View container health
docker-compose ps

# Check PostgreSQL connectivity
docker exec postgres pg_isready -U github_bot

# Test bot connectivity
docker exec github-commits-bot python -c "print('Bot OK')"

# View system logs
docker-compose logs --tail=100 github-commits-bot
```

---

## 🔄 Updates & Maintenance

### Update Bot Code

```bash
# Pull latest changes
git pull origin main

# Rebuild image
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
- **[.env.example](.env.example)** - Configuration template with descriptions
- **[Dockerfile](Dockerfile)** - Container build instructions
- **[docker-compose.yml](docker-compose.yml)** - Services definition

---

## 🚀 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram User                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Telegram API
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         GitHub Commits Verifier Bot (python-telegram-bot)    │
│                                                               │
│  • Conversation management (ConversationHandler)             │
│  • Command processing (CommandHandler)                       │
│  • Inline keyboards and callbacks                            │
│  • State machine (REPO_INPUT, COMMIT_INPUT, etc)            │
└───────────┬──────────────────────────┬──────────────────────┘
            │                          │
            ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────┐
│  GitHub Service       │    │  Database (PostgreSQL)  │
│                       │    │                         │
│ • get_repository()    │    │ • Users table           │
│ • get_commit_info()   │    │ • Verifications table   │
│ • get_commit_files()  │    │ • Indexes               │
│ • get_commit_diff()   │    │ • Audit trail           │
│ • get_branches()      │    └─────────────────────────┘
│ • cherry_pick()       │
│ • verify_commit()     │
└──────────┬────────────┘
           │
           ▼
   GitHub REST API
   (api.github.com)
```

---

## 📊 Performance

### Response Times

- **Commit Check:** 2-3 seconds
- **Diff Retrieval:** 1-2 seconds (varies by size)
- **Export to Branch:** 3-5 seconds
- **Database Query:** <100ms

### Resource Usage

- **Bot Container:** ~150-200 MB RAM
- **PostgreSQL Container:** ~50-100 MB RAM
- **Database Size:** ~1 MB per 1000 verifications

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
