"""
Performance monitoring and bottleneck detection system.
Provides real-time performance metrics, alerting, and optimization recommendations.
"""

import time
import threading
import logging
import psutil
import gc
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class BottleneckAlert:
    """Represents a performance bottleneck alert."""
    severity: str  # 'low', 'medium', 'high', 'critical'
    component: str
    metric: str
    value: float
    threshold: float
    message: str
    timestamp: float
    recommendations: List[str] = field(default_factory=list)

class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics = defaultdict(lambda: deque(maxlen=max_history))
        self._alerts = deque(maxlen=100)
        self._thresholds = {}
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # Performance tracking
        self._operation_times = defaultdict(list)
        self._memory_usage = deque(maxlen=100)
        self._cpu_usage = deque(maxlen=100)
        self._active_operations = {}
        
        # Alert handlers
        self._alert_handlers = []
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background performance monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check thresholds and generate alerts
                self._check_thresholds()
                
                # Cleanup old data
                self._cleanup_old_data()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self._memory_usage.append({
                'timestamp': time.time(),
                'used_percent': memory.percent,
                'used_mb': memory.used / (1024 * 1024),
                'available_mb': memory.available / (1024 * 1024)
            })
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self._cpu_usage.append({
                'timestamp': time.time(),
                'cpu_percent': cpu_percent
            })
            
            # Python-specific metrics
            gc_stats = gc.get_stats()
            for i, stat in enumerate(gc_stats):
                self._record_metric(f"gc_generation_{i}_collections", stat['collections'])
                self._record_metric(f"gc_generation_{i}_objects_collected", stat['collected'])
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _check_thresholds(self):
        """Check performance thresholds and generate alerts."""
        current_time = time.time()
        
        # Check memory usage
        if self._memory_usage:
            latest_memory = self._memory_usage[-1]
            if latest_memory['used_percent'] > 90:
                self._create_alert('critical', 'memory', 'used_percent', 
                                 latest_memory['used_percent'], 90,
                                 f"High memory usage: {latest_memory['used_percent']:.1f}%",
                                 ["Restart application", "Clear caches", "Optimize memory usage"])
        
        # Check CPU usage
        if self._cpu_usage:
            latest_cpu = self._cpu_usage[-1]
            if latest_cpu['cpu_percent'] > 80:
                self._create_alert('high', 'cpu', 'cpu_percent',
                                 latest_cpu['cpu_percent'], 80,
                                 f"High CPU usage: {latest_cpu['cpu_percent']:.1f}%",
                                 ["Optimize CPU-intensive operations", "Add more processing power"])
        
        # Check operation times
        for operation, times in self._operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > 5.0:  # 5 second threshold
                    self._create_alert('medium', 'operation', operation,
                                     avg_time, 5.0,
                                     f"Slow operation {operation}: {avg_time:.2f}s average",
                                     ["Optimize operation", "Add caching", "Use background processing"])
    
    def _create_alert(self, severity: str, component: str, metric: str, 
                     value: float, threshold: float, message: str, 
                     recommendations: List[str] = None):
        """Create a performance alert."""
        alert = BottleneckAlert(
            severity=severity,
            component=component,
            metric=metric,
            value=value,
            threshold=threshold,
            message=message,
            timestamp=time.time(),
            recommendations=recommendations or []
        )
        
        with self._lock:
            self._alerts.append(alert)
        
        # Notify alert handlers
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Performance alert: {message}")
    
    def _cleanup_old_data(self):
        """Cleanup old performance data."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # Keep 1 hour of data
        
        # Cleanup operation times (keep last 100 measurements)
        for operation in self._operation_times:
            if len(self._operation_times[operation]) > 100:
                self._operation_times[operation] = self._operation_times[operation][-100:]
    
    def _record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        with self._lock:
            self._metrics[name].append(metric)
    
    def record_operation_time(self, operation: str, duration: float):
        """Record operation execution time."""
        self._operation_times[operation].append(duration)
        
        # Also record as metric
        self._record_metric(f"operation_{operation}_duration", duration, {'operation': operation})
    
    def set_threshold(self, metric: str, threshold: float, severity: str = 'medium'):
        """Set performance threshold for a metric."""
        self._thresholds[metric] = {
            'threshold': threshold,
            'severity': severity
        }
    
    def add_alert_handler(self, handler: Callable[[BottleneckAlert], None]):
        """Add alert handler."""
        self._alert_handlers.append(handler)
    
    def get_metrics(self, metric_name: str = None, since: float = None) -> List[PerformanceMetric]:
        """Get performance metrics."""
        with self._lock:
            if metric_name:
                if since:
                    return [m for m in self._metrics[metric_name] if m.timestamp >= since]
                return list(self._metrics[metric_name])
            else:
                # Return all metrics
                all_metrics = []
                for metrics in self._metrics.values():
                    if since:
                        all_metrics.extend([m for m in metrics if m.timestamp >= since])
                    else:
                        all_metrics.extend(metrics)
                return all_metrics
    
    def get_alerts(self, severity: str = None, since: float = None) -> List[BottleneckAlert]:
        """Get performance alerts."""
        with self._lock:
            alerts = list(self._alerts)
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            if since:
                alerts = [a for a in alerts if a.timestamp >= since]
            
            return alerts
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system performance summary."""
        summary = {
            'timestamp': time.time(),
            'memory': {},
            'cpu': {},
            'operations': {},
            'alerts': {}
        }
        
        # Memory summary
        if self._memory_usage:
            latest_memory = self._memory_usage[-1]
            summary['memory'] = {
                'used_percent': latest_memory['used_percent'],
                'used_mb': latest_memory['used_mb'],
                'available_mb': latest_memory['available_mb']
            }
        
        # CPU summary
        if self._cpu_usage:
            latest_cpu = self._cpu_usage[-1]
            summary['cpu'] = {
                'cpu_percent': latest_cpu['cpu_percent']
            }
        
        # Operation summary
        for operation, times in self._operation_times.items():
            if times:
                summary['operations'][operation] = {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times),
                    'min_time': min(times)
                }
        
        # Alert summary
        with self._lock:
            recent_alerts = [a for a in self._alerts if time.time() - a.timestamp < 300]  # Last 5 minutes
            summary['alerts'] = {
                'total': len(recent_alerts),
                'by_severity': defaultdict(int)
            }
            for alert in recent_alerts:
                summary['alerts']['by_severity'][alert.severity] += 1
        
        return summary
    
    def get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        # Memory recommendations
        if self._memory_usage:
            latest_memory = self._memory_usage[-1]
            if latest_memory['used_percent'] > 80:
                recommendations.append("High memory usage detected. Consider clearing caches or optimizing memory usage.")
        
        # CPU recommendations
        if self._cpu_usage:
            latest_cpu = self._cpu_usage[-1]
            if latest_cpu['cpu_percent'] > 70:
                recommendations.append("High CPU usage detected. Consider optimizing CPU-intensive operations.")
        
        # Operation recommendations
        for operation, times in self._operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > 3.0:
                    recommendations.append(f"Slow operation '{operation}' detected (avg: {avg_time:.2f}s). Consider optimization.")
        
        # Alert-based recommendations
        recent_alerts = self.get_alerts(since=time.time() - 300)  # Last 5 minutes
        for alert in recent_alerts:
            recommendations.extend(alert.recommendations)
        
        return list(set(recommendations))  # Remove duplicates

def performance_timer(operation_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                _global_monitor.record_operation_time(operation_name, duration)
        return wrapper
    return decorator

def performance_monitor_route(route_name: str):
    """Decorator to monitor Flask route performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Record error
                _global_monitor._record_metric(f"route_{route_name}_error", 1, {'route': route_name})
                raise
            finally:
                duration = time.time() - start_time
                _global_monitor.record_operation_time(f"route_{route_name}", duration)
                _global_monitor._record_metric(f"route_{route_name}_response_time", duration, {'route': route_name})
        return wrapper
    return decorator

class DatabasePerformanceMonitor:
    """Specialized monitor for database performance."""
    
    def __init__(self):
        self._query_times = defaultdict(list)
        self._slow_queries = []
        self._lock = threading.Lock()
    
    def record_query(self, query_type: str, duration: float, rows_affected: int = 0):
        """Record database query performance."""
        with self._lock:
            self._query_times[query_type].append({
                'duration': duration,
                'rows_affected': rows_affected,
                'timestamp': time.time()
            })
            
            # Track slow queries
            if duration > 1.0:  # Queries slower than 1 second
                self._slow_queries.append({
                    'query_type': query_type,
                    'duration': duration,
                    'rows_affected': rows_affected,
                    'timestamp': time.time()
                })
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries."""
        with self._lock:
            return sorted(self._slow_queries, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_query_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get query performance statistics."""
        with self._lock:
            stats = {}
            for query_type, queries in self._query_times.items():
                if queries:
                    durations = [q['duration'] for q in queries]
                    stats[query_type] = {
                        'count': len(queries),
                        'avg_duration': sum(durations) / len(durations),
                        'max_duration': max(durations),
                        'min_duration': min(durations)
                    }
            return stats

# Global instances
_global_monitor = PerformanceMonitor()
_global_db_monitor = DatabasePerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor."""
    return _global_monitor

def get_database_monitor() -> DatabasePerformanceMonitor:
    """Get global database performance monitor."""
    return _global_db_monitor

def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        'system': _global_monitor.get_system_summary(),
        'database': _global_db_monitor.get_query_stats(),
        'recommendations': _global_monitor.get_recommendations(),
        'recent_alerts': _global_monitor.get_alerts(since=time.time() - 300)
    }

def start_performance_monitoring():
    """Start global performance monitoring."""
    _global_monitor.start_monitoring()

def stop_performance_monitoring():
    """Stop global performance monitoring."""
    _global_monitor.stop_monitoring()
