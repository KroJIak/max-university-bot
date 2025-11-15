import { useEffect, useState } from 'react';
import type { ServiceItem } from '@components/Services';
import { PrimaryServicesSection } from '@components/Services';
import { apiClient } from '@components/api/client';
import { primaryServices } from '@shared/data/services';
import styles from './PrimaryServicesPage.module.scss';

type PrimaryServicesPageProps = {
  userId: number;
  onOpenSchedule?: () => void;
  onOpenTeachers?: () => void;
  onOpenChats?: () => void;
  onOpenContacts?: () => void;
  onOpenMaps?: () => void;
  onOpenClubs?: () => void;
};

type CachedServicesData = {
  services: ServiceItem[];
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-services-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedServices(userId: number): ServiceItem[] | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as { services?: ServiceItem[]; timestamp: number };
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS || !parsed.services) {
      return null;
    }

    return parsed.services;
  } catch (error) {
    console.warn('[PrimaryServicesPage] Failed to load cached services', error);
    return null;
  }
}

function saveCachedServices(userId: number, services: ServiceItem[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const existing = window.localStorage.getItem(cacheKey);
    let cacheValue: { services: ServiceItem[]; platforms?: ServiceItem[]; timestamp: number };

    if (existing) {
      try {
        cacheValue = JSON.parse(existing);
      } catch {
        cacheValue = { services: [], timestamp: Date.now() };
      }
    } else {
      cacheValue = { services: [], timestamp: Date.now() };
    }

    cacheValue.services = services;
    cacheValue.timestamp = Date.now();
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[PrimaryServicesPage] Failed to save cached services', error);
  }
}

export function PrimaryServicesPage({ userId, onOpenSchedule, onOpenTeachers, onOpenChats, onOpenContacts, onOpenMaps, onOpenClubs }: PrimaryServicesPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedServices = loadCachedServices(userId);
  const [services, setServices] = useState<ServiceItem[]>(cachedServices || []);
  const [loading, setLoading] = useState(!cachedServices); // Показываем загрузку только если нет кэша

  useEffect(() => {
    let isCancelled = false;

    async function loadServices() {
      try {
        const response = await apiClient.getServices(userId);

        if (isCancelled) {
          return;
        }

        let newServices: ServiceItem[] = [];

        // Преобразуем сервисы из API в формат ServiceItem
        if (response.success && response.services) {
          newServices = response.services.map((service) => {
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
          }
          
          console.log('[PrimaryServicesPage] Loaded services from API:', newServices);
        } else {
          // Используем данные по умолчанию только при ошибке или отсутствии данных
          newServices = primaryServices;
          console.log('[PrimaryServicesPage] Using default services:', newServices);
        }

        // Сохраняем в кэш
        saveCachedServices(userId, newServices);

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setServices(newServices);
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[PrimaryServicesPage] Failed to load services', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          // Если нет текущих данных, используем дефолтные
          if (services.length === 0) {
            setServices(primaryServices);
          }
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    loadServices();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  const handleSelect = (item: ServiceItem) => {
    if (item.id === 'schedule') {
      onOpenSchedule?.();
      return;
    }

    if (item.id === 'teachers') {
      onOpenTeachers?.();
      return;
    }

    if (item.id === 'chat') {
      onOpenChats?.();
      return;
    }

    if (item.id === 'contacts') {
      onOpenContacts?.();
      return;
    }

    if (item.id === 'map') {
      onOpenMaps?.();
      return;
    }

    if (item.id === 'clubs') {
      console.log('[PrimaryServicesPage] Opening clubs page');
      onOpenClubs?.();
      return;
    }
  };

  // Не показываем компонент, пока данные загружаются
  if (loading) {
    return null;
  }

  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (scrollToElement === 'primary-services') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="primary-services"]') || document.body.firstElementChild;
        if (element) {
          const elementRect = element.getBoundingClientRect();
          const absoluteElementTop = elementRect.top + window.pageYOffset;
          const middle = absoluteElementTop - (window.innerHeight / 2) + (elementRect.height / 2);
          window.scrollTo({
            top: Math.max(0, middle),
            behavior: 'smooth'
          });
        }
        sessionStorage.removeItem('scrollToElement');
      }, 300);
      return () => clearTimeout(timeoutId);
    }
  }, []);

  return (
    <div className={styles.page} data-section="primary-services">
      {services.length > 0 && (
        <PrimaryServicesSection
          title="Основные сервисы"
          items={services}
          showMoreButton={false}
          hideTitle
          onItemSelect={handleSelect}
        />
      )}
    </div>
  );
}


