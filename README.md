# 🤖 GitHub Commits Verifier Bot

Professional Telegram bot for verifying and confirming the legitimacy of GitHub commits. Analyze commits, approve/reject them, export changes to branches, and view diffs—all through an intuitive Telegram interface with PostgreSQL backend and comprehensive history tracking.

**v3.0 Release: PostgreSQL, Diff Viewing, Code Export** 🚀

**Deploy with Docker Compose in seconds!**

---

## ✨ Key Features

🔍 **Commit Verification** - Get detailed commit information with automatic legitimacy checks

✅ **Approval System** - Mark commits as verified and legitimate

❌ **Rejection Tracking** - Flag suspicious commits for review

📄 **Diff Viewing** - See complete code changes with syntax-aware formatting

📈 **Code Export** - Cherry-pick commits to existing or new branches

📊 **Verification History** - Browse all your commit reviews with full history

📈 **Statistics Dashboard** - Track approval/rejection metrics with visual charts

📂 **File Change Logs** - See which files changed with detailed +/- statistics

🔐 **PostgreSQL Persistence** - Enterprise-grade database backend

🔗 **GitHub Integration** - Full GitHub API support for commits, branches, and code

🔍 **Beautiful UI** - Box-framed menus, visual indicators, emoji-rich interface

🜟 **Production-Ready** - Docker Compose, health checks, security hardening

---

## 🎆 What's New in v3.0

### 📄 Diff Viewing

**View complete code changes inline:**
- Click "📄 Show diff" button on any commit
- Small diffs (<4KB): Display as code block in chat
- Large diffs (>4KB): Send as downloadable `.patch` file
- Full patch format for external tools

**Example:**
```
📄 Diff for commit: `a1b2c3d4...`

```diff
 diff --git a/file.py b/file.py
 -    return "world"
 +    return "world v2"
```
```

### 📁 Files Changed Log

**Automatic file change tracking:**
- Status indicators: 🆕 added, ✍️ modified, ❌ removed, 📄 renamed, 📃 copied
- Line counters: +additions, -deletions, changes total
- First 5 files shown inline, summary for larger commits

**Example display:**
```
*🗁 Changed 3 files:*
✏️ src/auth.py (+15/-8)
🆕 tests/test_auth.py (+50/-0)
... and 1 more file
```

### 📈 Code Export to Branch

**Two export modes:**

**Mode 1: Export to Existing Branch**
- Select target branch from list
- Auto cherry-pick commit
- Get confirmation link

**Mode 2: Create New Branch**
- Enter new branch name
- Bot creates branch and cherry-picks commit
- Get new branch link on GitHub

**Example flow:**
```
User: [📈 Export code]
Bot: [📦 To existing]  [🌱 Create new]
User: [🌱 Create new]
Bot: Enter branch name: feature/backport-fix
Bot: ✅ Created `feature/backport-fix`
     🔗 New commit: `xyz789ab...`
     [Open branch](https://github.com/...)
```

### 📈 Enhanced Commit Display

Each commit now shows:
- 💬 Commit message with parsing
- 📁 Files changed with status & line counts
- 🔐 GPG signature status
- ✓ Verification results
- 🔗 Clickable GitHub link
- 4 action buttons: Approve, Reject, Show diff, Export code

---

## 📂 Database: SQLite → PostgreSQL Migration

### Why PostgreSQL?

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Concurrency** | Single writer | Multiple writers |
| **Scalability** | Files on disk | Full RDBMS |
| **Data types** | Basic | Advanced (JSON, UUID, etc.) |
| **Performance** | Good (files) | Excellent (server) |
| **Cloud deployment** | ❌ Not ideal | ✅ Excellent |
| **Backups** | Manual file copy | Native tools |
| **Data integrity** | Basic | ACID transactions |

### Configuration

**Environment variable:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/github_verifier
```

**Default (local):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/github_verifier
```

**Schema includes:**
- `users` table with Telegram user tracking
- `verifications` table with full audit trail
- Indexes on user_id, commit_sha, created_at
- CHECK constraints on status (approved/rejected only)
- Cascading deletes for data integrity

---

## 🔏 Prerequisites

- **Docker & Docker Compose** (v3.8+)
- **PostgreSQL** (v12+) - included in docker-compose.yml
- **Telegram Bot Token** (get from [@BotFather](https://t.me/botfather))
- **GitHub Personal Access Token** (PAT with `repo` access)
- **Unix-like environment** (Linux, macOS, WSL2 on Windows)

---

## 🚀 Quick Start (2 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# GitHub Configuration  
GITHUB_TOKEN=your_github_personal_access_token_here

# PostgreSQL Configuration
DATABASE_URL=postgresql://github_bot:secure_password@postgres:5432/github_verifier
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=github_verifier

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
Initializing services...
Connected to PostgreSQL
Database tables initialized successfully
Services initialized successfully
Starting bot...
```

Now open Telegram and send `/start` to your bot! 🎉

---

## 🜐 Docker Compose Services

### PostgreSQL Service

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=github_verifier
      - POSTGRES_USER=github_bot
      - POSTGRES_PASSWORD=secure_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U github_bot"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Bot Service

```yaml
  github-commits-bot:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://...
      - TELEGRAM_BOT_TOKEN=...
      - GITHUB_TOKEN=...
    volumes:
      - ./logs:/app/logs
```

### Database Volume Persistence

```yaml
volumes:
  postgres_data:
    driver: local
```

Database persists across container restarts.

---

## 📂 Database Management

### Connect to PostgreSQL

```bash
# Using psql in container
docker exec -it postgres psql -U github_bot -d github_verifier

# Common commands
\dt                     -- List tables
\d verifications        -- Show table structure
SELECT COUNT(*) FROM verifications;  -- Count records
```

### Query Examples

```sql
-- Get user's statistics
SELECT status, COUNT(*) 
FROM verifications 
WHERE user_id = 123456789 
GROUP BY status;

-- Find commits by repository
SELECT * FROM verifications 
WHERE repo = 'sileade/github-commits-verifier-bot' 
ORDER BY created_at DESC;

-- Global statistics
SELECT 
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_verifications,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
FROM verifications;
```

### Backup & Restore

```bash
# Backup entire database
docker exec postgres pg_dump -U github_bot github_verifier > backup.sql

# Restore from backup
docker exec -i postgres psql -U github_bot github_verifier < backup.sql

# Compress backup
tar -czf backup-$(date +%Y%m%d).tar.gz backup.sql
```

---

## 📂 Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,              -- Telegram user ID
    username TEXT NOT NULL,                  -- Telegram @username
    created_at TIMESTAMP WITH TIME ZONE      -- Registration time
);
```

### Verifications Table

```sql
CREATE TABLE verifications (
    id BIGSERIAL PRIMARY KEY,                -- Auto-increment ID
    user_id BIGINT NOT NULL,                 -- Foreign key to users
    repo TEXT NOT NULL,                      -- Repository path
    commit_sha TEXT NOT NULL,                -- Full commit SHA
    status TEXT NOT NULL,                    -- 'approved' or 'rejected'
    created_at TIMESTAMP WITH TIME ZONE,     -- Verification time
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (status IN ('approved', 'rejected'))
);

-- Indexes for query optimization
CREATE INDEX idx_verifications_user_id ON verifications(user_id);
CREATE INDEX idx_verifications_commit_sha ON verifications(commit_sha);
CREATE INDEX idx_verifications_created_at ON verifications(created_at DESC);
```

---

## 📁 Migration from SQLite

### Automatic Migration

Bot detects SQLite database and performs automated migration:

```bash
# Bot will automatically:
1. Connect to PostgreSQL
2. Create tables if missing
3. Create indexes
4. Set up constraints
5. Ready to use!
```

### Manual Migration (if needed)

```bash
# Export from SQLite
sqlite3 verifications.db ".mode csv" "SELECT * FROM verifications;" > data.csv

# Import to PostgreSQL
docker exec -i postgres psql -U github_bot github_verifier \
  -c "COPY verifications FROM STDIN CSV"
```

---

## 📈 API Changes in v3.0

### New Methods in `github_service.py`

```python
# Get files changed in commit
async def get_commit_files(repo_path, commit_sha) -> List[Dict]

# Get complete diff/patch
async def get_commit_diff(repo_path, commit_sha) -> str

# List all branches
async def get_branches(repo_path) -> List[str]

# Create new branch
async def create_branch(repo_path, new_branch, from_ref) -> bool

# Cherry-pick commit to another branch
async def cherry_pick_commit(repo_path, commit_sha, target_branch) -> str

# Create pull request
async def create_pull_request(repo_path, base, head, title, body) -> str
```

### New Methods in `database.py`

```python
# Async initialization
await db.init()

# Get global statistics across all users
async def get_global_stats() -> Dict[str, Any]
```

---

## 📂 Container Management

### View Services

```bash
# Check all services running
docker-compose ps

# Shows:
# postgres           - PostgreSQL database
# github-commits-bot - Main bot application
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

### Restart Services

```bash
# Graceful restart (30s timeout)
docker-compose restart

# Force restart
docker-compose kill
docker-compose up -d

# Restart specific service
docker-compose restart github-commits-bot
```

### Stop & Clean Up

```bash
# Stop containers
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

### Check Resource Usage

```bash
# View container statistics
docker stats

# Check database size
docker exec postgres psql -U github_bot -d github_verifier \
  -c "SELECT pg_size_pretty(pg_database_size('github_verifier'));"
```

---

## 📂 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec github-commits-bot psql -c "SELECT 1" \
  postgresql://github_bot:password@postgres:5432/github_verifier

# Check logs
docker-compose logs postgres | tail -20
```

### Bot Won't Start

| Issue | Solution |
|-------|----------|
| `TELEGRAM_BOT_TOKEN not found` | Set in `.env` |
| `DATABASE_URL not found` | Set correct PostgreSQL URL |
| `Connection refused (postgres)` | Ensure postgres container healthy: `docker-compose ps` |
| `psycopg2.OperationalError` | Check DATABASE_URL format |

### Check Bot Status

```bash
# Verify bot is connected
docker-compose logs github-commits-bot | grep "Starting bot"

# Send test command
# In Telegram: /start
```

---

## 👥 Obtaining Required Tokens

### GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ☑ `repo` - Full control of repositories
4. Generate & copy token immediately
5. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
   ```

### Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Choose bot name: "GitHub Commits Verifier"
4. Choose username: `github_commits_verifier_bot`
5. BotFather sends HTTP API token
6. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567
   ```

---

## 📈 Usage Guide

### Main Menu Options

```
🔍 Check Commit       → Analyze commit legitimacy & see diff
✅ Approve Commit     → Mark as verified
❌ Reject Commit      → Mark as suspicious
📊 History           → View recent verifications
📈 Statistics        → See approval/rejection stats
⚙️ Settings          → Configure bot
```

### Example Workflow

**Check and export a commit:**

1. `/start` → Select 🔍 Check Commit
2. Enter: `sileade/github-commits-verifier-bot`
3. Enter: commit SHA (e.g., `a1b2c3d4`)
4. See commit info, files changed, verification results
5. Click 📄 Show diff → View changes
6. Click 📈 Export code → Choose branch
7. Cherry-pick to target branch
8. Click ✅ Approve → Confirm action

---

## 📚 Documentation Files

- **[README.md](README.md)** - This file, setup & usage
- **[FEATURES_v3.md](FEATURES_v3.md)** - Detailed feature documentation
- **[.env.example](.env.example)** - Configuration template

---

## 📂 License

MIT License - see [LICENSE](LICENSE) for details

You're free to use, modify, and distribute this bot! 🌟

---

## 🤝 Support

- 🔍 Found a bug? [Open an issue](https://github.com/sileade/github-commits-verifier-bot/issues)
- 💯 Have a suggestion? [Discussions](https://github.com/sileade/github-commits-verifier-bot/discussions)
- 🔗 Want to contribute? [Pull requests welcome!](https://github.com/sileade/github-commits-verifier-bot/pulls)

---

**Made with ❤️ for DevOps engineers**
