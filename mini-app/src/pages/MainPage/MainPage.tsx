import { useEffect, useMemo, useState } from 'react';

import { NewsSection } from '@components/NewsSection';
import { ScheduleSection } from '@components/ScheduleSection';
import { apiClient } from '@components/api/client';
import { dayTabs } from '@shared/data/mainPage';
import type { ScheduleItem, DayTab } from '@shared/types/schedule';
import {
  formatDateForApi,
  formatDateRangeForApi,
  transformScheduleItemFromApi,
  groupScheduleByDate,
  getTodayTomorrowAfterTomorrow,
} from '@shared/utils/scheduleApi';
import styles from './MainPage.module.scss';

type MainPageProps = {
  userId: number;
  onOpenFullSchedule: () => void;
  onOpenAllNews: () => void;
};

const CACHE_KEY_PREFIX = 'max-app-schedule-main-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

type CachedScheduleData = {
  scheduleByTab: Record<string, ScheduleItem[]>;
  timestamp: number;
};

function loadCachedSchedule(userId: number): CachedScheduleData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
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
    console.warn('[MainPage] Failed to load cached schedule', error);
    return null;
  }
}

function saveCachedSchedule(userId: number, scheduleByTab: Record<string, ScheduleItem[]>): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cacheValue: CachedScheduleData = {
      scheduleByTab,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[MainPage] Failed to save cached schedule', error);
  }
}

function formatDateToKey(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
}

export function MainPage({ userId, onOpenFullSchedule, onOpenAllNews }: MainPageProps) {
  const cachedData = loadCachedSchedule(userId);
  const { today, tomorrow, afterTomorrow } = getTodayTomorrowAfterTomorrow();

  const todayKey = formatDateToKey(today);
  const tomorrowKey = formatDateToKey(tomorrow);
  const afterTomorrowKey = formatDateToKey(afterTomorrow);

  const defaultScheduleByTab: Record<string, ScheduleItem[]> = {
    today: [],
    tomorrow: [],
    afterTomorrow: [],
  };

  const [scheduleByTab, setScheduleByTab] = useState<Record<string, ScheduleItem[]>>(
    cachedData?.scheduleByTab || defaultScheduleByTab,
  );
  const [loading, setLoading] = useState(!cachedData);

  useEffect(() => {
    let isCancelled = false;

    async function loadSchedule() {
      try {
        // Загружаем расписание для сегодня, завтра и послезавтра
        const dateRange = formatDateRangeForApi(today, afterTomorrow);
        const response = await apiClient.getSchedule(userId, dateRange);

        if (isCancelled) {
          return;
        }

        if (response.success && response.schedule) {
          const items = response.schedule.map(transformScheduleItemFromApi);
          const grouped = groupScheduleByDate(items);

          const newScheduleByTab: Record<string, ScheduleItem[]> = {
            today: grouped[todayKey] || [],
            tomorrow: grouped[tomorrowKey] || [],
            afterTomorrow: grouped[afterTomorrowKey] || [],
          };

          saveCachedSchedule(userId, newScheduleByTab);

          if (!isCancelled) {
            setScheduleByTab(newScheduleByTab);
            if (loading) {
              setLoading(false);
            }
          }
        } else {
          if (!isCancelled) {
            setScheduleByTab(defaultScheduleByTab);
            if (loading) {
              setLoading(false);
            }
          }
        }
      } catch (error) {
        console.error('[MainPage] Failed to load schedule', error);
        if (!isCancelled) {
          setScheduleByTab(defaultScheduleByTab);
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    if (!cachedData) {
      loadSchedule();
    }

    return () => {
      isCancelled = true;
    };
  }, [userId, todayKey, tomorrowKey, afterTomorrowKey, cachedData, loading, today, afterTomorrow]);

  const updatedDayTabs = useMemo(() => {
    return dayTabs.map((tab, index) => {
      const date = index === 0 ? today : index === 1 ? tomorrow : afterTomorrow;
      const weekday = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'][date.getDay()];
      return {
        ...tab,
        label: `${tab.label.split(', ')[0]}, ${weekday}`,
      };
    });
  }, [today, tomorrow, afterTomorrow]);

  return (
    <div className={styles.page}>
      <div className={styles.mainContent}>
        <ScheduleSection
          tabs={updatedDayTabs}
          scheduleByTab={scheduleByTab}
          onOpenFullSchedule={onOpenFullSchedule}
        />
        <NewsSection onOpenAll={onOpenAllNews} />
      </div>
    </div>
  );
}
