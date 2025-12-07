# Max University Bot

Max University Bot is a microservices platform for creating university chatbots in the MAX messenger that provide students with access to academic schedules, teacher information, contacts, and personal data. The system automatically retrieves data from university websites via web scraping and supports multiple universities with isolated data through multi-tenancy architecture.

## Содержание

- [Описание проекта](#описание-проекта)
- [Быстрый старт](#быстрый-старт)
- [Архитектура системы](#архитектура-системы)
- [Документация](#документация)
- [Требования](#требования)

## Описание проекта

**Max University Bot** — это микросервисная система для создания и управления ботами университетов в MAX. Система позволяет:

- **Multi-tenancy**: Поддержка множества университетов с изолированными данными
- **Гибкая конфигурация**: Настройка endpoints через веб-админ-панель
- **Web Scraping**: Автоматическое получение данных с сайтов университетов
- **Ghost API**: Резервный API для ручного ввода данных через CSV
- **MAX Bot**: Интеграция с MAX Bot API для работы в MAX
- **Mini App**: Веб-приложение для расширенного функционала
- **CloudPub**: Поддержка публикации сервисов в облако (опционально)

## Быстрый старт

### Стандартный запуск (Docker Compose)

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd Max-University-Bot
   ```

2. **Создайте файл `.env` на основе `.env.example` и вставьте токен нашего бота (мы не публицируем его в гитхабе, т.к. это открытый репозиторий и его могут найти):**
   ```bash
   cp .env.example .env
   ```

3. **Настройте переменные окружения** (см. [SETUP.md](project-docs/SETUP.md))

4. **Запустите все сервисы:**
   ```bash
   # Для ARM64 (Raspberry Pi, Apple Silicon)
   docker compose -f docker-compose-arm64.yml up -d
   
   # Для AMD64 (обычные серверы)
   docker compose -f docker-compose.yml up -d
   ```

5. **Проверьте статус сервисов:**
   ```bash
   docker compose ps
   ```

6. **Откройте админ-панель:**
   - Локально: http://localhost:8081
   - Или по домену, если настроен `ADMIN_PANEL_DOMAIN_URL`


## Архитектура системы

Система состоит из следующих микросервисов:

| Сервис | Описание | Порт | Технологии |
|--------|----------|------|------------|
| **Bot** | MAX бот | - | Go |
| **API (MAX API)** | Основной API для управления | 8003 | Python FastAPI |
| **Admin Panel** | Веб-админ-панель | 8081 | Flutter Web |
| **University API** | API для работы с сайтом университета | 8001 | Python FastAPI |
| **Ghost API** | Резервный API для ручных данных | 8004 | Python FastAPI |
| **Mini App** | Веб-приложение для бота | 8002 | React + TypeScript |
| **PostgreSQL** | База данных | 5432 | PostgreSQL 15 |

Подробное описание в [ARCHITECTURE.md](project-docs/ARCHITECTURE.md).

## Варианты запуска

**Стандартный запуск (с CloudPub):**
```bash
# ARM64
docker compose -f docker-compose-arm64.yml up -d

# AMD64
docker compose -f docker-compose.yml up -d
```

**Без CloudPub (локальная разработка):**
```bash
docker compose -f docker-compose-without-cloudpub.yml up -d
```

**Важно:** Mini App требует CloudPub для работы, так как привязан к домену `max-miniapp.cloudpub.ru`.

Подробнее см. [SETUP.md](project-docs/SETUP.md).

## Разработка

### Структура проекта

```
Max-University-Bot/
├── app/                 # MAX API (основной API)
├── bot/                 # MAX бот (Go)
├── admin-panel/         # Админ-панель (Flutter Web)
├── university-app/      # University API (Python FastAPI)
├── ghost-app/           # Ghost API (Python FastAPI)
├── mini-app/            # Mini App (React + TypeScript)
├── migrations/          # SQL миграции
├── scripts/             # Вспомогательные скрипты
├── project-docs/        # Документация
└── docker-compose*.yml  # Docker Compose конфигурации
```

### Первые шаги для разработчиков

1. Изучите [архитектуру системы](project-docs/ARCHITECTURE.md)
2. Ознакомьтесь с [настройкой и запуском](project-docs/SETUP.md)
3. Прочитайте [детали реализации](project-docs/IMPLEMENTATION.md)

## Документация

- **[SETUP.md](project-docs/SETUP.md)** - Настройка, переменные окружения, запуск
- **[ARCHITECTURE.md](project-docs/ARCHITECTURE.md)** - Архитектура, сервисы, структура проекта
- **[IMPLEMENTATION.md](project-docs/IMPLEMENTATION.md)** - Детали реализации

## Решение проблем

См. раздел [Решение проблем](project-docs/SETUP.md#решение-проблем) в SETUP.md.