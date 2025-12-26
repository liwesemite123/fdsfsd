import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyautogui
import pyperclip
import time
import json
import os
from pathlib import Path


# Global variables for storing button coordinates
coords = {
    "compose_button": None,       # Coordinates for "Compose" button
    "send_button": None,          # Coordinates for "Send" button
}

# Placeholder text to check if template has default content
DEFAULT_TEMPLATE_PREFIX = "Введите текст"


class GmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📧 Gmail Automation Tool Pro")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Переменные для управления отправкой
        self.is_sending = False
        self.should_stop = False
        
        # Настройки по умолчанию
        self.config_file = "gmail_config.json"
        
        # Применяем современную тему
        self.setup_style()
        self.create_ui()
        self.load_config()

    def setup_style(self):
        """Настройка современного стиля интерфейса."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#333333',
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'danger': '#f44336',
            'warning': '#FF9800',
            'info': '#9C27B0',
            'accent': '#00BCD4'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Стили для кнопок
        style.configure('Primary.TButton', 
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Secondary.TButton',
                       background=self.colors['secondary'],
                       foreground='white',
                       font=('Arial', 9),
                       padding=8)
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)

    def create_ui(self):
        """Создание графического интерфейса."""
        # Главный контейнер с прокруткой
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        current_row = 0
        
        # === СЕКЦИЯ 1: Заголовок ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=current_row, column=0, columnspan=3, pady=(0, 15), sticky="ew")
        
        title_label = tk.Label(header_frame, 
                              text="📧 Gmail Automation Tool Pro",
                              font=('Arial', 18, 'bold'),
                              fg=self.colors['primary'],
                              bg=self.colors['bg'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Автоматизированная отправка писем с гибкими настройками",
                                 font=('Arial', 10),
                                 fg=self.colors['fg'],
                                 bg=self.colors['bg'])
        subtitle_label.pack()
        
        current_row += 1
        
        # === СЕКЦИЯ 2: Настройки задержек ===
        delay_frame = ttk.LabelFrame(main_frame, text="⏱️ Настройки задержек", padding="10")
        delay_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Задержка между письмами
        tk.Label(delay_frame, text="Задержка между письмами (сек):", 
                font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.email_delay = tk.Scale(delay_frame, from_=1, to=30, orient=tk.HORIZONTAL, 
                                   length=250, tickinterval=5)
        self.email_delay.set(3)
        self.email_delay.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(delay_frame, text="Задержка между действиями (сек):",
                font=('Arial', 9)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.action_delay = tk.Scale(delay_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL,
                                     length=250, resolution=0.1, tickinterval=1)
        self.action_delay.set(0.5)
        self.action_delay.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(delay_frame, text="Задержка для вставки текста (сек):",
                font=('Arial', 9)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.paste_delay = tk.Scale(delay_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL,
                                    length=250, resolution=0.1, tickinterval=0.5)
        self.paste_delay.set(0.3)
        self.paste_delay.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        current_row += 1
        
        # === СЕКЦИЯ 3: Координаты кнопок ===
        coords_frame = ttk.LabelFrame(main_frame, text="🎯 Координаты кнопок", padding="10")
        coords_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        tk.Label(coords_frame, text="Кнопка 'Написать':",
                font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.compose_entry = ttk.Entry(coords_frame, width=30)
        self.compose_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(coords_frame, text="📍 Указать", 
                  command=lambda: self.set_coords("compose_button")).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(coords_frame, text="Кнопка 'Отправить':",
                font=('Arial', 9, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.send_entry = ttk.Entry(coords_frame, width=30)
        self.send_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(coords_frame, text="📍 Указать",
                  command=lambda: self.set_coords("send_button")).grid(row=1, column=2, padx=5, pady=5)
        
        current_row += 1
        
        # === СЕКЦИЯ 4: Шаблоны ===
        templates_frame = ttk.LabelFrame(main_frame, text="📝 Шаблоны сообщений", padding="10")
        templates_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        for i in range(1, 4):
            tk.Label(templates_frame, text=f"Шаблон {i}:",
                    font=('Arial', 9, 'bold')).grid(row=i-1, column=0, padx=5, pady=5, sticky="ne")
            template_text = tk.Text(templates_frame, width=60, height=3, wrap=tk.WORD,
                                   font=('Arial', 9))
            template_text.insert("1.0", f"Введите текст шаблона {i} здесь...")
            template_text.grid(row=i-1, column=1, padx=5, pady=5, columnspan=2)
            setattr(self, f'template{i}_entry', template_text)
        
        current_row += 1
        
        # === СЕКЦИЯ 5: Файл с email ===
        file_frame = ttk.LabelFrame(main_frame, text="📁 Файл с email адресами", padding="10")
        file_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        tk.Label(file_frame, text="Выбранный файл:",
                font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.email_label = tk.Label(file_frame, text="Файл не выбран", 
                                    fg="gray", font=('Arial', 9, 'italic'))
        self.email_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(file_frame, text="📂 Выбрать файл",
                  command=self.select_email_file).grid(row=0, column=2, padx=5, pady=5)
        
        current_row += 1
        
        # === СЕКЦИЯ 6: Управление ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=current_row, column=0, columnspan=3, pady=15, sticky="ew")
        
        # Центрируем кнопки
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=0)
        control_frame.columnconfigure(2, weight=0)
        control_frame.columnconfigure(3, weight=0)
        control_frame.columnconfigure(4, weight=1)
        
        self.start_button = tk.Button(control_frame, text="▶️ Запустить отправку",
                                      command=self.start_sending,
                                      bg=self.colors['primary'], fg='white',
                                      font=('Arial', 11, 'bold'),
                                      padx=20, pady=10)
        self.start_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="⏹️ Остановить",
                                     command=self.stop_sending,
                                     bg=self.colors['danger'], fg='white',
                                     font=('Arial', 11, 'bold'),
                                     padx=20, pady=10,
                                     state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)
        
        tk.Button(control_frame, text="💾 Сохранить настройки",
                 command=self.save_config,
                 bg=self.colors['info'], fg='white',
                 font=('Arial', 10),
                 padx=15, pady=10).grid(row=0, column=3, padx=5)
        
        current_row += 1
        
        # === СЕКЦИЯ 7: Прогресс бар ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=800, mode='determinate',
                                           variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, padx=10)
        
        self.progress_label = tk.Label(progress_frame, text="Готов к работе",
                                      font=('Arial', 9), fg=self.colors['fg'])
        self.progress_label.pack(pady=5)
        
        current_row += 1
        
        # === СЕКЦИЯ 8: Лог ===
        log_frame = ttk.LabelFrame(main_frame, text="📋 Журнал событий", padding="10")
        log_frame.grid(row=current_row, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Текстовая область с прокруткой
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_area = tk.Text(log_container, wrap=tk.WORD, width=80, height=12,
                               font=('Consolas', 9), yscrollcommand=scrollbar.set)
        self.log_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_area.yview)
        
        # Цвета для разных типов логов
        self.log_area.tag_config('info', foreground='#2196F3')
        self.log_area.tag_config('success', foreground='#4CAF50')
        self.log_area.tag_config('error', foreground='#f44336')
        self.log_area.tag_config('warning', foreground='#FF9800')
        
        # Кнопка очистки лога
        ttk.Button(log_frame, text="🗑️ Очистить лог",
                  command=self.clear_log).pack(pady=5)
        
        current_row += 1
        
        # === СЕКЦИЯ 9: Статус бар внизу ===
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
        status_frame.grid(row=current_row, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
        self.status_label = tk.Label(status_frame, 
                                     text="⚡ Готов к работе | v2.0 Pro Edition",
                                     font=('Arial', 8),
                                     fg=self.colors['fg'],
                                     anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Добавляем всплывающие подсказки
        self.add_tooltips()
        
        # Добавляем горячие клавиши
        self.setup_keyboard_shortcuts()

    def add_tooltips(self):
        """Add tooltips/hints to UI elements."""
        # Tooltips could be implemented using a library like tkinter.tooltip
        # For now keeping simple version without external dependencies
        pass

    def setup_keyboard_shortcuts(self):
        """Настройка горячих клавиш."""
        self.root.bind('<Control-s>', lambda e: self.save_config())
        self.root.bind('<F5>', lambda e: self.start_sending())
        self.root.bind('<Escape>', lambda e: self.stop_sending())

    def add_log(self, message, level='info'):
        """Добавление сообщений в лог с цветовой маркировкой."""
        timestamp = time.strftime('%H:%M:%S')
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }
        
        icon = icons.get(level, 'ℹ️')
        full_message = f"[{timestamp}] {icon} {message}\n"
        
        self.log_area.insert(tk.END, full_message, level)
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Очистка лога."""
        self.log_area.delete('1.0', tk.END)
        self.add_log("Лог очищен", 'info')

    def set_coords(self, key):
        """Установка координат по клику."""
        display_names = {
            "compose_button": "кнопки 'Написать'",
            "send_button": "кнопки 'Отправить'"
        }
        name = display_names.get(key, key)
        
        response = messagebox.askokcancel(
            "Установка координат",
            f"Наведите курсор на {name}.\n\n"
            f"После нажатия OK у вас будет 3 секунды,\n"
            f"чтобы навести курсор на нужную позицию.\n\n"
            f"Позиция будет определена автоматически."
        )
        
        if not response:
            return
        
        # Даем время на наведение курсора
        for i in range(3, 0, -1):
            self.add_log(f"Захват позиции через {i} секунд...", 'warning')
            time.sleep(1)
        
        # Несколько быстрых замеров для точности
        samples = []
        for _ in range(5):
            samples.append(pyautogui.position())
            time.sleep(0.05)
        
        avg_x = int(sum(p[0] for p in samples) / len(samples))
        avg_y = int(sum(p[1] for p in samples) / len(samples))
        coords[key] = (avg_x, avg_y)
        
        # Обновляем поле ввода
        entry = getattr(self, f"{key.split('_')[0]}_entry")
        entry.delete(0, tk.END)
        entry.insert(0, str(coords[key]))
        
        self.add_log(f"Координаты для '{name}' установлены: {coords[key]}", 'success')
        self.status_label.config(text=f"✅ Координаты {name} сохранены")

    def select_email_file(self):
        """Выбор TXT файла с email адресами."""
        file = filedialog.askopenfilename(
            title="Выберите TXT файл с email адресами",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file:
            self.email_file = file
            filename = os.path.basename(file)
            self.email_label.config(text=filename, fg=self.colors['primary'])
            self.add_log(f"Выбран файл: {filename}", 'success')
            
            # Показываем количество email в файле
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    emails = [line.strip() for line in f if line.strip()]
                self.add_log(f"Найдено {len(emails)} email адресов в файле", 'info')
                self.status_label.config(text=f"📧 Загружено {len(emails)} адресов")
            except Exception as e:
                self.add_log(f"Ошибка чтения файла: {e}", 'error')

    def validate_inputs(self):
        """Проверка всех входных данных."""
        required_coords = ["compose_button", "send_button"]
        for coord in required_coords:
            if not coords.get(coord):
                messagebox.showerror("Ошибка", 
                                   f"Пожалуйста, укажите координаты для '{coord}'.")
                return False
        
        if not hasattr(self, "email_file"):
            messagebox.showerror("Ошибка", 
                               "Пожалуйста, выберите файл с email адресами.")
            return False
        
        # Проверяем, что есть хотя бы один шаблон
        templates = self.get_templates()
        if not any(templates):
            messagebox.showerror("Ошибка",
                               "Пожалуйста, заполните хотя бы один шаблон.")
            return False
        
        return True

    def get_templates(self):
        """Получение всех шаблонов."""
        templates = []
        for i in range(1, 4):
            template_text = getattr(self, f'template{i}_entry')
            text = template_text.get("1.0", tk.END).strip()
            templates.append(text if text and not text.startswith(DEFAULT_TEMPLATE_PREFIX) else "")
        return templates

    def attempt_paste(self, text):
        """Вставка текста через буфер обмена."""
        paste_delay = self.paste_delay.get()
        
        pyperclip.copy(text)
        time.sleep(0.05)
        
        try:
            pyautogui.hotkey("ctrl", "v")
            time.sleep(paste_delay)
            return True
        except Exception as e:
            self.add_log(f"Ошибка CTRL+V: {e}, пробую SHIFT+INSERT", 'warning')
            try:
                pyautogui.hotkey("shift", "insert")
                time.sleep(paste_delay)
                return True
            except Exception as e2:
                self.add_log(f"Ошибка вставки текста: {e2}", 'error')
                return False

    def send_email(self, recipient, message):
        """Отправка одного письма."""
        if self.should_stop:
            return False
        
        action_delay = self.action_delay.get()
        
        try:
            # Клик на кнопку "Написать"
            self.add_log(f"Открываю новое письмо...", 'info')
            pyautogui.click(*coords["compose_button"])
            time.sleep(action_delay)
            
            # Вставляем email получателя
            self.add_log(f"Ввожу адрес: {recipient}", 'info')
            if not self.attempt_paste(recipient):
                return False
            
            # Переходим к теме (пропускаем)
            pyautogui.press("tab")
            time.sleep(action_delay * 0.5)
            
            # Переходим к телу письма
            pyautogui.press("tab")
            time.sleep(action_delay * 0.5)
            
            # Вставляем сообщение
            self.add_log(f"Вставляю текст сообщения...", 'info')
            if not self.attempt_paste(message):
                return False
            
            # Отправляем письмо
            self.add_log(f"Отправляю письмо...", 'info')
            pyautogui.click(*coords["send_button"])
            time.sleep(action_delay)
            
            self.add_log(f"✉️ Письмо успешно отправлено на {recipient}", 'success')
            return True
            
        except Exception as e:
            self.add_log(f"Ошибка при отправке на {recipient}: {e}", 'error')
            return False

    def start_sending(self):
        """Запуск процесса отправки."""
        if self.is_sending:
            messagebox.showinfo("Информация", "Отправка уже выполняется!")
            return
        
        if not self.validate_inputs():
            return
        
        # Подтверждение от пользователя
        response = messagebox.askyesno(
            "Подтверждение",
            "Вы уверены, что хотите начать отправку писем?\n\n"
            "Убедитесь, что Gmail открыт в браузере\n"
            "и вы находитесь на главной странице."
        )
        
        if not response:
            return
        
        self.is_sending = True
        self.should_stop = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Загружаем email адреса
        try:
            with open(self.email_file, "r", encoding='utf-8') as file:
                emails = [email.strip() for email in file.readlines() if email.strip()]
        except Exception as e:
            self.add_log(f"Ошибка чтения файла: {e}", 'error')
            self.reset_sending_state()
            return
        
        # Получаем шаблоны
        templates = [t for t in self.get_templates() if t]
        
        if not templates:
            messagebox.showerror("Ошибка", "Нет доступных шаблонов!")
            self.reset_sending_state()
            return
        
        total_emails = len(emails)
        email_delay = self.email_delay.get()
        
        self.add_log(f"🚀 Начинаю отправку {total_emails} писем...", 'success')
        self.add_log(f"Используется шаблонов: {len(templates)}", 'info')
        self.add_log(f"Задержка между письмами: {email_delay} сек", 'info')
        
        self.progress_var.set(0)
        
        # Даем пользователю время переключиться на Gmail
        for i in range(5, 0, -1):
            self.add_log(f"Начало через {i} секунд... Переключитесь на Gmail!", 'warning')
            self.status_label.config(text=f"⏰ Начало через {i} секунд...")
            time.sleep(1)
            if self.should_stop:
                self.reset_sending_state()
                return
        
        # Отправка писем
        sent_count = 0
        failed_count = 0
        
        for idx, email in enumerate(emails, 1):
            if self.should_stop:
                self.add_log("⏹️ Отправка остановлена пользователем", 'warning')
                break
            
            # Выбираем шаблон циклически
            template_idx = (idx - 1) % len(templates)
            message = templates[template_idx]
            
            self.status_label.config(text=f"📤 Отправка {idx}/{total_emails}: {email}")
            self.add_log(f"[{idx}/{total_emails}] Отправляю на {email} (шаблон {template_idx + 1})", 'info')
            
            # Отправляем письмо
            if self.send_email(email, message):
                sent_count += 1
            else:
                failed_count += 1
            
            # Обновляем прогресс
            progress = (idx / total_emails) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"Прогресс: {idx}/{total_emails} ({progress:.1f}%)")
            
            # Задержка перед следующим письмом
            if idx < total_emails and not self.should_stop:
                for i in range(int(email_delay)):
                    if self.should_stop:
                        break
                    remaining = email_delay - i
                    self.status_label.config(text=f"⏳ Пауза: {remaining:.0f} сек...")
                    time.sleep(1)
        
        # Завершение
        self.progress_var.set(100)
        self.add_log("=" * 60, 'info')
        self.add_log(f"✅ Отправка завершена!", 'success')
        self.add_log(f"📊 Успешно: {sent_count} | Ошибок: {failed_count} | Всего: {total_emails}", 'info')
        
        self.status_label.config(text=f"✅ Готово! Отправлено: {sent_count}/{total_emails}")
        
        messagebox.showinfo(
            "Отправка завершена",
            f"Отправка завершена!\n\n"
            f"Успешно: {sent_count}\n"
            f"Ошибок: {failed_count}\n"
            f"Всего: {total_emails}"
        )
        
        self.reset_sending_state()

    def stop_sending(self):
        """Остановка отправки."""
        if self.is_sending:
            response = messagebox.askyesno(
                "Подтверждение",
                "Вы уверены, что хотите остановить отправку?"
            )
            if response:
                self.should_stop = True
                self.add_log("Получен сигнал остановки...", 'warning')
                self.status_label.config(text="⏹️ Остановка...")

    def reset_sending_state(self):
        """Сброс состояния отправки."""
        self.is_sending = False
        self.should_stop = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def save_config(self):
        """Сохранение конфигурации в файл."""
        config = {
            'email_delay': self.email_delay.get(),
            'action_delay': self.action_delay.get(),
            'paste_delay': self.paste_delay.get(),
            'coords': coords,
            'templates': self.get_templates(),
            'email_file': getattr(self, 'email_file', '')
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.add_log("💾 Настройки сохранены успешно", 'success')
            messagebox.showinfo("Успех", "Настройки сохранены!")
        except Exception as e:
            self.add_log(f"Ошибка сохранения настроек: {e}", 'error')
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки:\n{e}")

    def load_config(self):
        """Загрузка конфигурации из файла."""
        if not os.path.exists(self.config_file):
            self.add_log("Файл конфигурации не найден, используются настройки по умолчанию", 'info')
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Восстанавливаем настройки
            self.email_delay.set(config.get('email_delay', 3))
            self.action_delay.set(config.get('action_delay', 0.5))
            self.paste_delay.set(config.get('paste_delay', 0.3))
            
            # Restore coordinates
            saved_coords = config.get('coords', {})
            for key, value in saved_coords.items():
                if value:
                    # Ensure coordinates are properly formatted as tuple of two integers
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        try:
                            coords[key] = (int(value[0]), int(value[1]))
                            entry = getattr(self, f"{key.split('_')[0]}_entry", None)
                            if entry:
                                entry.delete(0, tk.END)
                                entry.insert(0, str(coords[key]))
                        except (ValueError, IndexError):
                            self.add_log(f"Ошибка загрузки координат для '{key}'", 'warning')
            
            # Восстанавливаем шаблоны
            templates = config.get('templates', [])
            for i, template in enumerate(templates[:3], 1):
                if template:
                    template_text = getattr(self, f'template{i}_entry')
                    template_text.delete("1.0", tk.END)
                    template_text.insert("1.0", template)
            
            # Восстанавливаем путь к файлу
            email_file = config.get('email_file', '')
            if email_file and os.path.exists(email_file):
                self.email_file = email_file
                self.email_label.config(text=os.path.basename(email_file), 
                                       fg=self.colors['primary'])
            
            self.add_log("✅ Настройки загружены из файла", 'success')
            
        except Exception as e:
            self.add_log(f"Ошибка загрузки настроек: {e}", 'error')


def main():
    """Главная функция запуска приложения."""
    root = tk.Tk()
    app = GmailSenderApp(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
