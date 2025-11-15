import { useMemo, useState } from 'react';

import { ArrowRightIcon } from '@components/icons';
import { useSubgroup } from '@shared/state/subgroup';
import { filterLessonsBySubgroup } from '@shared/utils/schedule';
import type { DayTab, ScheduleItem } from '@shared/types/schedule';
import { LessonDetailsModal } from './LessonDetailsModal';
import { ScheduleCard } from './ScheduleCard';
import { ScheduleTabs } from './ScheduleTabs';
import styles from './ScheduleSection.module.scss';

type ScheduleSectionProps = {
  title?: string;
  tabs: DayTab[];
  scheduleByTab: Record<string, ScheduleItem[]>;
  onOpenFullSchedule?: () => void;
};

export function ScheduleSection({
  title = 'Расписание',
  tabs,
  scheduleByTab,
  onOpenFullSchedule,
}: ScheduleSectionProps) {
  const [activeTab, setActiveTab] = useState(() => tabs[0]?.id ?? '');
  const [selectedLesson, setSelectedLesson] = useState<ScheduleItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { subgroup } = useSubgroup();

  const schedule = useMemo(() => {
    if (!activeTab) {
      return [];
    }

    const lessons = scheduleByTab[activeTab] ?? [];
    return filterLessonsBySubgroup(lessons, subgroup);
  }, [activeTab, scheduleByTab, subgroup]);

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

  if (!tabs.length) {
    return null;
  }

  return (
    <>
      <section className={styles.section}>
        <header className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <button
            className={styles.moreButton}
            type="button"
            aria-label="Открыть расписание"
            onClick={onOpenFullSchedule}
          >
            <ArrowRightIcon className={styles.moreIcon} />
          </button>
        </header>

        <ScheduleTabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

        {schedule.length > 0 ? (
          <div className={styles.list}>
            {schedule.map((lesson) => (
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

