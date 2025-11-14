import type { FC } from 'react';

import styles from './Profile.module.scss';

type ProfileSummarySectionProps = {
  name: string;
  subtitle: string;
};

export const ProfileSummarySection: FC<ProfileSummarySectionProps> = ({ name, subtitle }) => {
  return (
    <section className={styles.card}>
      <div className={styles.summary}>
      <div className={styles.avatar} />
      <div className={styles.info}>
        <span className={styles.name}>{name}</span>
        <span className={styles.value}>{subtitle}</span>
        </div>
      </div>
    </section>
  );
};

