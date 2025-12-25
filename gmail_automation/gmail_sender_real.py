#!/usr/bin/env python3
"""
Gmail Automation Script - РЕАЛЬНАЯ ОТПРАВКА
Автоматическая отправка писем через Gmail с использованием App Passwords

Для настройки см. REAL_SENDING.md

Структура папок:
- accounts.json  - Ваши Gmail аккаунты с App Passwords
- emails/        - Файл emails.txt с адресами получателей
- text/          - Файл text.txt с текстом сообщения
- proxies/       - Файл proxies.txt с прокси (опционально)

Управление:
- I - Режим Inbox (отправить на конкретный email)
- R - Возобновить автоматическую отправку
- Q - Выход
- Ctrl+C - Остановить скрипт
"""

import os
import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gmail_client_new import GmailClient, load_accounts_from_json
except ImportError:
    from gmail_client import GmailClient
    load_accounts_from_json = None

from email_manager import EmailManager
from proxy_manager import ProxyManager
from message_template import MessageTemplate
from response_checker import ResponseChecker


class GmailAutomationReal:
    """Main Gmail automation controller with REAL sending"""
    
    def __init__(self):
        """Initialize Gmail automation"""
        self.base_dir = Path(__file__).parent
        
        # Load accounts from accounts.json
        self.accounts = self._load_accounts()
        self.current_account_index = 0
        
        # Initialize managers
        self.email_manager = EmailManager(str(self.base_dir / 'emails' / 'emails.txt'))
        self.proxy_manager = ProxyManager(str(self.base_dir / 'proxies' / 'proxies.txt'))
        self.message_template = MessageTemplate(str(self.base_dir / 'text' / 'text.txt'))
        self.response_checker = ResponseChecker()
        
        # State
        self.is_running = False
        self.is_paused = False
        self.inbox_mode = False
        self.gmail_clients = []
        
        # Stats
        self.emails_sent = 0
        self.emails_failed = 0
        
        # Keyboard input
        self.user_command = None
        self.command_lock = threading.Lock()
    
    def _load_accounts(self):
        """Load Gmail accounts from accounts.json"""
        accounts_file = self.base_dir / 'accounts.json'
        
        if load_accounts_from_json:
            accounts = load_accounts_from_json(str(accounts_file))
            if accounts:
                print(f"✅ Загружено {len(accounts)} аккаунтов из accounts.json")
                for acc in accounts:
                    print(f"   - {acc['email']}")
                return accounts
        
        print(f"⚠️ Файл accounts.json не найден или пуст")
        print(f"")
        print(f"📖 Для реальной отправки писем:")
        print(f"   1. Создайте App Password: https://myaccount.google.com/apppasswords")
        print(f"   2. Создайте файл accounts.json:")
        print(f"")
        print(f'      [')
        print(f'        {{')
        print(f'          "email": "your.email@gmail.com",')
        print(f'          "app_password": "abcd efgh ijkl mnop"')
        print(f'        }}')
        print(f'      ]')
        print(f"")
        print(f"   3. См. REAL_SENDING.md для подробных инструкций")
        print(f"")
        print(f"⚠️ Работа в ДЕМО режиме (письма НЕ отправляются)")
        return []
    
    def _print_header(self):
        """Print script header"""
        print("\n" + "="*60)
        if self.accounts:
            print("📧 Gmail Automation Script - РЕАЛЬНАЯ ОТПРАВКА")
        else:
            print("📧 Gmail Automation Script - ДЕМО РЕЖИМ")
        print("="*60)
        print("Управление:")
        print("  I - Inbox режим (отправить на конкретный email)")
        print("  R - Возобновить автоматическую отправку")
        print("  Q - Выход")
        print("  Ctrl+C - Остановить")
        print("="*60 + "\n")
    
    def _listen_for_commands(self):
        """Listen for keyboard commands in background thread"""
        while self.is_running:
            try:
                # Non-blocking input with timeout
                if sys.platform == 'win32':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').upper()
                        with self.command_lock:
                            self.user_command = key
                else:
                    # Unix-like systems
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).upper()
                        with self.command_lock:
                            self.user_command = key
                
                time.sleep(0.1)
            except:
                time.sleep(0.1)
    
    def _process_commands(self):
        """Process user commands"""
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
        """Enter inbox mode - send to specific email"""
        print("\n" + "="*60)
        print("📥 INBOX РЕЖИМ")
        print("="*60)
        
        self.is_paused = True
        
        # Get email from user
        target_email = input("Введите email получателя: ").strip()
        
        if not target_email:
            print("⚠️ Email не указан, возвращаемся к автоматической отправке")
            self.is_paused = False
            return
        
        print(f"\n📧 Отправка на {target_email}...")
        
        # Get account and send
        if not self.accounts:
            print("❌ Нет аккаунтов! Настройте accounts.json")
            self.is_paused = False
            return
        
        try:
            # Get account
            account = self.accounts[self.current_account_index]
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            
            # Create client
            client = GmailClient(account['email'], account['app_password'])
            
            # Get message
            message = self.message_template.get_message()
            subject = "Привет!"
            
            # Send
            success = client.send_email(target_email, subject, message)
            
            if success:
                print(f"✅ Письмо отправлено на {target_email}")
                self.emails_sent += 1
            else:
                print(f"❌ Не удалось отправить на {target_email}")
                self.emails_failed += 1
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.emails_failed += 1
        
        print("\n" + "="*60)
        print("Нажмите R для возобновления автоматической отправки")
        print("="*60)
    
    def _resume_mode(self):
        """Resume automatic sending"""
        print("\n✅ Возобновление автоматической отправки...\n")
        self.is_paused = False
        self.inbox_mode = False
    
    def _quit(self):
        """Quit the script"""
        print("\n👋 Завершение работы...")
        self.is_running = False
    
    def _send_next_email(self):
        """Send email to next recipient in queue"""
        # Get next email
        target_email = self.email_manager.get_next_email()
        if not target_email:
            print("\n✅ Все email обработаны!")
            return False
        
        # Get account
        if not self.accounts:
            print("❌ Нет аккаунтов! Работа в ДЕМО режиме")
            time.sleep(2)
            return True
        
        try:
            # Get account
            account = self.accounts[self.current_account_index]
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            
            # Create client
            client = GmailClient(account['email'], account['app_password'])
            
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
                print(f"   ✅ Успешно отправлено")
                self.emails_sent += 1
            else:
                print(f"   ❌ Не удалось отправить")
                self.emails_failed += 1
            
            # Delay between sends
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            self.emails_failed += 1
            return True
    
    def _check_responses(self):
        """Check for new responses"""
        if self.response_checker.should_check():
            # Response checking not implemented for SMTP
            self.response_checker.last_check_time = time.time()
    
    def run(self):
        """Main run loop"""
        self._print_header()
        
        # Validate setup
        if not self.email_manager.has_more_emails():
            print("❌ Не найдено email адресов в emails/emails.txt")
            print("   Добавьте email адреса (по одному на строку) и запустите снова")
            return
        
        print(f"✅ Готов к работе!")
        if self.accounts:
            print(f"   Аккаунтов: {len(self.accounts)}")
        else:
            print(f"   Аккаунтов: 0 (ДЕМО режим)")
        print(f"   Email адресов: {self.email_manager.get_progress()[1]}")
        print()
        
        if not self.accounts:
            print("⚠️ ВАЖНО: Настройте accounts.json для реальной отправки!")
            print("⚠️ См. REAL_SENDING.md")
            print()
        
        # Start command listener
        self.is_running = True
        command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        command_thread.start()
        
        # Main loop
        try:
            while self.is_running:
                # Process commands
                if not self._process_commands():
                    break
                
                # If paused, just wait
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                
                # Check for responses periodically
                self._check_responses()
                
                # Send next email
                if not self._send_next_email():
                    break
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Прервано пользователем")
        
        finally:
            self.is_running = False
            self._print_stats()
    
    def _print_stats(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 Статистика")
        print("="*60)
        print(f"Отправлено успешно: {self.emails_sent}")
        print(f"Ошибки: {self.emails_failed}")
        print(f"Всего обработано: {self.emails_sent + self.emails_failed}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    automation = GmailAutomationReal()
    automation.run()


if __name__ == "__main__":
    main()
