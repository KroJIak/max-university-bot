import type { IconProps } from '../../components/icons';
import { HomeIcon, ProfileIcon, ServicesIcon } from '../../components/icons';
import styles from './Footer.module.scss';

export type FooterNavKey = 'home' | 'services' | 'profile';

type FooterItem = {
  id: FooterNavKey;
  label: string;
  Icon: (props: IconProps) => JSX.Element;
};

const footerItems: FooterItem[] = [
  { id: 'home', label: 'Главная', Icon: HomeIcon },
  { id: 'services', label: 'Сервисы', Icon: ServicesIcon },
  { id: 'profile', label: 'Профиль', Icon: ProfileIcon },
];

type FooterProps = {
  activePage: FooterNavKey;
  onNavigate: (page: FooterNavKey) => void;
};

export function Footer({ activePage, onNavigate }: FooterProps) {
  return (
    <footer className={styles.footer}>
      <nav className={styles.nav}>
        {footerItems.map((item) => {
          const Icon = item.Icon;
          return (
            <button
              key={item.id}
              className={item.id === activePage ? `${styles.item} ${styles.itemActive}` : styles.item}
              type="button"
              onClick={() => onNavigate(item.id)}
            >
              <Icon className={styles.icon} />
              <span className={styles.label}>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </footer>
  );
}

