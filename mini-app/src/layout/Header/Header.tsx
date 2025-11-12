import { BellIcon, SearchIcon } from '../../components/icons';
import { headerActions, type HeaderActionId } from './header.constants';
import styles from './Header.module.scss';

const actionIconMap: Record<HeaderActionId, JSX.Element> = {
  search: <SearchIcon className={styles.icon} />,
  notifications: <BellIcon className={styles.icon} />,
};

type HeaderProps = {
  title: string;
  showAvatar?: boolean;
};

export function Header({ title, showAvatar = true }: HeaderProps) {
  const brandClassName = showAvatar ? styles.brand : `${styles.brand} ${styles.brandCompact}`;

  return (
    <header className={styles.header}>
      <div className={brandClassName}>
        {showAvatar && <div className={styles.avatar} />}
        <span className={styles.title}>{title}</span>
      </div>
      <div className={styles.actions}>
        {headerActions.map((action) => (
          <button key={action.id} type="button" className={styles.action} aria-label={action.label}>
            {actionIconMap[action.id]}
          </button>
        ))}
      </div>
    </header>
  );
}

