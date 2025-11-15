import { useEffect, useMemo, useRef, useState } from 'react';

import { apiClient } from '@components/api/client';
import styles from './TeachersPage.module.scss';

type TeacherListItem = {
  id: string;
  name: string;
};

type TeachersPageProps = {
  userId: number;
  onSelectTeacher?: (teacherId: string) => void;
};

const PAGE_SIZE = 10;
const CACHE_KEY_PREFIX = 'max-app-teachers-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedTeachers(userId: number): TeacherListItem[] | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as { teachers: TeacherListItem[]; timestamp: number };
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed.teachers;
  } catch (error) {
    console.warn('[TeachersPage] Failed to load cached teachers', error);
    return null;
  }
}

function saveCachedTeachers(userId: number, teachers: TeacherListItem[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cacheValue = {
      teachers,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[TeachersPage] Failed to save cached teachers', error);
  }
}

export function TeachersPage({ userId, onSelectTeacher }: TeachersPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedTeachers = loadCachedTeachers(userId);
  const [teachers, setTeachers] = useState<TeacherListItem[]>(cachedTeachers || []);
  const [loading, setLoading] = useState(!cachedTeachers); // Показываем загрузку только если нет кэша
  const [query, setQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const loaderRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadTeachers() {
      try {
        const response = await apiClient.getTeachers(userId);

        if (isCancelled) {
          return;
        }

        let newTeachers: TeacherListItem[] = [];

        if (response.success && response.teachers) {
          newTeachers = response.teachers;
        }

        // Сохраняем в кэш
        if (newTeachers.length > 0) {
          saveCachedTeachers(userId, newTeachers);
        }

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          if (newTeachers.length > 0) {
            setTeachers(newTeachers);
          }
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[TeachersPage] Failed to load teachers', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    loadTeachers();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  const filteredTeachers = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) {
      return teachers;
    }

    return teachers.filter((teacher) => teacher.name.toLowerCase().includes(value));
  }, [query, teachers]);

  const displayedTeachers = useMemo(
    () => filteredTeachers.slice(0, visibleCount),
    [filteredTeachers, visibleCount],
  );

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [query]);

  useEffect(() => {
    const node = loaderRef.current;
    if (!node) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setVisibleCount((count) => {
            if (count >= filteredTeachers.length) {
              return count;
            }
            return Math.min(filteredTeachers.length, count + PAGE_SIZE);
          });
        }
      },
      {
        rootMargin: '120px',
      },
    );

    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, [filteredTeachers.length]);

  const handleSelect = (teacher: TeacherListItem) => {
    onSelectTeacher?.(teacher.id);
  };

  // Показываем "Загрузка данных" если данные загружаются
  if (loading && teachers.length === 0) {
    return (
      <div className={styles.page}>
        <p className={styles.empty}>Загрузка данных...</p>
      </div>
    );
  }

  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (scrollToElement === 'teachers') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="teachers"]') || document.body.firstElementChild;
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
    <div className={styles.page} data-section="teachers">
      <div className={styles.search}>
        <input
          type="search"
          className={styles.searchInput}
          placeholder="Поиск преподавателя"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>

      {displayedTeachers.length > 0 ? (
        <ul className={styles.list}>
          {displayedTeachers.map((teacher) => (
            <li key={teacher.id}>
              <button type="button" className={styles.card} onClick={() => handleSelect(teacher)}>
                <span className={styles.name}>{teacher.name}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : teachers.length === 0 ? (
        <p className={styles.empty}>Загрузка данных...</p>
      ) : (
        <p className={styles.empty}>Преподаватели не найдены</p>
      )}

      <div ref={loaderRef} aria-hidden="true" />
    </div>
  );
}


