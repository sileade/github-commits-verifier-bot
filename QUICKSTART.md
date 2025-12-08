# 🚀 Quick Start Guide - Interactive Buttons v2.0

## 🤖 First Time Setup

### 1. Deploy Bot

```bash
git clone https://github.com/sileade/github-commits-verifier-bot.git
cd github-commits-verifier-bot

cp .env.example .env
# Edit .env with your tokens

docker-compose up -d
```

### 2. Find Your Bot on Telegram

- Search for your bot username (set via @BotFather)
- Send `/start`
- See the main menu

---

## 📱 Using the Bot - Interactive Flows

### Flow 1: Check & Approve a Commit

**Goal:** Verify a commit is legitimate and approve it

**Steps:**

1. **Send `/start` to bot**
   ```
   🤖 GitHub Commits Verifier Bot
   
   Select action:
   [🔍 Check Commit]
   [✅ Approve Commit]
   [❌ Reject Commit]
   [📊 History]
   [⚙️ Settings]
   ```

2. **Click "🔍 Check Commit"**
   ```
   📝 Enter full GitHub URL or name: owner/repo
   ```

3. **Type repository**
   ```
   User: sileade/github-commits-verifier-bot
   Bot: ✅ Repository found: sileade/github-commits-verifier-bot
   
   📌 Enter commit SHA:
   ```

4. **Type commit SHA**
   ```
   User: a1b2c3d4e5f6g7h8i9j0
   Bot: [Shows commit details]
   ```

5. **See Commit Details**
   ```
   🔍 Commit Information:
   
   📦 Repository: sileade/github-commits-verifier-bot
   🔗 SHA: a1b2c3d4e5f6g7h8...
   👤 Author: John Doe
   📧 Email: john@example.com
   📅 Date: 2025-12-08 12:30:45
   📝 Message: Fix bug #123
   
   🔐 GPG Signed: Yes
   
   ✓ Verification Results:
   ✅ GPG Signature: PASS
   ✅ Known Author: PASS
   ✅ Commit Message: PASS
   ✅ Valid Date: PASS
   
   [🔗 Open on GitHub]
   
   [✅ Approve] [❌ Reject]
   [🔙 Main Menu]
   ```

6. **Click "✅ Approve" Button**
   ```
   ✅ Commit Successfully Processed
   
   📦 Repository: sileade/github-commits-verifier-bot
   🔗 SHA: a1b2c3d4...
   📋 Status: APPROVED
   
   🔐 Commit Approved
   
   [🔍 Check Another] [🔙 Main Menu]
   ```

7. **Done!** 🎉
   - Commit saved to database
   - Status: `approved`
   - Statistics updated
   - Ready to check another

---

### Flow 2: Quick Approve (Without Full Check)

**Goal:** Approve a commit directly without viewing details

**Steps:**

1. **Send `/start`**

2. **Click "✅ Approve Commit"**
   ```
   ✅ Enter commit SHA:
   ```

3. **Type SHA**
   ```
   User: a1b2c3d4e5f6g7h8i9j0
   ```

4. **Bot asks for repository** (if not in context)
   ```
   Note: Repository was stored from previous check
   Bot: Direct approval recorded
   ```

5. **Confirmation**
   ```
   ✅ Commit Successfully Processed
   
   Repository: org/repo
   SHA: a1b2c3d4...
   Status: APPROVED
   ```

---

### Flow 3: View Verification History

**Goal:** See all your recent commit verifications

**Steps:**

1. **Send `/start`**

2. **Click "📊 History"**
   ```
   📊 Verification History (Last 10):
   
   1. ✅ sileade/repo1 - a1b2c3d4...
      📅 2025-12-08 12:30:45
   
   2. ❌ sileade/repo2 - e5f6g7h8...
      📅 2025-12-08 12:25:30
   
   3. ✅ sileade/repo3 - i9j0k1l2...
      📅 2025-12-08 12:20:15
   
   [🔙 Back to Menu]
   ```

3. **Click "🔙 Back to Menu"**
   - Returns to main menu
   - No data lost
   - Session preserved

---

### Flow 4: View Statistics

**Goal:** See your verification stats

**Steps:**

1. **Send `/stats`** (or go to menu → Stats)
   ```
   📊 Your Statistics:
   
   ✅ Approved: 15
   ❌ Rejected: 3
   🔍 Total Verified: 18
   
   📈 Approval Ratio: 83.3%
   
   [🔙 Back to Menu]
   ```

2. **Interpret Results:**
   - You've approved 15 commits
   - You've rejected 3 commits
   - Approval rate: 83.3% (mostly trusting)

---

## 💼 Common Workflows

### Workflow 1: Quick Verification Session

```
1. /start
2. 🔍 Check Commit
3. Enter repo
4. Enter SHA
5. [✅ Approve] immediately
6. [🔍 Check Another]
7. Repeat steps 3-6
8. Done [🔙 Main Menu]
```

**Time:** ~30 seconds per commit

### Workflow 2: Bulk Approval

```
1. /start
2. ✅ Approve Commit (if repo in context)
3. Enter SHA
4. [✅ Another Approval]
5. Enter SHA
6. Repeat steps 3-5
7. [🔙 Main Menu]
```

**Time:** ~15 seconds per commit (faster, no details viewed)

### Workflow 3: Regular Check-in

```
1. /stats (quick overview)
2. 📊 History (what did I check?)
3. 🔍 Check Commit (verify one more)
4. [🔙 Main Menu]
```

**Time:** ~2 minutes

---

## 🪁 Button Reference

### Main Menu Buttons

| Button | Icon | Function | Next Step |
|--------|------|----------|----------|
| Check Commit | 🔍 | Verify commit | Enter repo |
| Approve Commit | ✅ | Quick approve | Enter SHA |
| Reject Commit | ❌ | Quick reject | Enter SHA |
| History | 📊 | View recent | Show list |
| Settings | ⚙️ | Configure | Show options |

### Action Buttons

| Button | Icon | Result | Flow |
|--------|------|--------|------|
| Approve | ✅ | Save approved | Show result |
| Reject | ❌ | Save rejected | Show result |
| Back to Menu | 🔙 | Return home | Main menu |
| Check Another | 🔍 | New check | Enter repo |
| GitHub Link | 🔗 | Open browser | GitHub.com |

---

## 💡 Pro Tips

### Tip 1: Use Back Button Strategically
- Any time you need to restart
- No confirmation needed
- Clean navigation

### Tip 2: Keep Repo in Context
- First check establishes repo
- Approve/Reject buttons remember it
- Faster subsequent actions

### Tip 3: Review Stats Regularly
- `/stats` command anytime
- Track your approval patterns
- Monitor workflow efficiency

### Tip 4: Use History for Audit
- `📊 History` shows timestamps
- Verify what you've done
- Reference for records

### Tip 5: GitHub Link Navigation
- Click 🔗 to view full commit
- See diffs and changes
- Verify before approving

---

## 🔸 Troubleshooting Buttons

### "Button doesn't respond"
- Wait a moment (API lag)
- Try clicking again
- /start and restart flow

### "Back button not showing"
- All screens have back button
- Scroll up if on mobile
- Try /start to reset

### "Numbers aren't updating"
- Statistics cache exists
- Send /stats again
- Close and reopen chat

### "Buttons look strange"
- Update Telegram app
- Different devices show differently
- Functionality is same

---

## 🏗️ Keyboard Shortcuts (Advanced)

### Telegram Desktop Shortcuts
```
Ctrl+A  - Select all
Ctrl+C  - Copy selected
Ctrl+V  - Paste
/start  - Send command
Tab     - Navigate buttons
Enter   - Click button
```

### Mobile Gestures
```
Tap      - Click button
Long tap - Copy text
Swipe    - Scroll
```

---

## 📚 More Information

- **[FEATURES.md](FEATURES.md)** - Detailed feature documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates
- **[README.md](README.md)** - Full project documentation
- **[GitHub Issues](https://github.com/sileade/github-commits-verifier-bot/issues)** - Report bugs

---

## 🌟 Example Session Transcript

```
You: /start
Bot: 🤖 GitHub Commits Verifier Bot
     [5 action buttons]

You: [🔍 Check Commit]
Bot: 📝 Enter repository...

You: sileade/my-app
Bot: ✅ Repository found!
     📌 Enter commit SHA:

You: abc123def456
Bot: 🔍 Commit Information:
     [details...]
     [✅ Approve] [❌ Reject]

You: [✅ Approve]
Bot: ✅ Commit Successfully Processed
     Status: APPROVED
     [🔍 Check Another] [🔙 Main Menu]

You: [🔙 Main Menu]
Bot: 🤖 GitHub Commits Verifier Bot
     [back to main menu]

You: /stats
Bot: 📊 Your Statistics:
     ✅ Approved: 1
     ❌ Rejected: 0
     📈 Approval Ratio: 100%
```

---

**Ready to verify commits? Send `/start` to your bot now! 🚀**
