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

// ChatAdminPermission представляет права администратора чата
type ChatAdminPermission = schemes.ChatAdminPermission

// Константы прав администратора
const (
	ReadAllMessages  ChatAdminPermission = schemes.READ_ALL_MESSAGES
	AddRemoveMembers ChatAdminPermission = schemes.ADD_REMOVE_MEMBERS
	AddAdmins        ChatAdminPermission = schemes.ADD_ADMINS
	ChangeChatInfo   ChatAdminPermission = schemes.CHANGE_CHAT_INFO
	PinMessage       ChatAdminPermission = schemes.PIN_MESSAGE
	Write            ChatAdminPermission = schemes.WRITE
)

// Administrator представляет администратора чата
type Administrator struct {
	UserId      int64                 `json:"user_id"`
	Name        string                `json:"name"`
	Username    string                `json:"username,omitempty"`
	Permissions []ChatAdminPermission  `json:"permissions,omitempty"`
}

// AdminMembersList представляет список администраторов
type AdminMembersList struct {
	Admins []Administrator `json:"admins"`
	Marker *int64          `json:"marker"`
}

// ChatAdmin представляет администратора для назначения
type ChatAdmin struct {
	UserId      int64                 `json:"user_id"`
	Permissions []ChatAdminPermission `json:"permissions,omitempty"`
}

// ChatAdminsList представляет список администраторов для назначения
type ChatAdminsList struct {
	Admins []ChatAdmin `json:"admins"`
}

// AdminsAPI предоставляет методы для работы с администраторами чатов
type AdminsAPI struct {
	api *maxbot.Api
}

// NewAdminsAPI создает новый экземпляр AdminsAPI
func NewAdminsAPI(api *maxbot.Api) *AdminsAPI {
	return &AdminsAPI{api: api}
}

// GetChatAdmins возвращает список всех администраторов чата
// GET /chats/{chatId}/members/admins
func (a *AdminsAPI) GetChatAdmins(ctx context.Context, chatID int64) (*AdminMembersList, error) {
	client := getClient(a.api)
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(AdminMembersList)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodGet, fmt.Sprintf("chats/%d/members/admins", chatID), values, false, nil)
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

// AddChatAdmins назначает администраторов чата
// POST /chats/{chatId}/members/admins
func (a *AdminsAPI) AddChatAdmins(ctx context.Context, chatID int64, admins []ChatAdmin) (*schemes.SimpleQueryResult, error) {
	client := getClient(a.api)
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	requestBody := ChatAdminsList{Admins: admins}
	result := new(schemes.SimpleQueryResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodPost, fmt.Sprintf("chats/%d/members/admins", chatID), values, false, requestBody)
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

// RemoveChatAdmin отменяет права администратора у пользователя в чате
// DELETE /chats/{chatId}/members/admins/{userId}
func (a *AdminsAPI) RemoveChatAdmin(ctx context.Context, chatID int64, userID int64) (*schemes.SimpleQueryResult, error) {
	client := getClient(a.api)
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(schemes.SimpleQueryResult)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodDelete, fmt.Sprintf("chats/%d/members/admins/%d", chatID, userID), values, false, nil)
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

