import { NewsSection } from '../../components/NewsSection';
import { ScheduleSection } from '../../components/ScheduleSection';
import { dayTabs, scheduleByDay } from './data';
import styles from './MainPage.module.scss';

export function MainPage() {
  return (
    <div className={styles.page}>
      <div className={styles.mainContent}>
        <ScheduleSection tabs={dayTabs} scheduleByTab={scheduleByDay} />
        <NewsSection />
      </div>
    </div>
  );
}

