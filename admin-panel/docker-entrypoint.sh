#!/bin/sh
set -e

# Подставляем переменные окружения в config.js
envsubst '${MAX_API_DOMAIN_URL} ${MAX_API_HOST} ${MAX_API_PORT} ${GHOST_API_DOMAIN_URL} ${GHOST_API_HOST} ${GHOST_API_PORT}' < /usr/share/nginx/html/config.js.template > /usr/share/nginx/html/config.js

# Подставляем переменные в конфигурацию nginx
envsubst '${ADMIN_PANEL_HOST} ${ADMIN_PANEL_PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Запускаем nginx
exec nginx -g "daemon off;"

