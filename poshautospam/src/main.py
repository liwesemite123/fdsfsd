"""Main entry point: парсинг -> валидация -> генерация ссылок -> отправка через GoDaddy."""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from src.account_stats import AccountStats
from src.logger import setup_logging
from src.ParserNew import AsyncPoshmarkParser
from src.progress import console, show_banner
from src.GoDaddy import GoDaddyClient
from src.link_generator import LinkGenerator
from src.keyboard_monitor import KeyboardMonitor
from src.Utils import (
    get_cookie_files,
    move_account_to_bad,
    move_account_to_spammed,
    read_message_text,
)
from src.validator import ValidationStatus, cleanup_connections, validate_batch

load_dotenv()

EMAILS_PER_ACCOUNT = int(os.getenv("EMAILS_PER_ACCOUNT", "200"))
EMAILS_PER_BATCH = int(os.getenv("EMAILS_PER_BATCH", "10"))
COOKIES_DIR = os.getenv("COOKIES_DIR", "cookies")
SPAMMED_DIR = os.getenv("SPAMMED_DIR", "spammed_square")
BAD_ACCOUNTS_DIR = os.getenv("BAD_ACCOUNTS_DIR", "bad_accounts")
TARGET_ITEMS_COUNT = int(os.getenv("TARGET_ITEMS_COUNT", "20"))
CONCURRENT_ACCOUNTS = int(os.getenv("CONCURRENT_ACCOUNTS", "2"))


class InvalidAccountError(Exception):
    pass


async def parse_and_validate_emails(items_count: int) -> tuple[list[str], list[dict]]:
    """Централизованный парсинг и валидация email'ов.
    
    Returns:
        Tuple (список валидных email'ов, данные продавцов)
    """
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[cyan]🔍 Парсим {items_count} объявлений...[/cyan]")

    parser = AsyncPoshmarkParser(
        target_items_count=items_count,
    )

    try:
        sellers_data = await parser.Start()
    except Exception as e:
        logging.exception(f"❌ Ошибка парсинга: {e}")
        console.print(f"[red]❌ Ошибка парсинга: {e}[/red]")
        return ([], [])

    if not sellers_data:
        logging.warning("⚠️ Парсинг не вернул результатов")
        console.print("[yellow]⚠️ Парсинг не вернул результатов[/yellow]")
        return ([], [])

    emails = [seller["email"] for seller in sellers_data]
    logging.info(f"✅ Спарсено {len(emails)} email")
    console.print(f"[green]✅ Спарсено {len(emails)} email[/green]")

    console.print(f"[cyan]🔎 Валидируем {len(emails)} email...[/cyan]")

    def progress_callback(email: str, status: ValidationStatus):
        if status == ValidationStatus.VALID:
            console.print(f"[green]✅ {email} - валиден[/green]")
        elif status == ValidationStatus.INVALID:
            console.print(f"[red]❌ {email} - невалиден[/red]")
        else:
            console.print(f"[yellow]⚠️ {email} - ошибка валидации[/yellow]")

    try:
        validation_results = await validate_batch(
            emails=emails,
            progress_callback=progress_callback,
            max_concurrent=25,
            timeout=10.0
        )
    except Exception as e:
        logging.exception(f"❌ Ошибка валидации: {e}")
        console.print(f"[red]❌ Ошибка валидации: {e}[/red]")
        return ([], sellers_data)

    valid_emails = [
        result.email
        for result in validation_results
        if result.status == ValidationStatus.VALID
    ]

    valid_count = len(valid_emails)
    console.print(f"[bold green]✅ Валидных email: {valid_count}/{len(emails)}[/bold green]")

    return (valid_emails, sellers_data)


async def generate_links_for_emails(
    sellers_data: list[dict],
    valid_emails: list[str]
) -> tuple[dict[str, str], dict[str, str]]:
    """Генерирует персональные ссылки для валидных email'ов.
    
    Args:
        sellers_data: Данные продавцов из парсера
        valid_emails: Список валидных email'ов
        
    Returns:
        Tuple (словарь {email: generated_link}, словарь {email: title})
    """
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[cyan]🔗 Генерируем персональные ссылки для {len(valid_emails)} email...[/cyan]")
    
    link_generator = LinkGenerator()
    
    # Создаём словарь email -> данные продавца
    email_to_seller = {seller["email"]: seller for seller in sellers_data}
    
    # Создаём словарь email -> title для логирования (используем username как title)
    email_to_title = {email: email_to_seller.get(email, {}).get("username", "Unknown User") for email in valid_emails}
    
    # Формируем список получателей для генерации ссылок
    recipients = []
    for email in valid_emails:
        seller = email_to_seller.get(email, {})
        username = seller.get("username", "Customer")
        recipients.append({
            "email": email,
            "name": username,
            "title": username,  # Title = username продавца
            "address": None,  # Нет данных из парсера, будет использован дефолт
            "photo": None,    # Нет данных из парсера, будет использован дефолт
            "price": None     # Нет данных из парсера, будет использован дефолт
        })
    
    # Генерируем ссылки батчами
    email_to_link = await link_generator.generate_links_batch(
        recipients=recipients,
        max_concurrent=5
    )
    
    success_count = len(email_to_link)
    console.print(f"[bold green]✅ Успешно сгенерировано ссылок: {success_count}/{len(valid_emails)}[/bold green]")
    
    if success_count < len(valid_emails):
        failed_emails = set(valid_emails) - set(email_to_link.keys())
        console.print(f"[yellow]⚠️ Не удалось сгенерировать ссылки для {len(failed_emails)} email'ов[/yellow]")
        logging.warning(f"Не удалось сгенерировать ссылки для: {failed_emails}")
    
    return email_to_link, email_to_title


async def process_account(
    cookie_file: str,
    message: str,
    assigned_emails: list[str],
    email_to_link: dict[str, str],
    email_to_title: dict[str, str],
    account_sent_count: int,
    target_emails: int,
    keyboard_monitor: KeyboardMonitor = None
) -> tuple[int, GoDaddyClient | None]:
    """Обработка аккаунта с назначенными email'ами.
    
    Args:
        cookie_file: Путь к файлу с куками
        message: Шаблон сообщения
        assigned_emails: Список email'ов для отправки
        email_to_link: Словарь {email: generated_link}
        email_to_title: Словарь {email: title}
        account_sent_count: Сколько уже отправлено этим аккаунтом
        target_emails: Целевое количество писем
        keyboard_monitor: Монитор клавиатуры для паузы
    
    Returns:
        Tuple (количество отправленных писем в этой итерации, клиент или None)
    """
    account_name = Path(cookie_file).stem
    cookie_filename = Path(cookie_file).name

    if not assigned_emails:
        return (0, None)

    try:
        godaddy_client = GoDaddyClient(cookie_file, cookie_filename)
    except Exception as e:
        logging.exception(f"❌ Ошибка загрузки куков для {account_name}: {e}")
        console.print(f"[bold red]❌ [{cookie_filename}] Ошибка загрузки куков: {e}[/bold red]")
        raise InvalidAccountError(f"Ошибка загрузки куков: {e}")

    console.print(f"\n[bold cyan]📧 [{cookie_filename}] Отправка {len(assigned_emails)} писем ({account_sent_count}/{target_emails})[/bold cyan]")

    # Разбиваем на батчи
    batches = [
        assigned_emails[i:i + EMAILS_PER_BATCH]
        for i in range(0, len(assigned_emails), EMAILS_PER_BATCH)
    ]

    sent_count = 0
    for batch_idx, batch in enumerate(batches, 1):
        # Проверяем паузу перед каждым батчом
        if keyboard_monitor:
            await keyboard_monitor.wait_if_paused()
            
        try:
            # Фильтруем словарь ссылок только для текущего батча
            batch_links = {email: email_to_link.get(email) for email in batch if email in email_to_link}
            
            # Логируем отправку
            for email in batch:
                link = batch_links.get(email, "NO_LINK")
                title = email_to_title.get(email, "Unknown")
                logging.info(f"📤 Отправка письма на {email} | Title: {title} | Ссылка: {link}")
            
            result = await godaddy_client.execute_solo_conversation(
                email_list=batch,
                message=message,
                email_to_link=batch_links
            )

            if result and isinstance(result, dict) and result.get("successful"):
                sent_count += len(batch)
                new_total = account_sent_count + sent_count
                
                # Логируем успешную отправку для каждого email
                for email in batch:
                    link = batch_links.get(email, "NO_LINK")
                    title = email_to_title.get(email, "Unknown")
                    logging.info(f"✅ Успешно отправлено на {email} | Title: {title} | Ссылка: {link}")
                
                console.print(
                    f"[green]✅ [{cookie_filename}] Батч {batch_idx}/{len(batches)} "
                    f"отправлен ({len(batch)} писем) | Всего: {new_total}/{target_emails}[/green]"
                )
            else:
                logging.error(f"❌ [{account_name}] Ошибка отправки батча {batch_idx}: {result}")

                if isinstance(result, tuple) and len(result) == 2 and result[0] == 401:
                    console.print(f"[bold red]🚫 [{cookie_filename}] 401 UNAUTHORIZED - Аккаунт невалиден![/bold red]")
                    logging.error(f"401 UNAUTHORIZED для аккаунта {account_name}")
                    raise InvalidAccountError("401 UNAUTHORIZED - куки невалидны")

                console.print(f"[yellow]⚠️ [{cookie_filename}] Пропускаем батч {batch_idx}[/yellow]")
                continue

        except InvalidAccountError:
            raise
        except Exception as e:
            logging.exception(f"❌ [{account_name}] Исключение при отправке батча {batch_idx}: {e}")
            console.print(f"[red]❌ [{cookie_filename}] Исключение: {e}[/red]")
            continue

        if batch_idx < len(batches):
            await asyncio.sleep(2)

    return (sent_count, godaddy_client)


async def process_account_wrapper(
    cookie_file: str,
    message: str,
    assigned_emails: list[str],
    email_to_link: dict[str, str],
    email_to_title: dict[str, str],
    account_sent_count: int,
    target_emails: int,
    keyboard_monitor: KeyboardMonitor = None
) -> tuple[str, int, Exception | None]:
    """Обёртка для обработки аккаунта.
    
    Returns:
        Tuple (cookie_file, количество отправленных писем, ошибка или None)
    """
    account_name = Path(cookie_file).stem
    cookie_filename = Path(cookie_file).name
    
    try:
        sent_count, _ = await process_account(
            cookie_file,
            message,
            assigned_emails,
            email_to_link,
            email_to_title,
            account_sent_count,
            target_emails,
            keyboard_monitor
        )
        return (cookie_file, sent_count, None)
    
    except InvalidAccountError as e:
        logging.exception(f"🚫 Аккаунт {account_name} невалиден (401): {e}")
        console.print(f"[bold red]🚫 [{cookie_filename}] Невалиден - перемещаем в bad_accounts[/bold red]")
        return (cookie_file, 0, e)
    
    except Exception as e:
        logging.exception(f"❌ Критическая ошибка при обработке {account_name}: {e}")
        console.print(f"[bold red]❌ [{cookie_filename}] Критическая ошибка: {e}[/bold red]")
        return (cookie_file, 0, e)


async def main() -> int:
    setup_logging()
    logging.info("GoDaddy Spammer starting...")

    show_banner()

    Path(COOKIES_DIR).mkdir(exist_ok=True)
    Path(SPAMMED_DIR).mkdir(exist_ok=True)
    Path(BAD_ACCOUNTS_DIR).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    stats_manager = AccountStats()
    
    # Создаём клавишный монитор
    keyboard_monitor = KeyboardMonitor()
    
    # Запускаем мониторинг клавиатуры в фоновом режиме
    keyboard_task = asyncio.create_task(keyboard_monitor.start_monitoring())

    try:
        cookie_files = get_cookie_files(COOKIES_DIR)
        account_count = len(cookie_files)

        if account_count == 0:
            logging.error(f"❌ Не найдено файлов куков в папке '{COOKIES_DIR}'")
            console.print(f"[bold red]❌ Не найдено файлов куков в папке '{COOKIES_DIR}'[/bold red]")
            console.print(f"[yellow]💡 Поместите JSON файлы с куками в папку '{COOKIES_DIR}'[/yellow]\n")
            return 1

        console.print(f"\n[bold cyan]📁 Найдено аккаунтов: {account_count}[/bold cyan]")
        console.print(f"[bold cyan]🎯 Цель: {EMAILS_PER_ACCOUNT} писем на аккаунт[/bold cyan]")
        console.print(f"[bold cyan]📦 Парсинг: {TARGET_ITEMS_COUNT} объявлений на итерацию[/bold cyan]\n")
        logging.info(f"📁 Найдено аккаунтов: {account_count}")
        logging.info(f"🎯 Цель: {EMAILS_PER_ACCOUNT} писем на аккаунт")

        message = read_message_text("Texts/text.txt", "Hello, sorry for distrub its just a test.")

        # Формируем список аккаунтов
        accounts_str = ", ".join([Path(cf).name for cf in cookie_files])
        console.print(f"[bold cyan]📁 Аккаунты: {accounts_str}[/bold cyan]\n")
        logging.info(f"📁 Аккаунты: {accounts_str}")

        # Трекер отправленных писем для каждого аккаунта
        account_sent = {Path(cf).stem: 0 for cf in cookie_files}
        bad_accounts = set()
        iteration = 0

        # Основной цикл: парсинг -> валидация -> распределение -> отправка
        while True:
            iteration += 1
            
            # Проверяем, есть ли аккаунты, которые еще не достигли цели
            active_accounts = [
                cf for cf in cookie_files 
                if Path(cf).stem not in bad_accounts and account_sent[Path(cf).stem] < EMAILS_PER_ACCOUNT
            ]
            
            if not active_accounts:
                console.print("\n[bold green]✅ Все аккаунты достигли цели![/bold green]")
                break

            console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
            console.print(f"[bold yellow]🔄 ИТЕРАЦИЯ {iteration}[/bold yellow]")
            console.print(f"[bold yellow]{'='*60}[/bold yellow]")
            
            # Показываем прогресс по аккаунтам
            console.print("[cyan]📊 Прогресс по аккаунтам:[/cyan]")
            for cf in cookie_files:
                acc_name = Path(cf).stem
                acc_filename = Path(cf).name
                if acc_name in bad_accounts:
                    console.print(f"  [red]❌ [{acc_filename}]: невалиден[/red]")
                else:
                    sent = account_sent[acc_name]
                    console.print(f"  [cyan]✅ [{acc_filename}]: {sent}/{EMAILS_PER_ACCOUNT}[/cyan]")
            
            # Шаг 1: Парсинг и валидация
            await keyboard_monitor.wait_if_paused()
            valid_emails, sellers_data = await parse_and_validate_emails(TARGET_ITEMS_COUNT)
            
            if not valid_emails:
                console.print("[yellow]⚠️ Не получены валидные email'ы, повторяем попытку...[/yellow]")
                await asyncio.sleep(5)
                continue
            
            # Шаг 2: Генерация персональных ссылок
            await keyboard_monitor.wait_if_paused()
            email_to_link, email_to_title = await generate_links_for_emails(sellers_data, valid_emails)
            
            # Фильтруем только те email, для которых успешно сгенерированы ссылки
            valid_emails = [email for email in valid_emails if email in email_to_link]
            
            if not valid_emails:
                console.print("[yellow]⚠️ Не удалось сгенерировать ссылки, повторяем попытку...[/yellow]")
                await asyncio.sleep(5)
                continue

            # Шаг 3: Распределение email'ов между активными аккаунтами
            console.print(f"\n[bold cyan]📦 Распределение {len(valid_emails)} email'ов между {len(active_accounts)} аккаунтами...[/bold cyan]")
            
            # Распределяем по кругу (round-robin)
            distribution = {Path(cf).stem: [] for cf in active_accounts}
            for idx, email in enumerate(valid_emails):
                account_idx = idx % len(active_accounts)
                account_name = Path(active_accounts[account_idx]).stem
                
                # Ограничиваем, чтобы не превысить EMAILS_PER_ACCOUNT
                if account_sent[account_name] + len(distribution[account_name]) < EMAILS_PER_ACCOUNT:
                    distribution[account_name].append(email)
            
            # Шаг 4: Отправка параллельно
            await keyboard_monitor.wait_if_paused()
            console.print(f"\n[bold green]🚀 Запуск отправки...[/bold green]\n")
            
            tasks = [
                process_account_wrapper(
                    cookie_file=cf,
                    message=message,
                    assigned_emails=distribution[Path(cf).stem],
                    email_to_link=email_to_link,
                    email_to_title=email_to_title,
                    account_sent_count=account_sent[Path(cf).stem],
                    target_emails=EMAILS_PER_ACCOUNT,
                    keyboard_monitor=keyboard_monitor
                )
                for cf in active_accounts
                if distribution[Path(cf).stem]  # Только если есть email'ы
            ]
            
            if not tasks:
                console.print("[yellow]⚠️ Нет задач для выполнения[/yellow]")
                break

            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            # Обработка результатов
            for cookie_file, sent_count, error in results:
                account_name = Path(cookie_file).stem
                
                if error is not None:
                    if isinstance(error, InvalidAccountError):
                        bad_accounts.add(account_name)
                        move_account_to_bad(cookie_file, BAD_ACCOUNTS_DIR)
                    continue
                
                # Обновляем трекер
                account_sent[account_name] += sent_count
                
                # Сохраняем статистику после каждой итерации
                stats_manager.save_stats(
                    account_name,
                    account_sent[account_name],
                    EMAILS_PER_ACCOUNT,
                    account_sent[account_name] >= EMAILS_PER_ACCOUNT
                )
            
            console.print(f"\n[bold]📊 Итерация {iteration} завершена[/bold]")
            
            # Пауза перед следующей итерацией
            await asyncio.sleep(3)

        # Сохраняем статистику и перемещаем аккаунты
        console.print(f"\n[bold green]{'='*60}[/bold green]")
        console.print("[bold green]🎉 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ[/bold green]")
        console.print(f"[bold green]{'='*60}[/bold green]\n")
        
        for cf in cookie_files:
            account_name = Path(cf).stem
            acc_filename = Path(cf).name
            sent = account_sent[account_name]
            
            if account_name in bad_accounts:
                console.print(f"[red]❌ [{acc_filename}]: невалиден[/red]")
            else:
                console.print(f"[green]✅ [{acc_filename}]: {sent}/{EMAILS_PER_ACCOUNT} писем[/green]")
                
                # Перемещаем в spammed, если достиг цели
                if sent >= EMAILS_PER_ACCOUNT:
                    move_account_to_spammed(cf, SPAMMED_DIR)

        console.print(f"\n[bold green]{'='*60}[/bold green]")
        console.print("[bold green]✅ ВСЕ АККАУНТЫ ОБРАБОТАНЫ[/bold green]")
        console.print(f"[bold green]{'='*60}[/bold green]\n")

        return 0

    except Exception as e:
        logging.exception("Unexpected error: %s", e)
        console.print(f"[bold red]❌ Критическая ошибка: {e}[/bold red]")
        return 1

    finally:
        # Останавливаем клавишный монитор
        keyboard_monitor.stop()
        keyboard_task.cancel()
        try:
            await keyboard_task
        except asyncio.CancelledError:
            pass
            
        logging.info("Cleaning up connections...")
        await cleanup_connections()
        logging.info("GoDaddy Spammer finished")
