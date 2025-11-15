import { useEffect, type FC } from 'react';
import styles from './NotificationsModal.module.scss';

type Notification = {
  id: string;
  title: string;
  message: string;
  time: string;
  date: string;
};

type NotificationsModalProps = {
  isOpen: boolean;
  notifications: Notification[];
  onClose: () => void;
  onMarkAsRead: () => void;
};

export const NotificationsModal: FC<NotificationsModalProps> = ({
  isOpen,
  notifications,
  onClose,
  onMarkAsRead,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      // Помечаем уведомления как просмотренные при открытии
      onMarkAsRead();
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, onMarkAsRead]);

  if (!isOpen) {
    return null;
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.backdrop} onClick={handleBackdropClick}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2 className={styles.title}>Уведомления</h2>
          <button
            type="button"
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Закрыть"
          >
            ×
          </button>
        </div>

        <div className={styles.content}>
          {notifications.length > 0 ? (
            <div className={styles.notificationsList}>
              {notifications.map((notification) => (
                <div key={notification.id} className={styles.notificationItem}>
                  <div className={styles.notificationContent}>
                    <h3 className={styles.notificationTitle}>{notification.title}</h3>
                    <p className={styles.notificationMessage}>{notification.message}</p>
                    <div className={styles.notificationTime}>
                      {notification.date} в {notification.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>Нет уведомлений</div>
          )}
        </div>
      </div>
    </div>
  );
};

