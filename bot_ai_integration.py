#!/usr/bin/env python3
"""
Bot AI Integration
Код для интеграции AI анализа в bot.py

Этот модуль необходимо импортировать в bot.py и использовать в функции handle_commit_input()
"""

import logging
from typing import Optional

from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class BotAIIntegration:
    """
    Helper class for AI integration in bot
    """
    
    def __init__(self):
        """
        Initialize AI integration
        """
        self.ai: Optional[AIAnalyzer] = None
        self.enabled = False
        self._init_ai()
    
    def _init_ai(self) -> None:
        """
        Initialize AI analyzer (gracefully handles missing API key)
        """
        try:
            self.ai = AIAnalyzer()
            self.enabled = True
            logger.info("🤖 AI analysis enabled")
        except ImportError:
            logger.warning("⚠️ OpenAI library not installed. AI analysis disabled.")
            self.enabled = False
        except ValueError as e:
            logger.warning(f"⚠️ AI analysis disabled: {e}")
            self.enabled = False
        except Exception as e:
            logger.warning(f"⚠️ Unexpected error initializing AI: {e}")
            self.enabled = False
    
    async def get_ai_analysis_text(self, diff: str, commit_message: str) -> Optional[str]:
        """
        Get formatted AI analysis text
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            
        Returns:
            Formatted analysis text or None
        """
        if not self.enabled or not self.ai:
            return None
        
        try:
            analysis = await self.ai.analyze_diff(diff, commit_message)
            
            if not analysis:
                return None
            
            # Format analysis for Telegram
            text = (
                f"\n\n🤖 *AI Analysis:*\n\n"
                f"🆕 *Summary:* {analysis['summary']}\n"
            )
            
            if analysis.get('impact'):
                text += f"✏️ *Impact:* {analysis['impact']}\n"
            
            if analysis.get('strengths'):
                text += f"✅ *Strengths:* {analysis['strengths']}\n"
            
            if analysis.get('concerns'):
                text += f"⚠️ *Concerns:* {analysis['concerns']}\n"
            
            if analysis.get('recommendation'):
                text += f"👩\u200d💻 *Review:* {analysis['recommendation']}"
            
            return text
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return None
    
    async def get_security_analysis_text(self, diff: str) -> Optional[str]:
        """
        Get formatted security analysis text
        
        Args:
            diff: Patch/diff content
            
        Returns:
            Formatted security analysis or None
        """
        if not self.enabled or not self.ai:
            return None
        
        try:
            analysis = await self.ai.analyze_security(diff)
            
            if not analysis:
                return None
            
            return f"\n\n🔐 *Security Analysis:*\n{analysis['security_analysis']}"
            
        except Exception as e:
            logger.error(f"Error getting security analysis: {e}")
            return None
    
    async def get_quality_score_text(self, diff: str, commit_message: str) -> Optional[str]:
        """
        Get formatted quality score text
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            
        Returns:
            Formatted quality score or None
        """
        if not self.enabled or not self.ai:
            return None
        
        try:
            quality = await self.ai.get_commit_quality_score(diff, commit_message)
            
            if not quality:
                return None
            
            score = quality.get('score')
            if score:
                # Visual score representation
                filled = "⭐" * min(score, 10)
                empty = "☆" * (10 - min(score, 10))
                score_bar = f"[{filled}{empty}] {score}/10"
                return f"\n\n🎯 *Quality Score:* {score_bar}\n{quality['analysis']}"
            else:
                return f"\n\n🎯 *Quality Analysis:*\n{quality['analysis']}"
            
        except Exception as e:
            logger.error(f"Error getting quality score: {e}")
            return None


# Example usage in bot.py:

# In main() function, initialize AI integration:
# ai_integration = BotAIIntegration()

# In handle_commit_input() function, after displaying commit details:
# if github_service and ai_integration.enabled:
#     diff = await github_service.get_commit_diff(repo, commit_sha)
#     if diff:
#         ai_text = await ai_integration.get_ai_analysis_text(diff, commit_message)
#         if ai_text:
#             commit_details += ai_text

# For security-conscious users, optionally add:
# if ai_integration.enabled:
#     security_text = await ai_integration.get_security_analysis_text(diff)
#     if security_text:
#         commit_details += security_text

# For quality metrics:
# if ai_integration.enabled:
#     quality_text = await ai_integration.get_quality_score_text(diff, commit_message)
#     if quality_text:
#         commit_details += quality_text
