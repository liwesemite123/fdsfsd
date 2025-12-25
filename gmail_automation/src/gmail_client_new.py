"""Gmail client with App Password support for real email sending"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, List
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailClient:
    """Gmail client for sending emails via SMTP with App Password"""
    
    def __init__(self, email: str, app_password: str, proxy: Optional[str] = None):
        """
        Initialize Gmail client
        
        Args:
            email: Gmail email address
            app_password: Gmail App Password (16 characters from myaccount.google.com/apppasswords)
            proxy: Proxy string (not used for SMTP)
        """
        self.email = email
        self.app_password = app_password.replace(' ', '')  # Remove spaces from app password
        self.proxy = proxy
        
        print(f"✅ Инициализирован аккаунт: {email}")
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = to_email
            
            # Add body
            part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part)
            
            # Send via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
                server.login(self.email, self.app_password)
                server.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Ошибка аутентификации для {self.email}")
            print(f"   Проверьте App Password: https://myaccount.google.com/apppasswords")
            print(f"   Убедитесь что:")
            print(f"   1. Включена 2FA (двухфакторная аутентификация)")
            print(f"   2. App Password создан для 'Mail'")
            print(f"   3. App Password скопирован без пробелов")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP ошибка: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка отправки на {to_email}: {e}")
            return False
    
    def check_new_messages(self) -> List[Dict]:
        """
        Check for new messages/replies
        
        Returns:
            List of new messages (not implemented for SMTP-only client)
        """
        # For checking messages, would need IMAP access
        # This is a placeholder
        return []
    
    def get_account_info(self) -> Optional[str]:
        """Get account email"""
        return self.email


# Legacy cookie-based client (kept for compatibility)
class GmailClientLegacy:
    """Gmail client using cookie-based authentication (DEMO ONLY)"""
    
    def __init__(self, cookie_file: str, proxy: Optional[str] = None):
        """
        Initialize Gmail client with cookies
        
        Note: Cookies alone cannot send emails. Use GmailClient with App Password instead.
        
        Args:
            cookie_file: Path to cookie JSON file
            proxy: Proxy string
        """
        self.cookie_file = cookie_file
        self.proxy = proxy
        self.cookies = {}
        self.account_email = None
        
        print(f"⚠️ Cookie-based auth НЕ РАБОТАЕТ для отправки писем!")
        print(f"⚠️ Используйте App Password (см. REAL_SENDING.md)")
        print(f"⚠️ Работа в ДЕМО режиме")
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """DEMO: Simulates sending (does not actually send)"""
        print(f"📧 [ДЕМО] Симуляция отправки на {to_email}")
        print(f"   Тема: {subject}")
        time.sleep(1)
        return True
    
    def check_new_messages(self) -> List[Dict]:
        """Placeholder"""
        return []
    
    def get_account_info(self) -> Optional[str]:
        """Get account email from cookies"""
        return self.account_email or "demo@gmail.com"


def load_accounts_from_json(filepath: str = "accounts.json") -> List[Dict]:
    """
    Load email accounts from JSON file
    
    Args:
        filepath: Path to accounts.json file
        
    Returns:
        List of account dicts with 'email' and 'app_password'
    """
    if not os.path.exists(filepath):
        print(f"⚠️ Файл {filepath} не найден")
        print(f"⚠️ Создайте accounts.json с вашими App Passwords")
        print(f"⚠️ См. REAL_SENDING.md для инструкций")
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not isinstance(accounts, list):
            print(f"❌ Неверный формат {filepath} - должен быть список")
            return []
        
        valid_accounts = []
        for acc in accounts:
            if 'email' in acc and 'app_password' in acc:
                valid_accounts.append(acc)
            else:
                print(f"⚠️ Пропущен аккаунт без email или app_password")
        
        return valid_accounts
    except Exception as e:
        print(f"❌ Ошибка загрузки {filepath}: {e}")
        return []
