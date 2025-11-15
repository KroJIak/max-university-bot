import { useEffect, useState } from 'react';
import { apiClient } from '@components/api/client';
import unknownUserImage from '@shared/data/unknown_user.jpg';
import styles from './TeacherDetailPage.module.scss';

type TeacherDetailPageProps = {
  userId: number;
  teacherId: string;
};

type CachedTeacherInfo = {
  fullName: string;
  departments: string[];
  photo: string | null;
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-teacher-info-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number, teacherId: string): string {
  return `${CACHE_KEY_PREFIX}${userId}-${teacherId}`;
}

function loadCachedTeacherInfo(userId: number, teacherId: string): CachedTeacherInfo | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId, teacherId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as CachedTeacherInfo;
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed;
  } catch (error) {
    console.warn('[TeacherDetailPage] Failed to load cached teacher info', error);
    return null;
  }
}

function saveCachedTeacherInfo(userId: number, teacherId: string, fullName: string, data: { departments: string[] | null; photo: string | null }): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId, teacherId);
    const cacheValue: CachedTeacherInfo = {
      fullName,
      departments: data.departments || [],
      photo: data.photo || null,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[TeacherDetailPage] Failed to save cached teacher info', error);
  }
}

export function TeacherDetailPage({ userId, teacherId }: TeacherDetailPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedInfo = loadCachedTeacherInfo(userId, teacherId);
  const [fullName, setFullName] = useState<string>(cachedInfo?.fullName || '');
  const [departments, setDepartments] = useState<string[]>(cachedInfo?.departments || []);
  const [photo, setPhoto] = useState<string | null>(cachedInfo?.photo || null);
  const [loading, setLoading] = useState(!cachedInfo); // Показываем загрузку только если нет кэша

  useEffect(() => {
    let isCancelled = false;

    async function loadTeacherInfo() {
      try {
        // Сначала получаем имя преподавателя из списка (нужно для кэша)
        const teachersResponse = await apiClient.getTeachers(userId);
        let teacherName = '';
        
        if (teachersResponse.success && teachersResponse.teachers) {
          const teacher = teachersResponse.teachers.find((t) => t.id === teacherId);
          if (teacher) {
            teacherName = teacher.name;
          }
        }

        const response = await apiClient.getTeacherInfo(userId, teacherId);

        if (isCancelled) {
          return;
        }

        if (response.success) {
          const newDepartments = response.departments || [];
          const newPhoto = response.photo || null;

          // Сохраняем в кэш
          if (teacherName || fullName) {
            saveCachedTeacherInfo(userId, teacherId, teacherName || fullName, {
              departments: newDepartments,
              photo: newPhoto,
            });
          }

          // Обновляем состояние только если компонент ещё смонтирован
          if (!isCancelled) {
            if (teacherName) {
              setFullName(teacherName);
            }
            setDepartments(newDepartments);
            setPhoto(newPhoto);
            if (loading) {
              setLoading(false);
            }
          }
        } else {
          if (!isCancelled && loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[TeacherDetailPage] Failed to load teacher info', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    // Но только если нет кэшированного имени или данных
    if (!cachedInfo || !fullName) {
      loadTeacherInfo();
    } else {
      // Если есть кэш, всё равно обновляем в фоне
      loadTeacherInfo();
    }

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, teacherId]); // Загружаем только при изменении userId или teacherId

  // Показываем "Загрузка данных" если данные загружаются и нет кэша
  if (loading && !cachedInfo) {
    return (
      <div className={styles.page}>
        <p className={styles.loading}>Загрузка данных...</p>
      </div>
    );
  }

  // Если нет данных о преподавателе
  if (!fullName && !cachedInfo) {
    return (
      <div className={styles.page}>
        <p className={styles.loading}>Преподаватель не найден</p>
      </div>
    );
  }

  const avatarSrc = photo || unknownUserImage;

  return (
    <div className={styles.page}>
      <article className={styles.card}>
        <div className={styles.avatarWrapper}>
          <img className={styles.avatar} src={avatarSrc} alt={fullName || 'Преподаватель'} />
        </div>

        <div className={styles.info}>
          <section className={styles.details}>
            {fullName && (
              <>
                <div className={styles.row}>
                  <span className={styles.label}>ФИО</span>
                  <span className={styles.value}>{fullName}</span>
                </div>
                {departments.length > 0 && <div className={styles.separator} />}
              </>
            )}
            {departments.length > 0 && (
              <>
                <div className={styles.row}>
                  <span className={styles.label}>Кафедра</span>
                  <span className={styles.value}>{departments.join(', ')}</span>
                </div>
              </>
            )}
          </section>
        </div>
      </article>
    </div>
  );
}


