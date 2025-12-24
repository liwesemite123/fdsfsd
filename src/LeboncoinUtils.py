"""
Утилиты для работы с парсером Leboncoin
"""
import os
from pathlib import Path
from typing import List


def load_proxies(proxy_file: str = "proxies.txt") -> List[str]:
    """
    Загрузить прокси из файла
    
    Args:
        proxy_file: Путь к файлу с прокси
        
    Returns:
        Список прокси
    """
    try:
        proxy_path = Path(proxy_file)
        if not proxy_path.exists():
            print(f"⚠️ Файл {proxy_file} не найден, прокси не будут использоваться")
            return []
        
        with proxy_path.open('r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"✅ Загружено {len(proxies)} прокси из {proxy_file}")
        return proxies
    except Exception as e:
        print(f"❌ Ошибка при загрузке прокси: {e}")
        return []


def create_results_dir(dir_name: str = "leboncoin_results") -> Path:
    """
    Создать директорию для результатов
    
    Args:
        dir_name: Имя директории
        
    Returns:
        Path объект директории
    """
    results_dir = Path(dir_name)
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def save_seller_filter_config(
    min_sales: int = 0,
    min_reviews: int = 0,
    min_rating: float = 0.0,
    seller_types: List[str] = None,
    filename: str = "seller_filters.txt"
):
    """
    Сохранить конфигурацию фильтров продавца
    
    Args:
        min_sales: Минимальное количество продаж
        min_reviews: Минимальное количество отзывов
        min_rating: Минимальный рейтинг
        seller_types: Типы продавцов ('pro' или 'particulier')
        filename: Имя файла
    """
    try:
        config = {
            'min_sales': min_sales,
            'min_reviews': min_reviews,
            'min_rating': min_rating,
            'seller_types': seller_types or ['pro', 'particulier']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Конфигурация фильтров сохранена в {filename}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении конфигурации: {e}")


def load_seller_filter_config(filename: str = "seller_filters.txt") -> dict:
    """
    Загрузить конфигурацию фильтров продавца
    
    Args:
        filename: Имя файла
        
    Returns:
        Словарь с настройками фильтров
    """
    default_config = {
        'min_sales': 0,
        'min_reviews': 0,
        'min_rating': 0.0,
        'seller_types': ['pro', 'particulier']
    }
    
    try:
        if not Path(filename).exists():
            return default_config
        
        config = {}
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    try:
                        # Пытаемся преобразовать в число
                        if '.' in value:
                            config[key] = float(value)
                        elif value.isdigit():
                            config[key] = int(value)
                        else:
                            # Обработка списков
                            if value.startswith('[') and value.endswith(']'):
                                config[key] = eval(value)
                            else:
                                config[key] = value
                    except:
                        config[key] = value
        
        return {**default_config, **config}
    except Exception as e:
        print(f"❌ Ошибка при загрузке конфигурации: {e}")
        return default_config


def filter_listings_by_seller(listings: List[dict], config: dict) -> List[dict]:
    """
    Фильтровать объявления по параметрам продавца
    
    Args:
        listings: Список объявлений
        config: Конфигурация фильтров
        
    Returns:
        Отфильтрованный список объявлений
    """
    filtered = []
    
    for listing in listings:
        seller_info = listing.get('seller_info', {})
        
        # Проверяем фильтры
        if seller_info.get('sales_count', 0) < config.get('min_sales', 0):
            continue
        
        if seller_info.get('reviews_count', 0) < config.get('min_reviews', 0):
            continue
        
        if seller_info.get('average_rating', 0.0) < config.get('min_rating', 0.0):
            continue
        
        seller_type = seller_info.get('seller_type')
        allowed_types = config.get('seller_types', ['pro', 'particulier'])
        if seller_type and seller_type not in allowed_types:
            continue
        
        filtered.append(listing)
    
    return filtered


def format_seller_stats(listings: List[dict]) -> dict:
    """
    Получить статистику по продавцам
    
    Args:
        listings: Список объявлений
        
    Returns:
        Словарь со статистикой
    """
    stats = {
        'total_listings': len(listings),
        'total_sellers': 0,
        'pro_sellers': 0,
        'particulier_sellers': 0,
        'avg_sales': 0,
        'avg_reviews': 0,
        'avg_rating': 0.0,
    }
    
    sellers = set()
    total_sales = 0
    total_reviews = 0
    total_rating = 0.0
    rating_count = 0
    
    for listing in listings:
        seller_info = listing.get('seller_info', {})
        seller_id = seller_info.get('seller_id')
        
        if seller_id:
            sellers.add(seller_id)
        
        seller_type = seller_info.get('seller_type')
        if seller_type == 'pro':
            stats['pro_sellers'] += 1
        elif seller_type == 'particulier':
            stats['particulier_sellers'] += 1
        
        total_sales += seller_info.get('sales_count', 0)
        total_reviews += seller_info.get('reviews_count', 0)
        
        rating = seller_info.get('average_rating', 0.0)
        if rating > 0:
            total_rating += rating
            rating_count += 1
    
    stats['total_sellers'] = len(sellers)
    
    if len(listings) > 0:
        stats['avg_sales'] = total_sales / len(listings)
        stats['avg_reviews'] = total_reviews / len(listings)
    
    if rating_count > 0:
        stats['avg_rating'] = total_rating / rating_count
    
    return stats
