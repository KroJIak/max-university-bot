import type { ScheduleItem } from '../../../shared/types/schedule';
import styles from './ScheduleCard.module.scss';

type ScheduleCardProps = {
  item: ScheduleItem;
};

const typeLabel: Record<ScheduleItem['type'], string> = {
  lecture: 'ЛК',
  practice: 'ПР',
};

const typeColor: Record<ScheduleItem['type'], string> = {
  lecture: '#4ad871',
  practice: '#ff9f3a',
};

export function ScheduleCard({ item }: ScheduleCardProps) {
  return (
    <article className={styles.card}>
      <div className={styles.timeColumn}>
        <span className={styles.time}>{item.start}</span>
        <span className={styles.timeMuted}>{item.end}</span>
        <span className={styles.timeZone}>МСК</span>
      </div>
      <div className={styles.content}>
        <span className={styles.title}>{item.title}</span>
        <div className={styles.meta}>
          <span className={styles.type} style={{ color: typeColor[item.type] }}>
            {typeLabel[item.type]}
          </span>
          <span className={styles.room}>{item.room}</span>
          <span className={styles.note}>{item.note}</span>
        </div>
      </div>
    </article>
  );
}

