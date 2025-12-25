#!/usr/bin/env python3
"""
Gmail Automation - РЕАЛЬНАЯ ОТПРАВКА С COOKIES!
Автоматическая отправка писем через Gmail используя ТОЛЬКО cookies

✅ Просто закиньте cookies и все работает!
✅ Не нужны App Passwords
✅ Работает через браузер (Selenium)

Требования:
- pip install selenium webdriver-manager

Структура:
- cookies/       - JSON файлы с cookies Gmail
- emails/        - emails.txt с адресами получателей  
- text/          - text.txt с текстом сообщения
- proxies/       - proxies.txt (опционально, не используется в браузере)

Управление:
- I - Inbox режим (отправить на конкретный email)
- R - Возобновить
- Q - Выход
- Ctrl+C - Остановить
"""

import os
import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gmail_browser import GmailBrowserClient, check_selenium_installed
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    GmailBrowserClient = None
    check_selenium_installed = lambda: False

from email_manager import EmailManager, AccountManager
from message_template import MessageTemplate
from response_checker import ResponseChecker


class GmailAutomationBrowser:
    """Gmail automation with browser automation (cookies only!)"""
    
    def __init__(self):
        """Initialize Gmail automation"""
        self.base_dir = Path(__file__).parent
        
        # Check Selenium
        if not BROWSER_AVAILABLE or not check_selenium_installed():
            print("❌ Selenium не установлен!")
            print("📦 Установите: pip install selenium webdriver-manager")
            print()
            sys.exit(1)
        
        # Initialize managers
        self.account_manager = AccountManager(str(self.base_dir / 'cookies'))
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
        print("📧 Gmail Automation - РЕАЛЬНАЯ ОТПРАВКА С COOKIES!")
        print("="*60)
        print("✅ Используется browser automation")
        print("✅ Работает с COOKIES без App Password!")
        print("="*60)
        print("Управление:")
        print("  I - Inbox режим")
        print("  R - Возобновить")
        print("  Q - Выход")
        print("="*60 + "\n")
    
    def _listen_for_commands(self):
        """Listen for keyboard commands"""
        while self.is_running:
            try:
                if sys.platform == 'win32':
                    import msvcrt
                    if msvcrt.kbhit():
                        try:
                            key = msvcrt.getch().decode('utf-8').upper()
                            with self.command_lock:
                                self.user_command = key
                        except:
                            pass
                else:
                    import select
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
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
        cookie_file = self.account_manager.get_next_account()
        if not cookie_file:
            print("❌ Нет аккаунтов!")
            self.is_paused = False
            return
        
        try:
            # Get or create browser client
            if cookie_file not in self.browser_clients:
                self.browser_clients[cookie_file] = GmailBrowserClient(cookie_file)
            
            client = self.browser_clients[cookie_file]
            
            # Get message
            message = self.message_template.get_message()
            subject = "Привет!"
            
            # Send
            success = client.send_email(target_email, subject, message)
            
            if success:
                print(f"✅ Отправлено на {target_email}")
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
        cookie_file = self.account_manager.get_next_account()
        if not cookie_file:
            print("❌ Нет аккаунтов!")
            return False
        
        try:
            # Get or create browser client
            if cookie_file not in self.browser_clients:
                print(f"\n🌐 Создание браузера для {os.path.basename(cookie_file)}...")
                self.browser_clients[cookie_file] = GmailBrowserClient(cookie_file, headless=True)
            
            client = self.browser_clients[cookie_file]
            
            # Get message
            message = self.message_template.get_message(EMAIL=target_email)
            subject = "Привет!"
            
            # Progress
            current, total = self.email_manager.get_progress()
            print(f"\n[{current}/{total}] 📧 Отправка на {target_email}...")
            print(f"   От: {os.path.basename(cookie_file)}")
            
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
        """Cleanup browser clients"""
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
        if self.account_manager.get_account_count() == 0:
            print("❌ Нет cookie файлов в cookies/")
            print("   Добавьте JSON файлы с cookies и запустите снова")
            return
        
        if not self.email_manager.has_more_emails():
            print("❌ Нет email в emails/emails.txt")
            return
        
        print(f"✅ Готов к работе!")
        print(f"   Аккаунтов (cookies): {self.account_manager.get_account_count()}")
        print(f"   Email адресов: {self.email_manager.get_progress()[1]}")
        print()
        print("⚠️ ВАЖНО:")
        print("   - Браузеры будут открываться автоматически")
        print("   - Первая отправка может занять ~10 секунд")
        print("   - Последующие отправки быстрее")
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
    """Main entry point"""
    automation = GmailAutomationBrowser()
    automation.run()


if __name__ == "__main__":
    main()
