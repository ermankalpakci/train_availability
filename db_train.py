import sqlite3
from dataclasses import dataclass
from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@dataclass
class DBConfig:
    db_path: str = "train.db"
    timeout: int = 5  # More reasonable timeout
    pragmas: dict = None  # For database optimizations

class DatabaseError(Exception):
    """Custom exception for database operations"""

class TrainDatabase:
    _instance = None  # Class-level attribute to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TrainDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: DBConfig = DBConfig()):
        # Avoid reinitializing if already initialized
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.config = config
        self._setup_pragmas()
        self._initialized = True
        
    def _setup_pragmas(self):
        """Configure database optimizations"""
        pragmas = self.config.pragmas or {
            "journal_mode": "WAL",  # Better concurrency
            "foreign_keys": "ON",    # Enable FK constraints
            "busy_timeout": 5000     # 5ms timeout
        }
        with self.connect() as conn:
            for pragma, value in pragmas.items():
                conn.execute(f"PRAGMA {pragma}={value};")

    @contextmanager
    def connect(self):
        """Thread-safe connection context manager"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.config.db_path,
                timeout=self.config.timeout,
                check_same_thread=False
            )
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            if conn:
                conn.rollback()
            raise DatabaseError(f"Operation failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_id_given_name(self, name: str) -> Optional[int]:
        """Get user ID by name (safe version)"""
        try:
            with self.connect() as conn:
                cursor = conn.execute(
                    "SELECT id FROM stations WHERE name = ?",
                    (name,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch user: {str(e)}")
            raise DatabaseError("User lookup failed") from e

    def get_station_names(self) -> list:
        """Retrieve a list of station names from the stations table."""
        try:
            with self.connect() as conn:
                cursor = conn.execute("SELECT name FROM stations")
                rows = cursor.fetchall()
                names = [row[0] for row in rows]
                return names
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch station names: {e}")
            raise DatabaseError("Station names lookup failed") from e
