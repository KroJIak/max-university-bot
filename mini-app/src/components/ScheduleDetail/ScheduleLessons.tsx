import { useState } from 'react';

import type { ScheduleItem } from '../../shared/types/schedule';
import { LessonDetailsModal } from '@components/ScheduleSection/LessonDetailsModal';
import { ScheduleCard } from '@components/ScheduleSection/ScheduleCard';
import styles from './ScheduleDetail.module.scss';

type ScheduleLessonsProps = {
  items: ScheduleItem[];
};

export function ScheduleLessons({ items }: ScheduleLessonsProps) {
  const [selectedLesson, setSelectedLesson] = useState<ScheduleItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleLessonClick = (lesson: ScheduleItem) => {
    setSelectedLesson(lesson);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedLesson(null);
  };

  const getTypeLabel = (type: ScheduleItem['type']): string => {
    const labels: Record<ScheduleItem['type'], string> = {
      lecture: 'Лекция',
      practice: 'Практика',
      lab: 'Лабораторная работа',
    };
    return labels[type];
  };

  return (
    <>
      <section className={styles.listWrapper}>
        <h2 className={styles.listTitle}>Расписание</h2>
        {items.length ? (
          <div className={styles.list}>
            {items.map((lesson) => (
              <ScheduleCard key={lesson.id} item={lesson} onClick={handleLessonClick} />
            ))}
          </div>
        ) : (
          <div className={styles.emptyState}>Занятия на этот день отсутствуют</div>
        )}
      </section>

      {selectedLesson && (
        <LessonDetailsModal
          isOpen={isModalOpen}
          lesson={{
            date: selectedLesson.date,
            time_start: selectedLesson.start,
            time_end: selectedLesson.end,
            subject: selectedLesson.title,
            type: getTypeLabel(selectedLesson.type),
            teacher: selectedLesson.teacher,
            room: selectedLesson.room,
            additional_info: selectedLesson.additional_info,
            undergruop: selectedLesson.undergruop,
          }}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}

