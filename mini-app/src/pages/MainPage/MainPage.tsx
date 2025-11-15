import { useEffect, useMemo, useState } from 'react';

import { NewsSection } from '@components/NewsSection';
import { ScheduleSection } from '@components/ScheduleSection';
import { apiClient } from '@components/api/client';
import { dayTabs } from '@shared/data/mainPage';
import type { ScheduleItem, DayTab } from '@shared/types/schedule';
import {
  formatDateRangeForApi,
  transformScheduleItemFromApi,
  groupScheduleByDate,
  getTodayTomorrowAfterTomorrow,
  formatDateToKey,
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


export function MainPage({ userId, onOpenFullSchedule, onOpenAllNews }: MainPageProps) {
  const cachedData = loadCachedSchedule(userId);
  
  // Мемоизируем даты, чтобы они не пересоздавались при каждом рендере
  const { today, tomorrow, afterTomorrow } = useMemo(() => getTodayTomorrowAfterTomorrow(), []);

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
    let timeoutId: NodeJS.Timeout | null = null;

    async function loadSchedule() {
      if (isCancelled) {
        return;
      }

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
            setLoading(false);
          }
        } else {
          if (!isCancelled) {
            setScheduleByTab(defaultScheduleByTab);
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[MainPage] Failed to load schedule', error);
        if (!isCancelled) {
          setScheduleByTab(defaultScheduleByTab);
          setLoading(false);
        }
      }
    }

    // Если кэша нет, загружаем сразу
    // Если кэш есть, показываем кэш и обновляем в фоне с задержкой, чтобы избежать лишних запросов
    if (cachedData) {
      // Кэш есть, показываем его сразу
      setScheduleByTab(cachedData.scheduleByTab);
      setLoading(false);
      
      // Обновляем в фоне только если кэш старше 4 минут (чтобы не дублировать запросы с DataPreloader)
      const cacheAge = Date.now() - (cachedData.timestamp || 0);
      const shouldRefresh = cacheAge > 4 * 60 * 1000; // 4 минуты
      
      if (shouldRefresh) {
        // Обновляем в фоне с задержкой
        timeoutId = setTimeout(() => {
          loadSchedule();
        }, 2000); // Задержка 2 секунды
      }
    } else {
      // Кэша нет, загружаем сразу
      loadSchedule();
    }

    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [userId, todayKey, tomorrowKey, afterTomorrowKey]); // Используем только строковые ключи, не объекты Date

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
