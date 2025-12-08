#!/usr/bin/env python3
"""
Database Module
Управление хранилищем данных проверок комитов
"""

import logging
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class Database:
    """
    SQLite database for storing verification records
    """
    
    def __init__(self, db_path: str = "verifications.db"):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """
        Initialize database tables
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Verifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    repo TEXT NOT NULL,
                    commit_sha TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """)
            
            # Create index on commit_sha for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commit_sha ON verifications(commit_sha)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
        
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
        
        finally:
            conn.close()
    
    async def add_user(self, user_id: int, username: str) -> bool:
        """
        Add or update user
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            conn.commit()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
            return False
        
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO verifications (user_id, repo, commit_sha, status)
                VALUES (?, ?, ?, ?)
            """, (user_id, repo, commit_sha, status))
            
            conn.commit()
            logger.info(f"Verification recorded: {repo} {commit_sha[:8]} - {status}")
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error adding verification: {e}")
            return False
        
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT repo, commit_sha, status, created_at
                FROM verifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except sqlite3.Error as e:
            logger.error(f"Error fetching history: {e}")
            return []
        
        finally:
            conn.close()
    
    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get user verification statistics
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM verifications
                WHERE user_id = ?
                GROUP BY status
            """, (user_id,))
            
            rows = cursor.fetchall()
            stats = {
                'total': 0,
                'approved': 0,
                'rejected': 0,
            }
            
            for row in rows:
                stats[row['status']] = row['count']
                stats['total'] += row['count']
            
            return stats
        
        except sqlite3.Error as e:
            logger.error(f"Error fetching statistics: {e}")
            return {'total': 0, 'approved': 0, 'rejected': 0}
        
        finally:
            conn.close()
