FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY university-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код University API (полностью изолированный)
COPY university-app/ .

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app

CMD ["sh", "-c", "uvicorn main:app --host ${UNIVERSITY_API_HOST:-0.0.0.0} --port ${UNIVERSITY_API_PORT:-8001}"]

