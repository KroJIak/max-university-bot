package handlers

import (
	"context"
	"log"
	"max-bot/api"
	"max-bot/config"
	"max-bot/pages"

	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

type Handler interface {
	HandleUpdate(ctx context.Context, update schemes.UpdateInterface) error
}

type handler struct {
	api     *api.API
	pages   *pages.PagesAPI
	config  *config.Config
}

func NewHandler(api *api.API, cfg *config.Config) Handler {
	return &handler{
		api:    api,
		pages:  pages.NewPagesAPI(api, cfg.UniversityAPIURL, cfg.WebAppURL),
		config: cfg,
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
	if update == nil {
		log.Printf("Received nil message update")
		return nil
	}

	if update.Message.Sender.UserId == 0 {
		log.Printf("Received message with zero user ID")
		return nil
	}

	userID := update.Message.Sender.UserId
	text := update.Message.Body.Text

	log.Printf("Received message from user %d: %s", userID, text)

	// Проверяем, залогинен ли пользователь в системе
	statusResp, err := h.pages.GetStudentStatus(ctx, userID)
	if err != nil {
		log.Printf("Failed to check student status: %v", err)
		// В случае ошибки показываем страницу авторизации
		return h.pages.ShowAuthRequiredPage(ctx, userID)
	}

	// Если пользователь не залогинен, показываем страницу авторизации
	if statusResp == nil || !statusResp.IsLinked {
		return h.pages.ShowAuthRequiredPage(ctx, userID)
	}

	// На любое сообщение (команду или текст) показываем главное меню
	// НЕ повторяем текст (не эхо-бот)
	return h.pages.ShowMainPage(ctx, userID, "today")
}

func (h *handler) handleCallback(ctx context.Context, update *schemes.MessageCallbackUpdate) error {
	userID := update.Callback.User.UserId
	callbackID := update.Callback.CallbackID

	log.Printf("Received callback from user %d: %s", userID, callbackID)

	// Обрабатываем callback через PagesAPI, передавая оригинальное сообщение
	var originalMessage *schemes.Message
	if update.Message != nil {
		originalMessage = update.Message
	}
	
	return h.pages.HandleCallback(ctx, update.Callback, userID, originalMessage)
}

func (h *handler) handleBotStarted(ctx context.Context, update *schemes.BotStartedUpdate) error {
	userID := update.User.UserId
	log.Printf("Bot started by user %d", userID)

	// Проверяем, залогинен ли пользователь в системе
	statusResp, err := h.pages.GetStudentStatus(ctx, userID)
	if err != nil {
		log.Printf("Failed to check student status: %v", err)
		// В случае ошибки показываем страницу авторизации
		return h.pages.ShowAuthRequiredPage(ctx, userID)
	}

	// Если пользователь не залогинен, показываем страницу авторизации
	if statusResp == nil || !statusResp.IsLinked {
		return h.pages.ShowAuthRequiredPage(ctx, userID)
	}

	// Показываем главную страницу при первом запуске бота
	return h.pages.ShowMainPage(ctx, userID, "today")
}

