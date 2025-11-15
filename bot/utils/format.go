package utils

import (
	"fmt"
	"strings"
)

// FormatHeader создает заголовок с выравниванием по ширине
func FormatHeader(title string) string {
	title = strings.TrimSpace(title)
	// Формат: "-------Главная----------"
	// Примерно 7 дефисов слева, название, остальные дефисы справа
	leftDashes := 7
	rightDashes := 11
	return strings.Repeat("-", leftDashes) + title + strings.Repeat("-", rightDashes)
}

// FormatSection создает заголовок секции
func FormatSection(title string) string {
	return "**" + title + ":**"
}

// FormatSeparator создает разделитель точно по ширине
func FormatSeparator(width int) string {
	if width <= 0 {
		width = 22
	}
	return strings.Repeat("_", width)
}

// FormatScheduleItem форматирует элемент расписания с выравниванием (простой формат)
func FormatScheduleItem(time string, subject string, type_ string, room string) string {
	// Выравниваем колонки: время (7), предмет (до 15), тип (до конца)
	timePadded := padRight(time, 7)
	subjectPadded := padRight(subject, 15)
	
	result := timePadded + " | " + subjectPadded + " | " + type_
	return result
}

// FormatScheduleItemNew форматирует элемент расписания в новом формате (две строки)
func FormatScheduleItemNew(startTime string, endTime string, subject string, type_ string, room string, note string) string {
	// Первая строка: время начала и название предмета
	timePadded := padRight(startTime, 7)
	line1 := timePadded + " | " + subject
	
	// Вторая строка: время окончания, тип, место, примечание
	var line2Parts []string
	if type_ != "" {
		line2Parts = append(line2Parts, type_)
	}
	if room != "" {
		line2Parts = append(line2Parts, room)
	}
	if note != "" {
		line2Parts = append(line2Parts, note)
	}
	
	line2 := ""
	if endTime != "" || len(line2Parts) > 0 {
		// Вторая строка начинается с времени окончания (7 символов для выравнивания)
		endTimePadded := padRight(endTime, 7)
		line2 = endTimePadded + " | " + strings.Join(line2Parts, " | ")
	}
	
	if line2 != "" {
		return line1 + "\n" + line2
	}
	return line1
}

// FormatScheduleHeader не используется, убираем
func FormatScheduleHeader() string {
	return ""
}

// FormatScheduleFooter не нужен для простого стиля
func FormatScheduleFooter() string {
	return ""
}

// FormatNewsItem форматирует новость красиво
func FormatNewsItem(number int, title string, description string) string {
	return fmt.Sprintf("%d. **%s**\n   _%s_", number, title, description)
}

// FormatListHeader создает заголовок списка
func FormatListHeader(title string) string {
	return "**" + title + "**\n"
}

// FormatListItem форматирует элемент списка
func FormatListItem(number int, text string) string {
	return fmt.Sprintf("   %d. %s", number, text)
}

// FormatInfoBlock создает информационный блок
func FormatInfoBlock(title string, content string) string {
	return "**" + title + ":**\n" + content + "\n"
}

// centerText центрирует текст в указанной ширине
func centerText(text string, width int) string {
	textLen := len([]rune(text))
	if textLen >= width {
		return text[:width]
	}
	
	padding := (width - textLen) / 2
	leftPad := strings.Repeat(" ", padding)
	rightPad := strings.Repeat(" ", width-textLen-padding)
	
	return leftPad + text + rightPad
}

// padRight дополняет строку справа пробелами до указанной длины
func padRight(s string, length int) string {
	runes := []rune(s)
	if len(runes) >= length {
		return string(runes[:length])
	}
	return s + strings.Repeat(" ", length-len(runes))
}

// padLeft дополняет строку слева пробелами до указанной длины
func padLeft(s string, length int) string {
	runes := []rune(s)
	if len(runes) >= length {
		return string(runes[:length])
	}
	return strings.Repeat(" ", length-len(runes)) + s
}

