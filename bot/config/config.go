package config

import (
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)

type Config struct {
	MaxBotToken      string
	UniversityAPIURL string
	WebAppURL        string
}

func Load() (*Config, error) {
	// Загружаем .env файл из корня проекта (на уровень выше от папки bot)
	// Пробуем загрузить из корня проекта
	_ = godotenv.Load("../.env")
	// Также пробуем загрузить из текущей директории (на случай если запускаем из корня)
	_ = godotenv.Load(".env")
	// Пробуем найти .env относительно текущего рабочего каталога
	if wd, err := os.Getwd(); err == nil {
		_ = godotenv.Load(filepath.Join(wd, ".env"))
		_ = godotenv.Load(filepath.Join(filepath.Dir(wd), ".env"))
	}

	return &Config{
		MaxBotToken:      getEnv("MAX_BOT_TOKEN", ""),
		UniversityAPIURL: getEnv("UNIVERSITY_API_URL", "https://max-api.cloudpub.ru"),
		WebAppURL:        getEnv("WEB_APP_URL", "https://max-miniapp.cloudpub.ru/"),
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
