# Changelog

All notable changes to this project will be documented in this file.

## [3.7.0] - 2025-12-09

### Added

- **🗂️ Repository Selector for All Menu Items:** Replaced all manual repository name input with button-based repository selection.
  - 🔍 **Check Commit:** Now shows repository selector, then commit list from selected repository.
  - 📄 **Analyze History:** Now shows repository selector, then displays commit history for selected repository.
  - ✅ **Approve Commit:** Already had repository selector (from v3.6), now consistent with other menu items.
  - ❌ **Reject Commit:** Already had repository selector (from v3.6), now consistent with other menu items.
  - Repositories are displayed in a 2-column grid layout for easy browsing.
  - Each repository button shows the repository name (truncated to 20 characters if too long).

- **🎮 Functional Bot Control Buttons:** Added working Start/Stop/Restart buttons to the Bot Control Panel.
  - **▶️ Start Bot:** Executes `docker-compose up -d` to start the bot service on the server.
  - **⏸️ Stop Bot:** Executes `docker-compose down` to stop the bot service on the server.
  - **🔄 Restart Bot:** Executes `docker-compose restart` to restart the bot service on the server.
  - All buttons show real-time status updates during execution.
  - Error handling with helpful error messages and fallback instructions.
  - Timeout protection: 60 seconds for start/stop/restart operations.

- **🔍 Commit Detail View:** Added detailed commit view when checking commits.
  - Shows full commit information: repository, SHA, author, date, message.
  - Displays verification status if the commit was previously approved/rejected.
  - Includes Approve/Reject buttons for quick action.
  - "Back" button returns to the commit list.

### Changed

- **Bot Control Panel:** Updated the panel layout to include Start/Stop/Restart buttons alongside the Update button.
- **Navigation Flow:** Improved navigation consistency across all menu items with uniform "Back" button behavior.
- **User Experience:** Eliminated all manual text input for repository and commit selection, making the bot fully button-driven.

### Fixed

- **Callback Data Parsing:** Improved parsing of callback data for commit selection to handle repository names with slashes correctly.

---

## [3.1.0] - 2025-12-09

### Added

- **🚀 Performance Boost:** Replaced blocking `requests` library with non-blocking `aiohttp` for all GitHub and Ollama API calls. This ensures the Telegram bot's event loop remains unblocked, significantly improving concurrency and responsiveness under load.
- **Parallel Repository Status Fetching:** Implemented `asyncio.gather` in `bot.py` to fetch the last commit date for multiple repositories concurrently, speeding up the main menu load time.
- **Strict Environment Variable Check:** `database.py` now strictly requires the `DATABASE_URL` environment variable to be set, aligning with best practices for production deployments.

### Changed

- **Asynchronous Service Layer:** The entire `GitHubService` class in `github_service.py` was refactored to be fully asynchronous using `aiohttp`.
- **Improved Database Module:** Added private helper methods (`_execute`, `_fetch`, `_fetchrow`) to `database.py` for cleaner query execution and centralized error handling.
- **Bot Service Initialization:** Centralized service initialization and shutdown logic in `bot.py`'s `post_init` and `post_shutdown` to manage the lifecycle of the `aiohttp` session.
- **Dependencies:** Updated `requirements.txt` to remove unused dependencies and ensure `aiohttp` is included.

### Fixed

- **Blocking I/O:** Eliminated all instances of blocking I/O in the core application logic, resolving a major performance bottleneck.

---

## [3.0.0] - 2025-12-08

### Added

#### Interactive Button System
- **✅ Approve/Reject Buttons** - Direct inline buttons on commit info messages
  - Approve button: `✅ Подтвердить`
  - Reject button: `❌ Отклонить`
  - Instant callback processing with database storage

#### Enhanced Main Menu
- **Back to Menu Button** - Quick navigation from any menu to main menu
  - `🔙 Назад в меню` button on all submenu screens
  - Smooth transitions between menu states

#### Improved User Flow
- **Commit Verification with Action Buttons**
  - Show commit details with two-button confirmation
  - Visual feedback with emojis
  - Links to GitHub commit view
  - Email display for commit author

#### Better Statistics
- **Approval Ratio Calculation**
  - Shows percentage of approved commits
  - `📈 Процент одобрений: X.X%`

#### Enhanced Navigation
- **Back to Menu from Any State**
  - History view with back button
  - Settings view with back button
  - Stats view with back button
  - Commit detail view with back button

### Changed

- **Improved Button Callbacks**
  - Dedicated handler: `handle_commit_action_callback()`
  - Pattern-based callback routing: `approve_<sha>` and `reject_<sha>`
  - Better error handling for invalid callbacks

- **Enhanced Commit Display**
  - Email field displayed for authors
  - Link to GitHub commit (clickable, no preview)
  - Cleaner formatting with emojis

- **Better User Experience**
  - Faster response to button clicks (no intermediate screens)
  - Immediate visual feedback
  - Inline commit approval without extra steps

### Technical Improvements

- **Conversation State Management**
  - Separate pattern-based callback handler for commit actions
  - `CallbackQueryHandler(pattern=r'^(approve|reject)_')` for specific actions
  - Better separation of concerns

- **Error Handling**
  - Try-catch blocks in all callback handlers
  - Detailed error logging
  - User-friendly error messages

- **Code Organization**
  - Cleaner function separation
  - Better documentation
  - Improved code comments

### Fixed

- **Dialog Flow Issues**
  - Fixed back navigation from sub-menus
  - Proper state cleanup after actions
  - Consistent response formatting

---

## [2.0.0] - 2025-12-08

### Added

#### Interactive Button System
- **✅ Approve/Reject Buttons** - Direct inline buttons on commit info messages
  - Approve button: `✅ Подтвердить`
  - Reject button: `❌ Отклонить`
  - Instant callback processing with database storage

#### Enhanced Main Menu
- **Back to Menu Button** - Quick navigation from any menu to main menu
  - `🔙 Назад в меню` button on all submenu screens
  - Smooth transitions between menu states

#### Improved User Flow
- **Commit Verification with Action Buttons**
  - Show commit details with two-button confirmation
  - Visual feedback with emojis
  - Links to GitHub commit view
  - Email display for commit author

#### Better Statistics
- **Approval Ratio Calculation**
  - Shows percentage of approved commits
  - `📈 Процент одобрений: X.X%`

#### Enhanced Navigation
- **Back to Menu from Any State**
  - History view with back button
  - Settings view with back button
  - Stats view with back button
  - Commit detail view with back button

### Changed

- **Improved Button Callbacks**
  - Dedicated handler: `handle_commit_action_callback()`
  - Pattern-based callback routing: `approve_<sha>` and `reject_<sha>`
  - Better error handling for invalid callbacks

- **Enhanced Commit Display**
  - Email field displayed for authors
  - Link to GitHub commit (clickable, no preview)
  - Cleaner formatting with emojis

- **Better User Experience**
  - Faster response to button clicks (no intermediate screens)
  - Immediate visual feedback
  - Inline commit approval without extra steps

### Technical Improvements

- **Conversation State Management**
  - Separate pattern-based callback handler for commit actions
  - `CallbackQueryHandler(pattern=r'^(approve|reject)_')` for specific actions
  - Better separation of concerns

- **Error Handling**
  - Try-catch blocks in all callback handlers
  - Detailed error logging
  - User-friendly error messages

- **Code Organization**
  - Cleaner function separation
  - Better documentation
  - Improved code comments

### Fixed

- **Dialog Flow Issues**
  - Fixed back navigation from sub-menus
  - Proper state cleanup after actions
  - Consistent response formatting

---

## [1.0.0] - 2025-12-08

### Initial Release

#### Core Features
- ✅ GitHub commit verification via Telegram
- ✅ Commit legitimacy checks (GPG signature, author, message, date)
- ✅ Commit approval/rejection tracking
- ✅ User history and statistics
- ✅ SQLite database for persistent storage

#### Infrastructure
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Production-ready security settings
- ✅ Health checks and resource limits
- ✅ Comprehensive logging

#### Commands
- ✅ `/start` - Main menu
- ✅ `/help` - Help information
- ✅ `/stats` - User statistics

#### Database
- ✅ SQLite with two tables: Users and Verifications
- ✅ Efficient querying with indexes
- ✅ Data persistence across restarts

---

## Future Roadmap

### Planned Features
- [ ] Export verification reports as CSV/PDF
- [ ] Team statistics and collaboration features
- [ ] Webhook integration for GitHub events
- [ ] Automated commit verification on push
- [ ] Custom verification rules
- [ ] Multi-language support
- [ ] API endpoint for external integrations
- [ ] Backup and restore functionality
- [ ] Web dashboard for statistics
- [ ] Email notifications

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 3.1.0 | 2025-12-09 | 🚀 Latest |
| 3.0.0 | 2025-12-08 | ✅ Released |
| 2.0.0 | 2025-12-08 | ✅ Released |
| 1.0.0 | 2025-12-08 | ✅ Released |


## [3.2.0] - 2025-12-09

### Added

- **Comprehensive Code Analysis:** Integrated multi-pass static analysis to identify code smells, performance issues, and potential bugs.

### Changed

- **Improved Exception Handling:** Replaced broad `except Exception` clauses with more specific exception types (`aiohttp.ClientError`, `asyncio.TimeoutError`, `json.JSONDecodeError`, `openai.APIError`, `asyncpg.PostgresError`) across the codebase for better error diagnostics and robustness.
- **Code Style:** Fixed multiple long lines (>120 characters) by reformatting them for better readability in `bot.py`, `github_service.py`, and `ai_analyzer.py`.

### Fixed

- **Potential Unhandled Exceptions:** Ensured that specific exceptions from `aiohttp`, `openai`, and `asyncpg` are caught, preventing unexpected crashes.
