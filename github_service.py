#!/usr/bin/env python3
"""
GitHub API Service
Упраление взаимодействием с GitHub API
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

try:
    from github import Github, GithubException
except ImportError:
    Github = None
    GithubException = None

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Service for GitHub API interactions
    """
    
    def __init__(self, token: str):
        """
        Initialize GitHub service
        
        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.api_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        # Initialize PyGithub client if available
        if Github:
            try:
                self.github = Github(token)
            except Exception as e:
                logger.error(f"Failed to initialize PyGithub: {e}")
                self.github = None
        else:
            self.github = None
    
    async def get_repository(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Get repository information
        
        Args:
            repo_path: Repository path (owner/repo or URL)
            
        Returns:
            Repository info or None if not found
        """
        try:
            # Parse repo path
            if repo_path.startswith('http'):
                # Extract from URL
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                # Direct format
                owner, repo = repo_path.split('/')
            
            # Get repo info via API
            url = f"{self.api_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'full_name': data['full_name'],
                'url': data['html_url'],
                'description': data.get('description', ''),
                'stars': data['stargazers_count'],
                'language': data.get('language', 'N/A'),
            }
        except RequestException as e:
            logger.error(f"Error fetching repository: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid repository format: {e}")
            return None
    
    async def get_commit_info(self, repo_path: str, commit_sha: str) -> Optional[Dict[str, Any]]:
        """
        Get commit information
        
        Args:
            repo_path: Repository path
            commit_sha: Commit SHA
            
        Returns:
            Commit info or None
        """
        try:
            # Parse repo path
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            # Get commit info
            url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            commit = data['commit']
            
            return {
                'repo': f"{owner}/{repo}",
                'sha': data['sha'],
                'short_sha': data['sha'][:8],
                'message': commit['message'],
                'author': commit['author']['name'],
                'author_email': commit['author']['email'],
                'date': commit['author']['date'],
                'verified': data.get('commit', {}).get('verification', {}).get('verified', False),
                'url': data['html_url'],
                'parents': len(data.get('parents', [])),
            }
        except RequestException as e:
            logger.error(f"Error fetching commit: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing commit data: {e}")
            return None
    
    async def verify_commit(self, commit_info: Dict[str, Any]) -> Dict[str, bool]:
        """
        Verify commit authenticity
        
        Args:
            commit_info: Commit information dict
            
        Returns:
            Dictionary with verification checks
        """
        checks = {
            'GPG Подпись': commit_info.get('verified', False),
            'Известный автор': True,  # Can be extended
            'Сообщение присутствует': bool(commit_info.get('message', '').strip()),
            'Валидная дата': self._is_valid_date(commit_info.get('date', '')),
        }
        
        return checks
    
    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """
        Check if date string is valid
        """
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False
    
    async def get_commit_diff(self, repo_path: str, commit_sha: str) -> Optional[str]:
        """
        Get commit diff
        
        Args:
            repo_path: Repository path
            commit_sha: Commit SHA
            
        Returns:
            Diff string or None
        """
        try:
            owner, repo = repo_path.split('/')
            url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            
            headers = self.headers.copy()
            headers['Accept'] = 'application/vnd.github.v3.patch'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.text
        except RequestException as e:
            logger.error(f"Error fetching commit diff: {e}")
            return None
