package services

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"sync"
)

const subgroupSettingsFile = "subgroup_settings.csv"

var (
	subgroupSettingsMutex sync.RWMutex
)

// SubgroupMode представляет режим отображения подгрупп
type SubgroupMode string

const (
	SubgroupModeFull    SubgroupMode = "full"     // Вся группа
	SubgroupModeGroup1  SubgroupMode = "group1"   // Подгруппа 1
	SubgroupModeGroup2  SubgroupMode = "group2"   // Подгруппа 2
)

// GetSubgroupMode получает режим подгруппы для пользователя
func GetSubgroupMode(userID int64) SubgroupMode {
	subgroupSettingsMutex.RLock()
	defer subgroupSettingsMutex.RUnlock()

	file, err := os.Open(subgroupSettingsFile)
	if err != nil {
		// Если файл не существует, возвращаем значение по умолчанию
		return SubgroupModeFull
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return SubgroupModeFull
	}

	userIDStr := strconv.FormatInt(userID, 10)
	for _, record := range records {
		if len(record) >= 2 && record[0] == userIDStr {
			return SubgroupMode(record[1])
		}
	}

	return SubgroupModeFull
}

// SetSubgroupMode устанавливает режим подгруппы для пользователя
func SetSubgroupMode(userID int64, mode SubgroupMode) error {
	subgroupSettingsMutex.Lock()
	defer subgroupSettingsMutex.Unlock()

	// Читаем существующие записи
	records := [][]string{}
	file, err := os.Open(subgroupSettingsFile)
	if err == nil {
		reader := csv.NewReader(file)
		records, _ = reader.ReadAll()
		file.Close()
	}

	userIDStr := strconv.FormatInt(userID, 10)
	found := false

	// Обновляем или добавляем запись
	for i, record := range records {
		if len(record) > 0 && record[0] == userIDStr {
			records[i] = []string{userIDStr, string(mode)}
			found = true
			break
		}
	}

	if !found {
		records = append(records, []string{userIDStr, string(mode)})
	}

	// Записываем обратно
	file, err = os.Create(subgroupSettingsFile)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, record := range records {
		if err := writer.Write(record); err != nil {
			return fmt.Errorf("failed to write record: %w", err)
		}
	}

	return nil
}

