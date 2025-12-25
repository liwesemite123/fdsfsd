"""Logging utilities for Gmail automation"""
from datetime import datetime
from typing import Optional


class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class Logger:
    """Simple logger for Gmail automation"""
    
    def __init__(self, enable_colors: bool = True):
        """Initialize logger"""
        self.enable_colors = enable_colors
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text if colors are enabled"""
        if not self.enable_colors:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def _timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().strftime('%H:%M:%S')
    
    def success(self, message: str, prefix: str = "✅"):
        """Log success message"""
        print(self._colorize(f"{prefix} {message}", Colors.GREEN))
    
    def error(self, message: str, prefix: str = "❌"):
        """Log error message"""
        print(self._colorize(f"{prefix} {message}", Colors.RED))
    
    def warning(self, message: str, prefix: str = "⚠️"):
        """Log warning message"""
        print(self._colorize(f"{prefix} {message}", Colors.YELLOW))
    
    def info(self, message: str, prefix: str = "ℹ️"):
        """Log info message"""
        print(f"{prefix} {message}")
    
    def debug(self, message: str):
        """Log debug message"""
        print(self._colorize(f"[DEBUG {self._timestamp()}] {message}", Colors.CYAN))
    
    def header(self, message: str):
        """Log header message"""
        print("\n" + "="*60)
        print(self._colorize(message, Colors.BOLD))
        print("="*60)
    
    def progress(self, current: int, total: int, message: str):
        """Log progress message"""
        percentage = (current / total * 100) if total > 0 else 0
        print(f"[{current}/{total} - {percentage:.1f}%] {message}")
    
    def notification(self, title: str, message: str):
        """Log notification"""
        print("\n" + "="*60)
        print(self._colorize(f"🔔 {title}", Colors.BOLD + Colors.BLUE))
        print("="*60)
        print(message)
        print("="*60 + "\n")


# Global logger instance
logger = Logger()
