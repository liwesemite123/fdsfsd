import asyncio
import aiohttp
import random
import ssl
import certifi
from typing import Optional, List, Dict, Any
from loguru import logger
from bs4 import BeautifulSoup
import json
import re
from .LeboncoinConfig import LEBONCOIN_CATEGORIES


class LeboncoinParser:
    """
    Парсер для сайта leboncoin.fr
    
    Особенности:
    - Поддержка прокси с ротацией
    - Выбор категорий для парсинга
    - Извлечение данных продавца (количество продаж, отзывы и т.д.)
    """

    # Категории leboncoin (используем из конфига)

    def __init__(
        self,
        categories: Optional[List[str]] = None,
        proxy_list: Optional[List[str]] = None,
        max_listings: int = 100,
        max_concurrent: int = 10,
    ):
        """
        Инициализация парсера
        
        Args:
            categories: Список категорий для парсинга (если None - все категории)
            proxy_list: Список прокси для ротации
            max_listings: Максимальное количество объявлений для парсинга
            max_concurrent: Максимальное количество одновременных запросов
        """
        self.base_url = "https://www.leboncoin.fr"
        self.api_url = "https://api.leboncoin.fr/api"
        
        # Категории
        if categories:
            self.categories = [c for c in categories if c in LEBONCOIN_CATEGORIES]
        else:
            self.categories = list(LEBONCOIN_CATEGORIES.keys())
        
        # Прокси
        self.proxy_list = proxy_list or []
        
        # Настройки парсинга
        self.max_listings = max_listings
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Результаты
        self.listings = []
        self._lock = asyncio.Lock()
        self._stop_parsing = False
        
        logger.info(
            f"Инициализация Leboncoin парсера: "
            f"категорий={len(self.categories)}, "
            f"прокси={len(self.proxy_list)}, "
            f"лимит={max_listings}"
        )

    def _get_random_proxy(self) -> Optional[str]:
        """Получить случайный прокси из списка"""
        if not self.proxy_list:
            return None
        
        proxy = random.choice(self.proxy_list)
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        return proxy

    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запросов"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def _fetch_page(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        retries: int = 3
    ) -> Optional[str]:
        """
        Получить HTML страницы с повторными попытками
        
        Args:
            session: Сессия aiohttp
            url: URL для запроса
            retries: Количество повторных попыток
            
        Returns:
            HTML контент или None при ошибке
        """
        for attempt in range(retries):
            try:
                proxy = self._get_random_proxy()
                
                async with self.semaphore:
                    async with session.get(
                        url,
                        headers=self._get_headers(),
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=30),
                        ssl=ssl.create_default_context(cafile=certifi.where())
                    ) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:
                            # Rate limit - подождем и повторим
                            logger.warning(f"Rate limit для {url}, ожидание...")
                            await asyncio.sleep(5 * (attempt + 1))
                        else:
                            logger.warning(f"Статус {response.status} для {url}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout для {url} (попытка {attempt + 1}/{retries})")
            except Exception as e:
                logger.error(f"Ошибка при запросе {url}: {e}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2 * (attempt + 1))
        
        return None

    async def _parse_seller_info(
        self, 
        session: aiohttp.ClientSession,
        seller_id: str
    ) -> Dict[str, Any]:
        """
        Парсинг информации о продавце
        
        Args:
            session: Сессия aiohttp
            seller_id: ID продавца
            
        Returns:
            Словарь с данными продавца
        """
        seller_info = {
            'seller_id': seller_id,
            'seller_name': None,
            'seller_type': None,  # 'pro' или 'particulier'
            'sales_count': 0,
            'reviews_count': 0,
            'average_rating': 0.0,
            'registration_date': None,
            'response_rate': None,
            'response_time': None,
        }
        
        try:
            # Попытка получить данные через API (может потребоваться авторизация)
            # Здесь используем базовый парсинг страницы продавца
            seller_url = f"{self.base_url}/profil/{seller_id}"
            html = await self._fetch_page(session, seller_url)
            
            if not html:
                return seller_info
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Имя продавца
            name_elem = soup.find('h1', {'data-qa-id': 'adview_seller_name'})
            if name_elem:
                seller_info['seller_name'] = name_elem.text.strip()
            
            # Тип продавца
            type_elem = soup.find('div', {'data-qa-id': 'seller_type'})
            if type_elem:
                seller_info['seller_type'] = 'pro' if 'professionnel' in type_elem.text.lower() else 'particulier'
            
            # Количество объявлений (как прокси для продаж)
            ads_count = soup.find('span', text=re.compile(r'annonces?', re.I))
            if ads_count:
                numbers = re.findall(r'\d+', ads_count.text)
                if numbers:
                    seller_info['sales_count'] = int(numbers[0])
            
            # Рейтинг и отзывы
            rating_elem = soup.find('div', {'data-qa-id': 'seller_rating'})
            if rating_elem:
                rating_text = rating_elem.text
                # Парсим рейтинг (например "4.5/5")
                rating_match = re.search(r'(\d+\.?\d*)/5', rating_text)
                if rating_match:
                    seller_info['average_rating'] = float(rating_match.group(1))
                
                # Парсим количество отзывов
                reviews_match = re.search(r'(\d+)\s+avis', rating_text)
                if reviews_match:
                    seller_info['reviews_count'] = int(reviews_match.group(1))
            
            # Дата регистрации
            reg_date = soup.find('div', text=re.compile(r'Membre depuis', re.I))
            if reg_date:
                seller_info['registration_date'] = reg_date.text.strip()
            
            # Время ответа
            response_time = soup.find('div', text=re.compile(r'R[ée]pond en', re.I))
            if response_time:
                seller_info['response_time'] = response_time.text.strip()
                
        except Exception as e:
            logger.error(f"Ошибка при парсинге продавца {seller_id}: {e}")
        
        return seller_info

    async def _parse_listing(
        self,
        session: aiohttp.ClientSession,
        listing_elem: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Парсинг одного объявления
        
        Args:
            session: Сессия aiohttp
            listing_elem: Элемент BeautifulSoup с объявлением
            
        Returns:
            Словарь с данными объявления или None
        """
        if self._stop_parsing:
            return None
        
        try:
            # Извлекаем базовую информацию из списка
            listing_data = {
                'title': None,
                'price': None,
                'location': None,
                'category': None,
                'url': None,
                'listing_id': None,
                'image_url': None,
                'date_posted': None,
                'seller_info': None,
            }
            
            # URL объявления
            link = listing_elem.find('a', href=True)
            if link:
                listing_data['url'] = link['href']
                if not listing_data['url'].startswith('http'):
                    listing_data['url'] = self.base_url + listing_data['url']
                
                # ID из URL
                id_match = re.search(r'/(\d+)\.htm', listing_data['url'])
                if id_match:
                    listing_data['listing_id'] = id_match.group(1)
            
            # Название
            title_elem = listing_elem.find('p', {'data-qa-id': 'aditem_title'})
            if title_elem:
                listing_data['title'] = title_elem.text.strip()
            
            # Цена
            price_elem = listing_elem.find('span', {'data-qa-id': 'aditem_price'})
            if price_elem:
                price_text = price_elem.text.strip()
                # Убираем символы валюты и пробелы
                price_text = re.sub(r'[^\d]', '', price_text)
                if price_text:
                    listing_data['price'] = int(price_text)
            
            # Локация
            location_elem = listing_elem.find('p', {'data-qa-id': 'aditem_location'})
            if location_elem:
                listing_data['location'] = location_elem.text.strip()
            
            # Категория
            category_elem = listing_elem.find('p', {'data-qa-id': 'aditem_category'})
            if category_elem:
                listing_data['category'] = category_elem.text.strip()
            
            # Изображение
            img_elem = listing_elem.find('img', src=True)
            if img_elem:
                listing_data['image_url'] = img_elem['src']
            
            # Дата публикации
            date_elem = listing_elem.find('p', {'data-qa-id': 'aditem_date'})
            if date_elem:
                listing_data['date_posted'] = date_elem.text.strip()
            
            # Получаем детальную информацию о продавце
            if listing_data['url']:
                detail_html = await self._fetch_page(session, listing_data['url'])
                if detail_html:
                    detail_soup = BeautifulSoup(detail_html, 'lxml')
                    
                    # Ищем ID продавца
                    seller_link = detail_soup.find('a', href=re.compile(r'/profil/'))
                    if seller_link:
                        seller_id_match = re.search(r'/profil/(\w+)', seller_link['href'])
                        if seller_id_match:
                            seller_id = seller_id_match.group(1)
                            listing_data['seller_info'] = await self._parse_seller_info(
                                session, seller_id
                            )
            
            # Проверяем, что получили минимум данных
            if listing_data['title'] and listing_data['listing_id']:
                return listing_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге объявления: {e}")
        
        return None

    async def _parse_category(
        self,
        session: aiohttp.ClientSession,
        category: str,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Парсинг страницы категории
        
        Args:
            session: Сессия aiohttp
            category: Название категории
            page: Номер страницы
            
        Returns:
            Список объявлений
        """
        if self._stop_parsing:
            return []
        
        results = []
        
        try:
            # Формируем URL категории
            url = f"{self.base_url}/recherche?category={category}&page={page}"
            
            html = await self._fetch_page(session, url)
            if not html:
                return results
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Ищем контейнеры с объявлениями
            # Структура может отличаться, нужно адаптировать под актуальную
            listing_elems = soup.find_all('a', {'data-qa-id': re.compile('aditem')})
            
            if not listing_elems:
                # Альтернативный поиск
                listing_elems = soup.find_all('li', {'data-qa-id': 'aditem_container'})
            
            logger.info(
                f"Категория {category}, страница {page}: "
                f"найдено {len(listing_elems)} объявлений"
            )
            
            # Парсим каждое объявление
            for listing_elem in listing_elems:
                if self._stop_parsing:
                    break
                
                async with self._lock:
                    if len(self.listings) >= self.max_listings:
                        self._stop_parsing = True
                        break
                
                listing_data = await self._parse_listing(session, listing_elem)
                
                if listing_data:
                    async with self._lock:
                        if len(self.listings) < self.max_listings:
                            self.listings.append(listing_data)
                            logger.success(
                                f"Объявление #{len(self.listings)}: "
                                f"{listing_data['title']} | "
                                f"Продавец: {listing_data.get('seller_info', {}).get('seller_name', 'N/A')}"
                            )
                
                # Небольшая задержка между объявлениями
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Ошибка при парсинге категории {category}: {e}")
        
        return results

    async def start_parsing(self) -> List[Dict[str, Any]]:
        """
        Запуск парсинга
        
        Returns:
            Список спарсенных объявлений
        """
        logger.info("Начало парсинга leboncoin.fr")
        
        try:
            # Создаем SSL контекст
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            # Настройки подключения
            connector = aiohttp.TCPConnector(
                limit=50,
                limit_per_host=10,
                ttl_dns_cache=300,
                ssl=ssl_context,
            )
            
            timeout = aiohttp.ClientTimeout(total=60)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
            ) as session:
                # Парсим каждую категорию
                for category in self.categories:
                    if self._stop_parsing:
                        break
                    
                    logger.info(f"Парсинг категории: {category} ({self.CATEGORIES[category]})")
                    
                    # Парсим первые несколько страниц каждой категории
                    for page in range(1, 6):  # 5 страниц
                        if self._stop_parsing:
                            break
                        
                        await self._parse_category(session, category, page)
                        
                        # Задержка между страницами
                        await asyncio.sleep(2)
                    
                    # Задержка между категориями
                    await asyncio.sleep(3)
                    
        except Exception as e:
            logger.error(f"Критическая ошибка парсинга: {e}")
        finally:
            logger.info(
                f"Парсинг завершен. Собрано объявлений: {len(self.listings)}/{self.max_listings}"
            )
        
        return self.listings

    def get_results(self) -> List[Dict[str, Any]]:
        """Получить результаты парсинга"""
        return self.listings

    def save_results(self, filename: str = 'leboncoin_results.json'):
        """
        Сохранить результаты в JSON файл
        
        Args:
            filename: Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.listings, f, ensure_ascii=False, indent=2)
            logger.success(f"Результаты сохранены в {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении результатов: {e}")
