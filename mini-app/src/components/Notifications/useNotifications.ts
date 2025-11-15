import { useEffect, useState, useCallback } from 'react';

type Notification = {
  id: string;
  title: string;
  message: string;
  time: string;
  date: string;
};

const NOTIFICATIONS_STORAGE_KEY = 'max-app-notifications';
const NOTIFICATIONS_VIEWED_KEY = 'max-app-notifications-viewed';

// Тестовые уведомления для примера
function getDefaultNotifications(): Notification[] {
  const today = new Date();
  const todayStr = `${String(today.getDate()).padStart(2, '0')}.${String(today.getMonth() + 1).padStart(2, '0')}.${today.getFullYear()}`;
  const timeStr = `${String(today.getHours()).padStart(2, '0')}:${String(today.getMinutes()).padStart(2, '0')}`;

  return [
    {
      id: '1',
      title: 'Новое расписание',
      message: 'В расписании на завтра произошли изменения. Проверьте обновления.',
      time: timeStr,
      date: todayStr,
    },
  ];
}

function loadNotifications(): Notification[] {
  if (typeof window === 'undefined') {
    return getDefaultNotifications();
  }

  try {
    const stored = window.localStorage.getItem(NOTIFICATIONS_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as Notification[];
      return parsed.length > 0 ? parsed : getDefaultNotifications();
    }
  } catch (error) {
    console.warn('[useNotifications] Failed to load notifications', error);
  }

  return getDefaultNotifications();
}

function saveNotifications(notifications: Notification[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.localStorage.setItem(NOTIFICATIONS_STORAGE_KEY, JSON.stringify(notifications));
  } catch (error) {
    console.warn('[useNotifications] Failed to save notifications', error);
  }
}

function loadViewedState(): Set<string> {
  if (typeof window === 'undefined') {
    return new Set();
  }

  try {
    const stored = window.localStorage.getItem(NOTIFICATIONS_VIEWED_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as string[];
      return new Set(parsed);
    }
  } catch (error) {
    console.warn('[useNotifications] Failed to load viewed state', error);
  }

  return new Set();
}

function saveViewedState(viewedIds: Set<string>): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const array = Array.from(viewedIds);
    window.localStorage.setItem(NOTIFICATIONS_VIEWED_KEY, JSON.stringify(array));
  } catch (error) {
    console.warn('[useNotifications] Failed to save viewed state', error);
  }
}

// Глобальный флаг для отслеживания первой загрузки модуля
let isFirstLoad = true;

export function useNotifications() {
  const [notifications] = useState<Notification[]>(() => loadNotifications());
  const [viewedIds, setViewedIds] = useState<Set<string>>(() => {
    // При каждой загрузке страницы сбрасываем просмотренные уведомления
    // sessionStorage сохраняется между перезагрузками страницы в той же вкладке
    // поэтому нужно синхронно очищать ключ при первой инициализации
    if (typeof window !== 'undefined') {
      // При первой загрузке модуля (после перезагрузки страницы) удаляем флаг
      if (isFirstLoad) {
        sessionStorage.removeItem('notifications-viewed-this-load');
        isFirstLoad = false;
      }
      
      const viewedInThisLoad = sessionStorage.getItem('notifications-viewed-this-load');
      
      // Если уведомления не были просмотрены в этой загрузке страницы, показываем красную точку
      if (!viewedInThisLoad) {
        return new Set(); // Возвращаем пустой Set, чтобы показать красную точку
      }
      
      // Если были просмотрены в этой загрузке, загружаем из localStorage (для сохранения состояния)
      return loadViewedState();
    }
    return new Set();
  });

  const hasUnreadNotifications = notifications.some((n) => !viewedIds.has(n.id));

  const markAsRead = useCallback(() => {
    const allIds = new Set(notifications.map((n) => n.id));
    setViewedIds(allIds);
    saveViewedState(allIds);
    
    // Помечаем, что уведомления были просмотрены в этой загрузке страницы
    // Это скроет красную точку до следующей перезагрузки
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('notifications-viewed-this-load', 'true');
    }
  }, [notifications]);

  // Сохраняем уведомления при первой загрузке
  useEffect(() => {
    saveNotifications(notifications);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Сохраняем состояние просмотра при изменении
  useEffect(() => {
    saveViewedState(viewedIds);
  }, [viewedIds]);

  return {
    notifications,
    hasUnreadNotifications,
    markAsRead,
  };
}

