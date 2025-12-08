#!/usr/bin/env python3
"""
Hybrid AI Manager
Менеджер для выбора между OpenAI и локальным LLM
Можно использовать обе модели одновременно
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AnalysisMode(Enum):
    """Analysis mode selection"""
    OPENAI = "openai"      # Use OpenAI GPT-3.5
    LOCAL = "local"        # Use local Ollama
    AUTO = "auto"          # Auto-select (local if available, else OpenAI)
    HYBRID = "hybrid"      # Use both for comparison


class HybridAIManager:
    """
    Manages both OpenAI and Local LLM for commit analysis
    """
    
    def __init__(self, openai_analyzer=None, local_analyzer=None):
        """
        Initialize with both analyzers
        
        Args:
            openai_analyzer: AIAnalyzer instance (optional)
            local_analyzer: LocalAnalyzer instance (optional)
        """
        self.openai = openai_analyzer
        self.local = local_analyzer
        self.mode = self._determine_mode()
    
    def _determine_mode(self) -> AnalysisMode:
        """
        Determine best analysis mode based on available analyzers
        """
        if self.local and self.openai:
            logger.info("🚀 Both analyzers available - using AUTO mode")
            return AnalysisMode.AUTO
        elif self.local:
            logger.info("🔗 Local analyzer available - using LOCAL mode")
            return AnalysisMode.LOCAL
        elif self.openai:
            logger.info("☁️ OpenAI analyzer available - using OPENAI mode")
            return AnalysisMode.OPENAI
        else:
            logger.warning("⚠️ No analyzers available")
            return AnalysisMode.AUTO
    
    async def analyze_diff(
        self,
        diff: str,
        commit_message: str,
        mode: Optional[AnalysisMode] = None,
        prefer_fast: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze diff with best available analyzer
        
        Args:
            diff: Patch/diff content
            commit_message: Commit message
            mode: Override mode (AUTO, LOCAL, OPENAI)
            prefer_fast: Prefer faster model (local) if available
            
        Returns:
            Analysis result with metadata
        """
        mode = mode or self.mode
        
        if mode == AnalysisMode.AUTO:
            # Auto-select: local if available and fast, else OpenAI
            if prefer_fast and self.local:
                return await self._analyze_with_local(diff, commit_message, method='analyze_diff')
            elif self.openai:
                return await self._analyze_with_openai(diff, commit_message, method='analyze_diff')
            elif self.local:
                return await self._analyze_with_local(diff, commit_message, method='analyze_diff')
            else:
                return None
        
        elif mode == AnalysisMode.LOCAL:
            if not self.local:
                logger.warning("Local analyzer not available")
                return None
            return await self._analyze_with_local(diff, commit_message, method='analyze_diff')
        
        elif mode == AnalysisMode.OPENAI:
            if not self.openai:
                logger.warning("OpenAI analyzer not available")
                return None
            return await self._analyze_with_openai(diff, commit_message, method='analyze_diff')
        
        elif mode == AnalysisMode.HYBRID:
            # Run both and combine results
            return await self._analyze_hybrid(diff, commit_message)
        
        return None
    
    async def _analyze_with_local(
        self,
        diff: str,
        commit_message: str,
        method: str = 'analyze_diff'
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze using local LLM
        """
        try:
            logger.info("Using local LLM for analysis...")
            
            if method == 'analyze_diff':
                result = await self.local.analyze_diff(diff, commit_message)
            elif method == 'security':
                result = await self.local.analyze_security(diff)
            elif method == 'quality':
                result = await self.local.get_commit_quality_score(diff, commit_message)
            else:
                return None
            
            if result:
                result['source'] = 'local'
                result['model'] = self.local.model
            
            return result
        
        except Exception as e:
            logger.error(f"Local analysis failed: {e}")
            return None
    
    async def _analyze_with_openai(
        self,
        diff: str,
        commit_message: str,
        method: str = 'analyze_diff'
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze using OpenAI API
        """
        try:
            logger.info("Using OpenAI for analysis...")
            
            if method == 'analyze_diff':
                result = await self.openai.analyze_diff(diff, commit_message)
            elif method == 'security':
                result = await self.openai.analyze_security(diff)
            elif method == 'quality':
                result = await self.openai.get_commit_quality_score(diff, commit_message)
            else:
                return None
            
            if result:
                result['source'] = 'openai'
                result['model'] = self.openai.model
            
            return result
        
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return None
    
    async def _analyze_hybrid(self, diff: str, commit_message: str) -> Optional[Dict[str, Any]]:
        """
        Run both analyzers and combine results
        """
        try:
            logger.info("Running hybrid analysis (both models)...")
            
            local_result = None
            openai_result = None
            
            # Run in parallel if both available
            import asyncio
            
            tasks = []
            if self.local:
                tasks.append(self.local.analyze_diff(diff, commit_message))
            if self.openai:
                tasks.append(self.openai.analyze_diff(diff, commit_message))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            if self.local:
                local_result = results[0]
            if self.openai:
                openai_result = results[1 if self.local else 0]
            
            # Combine results
            combined = {
                'source': 'hybrid',
                'local': local_result,
                'openai': openai_result,
                'summary': local_result.get('summary') if local_result else openai_result.get('summary'),
                'raw': {
                    'local': local_result.get('raw') if local_result else None,
                    'openai': openai_result.get('raw') if openai_result else None
                }
            }
            
            return combined
        
        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            return None
    
    async def analyze_security(
        self,
        diff: str,
        mode: Optional[AnalysisMode] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Security analysis with auto-selection
        """
        mode = mode or self.mode
        
        if mode == AnalysisMode.LOCAL or (mode == AnalysisMode.AUTO and self.local):
            return await self._analyze_with_local(diff, method='security')
        elif mode == AnalysisMode.OPENAI or (mode == AnalysisMode.AUTO and self.openai):
            return await self._analyze_with_openai(diff, method='security')
        
        return None
    
    async def get_quality_score(
        self,
        diff: str,
        commit_message: str,
        mode: Optional[AnalysisMode] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Quality score with auto-selection
        """
        mode = mode or self.mode
        
        if mode == AnalysisMode.LOCAL or (mode == AnalysisMode.AUTO and self.local):
            return await self._analyze_with_local(diff, commit_message, method='quality')
        elif mode == AnalysisMode.OPENAI or (mode == AnalysisMode.AUTO and self.openai):
            return await self._analyze_with_openai(diff, commit_message, method='quality')
        
        return None
    
    def set_mode(self, mode: AnalysisMode) -> None:
        """
        Override analysis mode
        """
        logger.info(f"Setting analysis mode to: {mode.value}")
        self.mode = mode
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of both analyzers
        """
        return {
            'mode': self.mode.value,
            'openai_available': bool(self.openai),
            'local_available': bool(self.local),
            'local_model': self.local.model if self.local else None,
            'local_host': self.local.ollama_host if self.local else None
        }
