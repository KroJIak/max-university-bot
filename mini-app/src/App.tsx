import { useState } from 'react';

import { Layout } from './layout';
import type { FooterNavKey } from './layout/Footer';
import { MainPage } from './pages/MainPage';
import { ProfilePage } from './pages/ProfilePage';
import { ServicesPage } from './pages/ServicesPage';

type PageConfig = {
  title: string;
  showAvatar?: boolean;
  Component: () => JSX.Element;
};

const pages: Record<FooterNavKey, PageConfig> = {
  home: {
    title: 'Главная',
    showAvatar: false,
    Component: MainPage,
  },
  services: {
    title: 'Сервисы',
    showAvatar: false,
    Component: ServicesPage,
  },
  profile: {
    title: 'Профиль',
    showAvatar: false,
    Component: ProfilePage,
  },
};

export function App() {
  const [activePage, setActivePage] = useState<FooterNavKey>('home');

  const pageConfig = pages[activePage];
  const PageComponent = pageConfig.Component;

  return (
    <Layout
      title={pageConfig.title}
      activePage={activePage}
      onNavigate={setActivePage}
      showAvatar={pageConfig.showAvatar}
    >
      <PageComponent />
    </Layout>
  );
}

export default App;

