"""
Carrd Client для отправки сообщений через контактные формы Carrd сайтов.

Этот модуль позволяет автоматизировать отправку сообщений через контактные формы
на сайтах, созданных с помощью Carrd.co.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

from curl_cffi.requests import AsyncSession
from dotenv import load_dotenv

from src.progress import console

load_dotenv()


class CarrdClient:
    """Клиент для отправки сообщений через Carrd контактные формы."""
    
    def __init__(self, site_config_file: str, site_name: str):
        """
        Инициализация клиента Carrd.
        
        Args:
            site_config_file: Путь к JSON файлу с конфигурацией сайта Carrd
            site_name: Имя конфигурации сайта (для логов)
        """
        self.site_config_file = site_config_file
        self.site_name = site_name
        self.session = AsyncSession(impersonate="chrome120")
        
        # Загружаем конфигурацию сайта
        self.config = self._load_site_config()
        
        # Базовые параметры
        self.site_url = self.config.get("site_url")
        self.form_action = self.config.get("form_action")
        self.form_fields = self.config.get("form_fields", {})
        
        # Настройки из .env
        self.proxy = os.getenv("MAIN_PROXY")
        self.send_timeout = int(os.getenv("SEND_TIMEOUT", "15"))
        self.name = os.getenv("NAME", "Customer")
        self.surname = os.getenv("SURNAME", "Support")
        
        # Заголовки для имитации браузера
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.site_url,
            "Referer": f"{self.site_url}/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    
    def _load_site_config(self) -> dict:
        """
        Загружает конфигурацию Carrd сайта из JSON файла.
        
        Returns:
            dict: Конфигурация сайта
        """
        try:
            with open(self.site_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.info(f"✅ Загружена конфигурация для сайта: {self.site_name}")
                return config
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки конфигурации {self.site_name}: {e}")
            raise
    
    def _get_cache_path(self) -> str:
        """Получает путь к файлу кеша для этого сайта."""
        site_basename = Path(self.site_config_file).stem
        cache_dir = os.path.join(os.path.dirname(__file__), 'db', 'carrd_cache')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{site_basename}.json")
    
    def _load_cache(self) -> Optional[dict]:
        """Загружает кеш для сайта."""
        cache_path = self._get_cache_path()
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logging.info(f"✅ Загружен кеш для сайта: {self.site_name}")
                return cache_data
        except Exception as e:
            logging.warning(f"⚠️ Ошибка загрузки кеша: {e}")
            return None
    
    def _save_cache(self, data: dict) -> bool:
        """Сохраняет кеш для сайта."""
        cache_path = self._get_cache_path()
        
        try:
            cache_data = {
                "last_submission": int(time.time()),
                "total_submissions": data.get("total_submissions", 0),
                "site_url": self.site_url
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"💾 Кеш сохранен для сайта: {self.site_name}")
            return True
        except Exception as e:
            logging.warning(f"⚠️ Ошибка сохранения кеша: {e}")
            return False
    
    async def submit_form(
        self,
        email: str,
        message: str,
        name: Optional[str] = None
    ) -> bool:
        """
        Отправляет контактную форму на Carrd сайт.
        
        Args:
            email: Email адрес получателя
            message: Текст сообщения
            name: Имя отправителя (опционально)
            
        Returns:
            bool: True если отправка успешна, False иначе
        """
        # Формируем данные формы
        form_data = {}
        
        # Заполняем стандартные поля
        if "email_field" in self.form_fields:
            form_data[self.form_fields["email_field"]] = email
        
        if "message_field" in self.form_fields:
            form_data[self.form_fields["message_field"]] = message
        
        if "name_field" in self.form_fields:
            form_data[self.form_fields["name_field"]] = name or f"{self.name} {self.surname}"
        
        # Добавляем дополнительные поля из конфигурации
        if "additional_fields" in self.form_fields:
            form_data.update(self.form_fields["additional_fields"])
        
        # Отправляем форму
        for attempt in range(3):
            try:
                response = await self.session.post(
                    self.form_action,
                    headers=self.headers,
                    data=form_data,
                    proxy=self.proxy,
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code in [200, 302, 303]:
                    logging.info(f"✅ Форма успешно отправлена на {email}")
                    return True
                else:
                    logging.warning(f"⚠️ Неожиданный статус {response.status_code} для {email}")
                    if attempt < 2:
                        await asyncio.sleep(2)
                        continue
                    return False
                    
            except asyncio.TimeoutError:
                logging.error(f"❌ Таймаут при отправке формы на {email}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                return False
            except Exception as e:
                logging.exception(f"❌ Ошибка отправки формы на {email}: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                return False
        
        return False
    
    async def execute_solo_conversation(
        self,
        email_list: list,
        message: str,
        email_to_link: Optional[dict[str, str]] = None,
        force_refresh: bool = False
    ) -> dict | bool:
        """
        Отправка сообщений списку email через Carrd формы.
        
        Args:
            email_list: Список email адресов
            message: Шаблон сообщения (может содержать {LINK})
            email_to_link: Словарь {email: generated_link} для подстановки персональных ссылок
            force_refresh: Принудительное обновление кеша (не используется для Carrd)
            
        Returns:
            dict: Результаты отправки или False при ошибке
        """
        logging.info(f"\n📧 Обрабатываем {len(email_list)} email-адресов через Carrd...")
        console.print(f"[bold cyan]📧 Отправка через Carrd: {len(email_list)} форм[/bold cyan]")
        
        results = []
        successful_count = 0
        
        for i, email in enumerate(email_list, 1):
            logging.info(f"\n[{i}/{len(email_list)}] Обработка {email}...")
            console.print(f"\n[bold white][{i}/{len(email_list)}][/bold white] [cyan]Обработка {email}...[/cyan]")
            
            # Подставляем персональную ссылку для этого email
            personalized_message = message
            if email_to_link and email in email_to_link:
                personalized_link = email_to_link[email]
                personalized_message = message.replace("{LINK}", personalized_link)
                logging.info(f"[{self.site_name}] 🔗 Используем персональную ссылку: {personalized_link}")
            else:
                # Если нет персональной ссылки, убираем плейсхолдер
                if "{LINK}" in personalized_message:
                    logging.warning(f"[{self.site_name}] ⚠️ Нет персональной ссылки для {email}")
                    personalized_message = personalized_message.replace("{LINK}", "")
            
            # Отправляем форму
            send_result = await self.submit_form(
                email=email,
                message=personalized_message,
                name=f"{self.name} {self.surname}"
            )
            
            if send_result:
                successful_count += 1
                logging.info(f"[{self.site_name}] ✅ Форма отправлена на {email}")
                
                # Выводим информацию об отправленной ссылке
                if email_to_link and email in email_to_link:
                    sent_link = email_to_link[email]
                    console.print(f"[bold green]  ✅ Форма отправлена на {email}[/bold green]")
                    console.print(f"[green]  🔗 Ссылка: {sent_link}[/green]")
                else:
                    console.print(f"[bold green]  ✅ Форма отправлена на {email}[/bold green]")
                
                results.append({
                    "email": email,
                    "success": True,
                    "method": "carrd_form"
                })
            else:
                logging.error(f"[{self.site_name}] ❌ Не удалось отправить форму на {email}")
                console.print(f"[red]  ❌ Ошибка отправки на {email}[/red]")
                
                results.append({
                    "email": email,
                    "success": False,
                    "error": "Failed to submit form"
                })
            
            # Пауза между отправками
            if i < len(email_list):
                logging.info(f"[{self.site_name}] ⏸️  Пауза {self.send_timeout} секунды...")
                console.print(f"[yellow]  ⏸️  Пауза {self.send_timeout} сек...[/yellow]")
                await asyncio.sleep(self.send_timeout)
        
        failed_count = len(results) - successful_count
        
        # Сохраняем статистику
        cache_data = self._load_cache() or {}
        total_submissions = cache_data.get("total_submissions", 0) + successful_count
        self._save_cache({"total_submissions": total_submissions})
        
        return {
            "total": len(email_list),
            "successful": successful_count,
            "failed": failed_count,
            "results": results,
            "message": message,
            "site_url": self.site_url,
            "site_name": self.site_name
        }
    
    async def close(self):
        """Закрывает сессию."""
        if self.session:
            await self.session.close()
