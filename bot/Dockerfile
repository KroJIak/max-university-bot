# === Build stage ===
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Копируем go.mod и go.sum (если есть)
COPY go.mod go.sum* ./

# Устанавливаем зависимости
RUN go mod download

# Копируем исходники
COPY . .

# Обновляем go.mod и go.sum
RUN go mod tidy

# Собираем бинарник
RUN CGO_ENABLED=0 GOOS=linux go build -o bot ./main.go

# === Final stage ===
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Копируем собранный бинарник
COPY --from=builder /app/bot .

# Запуск
CMD ["./bot"]
