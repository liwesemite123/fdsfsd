# 🔧 Troubleshooting - Решение проблем

## ❌ Ошибка: Selenium WebDriver crash / Renderer Timeout

### Симптомы:
```
Ошибка: Message: timeout: Timed out receiving message from renderer
Stacktrace:
Symbols not available. Dumping unresolved backtrace:
...
```

ИЛИ

```
Ошибка: Message: 
Stacktrace:
Symbols not available. Dumping unresolved backtrace:
...
```

### Причины:
1. **Chrome/ChromeDriver не установлен** или несовместимые версии
2. **Отсутствуют системные зависимости**
3. **Проблемы с headless режимом**
4. **Недостаточно памяти /dev/shm**
5. **Конфликты версий Chrome/ChromeDriver**
6. **Renderer процесс зависает или крашится**

---

## ✅ Решения

### Решение 1: Установка Chrome/Chromium (РЕКОМЕНДУЕТСЯ)

#### Ubuntu/Debian:
```bash
# Установка Chromium
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# ИЛИ установка Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

#### CentOS/RHEL:
```bash
sudo yum install -y chromium chromium-headless
```

#### Windows:
1. Скачайте и установите Google Chrome: https://www.google.com/chrome/
2. Selenium автоматически найдет Chrome

#### macOS:
```bash
brew install --cask google-chrome
```

---

### Решение 2: Обновление зависимостей

```bash
# Обновите Selenium и webdriver-manager
pip install --upgrade selenium webdriver-manager

# Переустановите зависимости
pip uninstall selenium webdriver-manager
pip install selenium webdriver-manager
```

---

### Решение 3: Отключение headless режима (для отладки)

Откройте `gmail_sender_password.py` и измените:

```python
# Было:
self.browser_clients[acc_key] = GmailPasswordClient(
    email=account['email'],
    password=account['password'],
    backup_email=account.get('backup_email'),
    twofa_code=account.get('twofa_code'),
    headless=True  # ← Измените это
)

# Станет:
self.browser_clients[acc_key] = GmailPasswordClient(
    email=account['email'],
    password=account['password'],
    backup_email=account.get('backup_email'),
    twofa_code=account.get('twofa_code'),
    headless=False  # ← Теперь браузер будет видимый
)
```

Это позволит увидеть что происходит в браузере.

---

### Решение 4: Увеличение /dev/shm (для renderer timeout)

Renderer timeout часто происходит из-за недостатка памяти в /dev/shm:

```bash
# Проверьте текущий размер /dev/shm
df -h /dev/shm

# Если меньше 512MB, увеличьте:
sudo mount -o remount,size=2G /dev/shm

# Проверьте снова
df -h /dev/shm
```

Или используйте флаг `--disable-dev-shm-usage` (уже включен в скрипт).

---

### Решение 5: Системные зависимости (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0
```

---

### Решение 6: Использование системного chromedriver

Если webdriver-manager не работает:

```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Проверка
which chromedriver
chromedriver --version
```

Скрипт автоматически попробует использовать системный chromedriver если webdriver-manager не сработает.

---

## 🔍 Диагностика

### Проверка установки Chrome:

```bash
# Linux
google-chrome --version
# или
chromium-browser --version

# Windows (PowerShell)
(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
```

### Проверка ChromeDriver:

```bash
chromedriver --version
```

### Тест Selenium:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com')
    print("✅ Selenium работает!")
    driver.quit()
except Exception as e:
    print(f"❌ Ошибка: {e}")
```

---

## 🐧 Для Linux-серверов без GUI

Если работаете на сервере без графического интерфейса:

```bash
# Установите Xvfb (виртуальный дисплей)
sudo apt-get install xvfb

# Запустите скрипт с Xvfb
xvfb-run python gmail_sender_password.py
```

---

## 🆘 Альтернативные методы

Если Selenium совсем не работает, используйте **SMTP метод**:

```bash
# Не требует браузер!
python gmail_sender_real.py
```

Требует App Password, но работает без Selenium и браузера.

См. `REAL_SENDING.md` для инструкций.

---

## 📝 Частые ошибки

### "ChromeDriver not found"
**Решение:** Установите chromium-chromedriver или запустите с webdriver-manager

### "Chrome not reachable"
**Решение:** 
1. Установите Chrome/Chromium
2. Попробуйте без headless режима
3. Проверьте системные зависимости

### "Session not created"
**Решение:** Обновите Chrome и ChromeDriver до совместимых версий

### "Message: invalid session id"
**Решение:** Браузер закрылся неожиданно - проверьте логи, отключите headless для отладки

### "timeout: Timed out receiving message from renderer" ⚠️ НОВОЕ
**Причина:** Chrome renderer процесс не отвечает - обычно из-за нехватки памяти или ресурсов

**Решение:**
1. Увеличьте /dev/shm:
   ```bash
   sudo mount -o remount,size=2G /dev/shm
   ```
2. Скрипт уже использует `--single-process` для снижения нагрузки
3. Используйте альтернативный метод:
   ```bash
   python gmail_sender_real.py  # SMTP - не требует браузер
   ```

---

## 💡 Дополнительная помощь

Если проблема не решена:

1. **Запустите с headless=False** чтобы увидеть что происходит
2. **Проверьте логи** - скрипт выводит подробную информацию
3. **Попробуйте SMTP метод** (`gmail_sender_real.py`) как альтернативу
4. **Обновите систему:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

---

## 📊 Быстрая проверка

```bash
# 1. Chrome установлен?
google-chrome --version || chromium-browser --version

# 2. Python зависимости установлены?
pip list | grep selenium

# 3. Попробуйте простой тест
python -c "from selenium import webdriver; print('OK')"
```

Если все 3 команды работают - проблема должна быть решена!
