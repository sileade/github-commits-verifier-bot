# Changelog

All notable changes to this project will be documented in this file.

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
