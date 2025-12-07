# Настройка и запуск

Руководство по настройке переменных окружения, запуску проекта и управлению сервисами.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [Docker Compose файлы](#docker-compose-файлы)
- [Управление сервисами](#управление-сервисами)
- [Решение проблем](#решение-проблем)

## Быстрый старт

### 1. Подготовка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd Max-University-Bot

# Создайте .env файл
cp .env.example .env
```

### 2. Настройка обязательных переменных

Откройте `.env` и укажите:

```env
MAX_BOT_TOKEN=your_bot_token_here          # Обязательно
POSTGRES_PASSWORD=secure_password          # Обязательно
CLOUDPUB_TOKEN=your_cloudpub_token         # Если используете CloudPub
```

**Где получить токен бота:** [MasterBot](https://max.ru/MasterBot)

### 3. Запуск

**Для ARM64 (Raspberry Pi, Apple Silicon):**
```bash
docker compose -f docker-compose-arm64.yml up -d
```

**Для AMD64 (обычные серверы):**
```bash
docker compose -f docker-compose.yml up -d
```

**Без CloudPub (локальная разработка):**
```bash
docker compose -f docker-compose-without-cloudpub.yml up -d
```

### 4. Проверка

```bash
# Статус сервисов
docker compose ps

# Логи
docker compose logs -f

# Доступ к сервисам
# Admin Panel: http://localhost:8081
# MAX API: http://localhost:8003/docs
```

---

## Переменные окружения

### Обязательные

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `MAX_BOT_TOKEN` | Токен MAX бота | `1234567890:ABC...` |
| `POSTGRES_PASSWORD` | Пароль БД | `secure_password` |
| `CLOUDPUB_TOKEN` | Токен CloudPub (если используется) | `your_token` |

### MAX API

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `MAX_API_HOST` | `0.0.0.0` | Хост сервера |
| `MAX_API_PORT` | `8003` | Порт сервера |
| `MAX_API_DOMAIN_URL` | - | Доменный URL (приоритет над HOST:PORT) |

### Admin Panel

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `ADMIN_PANEL_HOST` | `0.0.0.0` | Хост сервера |
| `ADMIN_PANEL_PORT` | `8081` | Порт сервера |
| `ADMIN_PANEL_DOMAIN_URL` | - | Доменный URL |

### University API

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `UNIVERSITY_API_HOST` | `0.0.0.0` | Хост сервера |
| `UNIVERSITY_API_PORT` | `8001` | Порт сервера |
| `UNIVERSITY_API_DOMAIN_URL` | - | Доменный URL |

### Ghost API

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `GHOST_API_HOST` | `0.0.0.0` | Хост сервера |
| `GHOST_API_PORT` | `8004` | Порт сервера |
| `GHOST_API_DOMAIN_URL` | - | Доменный URL |

### Mini App

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `MINI_APP_HOST` | `0.0.0.0` | Хост сервера |
| `MINI_APP_PORT` | `8002` | Порт сервера |
| `MINI_APP_DOMAIN_URL` | - | Доменный URL |

### База данных

| Переменная | По умолчанию | Описание |
|-----------|--------------|----------|
| `DATABASE_URL` | `postgresql://maxbot:maxbot123@postgres:5432/maxbot_db` | Основная БД |
| `UNIVERSITY_DATABASE_URL` | `postgresql://maxbot:maxbot123@postgres:5432/university_db` | БД University API |
| `GHOST_DATABASE_URL` | `postgresql://maxbot:maxbot123@postgres:5432/ghost_db` | БД Ghost API |
| `POSTGRES_USER` | `maxbot` | Пользователь БД |
| `POSTGRES_PASSWORD` | `maxbot123` | Пароль БД |
| `POSTGRES_DB` | `maxbot_db` | Имя основной БД |

### Fallback логика

Система автоматически переключается между доменными URL и HOST:PORT:

1. **Приоритет 1:** Доменный URL (если указан и доступен)
2. **Приоритет 2:** `http://HOST:PORT` (fallback)

**Пример:**
- Если `MAX_API_DOMAIN_URL=https://api.example.com` недоступен → используется `http://0.0.0.0:8003`

---

## Docker Compose файлы

### `docker-compose.yml` (AMD64)

Стандартная конфигурация для серверов x86_64.

**Включает:**
- Все основные сервисы
- CloudPub сервисы
- Автоматический перезапуск

### `docker-compose-arm64.yml` (ARM64)

Конфигурация для Raspberry Pi и Apple Silicon.

**Особенности:**
- Использует `cloudpub/cloudpub:latest-arm64`
- Оптимизирован для ARM архитектуры

### `docker-compose-without-cloudpub.yml`

Конфигурация без CloudPub (локальная разработка).

**Используется когда:**
- Не нужна публикация в облако
- Ограниченные ресурсы
- Локальная разработка

**Важно:** Mini App будет недоступен без CloudPub, так как он привязан к домену `max-miniapp.cloudpub.ru`.

### Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| `api` | 8003 | MAX API |
| `bot` | - | MAX бот |
| `admin-panel` | 8081 | Админ-панель |
| `university-api` | 8001 | University API |
| `ghost-api` | 8004 | Ghost API |
| `mini-app` | 8002 | Mini App |
| `postgres` | 5432 | PostgreSQL |
| `cloudpub-*` | - | CloudPub туннели (опционально) |

---

## Управление сервисами

### Запуск

```bash
# Все сервисы
docker compose -f docker-compose-arm64.yml up -d

# Конкретный сервис
docker compose -f docker-compose-arm64.yml up -d api
```

### Остановка

```bash
# Остановка
docker compose -f docker-compose-arm64.yml down

# Остановка с удалением volumes (удалит данные БД!)
docker compose -f docker-compose-arm64.yml down -v
```

### Перезапуск

```bash
# Конкретный сервис
docker compose -f docker-compose-arm64.yml restart api

# Все сервисы
docker compose -f docker-compose-arm64.yml restart
```

### Логи

```bash
# Все сервисы
docker compose -f docker-compose-arm64.yml logs -f

# Конкретный сервис
docker compose -f docker-compose-arm64.yml logs -f api
```

### Пересборка

```bash
# Все образы
docker compose -f docker-compose-arm64.yml build

# Конкретный сервис
docker compose -f docker-compose-arm64.yml build admin-panel

# Пересборка и запуск
docker compose -f docker-compose-arm64.yml up -d --build
```

### Статус

```bash
# Статус всех сервисов
docker compose ps

# Использование ресурсов
docker stats
```

---

## Решение проблем

### Порты заняты

**Ошибка:** `Error: bind: address already in use`

**Решение:**
1. Измените порты в `.env`
2. Или найдите и остановите процесс:
   ```bash
   sudo lsof -i :8003
   sudo kill -9 <PID>
   ```

### Ошибки базы данных

**Ошибка:** `FATAL: database "maxbot_db" does not exist`

**Решение:**
1. Проверьте `DATABASE_URL` в `.env`
2. Проверьте статус PostgreSQL:
   ```bash
   docker compose ps postgres
   docker compose logs postgres
   ```

### Сервис не запускается

**Решение:**
1. Проверьте логи: `docker compose logs -f <service-name>`
2. Проверьте зависимости: `docker compose ps`
3. Перезапустите: `docker compose restart <service-name>`

### Очистка

```bash
# Удаление неиспользуемых образов
docker image prune -a

# Полная очистка (удалит все!)
docker system prune -a --volumes
```

### Бэкап БД

```bash
# Создание бэкапа
docker compose exec postgres pg_dump -U maxbot maxbot_db > backup.sql

# Восстановление
docker compose exec -T postgres psql -U maxbot maxbot_db < backup.sql
```

---

## Безопасность

1. **Измените пароли по умолчанию** в `.env`
2. **Ограничьте доступ к портам** через firewall
3. **Используйте HTTPS** в продакшене
4. **Регулярно обновляйте образы:**
   ```bash
   docker compose pull
   docker compose up -d
   ```


