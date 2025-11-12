package api

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// MessagesAPI предоставляет расширенные методы для работы с сообщениями
type MessagesAPI struct {
	api *maxbot.Api
}

// NewMessagesAPI создает новый экземпляр MessagesAPI
func NewMessagesAPI(api *maxbot.Api) *MessagesAPI {
	return &MessagesAPI{api: api}
}

// Все методы из оригинального фреймворка (обертки)

// GetMessages возвращает список сообщений
func (m *MessagesAPI) GetMessages(ctx context.Context, chatID int64, messageIDs []string, from int, to int, count int) (*schemes.MessageList, error) {
	return m.api.Messages.GetMessages(ctx, chatID, messageIDs, from, to, count)
}

// Send отправляет сообщение
func (m *MessagesAPI) Send(ctx context.Context, message *maxbot.Message) (string, error) {
	return m.api.Messages.Send(ctx, message)
}

// SendMessageResult отправляет сообщение и возвращает результат
func (m *MessagesAPI) SendMessageResult(ctx context.Context, message *maxbot.Message) (schemes.Message, error) {
	return m.api.Messages.SendMessageResult(ctx, message)
}

// EditMessage редактирует сообщение
func (m *MessagesAPI) EditMessage(ctx context.Context, messageID int64, message *maxbot.Message) error {
	return m.api.Messages.EditMessage(ctx, messageID, message)
}

// DeleteMessage удаляет сообщение
func (m *MessagesAPI) DeleteMessage(ctx context.Context, messageID int64) (*schemes.SimpleQueryResult, error) {
	return m.api.Messages.DeleteMessage(ctx, messageID)
}

// AnswerOnCallback отвечает на callback
func (m *MessagesAPI) AnswerOnCallback(ctx context.Context, callbackID string, callback *schemes.CallbackAnswer) (*schemes.SimpleQueryResult, error) {
	return m.api.Messages.AnswerOnCallback(ctx, callbackID, callback)
}

// NewKeyboardBuilder создает новый билдер клавиатуры
func (m *MessagesAPI) NewKeyboardBuilder() *maxbot.Keyboard {
	return m.api.Messages.NewKeyboardBuilder()
}

// NewMessage создает новый объект сообщения (обертка над maxbot.NewMessage)
func (m *MessagesAPI) NewMessage() *maxbot.Message {
	return maxbot.NewMessage()
}

// Новые методы, не реализованные в оригинальном фреймворке

// GetMessage возвращает одно сообщение по его ID
// GET /messages/{messageId}
func (m *MessagesAPI) GetMessage(ctx context.Context, messageID string) (*schemes.Message, error) {
	client := getClient(m.api)
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(schemes.Message)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodGet, fmt.Sprintf("messages/%s", messageID), values, false, nil)
	if err != nil {
		return result, err
	}
	defer func() {
		if err := body.Close(); err != nil {
			log.Println(err)
		}
	}()
	return result, json.NewDecoder(body).Decode(result)
}

