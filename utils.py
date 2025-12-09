#!/usr/bin/env python3
"""
Utility functions and helpers
Помощние функции для парсинга, валидации и обработки данных
"""

import re
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RepositoryParser:
    """
    Utility class for parsing GitHub repository paths and URLs
    Парсинг GitHub репозиториев
    """
    
    GITHUB_URL_REGEX = re.compile(
        r'^(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)(?:/.*)?$'
    )
    OWNER_REPO_REGEX = re.compile(r'^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)$')
    
    @staticmethod
    def parse_repo_path(repo_path: str) -> Tuple[str, str]:
        """
        Parse repository path from URL or owner/repo format
        
        Args:
            repo_path: GitHub URL or 'owner/repo' format
            
        Returns:
            Tuple[owner, repo]: Parsed owner and repository name
            
        Raises:
            ValueError: If repository path format is invalid
            
        Examples:
            >>> RepositoryParser.parse_repo_path('https://github.com/sileade/repo')
            ('sileade', 'repo')
            >>> RepositoryParser.parse_repo_path('sileade/repo')
            ('sileade', 'repo')
        """
        if not repo_path or not isinstance(repo_path, str):
            raise ValueError("Repository path must be a non-empty string")
        
        repo_path = repo_path.strip()
        
        # Try GitHub URL format first
        url_match = RepositoryParser.GITHUB_URL_REGEX.match(repo_path)
        if url_match:
            owner, repo = url_match.groups()
            if not owner or not repo:
                raise ValueError(f"Invalid GitHub URL: {repo_path}")
            return owner, repo
        
        # Try owner/repo format
        owner_repo_match = RepositoryParser.OWNER_REPO_REGEX.match(repo_path)
        if owner_repo_match:
            owner, repo = owner_repo_match.groups()
            return owner, repo
        
        raise ValueError(
            f"Invalid repository format: '{repo_path}'. "
            "Use 'owner/repo' or 'https://github.com/owner/repo'"
        )
    
    @staticmethod
    def get_repo_name(repo_path: str) -> str:
        """
        Extract repository name from path
        
        Args:
            repo_path: Repository path or URL
            
        Returns:
            str: Repository name
        """
        _, repo = RepositoryParser.parse_repo_path(repo_path)
        return repo
    
    @staticmethod
    def get_repo_owner(repo_path: str) -> str:
        """
        Extract repository owner from path
        
        Args:
            repo_path: Repository path or URL
            
        Returns:
            str: Repository owner
        """
        owner, _ = RepositoryParser.parse_repo_path(repo_path)
        return owner


class CommitValidator:
    """
    Utility class for validating and normalizing commit SHAs
    Валидация SHA коммитов
    """
    
    # Match 7-40 character hex strings (short to full SHA)
    SHA_REGEX = re.compile(r'^[a-f0-9]{7,40}$', re.IGNORECASE)
    SHORT_SHA_LENGTH = 7
    FULL_SHA_LENGTH = 40
    
    @staticmethod
    def validate_commit_sha(sha: str) -> bool:
        """
        Validate commit SHA format
        
        Args:
            sha: Commit SHA to validate
            
        Returns:
            bool: True if SHA is valid
            
        Examples:
            >>> CommitValidator.validate_commit_sha('abc1234')
            True
            >>> CommitValidator.validate_commit_sha('invalid')
            False
        """
        if not isinstance(sha, str):
            return False
        
        sha = sha.strip()
        return bool(CommitValidator.SHA_REGEX.match(sha))
    
    @staticmethod
    def normalize_commit_sha(sha: str) -> str:
        """
        Normalize commit SHA (lowercase, stripped)
        
        Args:
            sha: Commit SHA
            
        Returns:
            str: Normalized SHA
            
        Raises:
            ValueError: If SHA is invalid
        """
        if not CommitValidator.validate_commit_sha(sha):
            raise ValueError(f"Invalid commit SHA: {sha}")
        return sha.strip().lower()
    
    @staticmethod
    def is_short_sha(sha: str) -> bool:
        """
        Check if SHA is a short SHA (7 characters)
        
        Args:
            sha: Commit SHA
            
        Returns:
            bool: True if short SHA
        """
        if not CommitValidator.validate_commit_sha(sha):
            return False
        return len(sha.strip()) == CommitValidator.SHORT_SHA_LENGTH
    
    @staticmethod
    def is_full_sha(sha: str) -> bool:
        """
        Check if SHA is a full SHA (40 characters)
        
        Args:
            sha: Commit SHA
            
        Returns:
            bool: True if full SHA
        """
        if not CommitValidator.validate_commit_sha(sha):
            return False
        return len(sha.strip()) == CommitValidator.FULL_SHA_LENGTH


class InputSanitizer:
    """
    Utility class for sanitizing user input
    Очистка пользовательского ввода
    """
    
    MAX_REPO_PATH_LENGTH = 200
    MAX_MESSAGE_LENGTH = 2000
    
    @staticmethod
    def sanitize_repo_path(repo_path: str) -> str:
        """
        Sanitize repository path input
        
        Args:
            repo_path: Repository path
            
        Returns:
            str: Sanitized path
            
        Raises:
            ValueError: If input is too long or invalid
        """
        if not isinstance(repo_path, str):
            raise ValueError("Repository path must be a string")
        
        repo_path = repo_path.strip()
        
        if len(repo_path) == 0:
            raise ValueError("Repository path cannot be empty")
        
        if len(repo_path) > InputSanitizer.MAX_REPO_PATH_LENGTH:
            raise ValueError(
                f"Repository path too long (max {InputSanitizer.MAX_REPO_PATH_LENGTH} chars)"
            )
        
        # Remove any control characters
        repo_path = ''.join(c for c in repo_path if ord(c) >= 32 or c in '\t\n')
        
        return repo_path
    
    @staticmethod
    def sanitize_commit_sha(sha: str) -> str:
        """
        Sanitize commit SHA input
        
        Args:
            sha: Commit SHA
            
        Returns:
            str: Sanitized SHA
            
        Raises:
            ValueError: If SHA is invalid
        """
        if not isinstance(sha, str):
            raise ValueError("Commit SHA must be a string")
        
        sha = sha.strip()
        
        if not CommitValidator.validate_commit_sha(sha):
            raise ValueError(f"Invalid commit SHA format: {sha}")
        
        return CommitValidator.normalize_commit_sha(sha)
    
    @staticmethod
    def truncate_message(message: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
        """
        Truncate message to maximum length
        
        Args:
            message: Message to truncate
            max_length: Maximum length
            
        Returns:
            str: Truncated message
        """
        if len(message) <= max_length:
            return message
        return message[:max_length - 3] + "..."


class TextFormatter:
    """
    Utility class for text formatting
    Форматирование текста
    """
    
    @staticmethod
    def format_commit_short_info(sha: str, message: str, author: str) -> str:
        """
        Format short commit information
        
        Args:
            sha: Commit SHA
            message: Commit message
            author: Author name
            
        Returns:
            str: Formatted string
        """
        short_sha = sha[:8] if len(sha) >= 8 else sha
        short_message = message.split('\n')[0][:100]
        return f"`{short_sha}` - {short_message} ({author})"
    
    @staticmethod
    def format_verification_status(status: str) -> str:
        """
        Format verification status with emoji
        
        Args:
            status: Verification status ('approved', 'rejected')
            
        Returns:
            str: Formatted status with emoji
        """
        emoji_map = {
            'approved': '✅',
            'rejected': '❌',
        }
        return f"{emoji_map.get(status, '❓')} {status.upper()}"
    
    @staticmethod
    def format_file_change(filename: str, status: str, additions: int, deletions: int) -> str:
        """
        Format file change information
        
        Args:
            filename: File name
            status: Change status (added, modified, removed, etc.)
            additions: Number of additions
            deletions: Number of deletions
            
        Returns:
            str: Formatted string
        """
        status_emoji = {
            'added': '🆕',
            'modified': '✍️',
            'removed': '❌',
            'renamed': '📄',
            'copied': '📃',
        }.get(status, '📄')
        
        return f"{status_emoji} {filename} (+{additions}/-{deletions})"


class RateLimiter:
    """
    Simple rate limiter for API calls
    Ограничение частоты API вызовов
    """
    
    def __init__(self, calls_per_second: float = 10):
        """
        Initialize rate limiter
        
        Args:
            calls_per_second: Maximum calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time: Optional[float] = None
    
    async def acquire(self) -> None:
        """
        Wait if necessary to maintain rate limit
        
        Example:
            >>> limiter = RateLimiter(10)  # 10 calls/sec
            >>> await limiter.acquire()
            >>> # Make API call
        """
        import asyncio
        import time
        
        now = time.time()
        
        if self.last_call_time is not None:
            elapsed = now - self.last_call_time
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_call_time = time.time()


def mask_token(token: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive token for logging
    
    Args:
        token: Token to mask
        visible_chars: Number of visible characters at the end
        
    Returns:
        str: Masked token
        
    Example:
        >>> mask_token('github_token_abc123', 4)
        '...c123'
    """
    if len(token) <= visible_chars:
        return f"...{token}"
    return f"...{token[-visible_chars:]}"


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes to human-readable format
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        str: Formatted string
        
    Example:
        >>> format_bytes(1024)
        '1.0 KB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


if __name__ == '__main__':
    # Test examples
    print("Testing RepositoryParser:")
    print(RepositoryParser.parse_repo_path('https://github.com/sileade/repo'))
    print(RepositoryParser.parse_repo_path('sileade/repo'))
    
    print("\nTesting CommitValidator:")
    print(CommitValidator.validate_commit_sha('abc1234567890'))
    print(CommitValidator.normalize_commit_sha('ABC1234567890'))
    
    print("\nTesting InputSanitizer:")
    print(InputSanitizer.sanitize_repo_path('  sileade/repo  '))
    
    print("\nTesting TextFormatter:")
    print(TextFormatter.format_commit_short_info('abc123def456', 'Fix bug', 'John'))
    print(TextFormatter.format_verification_status('approved'))
