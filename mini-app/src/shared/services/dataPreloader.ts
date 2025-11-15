import { apiClient } from '@components/api/client';
import { formatDateRangeForApi } from '@shared/utils/scheduleApi';

/**
 * Сервис для предзагрузки данных в фоне
 * Загружает все данные сразу после логина, чтобы при открытии страниц они уже были в кэше
 */
type BackgroundUpdateHandle = {
  interval: ReturnType<typeof setInterval>;
  visibilityHandler: () => void;
};

export class DataPreloader {
  private static preloadInProgress = new Set<number>();
  private static backgroundIntervals = new Map<number, BackgroundUpdateHandle>();
  private static lastPreloadTime = new Map<number, number>();

  // Интервал проверки и обновления данных в фоне (каждые 5 минут)
  private static readonly BACKGROUND_CHECK_INTERVAL_MS = 5 * 60 * 1000;
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
    // Проверяем, не запущены ли уже обновления для этого пользователя
    const existingHandle = this.backgroundIntervals.get(userId);
    if (existingHandle) {
      console.log('[DataPreloader] Background updates already running for user', userId, '- skipping restart');
      return;
    }

    console.log('[DataPreloader] Starting background updates for user', userId);

    // Первая проверка сразу
    this.checkAndUpdateIfNeeded(userId);

    // Затем периодически
    const interval = setInterval(() => {
      console.log('[DataPreloader] Periodic check triggered (every 5 minutes)');
      this.checkAndUpdateIfNeeded(userId);
    }, this.BACKGROUND_CHECK_INTERVAL_MS);

    // Также обновляем при возвращении фокуса на окно
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('[DataPreloader] Window became visible, checking for updates');
        this.checkAndUpdateIfNeeded(userId);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Сохраняем интервал и обработчик вместе
    this.backgroundIntervals.set(userId, {
      interval,
      visibilityHandler: handleVisibilityChange,
    });
    
    console.log('[DataPreloader] Background updates started, interval:', this.BACKGROUND_CHECK_INTERVAL_MS, 'ms');
  }

  /**
   * Останавливает периодическое обновление данных для пользователя
   */
  static stopBackgroundUpdates(userId: number): void {
    const handle = this.backgroundIntervals.get(userId);
    if (handle) {
      clearInterval(handle.interval);
      document.removeEventListener('visibilitychange', handle.visibilityHandler);
      this.backgroundIntervals.delete(userId);
      console.log('[DataPreloader] Stopped background updates for user', userId);
    }
  }

  /**
   * Проверяет кэши и обновляет данные, если они устарели
   * Также проверяет статус сессии
   */
  private static checkAndUpdateIfNeeded(userId: number): void {
    // Проверяем статус сессии в фоне (асинхронно)
    this.checkSessionStatus(userId).catch((error) => {
      console.warn('[DataPreloader] Failed to check session status', error);
    });

    // Проверяем, нужно ли обновлять данные
    const needsUpdate = this.checkCacheExpiration(userId);

    if (needsUpdate) {
      console.log('[DataPreloader] Cache expired or missing, updating data in background for user', userId);
      this.preloadAllData(userId, false).catch((error) => {
        console.error('[DataPreloader] Failed to update data in background', error);
      });
    } else {
      console.log('[DataPreloader] All caches are fresh, skipping update');
    }
  }

  /**
   * Проверяет статус сессии пользователя
   */
  private static async checkSessionStatus(userId: number): Promise<void> {
    try {
      const { apiClient } = await import('@components/api/client');
      const status = await apiClient.getStudentStatus(userId);
      
      if (!status.is_linked) {
        // Сессия невалидна, очищаем localStorage от данных этого пользователя
        console.warn('[DataPreloader] Session is not linked for user', userId);
        this.clearUserCache(userId);
      }
    } catch (error) {
      console.warn('[DataPreloader] Failed to check session status', error);
    }
  }

  /**
   * Очищает кэш пользователя при разрыве связи
   */
  private static clearUserCache(userId: number): void {
    if (typeof window === 'undefined') {
      return;
    }

    const cacheKeys = [
      `max-app-profile-${userId}`,
      `max-app-services-${userId}`,
      `max-app-teachers-${userId}`,
      `max-app-contacts-${userId}`,
      `max-app-maps-${userId}`,
      `max-app-schedule-main-${userId}`,
    ];

    for (const key of cacheKeys) {
      try {
        window.localStorage.removeItem(key);
      } catch (error) {
        console.warn('[DataPreloader] Failed to clear cache key', key, error);
      }
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
          console.log(`[DataPreloader] Cache missing for ${cacheKey}, need update`);
          return true;
        }

        const parsed = JSON.parse(cached) as { timestamp?: number };
        if (!parsed.timestamp || typeof parsed.timestamp !== 'number') {
          // Если timestamp отсутствует или некорректен, нужно обновить
          console.log(`[DataPreloader] Cache missing timestamp for ${cacheKey}, need update`);
          return true;
        }

        const age = now - parsed.timestamp;
        if (age > CACHE_TIMEOUT_MS) {
          // Кэш устарел, нужно обновить
          console.log(`[DataPreloader] Cache expired for ${cacheKey} (age: ${Math.round(age / 1000)}s), need update`);
          return true;
        }
      } catch (error) {
        // Если ошибка парсинга, считаем что нужно обновить
        console.warn(`[DataPreloader] Failed to parse cache for ${cacheKey}:`, error);
        return true;
      }
    }

    // Все кэши свежие
    console.log('[DataPreloader] All caches are fresh, no update needed');
    return false;
  }

  /**
   * Предзагружает данные профиля
   */
  private static async preloadProfile(userId: number): Promise<void> {
    try {
      const response = await apiClient.getPersonalData(userId);
      
      // Сохраняем в кэш в том же формате, что и ProfilePage
      if (typeof window !== 'undefined') {
        try {
          // Импортируем функцию преобразования данных
          const { transformApiResponseToProfileData } = await import('../../pages/ProfilePage/ProfilePage');
          
          const transformedData = transformApiResponseToProfileData(
            userId,
            response.success ? response.data : null,
          );
          
          const cacheKey = `max-app-profile-${userId}`;
          const cacheValue = {
            data: transformedData,
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
          console.log('[DataPreloader] Profile data preloaded and cached');
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save profile to cache', cacheError);
        }
      }
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload profile data', error);
    }
  }

  /**
   * Предзагружает сервисы и платформы
   */
  private static async preloadServices(userId: number): Promise<void> {
    try {
      const [servicesResponse, platformsResponse] = await Promise.all([
        apiClient.getServices(userId),
        apiClient.getPlatforms(userId),
      ]);
      
      // Сохраняем в кэш в том же формате, что и ServicesPage
      if (typeof window !== 'undefined') {
        try {
          // Импортируем функции преобразования данных
          const { primaryServices, platformServices } = await import('@shared/data/services');
          
          // Преобразуем сервисы из API в формат ServiceItem (как в ServicesPage)
          let transformedServices: any[] = [];
          if (servicesResponse.success && servicesResponse.services) {
            transformedServices = servicesResponse.services.map((service) => {
              let normalizedId = service.key;
              if (service.key === 'chats' || service.name?.toLowerCase().includes('чат')) {
                normalizedId = 'chat';
              }
              return {
                id: normalizedId,
                title: service.name,
                icon: service.emoji,
              };
            });
            
            // Добавляем кнопку "клубы" после подгрузки бэка, если её ещё нет
            const hasClubs = transformedServices.some(service => 
              service.id === 'clubs' || 
              service.id === 'клубы' || 
              service.title?.toLowerCase().includes('клуб')
            );
            if (!hasClubs) {
              transformedServices.push({
                id: 'clubs',
                title: 'Клубы',
                icon: '🎭',
              });
            }
          } else {
            transformedServices = primaryServices;
          }

          // Преобразуем платформы из API в формат ServiceItem (как в ServicesPage)
          let transformedPlatforms: any[] = [];
          if (platformsResponse.success && platformsResponse.platforms) {
            transformedPlatforms = platformsResponse.platforms.map((platform) => ({
              id: platform.key,
              title: platform.name,
              icon: platform.emoji,
              url: platform.url,
            }));
          } else {
            transformedPlatforms = platformServices;
          }
          
          const cacheKey = `max-app-services-${userId}`;
          const cacheValue = {
            services: transformedServices,
            platforms: transformedPlatforms,
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
          console.log('[DataPreloader] Services data preloaded and cached:', {
            servicesCount: transformedServices.length,
            platformsCount: transformedPlatforms.length,
            timestamp: cacheValue.timestamp,
            cacheKey
          });
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save services to cache', cacheError);
        }
      }
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload services data', error);
    }
  }

  /**
   * Предзагружает список преподавателей
   */
  private static async preloadTeachers(userId: number): Promise<void> {
    try {
      const response = await apiClient.getTeachers(userId);
      
      // Сохраняем в кэш
      if (typeof window !== 'undefined' && response.success && response.teachers) {
        try {
          const cacheKey = `max-app-teachers-${userId}`;
          const cacheValue = {
            teachers: response.teachers,
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save teachers to cache', cacheError);
        }
      }
      
      console.log('[DataPreloader] Teachers data preloaded and cached');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload teachers data', error);
    }
  }

  /**
   * Предзагружает контакты
   */
  private static async preloadContacts(userId: number): Promise<void> {
    try {
      const response = await apiClient.getContacts(userId);
      
      // Сохраняем в кэш
      if (typeof window !== 'undefined' && response.success) {
        try {
          const cacheKey = `max-app-contacts-${userId}`;
          const cacheValue = {
            deans: response.deans || [],
            departments: response.departments || [],
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save contacts to cache', cacheError);
        }
      }
      
      console.log('[DataPreloader] Contacts data preloaded and cached');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload contacts data', error);
    }
  }

  /**
   * Предзагружает карты
   */
  private static async preloadMaps(userId: number): Promise<void> {
    try {
      const response = await apiClient.getMaps(userId);
      
      // Сохраняем в кэш
      if (typeof window !== 'undefined' && response.buildings) {
        try {
          const cacheKey = `max-app-maps-${userId}`;
          const cacheValue = {
            buildings: response.buildings,
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save maps to cache', cacheError);
        }
      }
      
      console.log('[DataPreloader] Maps data preloaded and cached');
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
      const response = await apiClient.getSchedule(userId, dateRange);
      
      // Сохраняем в кэш в том же формате, что и MainPage
      if (typeof window !== 'undefined' && response.success && response.schedule) {
        try {
          const {
            transformScheduleItemFromApi,
            groupScheduleByDate,
            getTodayTomorrowAfterTomorrow,
            formatDateToKey,
          } = await import('@shared/utils/scheduleApi');
          const items = response.schedule.map(transformScheduleItemFromApi);
          const grouped = groupScheduleByDate(items);

          const { today, tomorrow, afterTomorrow } = getTodayTomorrowAfterTomorrow();
          const todayKey = formatDateToKey(today);
          const tomorrowKey = formatDateToKey(tomorrow);
          const afterTomorrowKey = formatDateToKey(afterTomorrow);

          const cacheKey = `max-app-schedule-main-${userId}`;
          const cacheValue = {
            scheduleByTab: {
              today: grouped[todayKey] || [],
              tomorrow: grouped[tomorrowKey] || [],
              afterTomorrow: grouped[afterTomorrowKey] || [],
            },
            timestamp: Date.now(),
          };
          window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
        } catch (cacheError) {
          console.warn('[DataPreloader] Failed to save schedule to cache', cacheError);
        }
      }
      
      console.log('[DataPreloader] Schedule data preloaded and cached');
    } catch (error) {
      console.warn('[DataPreloader] Failed to preload schedule data', error);
    }
  }
}

