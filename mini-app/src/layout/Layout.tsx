import type { PropsWithChildren } from 'react';

import type { FooterNavKey } from './Footer';
import { Footer } from './Footer';
import { Header } from './Header';
import styles from './Layout.module.scss';

type LayoutProps = PropsWithChildren<{
  title: string;
  activePage: FooterNavKey;
  onNavigate: (page: FooterNavKey) => void;
  showAvatar?: boolean;
  onBack?: (() => void) | null;
  onNotificationsClick?: () => void;
  hasUnreadNotifications?: boolean;
  onSearchClick?: () => void;
}>;

export function Layout({
  children,
  title,
  activePage,
  onNavigate,
  showAvatar = true,
  onBack = null,
  onNotificationsClick,
  hasUnreadNotifications = false,
  onSearchClick,
}: LayoutProps) {
  return (
    <div className={styles.container}>
      <Header
        title={title}
        showAvatar={showAvatar}
        onBack={onBack ?? undefined}
        onNotificationsClick={onNotificationsClick}
        hasUnreadNotifications={hasUnreadNotifications}
        onSearchClick={onSearchClick}
      />
      <main className={styles.main}>{children}</main>
      <Footer activePage={activePage} onNavigate={onNavigate} />
    </div>
  );
}

