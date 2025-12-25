#!/usr/bin/env python3
"""
Gmail Automation - Вход через EMAIL/PASSWORD
Автоматическая отправка писем через Gmail с входом по паролю

✅ Вход через email и пароль
✅ Поддержка доп. почты для проверки
✅ Поддержка 2FA через 2fa.online
✅ Множественные аккаунты

Требования:
- pip install selenium webdriver-manager

Структура:
- accounts/      - Файлы с аккаунтами (email, password, доп. почта, 2FA)
- emails/        - emails.txt с адресами получателей  
- text/          - text.txt с текстом сообщения

Управление:
- I - Inbox режим
- R - Возобновить
- Q - Выход
"""

import os
import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gmail_password import GmailPasswordClient, load_accounts_from_file, check_selenium_installed
    PASSWORD_AVAILABLE = True
except ImportError:
    PASSWORD_AVAILABLE = False
    GmailPasswordClient = None
    load_accounts_from_file = lambda x: []
    check_selenium_installed = lambda: False

from email_manager import EmailManager
from message_template import MessageTemplate
from response_checker import ResponseChecker


class GmailAutomationPassword:
    """Gmail automation with password authentication"""
    
    def __init__(self):
        """Initialize"""
        self.base_dir = Path(__file__).parent
        
        # Check Selenium
        if not PASSWORD_AVAILABLE or not check_selenium_installed():
            print("❌ Selenium не установлен!")
            print("📦 Установите: pip install selenium webdriver-manager")
            sys.exit(1)
        
        # Load accounts
        accounts_dir = self.base_dir / 'accounts'
        self.accounts = []
        
        if accounts_dir.exists():
            for file in accounts_dir.glob('*.txt'):
                accs = load_accounts_from_file(str(file))
                self.accounts.extend(accs)
        
        if not self.accounts:
            print("❌ Нет аккаунтов в папке accounts/")
            print("   Создайте файлы .txt с данными аккаунтов")
            print("   См. accounts/example.txt для примера")
            sys.exit(1)
        
        # Initialize managers
        self.email_manager = EmailManager(str(self.base_dir / 'emails' / 'emails.txt'))
        self.message_template = MessageTemplate(str(self.base_dir / 'text' / 'text.txt'))
        self.response_checker = ResponseChecker()
        
        # Browser clients
        self.browser_clients = {}
        self.current_account_index = 0
        
        # State
        self.is_running = False
        self.is_paused = False
        
        # Stats
        self.emails_sent = 0
        self.emails_failed = 0
        
        # Keyboard
        self.user_command = None
        self.command_lock = threading.Lock()
    
    def _print_header(self):
        """Print header"""
        print("\n" + "="*60)
        print("📧 Gmail Automation - ВХОД ПО EMAIL/PASSWORD")
        print("="*60)
        print("✅ Вход через пароль")
        print("✅ Поддержка доп. почты")
        print("✅ Поддержка 2FA")
        print("="*60)
        print("Управление:")
        print("  I - Inbox режим")
        print("  R - Возобновить")
        print("  Q - Выход")
        print("="*60 + "\n")
    
    def _listen_for_commands(self):
        """Listen for keyboard commands"""
        # Import platform-specific modules once
        if sys.platform == 'win32':
            import msvcrt
            win_module = msvcrt
        else:
            import select
            unix_module = select
        
        while self.is_running:
            try:
                if sys.platform == 'win32':
                    if win_module.kbhit():
                        try:
                            key = win_module.getch().decode('utf-8').upper()
                            with self.command_lock:
                                self.user_command = key
                        except:
                            pass
                else:
                    ready, _, _ = unix_module.select([sys.stdin], [], [], 0.1)
                    if ready:
                        try:
                            key = sys.stdin.read(1).upper()
                            with self.command_lock:
                                self.user_command = key
                        except:
                            pass
                time.sleep(0.1)
            except:
                time.sleep(0.1)
    
    def _process_commands(self):
        """Process commands"""
        with self.command_lock:
            if self.user_command:
                cmd = self.user_command
                self.user_command = None
                
                if cmd == 'I':
                    self._inbox_mode()
                elif cmd == 'R':
                    self._resume_mode()
                elif cmd == 'Q':
                    self._quit()
                    return False
        return True
    
    def _inbox_mode(self):
        """Inbox mode"""
        print("\n" + "="*60)
        print("📥 INBOX РЕЖИМ")
        print("="*60)
        
        self.is_paused = True
        target_email = input("Введите email получателя: ").strip()
        
        if not target_email:
            print("⚠️ Email не указан")
            self.is_paused = False
            return
        
        print(f"\n📧 Отправка на {target_email}...")
        
        # Get account
        account = self.accounts[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        
        try:
            # Get or create client
            acc_key = account['email']
            if acc_key not in self.browser_clients:
                self.browser_clients[acc_key] = GmailPasswordClient(
                    email=account['email'],
                    password=account['password'],
                    backup_email=account.get('backup_email'),
                    twofa_code=account.get('twofa_code')
                )
            
            client = self.browser_clients[acc_key]
            
            # Send
            message = self.message_template.get_message()
            subject = "Привет!"
            
            success = client.send_email(target_email, subject, message)
            
            if success:
                print(f"✅ Отправлено")
                self.emails_sent += 1
            else:
                print(f"❌ Не удалось отправить")
                self.emails_failed += 1
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.emails_failed += 1
        
        print("\nНажмите R для возобновления")
    
    def _resume_mode(self):
        """Resume"""
        print("\n✅ Возобновление...\n")
        self.is_paused = False
    
    def _quit(self):
        """Quit"""
        print("\n👋 Завершение...")
        self.is_running = False
    
    def _send_next_email(self):
        """Send next email"""
        target_email = self.email_manager.get_next_email()
        if not target_email:
            print("\n✅ Все email обработаны!")
            return False
        
        # Get account
        account = self.accounts[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        
        try:
            # Get or create client
            acc_key = account['email']
            if acc_key not in self.browser_clients:
                print(f"\n🌐 Вход в аккаунт {account['email']}...")
                self.browser_clients[acc_key] = GmailPasswordClient(
                    email=account['email'],
                    password=account['password'],
                    backup_email=account.get('backup_email'),
                    twofa_code=account.get('twofa_code'),
                    headless=True
                )
            
            client = self.browser_clients[acc_key]
            
            # Get message
            message = self.message_template.get_message(EMAIL=target_email)
            subject = "Привет!"
            
            # Progress
            current, total = self.email_manager.get_progress()
            print(f"\n[{current}/{total}] 📧 Отправка на {target_email}...")
            print(f"   От: {account['email']}")
            
            # Send
            success = client.send_email(target_email, subject, message)
            
            if success:
                print(f"   ✅ Успешно отправлено!")
                self.emails_sent += 1
            else:
                print(f"   ❌ Не удалось отправить")
                self.emails_failed += 1
            
            # Delay
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            self.emails_failed += 1
            return True
    
    def _cleanup(self):
        """Cleanup"""
        print("\n🔒 Закрытие браузеров...")
        for client in self.browser_clients.values():
            try:
                client.close()
            except:
                pass
    
    def run(self):
        """Main run loop"""
        self._print_header()
        
        # Validate
        if not self.email_manager.has_more_emails():
            print("❌ Нет email в emails/emails.txt")
            return
        
        print(f"✅ Готов к работе!")
        print(f"   Аккаунтов: {len(self.accounts)}")
        print(f"   Email адресов: {self.email_manager.get_progress()[1]}")
        print()
        
        # Start
        self.is_running = True
        command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        command_thread.start()
        
        try:
            while self.is_running:
                if not self._process_commands():
                    break
                
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                
                if not self._send_next_email():
                    break
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Прервано пользователем")
        
        finally:
            self.is_running = False
            self._cleanup()
            self._print_stats()
    
    def _print_stats(self):
        """Print stats"""
        print("\n" + "="*60)
        print("📊 Статистика")
        print("="*60)
        print(f"Отправлено: {self.emails_sent}")
        print(f"Ошибки: {self.emails_failed}")
        print(f"Всего: {self.emails_sent + self.emails_failed}")
        print("="*60 + "\n")


def main():
    """Main"""
    automation = GmailAutomationPassword()
    automation.run()


if __name__ == "__main__":
    main()
