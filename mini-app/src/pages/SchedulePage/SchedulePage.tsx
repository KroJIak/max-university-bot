import { useEffect, useMemo, useState } from 'react';

import { useSubgroup } from '@shared/state/subgroup';
import { filterLessonsBySubgroup } from '@shared/utils/schedule';
import type { ScheduleItem } from '@shared/types/schedule';
import { MonthCalendar, ScheduleLessons } from '@components/ScheduleDetail';
import type { CalendarCell } from '@components/ScheduleDetail/types';
import { apiClient } from '@components/api/client';
import { formatDateRangeForApi, transformScheduleItemFromApi, groupScheduleByDate, formatDateToKey } from '@shared/utils/scheduleApi';
import styles from './SchedulePage.module.scss';

type MonthMetadata = {
  month: number;
  year: number;
};

type SchedulePageProps = {
  userId: number;
};

const CACHE_KEY_PREFIX = 'max-app-schedule-full-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number, dateKey: string): string {
  return `${CACHE_KEY_PREFIX}${userId}-${dateKey}`;
}

type CachedScheduleData = {
  items: ScheduleItem[];
  timestamp: number;
};

function loadCachedSchedule(userId: number, dateKey: string): CachedScheduleData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId, dateKey);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as CachedScheduleData;
    const now = Date.now();

    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed;
  } catch (error) {
    console.warn('[SchedulePage] Failed to load cached schedule', error);
    return null;
  }
}

function saveCachedSchedule(userId: number, dateKey: string, items: ScheduleItem[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId, dateKey);
    const cacheValue: CachedScheduleData = {
      items,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[SchedulePage] Failed to save cached schedule', error);
  }
}


const weekdayShort = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function formatKey(date: Date) {
  // Используем локальное время для избежания смещения из-за UTC
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${year}-${month}-${day}`;
}

function buildCalendar({ month, year }: MonthMetadata): CalendarCell[] {
  const startOfMonth = new Date(year, month, 1);
  const endOfMonth = new Date(year, month + 1, 0);

  const startWeekday = (startOfMonth.getDay() + 6) % 7; // Monday-first
  const daysInMonth = endOfMonth.getDate();

  const cells: CalendarCell[] = [];

  // previous month tail
  for (let i = startWeekday; i > 0; i -= 1) {
    const date = new Date(year, month, 1 - i);
    cells.push({
      date,
      label: date.getDate(),
      key: formatKey(date),
      inCurrentMonth: false,
      hasLessons: false, // Будет обновлено после загрузки данных
    });
  }

  // current month
  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day);
    cells.push({
      date,
      label: day,
      key: formatKey(date),
      inCurrentMonth: true,
      hasLessons: false, // Будет обновлено после загрузки данных
    });
  }

  // next month head to fill grid (42 cells)
  while (cells.length % 7 !== 0) {
    const last = cells[cells.length - 1].date;
    const nextDate = new Date(last);
    nextDate.setDate(last.getDate() + 1);
    cells.push({
      date: nextDate,
      label: nextDate.getDate(),
      key: formatKey(nextDate),
      inCurrentMonth: false,
      hasLessons: false, // Будет обновлено после загрузки данных
    });
  }

  // ensure full 6 rows (42 cells) like native calendar
  while (cells.length < 42) {
    const last = cells[cells.length - 1].date;
    const nextDate = new Date(last);
    nextDate.setDate(last.getDate() + 1);
    cells.push({
      date: nextDate,
      label: nextDate.getDate(),
      key: formatKey(nextDate),
      inCurrentMonth: false,
      hasLessons: false, // Будет обновлено после загрузки данных
    });
  }

  return cells;
}

function formatMonthTitle({ month, year }: MonthMetadata) {
  const formatter = new Intl.DateTimeFormat('ru-RU', {
    month: 'long',
    year: 'numeric',
  });
  const sample = new Date(year, month, 1);
  return formatter.format(sample);
}

export function SchedulePage({ userId }: SchedulePageProps) {
  const today = new Date();
  const [view, setView] = useState<MonthMetadata>({ month: today.getMonth(), year: today.getFullYear() });
  const [selectedDate, setSelectedDate] = useState(today);
  const [selectedDateLessons, setSelectedDateLessons] = useState<ScheduleItem[]>([]);
  const [allLessonsByDate, setAllLessonsByDate] = useState<Record<string, ScheduleItem[]>>({});
  const { subgroup } = useSubgroup();

  const selectedDateKey = formatDateToKey(selectedDate);

  // Загружаем расписание для всего месяца при изменении view
  useEffect(() => {
    let isCancelled = false;

    async function loadMonthSchedule() {
      const startOfMonth = new Date(view.year, view.month, 1);
      const endOfMonth = new Date(view.year, view.month + 1, 0);

      // Загружаем расписание для всего месяца
      const dateRange = formatDateRangeForApi(startOfMonth, endOfMonth);
      const cachedKey = `${view.year}-${view.month}`;
      const cached = loadCachedSchedule(userId, cachedKey);

      if (cached && !isCancelled) {
        setAllLessonsByDate(cached.items.reduce((acc, item) => {
          if (item.date) {
            if (!acc[item.date]) {
              acc[item.date] = [];
            }
            acc[item.date].push(item);
          }
          return acc;
        }, {} as Record<string, ScheduleItem[]>));
        return;
      }

      try {
        const response = await apiClient.getSchedule(userId, dateRange);

        if (isCancelled) {
          return;
        }

        if (response.success && response.schedule) {
          const items = response.schedule.map(transformScheduleItemFromApi);
          const grouped = groupScheduleByDate(items);

          saveCachedSchedule(userId, cachedKey, items);

          if (!isCancelled) {
            setAllLessonsByDate(grouped);
          }
        } else {
          if (!isCancelled) {
            setAllLessonsByDate({});
          }
        }
      } catch (error) {
        console.error('[SchedulePage] Failed to load schedule', error);
        if (!isCancelled) {
          setAllLessonsByDate({});
        }
      }
    }

    loadMonthSchedule();

    return () => {
      isCancelled = true;
    };
  }, [userId, view.year, view.month]);

  // Обработчик выбора даты - автоматически переключает месяц, если дата из другого месяца
  const handleSelectDate = (date: Date) => {
    setSelectedDate(date);
    
    // Проверяем, относится ли выбранная дата к текущему месяцу
    const dateMonth = date.getMonth();
    const dateYear = date.getFullYear();
    
    // Если выбранная дата из другого месяца, переключаемся на этот месяц
    if (dateMonth !== view.month || dateYear !== view.year) {
      setView({ month: dateMonth, year: dateYear });
    }
  };

  // Обновляем занятия для выбранной даты
  useEffect(() => {
    const lessons = allLessonsByDate[selectedDateKey] || [];
    setSelectedDateLessons(lessons);
  }, [selectedDateKey, allLessonsByDate]);

  const calendarCells = useMemo(() => {
    const cells = buildCalendar(view);
    // Обновляем hasLessons на основе загруженных данных
    return cells.map((cell) => {
      const dateKey = formatDateToKey(cell.date);
      const hasLessons = (allLessonsByDate[dateKey]?.length || 0) > 0;
      return { ...cell, hasLessons };
    });
  }, [view, allLessonsByDate]);

  const lessons = useMemo(
    () => filterLessonsBySubgroup(selectedDateLessons, subgroup),
    [selectedDateLessons, subgroup],
  );

  // Проверяем, относится ли выбранная дата к текущему отображаемому месяцу
  const isSelectedDateInCurrentMonth = useMemo(() => {
    return selectedDate.getMonth() === view.month && selectedDate.getFullYear() === view.year;
  }, [selectedDate, view.month, view.year]);

  return (
    <div className={styles.page}>
      <MonthCalendar
        title={formatMonthTitle(view)}
        weekdayLabels={weekdayShort}
        cells={calendarCells}
        onPrevMonth={() =>
          setView((prev) => ({
            month: prev.month === 0 ? 11 : prev.month - 1,
            year: prev.month === 0 ? prev.year - 1 : prev.year,
          }))
        }
        onNextMonth={() =>
          setView((prev) => ({
            month: prev.month === 11 ? 0 : prev.month + 1,
            year: prev.month === 11 ? prev.year + 1 : prev.year,
          }))
        }
        onSelectToday={() => {
          const now = new Date();
          setView({ month: now.getMonth(), year: now.getFullYear() });
          setSelectedDate(now);
        }}
        onSelectDate={handleSelectDate}
        selectedDateKey={formatKey(selectedDate)}
        todayKey={formatKey(today)}
      />

      {!isSelectedDateInCurrentMonth ? (
        <div className={styles.selectDayMessage}>
          Выберите день для отображения расписания
        </div>
      ) : (
        <ScheduleLessons items={lessons} />
      )}
    </div>
  );
}
