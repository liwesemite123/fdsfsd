"""Gmail Automation Script - Source Package"""

__version__ = "1.0.0"
__author__ = "Gmail Automation"

from .gmail_client import GmailClient
from .email_manager import EmailManager, AccountManager
from .proxy_manager import ProxyManager
from .message_template import MessageTemplate
from .response_checker import ResponseChecker

__all__ = [
    'GmailClient',
    'EmailManager',
    'AccountManager',
    'ProxyManager',
    'MessageTemplate',
    'ResponseChecker',
]
