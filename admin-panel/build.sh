#!/bin/bash
# Скрипт для быстрой сборки admin-panel с использованием BuildKit

# Включаем BuildKit для ускорения сборки
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Собираем только admin-panel
docker compose build admin-panel

# Запускаем контейнер
docker compose up admin-panel -d


