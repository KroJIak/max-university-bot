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
	"time"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// PagesAPI предоставляет методы для отображения страниц
type PagesAPI struct {
	api         *api.API
	keyboards   *keyboards.Builder
	universityAPI *services.UniversityAPIClient
}

// NewPagesAPI создает новый экземпляр PagesAPI
func NewPagesAPI(api *api.API, universityAPIURL string) *PagesAPI {
	return &PagesAPI{
		api:         api,
		keyboards:   keyboards.NewBuilder(api.Api),
		universityAPI: services.NewUniversityAPIClient(universityAPIURL),
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
		if tab == "tomorrow" {
			scheduleDate = "завтра, " + tomorrowWeekday
		} else if tab == "afterTomorrow" {
			scheduleDate = "послезавтра, " + afterTomorrowWeekday
		} else {
			scheduleDate = "сегодня, " + todayWeekday
		}
		
		text += utils.FormatSection("Расписание") + " _(" + scheduleDate + ")_\n"
		text += utils.FormatSeparator(width) + "\n"
		text += "Занятия на этот день отсутствуют\n"
		keyboard := p.keyboards.MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday, tab)
		return text, keyboard
	}

	// Получаем режим подгруппы пользователя
	subgroupMode := services.GetSubgroupMode(userID)
	
	// Распределяем занятия по дням с учетом настроек подгруппы
	scheduleByDate := p.groupScheduleByDate(scheduleResp.Schedule, today, tomorrow, afterTomorrow, subgroupMode)
	
	// Определяем дату и получаем занятия для выбранного дня
	var scheduleDate string
	var scheduleItems []string
	
	if tab == "tomorrow" {
		scheduleDate = "завтра, " + tomorrowWeekday
		scheduleItems = p.formatScheduleItemsNew(scheduleByDate[tomorrow.Format("02.01.2006")])
	} else if tab == "afterTomorrow" {
		scheduleDate = "послезавтра, " + afterTomorrowWeekday
		scheduleItems = p.formatScheduleItemsNew(scheduleByDate[afterTomorrow.Format("02.01.2006")])
	} else {
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

	keyboard := p.keyboards.MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday, tab)
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
		typeStr := item.Type
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
	keyboard := p.keyboards.ServicesMenuWithData(servicesList, platformsList)
	
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
	
	keyboard := p.keyboards.ProfileMenu(subgroupModeStr)
	return text, keyboard
}

// HandleCallback обрабатывает callback от кнопок
func (p *PagesAPI) HandleCallback(ctx context.Context, callback schemes.Callback, userID int64, originalMessage *schemes.Message) error {
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
		// Для остальных действий показываем главную страницу
		newText, newKeyboard = p.buildMainPageText(ctx, userID, "today")
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
		Text:     newText,
		Format:   "markdown",
		Attachments: []interface{}{schemes.NewInlineKeyboardAttachmentRequest(newKeyboard.Build())},
	}

	// Отвечаем на callback с обновленным сообщением
	answer := &schemes.CallbackAnswer{
		Message: newMessageBody,
	}
	
	_, err := p.api.Messages.AnswerOnCallback(ctx, callback.CallbackID, answer)
	if err != nil {
		log.Printf("Error answering callback: %v", err)
		// Если редактирование не удалось, отправляем новое сообщение
		_, err = p.api.Messages.Send(ctx, newMsg)
	}
	
	return err
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

