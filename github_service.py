#!/usr/bin/env python3
"""
GitHub API Service
Управление взаимодействием с GitHub API
"""

import logging
import json
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
import asyncio

import aiohttp
from aiohttp import ClientSession, ClientResponseError

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Service for GitHub API interactions
    """
    
    def __init__(self, token: str, ollama_host: Optional[str] = None):
        """
        Initialize GitHub service
        
        Args:
            token: GitHub personal access token
            ollama_host: Ollama API endpoint (optional)
        """
        self.token = token
        self.api_url = "https://api.github.com"
        self.ollama_host = ollama_host or "http://localhost:11434"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.session: Optional[ClientSession] = None
        
    async def init_session(self):
        """Initialize aiohttp client session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        """Close aiohttp client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def _parse_repo_path(self, repo_path: str) -> Tuple[str, str]:
        """Helper to parse repository path from URL or owner/repo format."""
        if repo_path.startswith('http'):
            # Extract from URL
            parts = repo_path.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        else:
            # Direct format
            owner, repo = repo_path.split('/')
        return owner, repo

    async def _fetch(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """Generic asynchronous fetcher for GitHub API."""
        await self.init_session()
        try:
            async with self.session.request(method, url, params=params, json=json_data, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as e:
            logger.error("GitHub API error (%s) for %s: %s", e.status, url, e.message)
            return None
        except aiohttp.ClientError as e:
            logger.error("Network error fetching %s: %s", url, e)
            return None
        except (asyncio.TimeoutError, json.JSONDecodeError) as e:
            logger.error("Unexpected error fetching %s: %s", url, e)
            return None

    async def get_repository(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Get repository information."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}"
            data = await self._fetch(url)
            
            if data:
                return {
                    'full_name': data['full_name'],
                    'url': data['html_url'],
                    'description': data.get('description', ''),
                    'stars': data['stargazers_count'],
                    'language': data.get('language', 'N/A'),
                }
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def get_user_repositories(self) -> Optional[List[Dict[str, Any]]]:
        """Get all user repositories."""
        url = f"{self.api_url}/user/repos"
        data = await self._fetch(url, params={"per_page": 100})
        
        if data:
            repos = []
            for repo in data:
                repos.append({
                    'full_name': repo['full_name'],
                    'name': repo['name'],
                    'url': repo['html_url'],
                    'description': repo.get('description', ''),
                    'stargazers_count': repo.get('stargazers_count', 0),
                    'language': repo.get('language', 'Unknown'),
                    'private': repo.get('private', False),
                    'html_url': repo['html_url'],
                })
            return repos
        return None

    async def get_last_commit(self, repo_path: str) -> Optional[str]:
        """Get date of last commit."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/commits"
            data = await self._fetch(url, params={"per_page": 1})
            
            if data:
                commit_date = data[0]['commit']['author']['date']
                # Parse and format date
                dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def get_commit_history(self, repo_path: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get commit history for a repository."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/commits"
            per_page = min(limit, 100)
            
            commits = []
            page = 1
            
            while len(commits) < limit:
                data = await self._fetch(url, params={"per_page": per_page, "page": page})
                
                if not data:
                    break
                
                for commit in data:
                    if len(commits) >= limit:
                        break
                    
                    commit_data = commit['commit']
                    commits.append({
                        'sha': commit['sha'],
                        'short_sha': commit['sha'][:8],
                        'message': commit_data['message'],
                        'author': commit_data['author']['name'],
                        'author_email': commit_data['author']['email'],
                        'date': commit_data['author']['date'],
                        'url': commit['html_url'],
                    })
                
                page += 1
            
            return commits
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def analyze_commits_with_ai(
        self,
        repo_path: str,
        commits: List[Dict[str, Any]],
        analysis_type: str = "summary"
    ) -> Optional[str]:
        """Analyze commits using local AI (Ollama/Mistral)."""
        await self.init_session()
        try:
            # Prepare commit data for analysis
            commits_text = "\n\n".join([
                f"Commit: {c['short_sha']}\n"
                f"Author: {c['author']}\n"
                f"Date: {c['date']}\n"
                f"Message: {c['message'][:200]}..."
                for c in commits[:20]
            ])
            
            # Create analysis prompt
            prompts = {
                "summary": f"""Analyze these commits from repository {repo_path}:

{commits_text}

Provide a brief summary of the development progress and key changes.""",
                
                "quality": f"""Analyze code quality based on these commit messages from {repo_path}:

{commits_text}

Assess commit quality, message clarity, and development practices.""",
                
                "security": f"""Analyze security-related commits from {repo_path}:

{commits_text}

Identify any security fixes, vulnerability patches, or security-related changes.""",
                
                "patterns": f"""Analyze development patterns from these commits in {repo_path}:

{commits_text}

Identify development patterns, release cycles, and work patterns.""",
            }
            
            prompt = prompts.get(analysis_type, prompts["summary"])
            
            # Call Ollama API
            url = f"{self.ollama_host}/api/generate"
            json_data = {
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            async with self.session.post(url, json=json_data, timeout=60) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("response", "").strip()
        except ClientResponseError as e:
            logger.error("Ollama API error (%s): %s", e.status, e.message)
            return None
        except aiohttp.ClientError as e:
            logger.error("Network error calling Ollama API: %s", e)
            return None
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError) as e:
            logger.error("Error analyzing commits with AI: %s", e)
            return None

    async def get_commit_info(self, repo_path: str, commit_sha: str) -> Optional[Dict[str, Any]]:
        """Get commit information."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            data = await self._fetch(url)
            
            if data:
                commit_data = data['commit']
                return {
                    'repo': repo_path,
                    'sha': data['sha'],
                    'message': commit_data['message'],
                    'author': commit_data['author']['name'],
                    'author_email': commit_data['author']['email'],
                    'date': datetime.fromisoformat(
                        commit_data['author']['date'].replace('Z', '+00:00')
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    'url': data['html_url'],
                    'verified': data['commit']['verification']['verified'] if 'verification' in data['commit'] else False,
                }
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def get_commit_files(self, repo_path: str, commit_sha: str) -> Optional[List[Dict[str, Any]]]:
        """Get files changed in a commit."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            data = await self._fetch(url)
            
            if data and 'files' in data:
                files = []
                for file in data['files']:
                    files.append({
                        'filename': file['filename'],
                        'status': file['status'],
                        'additions': file['additions'],
                        'deletions': file['deletions'],
                        'changes': file['changes'],
                        'patch': file.get('patch'),
                    })
                return files
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def verify_commit(self, commit_info: Dict[str, Any]) -> Dict[str, bool]:
        """Perform basic commit verification checks."""
        # This is a placeholder for actual verification logic
        checks = {
            "GPG Signature": commit_info.get('verified', False),
            "Valid Author Email": "@users.noreply.github.com" not in commit_info.get('author_email', ''),
            "Message Length": len(commit_info.get('message', '')) > 10,
        }
        return checks

    async def get_branch_sha(self, repo_path: str, branch: str) -> Optional[str]:
        """Get the latest commit SHA for a branch."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/branches/{branch}"
            data = await self._fetch(url)
            
            if data and 'commit' in data:
                return data['commit']['sha']
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def create_branch(self, repo_path: str, new_branch: str, base_sha: str) -> bool:
        """Create a new branch from a base SHA."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/git/refs"
            data = {
                "ref": f"refs/heads/{new_branch}",
                "sha": base_sha,
            }
            
            result = await self._fetch(url, method='POST', json_data=data)
            
            if result:
                logger.info("Created branch %s in %s", new_branch, repo_path)
                return True
            return False
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return False

    async def create_pull_request(
        self,
        repo_path: str,
        base: str,
        head: str,
        title: str,
        body: str
    ) -> Optional[str]:
        """Create a pull request."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            url = f"{self.api_url}/repos/{owner}/{repo}/pulls"
            data = {
                "title": title,
                "body": body,
                "base": base,
                "head": head,
            }
            
            pr_data = await self._fetch(url, method='POST', json_data=data)
            
            if pr_data:
                logger.info("Created PR: %s", pr_data['html_url'])
                return pr_data['html_url']
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None

    async def cherry_pick_commit(
        self,
        repo_path: str,
        commit_sha: str,
        target_branch: str
    ) -> Optional[str]:
        """Cherry-pick a commit to target branch."""
        try:
            owner, repo = self._parse_repo_path(repo_path)
            
            # Get commit info
            commit_url = f"{self.api_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            commit_data = await self._fetch(commit_url)
            if not commit_data:
                return None
            
            # Get target branch HEAD
            branch_url = f"{self.api_url}/repos/{owner}/{repo}/branches/{target_branch}"
            branch_data = await self._fetch(branch_url)
            if not branch_data:
                return None
            target_sha = branch_data['commit']['sha']
            
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
            
            new_commit_result = await self._fetch(url, method='POST', json_data=new_commit_data)
            if not new_commit_result:
                return None
            new_commit_sha = new_commit_result['sha']
            
            # Update branch reference
            ref_url = f"{self.api_url}/repos/{owner}/{repo}/git/refs/heads/{target_branch}"
            ref_data = {"sha": new_commit_sha, "force": False}
            ref_response = await self._fetch(ref_url, method='PATCH', json_data=ref_data)
            
            if ref_response:
                logger.info("Cherry-picked %s to %s", commit_sha, target_branch)
                return new_commit_sha
            return None
        except ValueError as e:
            logger.error("Invalid repository format: %s", e)
            return None
