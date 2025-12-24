import asyncio
import json
import logging
import math
import os
import time
from urllib.parse import urlencode

from dotenv import load_dotenv
from curl_cffi.requests import AsyncSession

from src.progress import console
from src.Utils import encode_md5

load_dotenv()

class GoDaddyClient:
    def __init__(self, account_cookies, account_name: str):
        self.account_name = account_cookies
        self.acc_name = account_name
        self.session = AsyncSession(impersonate="safari")
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://conversations.godaddy.com",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }
        self.access_token = self._init_access_token()
        self.proxy = os.getenv("MAIN_PROXY")
        self.name = os.getenv("NAME", "Orders")
        self.surname = os.getenv("SURNAME", "Soldout")
        self.send_timeout = int(os.getenv("SEND_TIMEOUT", "15"))
        self.main_domain = None
        self.product_id = None
        self.staff_id = None
        self.conversation_id = None
        self.conversation_token = None

    def _init_access_token(self):
        with open(self.account_name, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            for cookie in cookies:
                if cookie['name'] == 'auth_idp':
                    self.access_token = cookie['value']
                    self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])

                    return self.access_token
    
    def _get_cache_path(self) -> str:
        account_basename = os.path.basename(self.account_name).replace('.json', '')
        cache_dir = os.path.join(os.path.dirname(__file__), 'db', 'accounts_data')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{account_basename}.json")
    
    def _load_cache(self) -> dict | None:
        cache_path = self._get_cache_path()
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logging.info(f"✅ Загружен кеш для аккаунта: {os.path.basename(self.account_name)}")
                console.print(f"[green]✅ Загружен кеш для аккаунта: {os.path.basename(self.account_name)}[/green]")
                return cache_data
        except Exception as e:
            logging.warning(f"⚠️ Ошибка загрузки кеша: {e}")
            return None
    
    def _save_cache(self, data: dict) -> bool:
        cache_path = self._get_cache_path()
        
        try:
            cache_data = {
                "main_domain": data.get("main_domain"),
                "product_id": data.get("product_id"),
                "staff_id": data.get("staff_id"),
                "cached_at": int(time.time())
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"💾 Кеш сохранен для аккаунта: {os.path.basename(self.account_name)}")
            console.print(f"[cyan]💾 Кеш сохранен для аккаунта: {os.path.basename(self.account_name)}[/cyan]")
            return True
        except Exception as e:
            logging.warning(f"⚠️ Ошибка сохранения кеша: {e}")
            return False
    
    def _is_cache_valid(self, cache_data: dict, max_age_hours: int = 24) -> bool:
        if not cache_data or 'cached_at' not in cache_data:
            return False
        
        cache_age = time.time() - cache_data['cached_at']
        max_age_seconds = max_age_hours * 3600
        
        is_valid = cache_age < max_age_seconds
        if not is_valid:
            logging.warning(f"⚠️ Кеш устарел (возраст: {cache_age / 3600:.1f}ч)")
        
        return is_valid
    
    async def refresh_token(self):
        url = "https://sso.godaddy.com/v1/api/token/ui_heartbeat"
        js = {
            "infotoken": "true",
            "realm": "idp",
            "calling_host": "conversations.godaddy.com",
        }
        for _ in range(3):
            try:
                r = await self.session.post(url, headers=self.headers, json=js, proxy=self.proxy)
                if r.status_code == 201:
                    self.access_token = self.session.cookies.get("auth_idp")
                    return True
                else:
                    return False

            except Exception as e:
                if 'curl' in str(e):
                    await asyncio.sleep(1.25)
                    continue
                else:
                    raise str(e)
        return False

    async def get_website_mainurl(self):
        url = 'https://start.godaddy.com/api/onboarding-info/?itc=slp_wsb_ft_getstarted_plans_nocc&lid=wsb-vnext-freemat-3'
        h = self.headers.copy()
        h['Content-Type'] = 'application/json'
        js = {
            "appVersion": "39be241",
            "data": 
                {
                    "domainIntentEmailFirst":None,
                    "switcherGoal":None,
                    "socialType":"answerMoreQuestions",
                    "facebookPickerStatus":"noStatus"
                },
            "step": None,
            "isMobile":True
        }

        for _ in range(3):
            try:
                r = await self.session.post(url, headers=h, json=js, proxy=self.proxy)
                if r.status_code == 200:
                    self.main_domain = r.json().get('ventures', [{}])[-1].get('projects', [{}])[0].get('domain')
                    self.product_id = r.json().get('ventures', [{}])[-1].get('projects', [{}])[0].get('product', {}).get('id')
                    return True
                return False

            except Exception as e:
                if 'curl' in str(e):
                    await asyncio.sleep(1.25)
                    continue
                else:
                    raise str(e)
        return False

    async def get_staff_id(self):
        url = f'https://{self.product_id}.reamaze.godaddy.com/api/v2/staff/self'

        for _ in range(3):
            try:
                r = await self.session.get(url, headers=self.headers, proxy=self.proxy)
                if r.status_code == 200:
                    self.staff_id = r.json().get('staff').get('id')
                    return True
                else:
                    return False

            except Exception as e:
                if 'curl' in str(e):
                    await asyncio.sleep(1.25)
                    continue
                else:
                    raise str(e)
        return False

    async def change_email(self, email: str):
        url = f"https://{self.product_id}.reamaze.godaddy.com/api/v2/staff/{self.staff_id}"

        js = {
            "notification_email": email
        }

        for _ in range(3):
            try: 
                r = await self.session.put(url, headers=self.headers, json=js, proxy=self.proxy)
                # print(r.status_code)
                # print(r.json())
                if r.status_code == 200:
                    return True
                else:
                    return False

            except Exception as e:
                if 'curl' in str(e):
                    await asyncio.sleep(1.25)
                    continue
                else:
                    raise str(e)
        return False

    async def send_text(self, text: str):
        url = f'https://{self.product_id}.reamaze.io/data/conversations'
        preload = {
            'sso[id]': '',
            'sso[anon_id]': '',
            'sso[first_seen]': '2025-12-08T01:51:57.361Z',
            'sso[name]': f'{self.name} {self.surname}',
            'sso[avatar]': '',
            'sso[email]': '123123@gmail.com',
            'sso[authkey]': '',
            'sso[authpath]': f'/m/api/reamaze/v2/customers/auth?brand={self.product_id}',
            'sso[parent_url]': f'https://{self.main_domain}/',
            'sso[tz_offset]': '0',
            'sso[tz_name]': 'Europe/London'
        }
        TIME_GD = math.floor(time.time())
        params = urlencode(preload)

        h = self.headers.copy()
        h['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        h['Origin'] = f"https://{self.main_domain}"
        h['Referer'] = f"https://{self.main_domain}/"
        h['Accept'] = '*/*'


        data = {
            'category_id': 69468158,
            "_zt": encode_md5("0" + str(TIME_GD)),
            "_zt2": TIME_GD,
            '_url': f'https://{self.main_domain}/',
            '_browser': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            '_zc_field': '5b5cd0da3121fc53b4bc84d0c8af2e81',
            'sparams': str(params),
            '__skip_bots': 'false',
            'conversation[messages_attributes][0][body]': text
        }

        for _ in range(3):
            try:
                r = await self.session.post(url, headers=h, data=data, proxy=self.proxy)
                # print(r.status_code)
                if r.status_code == 200:
                    self.conversation_id = r.json().get('conversation').get('id')
                    self.conversation_token = r.json().get('conversation').get('token')
                    return True
                else:
                    return False

            except Exception as e:
                if 'curl' in str(e):
                    await asyncio.sleep(1.25)
                    continue
                else:
                    raise str(e)
        return False

    async def execute_solo_conversation(
        self,
        email_list: list,
        message: str,
        email_to_link: dict[str, str] | None = None,
        force_refresh: bool = False
    ) -> dict | bool:
        """
        Отправка сообщений списку email.
        
        Args:
            email_list: Список email адресов
            message: Шаблон сообщения (может содержать {LINK})
            email_to_link: Словарь {email: generated_link} для подстановки персональных ссылок
            force_refresh: Принудительное обновление кеша
        """
        token_refreshed = await self.refresh_token()
        if not token_refreshed:
            logging.error("❌ Не удалось обновить рефреш токен")
            return False
        
        cache_data = None
        if not force_refresh:
            cache_data = self._load_cache()
            if cache_data and self._is_cache_valid(cache_data):
                self.main_domain = cache_data.get("main_domain")
                self.product_id = cache_data.get("product_id")
                self.staff_id = cache_data.get("staff_id")
                logging.info("🚀 Используем кешированные данные аккаунта")
                console.print("[bold cyan]🚀 Используем кешированные данные аккаунта[/bold cyan]")
            else:
                cache_data = None
        
        if not cache_data:
            logging.info("🔄 Получаем свежие данные аккаунта...")
            console.print("[cyan]🔄 Получаем свежие данные аккаунта...[/cyan]")
            
            website_data = await self.get_website_mainurl()
            staff_data = await self.get_staff_id()
            
            if isinstance(website_data, Exception) or not website_data:
                logging.error(f"❌ Не удалось получить данные с нашего вебсайта: {website_data if isinstance(website_data, Exception) else 'Unknown error'}")
                return False
            
            if isinstance(staff_data, Exception) or not staff_data:
                logging.error(f"❌ Не удалось получить staffID: {staff_data if isinstance(staff_data, Exception) else 'Unknown error'}")
                return False
            
            self._save_cache({
                "main_domain": self.main_domain,
                "product_id": self.product_id,
                "staff_id": self.staff_id
            })
        
        logging.info(f"\n📧 Обрабатываем {len(email_list)} email-адрес...")
        
        results = []
        for i, email in enumerate(email_list, 1):
            logging.info(f"\n[{i}/{len(email_list)}] Обработка {email}...")
            console.print(f"\n[bold white][{i}/{len(email_list)}][/bold white] [cyan]Обработка {email}...[/cyan]")
            
            change_result = await self.change_email(email)
            if not change_result:
                logging.error(f"❌ Не удалось изменить email на {email}")
                results.append({
                    "email": email,
                    "success": False,
                    "error": "Failed to change email"
                })
                continue
            
            logging.info(f"[{self.acc_name}] ✅ Email изменен на {email}")
            
            # Подставляем персональную ссылку для этого email
            personalized_message = message
            if email_to_link and email in email_to_link:
                personalized_link = email_to_link[email]
                personalized_message = message.replace("{LINK}", personalized_link)
                logging.info(f"[{self.acc_name}] 🔗 Используем персональную ссылку: {personalized_link}")
            else:
                # Если нет персональной ссылки, убираем плейсхолдер или оставляем как есть
                if "{LINK}" in personalized_message:
                    logging.warning(f"[{self.acc_name}] ⚠️ Нет персональной ссылки для {email}")
            
            send_result = await self.send_text(personalized_message)
            if not send_result:
                logging.error(f"[{self.acc_name}] ❌ Не удалось отправить сообщение на {email}")
                console.print(f"[red] [{self.acc_name}] ❌ Не удалось отправить сообщение на {email} | {send_result}[/red]")

                results.append({
                    "email": email,
                    "success": False,
                    "error": "Failed to send message"
                })
                continue
            
            logging.info(f"[{self.acc_name}] ✅ Сообщение отправлено на {email}")
            logging.info(f"[{self.acc_name}]   Conversation ID: {self.conversation_id}")
            logging.info(f"[{self.acc_name}]   Conversation Token: {self.conversation_token}")
            
            # Выводим информацию об отправленной ссылке
            if email_to_link and email in email_to_link:
                sent_link = email_to_link[email]
                console.print(f"[bold green]  ✅ Сообщение отправлено на {email}[/bold green]")
                console.print(f"[green]  🔗 Ссылка: {sent_link}[/green]")
            else:
                console.print(f"[bold green]  ✅ Сообщение отправлено на {email}[/bold green]")
            
            results.append({
                "email": email,
                "success": True,
                "conversation_id": self.conversation_id,
                "conversation_token": self.conversation_token
            })
            
            # Пауза между отправками, чтобы сервис успевал обрабатывать
            if i < len(email_list):
                logging.info(f"[{self.acc_name}] ⏸️  Пауза {self.send_timeout} секунды перед следующей отправкой...")
                console.print(f"[yellow] [{self.acc_name}] ⏸️  Пауза {self.send_timeout} сек...[/yellow]")
                await asyncio.sleep(self.send_timeout)
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "total": len(email_list),
            "successful": successful,
            "failed": failed,
            "results": results,
            "message": message,
            "product_id": self.product_id,
            "main_domain": self.main_domain
        }

