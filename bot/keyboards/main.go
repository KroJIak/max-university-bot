package keyboards

import (
	"max-bot/services"
	"max-bot/types"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// Builder предоставляет методы для создания клавиатур
type Builder struct {
	api *maxbot.Api
}

// NewBuilder создает новый билдер клавиатур
func NewBuilder(api *maxbot.Api) *Builder {
	return &Builder{api: api}
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
func (b *Builder) MainPageMenu(todayWeekday, tomorrowWeekday, afterTomorrowWeekday string, activeTab string) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	
	// Определяем эмоджи для активного/неактивного состояния табов (только день недели)
	var todayText, tomorrowText, afterTomorrowText string
	if activeTab == "today" {
		todayText = "✅ " + todayWeekday
		tomorrowText = tomorrowWeekday
		afterTomorrowText = afterTomorrowWeekday
	} else if activeTab == "tomorrow" {
		todayText = todayWeekday
		tomorrowText = "✅ " + tomorrowWeekday
		afterTomorrowText = afterTomorrowWeekday
	} else if activeTab == "afterTomorrow" {
		todayText = todayWeekday
		tomorrowText = tomorrowWeekday
		afterTomorrowText = "✅ " + afterTomorrowWeekday
	} else {
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
func (b *Builder) ServicesMenuWithData(servicesList []services.Service, platformsList []services.Platform) *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	
	// Заголовок "Основные сервисы" (неактивная кнопка)
	keyboard.
		AddRow().
		AddCallback("Основные сервисы", schemes.DEFAULT, "services_header")
	
	// Основные сервисы - размещаем по 2 в строке
	servicesCount := len(servicesList)
	for i := 0; i < servicesCount; i += 2 {
		row := keyboard.AddRow()
		
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
	
	// Заголовок "Веб платформы" (неактивная кнопка)
	keyboard.
		AddRow().
		AddCallback("Веб платформы", schemes.DEFAULT, "platforms_header")
	
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
	
	return keyboard
}

// ProfileMenu создает меню профиля (с эмоджи для активной страницы)
func (b *Builder) ProfileMenu() *maxbot.Keyboard {
	keyboard := b.api.Messages.NewKeyboardBuilder()
	keyboard.
		AddRow().
		AddCallback("📊 Зачетка", schemes.POSITIVE, string(types.ActionOpenGradebook)).
		AddCallback("💰 Долги", schemes.POSITIVE, string(types.ActionOpenDebts))
	keyboard.
		AddRow().
		AddCallback("🔔 Уведомления", schemes.POSITIVE, string(types.ActionOpenNotifications)).
		AddCallback("🎨 Тема", schemes.POSITIVE, string(types.ActionOpenTheme))
	// Навигация (профиль активен)
	keyboard.
		AddRow().
		AddCallback("⬅️ Назад", schemes.NEGATIVE, string(types.ActionBack)).
		AddCallback("🏠 Главная", schemes.NEGATIVE, string(types.ActionHome)).
		AddCallback("✅ Профиль", schemes.POSITIVE, string(types.ActionOpenProfile))
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

