#!/usr/bin/env python3
"""
Demo/Test script for Gmail Automation
Демонстрация работы без реальной отправки писем
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from email_manager import EmailManager, AccountManager
from proxy_manager import ProxyManager
from message_template import MessageTemplate


def print_header():
    """Print demo header"""
    print("\n" + "="*60)
    print("🧪 Gmail Automation - DEMO MODE")
    print("="*60)
    print("Это демонстрация работы скрипта без реальной отправки")
    print("="*60 + "\n")


def demo_account_manager():
    """Demo account management"""
    print("📁 1. Тест менеджера аккаунтов")
    print("-" * 40)
    
    manager = AccountManager('cookies')
    
    if manager.get_account_count() > 0:
        print(f"✅ Найдено аккаунтов: {manager.get_account_count()}")
        
        # Show rotation
        print("\nРотация аккаунтов:")
        for i in range(min(5, manager.get_account_count() * 2)):
            account = manager.get_next_account()
            print(f"  {i+1}. {os.path.basename(account)}")
    else:
        print("⚠️ Аккаунты не найдены (это нормально для демо)")
    
    print()


def demo_email_manager():
    """Demo email management"""
    print("📧 2. Тест менеджера email")
    print("-" * 40)
    
    # Create demo file if needed
    demo_file = 'emails/emails.txt'
    has_real_emails = os.path.exists(demo_file)
    
    if has_real_emails:
        manager = EmailManager(demo_file)
        
        if manager.emails:
            print(f"✅ Загружено email: {len(manager.emails)}")
            print("\nПервые 3 email:")
            for i in range(min(3, len(manager.emails))):
                email = manager.get_next_email()
                print(f"  {i+1}. {email}")
        else:
            print("⚠️ Email не найдены")
    else:
        print("⚠️ Файл emails.txt не найден (это нормально для демо)")
        print("📝 Создайте emails/emails.txt для тестирования")
    
    print()


def demo_proxy_manager():
    """Demo proxy management"""
    print("🌐 3. Тест менеджера прокси")
    print("-" * 40)
    
    manager = ProxyManager('proxies/proxies.txt')
    
    if manager.has_proxies():
        print(f"✅ Загружено прокси: {len(manager.proxies)}")
        print("\nПервые 3 прокси:")
        for i in range(min(3, len(manager.proxies))):
            proxy = manager.get_next_proxy()
            # Hide sensitive info
            display_proxy = proxy[:30] + "..." if len(proxy) > 30 else proxy
            print(f"  {i+1}. {display_proxy}")
    else:
        print("⚠️ Прокси не найдены (работа без прокси)")
    
    print()


def demo_message_template():
    """Demo message template"""
    print("📝 4. Тест шаблона сообщений")
    print("-" * 40)
    
    template = MessageTemplate('text/text.txt')
    
    if template.template:
        print(f"✅ Шаблон загружен ({len(template.template)} символов)")
        print("\nПример сообщения:")
        print("-" * 40)
        message = template.get_message(EMAIL="test@example.com")
        # Show first 200 chars
        preview = message[:200] + "..." if len(message) > 200 else message
        print(preview)
        print("-" * 40)
    else:
        print("⚠️ Шаблон не найден")
    
    print()


def demo_workflow():
    """Demo complete workflow"""
    print("🔄 5. Демонстрация рабочего процесса")
    print("-" * 40)
    
    # Simulate workflow
    accounts = AccountManager('cookies')
    emails = EmailManager('emails/emails.txt')
    proxies = ProxyManager('proxies/proxies.txt')
    template = MessageTemplate('text/text.txt')
    
    print("Симуляция отправки писем:")
    print()
    
    # Simulate 3 sends
    for i in range(3):
        if not emails.has_more_emails():
            print("📭 Email закончились")
            break
        
        email = emails.get_next_email() or f"demo{i+1}@example.com"
        account = accounts.get_next_account() if accounts.get_account_count() > 0 else "demo_account.json"
        proxy = proxies.get_next_proxy() or "без прокси"
        
        current, total = emails.get_progress()
        
        print(f"[{i+1}/3] 📧 Отправка на {email}...")
        print(f"   Аккаунт: {os.path.basename(str(account))}")
        if proxy != "без прокси":
            display_proxy = proxy[:30] + "..." if len(proxy) > 30 else proxy
            print(f"   Прокси: {display_proxy}")
        
        # Simulate send
        time.sleep(0.5)
        print(f"   ✅ [DEMO] Успешно отправлено")
        print()
    
    print("="*60)
    print("📊 Демо статистика")
    print("="*60)
    print(f"Отправлено: 3 (в демо режиме)")
    print(f"Аккаунтов использовано: {min(3, accounts.get_account_count()) if accounts.get_account_count() > 0 else 0}")
    print("="*60)


def main():
    """Main demo function"""
    print_header()
    
    print("Этот скрипт демонстрирует работу системы без реальной отправки писем.\n")
    
    demo_account_manager()
    time.sleep(0.5)
    
    demo_email_manager()
    time.sleep(0.5)
    
    demo_proxy_manager()
    time.sleep(0.5)
    
    demo_message_template()
    time.sleep(0.5)
    
    demo_workflow()
    
    print("\n" + "="*60)
    print("✅ Демонстрация завершена!")
    print("="*60)
    print()
    print("📝 Для реальной работы:")
    print("   1. Запустите: python setup.py")
    print("   2. Настройте все файлы")
    print("   3. Запустите: python gmail_sender.py")
    print()
    print("📖 Смотрите:")
    print("   - README.md - полная документация")
    print("   - QUICKSTART.md - быстрый старт")
    print("   - USAGE.md - подробное руководство")
    print()


if __name__ == "__main__":
    main()
