FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код Ghost API
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app

CMD ["sh", "-c", "uvicorn main:app --host ${GHOST_API_HOST:-0.0.0.0} --port ${GHOST_API_PORT:-8004}"]

