import { useEffect, useState } from 'react';
import {
  ProfileInfoSection,
  ProfileLogoutButton,
  ProfileSettingsSection,
  ProfileStatsSection,
  ProfileSubgroupSection,
  ProfileSummarySection,
  ProfileUniversitySection,
} from '@components/Profile';
import { apiClient } from '@components/api/client';
import styles from './ProfilePage.module.scss';

declare global {
  interface Window {
    WebApp?: {
      initDataUnsafe?: {
        user?: {
          id?: number;
          first_name?: string;
          last_name?: string;
          username?: string;
          language_code?: string;
          photo_url?: string;
        };
      };
      ready?: () => void;
    };
  }
}

type StatCard = {
  id: string;
  title: string;
  value: string;
  suffix: string;
  icon: string;
};

type SettingsGroup = {
  id: string;
  items: { id: string; icon: string; title: string }[];
};

const statCards: StatCard[] = [
  {
    id: 'gradebook',
    title: 'Зачётка',
    value: '4.90',
    suffix: 'ср. балл',
    icon: '🟦',
  },
  {
    id: 'debts',
    title: 'Долги',
    value: '0',
    suffix: 'долгов',
    icon: '😎',
  },
];

const settingsGroups: SettingsGroup[] = [
  {
    id: 'preferences',
    items: [
      { id: 'theme', icon: '🎨', title: 'Внешний вид' },
      { id: 'notifications', icon: '🔔', title: 'Уведомления и звуки' },
    ],
  },
  {
    id: 'support',
    items: [
      { id: 'about', icon: 'ℹ️', title: 'О приложении' },
      { id: 'support', icon: '🆘', title: 'Служба поддержки' },
      { id: 'improvements', icon: '⭐️', title: 'Предложить улучшение' },
    ],
  },
];

type ProfileData = {
  fullName: string;
  subtitle: string;
  photo?: string;
  infoRows: Array<{ id: string; label: string; value: string }>;
  contactRows: Array<{ id: string; label: string; value: string }>;
};

const PROFILE_CACHE_KEY_PREFIX = 'max-app-profile-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getProfileCacheKey(userId: number): string {
  return `${PROFILE_CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedProfileData(userId: number): ProfileData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getProfileCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as { data: ProfileData; timestamp: number };
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.warn('[ProfilePage] Failed to load cached profile data', error);
    return null;
  }
}

function saveProfileDataToCache(userId: number, data: ProfileData): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getProfileCacheKey(userId);
    const cacheValue = {
      data,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[ProfilePage] Failed to save profile data to cache', error);
  }
}

// Функция для получения username из MAX WebApp
// Согласно документации MAX Bridge: user.username может быть string или null
function getMaxUsername(): string | null {
  if (typeof window !== 'undefined') {
    // Проверяем, доступен ли объект WebApp (признак запуска через MAX)
    if (window.WebApp) {
      const userData = window.WebApp.initDataUnsafe?.user;
      if (userData) {
        const username = userData.username;
        // Username может быть null (если пользователь не установил username в MAX)
        // или строкой (если username установлен)
        if (username && typeof username === 'string' && username.trim().length > 0) {
          console.log('[ProfilePage] Got username from MAX WebApp:', username);
          return username;
        }
        // Username отсутствует, null или пустая строка
        console.log('[ProfilePage] WebApp available but username is null/empty:', username);
        return null;
      }
      console.log('[ProfilePage] WebApp available but user data not found');
      return null;
    }
    // Если открыто напрямую в браузере (для разработки), используем заглушку
    console.log('[ProfilePage] WebApp not available, using dev username');
    return 'dev_username'; // Заглушка для разработки
  }
  return null;
}

export function transformApiResponseToProfileData(
  userId: number,
  data: {
    fam?: string;
    name?: string;
    patronymic?: string;
    course?: string;
    faculty?: string;
    spec?: string;
    profile?: string;
    group?: string;
    zachetka?: string;
    phone?: string;
    birthday?: string;
    photo?: string;
  } | null,
): ProfileData {
  const maxUsername = getMaxUsername();

  if (!data) {
      return {
        fullName: 'Студент',
        subtitle: 'Студент',
        infoRows: [],
        contactRows: [
          { id: 'max-id', label: 'MAX ID', value: userId.toString() },
          ...(maxUsername ? [{ id: 'max-username', label: 'MAX username', value: `@${maxUsername}` }] : []),
        ],
      };
  }

  const fullName = [data.fam, data.name, data.patronymic].filter(Boolean).join(' ') || 'Студент';
  const subtitle = data.course ? `Студент, ${data.course} курс` : 'Студент';

  const infoRows = [
    { id: 'faculty', label: 'Факультет', value: data.faculty || '-' },
    { id: 'speciality', label: 'Специальность', value: data.spec || '-' },
    { id: 'major', label: 'Профиль', value: data.profile || '-' },
    { id: 'group', label: 'Группа', value: data.group || '-' },
    { id: 'gradebook-number', label: 'Номер зачётки', value: data.zachetka || '-' },
  ].filter((row) => row.value !== '-');

  const contactRows = [
    { id: 'max-id', label: 'MAX ID', value: userId.toString() },
    ...(maxUsername ? [{ id: 'max-username', label: 'MAX username', value: `@${maxUsername}` }] : []),
    { id: 'phone', label: 'Телефон', value: data.phone || '-' },
    { id: 'birthday', label: 'Дата рождения', value: data.birthday || '-' },
  ].filter((row) => row.value !== '-');

  return {
    fullName,
    subtitle,
    photo: data.photo,
    infoRows,
    contactRows,
  };
}

type ProfilePageProps = {
  onOpenNotifications?: () => void;
  onOpenTheme?: () => void;
  onLogout?: () => void;
  userId: number;
  universityName?: string;
  onOpenDebts?: () => void;
  onOpenGradebook?: () => void;
};

export function ProfilePage({ onLogout, userId, universityName = 'Макс Университет', onOpenDebts, onOpenGradebook, onOpenNotifications, onOpenTheme }: ProfilePageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedData = loadCachedProfileData(userId);
  const [personalData, setPersonalData] = useState<ProfileData | null>(cachedData);
  const [loading, setLoading] = useState(!cachedData); // Показываем загрузку только если нет кэша

  // Логируем доступность WebApp для отладки
  useEffect(() => {
    if (typeof window !== 'undefined') {
      console.log('[ProfilePage] WebApp available:', !!window.WebApp);
      if (window.WebApp) {
        console.log('[ProfilePage] WebApp.initDataUnsafe:', window.WebApp.initDataUnsafe);
        console.log('[ProfilePage] WebApp.initDataUnsafe?.user:', window.WebApp.initDataUnsafe?.user);
        if (window.WebApp.ready) {
          try {
            window.WebApp.ready();
            console.log('[ProfilePage] Called WebApp.ready()');
          } catch (e) {
            console.warn('[ProfilePage] Failed to call WebApp.ready()', e);
          }
        }
      }
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;

    // Проверяем кэш и его свежесть
    const cachedData = loadCachedProfileData(userId);
    
    // Если кэш есть и свежий (loadCachedProfileData вернул данные, значит кэш валидный),
    // показываем его сразу и обновляем в фоне только если кэш старше 4 минут
    if (cachedData) {
      // Получаем timestamp кэша для проверки возраста
      let cacheTimestamp = 0;
      try {
        const cacheKey = getProfileCacheKey(userId);
        const cached = window.localStorage.getItem(cacheKey);
        if (cached) {
          const parsed = JSON.parse(cached) as { data: ProfileData; timestamp: number };
          cacheTimestamp = parsed.timestamp || 0;
        }
      } catch (error) {
        console.warn('[ProfilePage] Failed to get cache timestamp', error);
      }
      
      if (!isCancelled) {
        setPersonalData(cachedData);
        setLoading(false);
      }
      
      // Обновляем данные в фоне только если кэш старше 4 минут (чтобы не дублировать запросы с DataPreloader)
      const cacheAge = Date.now() - cacheTimestamp;
      const shouldRefresh = cacheAge > 4 * 60 * 1000; // 4 минуты
      
      if (shouldRefresh) {
        async function refreshInBackground() {
          try {
            const response = await apiClient.getPersonalData(userId);

            if (isCancelled) {
              return;
            }

            const newData = transformApiResponseToProfileData(
              userId,
              response.success ? response.data : null,
            );

            // Сохраняем в кэш
            saveProfileDataToCache(userId, newData);

            // Обновляем состояние только если компонент ещё смонтирован
            if (!isCancelled) {
              setPersonalData(newData);
            }
          } catch (error) {
            console.error('[ProfilePage] Failed to refresh personal data in background', error);
          }
        }
        
        // Обновляем в фоне с задержкой
        const timeoutId = setTimeout(() => {
          refreshInBackground();
        }, 1000);
        
        return () => {
          isCancelled = true;
          clearTimeout(timeoutId);
        };
      }
      
      return; // Кэш свежий, основная загрузка не нужна
    }

    // Кэша нет или он устарел, загружаем данные
    async function loadPersonalData() {
      try {
        const response = await apiClient.getPersonalData(userId);

        if (isCancelled) {
          return;
        }

        const newData = transformApiResponseToProfileData(
          userId,
          response.success ? response.data : null,
        );

        // Сохраняем в кэш
        saveProfileDataToCache(userId, newData);

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setPersonalData(newData);
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[ProfilePage] Failed to load personal data', error);
        if (!isCancelled) {
          // Если была ошибка, проверяем текущее состояние
          setPersonalData((currentData) => {
            // Если нет текущих данных, показываем дефолтные
            if (!currentData) {
              return transformApiResponseToProfileData(userId, null);
            }
            // Иначе оставляем текущие данные (из кэша)
            return currentData;
          });
          setLoading(false);
        }
      }
    }

    // Загружаем данные только если кэша нет или он устарел
    loadPersonalData();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (!scrollToElement) return;

    // Даём время на рендеринг страницы
    const timeoutId = setTimeout(() => {
      let element: Element | null = null;
      
      // Проверяем, это раздел настроек или поле данных
      if (scrollToElement.startsWith('profile-')) {
        const fieldId = scrollToElement.replace('profile-', '');
        element = document.querySelector(`[data-profile-field="${fieldId}"]`) 
          || document.querySelector(`[data-profile-section="${fieldId}"]`);
      } else {
        // Ищем раздел настроек или подгруппу
        if (scrollToElement === 'subgroup') {
          element = document.querySelector('[data-profile-section="subgroup"]');
        } else {
          element = document.querySelector(`[data-profile-section="${scrollToElement}"]`);
        }
      }
      
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

  if (loading) {
    return (
      <div className={styles.page}>
        <ProfileUniversitySection name={universityName} />
        <ProfileSummarySection name="Загрузка..." subtitle="Загрузка данных" />
      </div>
    );
  }

  if (!personalData) {
    return (
      <div className={styles.page}>
        <ProfileUniversitySection name={universityName} />
        <ProfileSummarySection name="Ошибка" subtitle="Не удалось загрузить данные" />
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <ProfileUniversitySection name={universityName} />
      <ProfileSummarySection
        name={personalData.fullName}
        subtitle={personalData.subtitle}
        photo={personalData.photo}
      />
      <ProfileStatsSection
        cards={statCards}
        onCardClick={(cardId) => {
          if (cardId === 'debts' && onOpenDebts) {
            onOpenDebts();
          }
          if (cardId === 'gradebook' && onOpenGradebook) {
            onOpenGradebook();
          }
        }}
      />
      {personalData.infoRows.length > 0 && <ProfileInfoSection rows={personalData.infoRows} />}
      <div data-profile-section="subgroup">
        <ProfileSubgroupSection />
      </div>
      {personalData.contactRows.length > 0 && <ProfileInfoSection rows={personalData.contactRows} />}
      <div data-profile-section="settings">
        <ProfileSettingsSection groups={settingsGroups} onOpenNotifications={onOpenNotifications} onOpenTheme={onOpenTheme} />
      </div>
      <ProfileLogoutButton onClick={onLogout} />
    </div>
  );
}

