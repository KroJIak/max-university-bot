import { ArrowRightIcon } from '@components/icons';
import styles from './ScheduleDetail.module.scss';
import type { CalendarCell } from './types';

type MonthCalendarProps = {
  title: string;
  weekdayLabels: string[];
  cells: CalendarCell[];
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onSelectToday: () => void;
  onSelectDate: (date: Date) => void;
  selectedDateKey: string;
  todayKey: string;
};

export function MonthCalendar({
  title,
  weekdayLabels,
  cells,
  onPrevMonth,
  onNextMonth,
  onSelectToday,
  onSelectDate,
  selectedDateKey,
  todayKey,
}: MonthCalendarProps) {
  return (
    <section className={styles.calendarCard}>
      <div className={styles.calendarHeader}>
        <div className={styles.calendarControls}>
          <button
            type="button"
            className={`${styles.calendarButton} ${styles.calendarButtonPrev}`}
            onClick={onPrevMonth}
            aria-label="Предыдущий месяц"
          >
            <ArrowRightIcon />
          </button>
          <h1 className={styles.calendarTitle}>{title}</h1>
          <button
            type="button"
            className={`${styles.calendarButton} ${styles.calendarButtonNext}`}
            onClick={onNextMonth}
            aria-label="Следующий месяц"
          >
            <ArrowRightIcon />
          </button>
        </div>
        <button type="button" className={styles.todayButton} onClick={onSelectToday}>
          Сегодня
        </button>
      </div>

      <div className={styles.calendarGrid}>
        {weekdayLabels.map((weekday) => (
          <div key={weekday} className={styles.weekday}>
            {weekday}
          </div>
        ))}
        {cells.map((cell) => {
          const isSelected = cell.key === selectedDateKey;
          const isToday = cell.key === todayKey;
          const className = [
            styles.dayCell,
            !cell.inCurrentMonth && styles.dayCellMuted,
            isSelected && styles.dayCellActive,
            isToday && styles.dayCellToday,
          ]
            .filter(Boolean)
            .join(' ');

          return (
            <button
              key={cell.key}
              type="button"
              className={className}
              onClick={() => onSelectDate(cell.date)}
            >
              <span>{cell.label}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

