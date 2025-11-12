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
}>;

export function Layout({
  children,
  title,
  activePage,
  onNavigate,
  showAvatar = true,
}: LayoutProps) {
  return (
    <div className={styles.container}>
      <Header title={title} showAvatar={showAvatar} />
      <main className={styles.main}>{children}</main>
      <Footer activePage={activePage} onNavigate={onNavigate} />
    </div>
  );
}

