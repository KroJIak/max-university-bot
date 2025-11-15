import { useEffect, useState } from 'react';
import { PrimaryServicesSection } from '@components/Services';
import type { ServiceItem } from '@components/Services';
import { apiClient } from '@components/api/client';
import { platformServices } from '@shared/data/services';
import styles from './PlatformsPage.module.scss';

type PlatformsPageProps = {
  userId: number;
};

type CachedPlatformsData = {
  platforms: ServiceItem[];
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-services-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedPlatforms(userId: number): ServiceItem[] | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as { platforms?: ServiceItem[]; timestamp: number };
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS || !parsed.platforms) {
      return null;
    }

    return parsed.platforms;
  } catch (error) {
    console.warn('[PlatformsPage] Failed to load cached platforms', error);
    return null;
  }
}

function saveCachedPlatforms(userId: number, platforms: ServiceItem[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const existing = window.localStorage.getItem(cacheKey);
    let cacheValue: { services?: ServiceItem[]; platforms: ServiceItem[]; timestamp: number };

    if (existing) {
      try {
        cacheValue = JSON.parse(existing);
      } catch {
        cacheValue = { platforms: [], timestamp: Date.now() };
      }
    } else {
      cacheValue = { platforms: [], timestamp: Date.now() };
    }

    cacheValue.platforms = platforms;
    cacheValue.timestamp = Date.now();
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[PlatformsPage] Failed to save cached platforms', error);
  }
}

export function PlatformsPage({ userId }: PlatformsPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedPlatforms = loadCachedPlatforms(userId);
  const [platforms, setPlatforms] = useState<ServiceItem[]>(cachedPlatforms || []);
  const [loading, setLoading] = useState(!cachedPlatforms); // Показываем загрузку только если нет кэша

  useEffect(() => {
    let isCancelled = false;

    async function loadPlatforms() {
      try {
        const response = await apiClient.getPlatforms(userId);

        if (isCancelled) {
          return;
        }

        let newPlatforms: ServiceItem[] = [];

        // Преобразуем платформы из API в формат ServiceItem
        if (response.success && response.platforms) {
          newPlatforms = response.platforms.map((platform) => ({
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
        saveCachedPlatforms(userId, newPlatforms);

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setPlatforms(newPlatforms);
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[PlatformsPage] Failed to load platforms', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          // Если нет текущих данных, используем дефолтные
          if (platforms.length === 0) {
            setPlatforms(platformServices);
          }
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    loadPlatforms();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  const handlePlatformSelect = (item: ServiceItem) => {
    // Если у платформы есть URL, открываем его
    if (item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
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
    if (scrollToElement === 'platforms') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="platforms"]') || document.body.firstElementChild;
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
    <div className={styles.page} data-section="platforms">
      {platforms.length > 0 && (
        <PrimaryServicesSection
          title="Веб-платформы"
          items={platforms}
          showMoreButton={false}
          hideTitle
          onItemSelect={handlePlatformSelect}
        />
      )}
    </div>
  );
}


