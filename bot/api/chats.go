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

// ChatsAPI предоставляет расширенные методы для работы с чатами
type ChatsAPI struct {
	api *maxbot.Api
}

// NewChatsAPI создает новый экземпляр ChatsAPI
func NewChatsAPI(api *maxbot.Api) *ChatsAPI {
	return &ChatsAPI{api: api}
}

// Все методы из оригинального фреймворка (обертки)

// GetChats возвращает список чатов
func (c *ChatsAPI) GetChats(ctx context.Context, count, marker int64) (*schemes.ChatList, error) {
	return c.api.Chats.GetChats(ctx, count, marker)
}

// GetChat возвращает информацию о чате по ID
func (c *ChatsAPI) GetChat(ctx context.Context, chatID int64) (*schemes.Chat, error) {
	return c.api.Chats.GetChat(ctx, chatID)
}

// GetChatMembership возвращает информацию о членстве бота в чате
func (c *ChatsAPI) GetChatMembership(ctx context.Context, chatID int64) (*schemes.ChatMember, error) {
	return c.api.Chats.GetChatMembership(ctx, chatID)
}

// GetChatMembers возвращает список участников чата
func (c *ChatsAPI) GetChatMembers(ctx context.Context, chatID, count, marker int64) (*schemes.ChatMembersList, error) {
	return c.api.Chats.GetChatMembers(ctx, chatID, count, marker)
}

// LeaveChat удаляет бота из чата
func (c *ChatsAPI) LeaveChat(ctx context.Context, chatID int64) (*schemes.SimpleQueryResult, error) {
	return c.api.Chats.LeaveChat(ctx, chatID)
}

// EditChat редактирует информацию о чате
func (c *ChatsAPI) EditChat(ctx context.Context, chatID int64, update *schemes.ChatPatch) (*schemes.Chat, error) {
	return c.api.Chats.EditChat(ctx, chatID, update)
}

// AddMember добавляет участников в чат
func (c *ChatsAPI) AddMember(ctx context.Context, chatID int64, users schemes.UserIdsList) (*schemes.SimpleQueryResult, error) {
	return c.api.Chats.AddMember(ctx, chatID, users)
}

// RemoveMember удаляет участника из чата
func (c *ChatsAPI) RemoveMember(ctx context.Context, chatID int64, userID int64) (*schemes.SimpleQueryResult, error) {
	return c.api.Chats.RemoveMember(ctx, chatID, userID)
}

// SendAction отправляет действие в чат
func (c *ChatsAPI) SendAction(ctx context.Context, chatID int64, action schemes.SenderAction) (*schemes.SimpleQueryResult, error) {
	return c.api.Chats.SendAction(ctx, chatID, action)
}

// Новые методы, не реализованные в оригинальном фреймворке

// GetChatByLink возвращает информацию о чате по публичной ссылке или username
// GET /chats/{chatLink}
func (c *ChatsAPI) GetChatByLink(ctx context.Context, chatLink string) (*schemes.Chat, error) {
	// Используем внутренний клиент для запроса
	client := c.getClient()
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(schemes.Chat)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodGet, fmt.Sprintf("chats/%s", chatLink), values, false, nil)
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

// DeleteChat удаляет чат для всех участников
// DELETE /chats/{chatId}
func (c *ChatsAPI) DeleteChat(ctx context.Context, chatID int64) (*schemes.SimpleQueryResult, error) {
	client := c.getClient()
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(schemes.SimpleQueryResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodDelete, fmt.Sprintf("chats/%d", chatID), values, false, nil)
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

// PinMessage закрепляет сообщение в чате
// PUT /chats/{chatId}/pin
func (c *ChatsAPI) PinMessage(ctx context.Context, chatID int64, messageID string, notify *bool) (*schemes.SimpleQueryResult, error) {
	client := c.getClient()
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	pinBody := schemes.PinMessageBody{
		MessageId: messageID,
		Notify:    notify,
	}

	result := new(schemes.SimpleQueryResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodPut, fmt.Sprintf("chats/%d/pin", chatID), values, false, pinBody)
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

// GetPinnedMessage возвращает закрепленное сообщение в чате
// GET /chats/{chatId}/pin
func (c *ChatsAPI) GetPinnedMessage(ctx context.Context, chatID int64) (*schemes.Message, error) {
	client := c.getClient()
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	type GetPinnedMessageResult struct {
		Message *schemes.Message `json:"message"`
	}

	result := new(GetPinnedMessageResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodGet, fmt.Sprintf("chats/%d/pin", chatID), values, false, nil)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err := body.Close(); err != nil {
			log.Println(err)
		}
	}()

	if err := json.NewDecoder(body).Decode(result); err != nil {
		return nil, err
	}

	return result.Message, nil
}

// UnpinMessage удаляет закрепленное сообщение из чата
// DELETE /chats/{chatId}/pin
func (c *ChatsAPI) UnpinMessage(ctx context.Context, chatID int64) (*schemes.SimpleQueryResult, error) {
	client := c.getClient()
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(schemes.SimpleQueryResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodDelete, fmt.Sprintf("chats/%d/pin", chatID), values, false, nil)
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

// getClient получает внутренний клиент из API
func (c *ChatsAPI) getClient() *httpClient {
	return getClient(c.api)
}

