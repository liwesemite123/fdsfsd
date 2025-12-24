"""
Пример использования парсера Leboncoin

Этот скрипт демонстрирует как:
1. Загрузить прокси из файла
2. Выбрать категории для парсинга
3. Настроить фильтры по продавцам
4. Запустить парсер
5. Сохранить результаты
"""

import asyncio
import sys
from pathlib import Path

# Добавляем директорию src в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.LeboncoinParser import LeboncoinParser
from src.LeboncoinConfig import LEBONCOIN_CATEGORIES, DEFAULT_CATEGORIES
from src.LeboncoinUtils import (
    load_proxies,
    create_results_dir,
    filter_listings_by_seller,
    format_seller_stats,
)
from loguru import logger


async def main():
    """Основная функция запуска парсера"""
    
    # Настройка логирования
    logger.add(
        "leboncoin_parser.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )
    
    # 1. Загружаем прокси из файла
    logger.info("Загрузка прокси...")
    proxies = load_proxies("proxies.txt")
    
    if not proxies:
        logger.warning("⚠️ Прокси не загружены. Парсинг будет выполняться без прокси.")
    
    # 2. Выбираем категории для парсинга
    # Можно использовать DEFAULT_CATEGORIES или указать свои
    categories_to_parse = [
        'voitures',          # Автомобили
        'informatique',      # Компьютеры
        'telephonie',        # Телефония
        'ameublement',       # Мебель
        'immobilier',        # Недвижимость
    ]
    
    logger.info(f"Выбраны категории: {categories_to_parse}")
    
    # 3. Создаем парсер
    parser = LeboncoinParser(
        categories=categories_to_parse,
        proxy_list=proxies,
        max_listings=50,      # Максимум объявлений
        max_concurrent=5,     # Одновременных запросов
    )
    
    # 4. Запускаем парсинг
    logger.info("🚀 Запуск парсинга...")
    try:
        listings = await parser.start_parsing()
        logger.success(f"✅ Парсинг завершен! Найдено объявлений: {len(listings)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        return 1
    
    # 5. Фильтруем по параметрам продавца
    logger.info("Применение фильтров продавца...")
    
    # Настройки фильтра:
    seller_filters = {
        'min_sales': 5,           # Минимум 5 продаж
        'min_reviews': 2,         # Минимум 2 отзыва
        'min_rating': 3.5,        # Рейтинг не ниже 3.5
        'seller_types': ['pro', 'particulier']  # Оба типа продавцов
    }
    
    filtered_listings = filter_listings_by_seller(listings, seller_filters)
    logger.info(
        f"После фильтрации осталось {len(filtered_listings)} из {len(listings)} объявлений"
    )
    
    # 6. Получаем статистику
    stats = format_seller_stats(filtered_listings)
    logger.info("📊 Статистика продавцов:")
    logger.info(f"  Всего объявлений: {stats['total_listings']}")
    logger.info(f"  Уникальных продавцов: {stats['total_sellers']}")
    logger.info(f"  Профессиональных продавцов: {stats['pro_sellers']}")
    logger.info(f"  Частных продавцов: {stats['particulier_sellers']}")
    logger.info(f"  Средний рейтинг: {stats['avg_rating']:.2f}")
    logger.info(f"  Среднее количество отзывов: {stats['avg_reviews']:.1f}")
    logger.info(f"  Среднее количество продаж: {stats['avg_sales']:.1f}")
    
    # 7. Сохраняем результаты
    results_dir = create_results_dir("leboncoin_results")
    
    # Все результаты
    all_results_file = results_dir / "all_listings.json"
    parser.save_results(str(all_results_file))
    
    # Отфильтрованные результаты
    if filtered_listings:
        import json
        filtered_file = results_dir / "filtered_listings.json"
        with open(filtered_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_listings, f, ensure_ascii=False, indent=2)
        logger.success(f"💾 Отфильтрованные результаты сохранены в {filtered_file}")
    
    # Сохраняем статистику
    stats_file = results_dir / "statistics.json"
    import json
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    logger.success(f"📈 Статистика сохранена в {stats_file}")
    
    # 8. Выводим примеры найденных объявлений
    logger.info("\n📋 Примеры найденных объявлений:")
    for i, listing in enumerate(filtered_listings[:5], 1):
        seller_info = listing.get('seller_info', {})
        logger.info(f"\n{i}. {listing.get('title', 'N/A')}")
        logger.info(f"   Цена: {listing.get('price', 'N/A')} €")
        logger.info(f"   Локация: {listing.get('location', 'N/A')}")
        logger.info(f"   Продавец: {seller_info.get('seller_name', 'N/A')}")
        logger.info(f"   Тип продавца: {seller_info.get('seller_type', 'N/A')}")
        logger.info(f"   Продаж: {seller_info.get('sales_count', 0)}")
        logger.info(f"   Отзывов: {seller_info.get('reviews_count', 0)}")
        logger.info(f"   Рейтинг: {seller_info.get('average_rating', 0.0)}")
        logger.info(f"   URL: {listing.get('url', 'N/A')}")
    
    logger.success("\n✅ Работа завершена!")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Программа остановлена пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
