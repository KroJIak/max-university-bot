# Детали реализации

Ключевые технические детали реализации системы Max University Bot.

## Содержание

- [Архитектура проксирования](#архитектура-проксирования)
- [Web Scraping](#web-scraping)
- [Multi-tenancy](#multi-tenancy)
- [Конфигурация endpoints](#конфигурация-endpoints)
- [Fallback логика](#fallback-логика)

## Архитектура проксирования

MAX API проксирует запросы к University API или Ghost API в зависимости от конфигурации:

### Логика выбора API

1. **Проверка конфигурации:**
   - Если endpoint настроен в БД → запрос к **University API**
   - Если endpoint пустой → запрос к **Ghost API**

2. **Определение URL:**
   - Приоритет 1: `base_url` из БД (настраивается в админ-панели)
   - Приоритет 2: `http://UNIVERSITY_API_HOST:UNIVERSITY_API_PORT`

3. **Обработка ошибок:**
   - Если University API недоступен → автоматический fallback на Ghost API
   - Логирование всех ошибок для отладки

### Пример потока

```
Bot → MAX API → Проверка конфигурации
                    ├─ Endpoint настроен → University API
                    └─ Endpoint пустой → Ghost API
```

---

## Web Scraping

University API использует web scraping для получения данных с сайта университета.

### Управление сессиями

- **Cookies сохраняются в БД** для каждого студента
- **Сессии обновляются** при каждом логине
- **Кэширование данных** для уменьшения нагрузки

### Структура скрапера

```
university-app/services/
├── base.py          # Базовый класс с session management
├── auth.py          # Логин студентов
├── schedule.py      # Парсинг расписания
├── teachers.py      # Получение преподавателей
├── contacts.py      # Парсинг контактов
├── personal_data.py # Личные данные
└── utils.py         # Утилиты (парсинг дат и т.д.)
```

### Особенности парсинга

- **Динамические ID:** Используется поиск по паттернам (`id.endswith('-1')`)
- **AJAX запросы:** Эмуляция браузерных запросов
- **Обработка ошибок:** Graceful degradation при изменении структуры сайта

---

## Multi-tenancy

Система поддерживает изоляцию данных по `university_id`.

### Реализация

1. **Все запросы фильтруются** по `university_id`
2. **JWT токены** содержат `university_id`
3. **Конфигурация** хранится отдельно для каждого университета

### Таблицы с multi-tenancy

- `universities` - список университетов
- `users` - пользователи привязаны к `university_id`
- `university_config` - конфигурация для каждого университета
- `student_credentials` - студенты привязаны к пользователям

---

## Конфигурация endpoints

Конфигурация endpoints хранится в БД и настраивается через админ-панель.

### Структура конфигурации

```json
{
  "base_url": "https://university-api.example.com",
  "endpoints": {
    "students_login": "/students/login",
    "students_schedule": "/students/schedule",
    "students_teachers": "/students/teachers",
    // ... другие endpoints
  },
  "enabled_features": {
    "students_login": true,
    "students_schedule": true,
    // ... другие функции
  }
}
```

### Автоопределение endpoints

Админ-панель может автоматически определять endpoints через OpenAPI схему University API.

### Валидация

- Проверка доступности `base_url`
- Проверка существования endpoints
- Валидация структуры ответов

---

## Fallback логика

Система использует многоуровневую fallback логику для обеспечения надежности.

### Уровни fallback

1. **Доменный URL → HOST:PORT**
   - Если `DOMAIN_URL` указан, но недоступен → используется `http://HOST:PORT`

2. **University API → Ghost API**
   - Если endpoint настроен, но University API недоступен → запрос к Ghost API
   - Если endpoint пустой → сразу запрос к Ghost API

3. **Обработка ошибок**
   - Все ошибки логируются
   - Пользователю показывается понятное сообщение об ошибке

### Примеры

**Пример 1: Доменный URL недоступен**
```
MAX_API_DOMAIN_URL=https://api.example.com (недоступен)
→ Fallback: http://0.0.0.0:8003
```

**Пример 2: University API недоступен**
```
Endpoint настроен: /students/schedule
University API недоступен
→ Fallback: Ghost API
```

---

## Аутентификация

### JWT токены

- Используются для доступа к защищенным endpoints
- Содержат `university_id` для multi-tenancy
- Время жизни: настраивается

### Поток аутентификации

1. Администратор логинится через админ-панель
2. MAX API возвращает JWT токен
3. Админ-панель сохраняет токен
4. Все последующие запросы используют токен

---

## База данных

### Схема БД

**maxbot_db:**
- `universities` - университеты
- `users` - пользователи MAX
- `student_credentials` - связь пользователей и студентов
- `university_config` - конфигурация endpoints

**university_db:**
- `session_cookies` - cookies сессий студентов

**ghost_db:**
- `teachers` - преподаватели
- `schedule` - расписание
- `news` - новости
- `maps` - карты
- `contacts` - контакты

### Миграции

SQL миграции находятся в `migrations/` и применяются вручную.

---

## Тестирование

### Тестовый аккаунт

Для тестирования доступен специальный аккаунт:
- **Email:** `test@test.ru`
- **Пароль:** `test`
- Использует реальные данные студента ЧГУ
- Не привязан к конкретному `user_id`

### Тестирование API

Используйте скрипт `scripts/test_api.py` для тестирования endpoints.

---

## Ключевые файлы

### MAX API
- `app/api/v1/proxy.py` - проксирование запросов
- `app/api/v1/config.py` - управление конфигурацией
- `app/core/url_helper.py` - утилиты для работы с URL

### University API
- `university-app/services/university_scraper.py` - основной скрапер
- `university-app/api/students.py` - endpoints

### Ghost API
- `ghost-app/api/upload.py` - загрузка CSV
- `ghost-app/services/csv_parser.py` - парсинг CSV
