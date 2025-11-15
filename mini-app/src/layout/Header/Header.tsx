import { BellIcon, SearchIcon } from '@components/icons';
import { HeaderBackButton } from '@components/Header';
import { headerActions, type HeaderActionId } from './header.constants';
import styles from './Header.module.scss';

type HeaderProps = {
  title: string;
  showAvatar?: boolean;
  onBack?: () => void;
  onNotificationsClick?: () => void;
  hasUnreadNotifications?: boolean;
};

export function Header({
  title,
  showAvatar = true,
  onBack,
  onNotificationsClick,
  hasUnreadNotifications = false,
  onSearchClick,
}: HeaderProps) {
  const brandClassName = showAvatar ? styles.brand : `${styles.brand} ${styles.brandCompact}`;

  const handleActionClick = (actionId: HeaderActionId) => {
    if (actionId === 'notifications' && onNotificationsClick) {
      onNotificationsClick();
    } else if (actionId === 'search' && onSearchClick) {
      onSearchClick();
    }
  };

  return (
    <header className={styles.header}>
      <div className={brandClassName}>
        {showAvatar && <div className={styles.avatar} />}
        <span className={styles.title}>{title}</span>
      </div>
      <div className={styles.actions}>
        {onBack && <HeaderBackButton onClick={onBack} />}
        {headerActions.map((action) => (
          <button
            key={action.id}
            type="button"
            className={styles.action}
            aria-label={action.label}
            onClick={() => handleActionClick(action.id)}
          >
            {action.id === 'notifications' ? (
              <div className={styles.notificationWrapper}>
                <BellIcon className={styles.icon} />
                {hasUnreadNotifications && <span className={styles.notificationBadge} />}
              </div>
            ) : action.id === 'search' ? (
              <SearchIcon className={styles.icon} />
            ) : null}
          </button>
        ))}
      </div>
    </header>
  );
}

