"""Configuration settings for Gmail automation"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Directories
COOKIES_DIR = BASE_DIR / 'cookies'
EMAILS_DIR = BASE_DIR / 'emails'
TEXT_DIR = BASE_DIR / 'text'
PROXIES_DIR = BASE_DIR / 'proxies'

# Files
EMAILS_FILE = EMAILS_DIR / 'emails.txt'
TEXT_FILE = TEXT_DIR / 'text.txt'
PROXIES_FILE = PROXIES_DIR / 'proxies.txt'

# Email settings
DEFAULT_SUBJECT = "Привет!"
SEND_DELAY = 2  # Seconds between sends
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed sends

# Response checker settings
RESPONSE_CHECK_INTERVAL = 60  # Seconds between response checks

# Proxy settings
USE_PROXIES = True  # Set to False to disable proxy usage
PROXY_ROTATION = "sequential"  # "sequential" or "random"

# Account rotation settings
ACCOUNT_ROTATION = "sequential"  # "sequential" or "round_robin"

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
SHOW_EMAIL_CONTENT = False  # Show email content in logs

# Terminal settings
ENABLE_COLORS = True  # Enable colored terminal output
CLEAR_SCREEN = False  # Clear screen before starting

# Performance
MAX_RETRIES_PER_EMAIL = 3
TIMEOUT_SECONDS = 30
