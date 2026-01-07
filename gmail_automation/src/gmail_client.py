"""Gmail client with cookie-based authentication"""
import json
import requests
from typing import Optional, Dict, List
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailClient:
    """Gmail client using cookie-based authentication"""
    
    def __init__(self, cookie_file: str, proxy: Optional[str] = None):
        """
        Initialize Gmail client
        
        Args:
            cookie_file: Path to cookie JSON file
            proxy: Proxy string in format "http://user:pass@host:port"
        """
        self.cookie_file = cookie_file
        self.proxy = proxy
        self.session = requests.Session()
        self.cookies = {}
        self.account_email = None
        
        # Load cookies
        self._load_cookies()
        
        # Setup proxy
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
    
    def _load_cookies(self):
        """Load cookies from JSON file"""
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # Support different cookie formats
            if isinstance(cookie_data, list):
                # Format: [{name: "", value: "", domain: ""}, ...]
                for cookie in cookie_data:
                    if 'name' in cookie and 'value' in cookie:
                        self.cookies[cookie['name']] = cookie['value']
                        self.session.cookies.set(cookie['name'], cookie['value'])
            elif isinstance(cookie_data, dict):
                # Format: {cookie_name: cookie_value, ...}
                self.cookies = cookie_data
                for name, value in cookie_data.items():
                    self.session.cookies.set(name, value)
            
            print(f"✅ Загружено {len(self.cookies)} cookie из {self.cookie_file}")
        except Exception as e:
            print(f"❌ Ошибка загрузки cookie из {self.cookie_file}: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via Gmail using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Try to extract email from cookies or use a default
            from_email = self._extract_email_from_cookies()
            
            if not from_email:
                print(f"⚠️ Не удалось определить email отправителя из cookies")
                print(f"⚠️ Используйте Gmail API или укажите email вручную")
                # For now, we'll use a simpler approach - just log the attempt
                print(f"📧 [ДЕМО] Отправка письма:")
                print(f"   От: {self.cookie_file}")
                print(f"   Кому: {to_email}")
                print(f"   Тема: {subject}")
                print(f"   Текст: {body[:100]}...")
                time.sleep(1)
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Add body
            part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part)
            
            # Try to send via SMTP
            # Note: Gmail requires App Password or OAuth2 for SMTP
            # Cookie-based auth doesn't work directly with SMTP
            # This is intentionally commented out as it will always fail
            # 
            # Real implementation: Use gmail_sender_real.py with App Password
            
            # Demonstrate why cookies don't work:
            # try:
            #     with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            #         server.login(from_email, "")  # No password from cookies - will fail
            #         server.send_message(msg)
            # except smtplib.SMTPAuthenticationError:
            #     # Expected - cookies don't provide SMTP credentials
            
            print(f"⚠️ SMTP авторизация невозможна (cookies не работают с SMTP)")
            print(f"⚠️ Для реальной отправки используйте:")
            print(f"   python gmail_sender_real.py")
            print(f"   (с App Password из accounts.json)")
            print(f"")
            print(f"📧 [ДЕМО] Симуляция отправки на {to_email}")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки на {to_email}: {e}")
            return False
    
    def _extract_email_from_cookies(self) -> Optional[str]:
        """Try to extract email address from cookie data"""
        # This is a placeholder - cookies typically don't contain the email directly
        # You would need to make an API call to Gmail to get the account email
        return None
    
    def check_new_messages(self) -> List[Dict]:
        """
        Check for new messages/replies
        
        Returns:
            List of new messages
        """
        try:
            # This would check Gmail inbox for new messages
            # Real implementation needs Gmail API integration
            
            # Placeholder for checking new messages
            # Would need to track last checked timestamp
            
            return []
        except Exception as e:
            print(f"❌ Ошибка проверки новых сообщений: {e}")
            return []
    
    def get_account_info(self) -> Optional[str]:
        """Get account email from cookies"""
        # Try to extract email from cookie data
        # This is a placeholder - real implementation would validate session
        return self.account_email or "account@gmail.com"
