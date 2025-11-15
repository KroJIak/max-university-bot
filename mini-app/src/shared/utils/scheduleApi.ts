import type { ScheduleItem } from '@shared/types/schedule';
import type { ScheduleItemDto } from '@components/api/client';

/**
 * Форматирует дату в формат для API (ДД.ММ)
 */
export function formatDateForApi(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${day}.${month}`;
}

/**
 * Форматирует диапазон дат для API (ДД.ММ-ДД.ММ)
 */
export function formatDateRangeForApi(startDate: Date, endDate: Date): string {
  const start = formatDateForApi(startDate);
  const end = formatDateForApi(endDate);
  return `${start}-${end}`;
}

/**
 * Преобразует элемент расписания из API в ScheduleItem
 */
export function transformScheduleItemFromApi(dto: ScheduleItemDto): ScheduleItem {
  return {
    id: dto.id,
    start: dto.start,
    end: dto.end,
    title: dto.title,
    type: dto.type,
    room: dto.room,
    note: dto.note,
    audience: dto.audience,
    date: dto.date,
    teacher: dto.teacher,
    additional_info: dto.additional_info ?? undefined,
    undergruop: dto.undergruop ?? undefined,
  };
}

/**
 * Группирует расписание по датам
 */
export function groupScheduleByDate(items: ScheduleItem[]): Record<string, ScheduleItem[]> {
  const grouped: Record<string, ScheduleItem[]> = {};

  for (const item of items) {
    if (!item.date) {
      continue;
    }

    if (!grouped[item.date]) {
      grouped[item.date] = [];
    }

    grouped[item.date].push(item);
  }

  // Сортируем занятия по времени начала
  for (const date in grouped) {
    grouped[date].sort((a, b) => {
      const timeA = a.start.split(':').map(Number);
      const timeB = b.start.split(':').map(Number);
      const minutesA = timeA[0] * 60 + timeA[1];
      const minutesB = timeB[0] * 60 + timeB[1];
      return minutesA - minutesB;
    });
  }

  return grouped;
}

/**
 * Получает расписание для сегодня, завтра и послезавтра
 */
export function getTodayTomorrowAfterTomorrow(): { today: Date; tomorrow: Date; afterTomorrow: Date } {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const afterTomorrow = new Date(today);
  afterTomorrow.setDate(afterTomorrow.getDate() + 2);

  return { today, tomorrow, afterTomorrow };
}

/**
 * Форматирует дату в формат ключа для кэша (ДД.ММ.ГГГГ)
 */
export function formatDateToKey(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
}

