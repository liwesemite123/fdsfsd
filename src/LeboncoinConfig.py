"""
Конфигурация для Leboncoin парсера
"""

# Категории leboncoin для парсинга
LEBONCOIN_CATEGORIES = {
    # Транспорт
    'vehicules': 'Транспорт',
    'voitures': 'Автомобили',
    'motos': 'Мотоциклы',
    'caravaning': 'Караванинг',
    'utilitaires': 'Коммерческий транспорт',
    'equipement_auto': 'Автозапчасти',
    'equipement_moto': 'Мотозапчасти',
    'equipement_caravaning': 'Караванинг оборудование',
    'nautisme': 'Водный транспорт',
    'equipement_nautisme': 'Оборудование для водного транспорта',
    
    # Недвижимость
    'immobilier': 'Недвижимость',
    'ventes_immobilieres': 'Продажа недвижимости',
    'locations': 'Аренда',
    'colocations': 'Совместная аренда',
    'bureaux_commerces': 'Офисы и коммерция',
    
    # Мультимедиа
    'multimedia': 'Мультимедиа',
    'informatique': 'Компьютеры',
    'consoles_jeux_video': 'Консоли и видеоигры',
    'image_son': 'Изображение и звук',
    'telephonie': 'Телефония',
    
    # Дом
    'maison': 'Дом',
    'ameublement': 'Мебель',
    'electromenager': 'Бытовая техника',
    'arts_de_la_table': 'Столовые приборы',
    'decoration': 'Декор',
    'linge_de_maison': 'Домашний текстиль',
    'bricolage': 'DIY и ремонт',
    'jardinage': 'Садоводство',
    'vetements': 'Одежда',
    'chaussures': 'Обувь',
    'accessoires_bagagerie': 'Аксессуары и сумки',
    'montres_bijoux': 'Часы и ювелирные изделия',
    'equipement_bebe': 'Товары для детей',
    'vetements_bebe': 'Детская одежда',
    
    # Досуг
    'loisirs': 'Досуг',
    'dvd_films': 'DVD и фильмы',
    'cd_musique': 'CD и музыка',
    'livres': 'Книги',
    'animaux': 'Животные',
    'velos': 'Велосипеды',
    'sports_hobbies': 'Спорт и хобби',
    'instruments_de_musique': 'Музыкальные инструменты',
    'collection': 'Коллекционирование',
    'jeux_jouets': 'Игры и игрушки',
    'vins_gastronomie': 'Вино и гастрономия',
    
    # Профессиональное
    'materiel_professionnel': 'Профессиональное оборудование',
    'materiel_agricole': 'Сельхозтехника',
    'transport_manutention': 'Транспорт и погрузка',
    'btp_chantier': 'Строительство',
    'outillage_materiaux_2nd_oeuvre': 'Инструменты и материалы',
    'equipements_industriels': 'Промышленное оборудование',
    'restauration_hotellerie': 'Рестораны и отели',
    'fournitures_de_bureau': 'Офисные принадлежности',
    'commerces_marches': 'Торговля и рынки',
    'materiel_medical': 'Медицинское оборудование',
    
    # Услуги
    'services': 'Услуги',
    'prestations_de_services': 'Предоставление услуг',
    'billetterie': 'Билеты',
    'evenements': 'Мероприятия',
    'cours_particuliers': 'Частные уроки',
    'covoiturage': 'Совместные поездки',
    
    # Работа
    'emploi': 'Работа',
    'offres_emploi': 'Вакансии',
    'demandes_emploi': 'Поиск работы',
}

# Настройки по умолчанию
DEFAULT_CATEGORIES = [
    'voitures',
    'immobilier',
    'informatique',
    'telephonie',
    'ameublement',
]

# Регионы Франции
REGIONS = {
    'ile_de_france': 'Иль-де-Франс',
    'auvergne_rhone_alpes': 'Овернь-Рона-Альпы',
    'provence_alpes_cote_d_azur': 'Прованс-Альпы-Лазурный берег',
    'nouvelle_aquitaine': 'Новая Аквитания',
    'occitanie': 'Окситания',
    'hauts_de_france': 'О-де-Франс',
    'grand_est': 'Гранд-Эст',
    'pays_de_la_loire': 'Земли Луары',
    'bretagne': 'Бретань',
    'normandie': 'Нормандия',
    'bourgogne_franche_comte': 'Бургундия-Франш-Конте',
    'centre_val_de_loire': 'Центр-Долина Луары',
    'corse': 'Корсика',
}
