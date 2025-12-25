"""Модуль для мониторинга клавиатуры во время спама."""

import asyncio
import logging
import msvcrt
import os
import random
from pathlib import Path

from src.progress import console
from src.link_generator import LinkGenerator
from src.GoDaddy import GoDaddyClient
from src.Utils import get_cookie_files, read_message_text


class KeyboardMonitor:
    """Монитор нажатий клавиш для управления спамом."""
    
    def __init__(self):
        self.is_paused = False
        self.should_stop = False
        self._lock = asyncio.Lock()
        
    async def start_monitoring(self):
        """Запуск мониторинга клавиатуры в фоновом режиме."""
        console.print("\n[bold yellow]⌨️  УПРАВЛЕНИЕ: P-Пауза | R-Возобновить | I-Проверка inbox[/bold yellow]\n")
        logging.info("⌨️ Запущен мониторинг клавиатуры")
        
        while not self.should_stop:
            await asyncio.sleep(0.1)  # Небольшая задержка
            
            # Проверяем нажатия клавиш (только в Windows)
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').upper()
                
                if key == 'P':
                    await self.pause()
                elif key == 'R':
                    await self.resume()
                elif key == 'I':
                    if self.is_paused:
                        await self.check_inbox()
                    else:
                        console.print("[yellow]⚠️  Для проверки inbox сначала поставьте на паузу (нажмите P)[/yellow]")
                        
    async def pause(self):
        """Пауза процесса спама."""
        async with self._lock:
            if not self.is_paused:
                self.is_paused = True
                console.print("\n[bold red]⏸️  ПАУЗА - процесс остановлен[/bold red]")
                console.print("[yellow]Нажмите R для возобновления или I для проверки inbox[/yellow]\n")
                logging.info("⏸️ Процесс поставлен на паузу")
                
    async def resume(self):
        """Возобновление процесса спама."""
        async with self._lock:
            if self.is_paused:
                self.is_paused = False
                console.print("\n[bold green]▶️  ВОЗОБНОВЛЕНИЕ - процесс продолжен[/bold green]\n")
                logging.info("▶️ Процесс возобновлён")
            else:
                console.print("[yellow]⚠️  Процесс не был на паузе[/yellow]")
                
    async def check_inbox(self):
        """Отправка тестового письма для проверки inbox."""
        console.print("\n[bold cyan]📨 INBOX CHECK - отправка тестового письма...[/bold cyan]")
        logging.info("📨 Запущена проверка inbox")
        
        try:
            # Получаем список аккаунтов
            cookies_dir = os.getenv("COOKIES_DIR", "cookies")
            cookie_files = get_cookie_files(cookies_dir)
            
            if not cookie_files:
                console.print("[red]❌ Нет доступных аккаунтов в папке cookies[/red]")
                logging.error("❌ Нет доступных аккаунтов для inbox check")
                return
                
            # Выбираем случайный аккаунт
            random_cookie = random.choice(cookie_files)
            account_name = Path(random_cookie).stem
            cookie_filename = Path(random_cookie).name
            
            console.print(f"[cyan]📧 Выбран аккаунт: {cookie_filename}[/cyan]")
            logging.info(f"📧 Тестовое письмо через аккаунт: {cookie_filename}")
            
            # Читаем шаблон
            message = read_message_text()
            if not message:
                console.print("[red]❌ Не удалось прочитать шаблон сообщения[/red]")
                logging.error("❌ Не удалось прочитать шаблон для inbox check")
                return
                
            # Генерируем рандомную ссылку
            link_generator = LinkGenerator()
            test_link = await link_generator.generate_link(
                name="Test User",
                title="Inbox Check Test Item",
                address=None,
                photo=None,
                price=None
            )
            
            if not test_link:
                console.print("[red]❌ Не удалось сгенерировать тестовую ссылку[/red]")
                logging.error("❌ Не удалось сгенерировать ссылку для inbox check")
                return
                
            console.print(f"[green]🔗 Сгенерирована ссылка: {test_link}[/green]")
            
            # Заменяем плейсхолдер в шаблоне
            test_message = message.replace("{LINK}", test_link)
            
            # Инициализируем GoDaddy клиент
            try:
                godaddy_client = GoDaddyClient(random_cookie, cookie_filename)
            except Exception as e:
                console.print(f"[red]❌ Ошибка инициализации аккаунта: {e}[/red]")
                logging.exception(f"❌ Ошибка инициализации GoDaddy для inbox check: {e}")
                return
                
            # Запрашиваем email для inbox check у пользователя
            console.print("\n[bold yellow]📬 Введите email для проверки inbox:[/bold yellow]")
            try:
                inbox_email = input("Email: ").strip()
                if not inbox_email:
                    console.print("[red]❌ Email не может быть пустым[/red]")
                    logging.error("❌ Inbox check: пустой email")
                    return
                if "@" not in inbox_email:
                    console.print("[red]❌ Некорректный формат email[/red]")
                    logging.error(f"❌ Inbox check: некорректный email {inbox_email}")
                    return
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]⚠️  Проверка inbox отменена[/yellow]")
                return
            
            console.print(f"[cyan]📬 Отправка на: {inbox_email}[/cyan]")
            
            # Отправляем письмо
            result = await godaddy_client.execute_solo_conversation(
                email_list=[inbox_email],
                message=test_message,
                email_to_link={inbox_email: test_link}
            )
            
            if result:
                console.print(f"[bold green]✅ Тестовое письмо успешно отправлено на {inbox_email}[/bold green]")
                console.print(f"[green]🔗 Ссылка в письме: {test_link}[/green]")
                logging.info(f"✅ Inbox check: письмо отправлено на {inbox_email} с ссылкой {test_link}")
            else:
                console.print("[red]❌ Не удалось отправить тестовое письмо[/red]")
                logging.error("❌ Inbox check: не удалось отправить письмо")
                
        except Exception as e:
            console.print(f"[red]❌ Ошибка при проверке inbox: {e}[/red]")
            logging.exception(f"❌ Ошибка inbox check: {e}")
            
        console.print("\n[yellow]Нажмите R для возобновления процесса[/yellow]\n")
        
    async def wait_if_paused(self):
        """Ожидание возобновления при паузе."""
        while self.is_paused and not self.should_stop:
            await asyncio.sleep(0.5)
            
    def stop(self):
        """Остановка мониторинга."""
        self.should_stop = True
        logging.info("🛑 Мониторинг клавиатуры остановлен")
