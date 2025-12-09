#!/usr/bin/env python3
"""
Database Module
Управление хранилищем данных проверок комитов (PostgreSQL)
"""

import logging
import os
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
                   Can be set via DATABASE_URL environment variable
        """
        if asyncpg is None:
            raise ImportError(
                "asyncpg is required for PostgreSQL support. "
                "Install it with: pip install asyncpg"
            )
            
        self.db_url = db_url or os.getenv('DATABASE_URL')
        
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set.")
            
        self.pool: Optional[asyncpg.Pool] = None
    
    async def init(self) -> None:
        """
        Initialize connection pool and create tables
        """
        try:
            self.pool = await asyncpg.create_pool(self.db_url)
            logger.info("Connected to PostgreSQL")
            await self._init_tables()
        except (asyncpg.PostgresError, OSError) as e:
            logger.error("Error connecting to PostgreSQL: %s", e)
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
                logger.error("Error initializing tables: %s", e)
                raise

    async def _execute(self, query: str, *args) -> bool:
        """Helper for executing queries."""
        if not self.pool:
            logger.error("Database pool not initialized")
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
            return True
        except asyncpg.PostgresError as e:
            logger.error("Error executing query: %s", e)
            return False

    async def _fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Helper for fetching records."""
        if not self.pool:
            logger.error("Database pool not initialized")
            return []
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except asyncpg.PostgresError as e:
            logger.error("Error fetching records: %s", e)
            return []

    async def _fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Helper for fetching a single row."""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except asyncpg.PostgresError as e:
            logger.error("Error fetching row: %s", e)
            return None
    
    async def add_user(self, user_id: int, username: str) -> bool:
        """Add or update user."""
        query = """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username
        """
        return await self._execute(query, user_id, username)
    
    async def add_verification(
        self,
        user_id: int,
        repo: str,
        commit_sha: str,
        status: str
    ) -> bool:
        """Add verification record."""
        query = """
            INSERT INTO verifications (user_id, repo, commit_sha, status)
            VALUES ($1, $2, $3, $4)
        """
        success = await self._execute(query, user_id, repo, commit_sha, status)
        if success:
            logger.info("Verification recorded: %s %s - %s", repo, commit_sha[:8], status)
        return success
    
    async def get_user_history(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user verification history."""
        query = """
            SELECT repo, commit_sha, status, created_at
            FROM verifications
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        rows = await self._fetch(query, user_id, limit)
        return [dict(row) for row in rows]
    
    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user verification statistics."""
        query = """
            SELECT status, COUNT(*) as count
            FROM verifications
            WHERE user_id = $1
            GROUP BY status
        """
        rows = await self._fetch(query, user_id)
        
        stats = {
            'total': 0,
            'approved': 0,
            'rejected': 0,
        }
        
        for row in rows:
            stats[row['status']] = row['count']
            stats['total'] += row['count']
        
        return stats
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all users."""
        query = """
            SELECT
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(*) as total_verifications,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM verifications
        """
        stats = await self._fetchrow(query)
        return dict(stats) if stats else {}
