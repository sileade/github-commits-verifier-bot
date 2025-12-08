#!/usr/bin/env python3
"""
Database Module
Управление хранилищем данных проверок комитов (PostgreSQL)
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

try:
    import asyncpg
except ImportError:
    asyncpg = None

logger = logging.getLogger(__name__)


class Database:
    """
    PostgreSQL database for storing verification records
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database
        
        Args:
            db_url: PostgreSQL connection URL
                   Default: postgresql://user:password@localhost:5432/github_verifier
                   Can be set via DATABASE_URL environment variable
        """
        if db_url is None:
            db_url = os.getenv(
                'DATABASE_URL',
                'postgresql://user:password@localhost:5432/github_verifier'
            )
        
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
        
        if asyncpg is None:
            raise ImportError(
                "asyncpg is required for PostgreSQL support. "
                "Install it with: pip install asyncpg"
            )
    
    async def init(self) -> None:
        """
        Initialize connection pool and create tables
        """
        try:
            self.pool = await asyncpg.create_pool(self.db_url)
            logger.info("Connected to PostgreSQL")
            await self._init_tables()
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise
    
    async def close(self) -> None:
        """
        Close connection pool
        """
        if self.pool:
            await self.pool.close()
            logger.info("Closed PostgreSQL connection pool")
    
    async def _init_tables(self) -> None:
        """
        Create tables if they don't exist
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            try:
                # Users table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Verifications table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS verifications (
                        id BIGSERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                        repo TEXT NOT NULL,
                        commit_sha TEXT NOT NULL,
                        status TEXT NOT NULL CHECK (status IN ('approved', 'rejected')),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_verifications_user_id 
                    ON verifications(user_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_verifications_commit_sha 
                    ON verifications(commit_sha)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_verifications_created_at 
                    ON verifications(created_at DESC)
                """)
                
                logger.info("Database tables initialized successfully")
            
            except asyncpg.PostgresError as e:
                logger.error(f"Error initializing tables: {e}")
                raise
    
    async def add_user(self, user_id: int, username: str) -> bool:
        """
        Add or update user
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            
        Returns:
            True if successful
        """
        if not self.pool:
            logger.error("Database pool not initialized")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE
                    SET username = EXCLUDED.username
                """, user_id, username)
            
            return True
        
        except asyncpg.PostgresError as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    async def add_verification(
        self,
        user_id: int,
        repo: str,
        commit_sha: str,
        status: str
    ) -> bool:
        """
        Add verification record
        
        Args:
            user_id: Telegram user ID
            repo: Repository path
            commit_sha: Commit SHA
            status: Verification status (approved/rejected)
            
        Returns:
            True if successful
        """
        if not self.pool:
            logger.error("Database pool not initialized")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO verifications (user_id, repo, commit_sha, status)
                    VALUES ($1, $2, $3, $4)
                """, user_id, repo, commit_sha, status)
            
            logger.info(f"Verification recorded: {repo} {commit_sha[:8]} - {status}")
            return True
        
        except asyncpg.PostgresError as e:
            logger.error(f"Error adding verification: {e}")
            return False
    
    async def get_user_history(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user verification history
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of records
            
        Returns:
            List of verification records
        """
        if not self.pool:
            logger.error("Database pool not initialized")
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT repo, commit_sha, status, created_at
                    FROM verifications
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, user_id, limit)
            
            return [dict(row) for row in rows]
        
        except asyncpg.PostgresError as e:
            logger.error(f"Error fetching history: {e}")
            return []
    
    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get user verification statistics
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with statistics
        """
        if not self.pool:
            logger.error("Database pool not initialized")
            return {'total': 0, 'approved': 0, 'rejected': 0}
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM verifications
                    WHERE user_id = $1
                    GROUP BY status
                """, user_id)
            
            stats = {
                'total': 0,
                'approved': 0,
                'rejected': 0,
            }
            
            for row in rows:
                stats[row['status']] = row['count']
                stats['total'] += row['count']
            
            return stats
        
        except asyncpg.PostgresError as e:
            logger.error(f"Error fetching statistics: {e}")
            return {'total': 0, 'approved': 0, 'rejected': 0}
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global statistics across all users
        
        Returns:
            Dictionary with global statistics
        """
        if not self.pool:
            logger.error("Database pool not initialized")
            return {}
        
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(*) as total_verifications,
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
                    FROM verifications
                """)
            
            return dict(stats) if stats else {}
        
        except asyncpg.PostgresError as e:
            logger.error(f"Error fetching global stats: {e}")
            return {}
