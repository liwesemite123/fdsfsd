# 🎨 Визуальные примеры режимов поддоменов

## 📋 Три режима работы

### 🎲 Режим "random" - Полностью случайный

**Конфигурация:**
```env
SUBDOMAIN_MODE=random
SUBDOMAIN_PREFIX=              # Игнорируется в этом режиме
```

**Как работает:**
```
API возвращает: https://tracking-domain.com/abc123xyz
      ⬇️
Удаление https://: tracking-domain.com/abc123xyz
      ⬇️
Генерация 4 символов: abcd
      ⬇️
Финальная ссылка: abcd.tracking-domain.com/abc123xyz
```

**Примеры результатов:**
```
abcd.tracking-domain.com/abc123xyz
x9k2.tracking-domain.com/def456uvw
hj83.tracking-domain.com/ghi789rst
m5n7.tracking-domain.com/jkl012mno
```

---

### 🎯 Режим "semi_random" - Префикс + случайные символы

**Конфигурация:**
```env
SUBDOMAIN_MODE=semi_random
SUBDOMAIN_PREFIX=poshmark
```

**Как работает:**
```
API возвращает: https://tracking-domain.com/abc123xyz
      ⬇️
Удаление https://: tracking-domain.com/abc123xyz
      ⬇️
Генерация 4 символов: abcd
      ⬇️
Добавление префикса: poshmark + abcd = poshmarkabcd
      ⬇️
Финальная ссылка: poshmarkabcd.tracking-domain.com/abc123xyz
```

**Примеры с префиксом "poshmark":**
```
poshmarkabcd.tracking-domain.com/abc123xyz
poshmarkx9k2.tracking-domain.com/def456uvw
poshmarkhj83.tracking-domain.com/ghi789rst
poshmarkm5n7.tracking-domain.com/jkl012mno
```

**Примеры с префиксом "depop":**
```env
SUBDOMAIN_PREFIX=depop
```
```
depopabcd.tracking-domain.com/abc123xyz
depopx9k2.tracking-domain.com/def456uvw
depophj83.tracking-domain.com/ghi789rst
depopm5n7.tracking-domain.com/jkl012mno
```

**Примеры с префиксом "etsy":**
```env
SUBDOMAIN_PREFIX=etsy
```
```
etsyabcd.tracking-domain.com/abc123xyz
etsyx9k2.tracking-domain.com/def456uvw
etsyhj83.tracking-domain.com/ghi789rst
etsym5n7.tracking-domain.com/jkl012mno
```

---

### 🚫 Режим "none" - Без поддомена

**Конфигурация:**
```env
SUBDOMAIN_MODE=none
```

**Как работает:**
```
API возвращает: https://tracking-domain.com/abc123xyz
      ⬇️
Удаление https://: tracking-domain.com/abc123xyz
      ⬇️
Финальная ссылка: tracking-domain.com/abc123xyz
```

**Примеры результатов:**
```
tracking-domain.com/abc123xyz
tracking-domain.com/def456uvw
tracking-domain.com/ghi789rst
tracking-domain.com/jkl012mno
```

---

## 📧 Примеры в письмах

### С режимом "random":
```
Dear User,

We would like to notify you that your account has been temporarily suspended...

🔗 Click here abcd.tracking-domain.com/abc123xyz

Please ensure that all required steps are followed...
```

### С режимом "semi_random" (poshmark):
```
Dear User,

We would like to notify you that your account has been temporarily suspended...

🔗 Click here poshmarkabcd.tracking-domain.com/abc123xyz

Please ensure that all required steps are followed...
```

### С режимом "none":
```
Dear User,

We would like to notify you that your account has been temporarily suspended...

🔗 Click here tracking-domain.com/abc123xyz

Please ensure that all required steps are followed...
```

---

## 🔀 Сравнение режимов

| Режим | Длина поддомена | Пример | Использование |
|-------|----------------|--------|---------------|
| `random` | 4 символа | `abcd.domain.com` | Максимальная анонимность |
| `semi_random` | Префикс + 4 | `poshmarkabcd.domain.com` | Брендирование + уникальность |
| `none` | Нет поддомена | `domain.com` | Простота |

---

## 🎲 Генерация символов

Используются **строчные латинские буквы** и **цифры**:
```
a-z (26 букв) + 0-9 (10 цифр) = 36 символов
```

**Примеры 4-символьных комбинаций:**
```
abcd  →  poshmarkabcd
x9k2  →  poshmarkx9k2
hj83  →  poshmarkhj83
m5n7  →  poshmarkm5n7
7kp4  →  poshmark7kp4
2b9x  →  poshmark2b9x
```

**Количество уникальных комбинаций:**
```
36^4 = 1,679,616 возможных комбинаций
```

---

## 🔧 Рекомендации по выбору режима

### Используйте "random" если:
- ✅ Нужна максимальная анонимность
- ✅ Не важен брендинг
- ✅ Хотите короткие поддомены

### Используйте "semi_random" если:
- ✅ Хотите узнаваемость (poshmark, depop, etsy)
- ✅ Нужна уникальность для каждой ссылки
- ✅ Важно отслеживать источник трафика

### Используйте "none" если:
- ✅ Поддомены не нужны
- ✅ API уже возвращает готовые ссылки
- ✅ Хотите простоту

---

## 💡 Важные замечания

1. **Ссылки всегда БЕЗ https://**
   - API может вернуть: `https://domain.com/path`
   - В письме будет: `poshmarkabcd.domain.com/path` ✅

2. **Ровно 4 символа в случайной части**
   - Не 4-5, а всегда 4
   - Легче распознать визуально

3. **Префикс применяется только в semi_random**
   - В режиме `random` префикс игнорируется
   - В режиме `none` поддоменов нет вообще

4. **Каждая ссылка уникальна**
   - Новая генерация для каждого email
   - Разные поддомены даже в одной рассылке

---

**Выбирайте режим в зависимости от ваших задач! 🎯**
