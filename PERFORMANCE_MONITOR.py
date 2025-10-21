#!/usr/bin/env python3
"""
PERFORMANCE MONITOR
Monitors Excel processing performance and provides optimization recommendations
"""

import time
import os
import logging
from typing import Dict, Any, List
import pandas as pd

class PerformanceMonitor:
    """Monitor and analyze Excel processing performance"""
    
    def __init__(self):
        self.performance_log = []
        self.benchmarks = {
            'excellent': 5.0,    # < 5 seconds
            'good': 15.0,        # < 15 seconds  
            'acceptable': 30.0,  # < 30 seconds
            'slow': 60.0,        # < 60 seconds
            'very_slow': float('inf')  # > 60 seconds
        }
    
    def log_processing(self, filename: str, file_size_mb: float, 
                      rows_processed: int, processing_time: float, 
                      method: str = 'unknown') -> Dict[str, Any]:
        """Log a processing event"""
        
        # Calculate performance metrics
        rows_per_second = rows_processed / processing_time if processing_time > 0 else 0
        mb_per_second = file_size_mb / processing_time if processing_time > 0 else 0
        
        # Determine performance rating
        rating = self._get_performance_rating(processing_time)
        
        log_entry = {
            'timestamp': time.time(),
            'filename': filename,
            'file_size_mb': file_size_mb,
            'rows_processed': rows_processed,
            'processing_time': processing_time,
            'method': method,
            'rows_per_second': rows_per_second,
            'mb_per_second': mb_per_second,
            'rating': rating
        }
        
        self.performance_log.append(log_entry)
        
        # Log to console
        print(f"📊 PERFORMANCE LOG:")
        print(f"   File: {filename}")
        print(f"   Size: {file_size_mb:.2f} MB")
        print(f"   Rows: {rows_processed:,}")
        print(f"   Time: {processing_time:.3f}s")
        print(f"   Speed: {rows_per_second:.0f} rows/sec")
        print(f"   Rating: {rating.upper()}")
        print(f"   Method: {method}")
        
        return log_entry
    
    def _get_performance_rating(self, processing_time: float) -> str:
        """Get performance rating based on processing time"""
        if processing_time <= self.benchmarks['excellent']:
            return 'excellent'
        elif processing_time <= self.benchmarks['good']:
            return 'good'
        elif processing_time <= self.benchmarks['acceptable']:
            return 'acceptable'
        elif processing_time <= self.benchmarks['slow']:
            return 'slow'
        else:
            return 'very_slow'
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        if not self.performance_log:
            return {'message': 'No processing data available'}
        
        total_processings = len(self.performance_log)
        avg_processing_time = sum(log['processing_time'] for log in self.performance_log) / total_processings
        avg_rows_per_second = sum(log['rows_per_second'] for log in self.performance_log) / total_processings
        
        # Count by rating
        rating_counts = {}
        for log in self.performance_log:
            rating = log['rating']
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        # Find fastest and slowest
        fastest = min(self.performance_log, key=lambda x: x['processing_time'])
        slowest = max(self.performance_log, key=lambda x: x['processing_time'])
        
        return {
            'total_processings': total_processings,
            'average_processing_time': avg_processing_time,
            'average_rows_per_second': avg_rows_per_second,
            'rating_distribution': rating_counts,
            'fastest_processing': fastest,
            'slowest_processing': slowest,
            'performance_trend': self._analyze_trend()
        }
    
    def _analyze_trend(self) -> str:
        """Analyze performance trend over time"""
        if len(self.performance_log) < 2:
            return 'insufficient_data'
        
        # Compare recent vs older performance
        recent_logs = self.performance_log[-3:]  # Last 3 processings
        older_logs = self.performance_log[:-3] if len(self.performance_log) > 3 else []
        
        if not older_logs:
            return 'insufficient_data'
        
        recent_avg = sum(log['processing_time'] for log in recent_logs) / len(recent_logs)
        older_avg = sum(log['processing_time'] for log in older_logs) / len(older_logs)
        
        improvement = ((older_avg - recent_avg) / older_avg) * 100
        
        if improvement > 10:
            return f'improving ({improvement:.1f}% faster)'
        elif improvement < -10:
            return f'degrading ({abs(improvement):.1f}% slower)'
        else:
            return 'stable'
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on performance data"""
        recommendations = []
        
        if not self.performance_log:
            return ['No data available for recommendations']
        
        # Analyze recent performance
        recent_logs = self.performance_log[-5:]  # Last 5 processings
        avg_time = sum(log['processing_time'] for log in recent_logs) / len(recent_logs)
        avg_rows_per_sec = sum(log['rows_per_second'] for log in recent_logs) / len(recent_logs)
        
        if avg_time > 30:
            recommendations.append("Consider using chunked processing for large files")
        
        if avg_rows_per_sec < 1000:
            recommendations.append("Processing speed is slow - check for memory issues")
        
        # Check for method effectiveness
        method_performance = {}
        for log in self.performance_log:
            method = log['method']
            if method not in method_performance:
                method_performance[method] = []
            method_performance[method].append(log['rows_per_second'])
        
        for method, speeds in method_performance.items():
            avg_speed = sum(speeds) / len(speeds)
            if avg_speed < 500:
                recommendations.append(f"Method '{method}' is slow - consider optimization")
        
        if not recommendations:
            recommendations.append("Performance looks good! No specific recommendations.")
        
        return recommendations
    
    def print_performance_report(self):
        """Print a comprehensive performance report"""
        print("\n" + "="*60)
        print("📊 EXCEL PROCESSING PERFORMANCE REPORT")
        print("="*60)
        
        summary = self.get_performance_summary()
        
        if 'message' in summary:
            print(summary['message'])
            return
        
        print(f"Total Processings: {summary['total_processings']}")
        print(f"Average Processing Time: {summary['average_processing_time']:.3f}s")
        print(f"Average Speed: {summary['average_rows_per_second']:.0f} rows/sec")
        print(f"Performance Trend: {summary['performance_trend']}")
        
        print("\nRating Distribution:")
        for rating, count in summary['rating_distribution'].items():
            percentage = (count / summary['total_processings']) * 100
            print(f"  {rating.upper()}: {count} ({percentage:.1f}%)")
        
        print(f"\nFastest Processing:")
        fastest = summary['fastest_processing']
        print(f"  File: {fastest['filename']}")
        print(f"  Time: {fastest['processing_time']:.3f}s")
        print(f"  Speed: {fastest['rows_per_second']:.0f} rows/sec")
        
        print(f"\nSlowest Processing:")
        slowest = summary['slowest_processing']
        print(f"  File: {slowest['filename']}")
        print(f"  Time: {slowest['processing_time']:.3f}s")
        print(f"  Speed: {slowest['rows_per_second']:.0f} rows/sec")
        
        print("\nOptimization Recommendations:")
        recommendations = self.get_optimization_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("="*60)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def log_excel_processing(filename: str, file_size_mb: float, 
                       rows_processed: int, processing_time: float, 
                       method: str = 'unknown') -> Dict[str, Any]:
    """Convenience function to log Excel processing performance"""
    return performance_monitor.log_processing(filename, file_size_mb, rows_processed, processing_time, method)

def get_performance_report():
    """Get current performance report"""
    return performance_monitor.get_performance_summary()

def print_performance_report():
    """Print performance report to console"""
    performance_monitor.print_performance_report()

if __name__ == "__main__":
    # Test the performance monitor
    print("Testing Performance Monitor...")
    
    # Simulate some processing events
    log_excel_processing("test1.xlsx", 2.5, 1000, 3.2, "optimized")
    log_excel_processing("test2.xlsx", 5.1, 2500, 8.7, "lightning")
    log_excel_processing("test3.xlsx", 12.3, 5000, 25.4, "chunked")
    
    # Print report
    print_performance_report()
