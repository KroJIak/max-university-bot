import type { DayTab } from '../../../shared/types/schedule';
import styles from './ScheduleTabs.module.scss';

type ScheduleTabsProps = {
  tabs: DayTab[];
  activeTab: string;
  onChange: (id: string) => void;
};

export function ScheduleTabs({ tabs, activeTab, onChange }: ScheduleTabsProps) {
  return (
    <div className={styles.tabs}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;

        return (
          <button
            key={tab.id}
            type="button"
            className={isActive ? styles.tabActive : styles.tab}
            onClick={() => onChange(tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}

