"""Main entry point для Carrd: парсинг -> валидация -> генерация ссылок -> отправка через Carrd."""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from src.account_stats import AccountStats
from src.logger import setup_logging
from src.ParserNew import AsyncPoshmarkParser
from src.progress import console, show_banner
from src.Carrd import CarrdClient
from src.link_generator import LinkGenerator
from src.keyboard_monitor import KeyboardMonitor
from src.Utils import (
    get_site_config_files,
    move_account_to_bad,
    move_account_to_spammed,
    read_message_text,
)
from src.validator import ValidationStatus, cleanup_connections, validate_batch

load_dotenv()

EMAILS_PER_SITE = int(os.getenv("EMAILS_PER_SITE", "200"))
EMAILS_PER_BATCH = int(os.getenv("EMAILS_PER_BATCH", "10"))
SITES_DIR = os.getenv("SITES_DIR", "carrd_sites")
SPAMMED_DIR = os.getenv("SPAMMED_DIR", "spammed_carrd")
BAD_SITES_DIR = os.getenv("BAD_SITES_DIR", "bad_sites")
TARGET_ITEMS_COUNT = int(os.getenv("TARGET_ITEMS_COUNT", "20"))


class InvalidSiteError(Exception):
    """Исключение для невалидных сайтов."""
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
    
    # Создаём словарь email -> title для логирования
    email_to_title = {email: email_to_seller.get(email, {}).get("username", "Unknown User") for email in valid_emails}
    
    # Формируем список получателей для генерации ссылок
    recipients = []
    for email in valid_emails:
        seller = email_to_seller.get(email, {})
        username = seller.get("username", "Customer")
        recipients.append({
            "email": email,
            "name": username,
            "title": username,
            "address": None,
            "photo": None,
            "price": None
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


async def process_site(
    site_config_file: str,
    message: str,
    assigned_emails: list[str],
    email_to_link: dict[str, str],
    email_to_title: dict[str, str],
    site_sent_count: int,
    target_emails: int,
    keyboard_monitor: KeyboardMonitor = None
) -> tuple[int, CarrdClient | None]:
    """Обработка Carrd сайта с назначенными email'ами.
    
    Args:
        site_config_file: Путь к файлу конфигурации сайта
        message: Шаблон сообщения
        assigned_emails: Список email'ов для отправки
        email_to_link: Словарь {email: generated_link}
        email_to_title: Словарь {email: title}
        site_sent_count: Сколько уже отправлено с этого сайта
        target_emails: Целевое количество писем
        keyboard_monitor: Монитор клавиатуры для паузы
    
    Returns:
        Tuple (количество отправленных писем в этой итерации, клиент или None)
    """
    site_name = Path(site_config_file).stem
    site_filename = Path(site_config_file).name

    if not assigned_emails:
        return (0, None)

    try:
        carrd_client = CarrdClient(site_config_file, site_filename)
    except Exception as e:
        logging.exception(f"❌ Ошибка загрузки конфигурации для {site_name}: {e}")
        console.print(f"[bold red]❌ [{site_filename}] Ошибка загрузки конфигурации: {e}[/bold red]")
        raise InvalidSiteError(f"Ошибка загрузки конфигурации: {e}")

    console.print(f"\n[bold cyan]📧 [{site_filename}] Отправка {len(assigned_emails)} форм ({site_sent_count}/{target_emails})[/bold cyan]")

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
                logging.info(f"📤 Отправка формы на {email} | Title: {title} | Ссылка: {link}")
            
            result = await carrd_client.execute_solo_conversation(
                email_list=batch,
                message=message,
                email_to_link=batch_links
            )

            if result and isinstance(result, dict) and result.get("successful"):
                sent_count += len(batch)
                new_total = site_sent_count + sent_count
                
                # Логируем успешную отправку для каждого email
                for email in batch:
                    link = batch_links.get(email, "NO_LINK")
                    title = email_to_title.get(email, "Unknown")
                    logging.info(f"✅ Успешно отправлено на {email} | Title: {title} | Ссылка: {link}")
                
                console.print(
                    f"[green]✅ [{site_filename}] Батч {batch_idx}/{len(batches)} "
                    f"отправлен ({len(batch)} форм) | Всего: {new_total}/{target_emails}[/green]"
                )
            else:
                logging.error(f"❌ [{site_name}] Ошибка отправки батча {batch_idx}: {result}")
                console.print(f"[yellow]⚠️ [{site_filename}] Пропускаем батч {batch_idx}[/yellow]")
                continue

        except InvalidSiteError:
            raise
        except Exception as e:
            logging.exception(f"❌ [{site_name}] Исключение при отправке батча {batch_idx}: {e}")
            console.print(f"[red]❌ [{site_filename}] Исключение: {e}[/red]")
            continue

        if batch_idx < len(batches):
            await asyncio.sleep(2)

    return (sent_count, carrd_client)


async def process_site_wrapper(
    site_config_file: str,
    message: str,
    assigned_emails: list[str],
    email_to_link: dict[str, str],
    email_to_title: dict[str, str],
    site_sent_count: int,
    target_emails: int,
    keyboard_monitor: KeyboardMonitor = None
) -> tuple[str, int, Exception | None]:
    """Обёртка для обработки сайта.
    
    Returns:
        Tuple (site_config_file, количество отправленных форм, ошибка или None)
    """
    site_name = Path(site_config_file).stem
    site_filename = Path(site_config_file).name
    
    try:
        sent_count, _ = await process_site(
            site_config_file,
            message,
            assigned_emails,
            email_to_link,
            email_to_title,
            site_sent_count,
            target_emails,
            keyboard_monitor
        )
        return (site_config_file, sent_count, None)
    
    except InvalidSiteError as e:
        logging.exception(f"🚫 Сайт {site_name} невалиден: {e}")
        console.print(f"[bold red]🚫 [{site_filename}] Невалиден - перемещаем в bad_sites[/bold red]")
        return (site_config_file, 0, e)
    
    except Exception as e:
        logging.exception(f"❌ Критическая ошибка при обработке {site_name}: {e}")
        console.print(f"[bold red]❌ [{site_filename}] Критическая ошибка: {e}[/bold red]")
        return (site_config_file, 0, e)


async def main() -> int:
    setup_logging()
    logging.info("Carrd Spammer starting...")

    show_banner()

    Path(SITES_DIR).mkdir(exist_ok=True)
    Path(SPAMMED_DIR).mkdir(exist_ok=True)
    Path(BAD_SITES_DIR).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    stats_manager = AccountStats()
    
    # Создаём клавишный монитор
    keyboard_monitor = KeyboardMonitor()
    
    # Запускаем мониторинг клавиатуры в фоновом режиме
    keyboard_task = asyncio.create_task(keyboard_monitor.start_monitoring())

    try:
        site_files = get_site_config_files(SITES_DIR)
        site_count = len(site_files)

        if site_count == 0:
            logging.error(f"❌ Не найдено конфигураций сайтов в папке '{SITES_DIR}'")
            console.print(f"[bold red]❌ Не найдено конфигураций сайтов в папке '{SITES_DIR}'[/bold red]")
            console.print(f"[yellow]💡 Поместите JSON файлы с конфигурациями Carrd сайтов в папку '{SITES_DIR}'[/yellow]\n")
            return 1

        console.print(f"\n[bold cyan]📁 Найдено Carrd сайтов: {site_count}[/bold cyan]")
        console.print(f"[bold cyan]🎯 Цель: {EMAILS_PER_SITE} форм на сайт[/bold cyan]")
        console.print(f"[bold cyan]📦 Парсинг: {TARGET_ITEMS_COUNT} объявлений на итерацию[/bold cyan]\n")
        logging.info(f"📁 Найдено Carrd сайтов: {site_count}")
        logging.info(f"🎯 Цель: {EMAILS_PER_SITE} форм на сайт")

        message = read_message_text("Texts/text.txt", "Hello, sorry for disturb its just a test.")

        # Формируем список сайтов
        sites_str = ", ".join([Path(sf).name for sf in site_files])
        console.print(f"[bold cyan]📁 Сайты: {sites_str}[/bold cyan]\n")
        logging.info(f"📁 Сайты: {sites_str}")

        # Трекер отправленных форм для каждого сайта
        site_sent = {Path(sf).stem: 0 for sf in site_files}
        bad_sites = set()
        iteration = 0

        # Основной цикл: парсинг -> валидация -> распределение -> отправка
        while True:
            iteration += 1
            
            # Проверяем, есть ли сайты, которые еще не достигли цели
            active_sites = [
                sf for sf in site_files 
                if Path(sf).stem not in bad_sites and site_sent[Path(sf).stem] < EMAILS_PER_SITE
            ]
            
            if not active_sites:
                console.print("\n[bold green]✅ Все сайты достигли цели![/bold green]")
                break

            console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
            console.print(f"[bold yellow]🔄 ИТЕРАЦИЯ {iteration}[/bold yellow]")
            console.print(f"[bold yellow]{'='*60}[/bold yellow]")
            
            # Показываем прогресс по сайтам
            console.print("[cyan]📊 Прогресс по сайтам:[/cyan]")
            for sf in site_files:
                site_name = Path(sf).stem
                site_filename = Path(sf).name
                if site_name in bad_sites:
                    console.print(f"  [red]❌ [{site_filename}]: невалиден[/red]")
                else:
                    sent = site_sent[site_name]
                    console.print(f"  [cyan]✅ [{site_filename}]: {sent}/{EMAILS_PER_SITE}[/cyan]")
            
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

            # Шаг 3: Распределение email'ов между активными сайтами
            console.print(f"\n[bold cyan]📦 Распределение {len(valid_emails)} email'ов между {len(active_sites)} сайтами...[/bold cyan]")
            
            # Распределяем по кругу (round-robin)
            distribution = {Path(sf).stem: [] for sf in active_sites}
            for idx, email in enumerate(valid_emails):
                site_idx = idx % len(active_sites)
                site_name = Path(active_sites[site_idx]).stem
                
                # Ограничиваем, чтобы не превысить EMAILS_PER_SITE
                if site_sent[site_name] + len(distribution[site_name]) < EMAILS_PER_SITE:
                    distribution[site_name].append(email)
            
            # Шаг 4: Отправка параллельно
            await keyboard_monitor.wait_if_paused()
            console.print(f"\n[bold green]🚀 Запуск отправки...[/bold green]\n")
            
            tasks = [
                process_site_wrapper(
                    site_config_file=sf,
                    message=message,
                    assigned_emails=distribution[Path(sf).stem],
                    email_to_link=email_to_link,
                    email_to_title=email_to_title,
                    site_sent_count=site_sent[Path(sf).stem],
                    target_emails=EMAILS_PER_SITE,
                    keyboard_monitor=keyboard_monitor
                )
                for sf in active_sites
                if distribution[Path(sf).stem]  # Только если есть email'ы
            ]
            
            if not tasks:
                console.print("[yellow]⚠️ Нет задач для выполнения[/yellow]")
                break

            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            # Обработка результатов
            for site_config_file, sent_count, error in results:
                site_name = Path(site_config_file).stem
                
                if error is not None:
                    if isinstance(error, InvalidSiteError):
                        bad_sites.add(site_name)
                        move_account_to_bad(site_config_file, BAD_SITES_DIR)
                    continue
                
                # Обновляем трекер
                site_sent[site_name] += sent_count
                
                # Сохраняем статистику после каждой итерации
                stats_manager.save_stats(
                    site_name,
                    site_sent[site_name],
                    EMAILS_PER_SITE,
                    site_sent[site_name] >= EMAILS_PER_SITE
                )
            
            console.print(f"\n[bold]📊 Итерация {iteration} завершена[/bold]")
            
            # Пауза перед следующей итерацией
            await asyncio.sleep(3)

        # Сохраняем статистику и перемещаем сайты
        console.print(f"\n[bold green]{'='*60}[/bold green]")
        console.print("[bold green]🎉 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ[/bold green]")
        console.print(f"[bold green]{'='*60}[/bold green]\n")
        
        for sf in site_files:
            site_name = Path(sf).stem
            site_filename = Path(sf).name
            sent = site_sent[site_name]
            
            if site_name in bad_sites:
                console.print(f"[red]❌ [{site_filename}]: невалиден[/red]")
            else:
                console.print(f"[green]✅ [{site_filename}]: {sent}/{EMAILS_PER_SITE} форм[/green]")
                
                # Перемещаем в spammed, если достиг цели
                if sent >= EMAILS_PER_SITE:
                    move_account_to_spammed(sf, SPAMMED_DIR)

        console.print(f"\n[bold green]{'='*60}[/bold green]")
        console.print("[bold green]✅ ВСЕ САЙТЫ ОБРАБОТАНЫ[/bold green]")
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
        logging.info("Carrd Spammer finished")
