#!/usr/bin/env python3
"""
Gmail Automation Script
Автоматическая отправка писем через Gmail с использованием cookies

Структура папок:
- cookies/    - JSON файлы с cookie аккаунтов Gmail
- emails/     - Файл emails.txt с адресами получателей (по одному на строку)
- text/       - Файл text.txt с текстом сообщения
- proxies/    - Файл proxies.txt с прокси (по одному на строку)

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

from gmail_client import GmailClient
from email_manager import EmailManager, AccountManager
from proxy_manager import ProxyManager
from message_template import MessageTemplate
from response_checker import ResponseChecker


class GmailAutomation:
    """Main Gmail automation controller"""
    
    def __init__(self):
        """Initialize Gmail automation"""
        self.base_dir = Path(__file__).parent
        
        # Initialize managers
        self.account_manager = AccountManager(str(self.base_dir / 'cookies'))
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
    
    def _print_header(self):
        """Print script header"""
        print("\n" + "="*60)
        print("📧 Gmail Automation Script")
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
        cookie_file = self.account_manager.get_next_account()
        if not cookie_file:
            print("❌ Нет доступных аккаунтов!")
            self.is_paused = False
            return
        
        try:
            # Get proxy
            proxy = self.proxy_manager.get_next_proxy()
            
            # Create client
            client = GmailClient(cookie_file, proxy)
            
            # Get message
            message = self.message_template.get_message()
            subject = "Привет!"  # Default subject
            
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
        cookie_file = self.account_manager.get_next_account()
        if not cookie_file:
            print("❌ Нет доступных аккаунтов!")
            return False
        
        try:
            # Get proxy
            proxy = self.proxy_manager.get_next_proxy()
            
            # Create client
            client = GmailClient(cookie_file, proxy)
            
            # Get message
            message = self.message_template.get_message(EMAIL=target_email)
            subject = "Привет!"  # Default subject
            
            # Progress
            current, total = self.email_manager.get_progress()
            print(f"\n[{current}/{total}] 📧 Отправка на {target_email}...")
            print(f"   Аккаунт: {os.path.basename(cookie_file)}")
            if proxy:
                print(f"   Прокси: {proxy[:30]}...")
            
            # Send
            success = client.send_email(target_email, subject, message)
            
            if success:
                print(f"   ✅ Успешно отправлено")
                self.emails_sent += 1
            else:
                print(f"   ❌ Не удалось отправить")
                self.emails_failed += 1
            
            # Delay between sends
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            self.emails_failed += 1
            return True
    
    def _check_responses(self):
        """Check for new responses"""
        if self.response_checker.should_check():
            print("\n🔍 Проверка новых ответов...")
            # Would need active clients to check
            # For now, just update timestamp
            self.response_checker.last_check_time = time.time()
    
    def run(self):
        """Main run loop"""
        self._print_header()
        
        # Validate setup
        if self.account_manager.get_account_count() == 0:
            print("❌ Не найдено аккаунтов в папке cookies/")
            print("   Добавьте JSON файлы с cookie и запустите снова")
            return
        
        if not self.email_manager.has_more_emails():
            print("❌ Не найдено email адресов в emails/emails.txt")
            print("   Добавьте email адреса (по одному на строку) и запустите снова")
            return
        
        print(f"✅ Готов к работе!")
        print(f"   Аккаунтов: {self.account_manager.get_account_count()}")
        print(f"   Email адресов: {self.email_manager.get_progress()[1]}")
        print(f"   Прокси: {len(self.proxy_manager.proxies) if self.proxy_manager.has_proxies() else 'Без прокси'}")
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
    automation = GmailAutomation()
    automation.run()


if __name__ == "__main__":
    main()
