import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react';

import { Layout } from './layout';
import type { FooterNavKey } from './layout/Footer';
import { LoginPage } from './pages/LoginPage';
import { teachers } from '@shared/data/teachers';
import { apiClient } from '@components/api/client';

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

type StoredSession = {
  userId: number;
  universityId: number;
  email: string;
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
  | 'newsDetail';

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

  const activePage = history[history.length - 1];

  const pushPage = useCallback((page: PageKey) => {
    setHistory((trail) => {
      const current = trail[trail.length - 1];
      if (current === page) {
        return trail;
      }

      return [...trail, page];
    });
  }, []);

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
      return;
    }

    let isCancelled = false;

    apiClient
      .getStudentStatus(session.userId)
      .then((status) => {
        if (isCancelled) {
          return;
        }

        if (!status.is_linked) {
          setSession(null);
          setHistory(['login']);
        }
      })
      .catch((error) => {
        console.error('[session] failed to verify student status', error);
      });

    return () => {
      isCancelled = true;
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
            onOpenSchedule={() => pushPage('scheduleDetail')}
            onOpenPrimaryServices={() => pushPage('primaryServices')}
            onOpenPlatforms={() => pushPage('platforms')}
            onOpenTeachers={() => pushPage('teachers')}
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
            onOpenSchedule={() => pushPage('scheduleDetail')}
            onOpenTeachers={() => pushPage('teachers')}
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
      const teacher = teachers.find((item) => item.id === selectedTeacherId);
      if (!teacher) {
        return {
          title: 'Преподаватель',
          showAvatar: false,
          footerActive: 'services',
          render: () => (
            <TeachersPage
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
        render: () => <TeacherDetailPage teacher={teacher} />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'platforms') {
      return {
        title: 'Веб-платформы',
        showAvatar: false,
        footerActive: 'services',
        render: () => <PlatformsPage />,
        onBack: history.length > 1 ? handleBack : undefined,
      };
    }

    if (activePage === 'profile') {
      return {
              title: 'Профиль',
              showAvatar: false,
              footerActive: 'profile',
        render: () => <ProfilePage onLogout={handleLogout} />,
      };
            }

    if (activePage === 'scheduleDetail') {
      return {
                title: 'Расписание',
                showAvatar: false,
        footerActive: history.includes('services') ? 'services' : 'home',
                render: () => <SchedulePage />,
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
  }, [activePage, handleBack, handleLogout, history, pushPage]);

  const handleLoginComplete = useCallback((payload: { universityId: number; email: string; userId: number }) => {
    const nextSession: StoredSession = {
      userId: payload.userId,
      universityId: payload.universityId,
      email: payload.email,
    };

    setSession(nextSession);
    setSelectedTeacherId(null);
    setHistory(['home']);
  }, []);

  if (activePage === 'login') {
    return <LoginPage onLogin={handleLoginComplete} />;
  }

  return (
    <Layout
      title={pageConfig.title}
      activePage={pageConfig.footerActive}
      onNavigate={replaceRoot}
      showAvatar={pageConfig.showAvatar}
      onBack={pageConfig.onBack}
    >
      <Suspense fallback={null}>{pageConfig.render()}</Suspense>
    </Layout>
  );
}

export default App;

