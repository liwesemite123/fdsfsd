import aiofiles
import os
import shutil
from pathlib import Path
import hashlib

def _user_dir(uid: int) -> str:
	p = os.path.join("db", str(uid))
	os.makedirs(p, exist_ok=True)
	return p

async def add_user_to_database(path, user_id):
	try:
		async with aiofiles.open(
			path, mode="r", encoding="utf-8"
		) as f:
			users = await f.read()
			users = users.splitlines()
	except FileNotFoundError:
		users = []

	if str(user_id) not in users:
		async with aiofiles.open(
			path, mode="a", encoding="utf-8"
		) as f:
			await f.write(f"{user_id}\n")


def load_proxy() -> list[str]:
	with open("proxies.txt", "r") as f:
		return f.read().splitlines()


def get_cookie_files(cookies_dir: str = "cookies") -> list[str]:
    cookies_path = Path(cookies_dir)

    if not cookies_path.exists():
        cookies_path.mkdir(parents=True, exist_ok=True)
        return []

    cookie_files = [
        str(file_path)
        for file_path in cookies_path.iterdir()
        if file_path.suffix == ".txt"
    ]

    return sorted(cookie_files)

def move_account_to_spammed(cookie_file_path: str, spammed_dir: str = "spammed_square") -> bool:
    try:
        spammed_path = Path(spammed_dir)
        spammed_path.mkdir(parents=True, exist_ok=True)

        cookie_file = Path(cookie_file_path)
        if not cookie_file.exists():
            print(f"❌ Файл не найден: {cookie_file_path}")
            return False

        destination = spammed_path / cookie_file.name
        shutil.move(str(cookie_file), str(destination))
        return True

    except Exception as e:
        print(f"❌ Ошибка при перемещении файла {cookie_file_path}: {e}")
        return False

def get_account_count(cookies_dir: str = "cookies") -> int:
    """
    Получить количество доступных аккаунтов.

    Args:
        cookies_dir: Путь к папке с куками

    Returns:
        Количество файлов куков
    """
    return len(get_cookie_files(cookies_dir))

def read_message_text(text_file: str = "Texts/text.txt", default_message: str = "") -> str:
    """
    Считать текст сообщения из файла.

    Args:
        text_file: Путь к файлу с текстом сообщения
        default_message: Сообщение по умолчанию, если файл не найден

    Returns:
        Текст сообщения из файла или default_message
    """
    text_path = Path(text_file)

    try:
        if not text_path.exists():
            print(f"⚠️ Файл {text_file} не найден, используем сообщение по умолчанию")
            return default_message

        with text_path.open(encoding="utf-8") as f:
            message = f.read().strip()

        if not message:
            print(f"⚠️ Файл {text_file} пуст, используем сообщение по умолчанию")
            return default_message

        print(f"✅ Сообщение загружено из {text_file}: {message[:50]}...")
        return message

    except Exception as e:
        print(f"❌ Ошибка чтения файла {text_file}: {e}")
        return default_message

def move_account_to_bad(cookie_file_path: str, bad_dir: str = "bad_accounts") -> bool:
    """
    Переместить файл куков невалидного аккаунта в папку bad_accounts.

    Args:
        cookie_file_path: Полный путь к файлу куков
        bad_dir: Папка для перемещения невалидных аккаунтов

    Returns:
        True если перемещение успешно, False в случае ошибки
    """
    try:
        bad_path = Path(bad_dir)
        bad_path.mkdir(parents=True, exist_ok=True)

        cookie_file = Path(cookie_file_path)
        if not cookie_file.exists():
            print(f"❌ Файл не найден: {cookie_file_path}")
            return False

        destination = bad_path / cookie_file.name
        shutil.move(str(cookie_file), str(destination))

        return True

    except Exception as e:
        print(f"❌ Ошибка при перемещении файла {cookie_file_path}: {e}")
        return False

def encode_md5(e):
    message = str(e) + "f34c9278042a"
    md5_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
    return md5_hash