#!/usr/bin/env python3
"""
Local LLM Analyzer Service
Локальный анализ изменений с помощью Ollama и локальных моделей

Поддерживаемые модели:
- mistral (7B, очень быстрая, хорошее качество)
- llama2 (7B/13B, классическая модель)
- neural-chat (7B, оптимизирована для диалогов)
- dolphin-mixtral (быстрая и умная)
"""

import logging
from typing import Optional, Dict, Any
import asyncio
import aiohttp
import os

logger = logging.getLogger(__name__)


class LocalAnalyzer:
    """
    Local LLM-powered commit analysis using Ollama
    """
    
    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 60
    ):
        """
        Initialize Local Analyzer with Ollama
        
        Args:
            ollama_host: URL to Ollama server (default: localhost:11434)
            model: Model name to use (mistral, llama2, neural-chat, dolphin-mixtral)
            timeout: Request timeout in seconds
        """
        self.ollama_host = os.getenv('OLLAMA_HOST', ollama_host)
        self.model = os.getenv('LOCAL_MODEL', model)
        self.timeout = timeout
        self.api_url = f"{self.ollama_host}/api/generate"
        self.available_models = [
            "mistral",
            "llama2",
            "neural-chat",
            "dolphin-mixtral",
            "openchat",
            "orca-mini",
            "zephyr"
        ]
        
        logger.info("🤖 Local Analyzer initialized: %s @ %s", self.model, self.ollama_host)
    
    async def check_ollama_health(self) -> bool:
        """
        Check if Ollama server is running and model is available
        
        Returns:
            True if ready, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama is running
                async with session.get(
                    f"{self.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status != 200:
                        logger.warning("Ollama health check failed: %s", resp.status)
                        return False
                    
                    data = await resp.json()
                    models = [m.get('name', '').split(':')[0] for m in data.get('models', [])]
                    
                    if self.model in models or f"{self.model}:latest" in [m.get('name') for m in data.get('models', [])]:
                        logger.info("✓ Model '%s' is available", self.model)
                        return True
                    else:
                        logger.warning(
                            "Model '%s' not found. Available: %s\n"
                            "Install with: ollama pull %s",
                            self.model, models, self.model
                        )
                        return False
        except Exception as e:
            logger.warning("Ollama health check error: %s", e)
            return False
    
    async def analyze_diff(self, diff: str, commit_message: str) -> Optional[Dict[str, Any]]:
        """
        Analyze commit diff with local LLM
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            # Truncate if too large
            max_diff = 4000  # Меньше для локальных моделей
            if len(diff) > max_diff:
                diff = diff[:max_diff] + "\n... (truncated)"
            
            prompt = self._create_analysis_prompt(diff, commit_message)
            
            logger.info("Analyzing commit with %s...", self.model)
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 400  # Ограничиваем размер ответа
                }
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        logger.error("Ollama error: %s", resp.status)
                        return None
                    
                    data = await resp.json()
                    response_text = data.get('response', '')
                    
                    if not response_text:
                        logger.error("Empty response from Ollama")
                        return None
                    
                    result = self._parse_analysis(response_text)
                    logger.info("Local analysis completed successfully")
                    return result
        
        except asyncio.TimeoutError:
            logger.error("Ollama request timeout (>%ss). Model might be slow or busy.", self.timeout)
            return None
        except Exception as e:
            logger.error("Error during local analysis: %s", e)
            return None
    
    def _create_analysis_prompt(self, diff: str, commit_message: str) -> str:
        """
        Create analysis prompt optimized for local models
        """
        return f"""Analyze this code change. Keep response brief and in Russian.

Commit: {commit_message}

Code Diff:
{diff}

Provide analysis in this format:
🔍 SUMMARY: One sentence summary
✏️ IMPACT: 1 line about impact
✅ STRENGTHS: 1 line positive aspects
⚠️ CONCERNS: Issues or "None"
👨‍💻 REVIEW: APPROVE/REVIEW/REJECT with reason

Be concise and technical."""
    
    def _parse_analysis(self, text: str) -> Dict[str, Any]:
        """
        Parse local LLM analysis response
        """
        lines = text.split('\n')
        result = {
            'summary': '',
            'impact': '',
            'strengths': '',
            'concerns': '',
            'recommendation': '',
            'raw': text
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('🔍') or line.startswith('SUMMARY:'):
                result['summary'] = line.replace('🔍', '').replace('SUMMARY:', '').strip()
                current_section = 'summary'
            elif line.startswith('✏️') or line.startswith('IMPACT:'):
                result['impact'] = line.replace('✏️', '').replace('IMPACT:', '').strip()
                current_section = 'impact'
            elif line.startswith('✅') or line.startswith('STRENGTHS:'):
                result['strengths'] = line.replace('✅', '').replace('STRENGTHS:', '').strip()
                current_section = 'strengths'
            elif line.startswith('⚠️') or line.startswith('CONCERNS:'):
                result['concerns'] = line.replace('⚠️', '').replace('CONCERNS:', '').strip()
                current_section = 'concerns'
            elif line.startswith('👨‍💻') or line.startswith('REVIEW:'):
                result['recommendation'] = line.replace('👨‍💻', '').replace('REVIEW:', '').strip()
                current_section = 'recommendation'
            elif current_section and line:
                if result[current_section]:
                    result[current_section] += ' ' + line
                else:
                    result[current_section] = line
        
        return result
    
    async def analyze_security(self, diff: str) -> Optional[Dict[str, Any]]:
        """
        Security-focused analysis with local LLM
        """
        try:
            max_diff = 4000
            if len(diff) > max_diff:
                diff = diff[:max_diff] + "\n... (truncated)"
            
            prompt = f"""Analyze this code for security issues. Response in Russian, be brief.

Code Diff:
{diff}

Provide:
1. 🔐 SECURITY: Any vulnerabilities (or "None found")
2. 🔍 RECOMMENDATIONS: 1-2 security best practices
3. ⚠️ RISK LEVEL: LOW/MEDIUM/HIGH

Be concise."""
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "num_predict": 250
                }
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    return {
                        'security_analysis': data.get('response', ''),
                        'raw': data.get('response', '')
                    }
        
        except Exception as e:
            logger.error("Error during security analysis: %s", e)
            return None
    
    async def get_commit_quality_score(self, diff: str, commit_message: str) -> Optional[Dict[str, Any]]:
        """
        Get commit quality score with local LLM
        """
        try:
            max_diff = 4000
            if len(diff) > max_diff:
                diff = diff[:max_diff] + "\n... (truncated)"
            
            prompt = f"""Rate commit quality (1-10). Response in Russian, be brief.

Commit: {commit_message}

Code Diff:
{diff}

Provide:
1. 🎯 SCORE: Quality score 1-10
2. 📊 ASSESSMENT: 1-2 line assessment

Be concise."""
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "num_predict": 200
                }
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    analysis = data.get('response', '')
                    
                    # Try to extract score
                    score = None
                    for line in analysis.split('\n'):
                        for word in line.split():
                            if word.isdigit():
                                s = int(word)
                                if 1 <= s <= 10:
                                    score = s
                                    break
                        if score:
                            break
                    
                    return {
                        'analysis': analysis,
                        'score': score,
                        'raw': analysis
                    }
        
        except Exception as e:
            logger.error("Error getting quality score: %s", e)
            return None
