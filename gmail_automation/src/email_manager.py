"""Email queue and account manager"""
from typing import List, Optional
import os


class EmailManager:
    """Manages email addresses and account rotation"""
    
    def __init__(self, emails_file: str):
        """
        Initialize email manager
        
        Args:
            emails_file: Path to file containing email addresses (one per line)
        """
        self.emails_file = emails_file
        self.emails: List[str] = []
        self.current_index = 0
        self._load_emails()
    
    def _load_emails(self):
        """Load emails from file"""
        try:
            with open(self.emails_file, 'r', encoding='utf-8') as f:
                self.emails = [line.strip() for line in f if line.strip()]
            print(f"✅ Загружено {len(self.emails)} email адресов")
        except Exception as e:
            print(f"❌ Ошибка загрузки email из {self.emails_file}: {e}")
            self.emails = []
    
    def get_next_email(self) -> Optional[str]:
        """Get next email from queue"""
        if not self.emails:
            return None
        
        if self.current_index >= len(self.emails):
            return None
        
        email = self.emails[self.current_index]
        self.current_index += 1
        return email
    
    def reset(self):
        """Reset to beginning of email list"""
        self.current_index = 0
    
    def has_more_emails(self) -> bool:
        """Check if there are more emails to process"""
        return self.current_index < len(self.emails)
    
    def get_progress(self) -> tuple[int, int]:
        """Get progress (current, total)"""
        return (self.current_index, len(self.emails))


class AccountManager:
    """Manages Gmail accounts from cookie files"""
    
    def __init__(self, cookies_dir: str):
        """
        Initialize account manager
        
        Args:
            cookies_dir: Directory containing cookie JSON files
        """
        self.cookies_dir = cookies_dir
        self.accounts: List[str] = []
        self.current_account_index = 0
        self._load_accounts()
    
    def _load_accounts(self):
        """Load cookie files from directory"""
        try:
            if not os.path.exists(self.cookies_dir):
                os.makedirs(self.cookies_dir)
                print(f"⚠️ Создана папка {self.cookies_dir}")
                print(f"⚠️ Добавьте cookie файлы в папку cookies/")
                return
            
            # Find all .json and .txt files
            for filename in os.listdir(self.cookies_dir):
                if filename.endswith(('.json', '.txt')):
                    filepath = os.path.join(self.cookies_dir, filename)
                    self.accounts.append(filepath)
            
            if self.accounts:
                print(f"✅ Найдено {len(self.accounts)} аккаунтов в {self.cookies_dir}")
            else:
                print(f"⚠️ Не найдено cookie файлов в {self.cookies_dir}")
                print(f"⚠️ Добавьте файлы с cookie в формате JSON")
        except Exception as e:
            print(f"❌ Ошибка загрузки аккаунтов: {e}")
            self.accounts = []
    
    def get_next_account(self) -> Optional[str]:
        """Get next account cookie file, cycling through accounts"""
        if not self.accounts:
            return None
        
        account = self.accounts[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        return account
    
    def get_account_count(self) -> int:
        """Get total number of accounts"""
        return len(self.accounts)
    
    def reload_accounts(self):
        """Reload accounts from directory"""
        self.accounts = []
        self.current_account_index = 0
        self._load_accounts()
