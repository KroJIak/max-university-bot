# Max University Bot - Mini App

Мини-приложение для студентов университета на React + TypeScript + Vite.

## Технологии

- **React 18** — UI библиотека
- **TypeScript** — типизация
- **Vite** — сборщик и dev-сервер
- **SCSS** — стилизация (через sass-embedded)
- **ESLint** — линтинг кода

## Быстрый старт

```bash
npm install
npm run dev
```

Приложение будет доступно на `http://localhost:5177`

## Скрипты

- `npm run dev` — локальная разработка с HMR (порт 5177)
- `npm run build` — production-сборка
- `npm run preview` — предпросмотр итоговой сборки
- `npm run lint` — проверка кода ESLint

## Структура проекта

```
src/
├── App.tsx                 # Корневой компонент с роутингом
├── main.tsx                # Точка входа
├── index.css               # Глобальные стили
├── components/             # Переиспользуемые компоненты
│   ├── api/               # API клиент
│   ├── color/             # Цветовая палитра
│   ├── Header/            # Кнопка назад в хедере
│   ├── icons/             # Иконки
│   ├── NewsFeed/          # Лента новостей
│   ├── NewsSection/       # Секция новостей
│   ├── Notifications/     # Уведомления
│   ├── Profile/           # Компоненты профиля
│   ├── ScheduleDetail/    # Детали расписания
│   ├── ScheduleSection/   # Секция расписания
│   └── Services/          # Сервисы
├── layout/                 # Компоненты макета
│   ├── Header/            # Шапка приложения
│   ├── Footer/            # Нижняя навигация
│   └── Layout.tsx         # Основной layout
├── pages/                  # Страницы приложения
│   ├── MainPage/          # Главная страница
│   ├── LoginPage/         # Страница входа
│   ├── ProfilePage/       # Профиль пользователя
│   ├── SchedulePage/      # Расписание
│   ├── NewsPage/          # Новости
│   ├── ServicesPage/      # Сервисы
│   ├── PrimaryServicesPage/ # Основные сервисы
│   ├── PlatformsPage/     # Веб-платформы
│   ├── TeachersPage/      # Преподаватели
│   ├── TeacherDetailPage/ # Детали преподавателя
│   ├── GradebookPage/     # Зачётная книжка
│   ├── DebtsPage/         # Долги
│   ├── ChatsPage/         # Чаты
│   ├── ContactsPage/      # Контакты
│   ├── MapsPage/          # Карта
│   ├── ClubsPage/         # Клубы
│   ├── NotificationsPage/ # Уведомления
│   ├── ThemePage/         # Настройки темы
│   └── SearchPage/        # Поиск
└── shared/                 # Общие утилиты и сервисы
    ├── data/              # Моки и статические данные
    ├── services/          # Сервисы (DataPreloader и др.)
    ├── state/             # Управление состоянием
    ├── types/             # TypeScript типы
    └── utils/             # Утилиты
```

## Конфигурация

### Переменные окружения

Приложение использует переменные окружения из корневого `.env` или локального `.env`:

- `VITE_API_BASE_URL` — базовый URL API (или `MAX_API_DOMAIN_URL` из корня)
- `CLOUDPUB_URL` / `CLOUDPUB_DOMAIN_URL` / `VITE_CLOUDPUB_URL` — URL для CloudPub
- `VITE_ALLOWED_HOSTS` — разрешённые хосты (через запятую)
- `VITE_HMR_DISABLED` — отключить HMR (`true`/`false`)
- `VITE_HMR_PROTOCOL` — протокол HMR (`ws`/`wss`)
- `VITE_HMR_HOST` — хост HMR
- `VITE_HMR_PORT` — порт HMR
- `VITE_HMR_CLIENT_PORT` — клиентский порт HMR

### Алиасы путей

В `vite.config.ts` настроены алиасы:
- `@components` → `src/components`
- `@shared` → `src/shared`

## Docker

Для запуска в Docker:

```bash
docker build -t max-university-miniapp .
docker run -p 8002:8002 max-university-miniapp
```

Или с переменными окружения:

```bash
docker run -p 8002:8002 \
  -e MINI_APP_HOST=0.0.0.0 \
  -e MINI_APP_PORT=8002 \
  max-university-miniapp
```

## Основные возможности

- 🔐 Авторизация через API
- 📅 Расписание занятий
- 📰 Новости университета
- 👤 Профиль студента
- 📚 Зачётная книжка и долги
- 👨‍🏫 Информация о преподавателях
- 💬 Чаты и контакты
- 🗺️ Карта кампуса
- 🎨 Настройки темы
- 🔔 Уведомления
- 🔍 Поиск по приложению

## Разработка

### Добавление новой страницы

1. Создайте папку в `src/pages/YourPage/`
2. Экспортируйте компонент через `index.ts`
3. Добавьте lazy import в `App.tsx`
4. Добавьте обработку в `pageConfig` useMemo

### Стилизация

Используйте SCSS модули для изоляции стилей:
```tsx
import styles from './Component.module.scss';
```

Глобальные стили и цветовая палитра находятся в `src/components/color/`.

## Лицензия

Проект разработан для хакатона от MAX и VK Education.
