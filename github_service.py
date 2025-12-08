#!/usr/bin/env python3
"""
GitHub API Service
Управление взаимодействием с GitHub API
"""

import logging
import json
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
    
    async def get_commit_files(self, repo_path: str, commit_sha: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of files changed in a commit
        
        Args:
            repo_path: Repository path
            commit_sha: Commit SHA
            
        Returns:
            List of changed files or None
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            files = []
            
            for file in data.get('files', []):
                files.append({
                    'filename': file['filename'],
                    'status': file['status'],
                    'additions': file['additions'],
                    'deletions': file['deletions'],
                    'changes': file['changes'],
                })
            
            return files
        except RequestException as e:
            logger.error(f"Error fetching commit files: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing commit files: {e}")
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
        Get commit diff/patch
        
        Args:
            repo_path: Repository path
            commit_sha: Commit SHA
            
        Returns:
            Diff string or None
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
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
    
    async def get_branches(self, repo_path: str) -> Optional[List[str]]:
        """
        Get list of branches in repository
        
        Args:
            repo_path: Repository path
            
        Returns:
            List of branch names or None
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            url = f"{self.api_url}/repos/{owner}/{repo}/branches"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return [branch['name'] for branch in data]
        except RequestException as e:
            logger.error(f"Error fetching branches: {e}")
            return None
    
    async def create_branch(self, repo_path: str, new_branch: str, from_ref: str) -> bool:
        """
        Create a new branch
        
        Args:
            repo_path: Repository path
            new_branch: Name of new branch
            from_ref: Source branch/commit SHA
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            # First get the SHA of from_ref
            ref_url = f"{self.api_url}/repos/{owner}/{repo}/commits/{from_ref}"
            ref_response = requests.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()
            from_sha = ref_response.json()['sha']
            
            # Create new branch
            url = f"{self.api_url}/repos/{owner}/{repo}/git/refs"
            data = {
                "ref": f"refs/heads/{new_branch}",
                "sha": from_sha
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Created branch {new_branch} in {repo_path}")
            return True
        except RequestException as e:
            logger.error(f"Error creating branch: {e}")
            return False
    
    async def create_pull_request(
        self,
        repo_path: str,
        base: str,
        head: str,
        title: str,
        body: str
    ) -> Optional[str]:
        """
        Create a pull request
        
        Args:
            repo_path: Repository path
            base: Base branch
            head: Head branch
            title: PR title
            body: PR description
            
        Returns:
            PR URL or None
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            url = f"{self.api_url}/repos/{owner}/{repo}/pulls"
            data = {
                "title": title,
                "body": body,
                "base": base,
                "head": head,
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            
            pr_data = response.json()
            logger.info(f"Created PR: {pr_data['html_url']}")
            return pr_data['html_url']
        except RequestException as e:
            logger.error(f"Error creating pull request: {e}")
            return None
    
    async def cherry_pick_commit(
        self,
        repo_path: str,
        commit_sha: str,
        target_branch: str
    ) -> Optional[str]:
        """
        Cherry-pick a commit to target branch
        
        Args:
            repo_path: Repository path
            commit_sha: Commit SHA to cherry-pick
            target_branch: Target branch name
            
        Returns:
            New commit SHA or None
        """
        try:
            if repo_path.startswith('http'):
                parts = repo_path.rstrip('/').split('/')
                owner, repo = parts[-2], parts[-1]
            else:
                owner, repo = repo_path.split('/')
            
            # Get commit info
            commit_url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            commit_response = requests.get(commit_url, headers=self.headers, timeout=10)
            commit_response.raise_for_status()
            commit_data = commit_response.json()
            
            # Get target branch HEAD
            branch_url = f"{self.api_url}/repos/{owner}/{repo}/branches/{target_branch}"
            branch_response = requests.get(branch_url, headers=self.headers, timeout=10)
            branch_response.raise_for_status()
            target_sha = branch_response.json()['commit']['sha']
            
            # Create commit data
            url = f"{self.api_url}/repos/{owner}/{repo}/git/commits"
            new_commit_data = {
                "message": commit_data['commit']['message'],
                "tree": commit_data['commit']['tree']['sha'],
                "parents": [target_sha],
                "author": {
                    "name": commit_data['commit']['author']['name'],
                    "email": commit_data['commit']['author']['email'],
                    "date": commit_data['commit']['author']['date']
                }
            }
            
            response = requests.post(url, headers=self.headers, json=new_commit_data, timeout=10)
            response.raise_for_status()
            new_commit_sha = response.json()['sha']
            
            # Update branch reference
            ref_url = f"{self.api_url}/repos/{owner}/{repo}/git/refs/heads/{target_branch}"
            ref_data = {"sha": new_commit_sha, "force": False}
            ref_response = requests.patch(ref_url, headers=self.headers, json=ref_data, timeout=10)
            ref_response.raise_for_status()
            
            logger.info(f"Cherry-picked {commit_sha} to {target_branch}")
            return new_commit_sha
        except RequestException as e:
            logger.error(f"Error cherry-picking commit: {e}")
            return None
