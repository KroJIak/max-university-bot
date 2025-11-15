package keyboards

import (
	"encoding/json"
	"fmt"
	"max-bot/services"
	"max-bot/types"
	"strings"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// OpenAppButton представляет кнопку для открытия мини-приложения
type OpenAppButton struct {
	schemes.Button
	WebApp    string `json:"web_app,omitempty"`
	ContactId *int64 `json:"contact_id,omitempty"`
}

// Реализуем интерфейс ButtonInterface
func (b OpenAppButton) GetType() schemes.ButtonType {
	return schemes.ButtonType("open_app")
}

func (b OpenAppButton) GetText() string {
	return b.Text
}

// MarshalJSON кастомная сериализация для правильного формата JSON
func (b OpenAppButton) MarshalJSON() ([]byte, error) {
	// Создаем JSON вручную для правильного формата
	result := map[string]interface{}{
		"type":    "open_app",
		"text":    b.Text,
		"web_app": b.WebApp,
	}
	if b.ContactId != nil {
		result["contact_id"] = *b.ContactId
	}
	return json.Marshal(result)
}

// Builder предоставляет методы для создания клавиатур
type Builder struct {
	api *maxbot.Api
}

// NewBuilder создает новый билдер клавиатур
func NewBuilder(api *maxbot.Api) *Builder {
	return &Builder{api: api}
}

// AddOpenApp добавляет декоративную кнопку с текстом "👇 Открыть веб-приложение" без функционала
func (b *Builder) AddOpenApp(row *maxbot.KeyboardRow, text string, intent schemes.Intent, webAppURL string) *maxbot.KeyboardRow {
	if webAppURL == "" {
		return row
	}

	// Добавляем простую callback кнопку с текстом, которая при нажатии ничего не делает
	// (payload будет игнорироваться или показывать уведомление)
	row.AddCallback("👇 Открыть веб-приложение", schemes.DEFAULT, "web_app_info")

	return row
}

// MainMenu создает главное меню (старая версия, для обратной совместимости)
func (b *Builder) MainMenu() *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	keyboard.
		AddRow().
		AddCallback("📋 Расписание", schemes.POSITIVE, string(types.ActionOpenSchedule)).
		AddCallback("📰 Новости", schemes.POSITIVE, string(types.ActionOpenNews))
	keyboard.
		AddRow().
		AddCallback("🔧 Сервисы", schemes.POSITIVE, string(types.ActionOpenServices)).
		AddCallback("👤 Профиль", schemes.POSITIVE, string(types.ActionOpenProfile))
	return keyboard
}

// MainPageMenu создает клавиатуру для главной страницы
func (b *Builder) MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday string, activeTab string, webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Определяем эмоджи для активного/неактивного состояния табов (только день недели)
	var todayText, tomorrowText, afterTomorrowText string
	switch activeTab {
	case "today":
		todayText = "✅ " + todayWeekday
		tomorrowText = tomorrowWeekday
		afterTomorrowText = afterTomorrowWeekday
	case "tomorrow":
		todayText = todayWeekday
		tomorrowText = "✅ " + tomorrowWeekday
		afterTomorrowText = afterTomorrowWeekday
	case "afterTomorrow":
		todayText = todayWeekday
		tomorrowText = tomorrowWeekday
		afterTomorrowText = "✅ " + afterTomorrowWeekday
	default:
		// По умолчанию активна сегодня
		todayText = "✅ " + todayWeekday
		tomorrowText = tomorrowWeekday
		afterTomorrowText = afterTomorrowWeekday
	}

	// Табы для выбора даты расписания
	keyboard.
		AddRow().
		AddCallback(todayText, schemes.POSITIVE, string(types.ActionScheduleToday)).
		AddCallback(tomorrowText, schemes.NEGATIVE, string(types.ActionScheduleTomorrow)).
		AddCallback(afterTomorrowText, schemes.NEGATIVE, string(types.ActionScheduleAfterTomorrow))
	// Навигационное меню (главная активна)
	keyboard.
		AddRow().
		AddCallback("🏠 Главная", schemes.POSITIVE, string(types.ActionHome)).
		AddCallback("🔧 Сервисы", schemes.NEGATIVE, string(types.ActionOpenServices)).
		AddCallback("👤 Профиль", schemes.NEGATIVE, string(types.ActionOpenProfile))

	// Добавляем кнопку веб-приложения внизу, если URL указан
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}

// ServicesMenu создает меню сервисов (старая версия, для обратной совместимости)
func (b *Builder) ServicesMenu() *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	// Основные сервисы
	keyboard.
		AddRow().
		AddCallback("📋 Расписание", schemes.POSITIVE, string(types.ActionOpenSchedule)).
		AddCallback("👩‍🏫 Преподаватели", schemes.POSITIVE, string(types.ActionOpenTeachers))
	keyboard.
		AddRow().
		AddCallback("📞 Контакты", schemes.POSITIVE, string(types.ActionOpenContacts)).
		AddCallback("🗺️ Карта", schemes.POSITIVE, string(types.ActionOpenMaps))
	keyboard.
		AddRow().
		AddCallback("💬 Чаты", schemes.POSITIVE, string(types.ActionOpenChats))
	keyboard.
		AddRow().
		AddCallback("🌐 Платформы", schemes.POSITIVE, string(types.ActionOpenPlatforms))
	// Навигация (сервисы активны)
	keyboard.
		AddRow().
		AddCallback("⬅️ Назад", schemes.NEGATIVE, string(types.ActionBack)).
		AddCallback("🏠 Главная", schemes.NEGATIVE, string(types.ActionHome)).
		AddCallback("✅ Сервисы", schemes.POSITIVE, string(types.ActionOpenServices))
	return keyboard
}

// ServicesMenuWithData создает меню сервисов с данными из API
func (b *Builder) ServicesMenuWithData(servicesList []services.Service, platformsList []services.Platform, webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Заголовок "Основные сервисы" (неактивная кнопка)
	keyboard.
		AddRow().
		AddCallback("---Основные сервисы---", schemes.DEFAULT, "services_header")

	// Основные сервисы - размещаем по 2 в строке, находим строку с "Чатами"
	servicesCount := len(servicesList)
	var chatsRow *maxbot.KeyboardRow
	var chatsIndex = -1
	hasTeachers := false

	// Проверяем, есть ли "Чаты" и "Преподаватели" в списке из API
	for i, service := range servicesList {
		if service.Key == "chats" {
			chatsIndex = i
		}
		if service.Key == "teachers" {
			hasTeachers = true
		}
	}

	// Размещаем сервисы по 2 в строке
	for i := 0; i < servicesCount; i += 2 {
		row := keyboard.AddRow()

		// Проверяем, есть ли "Чаты" в этой строке
		if chatsIndex >= 0 && (i == chatsIndex || (i+1 == chatsIndex)) {
			chatsRow = row
		}

		// Добавляем первую кнопку в строке
		if i < servicesCount {
			service := servicesList[i]
			text := service.Emoji + " " + service.Name
			payload := "service_" + service.Key
			row.AddCallback(text, schemes.POSITIVE, payload)
		}

		// Добавляем вторую кнопку в строке (если есть)
		if i+1 < servicesCount {
			service := servicesList[i+1]
			text := service.Emoji + " " + service.Name
			payload := "service_" + service.Key
			row.AddCallback(text, schemes.POSITIVE, payload)
		}
	}

	// Добавляем кнопку "Клубы" рядом с "Чатами", если они найдены
	if chatsRow != nil {
		// Если "Чаты" найдены, добавляем "Клубы" в ту же строку рядом с ними
		chatsRow.AddCallback("🎭 Клубы", schemes.POSITIVE, "service_clubs")
		// Добавляем "Преподаватели" только если их нет в списке из API
		if !hasTeachers {
			chatsRow.AddCallback("👨‍🏫 Преподаватели", schemes.POSITIVE, "service_teachers")
		}
	} else {
		// Если "Чаты" не найдены, создаем новую строку для "Клубы" и "Преподаватели" (если их нет в API)
		row := keyboard.AddRow()
		row.AddCallback("🎭 Клубы", schemes.POSITIVE, "service_clubs")
		if !hasTeachers {
			row.AddCallback("👨‍🏫 Преподаватели", schemes.POSITIVE, "service_teachers")
		}
	}

	// Заголовок "Веб платформы" (неактивная кнопка)
	keyboard.
		AddRow().
		AddCallback("---Веб платформы---", schemes.DEFAULT, "platforms_header")

	// Веб-платформы - размещаем по 2 в строке
	platformsCount := len(platformsList)
	for i := 0; i < platformsCount; i += 2 {
		row := keyboard.AddRow()

		// Добавляем первую кнопку в строке
		if i < platformsCount {
			platform := platformsList[i]
			text := platform.Emoji + " " + platform.Name
			payload := "platform_" + platform.Key
			row.AddCallback(text, schemes.POSITIVE, payload)
		}

		// Добавляем вторую кнопку в строке (если есть)
		if i+1 < platformsCount {
			platform := platformsList[i+1]
			text := platform.Emoji + " " + platform.Name
			payload := "platform_" + platform.Key
			row.AddCallback(text, schemes.POSITIVE, payload)
		}
	}

	// Навигация (сервисы активны)
	keyboard.
		AddRow().
		AddCallback("🏠 Главная", schemes.NEGATIVE, string(types.ActionHome)).
		AddCallback("✅ Сервисы", schemes.POSITIVE, string(types.ActionOpenServices)).
		AddCallback("👤 Профиль", schemes.NEGATIVE, string(types.ActionOpenProfile))

	// Добавляем кнопку веб-приложения внизу, если URL указан
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}

// ProfileMenu создает меню профиля с кнопками подгрупп
func (b *Builder) ProfileMenu(subgroupMode string, webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Кнопки подгрупп (активная помечена ✅)
	var fullText, group1Text, group2Text string
	switch subgroupMode {
	case "full":
		fullText = "✅ Вся группа"
		group1Text = "Подгруппа 1"
		group2Text = "Подгруппа 2"
	case "group1":
		fullText = "Вся группа"
		group1Text = "✅ Подгруппа 1"
		group2Text = "Подгруппа 2"
	case "group2":
		fullText = "Вся группа"
		group1Text = "Подгруппа 1"
		group2Text = "✅ Подгруппа 2"
	default:
		fullText = "✅ Вся группа"
		group1Text = "Подгруппа 1"
		group2Text = "Подгруппа 2"
	}

	keyboard.
		AddRow().
		AddCallback(fullText, schemes.POSITIVE, string(types.ActionSubgroupFull)).
		AddCallback(group1Text, schemes.POSITIVE, string(types.ActionSubgroupGroup1)).
		AddCallback(group2Text, schemes.POSITIVE, string(types.ActionSubgroupGroup2))

	// Навигация (профиль активен)
	keyboard.
		AddRow().
		AddCallback("🏠 Главная", schemes.NEGATIVE, string(types.ActionHome)).
		AddCallback("🔧 Сервисы", schemes.NEGATIVE, string(types.ActionOpenServices)).
		AddCallback("✅ Профиль", schemes.POSITIVE, string(types.ActionOpenProfile))

	// Добавляем кнопку-линк для админ панели
	keyboard.
		AddRow().
		AddLink("🔐 Открыть админ панель", schemes.POSITIVE, "https://max-admin-panel.cloudpub.ru/")

	// Добавляем кнопку веб-приложения внизу, если URL указан
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}

// BackMenu создает меню с кнопкой "Назад"
func (b *Builder) BackMenu() *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	keyboard.
		AddRow().
		AddCallback("⬅️ Назад", schemes.NEGATIVE, string(types.ActionBack)).
		AddCallback("🏠 Главная", schemes.POSITIVE, string(types.ActionHome))
	return keyboard
}

// HomeMenu создает меню с кнопкой "Главная"
func (b *Builder) HomeMenu() *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	keyboard.
		AddRow().
		AddCallback("🏠 Главная", schemes.POSITIVE, string(types.ActionHome))
	return keyboard
}

// formatTeacherNameForButton форматирует имя преподавателя в формат "Фамилия И.О." для кнопки
func formatTeacherNameForButton(fullName string) string {
	nameParts := strings.Fields(fullName)
	if len(nameParts) == 0 {
		return fullName
	}

	// Фамилия (первое слово)
	surname := nameParts[0]

	// Инициалы (первые буквы остальных слов)
	initials := ""
	for i := 1; i < len(nameParts) && i < 4; i++ {
		wordRunes := []rune(nameParts[i])
		if len(wordRunes) > 0 {
			initials += string(wordRunes[0]) + "."
		}
	}

	if initials != "" {
		return fmt.Sprintf("%s %s", surname, initials)
	}
	return surname
}

// TeacherInfoMenu создает клавиатуру для страницы информации о преподавателе
func (b *Builder) TeacherInfoMenu(webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Кнопки навигации: Главная, Сервисы, Профиль
	navRow := keyboard.AddRow()
	navRow.AddCallback("🏠 Главная", schemes.POSITIVE, "open_main")
	navRow.AddCallback("📋 Сервисы", schemes.POSITIVE, "open_services")
	navRow.AddCallback("👤 Профиль", schemes.POSITIVE, "open_profile")

	// Кнопка "Открыть веб приложение" (если URL указан)
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}

// TeachersAlphabetMenu создает клавиатуру с алфавитом для поиска преподавателей
func (b *Builder) TeachersAlphabetMenu(webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Русский алфавит
	alphabet := []string{"А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Э", "Ю", "Я"}

	// Размещаем по 6 букв в строке
	for i := 0; i < len(alphabet); i += 6 {
		row := keyboard.AddRow()
		for j := i; j < i+6 && j < len(alphabet); j++ {
			letter := alphabet[j]
			payload := fmt.Sprintf("teacher_letter_%s", letter)
			row.AddCallback(letter, schemes.POSITIVE, payload)
		}
	}

	// Кнопки навигации: Главная, Сервисы, Профиль
	navRow := keyboard.AddRow()
	navRow.AddCallback("🏠 Главная", schemes.POSITIVE, "open_main")
	navRow.AddCallback("📋 Сервисы", schemes.POSITIVE, "open_services")
	navRow.AddCallback("👤 Профиль", schemes.POSITIVE, "open_profile")

	// Кнопка "Открыть веб приложение" (если URL указан)
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}

// TeachersListMenu создает клавиатуру со списком преподавателей и пагинацией
func (b *Builder) TeachersListMenu(teachers []services.Teacher, letter string, currentPage, totalPages int, webAppURL string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()

	// Размер страницы (должен совпадать с pageSize в buildTeachersListPage)
	const pageSize = 20

	// Начальный номер для текущей страницы
	startNumber := currentPage * pageSize

	// Кнопки преподавателей - по 2 в строке
	for i := 0; i < len(teachers); i += 2 {
		row := keyboard.AddRow()

		// Первая кнопка
		if i < len(teachers) {
			teacher := teachers[i]
			// Форматируем имя в формат "Фамилия И.О." для кнопки
			displayName := formatTeacherNameForButton(teacher.Name)
			number := startNumber + i + 1
			buttonText := fmt.Sprintf("%d) %s", number, displayName)
			payload := fmt.Sprintf("teacher_info_%s", teacher.ID)
			row.AddCallback(buttonText, schemes.POSITIVE, payload)
		}

		// Вторая кнопка
		if i+1 < len(teachers) {
			teacher := teachers[i+1]
			// Форматируем имя в формат "Фамилия И.О." для кнопки
			displayName := formatTeacherNameForButton(teacher.Name)
			number := startNumber + i + 2
			buttonText := fmt.Sprintf("%d) %s", number, displayName)
			payload := fmt.Sprintf("teacher_info_%s", teacher.ID)
			row.AddCallback(buttonText, schemes.POSITIVE, payload)
		}
	}

	// Пагинация: |<<|<|Стр #X|>|>>| (всегда показываем, даже если 1 страница)
	pageRow := keyboard.AddRow()

	// Кнопка |<< (на первую страницу)
	if currentPage > 0 {
		payload := fmt.Sprintf("teacher_page_%s_0", letter)
		pageRow.AddCallback("|<<", schemes.DEFAULT, payload)
	} else {
		pageRow.AddCallback("|<<", schemes.DEFAULT, "disabled")
	}

	// Кнопка < (на предыдущую страницу)
	if currentPage > 0 {
		payload := fmt.Sprintf("teacher_page_%s_%d", letter, currentPage-1)
		pageRow.AddCallback("<", schemes.DEFAULT, payload)
	} else {
		pageRow.AddCallback("<", schemes.DEFAULT, "disabled")
	}

	// Кнопка с номером страницы (всегда показываем)
	pageText := fmt.Sprintf("Стр #%d", currentPage+1)
	pageRow.AddCallback(pageText, schemes.DEFAULT, "disabled")

	// Кнопка > (на следующую страницу)
	if currentPage < totalPages-1 {
		payload := fmt.Sprintf("teacher_page_%s_%d", letter, currentPage+1)
		pageRow.AddCallback(">", schemes.DEFAULT, payload)
	} else {
		pageRow.AddCallback(">", schemes.DEFAULT, "disabled")
	}

	// Кнопка >>| (на последнюю страницу)
	if currentPage < totalPages-1 {
		payload := fmt.Sprintf("teacher_page_%s_%d", letter, totalPages-1)
		pageRow.AddCallback(">>|", schemes.DEFAULT, payload)
	} else {
		pageRow.AddCallback(">>|", schemes.DEFAULT, "disabled")
	}

	// Кнопки навигации: Главная, Сервисы, Профиль
	navRow := keyboard.AddRow()
	navRow.AddCallback("🏠 Главная", schemes.POSITIVE, "open_main")
	navRow.AddCallback("📋 Сервисы", schemes.POSITIVE, "open_services")
	navRow.AddCallback("👤 Профиль", schemes.POSITIVE, "open_profile")

	// Кнопка "Открыть веб приложение" (если URL указан)
	if webAppURL != "" {
		b.AddOpenApp(keyboard.AddRow(), "🌐 Открыть веб приложение", schemes.POSITIVE, webAppURL)
	}

	return keyboard
}
