#!/usr/bin/env python3
"""
AI Analyzer Service
Анализ изменений с помощью OpenAI GPT
"""

import logging
from typing import Optional, Dict, Any
import os

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI-powered commit analysis service
    Анализирует дифф коммита и генерирует краткую сводку
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        if AsyncOpenAI is None:
            raise ImportError(
                "openai library is required for AI analysis. "
                "Install it with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it to enable AI analysis."
            )
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
        self.max_diff_size = 8000  # Max chars for diff analysis
    
    async def analyze_diff(self, diff: str, commit_message: str) -> Optional[Dict[str, Any]]:
        """
        Analyze commit diff and generate summary
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            # Truncate diff if too large
            if len(diff) > self.max_diff_size:
                diff_truncated = diff[:self.max_diff_size] + "\n... (truncated)"
            else:
                diff_truncated = diff
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(diff_truncated, commit_message)
            
            # Call OpenAI API
            logger.info("Analyzing commit with AI...")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code review expert. Analyze code changes and provide concise summaries in Russian. Be brief and technical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent analysis
                max_tokens=500,
                timeout=30.0
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            
            # Parse structured analysis
            result = self._parse_analysis(analysis_text)
            logger.info("AI analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during AI analysis: {e}")
            return None
    
    def _create_analysis_prompt(self, diff: str, commit_message: str) -> str:
        """
        Create analysis prompt for OpenAI
        """
        return f"""Analyze this code change and provide a brief summary in Russian.

Commit Message:
{commit_message}

Code Diff:
{diff}

Provide analysis in this format:
🆕 SUMMARY: One sentence summary of what changed
✏️ IMPACT: 1-2 lines about the impact
✅ STRENGTHS: 1-2 positive aspects of this change
⚠️ CONCERNS: Potential issues (if any), or "None" if code looks good
👩\u200d💻 REVIEW: Quick recommendation (APPROVE/REVIEW/REJECT)

Keep it concise and technical."""
    
    def _parse_analysis(self, text: str) -> Dict[str, Any]:
        """
        Parse AI analysis response
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
            
            if line.startswith('🆕 SUMMARY:'):
                result['summary'] = line.replace('🆕 SUMMARY:', '').strip()
                current_section = 'summary'
            elif line.startswith('✏️ IMPACT:'):
                result['impact'] = line.replace('✏️ IMPACT:', '').strip()
                current_section = 'impact'
            elif line.startswith('✅ STRENGTHS:'):
                result['strengths'] = line.replace('✅ STRENGTHS:', '').strip()
                current_section = 'strengths'
            elif line.startswith('⚠️ CONCERNS:'):
                result['concerns'] = line.replace('⚠️ CONCERNS:', '').strip()
                current_section = 'concerns'
            elif line.startswith('👩\u200d💻 REVIEW:'):
                result['recommendation'] = line.replace('👩\u200d💻 REVIEW:', '').strip()
                current_section = 'recommendation'
            elif current_section and line:
                # Append to current section
                if result[current_section]:
                    result[current_section] += ' ' + line
                else:
                    result[current_section] = line
        
        return result
    
    async def analyze_security(self, diff: str) -> Optional[Dict[str, Any]]:
        """
        Security-focused analysis
        
        Args:
            diff: Patch/diff content
            
        Returns:
            Dictionary with security analysis or None
        """
        try:
            if len(diff) > self.max_diff_size:
                diff = diff[:self.max_diff_size] + "\n... (truncated)"
            
            prompt = f"""Analyze this code change for security issues. Respond in Russian.

Code Diff:
{diff}

Provide:
1. 🔐 SECURITY: Any security vulnerabilities (or "None found")
2. 🔍 RECOMMENDATIONS: Security best practices that should be applied
3. ⚠️ RISK LEVEL: LOW/MEDIUM/HIGH

Be concise and specific."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security expert. Analyze code for vulnerabilities and provide security recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300,
                timeout=30.0
            )
            
            return {
                'security_analysis': response.choices[0].message.content,
                'raw': response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error during security analysis: {e}")
            return None
    
    async def get_commit_quality_score(self, diff: str, commit_message: str) -> Optional[Dict[str, Any]]:
        """
        Get commit quality score (1-10)
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            
        Returns:
            Dictionary with score and explanation
        """
        try:
            if len(diff) > self.max_diff_size:
                diff = diff[:self.max_diff_size] + "\n... (truncated)"
            
            prompt = f"""Rate the quality of this commit (1-10). Respond in Russian.

Commit Message:
{commit_message}

Code Diff:
{diff}

Provide:
1. 🎯 SCORE: Quality score 1-10
2. 📊 BREAKDOWN:
   - Code quality: 1-10
   - Test coverage: 1-10
   - Commit message: 1-10
3. 🚀 OVERALL: Brief assessment
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code quality expert. Rate commits on quality criteria."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300,
                timeout=30.0
            )
            
            analysis = response.choices[0].message.content
            
            # Try to extract score
            score = None
            for line in analysis.split('\n'):
                if 'SCORE:' in line or 'Score:' in line or 'ОЦЕНКА:' in line:
                    # Try to find number
                    for word in line.split():
                        if word.isdigit():
                            score = int(word)
                            break
            
            return {
                'analysis': analysis,
                'score': score,
                'raw': analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting quality score: {e}")
            return None
