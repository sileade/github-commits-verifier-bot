# 🤖 GitHub Commits Verifier Bot - v3.0 Features

## 🎆 New Features in v3.0

### 1. 📄 Commit Diff Viewing

**Feature:** View the complete diff/patch for any commit directly in Telegram

**How it works:**
1. After checking a commit, you see the commit info with buttons
2. Click "📄 Show diff" button
3. Bot fetches the patch from GitHub
4. If diff is small (<4KB), shows as code block
5. If diff is large (>4KB), sends as downloadable `.patch` file

**What you see:**
```
📄 Diff for commit: `a1b2c3d4...`

```diff
diff --git a/file.py b/file.py
index abc..def 100644
--- a/file.py
+++ b/file.py
@@ -1,5 +1,6 @@
 def hello():
-    return "world"
+    return "world v2"
+    print("updated")
```
```

### 2. 📁 Files Changed Log

**Feature:** Shows all files modified in the commit with change statistics

**Displayed info for each file:**
- Status indicator:
  - 🆕 `added` - New file created
  - ✍️ `modified` - Existing file changed
  - ❌ `removed` - File deleted
  - 📄 `renamed` - File renamed
  - 📃 `copied` - File copied
- Filename
- Addition count (`+lines`)
- Deletion count (`-lines`)

**Example display:**
```
*📁 Онсканыются 3 файла:*
✍️ src/main.py (+15/-8)
🆕 new_feature.md (+50/-0)
❌ old_code.py (+0/-30)
```

### 3. 📈 Code Export to Branch

**Feature:** Export a commit's changes to an existing or new branch

**Two modes:**

#### Mode 1: Export to Existing Branch
1. Click "📈 Export code" button
2. Select "📦 To existing branch"
3. Choose target branch from list
4. Bot cherry-picks the commit to that branch
5. Get confirmation with link to branch

#### Mode 2: Create New Branch
1. Click "📈 Export code" button
2. Select "🌱 Create new branch"
3. Enter new branch name (e.g., `feature/new-feature`)
4. Bot creates branch and cherry-picks commit
5. Get confirmation with link to new branch

**What happens under the hood:**
- Uses GitHub API to cherry-pick commits
- Creates new branch if needed
- Updates branch HEAD to new commit SHA
- Returns clickable link to branch on GitHub

**Example flow:**
```
User: 📈 Export code
Bot: Select where to export:
     [📦 To existing branch]
     [🌱 Create new branch]

User: [🌱 Create new branch]
Bot: 🌱 Enter new branch name (e.g., `feature/new-feature`):

User: feature/cherry-picked-fix
Bot: ✅ *Commit successfully exported!*
     
     🌱 Branch: `feature/cherry-picked-fix`
     🔗 New commit: `e5f6g7h8...`
     
     [🔗 Open branch](https://github.com/owner/repo/tree/feature/cherry-picked-fix)
```

## 📈 Enhanced Commit Display

When you check a commit, you now see:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔍 Информация о коммите      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📦 Repository: `owner/repo`
🔗 SHA: `a1b2c3d4...`
👤 Author: John Doe
📧 Email: john@example.com
📅 Date: 2025-12-08

💬 Message:
`Fix critical bug in authentication module`

*🗂️ Changed 3 files:*
✏️ src/auth.py (+15/-8)
🆕 tests/test_auth.py (+50/-0)

🔐 GPG Signed: Yes

*✓ Verification Results:*
✅ GPG Signature: PASS
✅ Known Author: PASS
✅ Message Present: PASS
✅ Valid Date: PASS

[🔗 Open on GitHub](https://github.com/owner/repo/commit/a1b2c3d4...)

[✅ Approve] [❌ Reject]
[📄 Show diff] [📤 Export code]
[🔙 Main Menu]
```

## 🔐 API Methods Added (github_service.py)

### `get_commit_files(repo_path, commit_sha)`
Returns list of files changed in commit with:
- filename
- status (added/modified/removed/renamed/copied)
- additions (number of lines added)
- deletions (number of lines deleted)
- changes (total changes)

### `get_commit_diff(repo_path, commit_sha)`
Returns the patch format diff of the commit

### `get_branches(repo_path)`
Returns list of all branch names in repository

### `create_branch(repo_path, new_branch, from_ref)`
Creates a new branch from specified commit/branch SHA

### `cherry_pick_commit(repo_path, commit_sha, target_branch)`
Copies a commit to target branch (cherry-pick operation)

### `create_pull_request(repo_path, base, head, title, body)`
Creates a pull request (for future enhancements)

## 💡 User Stories

### Story 1: "I want to see what changed in this commit"
1. Check commit → View basic info
2. Click "📄 Show diff" → See full diff
3. Understand exactly what code changed

### Story 2: "I want to backport this fix to an older release branch"
1. Check commit → Verify it's good
2. Click "📤 Export code"
3. Select "📦 To existing branch" → Choose `release/v2.0`
4. Bot cherry-picks the commit
5. Fix is now in the older branch

### Story 3: "I want to try this feature in a separate branch first"
1. Check commit → Like what you see
2. Click "📤 Export code"
3. Select "🌱 Create new branch"
4. Enter name: `test/new-feature`
5. Bot creates branch with the commit
6. Click link to view in GitHub

## 🔰 Technical Implementation

### Diff Handling
- Fetches patch via GitHub API (`Accept: application/vnd.github.v3.patch`)
- Splits logic:
  - Small (<4KB): Sends as code block in Telegram message
  - Large (>4KB): Sends as `.patch` file attachment

### Files Changed
- Fetches from commit endpoint
- Filters to first 5 files for display
- Shows summary if more files exist
- Uses emoji for visual status indicators

### Branch Operations
- Uses Git API (`/repos/{owner}/{repo}/git/*` endpoints)
- Cherry-pick via commit creation API
- Updates branch ref to new commit SHA
- Returns clickable GitHub link for verification

## 🔄 Error Handling

**Graceful degradation:**
- Diff unavailable → Notify user
- Branch list unavailable → Still show manual input
- Cherry-pick failed → Show error, explain why (permissions, branch conflict, etc.)
- Large diff → Automatic file upload instead of text block

## 🐘 Limitations & Future Work

**Current limitations:**
- Cherry-pick uses commit creation API (works for most cases)
- No merge conflict resolution (simple cherry-picks only)
- No PR creation with cherry-picked commit (future)
- Files list limited to first 5 (can scroll/paginate)

**Future enhancements:**
- Create PR with exported commit
- Auto-detect merge conflicts
- Bulk export multiple commits
- Diff viewer with syntax highlighting
- Integration with CI/CD to verify export

## 🏗️ Usage Examples

### Example 1: Check diff
```
User: /start
Bot: [Main menu with 6 buttons]

User: [🔍 Check Commit]
Bot: 📝 Enter repository...

User: owner/repo
Bot: ✅ Found: owner/repo
Bot: 📌 Enter commit SHA...

User: abc123def456
Bot: [Shows full commit info with files]

User: [📄 Show diff]
Bot: [Sends diff file: commit-abc123de.patch]
```

### Example 2: Export to new branch
```
User: [📤 Export code]
Bot: 🌱 Create new branch?
     [📦 Existing] [🌱 New]

User: [🌱 New]
Bot: 🌱 Enter branch name:

User: feature/backport-fix
Bot: ✅ Commit successfully exported!
     
     🌱 Branch: `feature/backport-fix`
     🔗 New commit: `xyz789...`
     [Open branch](https://github.com/...)
```
