# Структура проекта

Подробное описание структуры директорий и файлов проекта Max University Bot.

## 📁 Общая структура

```
Max-University-Bot/
├── app/                      # MAX API (основной API)
├── bot/                      # MAX бот
├── admin-panel/              # Админ-панель (Flutter Web)
├── university-app/           # University API
├── ghost-app/                # Ghost API
├── mini-app/                 # Mini App (React)
├── migrations/               # SQL миграции
├── scripts/                  # Вспомогательные скрипты
├── documentation/            # Документация
├── cloudpub-config/          # Конфигурация CloudPub
├── docker-compose.yml        # Docker Compose для AMD64
├── docker-compose-arm64.yml  # Docker Compose для ARM64
├── docker-compose-without-cloudpub.yml  # Без CloudPub
├── .env.example              # Пример файла переменных окружения
└── README.md                 # Главный README
```

## 📦 Детальное описание компонентов

### 1. `app/` - MAX API (Основной API)

**Назначение:** Главный API сервис, который управляет университетами, пользователями, студентами и координирует работу всех остальных сервисов.

**Технологии:** Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL

**Структура:**
```
app/
├── api/
│   └── v1/
│       ├── health.py         # Health check endpoints
│       ├── users.py          # Управление пользователями
│       ├── universities.py   # Управление университетами
│       ├── config.py         # Конфигурация University API
│       └── proxy.py          # Проксирование запросов к University/Ghost API
├── core/
│   ├── database.py           # Настройка БД
│   └── url_helper.py         # Утилиты для работы с URL
├── models/                   # SQLAlchemy модели
│   ├── university.py
│   ├── user.py
│   ├── student_credentials.py
│   └── university_config.py
├── repositories/             # Репозитории для работы с БД
├── services/                 # Бизнес-логика
│   ├── students_service.py
│   └── university_api_client.py
├── main.py                   # Точка входа FastAPI
├── requirements.txt          # Python зависимости
└── Dockerfile                # Docker образ
```

**Основные функции:**
- Управление университетами (CRUD)
- Аутентификация университетов (JWT)
- Управление пользователями и студентами
- Конфигурация endpoints для University API
- Проксирование запросов к University API или Ghost API
- Multi-tenancy (изоляция данных по `university_id`)

**Порт:** 8003 (по умолчанию)

---

### 2. `bot/` - MAX бот

**Назначение:** MAX бот, который взаимодействует с пользователями через MAX Bot API.

**Технологии:** Go 1.23+, MAX Bot API Client

**Структура:**
```
bot/
├── api/                      # Обертка над MAX Bot API
│   ├── client.go
│   ├── messages.go
│   ├── keyboards.go
│   └── ...
├── handlers/                 # Обработчики событий
│   └── handler.go
├── keyboards/                # Компоненты клавиатур
│   └── main.go
├── pages/                    # Страницы интерфейса
│   └── pages.go
├── services/                 # Сервисы для работы с API
├── types/                    # Типы данных
│   └── types.go
├── config/                   # Конфигурация
│   └── config.go
├── main.go                   # Точка входа
├── go.mod                    # Go модуль
└── Dockerfile                # Docker образ
```

**Основные функции:**
- Обработка сообщений от пользователей
- Отображение меню и навигации
- Запросы к MAX API для получения данных
- Отображение расписания, преподавателей, новостей и т.д.

**Зависимости:** Требует запущенный MAX API

---

### 3. `admin-panel/` - Админ-панель

**Назначение:** Веб-интерфейс для настройки конфигурации университетов, endpoints и ручного ввода данных.

**Технологии:** Flutter Web, Dart

**Структура:**
```
admin-panel/
├── lib/
│   ├── main.dart             # Точка входа
│   ├── models/               # Модели данных
│   │   ├── university_config.dart
│   │   └── module.dart
│   ├── screens/              # Экраны приложения
│   │   ├── login_screen.dart
│   │   ├── main_screen.dart
│   │   ├── teachers_screen.dart
│   │   ├── schedule_screen.dart
│   │   └── ...
│   └── services/             # Сервисы для работы с API
│       ├── api_service.dart
│       └── mock_api_service.dart
├── web/
│   ├── index.html
│   └── config.js.template    # Шаблон конфигурации
├── docker-entrypoint.sh      # Entrypoint скрипт
├── Dockerfile                # Docker образ
├── pubspec.yaml              # Flutter зависимости
└── build.sh                  # Скрипт сборки
```

**Основные функции:**
- Аутентификация администраторов университетов
- Настройка base URL для University API
- Настройка endpoints для различных функций
- Ручной ввод данных (преподаватели, расписание) через CSV
- Загрузка CSV файлов в Ghost API

**Порт:** 8081 (по умолчанию)

**Особенности:**
- Динамическая конфигурация через `config.js` (генерируется из `.env`)
- Поддержка fallback URL (domain → host:port)
- Интеграция с OpenAPI для автоматического определения endpoints

---

### 4. `university-app/` - University API

**Назначение:** API для взаимодействия с сайтом университета через web scraping.

**Технологии:** Python 3.10+, FastAPI, BeautifulSoup, httpx

**Структура:**
```
university-app/
├── api/
│   └── students.py           # Endpoints для студентов
├── core/
│   └── database.py           # Настройка БД
├── services/
│   └── scraper.py            # Web scraping логика
├── models/                   # SQLAlchemy модели
├── repositories/             # Репозитории
├── data/                     # Данные для парсинга
├── main.py                   # Точка входа
├── requirements.txt
└── Dockerfile
```

**Основные функции:**
- Логин студентов на сайте университета
- Получение данных студентов (личные данные, расписание, преподаватели)
- Web scraping с сайта университета
- Управление cookies сессий
- Кэширование данных

**Порт:** 8001 (по умолчанию)

**База данных:** `university_db` (отдельная БД)

---

### 5. `ghost-app/` - Ghost API

**Назначение:** Резервный API, который симулирует University API, но использует данные из БД вместо scraping. Данные загружаются через CSV.

**Технологии:** Python 3.10+, FastAPI, SQLAlchemy

**Структура:**
```
ghost-app/
├── api/
│   ├── students.py           # Endpoints (симуляция University API)
│   └── upload.py             # Загрузка CSV файлов
├── core/
│   └── database.py
├── services/
│   └── csv_parser.py         # Парсинг CSV
├── models/
├── repositories/
├── main.py
├── requirements.txt
└── Dockerfile
```

**Основные функции:**
- Те же endpoints, что и University API
- Хранение данных в БД
- Загрузка данных через CSV файлы
- Используется, когда endpoint не настроен в админ-панели

**Порт:** 8004 (по умолчанию)

**База данных:** `ghost_db` (отдельная БД)

**Когда используется:**
- Если в админ-панели функционал включен, но endpoint пустой
- Администратор вводит данные вручную и загружает CSV
- MAX API автоматически переключается на Ghost API

---

### 6. `mini-app/` - Mini App

**Назначение:** Веб-приложение для расширенного функционала бота (открывается внутри MAX).

**Технологии:** React, TypeScript, Vite

**Структура:**
```
mini-app/
├── src/
│   ├── components/           # React компоненты
│   ├── pages/                # Страницы
│   ├── services/             # API клиенты
│   └── main.tsx              # Точка входа
├── index.html
├── package.json
├── vite.config.ts
└── Dockerfile
```

**Основные функции:**
- Расширенный интерфейс для функций бота
- Интеграция с MAX WebApp API
- Взаимодействие с MAX API

**Порт:** 8002 (по умолчанию)

---

### 7. `migrations/` - SQL миграции

**Назначение:** SQL скрипты для миграций базы данных.

**Структура:**
```
migrations/
├── add_login_password_to_universities.sql
├── add_university_id_to_university_config.sql
├── add_university_id_to_users.sql
├── update_existing_universities_passwords.sql
└── README.md
```

**Использование:**
- Применяются вручную или через скрипты
- Создают/изменяют структуру БД
- Обновляют существующие данные

---

### 8. `scripts/` - Вспомогательные скрипты

**Назначение:** Утилиты для разработки и обслуживания.

**Содержимое:**
```
scripts/
├── scraper.py                # Скрипты для парсинга
├── test_api.py               # Тестирование API
├── check_ajax.py             # Проверка AJAX запросов
└── html_to_md.py             # Конвертация HTML в Markdown
```

---

### 9. `cloudpub-config/` - Конфигурация CloudPub

**Назначение:** Хранилище конфигурации для CloudPub сервисов.

**Структура:**
```
cloudpub-config/
├── cloudpub-api/
├── cloudpub-admin-panel/
├── cloudpub-university-api/
├── cloudpub-mini-app/
└── cloudpub-ghost-api/
```

**Использование:**
- Автоматически создается при первом запуске
- Хранит конфигурацию туннелей CloudPub
- Не требует ручного редактирования

---

## 🔗 Взаимодействие компонентов

```
┌─────────────┐
│     MAX     │
│     Bot     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MAX API    │◄──────┐
│   (app/)    │       │
└──────┬──────┘       │
       │              │
       ├──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ University  │ │   Ghost     │ │  Admin      │
│    API      │ │    API      │ │   Panel     │
│(university- │ │ (ghost-app) │ │(admin-panel)│
│   app/)     │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
       │              │
       └──────┬───────┘
              │
              ▼
       ┌─────────────┐
       │  PostgreSQL │
       │   Database  │
       └─────────────┘
```

## 📝 Важные файлы

### Docker Compose файлы

- **`docker-compose.yml`** - Для AMD64 архитектуры (стандартные серверы)
- **`docker-compose-arm64.yml`** - Для ARM64 архитектуры (Raspberry Pi, Apple Silicon)
- **`docker-compose-without-cloudpub.yml`** - Без CloudPub сервисов

### Конфигурационные файлы

- **`.env`** - Переменные окружения (не коммитится в Git)
- **`.env.example`** - Пример переменных окружения
- **`config.js.template`** - Шаблон конфигурации для админ-панели

### Документация

- **`README.md`** - Главный README с быстрым стартом
- **`documentation/`** - Детальная документация

---

## 🔍 Поиск файлов

### Где найти основные компоненты:

- **API endpoints:** `app/api/v1/`
- **Модели БД:** `app/models/`, `university-app/models/`, `ghost-app/models/`
- **Web scraping:** `university-app/services/scraper.py`
- **Конфигурация:** `app/api/v1/config.py`
- **Проксирование:** `app/api/v1/proxy.py`
- **Обработчики бота:** `bot/handlers/`
- **Экраны админ-панели:** `admin-panel/lib/screens/`


