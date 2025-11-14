import { useMemo, useState } from 'react';

import { useSubgroup } from '@shared/state/subgroup';
import { filterLessonsBySubgroup } from '@shared/utils/schedule';
import type { ScheduleItem } from '@shared/types/schedule';
import { MonthCalendar, ScheduleLessons } from '@components/ScheduleDetail';
import type { CalendarCell } from '@components/ScheduleDetail/types';
import { scheduleByDay } from '@shared/data/mainPage';
import styles from './SchedulePage.module.scss';

type MonthMetadata = {
  month: number;
  year: number;
};

const weekdayShort = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function formatKey(date: Date) {
  return date.toISOString().slice(0, 10);
}

function getLessonsByDate(date: Date): ScheduleItem[] {
  const dayIndex = date.getDay();
  if (dayIndex === 1) {
    return scheduleByDay.today ?? [];
  }
  if (dayIndex === 2) {
    return scheduleByDay.tomorrow ?? [];
  }
  if (dayIndex === 3) {
    return scheduleByDay.afterTomorrow ?? [];
  }
  return [];
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
      hasLessons: getLessonsByDate(date).length > 0,
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
      hasLessons: getLessonsByDate(date).length > 0,
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
      hasLessons: getLessonsByDate(nextDate).length > 0,
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
      hasLessons: getLessonsByDate(nextDate).length > 0,
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

export function SchedulePage() {
  const today = new Date();
  const [view, setView] = useState<MonthMetadata>({ month: today.getMonth(), year: today.getFullYear() });
  const [selectedDate, setSelectedDate] = useState(today);
  const { subgroup } = useSubgroup();

  const calendarCells = useMemo(() => buildCalendar(view), [view]);
  const lessons = useMemo(
    () => filterLessonsBySubgroup(getLessonsByDate(selectedDate), subgroup),
    [selectedDate, subgroup],
  );

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
        onSelectDate={setSelectedDate}
        selectedDateKey={formatKey(selectedDate)}
        todayKey={formatKey(today)}
      />

      <ScheduleLessons items={lessons} />
    </div>
  );
}

