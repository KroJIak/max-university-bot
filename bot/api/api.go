package api

import (
	maxbot "github.com/max-messenger/max-bot-api-client-go"
)

// API представляет расширенный клиент MAX Bot API
// Включает все методы из оригинального фреймворка плюс дополнительные методы
// 
// Использование:
//   originalAPI, err := maxbot.New(token)
//   if err != nil {
//       log.Fatal(err)
//   }
//   api := api.New(originalAPI)
//   
//   // Использование оригинальных методов
//   botInfo, err := api.Bots.GetBot(ctx)
//   if err != nil {
//       log.Printf("Error: %v", err)
//   }
//   
//   // Использование расширенных методов
//   chat, err := api.Chats.GetChatByLink(ctx, "chat-link")
//   admins, err := api.Admins.GetChatAdmins(ctx, chatID)
//   message, err := api.Messages.GetMessage(ctx, messageID)
//   video, err := api.Videos.GetVideoDetails(ctx, videoToken)
type API struct {
	// Оригинальный API клиент - все методы доступны напрямую
	*maxbot.Api

	// Расширенные методы для работы с чатами (включая новые)
	Chats *ChatsAPI
	
	// Методы для работы с администраторами чатов
	Admins *AdminsAPI
	
	// Расширенные методы для работы с сообщениями
	Messages *MessagesAPI
	
	// Методы для работы с видео
	Videos *VideosAPI
}

// New создает новый экземпляр расширенного API
func New(originalAPI *maxbot.Api) *API {
	api := &API{
		Api: originalAPI,
	}

	// Инициализируем расширенные API
	api.Chats = NewChatsAPI(originalAPI)
	api.Admins = NewAdminsAPI(originalAPI)
	api.Messages = NewMessagesAPI(originalAPI)
	api.Videos = NewVideosAPI(originalAPI)

	return api
}

