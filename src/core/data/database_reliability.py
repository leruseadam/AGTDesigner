"""
Database Reliability System
==========================
Comprehensive crash prevention and recovery system for database operations.
Provides multiple layers of protection against database failures.
"""

import os
import sqlite3
import threading
import time
import shutil
import logging
import json
import psutil
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from pathlib import Path
from contextlib import contextmanager
import tempfile

logger = logging.getLogger(__name__)

class DatabaseHealthStatus:
    """Represents the health status of a database"""
    def __init__(self):
        self.is_healthy = True
        self.corruption_detected = False
        self.connection_errors = 0
        self.last_check = datetime.now()
        self.disk_space_ok = True
        self.memory_usage_ok = True
        self.backup_status = 'unknown'
        self.issues = []
        self.warnings = []

class ResourceMonitor:
    """Monitors system resources to prevent database crashes"""
    
    def __init__(self, min_disk_space_mb=1000, max_memory_percent=80):
        self.min_disk_space_mb = min_disk_space_mb
        self.max_memory_percent = max_memory_percent
        
    def check_disk_space(self, db_path: str) -> Tuple[bool, str, int]:
        """Check if sufficient disk space is available"""
        try:
            # Get disk usage for the directory containing the database
            db_dir = os.path.dirname(os.path.abspath(db_path))
            usage = shutil.disk_usage(db_dir)
            
            free_mb = usage.free // (1024 * 1024)
            free_percent = (usage.free / usage.total) * 100
            
            if free_mb < self.min_disk_space_mb:
                return False, f"Low disk space: {free_mb}MB remaining", free_mb
            
            return True, f"Disk space OK: {free_mb}MB available ({free_percent:.1f}%)", free_mb
            
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            return False, f"Error checking disk space: {e}", 0
    
    def check_memory_usage(self) -> Tuple[bool, str]:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > self.max_memory_percent:
                return False, f"High memory usage: {memory.percent:.1f}%"
            return True, f"Memory usage OK: {memory.percent:.1f}%"
        except Exception as e:
            logger.error(f"Error checking memory: {e}")
            return False, f"Error checking memory: {e}"

class DatabaseBackupManager:
    """Manages automatic database backups with rotation"""
    
    def __init__(self, db_path: str, backup_dir: str = None, max_backups: int = 10):
        self.db_path = db_path
        self.backup_dir = backup_dir or os.path.join(os.path.dirname(db_path), 'backups')
        self.max_backups = max_backups
        self._ensure_backup_dir()
        
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self, backup_name: str = None) -> Tuple[bool, str]:
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_path):
                return False, f"Source database not found: {self.db_path}"
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if backup_name is None:
                backup_name = f"backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup using SQLite backup API for consistency
            try:
                source_conn = sqlite3.connect(self.db_path)
                backup_conn = sqlite3.connect(backup_path)
                source_conn.backup(backup_conn)
                backup_conn.close()
                source_conn.close()
            except Exception as e:
                # Fallback to file copy if backup API fails
                logger.warning(f"SQLite backup API failed, using file copy: {e}")
                shutil.copy2(self.db_path, backup_path)
            
            # Verify backup integrity
            if self._verify_backup(backup_path):
                self._rotate_backups()
                return True, f"Backup created successfully: {backup_path}"
            else:
                os.remove(backup_path)
                return False, "Backup verification failed"
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False, f"Backup failed: {e}"
    
    def _verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity"""
        try:
            conn = sqlite3.connect(backup_path)
            conn.execute("PRAGMA integrity_check")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def _rotate_backups(self):
        """Remove old backups to maintain max_backups limit"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time, newest first
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for file_path, _ in backup_files[self.max_backups:]:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing old backup {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error rotating backups: {e}")
    
    def get_latest_backup(self) -> Optional[str]:
        """Get the path to the most recent backup"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            if backup_files:
                backup_files.sort(key=lambda x: x[1], reverse=True)
                return backup_files[0][0]
            return None
        except Exception as e:
            logger.error(f"Error finding latest backup: {e}")
            return None

class DatabaseRecoveryManager:
    """Handles database corruption detection and recovery"""
    
    def __init__(self, db_path: str, backup_manager: DatabaseBackupManager):
        self.db_path = db_path
        self.backup_manager = backup_manager
        
    def check_corruption(self) -> Tuple[bool, List[str]]:
        """Check database for corruption"""
        issues = []
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            
            # Run integrity check
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchall()
            
            # Check if integrity check passed
            if len(result) == 1 and result[0][0] == 'ok':
                conn.close()
                return False, []
            else:
                for row in result:
                    issues.append(str(row[0]))
                conn.close()
                return True, issues
                
        except sqlite3.DatabaseError as e:
            issues.append(f"Database error: {e}")
            return True, issues
        except Exception as e:
            issues.append(f"Unexpected error during corruption check: {e}")
            return True, issues
    
    def attempt_recovery(self) -> Tuple[bool, str]:
        """Attempt to recover from corruption"""
        try:
            # Create emergency backup before recovery
            emergency_backup = f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                shutil.copy2(self.db_path, os.path.join(self.backup_manager.backup_dir, emergency_backup))
            except Exception:
                pass  # Continue with recovery even if emergency backup fails
            
            # Try to recover using .recover command
            recovery_path = self.db_path + '.recovered'
            
            try:
                # Use sqlite3 .recover command if available (SQLite 3.37+)
                import subprocess
                result = subprocess.run([
                    'sqlite3', self.db_path, '.recover'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and result.stdout:
                    # Write recovered data to new file
                    with open(recovery_path, 'w') as f:
                        f.write(result.stdout)
                    
                    # Replace corrupted database with recovered one
                    shutil.move(recovery_path, self.db_path)
                    return True, "Database recovered using .recover command"
                    
            except Exception as e:
                logger.warning(f"Recovery command failed: {e}")
            
            # Fallback: Try to restore from latest backup
            latest_backup = self.backup_manager.get_latest_backup()
            if latest_backup and os.path.exists(latest_backup):
                shutil.copy2(latest_backup, self.db_path)
                return True, f"Database restored from backup: {latest_backup}"
            
            return False, "No recovery options available"
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return False, f"Recovery failed: {e}"

class ConnectionHealthManager:
    """Manages database connection health and recovery"""
    
    def __init__(self, max_connection_errors=5, connection_timeout=30.0):
        self.max_connection_errors = max_connection_errors
        self.connection_timeout = connection_timeout
        self.connection_errors = {}
        self.last_health_check = {}
        
    def is_connection_healthy(self, db_path: str) -> Tuple[bool, str]:
        """Check if database connection is healthy"""
        try:
            conn = sqlite3.connect(db_path, timeout=self.connection_timeout)
            
            # Perform simple query to test connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            
            # Reset error count on successful connection
            self.connection_errors[db_path] = 0
            self.last_health_check[db_path] = datetime.now()
            
            return True, "Connection healthy"
            
        except sqlite3.OperationalError as e:
            error_count = self.connection_errors.get(db_path, 0) + 1
            self.connection_errors[db_path] = error_count
            
            if error_count >= self.max_connection_errors:
                return False, f"Connection failed {error_count} times: {e}"
            else:
                return True, f"Connection warning ({error_count}/{self.max_connection_errors}): {e}"
                
        except Exception as e:
            error_count = self.connection_errors.get(db_path, 0) + 1
            self.connection_errors[db_path] = error_count
            return False, f"Connection error: {e}"

class TransactionSafetyWrapper:
    """Provides safe transaction handling with automatic rollback"""
    
    def __init__(self, connection):
        self.connection = connection
        self.in_transaction = False
        
    @contextmanager
    def safe_transaction(self):
        """Context manager for safe transactions with automatic rollback"""
        if self.in_transaction:
            # Nested transaction - use savepoint
            savepoint_name = f"sp_{int(time.time() * 1000000)}"
            try:
                self.connection.execute(f"SAVEPOINT {savepoint_name}")
                yield self.connection
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint_name}")
            except Exception as e:
                try:
                    self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                except Exception:
                    pass  # Savepoint may not exist
                raise e
        else:
            # Regular transaction
            self.in_transaction = True
            try:
                self.connection.execute("BEGIN")
                yield self.connection
                self.connection.commit()
            except Exception as e:
                try:
                    self.connection.rollback()
                except Exception:
                    pass  # Connection may be closed
                raise e
            finally:
                self.in_transaction = False

class DatabaseHealthMonitor:
    """Comprehensive database health monitoring system"""
    
    def __init__(self, db_path: str, check_interval_seconds: int = 300):
        self.db_path = db_path
        self.check_interval = check_interval_seconds
        self.resource_monitor = ResourceMonitor()
        self.backup_manager = DatabaseBackupManager(db_path)
        self.recovery_manager = DatabaseRecoveryManager(db_path, self.backup_manager)
        self.connection_health = ConnectionHealthManager()
        
        self.health_status = DatabaseHealthStatus()
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Create initial backup
        self._create_initial_backup()
        
    def _create_initial_backup(self):
        """Create initial backup when monitor starts"""
        try:
            success, message = self.backup_manager.create_backup("initial_backup.db")
            if success:
                logger.info(f"Initial backup created: {message}")
            else:
                logger.warning(f"Initial backup failed: {message}")
        except Exception as e:
            logger.error(f"Error creating initial backup: {e}")
    
    def start_monitoring(self):
        """Start the health monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Database health monitoring started")
    
    def stop_monitoring_thread(self):
        """Stop the health monitoring thread"""
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Database health monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.wait(self.check_interval):
            try:
                self.perform_health_check()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def perform_health_check(self) -> DatabaseHealthStatus:
        """Perform comprehensive health check"""
        self.health_status = DatabaseHealthStatus()
        self.health_status.last_check = datetime.now()
        
        # Check disk space
        disk_ok, disk_message, free_mb = self.resource_monitor.check_disk_space(self.db_path)
        self.health_status.disk_space_ok = disk_ok
        if not disk_ok:
            self.health_status.issues.append(disk_message)
            self.health_status.is_healthy = False
        
        # Check memory usage
        memory_ok, memory_message = self.resource_monitor.check_memory_usage()
        self.health_status.memory_usage_ok = memory_ok
        if not memory_ok:
            self.health_status.warnings.append(memory_message)
        
        # Check connection health
        conn_healthy, conn_message = self.connection_health.is_connection_healthy(self.db_path)
        if not conn_healthy:
            self.health_status.issues.append(conn_message)
            self.health_status.is_healthy = False
            self.health_status.connection_errors = self.connection_health.connection_errors.get(self.db_path, 0)
        
        # Check for corruption
        corrupted, corruption_issues = self.recovery_manager.check_corruption()
        self.health_status.corruption_detected = corrupted
        if corrupted:
            self.health_status.issues.extend(corruption_issues)
            self.health_status.is_healthy = False
            
            # Attempt recovery if corruption detected
            logger.error(f"Database corruption detected: {corruption_issues}")
            recovery_success, recovery_message = self.recovery_manager.attempt_recovery()
            if recovery_success:
                logger.info(f"Database recovery successful: {recovery_message}")
                self.health_status.warnings.append(f"Recovered from corruption: {recovery_message}")
            else:
                logger.error(f"Database recovery failed: {recovery_message}")
                self.health_status.issues.append(f"Recovery failed: {recovery_message}")
        
        # Create backup if needed (daily backups)
        self._check_backup_schedule()
        
        # Log health status
        if not self.health_status.is_healthy:
            logger.error(f"Database health check failed: {self.health_status.issues}")
        elif self.health_status.warnings:
            logger.warning(f"Database health warnings: {self.health_status.warnings}")
        else:
            logger.debug("Database health check passed")
            
        return self.health_status
    
    def _check_backup_schedule(self):
        """Check if it's time to create a scheduled backup"""
        try:
            # Create daily backups
            backup_files = os.listdir(self.backup_manager.backup_dir)
            today = datetime.now().strftime('%Y%m%d')
            
            # Check if we already have a backup from today
            has_today_backup = any(today in f for f in backup_files if f.endswith('.db'))
            
            if not has_today_backup:
                success, message = self.backup_manager.create_backup(f"daily_backup_{today}.db")
                if success:
                    self.health_status.backup_status = 'success'
                    logger.info(f"Daily backup created: {message}")
                else:
                    self.health_status.backup_status = 'failed'
                    self.health_status.warnings.append(f"Daily backup failed: {message}")
            else:
                self.health_status.backup_status = 'current'
                
        except Exception as e:
            self.health_status.backup_status = 'error'
            self.health_status.warnings.append(f"Backup schedule check failed: {e}")
    
    def force_backup(self) -> Tuple[bool, str]:
        """Force creation of a backup"""
        return self.backup_manager.create_backup()
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get detailed health report"""
        return {
            'timestamp': self.health_status.last_check.isoformat(),
            'is_healthy': self.health_status.is_healthy,
            'corruption_detected': self.health_status.corruption_detected,
            'connection_errors': self.health_status.connection_errors,
            'disk_space_ok': self.health_status.disk_space_ok,
            'memory_usage_ok': self.health_status.memory_usage_ok,
            'backup_status': self.health_status.backup_status,
            'issues': self.health_status.issues,
            'warnings': self.health_status.warnings,
            'database_path': self.db_path,
            'backup_directory': self.backup_manager.backup_dir
        }

# Global health monitors
_health_monitors = {}
_monitor_lock = threading.Lock()

def get_health_monitor(db_path: str) -> DatabaseHealthMonitor:
    """Get or create a health monitor for a database"""
    with _monitor_lock:
        if db_path not in _health_monitors:
            monitor = DatabaseHealthMonitor(db_path)
            monitor.start_monitoring()
            _health_monitors[db_path] = monitor
        return _health_monitors[db_path]

def ensure_database_reliability(db_path: str) -> DatabaseHealthStatus:
    """Ensure database reliability by performing health check"""
    monitor = get_health_monitor(db_path)
    return monitor.perform_health_check()

def create_safe_connection(db_path: str, timeout: float = 30.0):
    """Create a safe database connection with reliability checks"""
    # Perform health check first
    health_status = ensure_database_reliability(db_path)
    
    if not health_status.is_healthy:
        raise sqlite3.DatabaseError(f"Database health check failed: {health_status.issues}")
    
    # Create connection with optimal settings
    conn = sqlite3.connect(
        db_path,
        timeout=timeout,
        check_same_thread=False
    )
    
    # Configure for reliability
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA foreign_keys=ON")
    
    return TransactionSafetyWrapper(conn)

# Decorator for safe database operations
def safe_database_operation(max_retries: int = 3, backup_on_failure: bool = True):
    """Decorator to make database operations safe with automatic retry and backup"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            db_path = None
            
            # Try to extract db_path from args or self
            if args and hasattr(args[0], 'db_path'):
                db_path = args[0].db_path
            
            for attempt in range(max_retries + 1):
                try:
                    # Perform health check before operation
                    if db_path:
                        health_status = ensure_database_reliability(db_path)
                        if not health_status.is_healthy and attempt == 0:
                            logger.warning(f"Database health issues detected before operation: {health_status.issues}")
                    
                    return func(*args, **kwargs)
                    
                except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
                    if attempt < max_retries:
                        wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                        logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        
                        # Create backup on failure if enabled
                        if backup_on_failure and db_path and attempt == 0:
                            try:
                                monitor = get_health_monitor(db_path)
                                monitor.force_backup()
                                logger.info("Emergency backup created due to database error")
                            except Exception as backup_error:
                                logger.error(f"Emergency backup failed: {backup_error}")
                    else:
                        logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
                        raise
                        
                except Exception as e:
                    logger.error(f"Unexpected error in database operation: {e}")
                    raise
                    
            return None
        return wrapper
    return decorator
