#!/usr/bin/env python3
"""
Setup script for Gmail Automation
Автоматическая настройка директорий и файлов
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Create necessary directories"""
    base_dir = Path(__file__).parent
    
    directories = [
        base_dir / 'cookies',
        base_dir / 'emails',
        base_dir / 'text',
        base_dir / 'proxies',
        base_dir / 'logs',
    ]
    
    print("📁 Создание структуры директорий...")
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"   ✅ {directory.name}/")
    
    print()


def create_example_files():
    """Create example configuration files"""
    base_dir = Path(__file__).parent
    
    # Create emails example if not exists
    emails_file = base_dir / 'emails' / 'emails.txt'
    if not emails_file.exists():
        with open(emails_file, 'w', encoding='utf-8') as f:
            f.write("# Добавьте email адреса получателей (один на строку)\n")
            f.write("# Пример:\n")
            f.write("# user1@example.com\n")
            f.write("# user2@example.com\n")
        print(f"✅ Создан {emails_file}")
    
    # Create text example if not exists
    text_file = base_dir / 'text' / 'text.txt'
    if not text_file.exists():
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("Привет!\n\n")
            f.write("Это автоматическое сообщение.\n\n")
            f.write("С уважением,\n")
            f.write("Ваше имя\n")
        print(f"✅ Создан {text_file}")
    
    # Create proxies example if not exists
    proxies_file = base_dir / 'proxies' / 'proxies.txt'
    if not proxies_file.exists():
        with open(proxies_file, 'w', encoding='utf-8') as f:
            f.write("# Добавьте прокси (один на строку)\n")
            f.write("# Форматы:\n")
            f.write("# http://user:pass@host:port\n")
            f.write("# host:port:user:pass\n")
            f.write("# host:port\n")
            f.write("#\n")
            f.write("# Пример:\n")
            f.write("# http://myuser:mypass@123.45.67.89:8080\n")
        print(f"✅ Создан {proxies_file}")
    
    print()


def show_next_steps():
    """Show next steps to user"""
    print("="*60)
    print("🎉 Установка завершена!")
    print("="*60)
    print()
    print("📝 Следующие шаги:")
    print()
    print("1. Добавьте cookie файлы в папку cookies/")
    print("   - Формат: account1.json, account2.json и т.д.")
    print("   - Смотрите README.md для инструкций")
    print()
    print("2. Добавьте email адреса в emails/emails.txt")
    print("   - По одному адресу на строку")
    print()
    print("3. Настройте текст в text/text.txt")
    print("   - Ваш текст сообщения")
    print()
    print("4. (Опционально) Добавьте прокси в proxies/proxies.txt")
    print()
    print("5. Запустите скрипт:")
    print("   python gmail_sender.py")
    print()
    print("="*60)
    print()
    print("📖 Полная документация: README.md")
    print("🚀 Быстрый старт: QUICKSTART.md")
    print()


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Проверка зависимостей...")
    
    try:
        import requests
        print("   ✅ requests установлен")
    except ImportError:
        print("   ❌ requests не установлен")
        print()
        print("Установите зависимости:")
        print("   pip install requests")
        print()
        return False
    
    print()
    return True


def main():
    """Main setup function"""
    print()
    print("="*60)
    print("📧 Gmail Automation - Установка")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create structure
    create_directory_structure()
    
    # Create example files
    create_example_files()
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()
