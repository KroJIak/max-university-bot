import { useEffect } from 'react';
import type { FC } from 'react';

import styles from './AboutModal.module.scss';

type AboutModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

const GOLILUHA_TG_URL = 'https://t.me/Goliluha';
const KROJIAK_TG_URL = 'https://t.me/krojiak';

export const AboutModal: FC<AboutModalProps> = ({ isOpen, onClose }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

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
          <h2 className={styles.title}>О приложении</h2>
          <button type="button" className={styles.closeButton} onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.section}>
            <p className={styles.description}>
              Приложение для студентов университета, предоставляющее удобный доступ к расписанию, новостям, 
              контактам преподавателей и другим важным сервисам.
            </p>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Разработчики</h3>
            <div className={styles.developers}>
              <div className={styles.developer}>
                <span className={styles.developerLabel}>Веб-интерфейс:</span>
                <a
                  href={GOLILUHA_TG_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.developerLink}
                >
                  @Goliluha
                </a>
              </div>
              <div className={styles.developer}>
                <span className={styles.developerLabel}>Бэкенд:</span>
                <a
                  href={KROJIAK_TG_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.developerLink}
                >
                  @krojiak
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

