# Как остановить бота

## Способ 1: Остановить все процессы `go run main.go`
```bash
pkill -f "go run main.go"
```

## Способ 2: Остановить все процессы принудительно (если способ 1 не работает)
```bash
pkill -9 -f "go run main.go"
```

## Способ 3: Остановить все процессы скомпилированного бота
```bash
pkill -f "./bot"
# или принудительно
pkill -9 -f "./bot"
```

## Способ 4: Остановить по PID (если знаете ID процесса)
```bash
# Найти PID
ps aux | grep "go run main.go\|\./bot$" | grep -v grep

# Остановить по PID (замените 12345 на реальный PID)
kill 12345

# Или принудительно
kill -9 12345
```

## Способ 5: Если бот запущен в текущем терминале
Нажмите `Ctrl+C` в терминале, где запущен бот.

## Проверить, что все процессы остановлены
```bash
ps aux | grep -E "go run main.go|\./bot$" | grep -v grep
```
Если команда ничего не выводит - все процессы остановлены.

## Остановить все процессы одним разом
```bash
pkill -9 -f "go run main.go" && pkill -9 -f "./bot"
```

## Остановить Docker контейнер бота (если запущен)
```bash
# Проверить, запущен ли контейнер
docker ps | grep maxbot_bot

# Остановить контейнер бота
docker stop maxbot_bot

# Или через docker-compose
docker compose -f docker-compose-arm64.yml stop bot
```
