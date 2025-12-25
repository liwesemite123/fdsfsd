# 📧 Gmail Automation Script

[English](#english) | [Русский](#русский)

---

## Русский

### О проекте

Автоматический скрипт для отправки писем через Gmail с использованием cookie авторизации. Поддерживает множественные аккаунты, прокси, интерактивное управление через терминал и проверку ответов.

### 🎯 Основные возможности

- ✅ **Cookie авторизация** - Вход в Gmail через сохраненные cookie
- ✅ **Множественные аккаунты** - Неограниченное количество Gmail аккаунтов
- ✅ **Умная ротация** - Автоматическое переключение между аккаунтами
- ✅ **Поддержка прокси** - Работа через прокси для безопасности
- ✅ **Интерактивное управление** - Управление через клавиши I/R/Q
- ✅ **Inbox режим** - Отправка на конкретный email по требованию
- ✅ **Проверка ответов** - Уведомления о новых письмах
- ✅ **Подробная статистика** - Отслеживание всех отправок

### 🚀 Быстрый старт

⚠️ **ВАЖНО:** Текущая версия использует mock-реализацию отправки. Для реальной отправки писем требуется интеграция с Gmail API, SMTP или browser automation. См. раздел "О реальной отправке писем" ниже.

1. **Перейдите в папку Gmail Automation:**
   ```bash
   cd gmail_automation
   ```

2. **Запустите установку:**
   ```bash
   python setup.py
   ```

3. **Настройте файлы:**
   - `cookies/` - Добавьте JSON файлы с cookie Gmail
   - `emails/emails.txt` - Список email получателей
   - `text/text.txt` - Текст сообщения
   - `proxies/proxies.txt` - Прокси (опционально)

4. **Запустите скрипт:**
   ```bash
   python gmail_sender.py
   ```

### 📖 Документация

- **[README.md](gmail_automation/README.md)** - Полная документация
- **[QUICKSTART.md](gmail_automation/QUICKSTART.md)** - Быстрый старт (5 минут)
- **[USAGE.md](gmail_automation/USAGE.md)** - Подробное руководство

### 🎮 Управление

Во время работы используйте клавиши:

- **I** - Inbox режим (отправить на конкретный email)
- **R** - Возобновить автоматическую отправку
- **Q** - Выход
- **Ctrl+C** - Экстренная остановка

### 📦 Структура

```
gmail_automation/
├── gmail_sender.py      # Главный скрипт
├── setup.py             # Скрипт установки
├── demo.py              # Демонстрация
├── src/                 # Исходный код
│   ├── gmail_client.py
│   ├── email_manager.py
│   ├── proxy_manager.py
│   └── ...
├── cookies/             # Cookie файлы Gmail
├── emails/              # Список email
├── text/                # Текст сообщения
└── proxies/             # Прокси
```

### 🔐 Безопасность

- ✅ Cookie файлы защищены через `.gitignore`
- ✅ Поддержка прокси для анонимности
- ✅ Задержки между отправками
- ✅ Лимиты на количество отправок

### ⚠️ Важно

1. **Cookie дают полный доступ к аккаунту** - храните их в безопасности
2. **Gmail лимиты** - не более 500 писем в день с одного аккаунта
3. **Используйте прокси** - для дополнительной защиты
4. **Обновляйте cookie** - они действительны ~2 недели

---

## English

### About

Automated Gmail email sender using cookie authentication. Supports multiple accounts, proxies, interactive terminal control, and response monitoring.

### 🎯 Features

- ✅ **Cookie Authentication** - Login to Gmail via saved cookies
- ✅ **Multiple Accounts** - Unlimited Gmail accounts support
- ✅ **Smart Rotation** - Automatic account switching
- ✅ **Proxy Support** - Work through proxies for security
- ✅ **Interactive Control** - Control via I/R/Q keys
- ✅ **Inbox Mode** - Send to specific email on demand
- ✅ **Response Checker** - Notifications for new messages
- ✅ **Detailed Statistics** - Track all sends

### 🚀 Quick Start

1. **Navigate to Gmail Automation:**
   ```bash
   cd gmail_automation
   ```

2. **Run setup:**
   ```bash
   python setup.py
   ```

3. **Configure files:**
   - `cookies/` - Add Gmail cookie JSON files
   - `emails/emails.txt` - List of recipient emails
   - `text/text.txt` - Message text
   - `proxies/proxies.txt` - Proxies (optional)

4. **Run script:**
   ```bash
   python gmail_sender.py
   ```

### 📖 Documentation

- **[README.md](gmail_automation/README.md)** - Full documentation (Russian)
- **[QUICKSTART.md](gmail_automation/QUICKSTART.md)** - Quick start guide
- **[USAGE.md](gmail_automation/USAGE.md)** - Detailed usage guide

### 🎮 Controls

During operation, use these keys:

- **I** - Inbox mode (send to specific email)
- **R** - Resume automatic sending
- **Q** - Quit
- **Ctrl+C** - Emergency stop

### 🔐 Security

- ✅ Cookie files protected via `.gitignore`
- ✅ Proxy support for anonymity
- ✅ Delays between sends
- ✅ Send limits

### ⚠️ Important

1. **Cookies grant full account access** - keep them secure
2. **Gmail limits** - max ~500 emails per day per account
3. **Use proxies** - for additional protection
4. **Update cookies** - they're valid for ~2 weeks

---

## 📄 License

Private project for personal use.

## 🤝 Support

For questions, see the documentation files in `gmail_automation/`.

---

**Happy automating! 🚀**
