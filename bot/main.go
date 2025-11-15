package main

import (
	"context"
	"log"
	"max-bot/api"
	"max-bot/config"
	"max-bot/handlers"
	"os"
	"os/signal"
	"syscall"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
)

func main() {
	// Загружаем конфигурацию
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	if cfg.MaxBotToken == "" {
		log.Fatal("MAX_BOT_TOKEN is required")
	}

	// Создаем оригинальный API клиент MAX
	originalAPI, err := maxbot.New(cfg.MaxBotToken)
	if err != nil {
		log.Fatalf("Failed to create MAX API client: %v", err)
	}

	// Создаем расширенный API клиент
	maxAPI := api.New(originalAPI)

	// Создаем контекст для graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Получаем информацию о боте
	botInfo, err := maxAPI.Bots.GetBot(ctx)
	if err != nil {
		log.Fatalf("Failed to get bot info: %v", err)
	}
	log.Printf("Bot started: %s (ID: %d)", botInfo.Name, botInfo.UserId)

	// Создаем обработчики
	handler := handlers.NewHandler(maxAPI, cfg)

	// Обработка сигналов для graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Запускаем обработку обновлений в отдельной горутине
	// Используем обертку API (GetUpdates доступен через встроенный *maxbot.Api)
	go func() {
		for update := range maxAPI.GetUpdates(ctx) {
			if err := handler.HandleUpdate(ctx, update); err != nil {
				// Логируем ошибку с деталями типа обновления
				if err.Error() != "" {
					log.Printf("Failed to handle update (type: %T): %v", update, err)
				} else {
					log.Printf("Failed to handle update (type: %T): unknown error", update)
				}
			}
		}
		log.Println("Updates channel closed")
	}()

	// Ожидаем сигнал завершения
	go func() {
		<-sigChan
		log.Println("Shutting down bot...")
		cancel()
	}()

	log.Println("Bot is running. Press Ctrl+C to stop.")
	<-ctx.Done()
	log.Println("Bot stopped")
}
