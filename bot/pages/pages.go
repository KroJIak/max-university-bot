package pages

import (
	"context"
	"fmt"
	"log"
	"max-bot/api"
	"max-bot/keyboards"
	"max-bot/services"
	"max-bot/types"
	"max-bot/utils"
	"strings"
	"time"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// PagesAPI предоставляет методы для отображения страниц
type PagesAPI struct {
	api           *api.API
	keyboards     *keyboards.Builder
	universityAPI *services.UniversityAPIClient
	webAppURL     string
}

// NewPagesAPI создает новый экземпляр PagesAPI
func NewPagesAPI(api *api.API, universityAPIURL string, webAppURL string) *PagesAPI {
	return &PagesAPI{
		api:           api,
		keyboards:     keyboards.NewBuilder(api.Api),
		universityAPI: services.NewUniversityAPIClient(universityAPIURL),
		webAppURL:     webAppURL,
	}
}

// ShowMainPage показывает главную страницу
func (p *PagesAPI) ShowMainPage(ctx context.Context, userID int64, activeTab ...string) error {
	tab := "today"
	if len(activeTab) > 0 {
		tab = activeTab[0]
	}

	text, keyboard := p.buildMainPageText(ctx, userID, tab)

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(keyboard)

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowServicesPage показывает страницу сервисов
func (p *PagesAPI) ShowServicesPage(ctx context.Context, userID int64) error {
	text, keyboard := p.buildServicesPageText(ctx, userID)

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(keyboard)

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// GetStudentStatus получает статус студента (обертка над universityAPI)
func (p *PagesAPI) GetStudentStatus(ctx context.Context, userID int64) (*services.StudentStatusResponse, error) {
	return p.universityAPI.GetStudentStatus(ctx, userID)
}

// ShowAuthRequiredPage показывает страницу с требованием авторизации
func (p *PagesAPI) ShowAuthRequiredPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Авторизация") + "\n\n"
	text += "*Для использования бота необходимо авторизоваться в системе.*\n\n"
	text += "Пожалуйста, войдите в веб-приложение для авторизации."

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown")

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowProfilePage показывает страницу профиля
func (p *PagesAPI) ShowProfilePage(ctx context.Context, userID int64) error {
	text, keyboard := p.buildProfilePageText(ctx, userID)

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(keyboard)

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowSchedulePage показывает страницу расписания
func (p *PagesAPI) ShowSchedulePage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Расписание") + "\n\n"

	// TODO: Получить расписание из API
	today := time.Now()
	text += "*" + formatDate(today) + "*\n"
	text += "Расписание будет добавлено после подключения API\n\n"
	text += "Выберите действие:"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowNewsPage показывает страницу новостей
func (p *PagesAPI) ShowNewsPage(ctx context.Context, userID int64) error {
	width := 22
	text := utils.FormatHeader("Новости") + "\n\n"

	// TODO: Получить новости из API
	text += utils.FormatListHeader("Последние новости")
	text += utils.FormatSeparator(width) + "\n\n"
	text += utils.FormatNewsItem(1, "Стартует зимний интенсив по Python", "Институт цифровых технологий · 2 дек.") + "\n\n"
	text += utils.FormatNewsItem(2, "Команда ЧГУ победила в хакатоне «Витязь»", "Пресс-служба ЧГУ · 30 нояб.") + "\n\n"
	text += utils.FormatNewsItem(3, "Запущена запись на весенний отбор в акселератор", "Центр предпринимательства · 28 нояб.") + "\n\n"
	text += utils.FormatSeparator(width) + "\n"
	text += "_Новости будут обновляться автоматически_"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowTeachersPage показывает страницу преподавателей
func (p *PagesAPI) ShowTeachersPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Преподаватели") + "\n\n"

	// TODO: Получить список преподавателей из API
	text += "*Список преподавателей:*\n\n"
	text += "1. Петров П.П. - Правоведение\n"
	text += "2. Иванова И.И. - Физика\n"
	text += "3. Сидоров С.С. - Математическая логика\n\n"
	text += "Выберите преподавателя для подробной информации"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowContactsPage показывает страницу контактов
func (p *PagesAPI) ShowContactsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Контакты") + "\n\n"

	// TODO: Получить контакты из API
	text += "*Важные контакты:*\n\n"
	text += "📞 Приёмная комиссия: +7 (XXX) XXX-XX-XX\n"
	text += "📧 Email: info@university.ru\n\n"
	text += "Дополнительные контакты будут добавлены"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowMapsPage показывает страницу карт
func (p *PagesAPI) ShowMapsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Карта") + "\n\n"
	text += "Интерактивная карта кампуса будет доступна после подключения API"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowChatsPage показывает страницу чатов
func (p *PagesAPI) ShowChatsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Чаты") + "\n\n"

	// TODO: Получить список чатов из API
	text += "*Активные чаты:*\n\n"
	text += "1. Общий чат группы\n"
	text += "2. Чат с преподавателем\n\n"
	text += "Список чатов будет обновляться автоматически"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowDebtsPage показывает страницу долгов
func (p *PagesAPI) ShowDebtsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Долги") + "\n\n"

	// TODO: Получить информацию о долгах из API
	text += "*Ваши долги:*\n\n"
	text += "На данный момент у вас нет задолженностей ✅"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowGradebookPage показывает страницу зачетки
func (p *PagesAPI) ShowGradebookPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Зачетка") + "\n\n"

	// TODO: Получить информацию о зачетке из API
	text += "*Ваши оценки:*\n\n"
	text += "Информация о зачетке будет доступна после подключения API"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowNotificationsPage показывает страницу уведомлений
func (p *PagesAPI) ShowNotificationsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Уведомления") + "\n\n"

	// TODO: Получить уведомления из API
	text += "*Новые уведомления:*\n\n"
	text += "Новых уведомлений нет"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowThemePage показывает страницу тем
func (p *PagesAPI) ShowThemePage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Тема") + "\n\n"
	text += "Выберите тему оформления:\n\n"
	text += "• Светлая\n"
	text += "• Темная\n"
	text += "• Автоматическая"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// ShowPlatformsPage показывает страницу платформ
func (p *PagesAPI) ShowPlatformsPage(ctx context.Context, userID int64) error {
	text := utils.FormatHeader("Платформы") + "\n\n"

	// TODO: Получить список платформ из API
	text += "*Доступные платформы:*\n\n"
	text += "1. Курсы\n"
	text += "2. Портфолио\n"
	text += "3. Расписание\n"
	text += "4. Услуги\n\n"
	text += "Платформы будут обновляться автоматически"

	msg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(text).
		SetFormat("markdown").
		AddKeyboard(p.keyboards.BackMenu())

	_, err := p.api.Messages.Send(ctx, msg)
	return err
}

// buildMainPageText строит текст для главной страницы
func (p *PagesAPI) buildMainPageText(ctx context.Context, userID int64, activeTab string) (string, *maxbot.Keyboard) {
	today := time.Now()
	tomorrow := today.AddDate(0, 0, 1)
	afterTomorrow := today.AddDate(0, 0, 2)

	weekdays := []string{"вс", "пн", "вт", "ср", "чт", "пт", "сб"}
	todayWeekday := weekdays[today.Weekday()]
	tomorrowWeekday := weekdays[tomorrow.Weekday()]
	afterTomorrowWeekday := weekdays[afterTomorrow.Weekday()]

	// Определяем активный таб (по умолчанию сегодня)
	tab := "today"
	if activeTab != "" {
		tab = activeTab
	}

	width := 22 // Ширина для выравнивания

	text := utils.FormatHeader("Главная") + "\n\n"

	// Запрашиваем расписание на 3 дня (сегодня + 2 дня вперед)
	dateRange := services.FormatDateRange(today, afterTomorrow)
	scheduleResp, err := p.universityAPI.GetSchedule(ctx, userID, dateRange)
	if err != nil {
		log.Printf("Error getting schedule from API: %v", err)
		// Если ошибка, показываем пустое расписание для всех дней
		var scheduleDate string
		switch tab {
		case "tomorrow":
			scheduleDate = "завтра, " + tomorrowWeekday
		case "afterTomorrow":
			scheduleDate = "послезавтра, " + afterTomorrowWeekday
		default:
			scheduleDate = "сегодня, " + todayWeekday
		}

		text += utils.FormatSection("Расписание") + " _(" + scheduleDate + ")_\n"
		text += utils.FormatSeparator(width) + "\n"
		text += "Занятия на этот день отсутствуют\n"
		keyboard := p.keyboards.MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday, tab, p.webAppURL)
		return text, keyboard
	}

	// Получаем режим подгруппы пользователя
	subgroupMode := services.GetSubgroupMode(userID)

	// Распределяем занятия по дням с учетом настроек подгруппы
	scheduleByDate := p.groupScheduleByDate(scheduleResp.Schedule, today, tomorrow, afterTomorrow, subgroupMode)

	// Определяем дату и получаем занятия для выбранного дня
	var scheduleDate string
	var scheduleItems []string

	switch tab {
	case "tomorrow":
		scheduleDate = "завтра, " + tomorrowWeekday
		scheduleItems = p.formatScheduleItemsNew(scheduleByDate[tomorrow.Format("02.01.2006")])
	case "afterTomorrow":
		scheduleDate = "послезавтра, " + afterTomorrowWeekday
		scheduleItems = p.formatScheduleItemsNew(scheduleByDate[afterTomorrow.Format("02.01.2006")])
	default:
		// Сегодня (по умолчанию)
		scheduleDate = "сегодня, " + todayWeekday
		scheduleItems = p.formatScheduleItemsNew(scheduleByDate[today.Format("02.01.2006")])
	}

	// Расписание
	text += utils.FormatSection("Расписание") + " _(" + scheduleDate + ")_\n\n"

	// Добавляем элементы расписания
	if len(scheduleItems) == 0 {
		text += "Занятия на этот день отсутствуют\n"
	} else {
		for i, item := range scheduleItems {
			text += item
			if i < len(scheduleItems)-1 {
				// Разделитель между занятиями
				text += "\n" + utils.FormatSeparator(width) + "\n"
			}
		}
	}

	keyboard := p.keyboards.MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday, tab, p.webAppURL)
	return text, keyboard
}

// groupScheduleByDate группирует занятия по датам с учетом настроек подгруппы
func (p *PagesAPI) groupScheduleByDate(items []services.ScheduleItem, today, tomorrow, afterTomorrow time.Time, subgroupMode services.SubgroupMode) map[string][]services.ScheduleItem {
	result := make(map[string][]services.ScheduleItem)

	// Инициализируем пустые списки для всех трех дней
	result[today.Format("02.01.2006")] = []services.ScheduleItem{}
	result[tomorrow.Format("02.01.2006")] = []services.ScheduleItem{}
	result[afterTomorrow.Format("02.01.2006")] = []services.ScheduleItem{}

	// Распределяем занятия по датам с фильтрацией по подгруппам
	for _, item := range items {
		// Парсим дату из формата "15.11.2025"
		itemDate, err := time.Parse("02.01.2006", item.Date)
		if err != nil {
			log.Printf("Error parsing date %s: %v", item.Date, err)
			continue
		}

		// Определяем, к какому дню относится занятие
		dateKey := itemDate.Format("02.01.2006")
		if dateKey == today.Format("02.01.2006") ||
			dateKey == tomorrow.Format("02.01.2006") ||
			dateKey == afterTomorrow.Format("02.01.2006") {
			// Фильтруем по настройкам подгруппы
			shouldInclude := false

			// Получаем подгруппу из поля undergruop или audience
			undergroup := item.Undergroup
			audience := item.Audience

			// Определяем, является ли пара общей
			isCommonPair := false
			if undergroup == "" {
				// Если undergroup пустой, проверяем audience
				if audience == "" || audience == "full" || audience == "Full" || audience == "FULL" {
					isCommonPair = true
				}
			}

			// Применяем фильтр
			switch subgroupMode {
			case services.SubgroupModeFull:
				// Вся группа - показываем все пары
				shouldInclude = true
			case services.SubgroupModeGroup1:
				// Подгруппа 1 - показываем общие и подгруппу 1
				if isCommonPair {
					shouldInclude = true
				} else {
					// Проверяем различные варианты названия подгруппы 1
					shouldInclude = undergroup == "Подгруппа 1" || undergroup == "подгруппа 1" || undergroup == "1" ||
						audience == "subgroup1" || audience == "Subgroup1" || audience == "SUBGROUP1"
				}
			case services.SubgroupModeGroup2:
				// Подгруппа 2 - показываем общие и подгруппу 2
				if isCommonPair {
					shouldInclude = true
				} else {
					// Проверяем различные варианты названия подгруппы 2
					shouldInclude = undergroup == "Подгруппа 2" || undergroup == "подгруппа 2" || undergroup == "2" ||
						audience == "subgroup2" || audience == "Subgroup2" || audience == "SUBGROUP2"
				}
			default:
				shouldInclude = true
			}

			if shouldInclude {
				result[dateKey] = append(result[dateKey], item)
			}
		}
	}

	return result
}

// formatScheduleItemsNew преобразует элементы расписания из API в новый формат (две строки)
func (p *PagesAPI) formatScheduleItemsNew(items []services.ScheduleItem) []string {
	result := make([]string, 0, len(items))

	// Не сортируем - бэк уже возвращает в правильном порядке
	for _, item := range items {
		// Определяем тип занятия (сокращенная форма)
		var typeStr string
		switch item.Type {
		case "lecture":
			typeStr = "ЛК"
		case "practice":
			typeStr = "ПР"
		case "laboratory":
			typeStr = "ЛБ"
		default:
			typeStr = item.Type
		}

		// Определяем место и примечание
		room := item.Room
		note := item.Note

		// Если есть undergroup, добавляем его в note
		if item.Undergroup != "" && note == "" {
			note = item.Undergroup
		}

		// Форматируем элемент расписания в новом формате
		formatted := utils.FormatScheduleItemNew(item.Start, item.End, item.Title, typeStr, room, note)
		result = append(result, formatted)
	}

	return result
}

// buildServicesPageText строит текст и клавиатуру для страницы сервисов
func (p *PagesAPI) buildServicesPageText(ctx context.Context, userID int64) (string, *maxbot.Keyboard) {
	text := utils.FormatHeader("Сервисы") + "\n\n"

	// Получаем сервисы и платформы из API
	servicesResp, errServices := p.universityAPI.GetServices(ctx, userID)
	platformsResp, errPlatforms := p.universityAPI.GetPlatforms(ctx, userID)

	if errServices != nil {
		log.Printf("Error getting services from API: %v", errServices)
	}
	if errPlatforms != nil {
		log.Printf("Error getting platforms from API: %v", errPlatforms)
	}

	var servicesList []services.Service
	var platformsList []services.Platform

	if servicesResp != nil && servicesResp.Success {
		servicesList = servicesResp.Services
	}
	if platformsResp != nil && platformsResp.Success {
		platformsList = platformsResp.Platforms
	}

	// Создаем клавиатуру с сервисами и платформами
	keyboard := p.keyboards.ServicesMenuWithData(servicesList, platformsList, p.webAppURL)

	return text, keyboard
}

// buildProfilePageText строит текст для страницы профиля
func (p *PagesAPI) buildProfilePageText(ctx context.Context, userID int64) (string, *maxbot.Keyboard) {
	width := 22

	// Получаем режим подгруппы
	subgroupMode := services.GetSubgroupMode(userID)
	subgroupModeStr := string(subgroupMode)

	// Получаем данные из API
	personalDataResp, errPersonalData := p.universityAPI.GetPersonalData(ctx, userID)
	userResp, errUser := p.universityAPI.GetUser(ctx, userID)

	text := ""

	// Название университета
	var universityName string
	if errUser == nil && userResp != nil {
		universityResp, errUniversity := p.universityAPI.GetUniversity(ctx, userResp.UniversityID)
		if errUniversity == nil && universityResp != nil {
			universityName = universityResp.Name
		}
	}

	text += utils.FormatSeparator(width) + "\n"
	if universityName != "" {
		text += universityName + "\n"
	}
	text += utils.FormatSeparator(width) + "\n"

	// ФИО и статус
	var fullName, course string
	if errPersonalData == nil && personalDataResp != nil && personalDataResp.Data != nil {
		if fam, ok := personalDataResp.Data["fam"].(string); ok {
			fullName = fam
		}
		if name, ok := personalDataResp.Data["name"].(string); ok {
			if fullName != "" {
				fullName += " " + name
			} else {
				fullName = name
			}
		}
		if patronymic, ok := personalDataResp.Data["patronymic"].(string); ok {
			if fullName != "" {
				fullName += " " + patronymic
			} else {
				fullName = patronymic
			}
		}
		if c, ok := personalDataResp.Data["course"].(string); ok {
			course = c
		}
	}

	if fullName != "" {
		text += fullName + "\n"
	}
	if course != "" {
		text += "Студент, " + course + " курс\n"
	}
	text += utils.FormatSeparator(width) + "\n"

	// Зачетка и долги
	var avgGrade, debts string
	if errPersonalData == nil && personalDataResp != nil && personalDataResp.Data != nil {
		// TODO: Получить средний балл из API
		avgGrade = "4.90"
		// TODO: Получить долги из API
		debts = "0"
	} else {
		avgGrade = "-"
		debts = "-"
	}

	text += "Зачётка\n"
	text += "🟦 " + avgGrade + " ср. балл\n"
	text += "\n"
	text += "Долги\n"
	text += "😎 " + debts + " долгов\n"
	text += utils.FormatSeparator(width) + "\n"

	// Дополнительная информация
	if errPersonalData == nil && personalDataResp != nil && personalDataResp.Data != nil {
		if faculty, ok := personalDataResp.Data["faculty"].(string); ok && faculty != "" {
			text += "--Факультет--\n"
			text += faculty + "\n"
		}
		if spec, ok := personalDataResp.Data["spec"].(string); ok && spec != "" {
			text += "\n"
			text += "--Специальность--\n"
			text += spec + "\n"
		}
		if profile, ok := personalDataResp.Data["profile"].(string); ok && profile != "" {
			text += "\n"
			text += "--Профиль--\n"
			text += profile + "\n"
		}
		if group, ok := personalDataResp.Data["group"].(string); ok && group != "" {
			text += "\n"
			text += "--Группа--\n"
			text += group + "\n"
		}
		if zachetka, ok := personalDataResp.Data["zachetka"].(string); ok && zachetka != "" {
			text += "\n"
			text += "--Номер зачётки--\n"
			text += zachetka + "\n"
		}
	}

	text += utils.FormatSeparator(width) + "\n"

	// MAX ID и контакты
	text += "MAX ID: " + fmt.Sprintf("%d", userID) + "\n"

	if errPersonalData == nil && personalDataResp != nil && personalDataResp.Data != nil {
		if phone, ok := personalDataResp.Data["phone"].(string); ok && phone != "" {
			text += "Телефон: " + phone + "\n"
		}
		if birthday, ok := personalDataResp.Data["birthday"].(string); ok && birthday != "" {
			text += "Дата рождения: " + birthday + "\n"
		}
	}

	keyboard := p.keyboards.ProfileMenu(subgroupModeStr, p.webAppURL)
	return text, keyboard
}

// HandleCallback обрабатывает callback от кнопок
func (p *PagesAPI) HandleCallback(ctx context.Context, callback schemes.Callback, userID int64, originalMessage *schemes.Message) error {
	// Проверяем, залогинен ли пользователь в системе
	statusResp, err := p.GetStudentStatus(ctx, userID)
	if err != nil {
		log.Printf("Failed to check student status: %v", err)
		// В случае ошибки показываем страницу авторизации
		return p.ShowAuthRequiredPage(ctx, userID)
	}

	// Если пользователь не залогинен, показываем страницу авторизации
	if statusResp == nil || !statusResp.IsLinked {
		return p.ShowAuthRequiredPage(ctx, userID)
	}

	// Используем Payload для определения действия (CallbackID - это идентификатор клавиатуры)
	action := types.NavigationAction(callback.Payload)

	log.Printf("Processing callback: payload=%s, callback_id=%s", callback.Payload, callback.CallbackID)

	// Генерируем новый текст и клавиатуру в зависимости от действия
	var newText string
	var newKeyboard *maxbot.Keyboard

	switch action {
	case types.ActionOpenMain, types.ActionHome:
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "today")
	case types.ActionOpenServices:
		newText, newKeyboard = p.buildServicesPageText(ctx, userID)
	case types.ActionOpenProfile:
		newText, newKeyboard = p.buildProfilePageText(ctx, userID)
	case types.ActionSubgroupFull:
		services.SetSubgroupMode(userID, services.SubgroupModeFull)
		newText, newKeyboard = p.buildProfilePageText(ctx, userID)
	case types.ActionSubgroupGroup1:
		services.SetSubgroupMode(userID, services.SubgroupModeGroup1)
		newText, newKeyboard = p.buildProfilePageText(ctx, userID)
	case types.ActionSubgroupGroup2:
		services.SetSubgroupMode(userID, services.SubgroupModeGroup2)
		newText, newKeyboard = p.buildProfilePageText(ctx, userID)
	case types.ActionScheduleToday:
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "today")
	case types.ActionScheduleTomorrow:
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "tomorrow")
	case types.ActionScheduleAfterTomorrow:
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "afterTomorrow")
	case types.ActionBack:
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "today")
	default:
		// Обработка декоративной кнопки веб-приложения
		if callback.Payload == "web_app_info" {
			// Просто показываем уведомление без изменения сообщения
			answer := &schemes.CallbackAnswer{
				Notification: "Веб-приложение доступно по ссылке: " + p.webAppURL,
			}
			_, err := p.api.Messages.AnswerOnCallback(ctx, callback.CallbackID, answer)
			return err
		}

		// Обработка преподавателей
		payload := callback.Payload
		log.Printf("Processing teacher callback: payload=%s", payload)
		if payload == "service_teachers" {
			// Показываем алфавит
			log.Printf("Showing teachers alphabet")
			newText, newKeyboard = p.buildTeachersAlphabetPage(ctx, userID)
		} else if strings.HasPrefix(payload, "teacher_letter_") {
			// Формат: teacher_letter_А (буква кириллицы)
			letter := payload[len("teacher_letter_"):]
			log.Printf("Processing teacher letter: %s", letter)
			// Преобразуем букву в верхний регистр для сравнения
			letterRunes := []rune(letter)
			if len(letterRunes) > 0 {
				letter = string([]rune{letterRunes[0]})
			}
			log.Printf("Showing teachers list for letter: %s", letter)
			newText, newKeyboard = p.buildTeachersListPage(ctx, userID, letter, 0)
		} else if strings.HasPrefix(payload, "teacher_page_") {
			// Формат: teacher_page_А_0 (буква и номер страницы)
			parts := payload[len("teacher_page_"):]
			// Находим последний подчеркивание
			lastUnderscore := -1
			for i := len(parts) - 1; i >= 0; i-- {
				if parts[i] == '_' {
					lastUnderscore = i
					break
				}
			}
			if lastUnderscore > 0 {
				letter := parts[:lastUnderscore]
				// Преобразуем букву в верхний регистр
				letterRunes := []rune(letter)
				if len(letterRunes) > 0 {
					letter = string([]rune{letterRunes[0]})
				}
				var page int
				fmt.Sscanf(parts[lastUnderscore+1:], "%d", &page)
				newText, newKeyboard = p.buildTeachersListPage(ctx, userID, letter, page)
			}
		} else if strings.HasPrefix(payload, "teacher_info_") {
			// Формат: teacher_info_tech123
			teacherID := payload[len("teacher_info_"):]
			newText, newKeyboard, _ = p.buildTeacherInfoPage(ctx, userID, teacherID)
		} else if payload == "service_maps" || payload == "open_maps" {
			// Показываем список корпусов
			newText, newKeyboard = p.buildMapsListPage(ctx, userID, 0)
		} else if strings.HasPrefix(payload, "maps_page_") {
			// Формат: maps_page_0 (номер страницы)
			var page int
			fmt.Sscanf(payload[len("maps_page_"):], "%d", &page)
			newText, newKeyboard = p.buildMapsListPage(ctx, userID, page)
		} else if strings.HasPrefix(payload, "map_info_") {
			// Формат: map_info_0 (индекс корпуса)
			var index int
			fmt.Sscanf(payload[len("map_info_"):], "%d", &index)
			newText, newKeyboard = p.buildMapInfoPage(ctx, userID, index)
		} else {
			// Для остальных действий показываем главную страницу
			newText, newKeyboard = p.buildMainPageText(ctx, userID, "today")
		}
	}

	// Создаем новое сообщение для редактирования
	newMsg := p.api.Messages.NewMessage().
		SetUser(userID).
		SetText(newText).
		SetFormat("markdown").
		AddKeyboard(newKeyboard)

	// Получаем NewMessageBody из сообщения (нужно получить доступ к внутреннему полю)
	// Создаем NewMessageBody вручную
	newMessageBody := &schemes.NewMessageBody{
		Text:        newText,
		Format:      "markdown",
		Attachments: []interface{}{schemes.NewInlineKeyboardAttachmentRequest(newKeyboard.Build())},
	}

	// Отвечаем на callback с обновленным сообщением
	answer := &schemes.CallbackAnswer{
		Message: newMessageBody,
	}

	// Логируем информацию для отладки
	log.Printf("Answering callback: callback_id=%s, text_length=%d, attachments_count=%d",
		callback.CallbackID, len(newText), len(newMessageBody.Attachments))

	_, callbackErr := p.api.Messages.AnswerOnCallback(ctx, callback.CallbackID, answer)
	if callbackErr != nil {
		log.Printf("Error answering callback: %v", callbackErr)
		// Если редактирование не удалось (404 может означать, что callback_id устарел),
		// отправляем новое сообщение
		log.Printf("Sending new message instead of editing")
		_, sendErr := p.api.Messages.Send(ctx, newMsg)
		if sendErr != nil {
			log.Printf("Error sending new message: %v", sendErr)
			return sendErr
		}
	}

	return nil
}

// formatDate форматирует дату в читаемый формат
func formatDate(t time.Time) string {
	weekdays := []string{"Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"}
	months := []string{"января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"}

	weekday := weekdays[t.Weekday()]
	day := t.Day()
	month := months[t.Month()-1]
	year := t.Year()

	return fmt.Sprintf("%s, %d %s %d", weekday, day, month, year)
}

// formatTeacherName форматирует имя преподавателя в формат "Фамилия И.О."
func formatTeacherName(fullName string) string {
	parts := []rune(fullName)
	words := []string{}
	currentWord := ""

	for _, r := range parts {
		if r == ' ' {
			if currentWord != "" {
				words = append(words, currentWord)
				currentWord = ""
			}
		} else {
			currentWord += string(r)
		}
	}
	if currentWord != "" {
		words = append(words, currentWord)
	}

	if len(words) == 0 {
		return fullName
	}

	// Если есть хотя бы фамилия и имя
	if len(words) >= 2 {
		surname := words[0]
		initials := ""
		// Берем первые буквы всех остальных слов (имя, отчество)
		for i := 1; i < len(words) && i < 4; i++ {
			wordRunes := []rune(words[i])
			if len(wordRunes) > 0 {
				initials += string(wordRunes[0]) + "."
			}
		}
		if initials != "" {
			return fmt.Sprintf("%s %s", surname, initials)
		}
		return surname
	}

	return fullName
}

// buildTeachersAlphabetPage показывает алфавит для поиска преподавателей
func (p *PagesAPI) buildTeachersAlphabetPage(ctx context.Context, userID int64) (string, *maxbot.Keyboard) {
	text := utils.FormatHeader("Преподаватели") + "\n\n"
	text += "*Поиск преподавателя по ФИО:*\n"
	text += "Пример: если надо найти Обломов Игорь Александрович, надо нажать на О\n"

	keyboard := p.keyboards.TeachersAlphabetMenu(p.webAppURL)

	return text, keyboard
}

// buildTeachersListPage показывает список преподавателей по букве с пагинацией
func (p *PagesAPI) buildTeachersListPage(ctx context.Context, userID int64, letter string, page int) (string, *maxbot.Keyboard) {
	// Получаем список всех преподавателей
	teachersResp, err := p.universityAPI.GetTeachers(ctx, userID)
	if err != nil {
		log.Printf("Failed to get teachers: %v", err)
		text := utils.FormatHeader("Ошибка") + "\n\n"
		text += "Не удалось загрузить список преподавателей."
		// Используем главное меню
		_, keyboard := p.buildMainPageText(ctx, userID, "today")
		return text, keyboard
	}

	// Фильтруем преподавателей по первой букве фамилии
	var filteredTeachers []services.Teacher
	letterUpper := strings.ToUpper(letter)
	for _, teacher := range teachersResp.Teachers {
		// Получаем первую букву фамилии
		firstChar := ""
		if len(teacher.Name) > 0 {
			firstChar = string([]rune(teacher.Name)[0])
			firstChar = strings.ToUpper(firstChar)
		}
		// Сравниваем с учетом регистра
		if firstChar == letterUpper {
			filteredTeachers = append(filteredTeachers, teacher)
		}
	}

	// Пагинация: по 20 преподавателей на страницу
	const pageSize = 20
	totalPages := (len(filteredTeachers) + pageSize - 1) / pageSize

	if totalPages == 0 {
		text := utils.FormatHeader("Преподаватели") + "\n\n"
		text += fmt.Sprintf("*Преподаватели на \"%s\"*\n\n", letter)
		text += "Не найдено преподавателей, начинающихся с этой буквы."
		keyboard := p.keyboards.TeachersAlphabetMenu(p.webAppURL)
		return text, keyboard
	}


	// Корректируем номер страницы
	if page < 0 {
		page = 0
	}
	if page >= totalPages {
		page = totalPages - 1
	}

	// Получаем преподавателей для текущей страницы
	start := page * pageSize
	end := start + pageSize
	if end > len(filteredTeachers) {
		end = len(filteredTeachers)
	}
	pageTeachers := filteredTeachers[start:end]

	// Формируем текст
	text := utils.FormatHeader("Преподаватели") + "\n\n"
	text += fmt.Sprintf("*Преподаватели на \"%s\"*\n\n", letter)

	// Нумеруем преподавателей (номер учитывает страницу)
	globalIndex := page * pageSize
	for i, teacher := range pageTeachers {
		number := globalIndex + i + 1
		// В тексте используем полное ФИО с номером
		text += fmt.Sprintf("%d) %s\n", number, teacher.Name)
	}

	text += fmt.Sprintf("\n_Страница %d из %d_\n", page+1, totalPages)

	// Создаем клавиатуру с кнопками преподавателей и пагинацией
	keyboard := p.keyboards.TeachersListMenu(pageTeachers, letter, page, totalPages, p.webAppURL)

	return text, keyboard
}

// buildTeacherInfoPage показывает детальную информацию о преподавателе
func (p *PagesAPI) buildTeacherInfoPage(ctx context.Context, userID int64, teacherID string) (string, *maxbot.Keyboard, string) {
	// Получаем информацию о преподавателе
	teacherInfoResp, err := p.universityAPI.GetTeacherInfo(ctx, userID, teacherID)
	if err != nil {
		log.Printf("Failed to get teacher info: %v", err)
		text := utils.FormatHeader("Ошибка") + "\n\n"
		text += "Не удалось загрузить информацию о преподавателе."
		keyboard := p.keyboards.TeachersAlphabetMenu(p.webAppURL)
		return text, keyboard, ""
	}

	// Получаем имя преподавателя из списка
	teachersResp, err := p.universityAPI.GetTeachers(ctx, userID)
	var teacherName string
	if err == nil {
		for _, teacher := range teachersResp.Teachers {
			if teacher.ID == teacherID {
				teacherName = teacher.Name
				break
			}
		}
	}

	if teacherName == "" {
		teacherName = "Преподаватель"
	}

	// Формируем текст
	text := utils.FormatHeader("Информация о преподавателе") + "\n\n"
	text += fmt.Sprintf("*%s*\n\n", teacherName)

	if len(teacherInfoResp.Departments) > 0 {
		text += utils.FormatSection("Кафедры") + "\n"
		for _, dept := range teacherInfoResp.Departments {
			text += fmt.Sprintf("• %s\n", dept)
		}
		text += "\n"
	}

	// Создаем клавиатуру с навигацией
	keyboard := p.keyboards.TeacherInfoMenu(p.webAppURL)

	return text, keyboard, ""
}

// buildMapsListPage показывает список корпусов с пагинацией
func (p *PagesAPI) buildMapsListPage(ctx context.Context, userID int64, page int) (string, *maxbot.Keyboard) {
	// Получаем список всех корпусов
	mapsResp, err := p.universityAPI.GetMaps(ctx, userID)
	if err != nil {
		log.Printf("Failed to get maps: %v", err)
		text := utils.FormatHeader("Ошибка") + "\n\n"
		text += "Не удалось загрузить список корпусов."
		// Используем главное меню
		_, keyboard := p.buildMainPageText(ctx, userID, "today")
		return text, keyboard
	}

	buildings := mapsResp.Buildings
	if len(buildings) == 0 {
		text := utils.FormatHeader("Карта") + "\n\n"
		text += "Корпуса не найдены."
		keyboard := p.keyboards.MapsListMenu([]services.Building{}, 0, 0, p.webAppURL)
		return text, keyboard
	}

	// Пагинация: по 20 корпусов на страницу
	const pageSize = 20
	totalPages := (len(buildings) + pageSize - 1) / pageSize

	// Корректируем номер страницы
	if page < 0 {
		page = 0
	}
	if page >= totalPages {
		page = totalPages - 1
	}

	// Получаем корпуса для текущей страницы
	start := page * pageSize
	end := start + pageSize
	if end > len(buildings) {
		end = len(buildings)
	}
	pageBuildings := buildings[start:end]

	// Формируем текст
	text := utils.FormatHeader("Карта") + "\n\n"
	text += "*Корпуса университета*\n\n"

	// Нумеруем корпуса (номер учитывает страницу)
	globalIndex := page * pageSize
	for i, building := range pageBuildings {
		number := globalIndex + i + 1
		text += fmt.Sprintf("%d) %s\n", number, building.Name)
	}

	text += fmt.Sprintf("\n_Страница %d из %d_\n", page+1, totalPages)

	// Создаем клавиатуру с кнопками корпусов и пагинацией
	keyboard := p.keyboards.MapsListMenu(pageBuildings, page, totalPages, p.webAppURL)

	return text, keyboard
}

// buildMapInfoPage показывает информацию о конкретном корпусе с кнопками-ссылками
func (p *PagesAPI) buildMapInfoPage(ctx context.Context, userID int64, buildingIndex int) (string, *maxbot.Keyboard) {
	// Получаем список всех корпусов
	mapsResp, err := p.universityAPI.GetMaps(ctx, userID)
	if err != nil {
		log.Printf("Failed to get maps: %v", err)
		text := utils.FormatHeader("Ошибка") + "\n\n"
		text += "Не удалось загрузить информацию о корпусе."
		keyboard := p.keyboards.MapsListMenu([]services.Building{}, 0, 0, p.webAppURL)
		return text, keyboard
	}

	if buildingIndex < 0 || buildingIndex >= len(mapsResp.Buildings) {
		text := utils.FormatHeader("Ошибка") + "\n\n"
		text += "Корпус не найден."
		keyboard := p.keyboards.MapsListMenu([]services.Building{}, 0, 0, p.webAppURL)
		return text, keyboard
	}

	building := mapsResp.Buildings[buildingIndex]

	// Формируем текст
	text := utils.FormatHeader("Карта") + "\n\n"
	text += fmt.Sprintf("*%s*\n\n", building.Name)

	if building.Latitude != 0 && building.Longitude != 0 {
		text += fmt.Sprintf("Координаты: %.6f, %.6f\n\n", building.Latitude, building.Longitude)
	}

	// Создаем клавиатуру с кнопками-ссылками на карты
	keyboard := p.keyboards.MapInfoMenu(building, p.webAppURL)

	return text, keyboard
}
