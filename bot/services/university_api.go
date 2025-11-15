package services

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

// ScheduleItem представляет одно занятие из расписания
type ScheduleItem struct {
	ID             string `json:"id"`
	Start          string `json:"start"`
	End            string `json:"end"`
	Title          string `json:"title"`
	Type           string `json:"type"`
	Room           string `json:"room"`
	Note           string `json:"note"`
	Audience       string `json:"audience"`
	Date           string `json:"date"`
	Teacher        string `json:"teacher"`
	AdditionalInfo string `json:"additional_info,omitempty"`
	Undergroup     string `json:"undergruop,omitempty"`
}

// ScheduleResponse представляет ответ API с расписанием
type ScheduleResponse struct {
	Success  bool           `json:"success"`
	Schedule []ScheduleItem `json:"schedule"`
	Error    string         `json:"error,omitempty"`
}

// UniversityAPIClient клиент для работы с University API
type UniversityAPIClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewUniversityAPIClient создает новый клиент для University API
func NewUniversityAPIClient(baseURL string) *UniversityAPIClient {
	return &UniversityAPIClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// GetSchedule получает расписание студента за указанный период
func (c *UniversityAPIClient) GetSchedule(ctx context.Context, userID int64, dateRange string) (*ScheduleResponse, error) {
	// Формируем URL запроса
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/schedule", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	// Добавляем query параметры
	q := reqURL.Query()
	q.Set("date_range", dateRange)
	reqURL.RawQuery = q.Encode()

	// Создаем запрос
	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	// Выполняем запрос
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	// Читаем ответ
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Проверяем статус код
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	// Парсим JSON ответ
	var scheduleResp ScheduleResponse
	if err := json.Unmarshal(body, &scheduleResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	// Проверяем на ошибки в ответе
	if !scheduleResp.Success {
		return nil, fmt.Errorf("API returned error: %s", scheduleResp.Error)
	}

	return &scheduleResp, nil
}

// FormatDateRange форматирует даты для date_range параметра (без года)
// dateRange формат: "15.11-17.11"
func FormatDateRange(startDate, endDate time.Time) string {
	startStr := startDate.Format("02.01")
	endStr := endDate.Format("02.01")
	return fmt.Sprintf("%s-%s", startStr, endStr)
}

// FormatDateRangeWithYear форматирует даты с годом (устаревший, используйте FormatDateRange)
func FormatDateRangeWithYear(startDate, endDate time.Time) string {
	return FormatDateRange(startDate, endDate)
}

// Service представляет один сервис
type Service struct {
	Emoji string `json:"emoji"`
	Key   string `json:"key"`
	Name  string `json:"name"`
}

// ServicesResponse представляет ответ API со списком сервисов
type ServicesResponse struct {
	Success  bool      `json:"success"`
	Services []Service `json:"services"`
	Error    string    `json:"error,omitempty"`
}

// Platform представляет одну веб-платформу
type Platform struct {
	Emoji string `json:"emoji"`
	Key   string `json:"key"`
	Name  string `json:"name"`
	URL   string `json:"url"`
}

// PlatformsResponse представляет ответ API со списком платформ
type PlatformsResponse struct {
	Success   bool       `json:"success"`
	Platforms []Platform `json:"platforms"`
	Error     string     `json:"error,omitempty"`
}

// GetServices получает список сервисов студента
func (c *UniversityAPIClient) GetServices(ctx context.Context, userID int64) (*ServicesResponse, error) {
	// Формируем URL запроса
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/services", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	// Создаем запрос
	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	// Выполняем запрос
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	// Читаем ответ
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Проверяем статус код
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	// Парсим JSON ответ
	var servicesResp ServicesResponse
	if err := json.Unmarshal(body, &servicesResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	// Проверяем на ошибки в ответе
	if !servicesResp.Success {
		return nil, fmt.Errorf("API returned error: %s", servicesResp.Error)
	}

	return &servicesResp, nil
}

// GetPlatforms получает список веб-платформ студента
func (c *UniversityAPIClient) GetPlatforms(ctx context.Context, userID int64) (*PlatformsResponse, error) {
	// Формируем URL запроса
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/platforms", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	// Создаем запрос
	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	// Выполняем запрос
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	// Читаем ответ
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Проверяем статус код
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	// Парсим JSON ответ
	var platformsResp PlatformsResponse
	if err := json.Unmarshal(body, &platformsResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	// Проверяем на ошибки в ответе
	if !platformsResp.Success {
		return nil, fmt.Errorf("API returned error: %s", platformsResp.Error)
	}

	return &platformsResp, nil
}

// PersonalDataResponse представляет ответ API с личными данными студента
type PersonalDataResponse struct {
	Success bool                   `json:"success"`
	Data    map[string]interface{} `json:"data"`
	Error   string                 `json:"error,omitempty"`
}

// GetPersonalData получает личные данные студента
func (c *UniversityAPIClient) GetPersonalData(ctx context.Context, userID int64) (*PersonalDataResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/personal_data", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var personalDataResp PersonalDataResponse
	if err := json.Unmarshal(body, &personalDataResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	if !personalDataResp.Success {
		return nil, fmt.Errorf("API returned error: %s", personalDataResp.Error)
	}

	return &personalDataResp, nil
}

// UserResponse представляет ответ API с информацией о пользователе
type UserResponse struct {
	ID           int64  `json:"id"`
	UserID       int64  `json:"user_id"`
	UniversityID int64  `json:"university_id"`
	FirstName    string `json:"first_name"`
	LastName     string `json:"last_name,omitempty"`
	Username     string `json:"username,omitempty"`
}

// GetUser получает информацию о пользователе
func (c *UniversityAPIClient) GetUser(ctx context.Context, userID int64) (*UserResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/users/%d", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var userResp UserResponse
	if err := json.Unmarshal(body, &userResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &userResp, nil
}

// UniversityResponse представляет ответ API с информацией об университете
type UniversityResponse struct {
	ID   int64  `json:"id"`
	Name string `json:"name"`
}

// GetUniversity получает информацию об университете
func (c *UniversityAPIClient) GetUniversity(ctx context.Context, universityID int64) (*UniversityResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/universities/%d", c.baseURL, universityID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var universityResp UniversityResponse
	if err := json.Unmarshal(body, &universityResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &universityResp, nil
}

// StudentStatusResponse представляет ответ API со статусом студента
type StudentStatusResponse struct {
	IsLinked     bool   `json:"is_linked"`
	StudentEmail string `json:"student_email,omitempty"`
	LinkedAt     string `json:"linked_at,omitempty"`
}

// GetStudentStatus получает статус связи пользователя с аккаунтом студента
func (c *UniversityAPIClient) GetStudentStatus(ctx context.Context, userID int64) (*StudentStatusResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/status", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var statusResp StudentStatusResponse
	if err := json.Unmarshal(body, &statusResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &statusResp, nil
}

// Teacher представляет одного преподавателя в списке
type Teacher struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

// TeachersResponse представляет ответ API со списком преподавателей
type TeachersResponse struct {
	Success  bool      `json:"success"`
	Teachers []Teacher `json:"teachers"`
	Error    string    `json:"error,omitempty"`
}

// TeacherInfoResponse представляет ответ API с информацией о преподавателе
type TeacherInfoResponse struct {
	Success    bool     `json:"success"`
	Departments []string `json:"departments"`
	Photo      string   `json:"photo,omitempty"`
	Error      string   `json:"error,omitempty"`
}

// GetTeachers получает список всех преподавателей университета
func (c *UniversityAPIClient) GetTeachers(ctx context.Context, userID int64) (*TeachersResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/teachers", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var teachersResp TeachersResponse
	if err := json.Unmarshal(body, &teachersResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	if !teachersResp.Success {
		return nil, fmt.Errorf("API returned error: %s", teachersResp.Error)
	}

	return &teachersResp, nil
}

// GetTeacherInfo получает информацию о конкретном преподавателе
func (c *UniversityAPIClient) GetTeacherInfo(ctx context.Context, userID int64, teacherID string) (*TeacherInfoResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/teacher/%s", c.baseURL, userID, teacherID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var teacherInfoResp TeacherInfoResponse
	if err := json.Unmarshal(body, &teacherInfoResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	if !teacherInfoResp.Success {
		return nil, fmt.Errorf("API returned error: %s", teacherInfoResp.Error)
	}

	return &teacherInfoResp, nil
}

// Building представляет один корпус с картами
type Building struct {
	Name          string  `json:"name"`
	Latitude      float64 `json:"latitude"`
	Longitude     float64 `json:"longitude"`
	YandexMapURL  string  `json:"yandex_map_url"`
	Gis2MapURL    string  `json:"gis2_map_url"`
	GoogleMapURL  string  `json:"google_map_url"`
}

// MapsResponse представляет ответ API со списком карт корпусов
type MapsResponse struct {
	Buildings []Building `json:"buildings"`
}

// GetMaps получает список всех корпусов университета с картами
func (c *UniversityAPIClient) GetMaps(ctx context.Context, userID int64) (*MapsResponse, error) {
	apiURL := fmt.Sprintf("%s/api/v1/students/%d/maps", c.baseURL, userID)
	reqURL, err := url.Parse(apiURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", reqURL.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var mapsResp MapsResponse
	if err := json.Unmarshal(body, &mapsResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &mapsResp, nil
}
