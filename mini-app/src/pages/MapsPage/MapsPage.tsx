import { useEffect, useState } from 'react';
import { apiClient } from '@components/api/client';
import styles from './MapsPage.module.scss';

type BuildingMap = {
  name: string;
  latitude: number;
  longitude: number;
  yandex_map_url: string;
  gis2_map_url: string;
  google_map_url: string;
};

type MapsPageProps = {
  userId: number;
};

type CachedMapsData = {
  buildings: BuildingMap[];
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-maps-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedMaps(userId: number): BuildingMap[] | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as CachedMapsData;
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed.buildings;
  } catch (error) {
    console.warn('[MapsPage] Failed to load cached maps', error);
    return null;
  }
}

function saveCachedMaps(userId: number, buildings: BuildingMap[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cacheValue: CachedMapsData = {
      buildings,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[MapsPage] Failed to save cached maps', error);
  }
}

export function MapsPage({ userId }: MapsPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedBuildings = loadCachedMaps(userId);
  const [buildings, setBuildings] = useState<BuildingMap[]>(cachedBuildings || []);
  const [loading, setLoading] = useState(!cachedBuildings); // Показываем загрузку только если нет кэша

  useEffect(() => {
    let isCancelled = false;

    async function loadMaps() {
      try {
        const response = await apiClient.getMaps(userId);

        if (isCancelled) {
          return;
        }

        const newBuildings = response.buildings || [];

        // Сохраняем в кэш
        if (newBuildings.length > 0) {
          saveCachedMaps(userId, newBuildings);
        }

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setBuildings(newBuildings);
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[MapsPage] Failed to load maps', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    loadMaps();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  const handleMapClick = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  // Показываем "Загрузка данных" если данные загружаются
  if (loading && buildings.length === 0) {
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
    if (scrollToElement === 'maps') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="maps"]') || document.body.firstElementChild;
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
    <div className={styles.page} data-section="maps">
      {buildings.length > 0 ? (
        <div className={styles.list}>
          {buildings.map((building, index) => (
            <div key={index} className={styles.card}>
              <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>{building.name}</h3>
              </div>
              <div className={styles.cardContent}>
                <div className={styles.mapButtons}>
                  <button
                    type="button"
                    className={styles.mapButton}
                    onClick={() => handleMapClick(building.yandex_map_url)}
                  >
                    <span className={styles.mapButtonIcon}>🗺️</span>
                    <span className={styles.mapButtonLabel}>Яндекс Карты</span>
                  </button>
                  <button
                    type="button"
                    className={styles.mapButton}
                    onClick={() => handleMapClick(building.gis2_map_url)}
                  >
                    <span className={styles.mapButtonIcon}>📍</span>
                    <span className={styles.mapButtonLabel}>2ГИС</span>
                  </button>
                  <button
                    type="button"
                    className={styles.mapButton}
                    onClick={() => handleMapClick(building.google_map_url)}
                  >
                    <span className={styles.mapButtonIcon}>🌍</span>
                    <span className={styles.mapButtonLabel}>Google Maps</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className={styles.loading}>Карты не найдены</p>
      )}
    </div>
  );
}

