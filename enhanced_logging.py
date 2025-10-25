#!/usr/bin/env python3
"""
Enhanced Web Error Logging System
Makes error logs easier to read and debug
"""

import logging
import traceback
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

class EnhancedLogger:
    """Enhanced logger with better formatting and error categorization"""
    
    def __init__(self, name: str = "labelmaker"):
        self.logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup enhanced logging configuration"""
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Enhanced formatter with colors and better structure
        class ColoredFormatter(logging.Formatter):
            """Colored formatter for better readability"""
            
            COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
                'RESET': '\033[0m'      # Reset
            }
            
            def format(self, record):
                # Add color based on level
                color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                reset = self.COLORS['RESET']
                
                # Format timestamp
                timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
                
                # Format message with better structure
                if record.levelname == 'ERROR':
                    formatted = f"{color}🚨 ERROR [{timestamp}] {record.name}{reset}\n"
                    formatted += f"   📍 {record.filename}:{record.lineno} in {record.funcName}()\n"
                    formatted += f"   💬 {record.getMessage()}{reset}\n"
                elif record.levelname == 'WARNING':
                    formatted = f"{color}⚠️  WARN  [{timestamp}] {record.name}{reset}\n"
                    formatted += f"   📍 {record.filename}:{record.lineno}\n"
                    formatted += f"   💬 {record.getMessage()}{reset}\n"
                elif record.levelname == 'INFO':
                    formatted = f"{color}ℹ️  INFO  [{timestamp}] {record.name}{reset}\n"
                    formatted += f"   💬 {record.getMessage()}{reset}\n"
                else:
                    formatted = f"{color}{record.levelname:8} [{timestamp}] {record.name}{reset}\n"
                    formatted += f"   💬 {record.getMessage()}{reset}\n"
                
                return formatted
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        
        # File handler with structured format
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)-20s:%(lineno)-4d | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Error log file
        error_handler = logging.FileHandler(log_dir / 'errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # General log file
        general_handler = logging.FileHandler(log_dir / 'app.log')
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(general_handler)
        self.logger.setLevel(logging.INFO)
        
        # Suppress noisy third-party loggers
        for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas', 'openpyxl', 'xlrd']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """Log an error with enhanced context"""
        
        # Base error message
        error_msg = f"❌ {message}"
        
        # Add context if provided
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            error_msg += f" | Context: {context_str}"
        
        # Log the error
        self.logger.error(error_msg)
        
        # Log exception details if provided
        if exception:
            self.logger.error(f"   Exception: {type(exception).__name__}: {str(exception)}")
            
            # Log traceback for debugging
            tb_lines = traceback.format_exc().split('\n')
            for line in tb_lines:
                if line.strip():
                    self.logger.error(f"   Traceback: {line}")
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a warning with context"""
        warning_msg = f"⚠️  {message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            warning_msg += f" | Context: {context_str}"
        
        self.logger.warning(warning_msg)
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info with context"""
        info_msg = f"ℹ️  {message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            info_msg += f" | Context: {context_str}"
        
        self.logger.info(info_msg)
    
    def log_success(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a success message"""
        success_msg = f"✅ {message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            success_msg += f" | Context: {context_str}"
        
        self.logger.info(success_msg)
    
    def log_performance(self, operation: str, duration: float, context: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        perf_msg = f"⚡ {operation} completed in {duration:.3f}s"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            perf_msg += f" | Context: {context_str}"
        
        self.logger.info(perf_msg)

class ErrorContext:
    """Context manager for adding error context"""
    
    def __init__(self, logger: EnhancedLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log_info(f"Starting {self.operation}", self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log_success(f"Completed {self.operation}", 
                                  {**self.context, 'duration': f"{duration:.3f}s"})
        else:
            self.logger.log_error(f"Failed {self.operation}", exc_val, 
                                {**self.context, 'duration': f"{duration:.3f}s"})
        
        return False  # Don't suppress exceptions

def setup_enhanced_logging():
    """Setup enhanced logging for the application"""
    
    # Create enhanced logger instance
    enhanced_logger = EnhancedLogger("labelmaker")
    
    # Replace the default logger
    logging.getLogger().handlers.clear()
    logging.getLogger().addHandler(enhanced_logger.logger.handlers[0])  # Console handler
    logging.getLogger().addHandler(enhanced_logger.logger.handlers[1])  # Error handler
    logging.getLogger().addHandler(enhanced_logger.logger.handlers[2])  # General handler
    logging.getLogger().setLevel(logging.INFO)
    
    return enhanced_logger

def log_route_error(route_name: str, exception: Exception, request_data: Optional[Dict] = None):
    """Log route-specific errors with request context"""
    
    logger = EnhancedLogger("routes")
    
    context = {
        'route': route_name,
        'method': getattr(request_data, 'method', 'Unknown') if request_data else 'Unknown',
        'url': getattr(request_data, 'url', 'Unknown') if request_data else 'Unknown'
    }
    
    logger.log_error(f"Route error in {route_name}", exception, context)

def log_database_error(operation: str, exception: Exception, query: Optional[str] = None):
    """Log database-specific errors"""
    
    logger = EnhancedLogger("database")
    
    context = {
        'operation': operation,
        'query': query[:100] + "..." if query and len(query) > 100 else query
    }
    
    logger.log_error(f"Database error during {operation}", exception, context)

def log_file_processing_error(filename: str, operation: str, exception: Exception):
    """Log file processing errors"""
    
    logger = EnhancedLogger("file_processing")
    
    context = {
        'filename': filename,
        'operation': operation,
        'file_size': os.path.getsize(filename) if os.path.exists(filename) else 'Unknown'
    }
    
    logger.log_error(f"File processing error for {filename}", exception, context)

if __name__ == "__main__":
    # Test the enhanced logging
    logger = setup_enhanced_logging()
    
    logger.log_info("Enhanced logging system initialized")
    logger.log_success("Test successful operation")
    logger.log_warning("Test warning message")
    
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.log_error("Test error", e, {'test': True})
    
    with ErrorContext(logger, "test operation", param1="value1"):
        import time
        time.sleep(0.1)
        logger.log_info("Operation in progress")
