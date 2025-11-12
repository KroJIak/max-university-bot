FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

CMD ["sh", "-c", "uvicorn main:app --host ${MAX_API_HOST:-0.0.0.0} --port ${MAX_API_PORT:-8000}"]

