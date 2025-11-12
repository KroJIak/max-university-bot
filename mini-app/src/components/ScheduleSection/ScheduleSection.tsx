import { useMemo, useState } from 'react';

import type { DayTab, ScheduleItem } from '../../shared/types/schedule';
import { ArrowRightIcon } from '../icons';
import { ScheduleCard } from './components/ScheduleCard';
import { ScheduleTabs } from './components/ScheduleTabs';
import styles from './ScheduleSection.module.scss';

type ScheduleSectionProps = {
  title?: string;
  tabs: DayTab[];
  scheduleByTab: Record<string, ScheduleItem[]>;
};

export function ScheduleSection({ title = 'Расписание', tabs, scheduleByTab }: ScheduleSectionProps) {
  const [activeTab, setActiveTab] = useState(() => tabs[0]?.id ?? '');

  const schedule = useMemo(() => {
    if (!activeTab) {
      return [];
    }

    return scheduleByTab[activeTab] ?? [];
  }, [activeTab, scheduleByTab]);

  if (!tabs.length) {
    return null;
  }

  return (
    <section className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        <button className={styles.moreButton} type="button" aria-label="Открыть расписание">
          <ArrowRightIcon className={styles.moreIcon} />
        </button>
      </header>

      <ScheduleTabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <div className={styles.list}>
        {schedule.map((lesson) => (
          <ScheduleCard key={lesson.id} item={lesson} />
        ))}
      </div>
    </section>
  );
}

