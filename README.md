# 📧 Automation Scripts Repository

This repository contains two automation systems:

1. **GoDaddy Email Sender** - Email automation with dynamic link generation
2. **Carrd.co Automation** - Website creation and form messaging automation (NEW!)

---

## 🆕 Carrd.co Automation Script (HTTP API Version)

Automated script for creating Carrd sites with forms and sending messages through them **using HTTP requests only** - no browser window is opened.

### Quick Start

See **[CARRD_README_API.md](CARRD_README_API.md)** and **[QUICKSTART_CARRD.md](QUICKSTART_CARRD.md)** for detailed instructions.

#### Installation

```bash
# Install dependencies (NO browser needed!)
pip install -r requirements.txt

# Run validation
python validate_config.py

# Run automation
python carrd_automation.py
```

Or use the launcher scripts:
- **Linux/Mac**: `./run_carrd.sh`
- **Windows**: `run_carrd.bat`

### Features

- ✅ **HTTP API-based** - No browser window, pure HTTP requests
- ✅ **Faster & Lighter** - No browser means lower resource usage
- ✅ Proxy support (HTTP and SOCKS5)
- ✅ Template selection and form creation via API
- ✅ Pro trial activation with Telegram bot API
- ✅ Automated message sending
- ✅ Duplicate prevention
- ✅ Comprehensive logging

---

## 📧 GoDaddy Email Sender с динамической генерацией ссылок

Автоматизированная система для отправки персонализированных писем через GoDaddy с динамической генерацией ссылок через API.

## 🎯 Основные возможности

- ✅ Парсинг объявлений Poshmark
- ✅ Валидация email адресов
- ✅ **Динамическая генерация персональных ссылок через API**
- ✅ **Автоматическое создание поддоменов (случайные или полу-случайные)**
- ✅ Отправка персонализированных писем через GoDaddy
- ✅ Поддержка нескольких аккаунтов одновременно
- ✅ Автоматическое управление невалидными аккаунтами

## 📋 Требования

- Python 3.10+
- Библиотеки из `pyproject.toml`

## ⚙️ Настройка

### 1. Настройка `.env` файла

Скопируйте `.env.example` в `.env` и настройте параметры:

```bash
cp .env.example .env
```

#### Ключевые параметры:

**🔧 ID Работника (обязательно):**
```env
WORKER_ID=6932206485  # УКАЖИТЕ СВОЙ ID РАБОТНИКА
```

**🔗 API для генерации ссылок:**
```env
API_URL=https://arthas-api.com/obezyanaPidor
LINK_SERVICE=etsyverify_world
```

**🌐 Настройки поддоменов:**
```env
SUBDOMAIN_MODE=semi_random     # "random" | "semi_random" | "none"
SUBDOMAIN_PREFIX=poshmark      # Префикс для режима semi_random
```

### 2. Структура директорий

```
posh/
├── cookies/           # JSON файлы с куками GoDaddy аккаунтов
├── Texts/
│   └── text.txt      # Шаблон письма с {GENERATED_LINK}
├── spammed_godaddy/  # Аккаунты, достигшие лимита
├── bad_accounts/     # Невалидные аккаунты
└── logs/             # Логи работы
```

### 3. Шаблон письма

Откройте `Texts/text.txt` и убедитесь, что в нем есть плейсхолдер `{LINK}`:

```
🔗 Click here {LINK}
```

Система автоматически заменит `{LINK}` на сгенерированную ссылку **без https://**

**Примеры результата:**
- **random режим:** `abcd.domain.com/abc123` (4 случайных символа)
- **semi_random режим:** `poshmarkabcd.domain.com/abc123` (префикс + 4 символа)
- **none режим:** `domain.com/abc123` (без поддомена)

## 🚀 Запуск

```bash
python main.py
```

## 📊 Как работает генерация ссылок

### 1. API Запрос

Для каждого email система отправляет запрос на API:

```json
{
  "id": "6932206485",              // WORKER_ID из .env
  "title": "Item Title",           // Название товара из парсера
  "address": "Customer Address",   // DEFAULT_ADDRESS из .env
  "photo": "https://...",          // DEFAULT_PHOTO из .env
  "price": "25.00",                // DEFAULT_PRICE из .env
  "name": "Customer Name",         // Username из парсера
  "linkService": "etsyverify_world"
}
```

### 2. Генерация поддомена

API возвращает ссылку, например: `https://domain.com/abc123`

Система обрабатывает её:
- ✂️ Удаляет `https://`
- 🔀 В зависимости от `SUBDOMAIN_MODE`:
  - **random**: генерирует 4 случайных символа → `abcd`
  - **semi_random**: префикс + 4 символа → `poshmark` + `abcd` = `poshmarkabcd`
  - **none**: оставляет как есть
- 🔗 Формирует финальную ссылку: `poshmarkabcd.domain.com/abc123`

### 3. Персонализация

Каждый email получает **уникальную ссылку** с уникальным поддоменом.

## 🎨 Примеры конфигураций поддоменов

### Режим "random" - полностью случайный (4 символа)
```env
SUBDOMAIN_MODE=random
SUBDOMAIN_PREFIX=               # Игнорируется в этом режиме
```
Результат: `abcd.domain.com/path`, `x9k2.domain.com/path`, `fg4a.domain.com/path`

### Режим "semi_random" - префикс + 4 случайных символа
```env
SUBDOMAIN_MODE=semi_random
SUBDOMAIN_PREFIX=poshmark
```
Результат: `poshmarkabcd.domain.com/path`, `poshmarkx9k2.domain.com/path`

### Режим "semi_random" с другим префиксом
```env
SUBDOMAIN_MODE=semi_random
SUBDOMAIN_PREFIX=depop
```
Результат: `depopabcd.domain.com/path`, `depopx9k2.domain.com/path`

### Режим "none" - без поддомена
```env
SUBDOMAIN_MODE=none
```
Результат: `domain.com/path` (оригинальная ссылка от API)

## 📝 Логирование

Все действия логируются в:
- Консоль (цветной вывод)
- `logs/` директория

Примеры логов:
```
✅ Спарсено 20 email
✅ Валидных email: 15/20
🔗 Генерируем персональные ссылки для 15 email...
✅ Успешно сгенерировано ссылок: 15/15
🔗 Используем персональную ссылку: poshmarkfg4ad.domain.com/abc123
✅ Сообщение отправлено на user@gmail.com
```

## ⚠️ Важные примечания

1. **WORKER_ID обязателен** - убедитесь, что указали свой ID в `.env`
2. **Формат ответа API** - если ваш API возвращает ссылку в другом формате (не `{"link": "..."}` или `{"url": "..."}`), отредактируйте `src/link_generator.py`
3. **Плейсхолдер в шаблоне** - обязательно должен быть `{GENERATED_LINK}` в `Texts/text.txt`
4. **Лимиты API** - учитывайте rate limits вашего API (настройте `max_concurrent` в коде при необходимости)

## 🔧 Troubleshooting

### Ошибка "API не вернул ссылку"
Проверьте формат ответа вашего API и обновите `link_generator.py`:
```python
# В функции generate_link() найдите:
if "link" in data:
    original_link = data["link"]
elif "url" in data:
    original_link = data["url"]
# Добавьте свой ключ если другой
```

### Не генерируются поддомены
Убедитесь что:
```env
SUBDOMAIN_MODE=random  # или semi_random (не none)
```

### Ссылки с https://
Система автоматически удаляет `https://` и `http://`. Если ссылка все равно с протоколом, проверьте функцию `_remove_https()` в `link_generator.py`

## 📦 Структура проекта

```
src/
├── main.py              # Основной файл с логикой
├── link_generator.py    # 🆕 Генерация ссылок через API
├── GoDaddy.py          # Клиент для отправки через GoDaddy
├── ParserNew.py        # Парсер Poshmark
├── validator.py        # Валидация email
└── ...
```

## 📄 Лицензия

Приватный проект

---

**Удачной работы! 🚀**
