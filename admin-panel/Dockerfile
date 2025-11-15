# Многостадийная сборка для Flutter web
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Копируем только файлы зависимостей для лучшего кеширования
COPY pubspec.yaml pubspec.lock ./

# Получаем зависимости (кешируется, если pubspec не изменился)
RUN flutter pub get

# Копируем только необходимые файлы для сборки
COPY lib/ lib/
COPY web/ web/
COPY analysis_options.yaml ./

# Собираем Flutter web приложение с оптимизациями
# В новых версиях Flutter --web-renderer убран, используется canvaskit по умолчанию
RUN flutter build web --release --base-href /

# Финальный образ с nginx
FROM nginx:alpine

# Устанавливаем envsubst для подстановки переменных окружения
RUN apk add --no-cache gettext

# Копируем собранные файлы Flutter web
COPY --from=build /app/build/web /usr/share/nginx/html

# Копируем шаблон конфигурационного файла
COPY config.js.template /usr/share/nginx/html/config.js.template

# Копируем entrypoint скрипт
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Настройка nginx для SPA (шаблон)
RUN echo 'server { \
    listen 8080; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /config.js { \
        add_header Cache-Control "no-cache, no-store, must-revalidate"; \
        add_header Pragma "no-cache"; \
        add_header Expires "0"; \
    } \
}' > /etc/nginx/conf.d/default.conf.template

EXPOSE 8080

CMD ["/docker-entrypoint.sh"]

