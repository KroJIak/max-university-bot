package handlers

import (
	"context"
	"fmt"
	"log"
	"max-bot/api"

	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

type Handler interface {
	HandleUpdate(ctx context.Context, update schemes.UpdateInterface) error
}

type handler struct {
	api *api.API
}

func NewHandler(api *api.API) Handler {
	return &handler{
		api: api,
	}
}

func (h *handler) HandleUpdate(ctx context.Context, update schemes.UpdateInterface) error {
	switch upd := update.(type) {
	case *schemes.MessageCreatedUpdate:
		return h.handleMessage(ctx, upd)
	case *schemes.MessageCallbackUpdate:
		return h.handleCallback(ctx, upd)
	case *schemes.BotStartedUpdate:
		return h.handleBotStarted(ctx, upd)
	default:
		log.Printf("Unknown update type: %T", update)
		return nil
	}
}

func (h *handler) handleMessage(ctx context.Context, update *schemes.MessageCreatedUpdate) error {
	// Простой эхо-бот: повторяем сообщение пользователя
	text := update.Message.Body.Text
	if text == "" {
		text = "Вы отправили сообщение без текста"
	}

	userID := update.Message.Sender.UserId
	responseText := fmt.Sprintf("Вы написали: %s", text)

	// Создаем сообщение используя обертку API
	msg := h.api.Messages.NewMessage().
		SetUser(userID).
		SetText(responseText)

	messageID, err := h.api.Messages.Send(ctx, msg)

	if err != nil {
		// Проверяем, является ли это реальной ошибкой или успешным ответом
		if apiErr, ok := err.(*schemes.Error); ok {
			// Если Code пустой, то это успешный ответ (библиотека возвращает Error даже при успехе)
			if apiErr.Code == "" {
				log.Printf("Echoed message to user %d (message ID: %s): %s", userID, messageID, responseText)
				return nil
			}
			// Это реальная ошибка
			log.Printf("Failed to send message to user %d: code=%s, error=%s", userID, apiErr.Code, apiErr.ErrorText)
			return fmt.Errorf("failed to send message to user %d: code=%s, error=%s", userID, apiErr.Code, apiErr.ErrorText)
		}
		// Другая ошибка (сетевая, таймаут и т.д.)
		log.Printf("Failed to send message to user %d: %v (type: %T)", userID, err, err)
		return fmt.Errorf("failed to send message to user %d: %w", userID, err)
	}

	log.Printf("Echoed message to user %d (message ID: %s): %s", userID, messageID, responseText)
	return nil
}

func (h *handler) handleCallback(ctx context.Context, update *schemes.MessageCallbackUpdate) error {
	log.Printf("Received callback from user %d: %s", update.Callback.User.UserId, update.Callback.CallbackID)
	// Здесь можно обработать callback от кнопок
	return nil
}

func (h *handler) handleBotStarted(ctx context.Context, update *schemes.BotStartedUpdate) error {
	log.Printf("Bot started by user %d", update.User.UserId)
	// Здесь можно отправить приветственное сообщение
	return nil
}

