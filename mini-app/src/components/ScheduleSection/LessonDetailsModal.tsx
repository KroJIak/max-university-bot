import { useEffect } from 'react';
import type { FC } from 'react';

import styles from './LessonDetailsModal.module.scss';

type LessonDetails = {
  date?: string;
  time_start: string;
  time_end: string;
  subject: string;
  type: string;
  teacher?: string;
  room: string;
  additional_info?: string | null;
  undergruop?: string;
};

type LessonDetailsModalProps = {
  isOpen: boolean;
  lesson: LessonDetails | null;
  onClose: () => void;
};

export const LessonDetailsModal: FC<LessonDetailsModalProps> = ({ isOpen, onClose, lesson }) => {
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

  if (!isOpen || !lesson) {
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
          <h2 className={styles.title}>Информация</h2>
          <button type="button" className={styles.closeButton} onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.row}>
            <span className={styles.label}>Предмет:</span>
            <span className={styles.value}>{lesson.subject}</span>
          </div>

          {lesson.date && (
            <div className={styles.row}>
              <span className={styles.label}>Дата:</span>
              <span className={styles.value}>{lesson.date}</span>
            </div>
          )}

          <div className={styles.row}>
            <span className={styles.label}>Время:</span>
            <span className={styles.value}>
              {lesson.time_start} – {lesson.time_end}
            </span>
          </div>

          <div className={styles.row}>
            <span className={styles.label}>Тип занятия:</span>
            <span className={styles.value}>{lesson.type}</span>
          </div>

          <div className={styles.row}>
            <span className={styles.label}>Аудитория:</span>
            <span className={styles.value}>{lesson.room}</span>
          </div>

          {lesson.teacher && (
            <div className={styles.row}>
              <span className={styles.label}>Преподаватель:</span>
              <span className={styles.value}>{lesson.teacher}</span>
            </div>
          )}

          {lesson.undergruop && (
            <div className={styles.row}>
              <span className={styles.label}>Подгруппа:</span>
              <span className={styles.value}>{lesson.undergruop}</span>
            </div>
          )}

          {lesson.additional_info && (
            <div className={styles.row}>
              <span className={styles.label}>Дополнительная информация:</span>
              <span className={styles.value}>{lesson.additional_info}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

