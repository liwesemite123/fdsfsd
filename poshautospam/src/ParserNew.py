import asyncio
import aiohttp
import bs4
from bs4 import Tag
import random
import os
import ssl 
import certifi

from typing import Optional, List, Dict, Any
from loguru import logger
from src.Utils import load_proxy
from src.Config import categories_list

class TargetReachedException(Exception):
    """Кастомное исключение при достижении целевого количества товаров"""

    def __init__(self, items_count: int, target_count: int):
        self.items_count = items_count
        self.target_count = target_count
        super().__init__(
            f"Достигнуто целевое количество товаров: {items_count}/{target_count}"
        )


class LocalDBManager:
    """Класс для управления локальной базой данных пользователей"""

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self.db_dir = os.path.join(os.path.dirname(__file__), "db")
        self.db_file = os.path.join(self.db_dir, f"{telegram_id}.txt")
        self._ensure_db_file()

    def _ensure_db_file(self):
        """Создает файл БД если он не существует"""
        os.makedirs(self.db_dir, exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8'):
                pass

    def is_user_parsed(self, user_id: str) -> bool:
        """Проверяет, был ли уже спарсен данный user_id"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return user_id.strip() in [line.strip() for line in f.readlines()]
        except Exception:
            return False

    def add_user(self, user_id: str) -> bool:
        """Добавляет user_id в БД если его еще нет. Возвращает True если добавлен"""
        user_id = user_id.strip()
        if not user_id or self.is_user_parsed(user_id):
            return False

        try:
            with open(self.db_file, 'a', encoding='utf-8') as f:
                f.write(f"{user_id}\n")
            return True
        except Exception as e:
            logger.error(f"Ошибка записи в БД {self.telegram_id}: {e}")
            return False

    def get_count(self) -> int:
        """Возвращает количество спарсенных пользователей"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return len([line.strip() for line in f.readlines() if line.strip()])
        except Exception:
            return 0

    def clear_db(self) -> bool:
        """Очищает базу данных"""
        try:
            with open(self.db_file, 'w', encoding='utf-8'):
                pass
            return True
        except Exception as e:
            logger.error(f"Ошибка очистки БД {self.telegram_id}: {e}")
            return False


class Listing:
    _poshmark = 'https://poshmark.com'

    def __init__(self, html: str):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        ids = soup.find('div', {'data-et-prop-location': 'listing_tile'})
        self.user_id = ids.attrs.get('data-et-prop-lister_id') if isinstance(ids, Tag) else None
        self.item_id = ids.attrs.get('data-et-prop-listing_id') if isinstance(ids, Tag) else None
        a_tag = soup.find('a', href=True)
        self.item_slug = a_tag.get('href') if isinstance(a_tag, Tag) else None
        username_tag = soup.find('span', {'class': 'm--l--1 tc--g'})
        self.username = username_tag.text.strip() if isinstance(username_tag, Tag) and hasattr(username_tag, 'text') else None
        title_tag = soup.find('a', {'class': 'tile__title tc--b'})
        self.title = title_tag.get_text(strip=True) if isinstance(title_tag, Tag) else None
        self.sold = None
        self.email = None

    async def scrapItem(self, session: aiohttp.ClientSession, proxy: Optional[str]) -> bool:
        """Скрапит информацию о товаре"""
        if not self.item_slug:
            return False
        url = f"{self._poshmark}{self.item_slug}"

        try:
            async with session.get(url, proxy=proxy) as resp:
                if resp.status != 200:
                    logger.warning(f'Bad status code: {resp.status}')
                    return False

                html = await resp.text()
                soup = bs4.BeautifulSoup(html, 'lxml')
                stats = soup.find('div', {'class': 'seller-details__stats'})
                if not isinstance(stats, Tag):
                    logger.warning('No stats')
                    return False

                stats_divs = stats.find_all('div')
                if len(stats_divs) < 2:
                    return False

                sold = stats_divs[1]
                value = sold.find('h4') if isinstance(sold, Tag) else None
                if value is None:
                    return False

                self.sold = value.text.strip() if hasattr(value, 'text') else None
                return True

        except asyncio.TimeoutError:
            logger.error(f'Timeout error for {url}')
            return False
        except Exception:
            pass

    async def validate(self) -> bool:
        """Валидирует данные товара"""
        if not self.sold or '--' not in self.sold:
            return False
        return True

    async def getData(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'user_id': self.user_id,
            'item_slug': self.item_slug,
            'username': self.username,
            'item_url': f'https://poshmark.com{self.item_slug}',
            'item_title': self.title,
            'email': self.username + '@gmail.com' if self.username else None
        }


class AsyncPoshmarkParser:
    """Асинхронный парсер Poshmark с контролем количества товаров"""

    _past_pages = 100
    _first_pages = 2
    _poshmark = 'https://poshmark.com'
    _filters = '?sort_by=added_desc'
    _page = '&max_id='

    def __init__(
        self,
        target_items_count: int,
        telegram_id: int = 123456789,
        max_concurrent_requests: int = 150
    ):
        """
        Инициализация парсера

        Args:
            target_items_count: Целевое количество товаров для парсинга
            telegram_id: ID телеграм пользователя для БД
            max_concurrent_requests: Максимальное количество одновременных запросов
        """
        self.itemClass: List[Dict[str, Any]] = []
        self.parsed_users: List[str] = []
        self.proxy_pool = list(load_proxy())
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._categories = categories_list
        self.telegram_id = telegram_id
        self.target_items_count = target_items_count
        self.db_manager = LocalDBManager(telegram_id)
        self._stop_parsing = False
        self._lock = asyncio.Lock()  # Защита от race condition

        logger.info(
            f"Инициализирован парсер для telegram_id={telegram_id}, "
            f"target={target_items_count}, categories={len(categories_list)}"
        )

    def get_random_proxy(self) -> Optional[str]:
        """Возвращает случайный прокси из пула"""
        if not self.proxy_pool:
            return None
        proxy = random.choice(self.proxy_pool)
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        return proxy

    async def _check_target_reached(self) -> None:
        """Проверяет достижение целевого количества товаров (потокобезопасно)"""
        async with self._lock:
            if len(self.itemClass) >= self.target_items_count:
                self._stop_parsing = True
                raise TargetReachedException(
                    items_count=len(self.itemClass),
                    target_count=self.target_items_count
                )

    async def _parseListing(self, html: str, session: aiohttp.ClientSession) -> None:
        """Парсит отдельный листинг"""
        # Немедленная проверка на остановку
        if self._stop_parsing:
            return

        try:
            user = Listing(html)
            data = await user.getData()

            if not data['username'] or data['username'] in self.parsed_users:
                return

            # Проверяем дубли в локальной БД
            if not data['user_id'] or self.db_manager.is_user_parsed(data['user_id']):
                return

            if self._stop_parsing:
                return

            self.parsed_users.append(data['username'])
            proxy = self.get_random_proxy()

            async with self.semaphore:
                if self._stop_parsing:
                    return

                if not await user.scrapItem(session, proxy):
                    return

            if self._stop_parsing:
                return

            if not await user.validate():
                return

            if self._stop_parsing:
                return

            # Добавляем в БД и список (потокобезопасно)
            async with self._lock:
                if self._stop_parsing:
                    return

                # Финальная проверка перед добавлением
                if len(self.itemClass) >= self.target_items_count:
                    return

                if self.db_manager.add_user(data['user_id']):
                    self.itemClass.append(data)
                    logger.success(f"Найдено обьявление #{len(self.itemClass)}: {data['item_title']} | Email: {data['email']}")

                    # Проверяем цель после добавления
                    if len(self.itemClass) >= self.target_items_count:
                        self._stop_parsing = True
                        raise TargetReachedException(
                            items_count=len(self.itemClass),
                            target_count=self.target_items_count
                        )
                else:
                    logger.warning(f"User ID {data['user_id']} уже был спарсен ранее")

        except TargetReachedException:
            raise
        except asyncio.CancelledError:
            # Задача отменена - выходим немедленно
            return

    async def _categoryEntry(self, _url: str, _p: int, session: aiohttp.ClientSession) -> None:
        """Обрабатывает страницу категории"""
        if self._stop_parsing:
            return

        url = f"{self._poshmark}{_url}{self._filters}{self._page}{str(_p)}"
        proxy = self.get_random_proxy()

        try:
            async with self.semaphore:
                if self._stop_parsing:
                    return

                timeout = aiohttp.ClientTimeout(total=15)
                async with session.get(url, proxy=proxy, timeout=timeout) as resp:
                    if resp.status != 200:
                        logger.warning(f'Bad request {resp.status} for {url}')
                        return

                    if self._stop_parsing:
                        return

                    html = await resp.text()
                    # lxml быстрее html.parser для uvloop
                    soup = bs4.BeautifulSoup(html, 'lxml')
                    items = soup.find_all('div', {'data-et-prop-location': 'listing_tile'})

                    if not items or self._stop_parsing:
                        return

                    tasks = [self._parseListing(str(item), session) for item in items]
                    # НЕ используем return_exceptions, чтобы TargetReachedException прервал все
                    await asyncio.gather(*tasks)

        except asyncio.TimeoutError:
            logger.error(f'Timeout for {url}')
        except asyncio.CancelledError:
            return
        except TargetReachedException:
            self._stop_parsing = True
            raise
        except Exception as e:
            if not self._stop_parsing:
                logger.error(f'Error in category entry: {e}')

    async def _firstCategories(self, session: aiohttp.ClientSession) -> None:
        """Парсит первые страницы категорий в цикле"""
        try:
            while not self._stop_parsing:
                for i in range(1, self._first_pages + 1):
                    if self._stop_parsing:
                        return

                    tasks = [
                        self._categoryEntry(c, i, session)
                        for c in self._categories
                    ]
                    await asyncio.gather(*tasks)

                if self._stop_parsing:
                    return

                logger.info(
                    f'Первые страницы обработаны. '
                    f'Собрано товаров: {len(self.itemClass)}/{self.target_items_count}'
                )

                # Добавляем небольшую задержку между циклами
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            return
        except TargetReachedException:
            return

    async def _pastCategories(self, session: aiohttp.ClientSession) -> None:
        """Парсит старые страницы категорий"""
        try:
            for i in range(self._first_pages + 1, self._past_pages + 1):
                if self._stop_parsing:
                    return

                tasks = [
                    self._categoryEntry(c, i, session)
                    for c in self._categories
                ]
                await asyncio.gather(*tasks)

                if self._stop_parsing:
                    return

                # Небольшая задержка между страницами
                await asyncio.sleep(1)

                if i % 10 == 0:
                    logger.info(
                        f'Обработана страница {i}/{self._past_pages}. '
                        f'Собрано: {len(self.itemClass)}/{self.target_items_count}'
                    )

        except asyncio.CancelledError:
            logger.info("_pastCategories отменена")
            return
        except TargetReachedException:
            logger.success(f"Целевое количество достигнуто в _pastCategories")
            return

    async def Start(self) -> List[Dict[str, Any]]:
        """
        Запускает парсинг

        Returns:
            Список спарсенных товаров

        Raises:
            TargetReachedException: При достижении целевого количества товаров
        """
        logger.info(
            f"Начало парсинга. Цель: {self.target_items_count} товаров, "
            f"категорий: {len(self._categories)}, прокси: {len(self.proxy_pool)}"
        )

        first_task = None
        past_task = None

        try:
            # Оптимизированные настройки для uvloop
            connector = aiohttp.TCPConnector(
                limit=200,
                limit_per_host=50,
                ttl_dns_cache=300,
                enable_cleanup_closed=True,
                ssl=ssl.create_default_context(cafile=certifi.where())

            )

            timeout = aiohttp.ClientTimeout(total=30)

            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
            ) as session:
                # Создаем задачи
                first_task = asyncio.create_task(self._firstCategories(session))
                past_task = asyncio.create_task(self._pastCategories(session))

                # Ждем завершения
                await asyncio.gather(first_task, past_task)

        except TargetReachedException as e:
            logger.success(str(e))
            # ЖЕСТКО отменяем все оставшиеся задачи
            if first_task and not first_task.done():
                first_task.cancel()
            if past_task and not past_task.done():
                past_task.cancel()

            # Ждем отмены
            if first_task:
                try:
                    await first_task
                except asyncio.CancelledError:
                    pass
            if past_task:
                try:
                    await past_task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logger.error(f"Критическая ошибка парсинга: {e}")
            # Отменяем задачи при любой ошибке
            if first_task and not first_task.done():
                first_task.cancel()
            if past_task and not past_task.done():
                past_task.cancel()
        finally:
            logger.info(
                f"Парсинг завершен. Собрано товаров: {len(self.itemClass)}/{self.target_items_count}"
            )

        return self.itemClass

    def stop(self) -> None:
        """Останавливает парсинг"""
        logger.warning("Получен сигнал остановки парсинга")
        self._stop_parsing = True


# async def main():

#     parser = AsyncPoshmarkParser(
#         target_items_count=20,
#     )

#     try:
#         items = await parser.Start()
#         logger.info(f"Парсинг завершен успешно. Получено {len(items)} товаров")
        
#         for item in items:
#             print(item['email'])

#     except Exception as e:
#         logger.error(f"Ошибка в main: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())
