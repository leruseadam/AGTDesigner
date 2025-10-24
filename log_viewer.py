#!/usr/bin/env python3
"""
Enhanced Log Viewer
Makes web error logs easier to read and analyze
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
import argparse

class LogViewer:
    """Enhanced log viewer with filtering and formatting"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.error_log = self.log_dir / "errors.log"
        self.app_log = self.log_dir / "app.log"
        self.legacy_log = self.log_dir / "label_maker.log"
    
    def get_log_files(self):
        """Get available log files"""
        files = []
        for log_file in [self.error_log, self.app_log, self.legacy_log]:
            if log_file.exists():
                files.append(log_file)
        return files
    
    def parse_log_line(self, line):
        """Parse a log line into structured data"""
        # Enhanced log format: timestamp | level | name | filename:line | function | message
        enhanced_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)\s+\| ([^|]+) \| ([^:]+):(\d+)\s+\| ([^|]+) \| (.+)'
        
        # Legacy format: timestamp - name - level - message
        legacy_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - ([^-]+) - (\w+) - (.+)'
        
        enhanced_match = re.match(enhanced_pattern, line)
        if enhanced_match:
            return {
                'timestamp': enhanced_match.group(1),
                'level': enhanced_match.group(2),
                'name': enhanced_match.group(3).strip(),
                'filename': enhanced_match.group(4).strip(),
                'line': int(enhanced_match.group(5)),
                'function': enhanced_match.group(6).strip(),
                'message': enhanced_match.group(7),
                'type': 'enhanced'
            }
        
        legacy_match = re.match(legacy_pattern, line)
        if legacy_match:
            return {
                'timestamp': legacy_match.group(1).split(',')[0],
                'level': legacy_match.group(3),
                'name': legacy_match.group(2).strip(),
                'filename': 'unknown',
                'line': 0,
                'function': 'unknown',
                'message': legacy_match.group(4),
                'type': 'legacy'
            }
        
        return None
    
    def format_log_entry(self, entry, show_context=True):
        """Format a log entry for display"""
        if not entry:
            return None
        
        # Color codes
        colors = {
            'ERROR': '\033[31m',    # Red
            'WARNING': '\033[33m',  # Yellow
            'INFO': '\033[32m',     # Green
            'DEBUG': '\033[36m',    # Cyan
            'RESET': '\033[0m'      # Reset
        }
        
        color = colors.get(entry['level'], colors['RESET'])
        reset = colors['RESET']
        
        # Format timestamp
        timestamp = entry['timestamp']
        
        # Format based on log type
        if entry['type'] == 'enhanced':
            formatted = f"{color}🚨 {entry['level']:8} [{timestamp}] {entry['name']}{reset}\n"
            if show_context:
                formatted += f"   📍 {entry['filename']}:{entry['line']} in {entry['function']}()\n"
            formatted += f"   💬 {entry['message']}{reset}\n"
        else:
            formatted = f"{color}📝 {entry['level']:8} [{timestamp}] {entry['name']}{reset}\n"
            formatted += f"   💬 {entry['message']}{reset}\n"
        
        return formatted
    
    def filter_logs(self, log_file, level=None, name=None, search=None, hours=None):
        """Filter logs based on criteria"""
        if not log_file.exists():
            return []
        
        entries = []
        cutoff_time = None
        
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                entry = self.parse_log_line(line)
                if not entry:
                    continue
                
                # Apply filters
                if level and entry['level'] != level:
                    continue
                
                if name and name.lower() not in entry['name'].lower():
                    continue
                
                if search and search.lower() not in entry['message'].lower():
                    continue
                
                if cutoff_time:
                    try:
                        entry_time = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                        if entry_time < cutoff_time:
                            continue
                    except ValueError:
                        continue
                
                entries.append(entry)
        
        return entries
    
    def show_errors(self, hours=24, search=None):
        """Show recent errors"""
        print("🔍 Recent Errors")
        print("=" * 50)
        
        all_errors = []
        for log_file in self.get_log_files():
            errors = self.filter_logs(log_file, level='ERROR', hours=hours, search=search)
            all_errors.extend(errors)
        
        if not all_errors:
            print("✅ No errors found in the specified time range")
            return
        
        # Sort by timestamp (newest first)
        all_errors.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for entry in all_errors[:20]:  # Show last 20 errors
            formatted = self.format_log_entry(entry)
            if formatted:
                print(formatted)
    
    def show_warnings(self, hours=24, search=None):
        """Show recent warnings"""
        print("⚠️  Recent Warnings")
        print("=" * 50)
        
        all_warnings = []
        for log_file in self.get_log_files():
            warnings = self.filter_logs(log_file, level='WARNING', hours=hours, search=search)
            all_warnings.extend(warnings)
        
        if not all_warnings:
            print("✅ No warnings found in the specified time range")
            return
        
        # Sort by timestamp (newest first)
        all_warnings.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for entry in all_warnings[:20]:  # Show last 20 warnings
            formatted = self.format_log_entry(entry)
            if formatted:
                print(formatted)
    
    def show_recent(self, hours=1, level=None, search=None):
        """Show recent log entries"""
        print(f"📋 Recent Log Entries (last {hours} hour{'s' if hours != 1 else ''})")
        print("=" * 50)
        
        all_entries = []
        for log_file in self.get_log_files():
            entries = self.filter_logs(log_file, level=level, hours=hours, search=search)
            all_entries.extend(entries)
        
        if not all_entries:
            print("✅ No log entries found in the specified time range")
            return
        
        # Sort by timestamp (newest first)
        all_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for entry in all_entries[:50]:  # Show last 50 entries
            formatted = self.format_log_entry(entry)
            if formatted:
                print(formatted)
    
    def search_logs(self, search_term, hours=24, level=None):
        """Search logs for specific terms"""
        print(f"🔍 Searching logs for: '{search_term}'")
        print("=" * 50)
        
        all_matches = []
        for log_file in self.get_log_files():
            matches = self.filter_logs(log_file, level=level, hours=hours, search=search_term)
            all_matches.extend(matches)
        
        if not all_matches:
            print(f"❌ No matches found for '{search_term}'")
            return
        
        # Sort by timestamp (newest first)
        all_matches.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for entry in all_matches[:30]:  # Show last 30 matches
            formatted = self.format_log_entry(entry)
            if formatted:
                print(formatted)
    
    def show_stats(self, hours=24):
        """Show log statistics"""
        print(f"📊 Log Statistics (last {hours} hours)")
        print("=" * 50)
        
        stats = {'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'DEBUG': 0}
        total_entries = 0
        
        for log_file in self.get_log_files():
            entries = self.filter_logs(log_file, hours=hours)
            for entry in entries:
                level = entry['level']
                if level in stats:
                    stats[level] += 1
                total_entries += 1
        
        print(f"Total entries: {total_entries}")
        for level, count in stats.items():
            if count > 0:
                print(f"{level:8}: {count:4} entries")
    
    def tail_logs(self, lines=20, follow=False):
        """Show last N lines of logs (like tail -f)"""
        print(f"📄 Last {lines} log entries")
        print("=" * 50)
        
        all_entries = []
        for log_file in self.get_log_files():
            entries = self.filter_logs(log_file)
            all_entries.extend(entries)
        
        # Sort by timestamp (newest first)
        all_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for entry in all_entries[:lines]:
            formatted = self.format_log_entry(entry)
            if formatted:
                print(formatted)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Enhanced Log Viewer for Label Maker')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--hours', type=int, default=24, help='Time range in hours')
    parser.add_argument('--level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'], help='Filter by log level')
    parser.add_argument('--search', help='Search term')
    parser.add_argument('--tail', type=int, help='Show last N lines')
    parser.add_argument('--stats', action='store_true', help='Show log statistics')
    
    args = parser.parse_args()
    
    viewer = LogViewer(args.log_dir)
    
    if args.stats:
        viewer.show_stats(args.hours)
    elif args.tail:
        viewer.tail_logs(args.tail)
    elif args.search:
        viewer.search_logs(args.search, args.hours, args.level)
    elif args.level == 'ERROR':
        viewer.show_errors(args.hours, args.search)
    elif args.level == 'WARNING':
        viewer.show_warnings(args.hours, args.search)
    else:
        viewer.show_recent(args.hours, args.level, args.search)

if __name__ == "__main__":
    main()
