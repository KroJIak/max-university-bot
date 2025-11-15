import { useEffect, useState } from 'react';
import { PlatformsSection, PrimaryServicesSection } from '@components/Services';
import type { ServiceItem } from '@components/Services';
import { apiClient } from '@components/api/client';
import { platformServices, primaryServices } from '@shared/data/services';
import styles from './ServicesPage.module.scss';

type ServicesPageProps = {
  userId: number;
  onOpenSchedule?: () => void;
  onOpenPrimaryServices?: () => void;
  onOpenPlatforms?: () => void;
  onOpenTeachers?: () => void;
  onOpenChats?: () => void;
  onOpenContacts?: () => void;
  onOpenMaps?: () => void;
  onOpenClubs?: () => void;
};

type CachedServicesData = {
  services: ServiceItem[];
  platforms: ServiceItem[];
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-services-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedData(userId: number): CachedServicesData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as CachedServicesData;
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed;
  } catch (error) {
    console.warn('[ServicesPage] Failed to load cached data', error);
    return null;
  }
}

function saveCachedData(userId: number, services: ServiceItem[], platforms: ServiceItem[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cacheValue: CachedServicesData = {
      services,
      platforms,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[ServicesPage] Failed to save cached data', error);
  }
}

export function ServicesPage({
  userId,
  onOpenSchedule,
  onOpenPrimaryServices,
  onOpenPlatforms,
  onOpenTeachers,
  onOpenChats,
  onOpenContacts,
  onOpenMaps,
  onOpenClubs,
}: ServicesPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedData = loadCachedData(userId);
  console.log('[ServicesPage] Loaded cached data:', {
    hasCache: !!cachedData,
    servicesCount: cachedData?.services?.length || 0,
    platformsCount: cachedData?.platforms?.length || 0,
    cacheAge: cachedData ? Math.round((Date.now() - cachedData.timestamp) / 1000) : null,
    userId
  });
  // Инициализируем состояние с проверкой наличия кнопки "клубы"
  const initialServices = cachedData?.services || [];
  const hasClubsInitially = initialServices.some(service => 
    service.id === 'clubs' || 
    service.id === 'клубы' || 
    service.title?.toLowerCase().includes('клуб')
  );
  const servicesWithClubs = hasClubsInitially 
    ? initialServices 
    : [...initialServices, { id: 'clubs', title: 'Клубы', icon: '🎭' }];
  
  const [services, setServices] = useState<ServiceItem[]>(servicesWithClubs);
  const [platforms, setPlatforms] = useState<ServiceItem[]>(cachedData?.platforms || []);
  const [loading, setLoading] = useState(!cachedData); // Показываем загрузку только если нет кэша

  useEffect(() => {
    let isCancelled = false;
    let timeoutId: NodeJS.Timeout | null = null;

    // Если кэш есть, показываем его сразу и обновляем в фоне только если кэш старше 4 минут
    if (cachedData) {
      // Проверяем, есть ли кнопка "клубы" в кэшированных данных
      const hasClubsInCache = cachedData.services.some(service => 
        service.id === 'clubs' || 
        service.id === 'клубы' || 
        service.title?.toLowerCase().includes('клуб')
      );
      
      // Если кнопки "клубы" нет в кэше, добавляем её
      let servicesToShow = cachedData.services;
      if (!hasClubsInCache) {
        servicesToShow = [...cachedData.services, {
          id: 'clubs',
          title: 'Клубы',
          icon: '🎭',
        }];
        console.log('[ServicesPage] Added clubs button to cached services');
      }
      
      setServices(servicesToShow);
      setPlatforms(cachedData.platforms);
      setLoading(false);
      
      // Обновляем данные в фоне только если кэш старше 4 минут (чтобы не дублировать запросы с DataPreloader)
      const cacheAge = Date.now() - cachedData.timestamp;
      const shouldRefresh = cacheAge > 4 * 60 * 1000; // 4 минуты
      
      if (shouldRefresh) {
        async function refreshInBackground() {
          try {
            const [servicesResponse, platformsResponse] = await Promise.all([
              apiClient.getServices(userId),
              apiClient.getPlatforms(userId),
            ]);

            if (isCancelled) {
              return;
            }

            let newServices: ServiceItem[] = [];
            let newPlatforms: ServiceItem[] = [];

            // Преобразуем сервисы из API в формат ServiceItem
            if (servicesResponse.success && servicesResponse.services) {
              newServices = servicesResponse.services.map((service) => {
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
              const hasClubs = newServices.some(service => 
                service.id === 'clubs' || 
                service.id === 'клубы' || 
                service.title?.toLowerCase().includes('клуб')
              );
              if (!hasClubs) {
                newServices.push({
                  id: 'clubs',
                  title: 'Клубы',
                  icon: '🎭',
                });
                console.log('[ServicesPage] Added clubs button to services list (background refresh)');
              } else {
                console.log('[ServicesPage] Clubs button already exists in services list (background refresh)');
              }
            } else {
              newServices = primaryServices;
            }

            // Преобразуем платформы из API в формат ServiceItem
            if (platformsResponse.success && platformsResponse.platforms) {
              newPlatforms = platformsResponse.platforms.map((platform) => ({
                id: platform.key,
                title: platform.name,
                icon: platform.emoji,
                url: platform.url,
              }));
            } else {
              newPlatforms = platformServices;
            }

            // Сохраняем в кэш
            saveCachedData(userId, newServices, newPlatforms);

            // Обновляем состояние только если компонент ещё смонтирован
            if (!isCancelled) {
              setServices(newServices);
              setPlatforms(newPlatforms);
            }
          } catch (error) {
            console.error('[ServicesPage] Failed to refresh services in background', error);
          }
        }
        
        // Обновляем в фоне с задержкой
        timeoutId = setTimeout(() => {
          refreshInBackground();
        }, 1000);
        
        return () => {
          isCancelled = true;
          if (timeoutId) {
            clearTimeout(timeoutId);
          }
        };
      }
      return;
    }

    // Кэша нет, загружаем сразу
    async function loadServices() {
      try {
        const [servicesResponse, platformsResponse] = await Promise.all([
          apiClient.getServices(userId),
          apiClient.getPlatforms(userId),
        ]);

        if (isCancelled) {
          return;
        }

        let newServices: ServiceItem[] = [];
        let newPlatforms: ServiceItem[] = [];

        // Преобразуем сервисы из API в формат ServiceItem
        if (servicesResponse.success && servicesResponse.services) {
          newServices = servicesResponse.services.map((service) => {
            // Нормализуем ключ для чатов (может быть разные варианты с бэка)
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
          const hasClubs = newServices.some(service => 
            service.id === 'clubs' || 
            service.id === 'клубы' || 
            service.title?.toLowerCase().includes('клуб')
          );
          if (!hasClubs) {
            newServices.push({
              id: 'clubs',
              title: 'Клубы',
              icon: '🎭',
            });
            console.log('[ServicesPage] Added clubs button to services list');
          } else {
            console.log('[ServicesPage] Clubs button already exists in services list');
          }
          
          console.log('[ServicesPage] Loaded services from API:', newServices);
        } else {
          // Используем данные по умолчанию только при ошибке или отсутствии данных
          newServices = primaryServices;
          console.log('[ServicesPage] Using default services:', newServices);
        }

        // Преобразуем платформы из API в формат ServiceItem
        if (platformsResponse.success && platformsResponse.platforms) {
          newPlatforms = platformsResponse.platforms.map((platform) => ({
            id: platform.key,
            title: platform.name,
            icon: platform.emoji,
            url: platform.url,
          }));
        } else {
          // Используем данные по умолчанию только при ошибке или отсутствии данных
          newPlatforms = platformServices;
        }

        // Сохраняем в кэш
        saveCachedData(userId, newServices, newPlatforms);

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setServices(newServices);
          setPlatforms(newPlatforms);
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[ServicesPage] Failed to load services and platforms', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          // Если нет текущих данных, используем дефолтные
          if (services.length === 0) {
            setServices(primaryServices);
          }
          if (platforms.length === 0) {
            setPlatforms(platformServices);
          }
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    loadServices();

    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  const handlePrimarySelect = (item: ServiceItem) => {
    console.log('[ServicesPage] handlePrimarySelect called with item:', item);
    console.log('[ServicesPage] Available handlers:', {
      onOpenSchedule: !!onOpenSchedule,
      onOpenTeachers: !!onOpenTeachers,
      onOpenChats: !!onOpenChats,
      onOpenContacts: !!onOpenContacts,
      onOpenMaps: !!onOpenMaps,
      onOpenClubs: !!onOpenClubs,
    });
    if (item.id === 'schedule') {
      onOpenSchedule?.();
      return;
    }
    if (item.id === 'teachers') {
      onOpenTeachers?.();
      return;
    }
    if (item.id === 'chat') {
      console.log('[ServicesPage] Opening chats page');
      onOpenChats?.();
      return;
    }
    if (item.id === 'contacts') {
      console.log('[ServicesPage] Opening contacts page');
      onOpenContacts?.();
      return;
    }
    if (item.id === 'map') {
      console.log('[ServicesPage] Opening maps page');
      onOpenMaps?.();
      return;
    }
    if (item.id === 'clubs') {
      console.log('[ServicesPage] Opening clubs page, onOpenClubs:', onOpenClubs);
      if (onOpenClubs) {
        onOpenClubs();
      } else {
        console.error('[ServicesPage] onOpenClubs is not defined!');
      }
      return;
    }
    console.log('[ServicesPage] No handler for item.id:', item.id);
  };

  const handlePlatformSelect = (item: ServiceItem) => {
    // Если у платформы есть URL, открываем его
    if (item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
    }
  };

  // Показываем "Загрузка данных" если данные загружаются
  if (loading && services.length === 0 && platforms.length === 0) {
    return (
      <div className={styles.page}>
        <p className={styles.loading}>Загрузка данных...</p>
      </div>
    );
  }

  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (!scrollToElement) return;

    const timeoutId = setTimeout(() => {
      const element = document.querySelector(`[data-section="${scrollToElement}"]`);
      if (element) {
        const elementRect = element.getBoundingClientRect();
        const absoluteElementTop = elementRect.top + window.pageYOffset;
        const middle = absoluteElementTop - (window.innerHeight / 2) + (elementRect.height / 2);
        window.scrollTo({
          top: Math.max(0, middle),
          behavior: 'smooth'
        });
        
        // Подсвечиваем элемент
        (element as HTMLElement).style.transition = 'background-color 0.3s ease';
        (element as HTMLElement).style.backgroundColor = 'var(--color-surface-hover)';
        setTimeout(() => {
          (element as HTMLElement).style.backgroundColor = '';
        }, 2000);
      }
      sessionStorage.removeItem('scrollToElement');
    }, 300);

    return () => clearTimeout(timeoutId);
  }, []);

  return (
    <div className={styles.page}>
      {services.length > 0 && (
        <div data-section="primary-services">
          <PrimaryServicesSection
            title="Основные сервисы"
            items={services}
            onOpen={onOpenPrimaryServices}
            onItemSelect={handlePrimarySelect}
          />
        </div>
      )}
      {platforms.length > 0 && (
        <div data-section="platforms">
          <PlatformsSection
            title="Веб-платформы"
            items={platforms}
            onOpen={onOpenPlatforms}
            onItemSelect={handlePlatformSelect}
          />
        </div>
      )}
      {!loading && services.length === 0 && platforms.length === 0 && (
        <p className={styles.loading}>Загрузка данных...</p>
      )}
    </div>
  );
}

