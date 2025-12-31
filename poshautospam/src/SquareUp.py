import asyncio
import json
import os

import certifi
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from dotenv import load_dotenv

from src.decode_response import parse_create_project_response
from src.protobuf_generator import (
    build_create_project_payload,
    write_string_field,
    write_varint_field,
)

load_dotenv()

class SquareUpClient:
    def __init__(self, account_cookies):
        self.session = AsyncSession(impersonate="safari_ios", cert=certifi.where())
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "content-type": "application/json; charset=UTF-8",
            "origin": "https://app.squareup.com",
            "priority": "u=1, i",
            "referer": "https://app.squareup.com/dashboard/projects/proj_4ZR7S76KYHEDTZ5B7YVWX4HX46?currentUnitToken=LYMAMGTGMRS8B",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "traceparent": "00-0000000000000000587b43a0b4baa493-54747a679a4de9ff-01",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "x-allow-cookies": ",C0001,C0002,C0003,C0004,",
            "x-block-cookies": "true",
            "x-csrf-token": "",
            "x-datadog-origin": "rum",
            "x-datadog-parent-id": "6085623581873400319",
            "x-datadog-sampling-priority": "1",
            "x-datadog-trace-id": "6375764054979028115",
            "x-requested-with": "XMLHttpRequest"
        }
        self.name = os.getenv("NAME", "Orders")
        self.surname = os.getenv("SURNAME", "Soldout")
        self.proxy = os.getenv("MAIN_PROXY")
        self.merchant_token = None
        self.unit_token = None
        self.csfr_token = None
        self.account_name = account_cookies

        self.init_cookies()

    def init_cookies(self):
        with open(self.account_name, encoding="utf-8") as f:
            cookies = json.load(f)
            for cookie in cookies:
                self.session.cookies.set(name=cookie["name"], value=cookie["value"], path=cookie["path"], domain=cookie["domain"])

    def _parse_csfr(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.find("meta", {"name": "csrf-token"})["content"]

    async def main(self):
        url = "https://app.squareup.com/dashboard/projects"
        for _ in range(3):
            try:
                r = await self.session.get(url, headers=self.headers, proxy=self.proxy)
                if r.status_code == 200:
                    data = r.text
                    self.csfr_token = self._parse_csfr(data)
                    return True
                return (r.status_code, False)
            except Exception as e:
                if "curl" in str(e):
                    print(f"❌ Curl: {e}")
                    await asyncio.sleep(0.4)
                    continue
                return (e, False)
        return False

    async def get_self_data(self):
        import time
        self.headers["x-csrf-token"] = self.csfr_token
        url = f"https://app.squareup.com/dashboard/current-user-data?d={int(time.time())}"
        for _ in range(3):
            try:

                r = await self.session.get(url, headers=self.headers, proxy=self.proxy)
                if r.status_code == 200:
                    data = r.json()
                    self.merchant_token = data["user"]["token"]
                    self.unit_token = data["user"]["main_unit_token"]
                    return True
                return (r.status_code, False)
            except Exception as e:
                if "curl" in str(e):
                    await asyncio.sleep(0.4)
                    continue
                return (e, False)
        return False

    async def create_contact(self, email: str, name: str = "Orders", surname: str = "Soldout"):
        import uuid

        url = "https://app.squareup.com/services/squareup.rolodex.RolodexService/CreateContact"
        js = {
            "merchant_token": self.merchant_token,
            "request_token": str(uuid.uuid4()),
            "contact": {
                "profile": {
                "address": {},
                "birthday": {},
                "email_address": email,
                "given_name": name,
                "surname": surname
                }
            }
        }
        try:
            r = await self.session.post(url, headers=self.headers, json=js, proxy=self.proxy)
            if r.status_code == 200:
                data = r.json()
                return data["contact"]["contact_token"]
            print(f"❌ Error: {r.text} | Status_code: {r.status_code}")
            # При 401 сразу возвращаем без retry
            if r.status_code == 401:
                return (401, False)
            return (r.status_code, False)
        except Exception as e:
            return (e, False)

    async def create_project(self, project_name: str, contact_tokens: list, timezone: str = "Europe/London"):
        h = self.headers.copy()
        h["content-type"] = "application/x-protobuf"
        h["accept"] = "application/x-protobuf"
        h["x-speleo-trace-id"] = "aVVKCVfdFVRbH"

        url = "https://app.squareup.com/services/squareup.projects.service.ProjectsService/CreateProject"

        payload = build_create_project_payload(
            unit_token=self.unit_token,
            project_name=project_name,
            contact_tokens=contact_tokens,
            timezone=timezone
        )

        for attempt in range(3):
            try:
                r = await self.session.post(url, headers=h, data=payload, proxy=self.proxy)

                if r.status_code == 200:
                    response_data = parse_create_project_response(r.content)

                    if response_data and response_data.get("project_token"):
                        return response_data
                    print(f"❌ Попытка {attempt + 1}/3: project_token не найден в ответе")
                    print(f"📄 Response content (first 500 bytes): {r.content[:500]}")
                    if attempt < 2:
                        await asyncio.sleep(0.5)
                        continue
                    return False
                print(f"❌ Попытка {attempt + 1}/3: HTTP {r.status_code}")
                print(f"📄 Response text: {r.text}")
                if attempt < 2:
                    await asyncio.sleep(0.5)
                    continue
                return False
            except Exception as e:
                print(f"❌ Попытка {attempt + 1}/3: Exception - {e}")
                if "curl" in str(e) and attempt < 2:
                    await asyncio.sleep(0.4)
                    continue
                return (e, False)
        return False

    async def send_to_email(self, project_token: str, contact_tokens: list, message: str = ""):
        h = self.headers.copy()

        h["content-type"] = "application/x-protobuf"
        h["accept"] = "application/x-protobuf"
        h["x-speleo-trace-id"] = "BQbKcekkXajgf"

        url = "https://app.squareup.com/services/squareup.projects.service.ProjectsService/ShareProject"

        payload = bytearray()

        payload.extend(write_string_field(1, project_token))

        for contact_token in contact_tokens:
            payload.extend(write_string_field(2, contact_token))

        payload.extend(write_varint_field(3, 0))

        if message:
            payload.extend(write_string_field(4, message))

        for _ in range(3):
            try:
                r = await self.session.post(
                    url,
                    data=bytes(payload),
                    headers=h,
                    proxy=self.proxy
                )

                if r.status_code == 200:
                    return True
                return (r.status_code, r.text)
            except Exception as e:
                if "curl" in str(e):
                    await asyncio.sleep(0.4)
                    continue
                return (e, False)
        return False

    async def execute_solo_project(
        self,
        email_list: list,
        message: str,
        project_prefix: str = "Depop",
        timezone: str = "Europe/London",
        name: str = "Orders",
        surname: str = "Soldout"
    ) -> dict | bool:
        import time

        main_page = await self.main()
        self_data = await self.get_self_data()

        if not main_page or isinstance(main_page, Exception):
            print(f"❌ Не удалось получить КСФР: {main_page if isinstance(main_page, Exception) else 'Unknown error'}")
            return False

        if not self_data or isinstance(self_data, Exception):
            print(f"❌ Не удалось получить данные пользователя: {self_data if isinstance(self_data, Exception) else 'Unknown error'}")
            return False

        project_name = f"{project_prefix}{int(time.time())}"

        print(f"📧 Создаем {len(email_list)} контактов...")
        contact_results = await asyncio.gather(
            *[self.create_contact(email, name=name, surname=surname) for email in email_list],
            return_exceptions=True
        )

        tokens = []
        for i, (email, result) in enumerate(zip(email_list, contact_results), 1):
            if isinstance(result, Exception):
                print(f"❌ Ошибка создания контакта {email}: {result}")
                return False
            if not result or isinstance(result, tuple):
                print(f"❌ Не удалось создать контакт {email}: {result}")
                if isinstance(result, tuple) and len(result) == 2 and result[0] == 401:
                    print("🚫 401 UNAUTHORIZED - куки невалидны!")
                    return (401, False)
                return False
            print(f"✅ [{i}/{len(email_list)}] Контакт создан: {result}")
            tokens.append(result)

        print(f"\n📁 Создаем проект '{project_name}'...")
        create_project = await self.create_project(
            project_name=project_name,
            contact_tokens=tokens,
            timezone=timezone
        )

        if not create_project or isinstance(create_project, (tuple, bool)):
            print(f"❌ Не удалось создать проект: {create_project}")
            return False

        project_token = create_project["project_token"]
        print(f"✅ Проект создан: {project_token}")

        print(f"\n📨 Отправляем email на {len(tokens)} контактов...")
        send_result = await self.send_to_email(
            project_token=project_token,
            contact_tokens=tokens,
            message=message
        )

        if not send_result or isinstance(send_result, tuple):
            print(f"❌ Не удалось отправить на почту: {send_result}")
            return False

        print("✅ Все письма успешно отправлены!")

        return {
            "project_token": project_token,
            "project_name": project_name,
            "contact_tokens": tokens,
            "emails": email_list,
            "success": True
        }
