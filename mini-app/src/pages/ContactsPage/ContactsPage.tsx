import { useEffect, useMemo, useState } from 'react';
import { apiClient } from '@components/api/client';
import styles from './ContactsPage.module.scss';

type TabType = 'deans' | 'departments';

type DeanContact = {
  email: string;
  faculty: string;
  phone: string;
};

type DepartmentContact = {
  department: string;
  email: string;
  faculty: string;
  phones: string;
};

type ContactsPageProps = {
  userId: number;
};

type CachedContactsData = {
  deans: DeanContact[];
  departments: DepartmentContact[];
  timestamp: number;
};

const CACHE_KEY_PREFIX = 'max-app-contacts-';
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут

function getCacheKey(userId: number): string {
  return `${CACHE_KEY_PREFIX}${userId}`;
}

function loadCachedContacts(userId: number): CachedContactsData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cached = window.localStorage.getItem(cacheKey);
    if (!cached) {
      return null;
    }

    const parsed = JSON.parse(cached) as CachedContactsData;
    const now = Date.now();

    // Проверяем, не устарел ли кэш
    if (now - parsed.timestamp > CACHE_TIMEOUT_MS) {
      window.localStorage.removeItem(cacheKey);
      return null;
    }

    return parsed;
  } catch (error) {
    console.warn('[ContactsPage] Failed to load cached contacts', error);
    return null;
  }
}

function saveCachedContacts(userId: number, deans: DeanContact[], departments: DepartmentContact[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cacheKey = getCacheKey(userId);
    const cacheValue: CachedContactsData = {
      deans,
      departments,
      timestamp: Date.now(),
    };
    window.localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
  } catch (error) {
    console.warn('[ContactsPage] Failed to save cached contacts', error);
  }
}

export function ContactsPage({ userId }: ContactsPageProps) {
  // Загружаем кэшированные данные сразу при монтировании
  const cachedData = loadCachedContacts(userId);
  const [deans, setDeans] = useState<DeanContact[]>(cachedData?.deans || []);
  const [departments, setDepartments] = useState<DepartmentContact[]>(cachedData?.departments || []);
  const [loading, setLoading] = useState(!cachedData); // Показываем загрузку только если нет кэша
  const [activeTab, setActiveTab] = useState<TabType>('deans');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let isCancelled = false;

    async function loadContacts() {
      try {
        const response = await apiClient.getContacts(userId);

        if (isCancelled) {
          return;
        }

        const newDeans = response.success && response.deans ? response.deans : [];
        const newDepartments = response.success && response.departments ? response.departments : [];

        // Сохраняем в кэш
        if (newDeans.length > 0 || newDepartments.length > 0) {
          saveCachedContacts(userId, newDeans, newDepartments);
        }

        // Обновляем состояние только если компонент ещё смонтирован
        if (!isCancelled) {
          setDeans(newDeans);
          setDepartments(newDepartments);
          
          // Автоматически выбираем активную вкладку при загрузке данных
          if (newDeans.length > 0 && newDepartments.length === 0) {
            setActiveTab('deans');
          } else if (newDeans.length === 0 && newDepartments.length > 0) {
            setActiveTab('departments');
          }
          
          if (loading) {
            setLoading(false);
          }
        }
      } catch (error) {
        console.error('[ContactsPage] Failed to load contacts', error);
        // Если была ошибка, проверяем текущее состояние
        if (!isCancelled) {
          if (loading) {
            setLoading(false);
          }
        }
      }
    }

    // Загружаем данные в фоне (кэш уже показан, если был)
    loadContacts();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]); // Загружаем только при изменении userId

  // Автоматически выбираем активную вкладку на основе загруженных данных
  useEffect(() => {
    if (deans.length > 0 && departments.length === 0) {
      setActiveTab('deans');
    } else if (deans.length === 0 && departments.length > 0) {
      setActiveTab('departments');
    }
  }, [deans.length, departments.length]);

  // Фильтрация деканатов по запросу поиска
  const filteredDeans = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return deans;
    }

    return deans.filter((dean) => {
      const faculty = dean.faculty?.toLowerCase() || '';
      const email = dean.email?.toLowerCase() || '';
      const phone = dean.phone?.toLowerCase() || '';
      
      return faculty.includes(query) || email.includes(query) || phone.includes(query);
    });
  }, [deans, searchQuery]);

  // Фильтрация кафедр по запросу поиска
  const filteredDepartments = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return departments;
    }

    return departments.filter((dept) => {
      const department = dept.department?.toLowerCase() || '';
      const faculty = dept.faculty?.toLowerCase() || '';
      const email = dept.email?.toLowerCase() || '';
      const phones = dept.phones?.toLowerCase() || '';
      
      return department.includes(query) || faculty.includes(query) || email.includes(query) || phones.includes(query);
    });
  }, [departments, searchQuery]);

  // Показываем "Загрузка данных" если данные загружаются
  if (loading && deans.length === 0 && departments.length === 0) {
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
    if (scrollToElement === 'contacts') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="contacts"]') || document.body.firstElementChild;
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
    <div className={styles.page} data-section="contacts">
      {(deans.length > 0 || departments.length > 0) && (
        <>
          <div className={styles.search}>
            <input
              type="search"
              className={styles.searchInput}
              placeholder="Поиск контактов..."
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
          </div>

          <div className={styles.tabSelector}>
            <button
              type="button"
              className={`${styles.tabButton} ${activeTab === 'deans' ? styles.tabButtonActive : ''}`}
              onClick={() => setActiveTab('deans')}
              disabled={deans.length === 0}
            >
              Деканаты
            </button>
            <button
              type="button"
              className={`${styles.tabButton} ${activeTab === 'departments' ? styles.tabButtonActive : ''}`}
              onClick={() => setActiveTab('departments')}
              disabled={departments.length === 0}
            >
              Кафедры
            </button>
          </div>
        </>
      )}

      {activeTab === 'deans' && deans.length > 0 && (
        <section className={styles.section}>
          <div className={styles.list}>
            {filteredDeans.length > 0 ? (
              filteredDeans.map((dean, index) => (
              <div key={index} className={styles.card}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.cardTitle}>{dean.faculty}</h3>
                </div>
                <div className={styles.cardContent}>
                  {dean.phone && (
                    <div className={styles.contactRow}>
                      <span className={styles.label}>Телефон:</span>
                      <a className={styles.link} href={`tel:${dean.phone.replace(/\s/g, '')}`}>
                        {dean.phone}
                      </a>
                    </div>
                  )}
                  {dean.email && (
                    <div className={styles.contactRow}>
                      <span className={styles.label}>Email:</span>
                      <a className={styles.link} href={`mailto:${dean.email}`}>
                        {dean.email}
                      </a>
                    </div>
                  )}
                </div>
              </div>
              ))
            ) : (
              <p className={styles.empty}>Деканаты не найдены</p>
            )}
          </div>
        </section>
      )}

      {activeTab === 'departments' && departments.length > 0 && (
        <section className={styles.section}>
          <div className={styles.list}>
            {filteredDepartments.length > 0 ? (
              filteredDepartments.map((dept, index) => (
              <div key={index} className={styles.card}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.cardTitle}>{dept.department}</h3>
                  {dept.faculty && <p className={styles.faculty}>{dept.faculty}</p>}
                </div>
                <div className={styles.cardContent}>
                  {dept.phones && (
                    <div className={styles.contactRow}>
                      <span className={styles.label}>Телефон:</span>
                      <a className={styles.link} href={`tel:${dept.phones.replace(/\s/g, '')}`}>
                        {dept.phones}
                      </a>
                    </div>
                  )}
                  {dept.email && (
                    <div className={styles.contactRow}>
                      <span className={styles.label}>Email:</span>
                      <a className={styles.link} href={`mailto:${dept.email}`}>
                        {dept.email}
                      </a>
                    </div>
                  )}
                </div>
              </div>
              ))
            ) : (
              <p className={styles.empty}>Кафедры не найдены</p>
            )}
          </div>
        </section>
      )}

      {!loading && deans.length === 0 && departments.length === 0 && (
        <p className={styles.loading}>Контакты не найдены</p>
      )}
    </div>
  );
}

