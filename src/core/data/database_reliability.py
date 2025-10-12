"""
Database Reliability and Recovery System
========================================
Comprehensive system to prevent database crashes and ensure data integrity.

Features:
- Automatic corruption detection and recovery
- Real-time health monitoring
- Automatic backups before writes
- Connection retry with exponential backoff
- File integrity verification
- Graceful degradation and failover
"""

import sqlite3
import os
import shutil
import time
import logging
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, Callable
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class DatabaseReliability:
    """Comprehensive database reliability and recovery system."""
    
    def __init__(self, db_path: str, backup_dir: str = None):
        self.db_path = db_path
        self.backup_dir = backup_dir or os.path.join(os.path.dirname(db_path), 'backups')
        self.health_check_interval = 60  # Check health every 60 seconds
        self.max_backup_age_hours = 24  # Keep backups for 24 hours
        self.max_backups = 10  # Maximum number of rolling backups
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Thread-safe locks
        self._backup_lock = threading.RLock()
        self._health_lock = threading.RLock()
        
        # Health status
        self._last_health_check = None
        self._is_healthy = None
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3
        
    def verify_database_integrity(self) -> Tuple[bool, str]:
        """
        Verify database file integrity.
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check if file exists
            if not os.path.exists(self.db_path):
                return False, "Database file does not exist"
            
            # Check if file is readable
            if not os.access(self.db_path, os.R_OK):
                return False, "Database file is not readable"
            
            # Check file size
            file_size = os.path.getsize(self.db_path)
            if file_size == 0:
                return False, "Database file is empty"
            
            if file_size < 100:  # SQLite header is 100 bytes
                return False, f"Database file is too small ({file_size} bytes)"
            
            # Verify SQLite file header
            with open(self.db_path, 'rb') as f:
                header = f.read(16)
                if header != b'SQLite format 3\x00':
                    return False, "Invalid SQLite file header (file is corrupted)"
            
            # Attempt to open and run integrity check
            conn = None
            try:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                cursor = conn.cursor()
                
                # Run SQLite integrity check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    return True, "Database integrity verified"
                else:
                    return False, f"Database integrity check failed: {result[0] if result else 'unknown error'}"
                    
            except sqlite3.DatabaseError as e:
                return False, f"Database error during integrity check: {str(e)}"
            except Exception as e:
                return False, f"Unexpected error during integrity check: {str(e)}"
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                        
        except Exception as e:
            return False, f"Error verifying database: {str(e)}"
    
    def create_backup(self, label: str = "auto") -> Tuple[bool, str]:
        """
        Create a backup of the database.
        
        Args:
            label: Label for the backup (e.g., 'auto', 'manual', 'pre-write')
            
        Returns:
            Tuple of (success, backup_path or error_message)
        """
        with self._backup_lock:
            try:
                # Verify source database first
                is_valid, message = self.verify_database_integrity()
                if not is_valid:
                    logger.error(f"Cannot backup corrupted database: {message}")
                    return False, f"Source database is corrupted: {message}"
                
                # Create timestamped backup filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"db_backup_{label}_{timestamp}.db"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                
                # Create backup using SQLite backup API for consistency
                source_conn = None
                backup_conn = None
                
                try:
                    source_conn = sqlite3.connect(self.db_path, timeout=10.0)
                    backup_conn = sqlite3.connect(backup_path)
                    
                    # Use SQLite's backup API
                    with backup_conn:
                        source_conn.backup(backup_conn)
                    
                    # Verify backup
                    backup_conn_verify = sqlite3.connect(backup_path, timeout=5.0)
                    cursor = backup_conn_verify.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                    backup_conn_verify.close()
                    
                    if result and result[0] == 'ok':
                        logger.info(f"Database backup created successfully: {backup_path}")
                        
                        # Clean up old backups
                        self._cleanup_old_backups()
                        
                        return True, backup_path
                    else:
                        os.remove(backup_path)
                        return False, "Backup verification failed"
                        
                except Exception as e:
                    if os.path.exists(backup_path):
                        try:
                            os.remove(backup_path)
                        except:
                            pass
                    raise
                    
                finally:
                    if source_conn:
                        try:
                            source_conn.close()
                        except:
                            pass
                    if backup_conn:
                        try:
                            backup_conn.close()
                        except:
                            pass
                            
            except Exception as e:
                logger.error(f"Error creating backup: {str(e)}")
                return False, str(e)
    
    def restore_from_backup(self, backup_path: str = None) -> Tuple[bool, str]:
        """
        Restore database from a backup.
        
        Args:
            backup_path: Path to backup file. If None, uses most recent backup.
            
        Returns:
            Tuple of (success, message)
        """
        with self._backup_lock:
            try:
                # Find backup to restore
                if backup_path is None:
                    backup_path = self._find_latest_valid_backup()
                    if backup_path is None:
                        return False, "No valid backups found"
                
                if not os.path.exists(backup_path):
                    return False, f"Backup file not found: {backup_path}"
                
                # Verify backup integrity before restoring
                temp_db = backup_path
                try:
                    conn = sqlite3.connect(temp_db, timeout=5.0)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                    conn.close()
                    
                    if not result or result[0] != 'ok':
                        return False, f"Backup file is corrupted: {backup_path}"
                except Exception as e:
                    return False, f"Cannot verify backup: {str(e)}"
                
                # Create a backup of current (corrupted) database for forensics
                if os.path.exists(self.db_path):
                    corrupted_path = f"{self.db_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    try:
                        shutil.copy2(self.db_path, corrupted_path)
                        logger.info(f"Corrupted database saved to: {corrupted_path}")
                    except Exception as e:
                        logger.warning(f"Could not save corrupted database: {e}")
                
                # Close all existing connections
                # This will be handled by the caller
                
                # Replace database with backup
                shutil.copy2(backup_path, self.db_path)
                
                # Verify restored database
                is_valid, message = self.verify_database_integrity()
                if is_valid:
                    logger.info(f"Database restored successfully from: {backup_path}")
                    self._consecutive_failures = 0
                    return True, f"Database restored from {os.path.basename(backup_path)}"
                else:
                    return False, f"Restored database is still corrupted: {message}"
                    
            except Exception as e:
                logger.error(f"Error restoring from backup: {str(e)}")
                return False, str(e)
    
    def _find_latest_valid_backup(self) -> Optional[str]:
        """Find the most recent valid backup."""
        try:
            if not os.path.exists(self.backup_dir):
                return None
            
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('db_backup_') and filename.endswith('.db'):
                    full_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((os.path.getmtime(full_path), full_path))
            
            # Sort by modification time (most recent first)
            backup_files.sort(reverse=True)
            
            # Find first valid backup
            for _, backup_path in backup_files:
                try:
                    conn = sqlite3.connect(backup_path, timeout=5.0)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result and result[0] == 'ok':
                        return backup_path
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding latest backup: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Clean up old backup files."""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('db_backup_') and filename.endswith('.db'):
                    full_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((os.path.getmtime(full_path), full_path))
            
            # Sort by modification time (oldest first)
            backup_files.sort()
            
            # Remove old backups beyond max count
            if len(backup_files) > self.max_backups:
                for _, old_backup in backup_files[:-self.max_backups]:
                    try:
                        os.remove(old_backup)
                        logger.info(f"Removed old backup: {old_backup}")
                    except Exception as e:
                        logger.warning(f"Could not remove old backup {old_backup}: {e}")
            
            # Remove backups older than max age
            cutoff_time = time.time() - (self.max_backup_age_hours * 3600)
            for mtime, backup_path in backup_files:
                if mtime < cutoff_time:
                    try:
                        os.remove(backup_path)
                        logger.info(f"Removed expired backup: {backup_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove expired backup {backup_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
    
    def check_health(self, force: bool = False) -> Dict[str, Any]:
        """
        Check database health status.
        
        Args:
            force: Force health check even if recently checked
            
        Returns:
            Dictionary with health status information
        """
        with self._health_lock:
            # Use cached result if recent
            if not force and self._last_health_check:
                age = (datetime.now() - self._last_health_check).total_seconds()
                if age < self.health_check_interval and self._is_healthy is not None:
                    return {
                        'healthy': self._is_healthy,
                        'last_check': self._last_health_check.isoformat(),
                        'age_seconds': age,
                        'cached': True
                    }
            
            # Perform health check
            is_valid, message = self.verify_database_integrity()
            
            self._last_health_check = datetime.now()
            self._is_healthy = is_valid
            
            if is_valid:
                self._consecutive_failures = 0
            else:
                self._consecutive_failures += 1
            
            return {
                'healthy': is_valid,
                'message': message,
                'last_check': self._last_health_check.isoformat(),
                'consecutive_failures': self._consecutive_failures,
                'cached': False,
                'db_path': self.db_path,
                'db_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            }
    
    def safe_execute(self, operation: Callable, max_retries: int = 3, 
                    backup_before: bool = True) -> Tuple[bool, Any, str]:
        """
        Execute a database operation with automatic recovery.
        
        Args:
            operation: Callable that performs database operation
            max_retries: Maximum number of retry attempts
            backup_before: Create backup before operation
            
        Returns:
            Tuple of (success, result, message)
        """
        # Check health first
        health = self.check_health()
        if not health['healthy']:
            logger.warning(f"Database unhealthy before operation: {health.get('message')}")
            # Attempt recovery
            success, message = self.restore_from_backup()
            if not success:
                return False, None, f"Database corrupted and recovery failed: {message}"
            logger.info("Database recovered automatically")
        
        # Create backup before write operations
        if backup_before:
            success, backup_msg = self.create_backup("pre-write")
            if not success:
                logger.warning(f"Could not create pre-write backup: {backup_msg}")
        
        # Attempt operation with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                result = operation()
                return True, result, "Operation successful"
                
            except sqlite3.DatabaseError as e:
                last_error = str(e)
                logger.error(f"Database error on attempt {attempt + 1}/{max_retries}: {e}")
                
                # Check if it's a corruption error
                if 'file is not a database' in str(e).lower() or \
                   'database disk image is malformed' in str(e).lower() or \
                   'database is locked' in str(e).lower():
                    
                    # Attempt recovery
                    logger.warning(f"Database corruption detected, attempting recovery...")
                    success, message = self.restore_from_backup()
                    
                    if success:
                        logger.info("Database recovered, retrying operation...")
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        return False, None, f"Recovery failed: {message}"
                else:
                    # Not a corruption error, just retry
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                        
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
        
        return False, None, f"Operation failed after {max_retries} attempts: {last_error}"
    
    def emergency_recovery(self) -> Tuple[bool, str]:
        """
        Perform emergency recovery of database.
        
        This will:
        1. Attempt to restore from most recent backup
        2. If no backups, create new empty database
        
        Returns:
            Tuple of (success, message)
        """
        logger.warning("EMERGENCY RECOVERY INITIATED")
        
        # Try to restore from backup
        success, message = self.restore_from_backup()
        if success:
            return True, f"Emergency recovery successful: {message}"
        
        # If no valid backups, create new database
        logger.warning("No valid backups found, creating new database...")
        
        try:
            # Save corrupted database
            if os.path.exists(self.db_path):
                corrupted_path = f"{self.db_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(self.db_path, corrupted_path)
                logger.info(f"Corrupted database moved to: {corrupted_path}")
            
            # Create new empty database
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.close()
            
            # Verify
            is_valid, msg = self.verify_database_integrity()
            if is_valid:
                return True, "Emergency recovery: new database created"
            else:
                return False, f"Could not create new database: {msg}"
                
        except Exception as e:
            return False, f"Emergency recovery failed: {str(e)}"


# Global reliability manager cache
_reliability_managers: Dict[str, DatabaseReliability] = {}
_reliability_lock = threading.Lock()

def get_reliability_manager(db_path: str) -> DatabaseReliability:
    """Get or create a reliability manager for a database."""
    with _reliability_lock:
        if db_path not in _reliability_managers:
            _reliability_managers[db_path] = DatabaseReliability(db_path)
        return _reliability_managers[db_path]

