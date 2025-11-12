package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	MaxBotToken string
}

func Load() (*Config, error) {
	// Загружаем .env файл если он существует
	_ = godotenv.Load()

	return &Config{
		MaxBotToken: getEnv("MAX_BOT_TOKEN", ""),
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
