import { NewsSection } from '@components/NewsSection';
import { ScheduleSection } from '@components/ScheduleSection';
import { dayTabs, scheduleByDay } from '@shared/data/mainPage';
import styles from './MainPage.module.scss';

type MainPageProps = {
  onOpenFullSchedule: () => void;
  onOpenAllNews: () => void;
};

export function MainPage({ onOpenFullSchedule, onOpenAllNews }: MainPageProps) {
  return (
    <div className={styles.page}>
      <div className={styles.mainContent}>
        <ScheduleSection tabs={dayTabs} scheduleByTab={scheduleByDay} onOpenFullSchedule={onOpenFullSchedule} />
        <NewsSection onOpenAll={onOpenAllNews} />
      </div>
    </div>
  );
}

