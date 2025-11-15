import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react';

import { Layout } from './layout';
import type { FooterNavKey } from './layout/Footer';
import { LoginPage } from './pages/LoginPage';
import { apiClient } from '@components/api/client';
import { DataPreloader } from '@shared/services/dataPreloader';
import { NotificationsModal } from '@components/Notifications';
import { useNotifications } from '@components/Notifications/useNotifications';

const MainPage = lazy(() => import('./pages/MainPage').then((module) => ({ default: module.MainPage })));
const NewsPage = lazy(() => import('./pages/NewsPage').then((module) => ({ default: module.NewsPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then((module) => ({ default: module.ProfilePage })));
const SchedulePage = lazy(() => import('./pages/SchedulePage').then((module) => ({ default: module.SchedulePage })));
const ServicesPage = lazy(() => import('./pages/ServicesPage').then((module) => ({ default: module.ServicesPage })));
const PrimaryServicesPage = lazy(() =>
  import('./pages/PrimaryServicesPage').then((module) => ({ default: module.PrimaryServicesPage })),
);
const PlatformsPage = lazy(() => import('./pages/PlatformsPage').then((module) => ({ default: module.PlatformsPage })));
const TeachersPage = lazy(() => import('./pages/TeachersPage').then((module) => ({ default: module.TeachersPage })));
const TeacherDetailPage = lazy(() =>
  import('./pages/TeacherDetailPage').then((module) => ({ default: module.TeacherDetailPage })),
);
const DebtsPage = lazy(() => import('./pages/DebtsPage').then((module) => ({ default: module.DebtsPage })));
const GradebookPage = lazy(() => import('./pages/GradebookPage').then((module) => ({ default: module.GradebookPage })));
const ChatsPage = lazy(() => import('./pages/ChatsPage').then((module) => ({ default: module.ChatsPage })));
const ContactsPage = lazy(() => import('./pages/ContactsPage').then((module) => ({ default: module.ContactsPage })));
const MapsPage = lazy(() => import('./pages/MapsPage').then((module) => ({ default: module.MapsPage })));
const ClubsPage = lazy(() => import('./pages/ClubsPage').then((module) => ({ default: module.ClubsPage })));
const NotificationsPage = lazy(() =>
  import('./pages/NotificationsPage').then((module) => ({ default: module.NotificationsPage })),
);
const ThemePage = lazy(() => import('./pages/ThemePage').then((module) => ({ default: module.ThemePage })));
const SearchPage = lazy(() => import('./pages/SearchPage').then((module) => ({ default: module.SearchPage })));

type StoredSession = {
  userId: number;
  universityId: number;
  email: string;
  universityName?: string;
};

const SESSION_STORAGE_KEY = 'max-app-session';

function loadStoredSession(): StoredSession | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as Partial<StoredSession>;
    if (
      parsed &&
      typeof parsed === 'object' &&
      typeof parsed.userId === 'number' &&
      typeof parsed.universityId === 'number' &&
      typeof parsed.email === 'string'
    ) {
      return {
        userId: parsed.userId,
        universityId: parsed.universityId,
        email: parsed.email,
        universityName: typeof parsed.universityName === 'string' ? parsed.universityName : undefined,
      };
    }
  } catch (error) {
    console.warn('[session] failed to load stored session', error);
  }

  return null;
}

function persistSession(session: StoredSession | null) {
  if (typeof window === 'undefined') {
    return;
  }

  if (!session) {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

type PageKey =
  | 'login'
  | 'home'
  | 'services'
  | 'platforms'
  | 'primaryServices'
  | 'teachers'
  | 'teacherDetail'
  | 'profile'
  | 'scheduleDetail'
  | 'newsDetail'
  | 'debts'
  | 'gradebook'
  | 'chats'
  | 'contacts'
  | 'maps'
  | 'clubs'
  | 'notifications'
  | 'theme'
  | 'search';

type PageConfig = {
  title: string;
  showAvatar?: boolean;
  footerActive: FooterNavKey;
  render: () => JSX.Element;
  onBack?: () => void;
};

export function App() {
  const [session, setSession] = useState<StoredSession | null>(() => loadStoredSession());
  const [history, setHistory] = useState<PageKey[]>(() => (loadStoredSession() ? ['home'] : ['login']));
  const [selectedTeacherId, setSelectedTeacherId] = useState<string | null>(null);
  const [isNotificationsModalOpen, setIsNotificationsModalOpen] = useState(false);

  const { notifications, hasUnreadNotifications, markAsRead } = useNotifications();

  const activePage = history[history.length - 1];

  // Отладка
  useEffect(() => {
    console.log('[App] Render - activePage:', activePage, 'history:', history, 'session:', !!session);
  });

  const pushPage = useCallback((page: PageKey) => {
    setHistory((trail) => {
      const current = trail[trail.length - 1];
      if (current === page) {
        return trail;
      }

      return [...trail, page];
    });
  }, []);

  const handleSearchClick = useCallback(() => {
    pushPage('search');
  }, [pushPage]);

  const handleNavigateFromSearch = useCallback(
    (pageId: string) => {
      // Сохраняем информацию о скролле для некоторых страниц
      if (typeof window !== 'undefined') {
        const scrollTargets: Record<string, string> = {
          'primaryServices': 'primary-services',
          'platforms': 'platforms',
          'teachers': 'teachers',
          'maps': 'maps',
          'contacts': 'contacts',
          'chats': 'chats',
        };
        
        if (scrollTargets[pageId]) {
          sessionStorage.setItem('scrollToElement', scrollTargets[pageId]);
        }
      }
      
      // Преобразуем ID страницы в PageKey и навигируем
      const pageMap: Record<string, PageKey> = {
        home: 'home',
        news: 'newsDetail',
        schedule: 'scheduleDetail',
        services: 'services',
        profile: 'profile',
        primaryServices: 'primaryServices',
        platforms: 'platforms',
        teachers: 'teachers',
        maps: 'maps',
        contacts: 'contacts',
        chats: 'chats',
        requests: 'services', // Запросы и справки пока ведут на сервисы
        practice: 'services', // Практика пока ведет на сервисы
        gradebook: 'gradebook',
        debts: 'debts',
        theme: 'theme',
        notifications: 'notifications',
        about: 'profile', // О приложении открывается из профиля
        support: 'profile', // Служба поддержки открывается из профиля
        improvements: 'profile', // Предложить улучшение открывается из профиля
        usefulLinks: 'services', // Полезные ссылки пока ведут на сервисы
      };
      const targetPage = pageMap[pageId] || 'home';
      pushPage(targetPage);
    },
    [pushPage],
  );

  const handleNavigateToProfileSection = useCallback(
    (section?: string) => {
      // Сохраняем информацию о скролле в sessionStorage
      if (section && typeof window !== 'undefined') {
        sessionStorage.setItem('scrollToElement', section);
      }
      
      // Сначала переходим на профиль
      pushPage('profile');
      
      // Затем, если указан раздел, переходим на него или скроллим к элементу
      if (section === 'gradebook') {
        setTimeout(() => pushPage('gradebook'), 100);
      } else if (section === 'debts') {
        setTimeout(() => pushPage('debts'), 100);
      } else if (section === 'theme') {
        setTimeout(() => pushPage('theme'), 100);
      } else if (section === 'notifications') {
        setTimeout(() => pushPage('notifications'), 100);
      } else if (section === 'about' || section === 'support' || section === 'improvements') {
        // Для этих разделов остаемся на странице профиля и скроллим к нужному элементу
        setTimeout(() => {
          if (typeof window !== 'undefined') {
            const element = document.querySelector(`[data-profile-section="${section}"]`);
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
          }
        }, 300);
      } else if (section && section.startsWith('profile-')) {
        // Для полей профиля (факультет, телефон и т.д.) скроллим к нужному полю
        setTimeout(() => {
          if (typeof window !== 'undefined') {
            const fieldId = section.replace('profile-', '');
            const element = document.querySelector(`[data-profile-field="${fieldId}"]`);
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
          }
        }, 300);
      }
    },
    [pushPage],
  );

  const replaceRoot = useCallback((page: FooterNavKey) => {
    setHistory([page]);
  }, []);

  const handleBack = useCallback(() => {
    setHistory((trail) => {
      if (trail.length <= 1) {
        return trail;
      }

      return trail.slice(0, -1);
    });
  }, []);

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    });
  }, [activePage]);

  const handleLogout = useCallback(async () => {
    const currentSession = session;
    if (!currentSession) {
      setHistory(['login']);
      return;
    }

    try {
      // Останавливаем фоновое обновление перед выходом
      DataPreloader.stopBackgroundUpdates(currentSession.userId);
      await apiClient.unlinkStudent(currentSession.userId);
    } catch (error) {
      console.error('[logout] failed to unlink student', error);
    } finally {
      setSession(null);
      setSelectedTeacherId(null);
      setHistory(['login']);
    }
  }, [session]);

  useEffect(() => {
    persistSession(session);
  }, [session]);

  useEffect(() => {
    if (!session) {
      // Останавливаем фоновое обновление, если сессии нет
      return;
    }

    const currentUserId = session.userId;
    let isCancelled = false;

    // Запускаем автоподгрузку сразу при наличии сессии (даже до проверки статуса)
    // Это обеспечивает работу автоподгрузки при каждой загрузке страницы
    console.log('[App] Session found, starting background updates for user', currentUserId);
    
    // Запускаем автоподгрузку в фоне (с force=true, чтобы загрузить даже если недавно загружали)
    // Это нужно для того, чтобы при первой загрузке страницы данные точно подгрузились
    DataPreloader.preloadAllData(currentUserId, true).catch((error) => {
      console.error('[App] Failed to preload data on page load', error);
    });
    
    // Запускаем периодическое обновление
    DataPreloader.startBackgroundUpdates(currentUserId);

    // Проверяем статус сессии при запуске (в фоне)
    // Периодическая проверка будет происходить через startBackgroundUpdates
    apiClient
      .getStudentStatus(currentUserId)
      .then((status) => {
        if (isCancelled) {
          return;
        }

        if (!status.is_linked) {
          // Сессия невалидна, останавливаем обновления и переходим на логин
          DataPreloader.stopBackgroundUpdates(currentUserId);
          setSession(null);
          setHistory(['login']);
        }
        // Если сессия валидна, ничего не делаем - автоподгрузка уже запущена выше
        // Периодическая проверка статуса будет происходить через startBackgroundUpdates
      })
      .catch((error) => {
        console.error('[App] Failed to verify student status on startup', error);
        // Не останавливаем автоподгрузку при ошибке проверки статуса,
        // так как сессия может быть валидной, просто проверка не удалась
      });

    return () => {
      isCancelled = true;
      // Останавливаем фоновое обновление только если сессия изменилась или компонент размонтирован
      // Проверяем, что userId все еще тот же (чтобы избежать остановки при Strict Mode двойном рендере)
      const currentSession = loadStoredSession();
      if (!currentSession || currentSession.userId !== currentUserId) {
        console.log('[App] Cleanup: stopping background updates for user', currentUserId);
        DataPreloader.stopBackgroundUpdates(currentUserId);
      } else {
        console.log('[App] Cleanup: skipping stop (session still active)');
      }
    };
  }, [session]);

  const pageConfig: PageConfig = useMemo(() => {
    if (activePage === 'home') {
      return {
          title: 'Главная',
          showAvatar: false,
          footerActive: 'home',
          render: () => (
            <MainPage
              userId={session?.userId || 123456789}
              onOpenFullSchedule={() => pushPage('scheduleDetail')}
              onOpenAllNews={() => pushPage('newsDetail')}
            />
          ),
      };
        }

    if (activePage === 'services') {
      return {
            title: 'Сервисы',
            showAvatar: false,
            footerActive: 'services',
        render: () => (
          <ServicesPage
            userId={session?.userId || 123456789}
            onOpenSchedule={() => pushPage('scheduleDetail')}
            onOpenPrimaryServices={() => pushPage('primaryServices')}
            onOpenPlatforms={() => pushPage('platforms')}
            onOpenTeachers={() => pushPage('teachers')}
            onOpenChats={() => pushPage('chats')}
            onOpenContacts={() => pushPage('contacts')}
            onOpenMaps={() => pushPage('maps')}
            onOpenClubs={() => pushPage('clubs')}
          />
        ),
      };
    }

    if (activePage === 'primaryServices') {
      return {
        title: 'Основные сервисы',
        showAvatar: false,
        footerActive: 'services',
        render: () => (
          <PrimaryServicesPage
            userId={session?.userId || 123456789}
            onOpenSchedule={() => pushPage('scheduleDetail')}
            onOpenTeachers={() => pushPage('teachers')}
            onOpenChats={() => pushPage('chats')}
            onOpenContacts={() => pushPage('contacts')}
            onOpenMaps={() => pushPage('maps')}
            onOpenClubs={() => pushPage('clubs')}
          />
        ),
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'teachers') {
      return {
        title: 'Преподаватели',
        showAvatar: false,
        footerActive: 'services',
        render: () => (
          <TeachersPage
            userId={session?.userId || 123456789}
            onSelectTeacher={(id: string) => {
              setSelectedTeacherId(id);
              pushPage('teacherDetail');
            }}
          />
        ),
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'teacherDetail') {
      if (!selectedTeacherId) {
        return {
          title: 'Преподаватель',
          showAvatar: false,
          footerActive: 'services',
          render: () => (
            <TeachersPage
              userId={session?.userId || 123456789}
              onSelectTeacher={(id: string) => {
                setSelectedTeacherId(id);
                pushPage('teacherDetail');
              }}
            />
          ),
          onBack: history.length > 1 ? handleBack : undefined,
        };
      }
      return {
        title: 'Преподаватель',
        showAvatar: false,
        footerActive: 'services',
        render: () => <TeacherDetailPage userId={session?.userId || 123456789} teacherId={selectedTeacherId} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'platforms') {
      return {
        title: 'Веб-платформы',
        showAvatar: false,
        footerActive: 'services',
        render: () => <PlatformsPage userId={session?.userId || 123456789} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'profile') {
      if (!session) {
        return {
          title: 'Профиль',
          showAvatar: false,
          footerActive: 'profile',
          render: () => (
            <ProfilePage
              onLogout={handleLogout}
              userId={123456789}
              universityName="Макс Университет"
              onOpenDebts={() => pushPage('debts')}
              onOpenGradebook={() => pushPage('gradebook')}
              onOpenNotifications={() => pushPage('notifications')}
              onOpenTheme={() => pushPage('theme')}
            />
          ),
        };
      }
      return {
        title: 'Профиль',
        showAvatar: false,
        footerActive: 'profile',
        render: () => (
          <ProfilePage
            onLogout={handleLogout}
            userId={session.userId}
            universityName={session.universityName || 'Университет'}
            onOpenDebts={() => pushPage('debts')}
            onOpenGradebook={() => pushPage('gradebook')}
            onOpenNotifications={() => pushPage('notifications')}
            onOpenTheme={() => pushPage('theme')}
          />
        ),
      };
    }

    if (activePage === 'debts') {
      return {
        title: 'Долги',
        showAvatar: false,
        footerActive: 'profile',
        render: () => <DebtsPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'gradebook') {
      return {
        title: 'Зачётная книжка',
        showAvatar: false,
        footerActive: 'profile',
        render: () => <GradebookPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'chats') {
      return {
        title: 'Чаты',
        showAvatar: false,
        footerActive: 'services',
        render: () => <ChatsPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'contacts') {
      return {
        title: 'Контакты',
        showAvatar: false,
        footerActive: 'services',
        render: () => <ContactsPage userId={session?.userId || 123456789} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'maps') {
      return {
        title: 'Карта',
        showAvatar: false,
        footerActive: 'services',
        render: () => <MapsPage userId={session?.userId || 123456789} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'clubs') {
      return {
        title: 'Клубы',
        showAvatar: false,
        footerActive: 'services',
        render: () => <ClubsPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'notifications') {
      return {
        title: 'Уведомления',
        showAvatar: false,
        footerActive: 'profile',
        render: () => <NotificationsPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'theme') {
      return {
        title: 'Внешний вид',
        showAvatar: false,
        footerActive: 'profile',
        render: () => <ThemePage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'search') {
      return {
        title: 'Поиск',
        showAvatar: false,
        footerActive: history.length > 1 && history[history.length - 2] === 'services' ? 'services' : history.length > 1 && history[history.length - 2] === 'profile' ? 'profile' : 'home',
        render: () => (
          <SearchPage
            onNavigate={handleNavigateFromSearch}
            onNavigateToProfile={handleNavigateToProfileSection}
          />
        ),
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'scheduleDetail') {
      return {
        title: 'Расписание',
        showAvatar: false,
        footerActive: history.includes('services') ? 'services' : 'home',
        render: () => <SchedulePage userId={session?.userId || 123456789} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    return {
                title: 'Новости',
                showAvatar: false,
                footerActive: 'home',
                render: () => <NewsPage />,
      onBack: history.length > 1 ? handleBack : undefined,
    };
  }, [activePage, handleBack, handleLogout, history, pushPage, session, selectedTeacherId, handleNavigateFromSearch, handleNavigateToProfileSection]);

  const handleLoginComplete = useCallback(
    (payload: { universityId: number; email: string; userId: number; universityName?: string }) => {
      const nextSession: StoredSession = {
        userId: payload.userId,
        universityId: payload.universityId,
        email: payload.email,
        universityName: payload.universityName,
      };

      setSession(nextSession);
      setSelectedTeacherId(null);
      setHistory(['home']);

      // Предзагружаем все данные в фоне после логина
      DataPreloader.preloadAllData(payload.userId).catch((error) => {
        console.error('[App] Failed to preload data after login', error);
      });
    },
    [],
  );

  console.log('[App] Before render - activePage:', activePage, 'pageConfig:', !!pageConfig);

  if (activePage === 'login') {
    console.log('[App] Rendering LoginPage');
    return <LoginPage onLogin={handleLoginComplete} />;
  }

  // Защита от случая, когда pageConfig не определен
  if (!pageConfig) {
    console.error('[App] pageConfig is undefined, activePage:', activePage);
    return (
      <div style={{ padding: '20px', color: 'white' }}>
        Ошибка: не удалось загрузить страницу. activePage: {activePage}
      </div>
    );
  }

  console.log('[App] Rendering Layout with pageConfig:', pageConfig.title);

  try {
    return (
      <>
        <Layout
          title={pageConfig.title}
          activePage={pageConfig.footerActive}
          onNavigate={replaceRoot}
          showAvatar={pageConfig.showAvatar}
          onBack={pageConfig.onBack}
          onNotificationsClick={() => setIsNotificationsModalOpen(true)}
          hasUnreadNotifications={hasUnreadNotifications}
          onSearchClick={handleSearchClick}
        >
          <Suspense fallback={<div style={{ padding: '20px', color: 'white' }}>Загрузка...</div>}>
            {pageConfig.render()}
          </Suspense>
        </Layout>

        <NotificationsModal
          isOpen={isNotificationsModalOpen}
          notifications={notifications}
          onClose={() => setIsNotificationsModalOpen(false)}
          onMarkAsRead={markAsRead}
        />
      </>
    );
  } catch (error) {
    console.error('[App] Error rendering:', error);
    return (
      <div style={{ padding: '20px', color: 'white' }}>
        Ошибка при рендеринге: {error instanceof Error ? error.message : String(error)}
      </div>
    );
  }
}

export default App;

