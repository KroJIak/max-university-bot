import { apiClient } from '@components/api/client';
import { formatDateRangeForApi } from '@shared/utils/scheduleApi';

/**
 * Сервис для предзагрузки данных в фоне
 * Загружает все данные сразу после логина, чтобы при открытии страниц они уже были в кэше
 */
export class DataPreloader {
  private static preloadInProgress = new Set<number>();
  private static backgroundIntervals = new Map<number, NodeJS.Timeout>();
  private static lastPreloadTime = new Map<number, number>();

  // Интервал проверки и обновления данных в фоне (каждые 30 секунд)
  private static readonly BACKGROUND_CHECK_INTERVAL_MS = 30 * 1000;
  // Минимальный интервал между полными обновлениями (4 минуты)
  private static readonly MIN_PRELOAD_INTERVAL_MS = 4 * 60 * 1000;

  /**
   * Предзагружает все данные для пользователя в фоне
   * @param force - принудительная загрузка, даже если недавно уже загружали
   */
  static async preloadAllData(userId: number, force = false): Promise<void> {
    // Предотвращаем параллельные запросы для одного пользователя
    if (this.preloadInProgress.has(userId)) {
      console.log('[DataPreloader] Preload already in progress for user', userId);
      return;
    }

    // Проверяем, не слишком ли часто мы загружаем данные
    if (!force) {
      const lastPreload = this.lastPreloadTime.get(userId);
      const now = Date.now();
      if (lastPreload && now - lastPreload < this.MIN_PRELOAD_INTERVAL_MS) {
        console.log('[DataPreloader] Skipping preload, too soon since last preload');
        return;
      }
    }

    this.preloadInProgress.add(userId);

    try {
      console.log('[DataPreloader] Starting preload for user', userId);

      // Загружаем все данные параллельно в фоне
      await Promise.allSettled([
        this.preloadProfile(userId),
        this.preloadServices(userId),
        this.preloadTeachers(userId),
        this.preloadContacts(userId),
        this.preloadMaps(userId),
        this.preloadSchedule(userId),
      ]);

      this.lastPreloadTime.set(userId, Date.now());
      console.log('[DataPreloader] Preload completed for user', userId);
    } catch (error) {
      console.error('[DataPreloader] Error during preload', error);
    } finally {
      this.preloadInProgress.delete(userId);
    }
  }

  /**
   * Запускает периодическое обновление данных в фоне для пользователя
   */
  static startBackgroundUpdates(userId: number): void {
    // Останавливаем предыдущий интервал, если был
    this.stopBackgroundUpdates(userId);

    console.log('[DataPreloader] Starting background updates for user', userId);

    // Первая проверка сразу
    this.checkAndUpdateIfNeeded(userId);

    // Затем периодически
    const interval = setInterval(() => {
      this.checkAndUpdateIfNeeded(userId);
    }, this.BACKGROUND_CHECK_INTERVAL_MS);

    this.backgroundIntervals.set(userId, interval);

    // Также обновляем при возвращении фокуса на окно
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('[DataPreloader] Window became visible, checking for updates');
        this.checkAndUpdateIfNeeded(userId);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Сохраняем обработчик для последующего удаления
    (interval as any).__visibilityHandler = handleVisibilityChange;
  }

  /**
   * Останавливает периодическое обновление данных для пользователя
   */
  static stopBackgroundUpdates(userId: number): void {
    const interval = this.backgroundIntervals.get(userId);
    if (interval) {
      clearInterval(interval);
      this.backgroundIntervals.delete(userId);

      // Удаляем обработчик события visibilitychange
      const handler = (interval as any).__visibilityHandler;
      if (handler) {
        document.removeEventListener('visibilitychange', handler);
      }

      console.log('[DataPreloader] Stopped background updates for user', userId);
    }
  }

  /**
   * Проверяет кэши и обновляет данные, если они устарели
   */
  private static checkAndUpdateIfNeeded(userId: number): void {
    // Проверяем, нужно ли обновлять данные
    const needsUpdate = this.checkCacheExpiration(userId);

    if (needsUpdate) {
      console.log('[DataPreloader] Cache expired, updating data in background');
      this.preloadAllData(userId, false).catch((error) => {
        console.error('[DataPreloader] Failed to update data in background', error);
      });
    }
  }

  /**
   * Проверяет, устарел ли кэш данных
   */
  private static checkCacheExpiration(userId: number): boolean {
    if (typeof window === 'undefined') {
      return false;
    }

    // Проверяем кэши основных страниц
    const cacheKeys = [
      `max-app-profile-${userId}`,
      `max-app-services-${userId}`,
      `max-app-teachers-${userId}`,
      `max-app-contacts-${userId}`,
      `max-app-maps-${userId}`,
    ];

    const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут
    const now = Date.now();

    for (const cacheKey of cacheKeys) {
      try {
        const cached = window.localStorage.getItem(cacheKey);
        if (!cached) {
          // Если кэша нет, нужно обновить
          return true;
        }

        const parsed = JSON.parse(cached) as { timestamp?: number };
        if (parsed.timestamp) {
          const age = now - parsed.timestamp;
          if (age > CACHE_TIMEOUT_MS) {
            // Кэш устарел, нужно обновить
            return true;
          }
        }
      } catch (error) {
        // Если ошибка парсинга, считаем что нужно обновить
        return true;
      }
    }

    // Все кэши свежие
    return false;
  }

  /**
   * Предзагружает данные профиля
   */
  private static async preloadProfile(userId: number): Promise<void> {
    try {
      await apiClient.getPersonalData(userId);
      console.log('[DataPreloader] Profile data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload profile data', error);
    }
  }

  /**
   * Предзагружает сервисы и платформы
   */
  private static async preloadServices(userId: number): Promise<void> {
    try {
      await Promise.allSettled([
        apiClient.getServices(userId),
        apiClient.getPlatforms(userId),
      ]);
      console.log('[DataPreloader] Services data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload services data', error);
    }
  }

  /**
   * Предзагружает список преподавателей
   */
  private static async preloadTeachers(userId: number): Promise<void> {
    try {
      await apiClient.getTeachers(userId);
      console.log('[DataPreloader] Teachers data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload teachers data', error);
    }
  }

  /**
   * Предзагружает контакты
   */
  private static async preloadContacts(userId: number): Promise<void> {
    try {
      await apiClient.getContacts(userId);
      console.log('[DataPreloader] Contacts data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload contacts data', error);
    }
  }

  /**
   * Предзагружает карты
   */
  private static async preloadMaps(userId: number): Promise<void> {
    try {
      await apiClient.getMaps(userId);
      console.log('[DataPreloader] Maps data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload maps data', error);
    }
  }

  /**
   * Предзагружает расписание (сегодня, завтра, послезавтра)
   */
  private static async preloadSchedule(userId: number): Promise<void> {
    try {
      const today = new Date();
      const afterTomorrow = new Date(today);
      afterTomorrow.setDate(afterTomorrow.getDate() + 2);

      const dateRange = formatDateRangeForApi(today, afterTomorrow);
      await apiClient.getSchedule(userId, dateRange);
      console.log('[DataPreloader] Schedule data preloaded');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload schedule data', error);
    }
  }
}

