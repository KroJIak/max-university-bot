package api

import (
	"context"
	"fmt"
	"io"
	"net/url"
	"reflect"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
)

// httpClient обертка для доступа к методам клиента через рефлексию
type httpClient struct {
	client interface{}
}

// getClient получает внутренний клиент из API через рефлексию
func getClient(api *maxbot.Api) *httpClient {
	// Используем рефлексию для доступа к приватному полю client
	apiValue := reflect.ValueOf(api).Elem()
	clientField := apiValue.FieldByName("client")
	if !clientField.IsValid() || clientField.IsNil() {
		return nil
	}

	// Получаем указатель на client
	clientPtr := clientField.Interface()
	return &httpClient{client: clientPtr}
}

// request выполняет HTTP запрос используя внутренний клиент
func (hc *httpClient) request(ctx context.Context, method, path string, query url.Values, reset bool, body interface{}) (io.ReadCloser, error) {
	// Используем рефлексию для вызова метода request
	clientValue := reflect.ValueOf(hc.client)
	requestMethod := clientValue.MethodByName("request")
	if !requestMethod.IsValid() {
		return nil, fmt.Errorf("request method not found")
	}

	// Подготавливаем параметры
	args := []reflect.Value{
		reflect.ValueOf(ctx),
		reflect.ValueOf(method),
		reflect.ValueOf(path),
		reflect.ValueOf(query),
		reflect.ValueOf(reset),
		reflect.ValueOf(body),
	}

	// Вызываем метод
	results := requestMethod.Call(args)
	if len(results) != 2 {
		return nil, fmt.Errorf("unexpected number of return values")
	}

	// Проверяем ошибку
	if !results[1].IsNil() {
		err := results[1].Interface().(error)
		return nil, err
	}

	// Возвращаем ReadCloser
	readCloser, ok := results[0].Interface().(io.ReadCloser)
	if !ok {
		return nil, fmt.Errorf("unexpected return type")
	}

	return readCloser, nil
}

