"""
Простой тест для проверки импорта и базовой функциональности
"""

import sys
from pathlib import Path

# Добавляем директорию src в путь
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импорта модулей"""
    print("🧪 Тестирование импортов...")
    
    try:
        from src.LeboncoinParser import LeboncoinParser
        print("✅ LeboncoinParser импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта LeboncoinParser: {e}")
        return False
    
    try:
        from src.LeboncoinConfig import LEBONCOIN_CATEGORIES, DEFAULT_CATEGORIES
        print("✅ LeboncoinConfig импортирован успешно")
        print(f"   Доступно категорий: {len(LEBONCOIN_CATEGORIES)}")
    except Exception as e:
        print(f"❌ Ошибка импорта LeboncoinConfig: {e}")
        return False
    
    try:
        from src.LeboncoinUtils import load_proxies, filter_listings_by_seller
        print("✅ LeboncoinUtils импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта LeboncoinUtils: {e}")
        return False
    
    return True


def test_parser_creation():
    """Тест создания парсера"""
    print("\n🧪 Тестирование создания парсера...")
    
    try:
        from src.LeboncoinParser import LeboncoinParser
        
        # Создаем парсер без прокси
        parser = LeboncoinParser(
            categories=['voitures', 'informatique'],
            max_listings=10,
            max_concurrent=5,
        )
        
        print(f"✅ Парсер создан успешно")
        print(f"   Категорий выбрано: {len(parser.categories)}")
        print(f"   Максимум объявлений: {parser.max_listings}")
        print(f"   Base URL: {parser.base_url}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания парсера: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Тест конфигурации"""
    print("\n🧪 Тестирование конфигурации...")
    
    try:
        from src.LeboncoinConfig import LEBONCOIN_CATEGORIES, REGIONS
        
        print(f"✅ Конфигурация загружена")
        print(f"   Всего категорий: {len(LEBONCOIN_CATEGORIES)}")
        print(f"   Всего регионов: {len(REGIONS)}")
        
        # Показываем несколько категорий
        print("\n   Примеры категорий:")
        for i, (key, name) in enumerate(list(LEBONCOIN_CATEGORIES.items())[:5]):
            print(f"     - {key}: {name}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False


def test_utils():
    """Тест утилит"""
    print("\n🧪 Тестирование утилит...")
    
    try:
        from src.LeboncoinUtils import format_seller_stats, filter_listings_by_seller
        
        # Тестовые данные
        test_listings = [
            {
                'title': 'Test Item 1',
                'seller_info': {
                    'seller_id': 'seller1',
                    'seller_type': 'pro',
                    'sales_count': 10,
                    'reviews_count': 5,
                    'average_rating': 4.5,
                }
            },
            {
                'title': 'Test Item 2',
                'seller_info': {
                    'seller_id': 'seller2',
                    'seller_type': 'particulier',
                    'sales_count': 3,
                    'reviews_count': 2,
                    'average_rating': 3.8,
                }
            },
        ]
        
        # Тестируем статистику
        stats = format_seller_stats(test_listings)
        print(f"✅ Статистика вычислена:")
        print(f"   Всего объявлений: {stats['total_listings']}")
        print(f"   Средний рейтинг: {stats['avg_rating']:.2f}")
        
        # Тестируем фильтрацию
        filters = {
            'min_sales': 5,
            'min_rating': 4.0,
        }
        filtered = filter_listings_by_seller(test_listings, filters)
        print(f"✅ Фильтрация работает:")
        print(f"   До фильтрации: {len(test_listings)}")
        print(f"   После фильтрации: {len(filtered)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка утилит: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("🚀 Запуск тестов Leboncoin Parser")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_parser_creation,
        test_config,
        test_utils,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
